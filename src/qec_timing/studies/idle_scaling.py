"""How the optimal interval moves with idle-noise strength. (Original notebook 07: 07b, 07d.)

Setup of the original notebook 07, which `stim_circuit` reproduces exactly at the
same seeds: textbook gates, X-basis memory, idle noise on the data once per interval
("data_interval"), H2-1E gate ratios scaled so p2 = 5e-3, T = 192, 2 x 100k shots.
`--placement uniform` instead puts the idle noise on every qubit, during each layer
and the wait, as in the premise and regime studies (output idle_scaling_uniform.json).
Idle families: linear gamma / p2 in {0.15, 0.3, 0.6}, quadratic c / p2 in
{0.0025, 0.01, 0.04}, at d = 3, 5, 7.

Two results:
  - power laws: in the ansatz the rate is ~ (1 + q(dt)/p_e)^alpha / dt with
    q = gamma dt (linear) or ~ c dt^2 (quadratic), so dt* ~ gamma^-1 or c^-1/2.
    The log-log slopes are fitted per distance;
  - the dt* map (figure 07c, revised): the calibrated ansatz's dt* over the
    (gamma, c) plane, with one held-out simulation (both terms at once) as a test;
  - the calibrated ansatz (notebook 07): per distance, fit
        R(dt) = (A / dt) (1 + q(dt) / p_e)^alpha,  q(dt) = gamma dt + sin^2(sqrt(c) dt)
    to all six curves at once (A, p_e, alpha), then predict dt* for any idle error
    per round q(1) / p2, all-linear or all-quadratic (figure 07d).

    python -m qec_timing.studies.idle_scaling --workers 8
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares

from qec_timing.analysis.interval import dt_grid, optimum, rate
from qec_timing.backends.stim_circuit import StimCircuitBackend
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.noise.circuit import CircuitNoise, IdleNoise
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.store import Store
from qec_timing.studies import runs
from qec_timing.studies.premise import GATES, P2

T, SHOTS, SEEDS = 192, 100_000, (1, 2)
LIN = (0.15, 0.3, 0.6)          # gamma / p2
QUAD = (0.0025, 0.01, 0.04)     # c / p2
MIXED = (0.3, 0.01)             # (gamma, c) / p2: simulated but held OUT of the fit, to test it
MAP_AXIS = np.geomspace(1e-4, 3.0, 56)          # gamma/p2 and c/p2 axes of the dt* map


def families():
    return [("lin", v, IdleNoise(gamma=v * P2)) for v in LIN] + \
           [("quad", v, IdleNoise(c=v * P2)) for v in QUAD]


def curve(store, d, idle, workers, placement="data_interval"):
    noise = CircuitNoise(**GATES, idle=idle, placement=placement)
    code = RotatedSurfaceCode(d)
    grid = dt_grid(T, d)
    specs = [MemorySpec(code, "X", Schedule.rounds(dt, R), noise, SHOTS, s) for dt, R in grid for s in SEEDS]
    res = iter(runs.failures_many(store, StimCircuitBackend(), specs, workers))
    pts = []
    for dt, R in grid:
        F = N = 0
        for _ in SEEDS:
            _, f, n = next(res)
            F, N = F + f, N + n
        r, sr = rate(F, N, T)
        pts.append({"dt": dt, "R": R, "pL": F / N, "r": r, "sr": sr})
    a = {k: np.array([p[k] for p in pts]) for k in ("dt", "pL", "r", "sr")}
    return pts, optimum(a["dt"], a["pL"], a["r"], a["sr"]).as_dict()


def power_slope(xs, opts):
    x = np.log(xs)
    y = np.log([o["dt_star"] for o in opts])
    s = np.array([max((math.log(o["hi"]) - math.log(o["lo"])) / 2, 0.02) for o in opts])
    (m, b), cov = np.polyfit(x, y, 1, w=1 / s, cov="unscaled")
    return float(m), float(math.sqrt(cov[0, 0]))


from qec_timing.backends.stim_circuit import LAYERS   # layers per round of the textbook circuit


def _pz(t, gamma, c):
    """Z probability of one twirled idle chunk of duration t (IdleNoise.channel's Z part)."""
    lin = np.minimum(gamma * t, 0.5)
    quad = np.sin(np.sqrt(c) * t) ** 2
    return lin + quad - 2 * lin * quad


def q_idle(dt, gamma, c, placement="data_interval"):
    """Idle Z error on a data qubit over one period dt, as the ansatz sees it.

    data_interval: one idle(dt) chunk per round; kept in the original notebook 07 form
    (gamma dt + sin^2(sqrt(c) dt), the two terms added) so its fit is reproduced exactly.
    uniform: the chunks the circuit actually applies, each twirled on its own:
    LAYERS x idle(1/LAYERS) inside the round and idle(dt - 1) for the wait, composed
    as independent flips. The quadratic term restarts in every chunk, so inside the
    round it is ~ LAYERS sin^2(sqrt(c)/LAYERS) ~ c / LAYERS, not sin^2(sqrt(c))."""
    dt = np.asarray(dt, dtype=float)
    if placement == "data_interval":
        return gamma * dt + np.sin(np.sqrt(c) * dt) ** 2
    if placement != "uniform":
        raise ValueError(f"unknown placement {placement!r}")
    keep = (1 - 2 * _pz(1.0 / LAYERS, gamma, c)) ** LAYERS * (1 - 2 * _pz(dt - 1.0, gamma, c))
    return (1 - keep) / 2


def fit_ansatz(curves, d, placement="data_interval"):
    """Least squares in log R over all curves of one distance, pL < 0.3 (as notebook 07)."""
    data = [(fam, v, np.array([p["dt"] for p in pts if p["pL"] < 0.3 and np.isfinite(p["r"])]),
             np.array([p["r"] for p in pts if p["pL"] < 0.3 and np.isfinite(p["r"])]),
             np.array([p["sr"] for p in pts if p["pL"] < 0.3 and np.isfinite(p["r"])]))
            for (fam, v), pts in curves.items()]

    def model(dt, g, c, th):
        logA, logpe, alpha = th
        return np.exp(logA) / dt * (1 + q_idle(dt, g, c, placement) / np.exp(logpe)) ** alpha

    def resid(th):
        out = []
        for fam, v, dt, r, sr in data:
            g, c = (v * P2, 0.0) if fam == "lin" else (0.0, v * P2)
            out.append((np.log(model(dt, g, c, th)) - np.log(r)) / (sr / r))
        return np.concatenate(out)

    r0 = data[0][3][0]
    res = least_squares(resid, [math.log(r0), math.log(3 * P2), 0.8 * (d + 1) / 2])
    dof = res.fun.size - 3
    chi2 = float(res.fun @ res.fun / dof)
    cov = np.linalg.inv(res.jac.T @ res.jac) * max(chi2, 1.0)
    return {"logA": float(res.x[0]), "p_e": float(math.exp(res.x[1])), "alpha": float(res.x[2]),
            "alpha_se": float(math.sqrt(cov[2, 2])), "implied_g": float(2 * res.x[2] / (d + 1)),
            "chi2_dof": chi2, "points": int(res.fun.size)}


_DT = np.geomspace(0.05, 5000, 6000)


def dt_star_gc(g: float, c: float, fit, placement="data_interval") -> float:
    """dt* of the calibrated ansatz at linear rate g and quadratic c (absolute, per t_R).
    Searched only up to the first rephasing of the quadratic term (sqrt(c) dt < pi/2,
    dt - 1 for the wait chunk under uniform placement), where the twirled form stops
    describing decoherence. Uniform placement needs dt >= 1."""
    grid = _DT if placement == "data_interval" else np.r_[1.0, _DT[_DT > 1.0]]   # back to back included
    if c:
        span = grid if placement == "data_interval" else grid - 1.0
        grid = grid[span * math.sqrt(c) < math.pi / 2]
    R = 1 / grid * (1 + q_idle(grid, g, c, placement) / fit["p_e"]) ** fit["alpha"]
    # The FIRST local minimum. Under uniform placement the idle error saturates at 1/2 for
    # long waits, after which the ansatz's 1/dt factor keeps falling: a spurious minimum
    # at the end of the grid, in a region (p_L -> 1/2) the ansatz does not describe.
    rising = np.nonzero(np.diff(R) > 0)[0]
    return float(grid[rising[0]] if rising.size else grid[-1])


def gain_gc(g: float, c: float, fit, placement="data_interval") -> float:
    """R(back to back) / R(dt*) of the calibrated ansatz: what an optimised interval buys."""
    def R(dt):
        return float(1 / dt * (1 + q_idle(dt, g, c, placement) / fit["p_e"]) ** fit["alpha"])
    return R(1.0) / R(dt_star_gc(g, c, fit, placement))


def rate_for_q1(q: float, family: str, placement="data_interval") -> float:
    """The gamma (family "lin") or c ("quad") whose idle error per round q(1) is q."""
    from scipy.optimize import brentq
    if placement == "data_interval":
        return q if family == "lin" else float(np.arcsin(np.sqrt(min(q, 1.0))) ** 2)
    f = (lambda x: float(q_idle(1.0, x, 0.0, placement)) - q) if family == "lin" else \
        (lambda x: float(q_idle(1.0, 0.0, x, placement)) - q)
    hi = 1.0 if family == "lin" else (LAYERS * math.pi / 2) ** 2 * 0.999
    return float(brentq(f, 0.0, hi)) if f(hi) > 0 else math.nan


def dt_star_formula(q_over_p2, family, fit, placement="data_interval"):
    """dt* of the calibrated ansatz for idle error per round q(1) = q_over_p2 * p2."""
    x = rate_for_q1(q_over_p2 * P2, family, placement)
    if not math.isfinite(x):
        return math.nan
    g, c = (x, 0.0) if family == "lin" else (0.0, x)
    return dt_star_gc(g, c, fit, placement)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/idle_scaling"))
    ap.add_argument("--placement", choices=("data_interval", "uniform"), default="data_interval",
                    help="data_interval: idle(dt) on the data once per round (original notebook 07, "
                         "the default); uniform: every qubit, during each layer and the wait")
    a = ap.parse_args(argv)
    store, rows = Store(a.store), []
    q_axis = np.geomspace(1e-4, 3, 50)
    for d in a.distances:
        curves, opts = {}, {}
        for fam, v, idle in families():
            pts, o = curve(store, d, idle, a.workers, a.placement)
            curves[(fam, v)], opts[(fam, v)] = pts, o
            print(f"d={d} {fam} {v:<7} dt* = {o['dt_star']:.2f} [{o['lo']:.2f}, {o['hi']:.2f}]", flush=True)
        slopes = {fam: power_slope(vals, [opts[(fam, v)] for v in vals])
                  for fam, vals in (("lin", LIN), ("quad", QUAD))}
        fit = fit_ansatz(curves, d, a.placement)
        # Held-out test of the formula: both idle terms at once, not used in the fit.
        held_pts, held = curve(store, d, IdleNoise(gamma=MIXED[0] * P2, c=MIXED[1] * P2), a.workers,
                               a.placement)
        held_pred = dt_star_gc(MIXED[0] * P2, MIXED[1] * P2, fit, a.placement)
        print(f"d={d} held out (gamma, c) = {MIXED} p2: simulated dt* {held['dt_star']:.2f} "
              f"[{held['lo']:.2f}, {held['hi']:.2f}], formula {held_pred:.2f}", flush=True)
        dmap = [[dt_star_gc(gx * P2, cy * P2, fit, a.placement) for gx in MAP_AXIS] for cy in MAP_AXIS]
        print(f"d={d}: slopes lin {slopes['lin'][0]:.3f}+/-{slopes['lin'][1]:.3f} (pred -1), "
              f"quad {slopes['quad'][0]:.3f}+/-{slopes['quad'][1]:.3f} (pred -0.5); "
              f"alpha {fit['alpha']:.2f} (g = {fit['implied_g']:.2f})", flush=True)
        rows.append({"d": d,
                     "curves": [{"family": f, "value": v, "points": curves[(f, v)], "optimum": opts[(f, v)]}
                                for f, v, _ in families()],
                     "slopes": {k: {"slope": m, "se": s} for k, (m, s) in slopes.items()},
                     "ansatz": fit,
                     "held_out": {"gamma_over_p2": MIXED[0], "c_over_p2": MIXED[1], "points": held_pts,
                                  "optimum": held, "formula_dt_star": held_pred},
                     "map": {"axis": MAP_AXIS.tolist(), "dt_star": dmap,
                             "gain": [[gain_gc(gx * P2, cy * P2, fit, a.placement) for gx in MAP_AXIS]
                                      for cy in MAP_AXIS],
                             "note": "rows: c/p2, columns: gamma/p2"},
                     "formula": {fam: [{"q_over_p2": float(q), "dt_star": dt_star_formula(q, fam, fit, a.placement)}
                                       for q in q_axis] for fam in ("lin", "quad")}})
    a.out.mkdir(parents=True, exist_ok=True)
    out = a.out / ("idle_scaling.json" if a.placement == "data_interval" else f"idle_scaling_{a.placement}.json")
    out.write_text(json.dumps(
        {"setup": {"gates": GATES, "T": T, "shots": SHOTS, "seeds": SEEDS, "placement": a.placement,
                   "basis": "X", "lin": LIN, "quad": QUAD, "held_out": MIXED, "p2": P2}, "rows": rows}, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
