"""How the optimal interval moves with idle-noise strength. (Original notebook 07: 07b, 07d.)

Setup of the original notebook 07, which `stim_circuit` reproduces exactly at the
same seeds: textbook gates, X-basis memory, idle noise on the data once per interval
("data_interval"), H2-1E gate ratios scaled so p2 = 5e-3, T = 192, 2 x 100k shots.
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


def curve(store, d, idle, workers):
    noise = CircuitNoise(**GATES, idle=idle, placement="data_interval")
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


def q_idle(dt, gamma, c):
    return gamma * dt + np.sin(np.sqrt(c) * dt) ** 2


def fit_ansatz(curves, d):
    """Least squares in log R over all curves of one distance, pL < 0.3 (as notebook 07)."""
    data = [(fam, v, np.array([p["dt"] for p in pts if p["pL"] < 0.3 and np.isfinite(p["r"])]),
             np.array([p["r"] for p in pts if p["pL"] < 0.3 and np.isfinite(p["r"])]),
             np.array([p["sr"] for p in pts if p["pL"] < 0.3 and np.isfinite(p["r"])]))
            for (fam, v), pts in curves.items()]

    def model(dt, g, c, th):
        logA, logpe, alpha = th
        return np.exp(logA) / dt * (1 + q_idle(dt, g, c) / np.exp(logpe)) ** alpha

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


def dt_star_gc(g: float, c: float, fit) -> float:
    """dt* of the calibrated ansatz at linear rate g and quadratic c (absolute, per t_R).
    Searched only up to the first rephasing of the quadratic term (sqrt(c) dt < pi/2),
    where the twirled form stops describing decoherence."""
    grid = _DT if c == 0 else _DT[_DT * math.sqrt(c) < math.pi / 2]
    R = 1 / grid * (1 + q_idle(grid, g, c) / fit["p_e"]) ** fit["alpha"]
    return float(grid[np.argmin(R)])


def dt_star_formula(q_over_p2, family, fit):
    """dt* of the calibrated ansatz for idle error per round q(1) = q_over_p2 * p2."""
    q = q_over_p2 * P2
    g, c = (q, 0.0) if family == "lin" else (0.0, float(np.arcsin(np.sqrt(min(q, 1.0))) ** 2))
    return dt_star_gc(g, c, fit)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/idle_scaling"))
    a = ap.parse_args(argv)
    store, rows = Store(a.store), []
    q_axis = np.geomspace(1e-3, 3, 40)
    for d in a.distances:
        curves, opts = {}, {}
        for fam, v, idle in families():
            pts, o = curve(store, d, idle, a.workers)
            curves[(fam, v)], opts[(fam, v)] = pts, o
            print(f"d={d} {fam} {v:<7} dt* = {o['dt_star']:.2f} [{o['lo']:.2f}, {o['hi']:.2f}]", flush=True)
        slopes = {fam: power_slope(vals, [opts[(fam, v)] for v in vals])
                  for fam, vals in (("lin", LIN), ("quad", QUAD))}
        fit = fit_ansatz(curves, d)
        # Held-out test of the formula: both idle terms at once, not used in the fit.
        held_pts, held = curve(store, d, IdleNoise(gamma=MIXED[0] * P2, c=MIXED[1] * P2), a.workers)
        held_pred = dt_star_gc(MIXED[0] * P2, MIXED[1] * P2, fit)
        print(f"d={d} held out (gamma, c) = {MIXED} p2: simulated dt* {held['dt_star']:.2f} "
              f"[{held['lo']:.2f}, {held['hi']:.2f}], formula {held_pred:.2f}", flush=True)
        dmap = [[dt_star_gc(gx * P2, cy * P2, fit) for gx in MAP_AXIS] for cy in MAP_AXIS]
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
                             "note": "rows: c/p2, columns: gamma/p2"},
                     "formula": {fam: [{"q_over_p2": float(q), "dt_star": dt_star_formula(q, fam, fit)}
                                       for q in q_axis] for fam in ("lin", "quad")}})
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "idle_scaling.json").write_text(json.dumps(
        {"setup": {"gates": GATES, "T": T, "shots": SHOTS, "seeds": SEEDS, "placement": "data_interval",
                   "basis": "X", "lin": LIN, "quad": QUAD, "held_out": MIXED, "p2": P2}, "rows": rows}, indent=1))
    print(f"wrote {a.out / 'idle_scaling.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
