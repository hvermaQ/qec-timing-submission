"""A circuit's effective paper parameters: lambda and b_read. (Original notebooks 04, 04c, 05.)

The first, deliberately artificial step of the notebook arc (narrative point 7):
Selene's depolarizing model on its native gates, mirrored exactly in Stim
(`stim_native`): a uniform Pauli before every single-qubit gate including Rz
(`rz_noise`), Rzz charged p2 = rho * p1, readout flips p_meas, and idling as
explicit identity ops charged p1 each, one per unit of interval on every data qubit
(depolarizing idle, "data_interval"). Z-basis memory, as in the original 04-06.

The paper's model has p_data = 1 - (1 - p_stab)(1 - p_idle), p_idle = 1 - exp(-p_stab lam dt),
p_read = b_read p_stab (Eqs. 1-3). Hence
    ln(1 - p_data(dt)) = ln(1 - p_stab) - p_stab * lam * dt,
linear in dt. p_data and p_read are measured from detection events (`EdgeExtractor`)
at several dt, giving p_stab (intercept), lam (slope) and b_read = p_read / p_stab.
b_read includes the readout error; the "floor" (readout error off, the original repo's
definition) isolates what the ancilla's gate noise alone adds to the record.
The paper assumed lam = 0.31 (fitted to Willow) and b_read = 1.

Then the consequence (figure 05a): p_L against dt under the paper's parameters and
under the effective ones, same p_stab, T = 96.

    python -m qec_timing.studies.effective --distances 3 5 7
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np

from qec_timing.analysis.interval import optimum, rate
from qec_timing.backends.stim_native import StimNativeBackend
from qec_timing.backends.stim_phenom import StimPhenomBackend
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.noise.circuit import CircuitNoise, IdleNoise
from qec_timing.noise.paper import PaperNoise
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.store import Store
from qec_timing.studies import runs

P1, P_MEAS = 5e-4, 2e-3                 # original 06c settings
RHOS = (0.0, 1.0, 3.0, 10.0, 30.0, 100.0)
DTS = (1.0, 2.0, 4.0, 8.0)
R_CAL, SHOTS_CAL = 20, 200_000
PAPER_LAM, PAPER_B_READ = 0.31, 1.0
T_CURVE, SHOTS_CURVE = 96.0, 100_000
SEED = 61_000_000


def selene_like(rho: float, p_meas: float = P_MEAS) -> CircuitNoise:
    return CircuitNoise(p1=P1, p2=rho * P1, p_meas=p_meas, p_init=0.0,
                        idle=IdleNoise(depol=P1), placement="data_interval")


def fit_lambda(dts, p_data) -> tuple[float, float]:
    """(p_stab, lam) from p_data measured at several dt, using Eqs. 1-2:
    ln(1 - p_data) = ln(1 - p_stab) - p_stab * lam * dt (a straight line in dt)."""
    slope, icept = np.polyfit(np.asarray(dts, float), np.log1p(-np.asarray(p_data, float)), 1)
    p_stab = -math.expm1(icept)
    return p_stab, -slope / p_stab


def effective(store: Store, d: int, rho: float) -> dict:
    code, b = RotatedSurfaceCode(d), StimNativeBackend()
    pd, pr = [], []
    for dt in DTS:
        m = runs.edges(store, b, MemorySpec(code, "Z", Schedule.rounds(dt, R_CAL), selene_like(rho),
                                            SHOTS_CAL, SEED, extra={"rz_noise": True}))
        pd.append(m.params["p_data"].value)
        pr.append(m.params["p_read"].value)
    p_stab, lam = fit_lambda(DTS, pd)
    b_read = float(np.mean(pr)) / p_stab
    # The original repo's "b_read floor": the same ratio with readout error off, i.e. what
    # the ancilla's own gate noise alone contributes to the syndrome record.
    m0 = runs.edges(store, b, MemorySpec(code, "Z", Schedule.rounds(1.0, R_CAL), selene_like(rho, 0.0),
                                         SHOTS_CAL, SEED, extra={"rz_noise": True}))
    floor = m0.params["p_read"].value / m0.params["p_data"].value
    return {"d": d, "rho": rho, "p_stab": p_stab, "lam": lam, "b_read": b_read, "b_read_floor": floor,
            "p_data": dict(zip(map(str, DTS), pd)), "p_read": dict(zip(map(str, DTS), pr))}


def pl_curve(store: Store, d: int, p: float, lam: float, b_read: float, workers: int, tag: int,
             target: int = 300, pilot: int = 20_000, max_shots: int = 3_000_000) -> dict:
    """p_L against dt, the paper's model at (p, lam, b_read), Z basis, fixed T.

    Shots are sized per point from a pilot so each point has ~`target` failures: at
    d = 7 and p ~ 2.5e-3, p_L ~ 5e-4, and a fixed 100k shots (an earlier version)
    left 20-90 failures per point, too few to locate the minimum."""
    grid = sorted({round(T_CURVE / R, 6) for R in
                   {int(round(T_CURVE / x)) for x in np.geomspace(0.25, 32, 22)} if R >= 1})
    spec_at = lambda i, dt, n, k: MemorySpec(                                  # noqa: E731
        RotatedSurfaceCode(d), "Z", Schedule.rounds(dt, int(round(T_CURVE / dt))),
        PaperNoise(p, lam, b_read), n, SEED + 100_000 * tag + 100 * i + k)
    pilots = runs.failures_many(store, StimPhenomBackend(), [spec_at(i, dt, pilot, 0) for i, dt in enumerate(grid)],
                                workers)
    want = [int(min(max_shots, max(0, target * n / max(f, 1) - n))) for _, f, n in pilots]
    sized = [spec_at(i, dt, k, 1) for i, (dt, k) in enumerate(zip(grid, want)) if k > 0]
    more = dict(zip([s.schedule.dts[0] for s in sized], runs.failures_many(store, StimPhenomBackend(), sized, workers)))
    pts = []
    for dt, (_, f, n) in zip(grid, pilots):
        if dt in more:
            f, n = f + more[dt][1], n + more[dt][2]
        r, sr = rate(f, n, T_CURVE)
        pts.append({"dt": dt, "failures": f, "shots": n, "pL": f / n, "r": r, "sr": sr})
    a = {k: np.array([x[k] for x in pts]) for k in ("dt", "pL", "r", "sr")}
    return {"points": pts, "optimum": optimum(a["dt"], a["pL"], a["r"], a["sr"]).as_dict()}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/effective"))
    a = ap.parse_args(argv)
    store = Store(a.store)
    params = []
    for d in a.distances:
        for rho in RHOS:
            e = effective(store, d, rho)
            params.append(e)
            print(f"d={d} rho={rho:<5g} p_stab {e['p_stab']:.2e}  lambda {e['lam']:.3f}  "
                  f"b_read {e['b_read']:.3f} (floor, p_meas = 0: {e['b_read_floor']:.3f})", flush=True)
    curves = []
    for i, d in enumerate(a.distances):
        e = next(x for x in params if x["d"] == d and x["rho"] == 0.0)
        paper = pl_curve(store, d, e["p_stab"], PAPER_LAM, PAPER_B_READ, a.workers, 2 * i)
        eff = pl_curve(store, d, e["p_stab"], e["lam"], e["b_read"], a.workers, 2 * i + 1)
        print(f"d={d}: dt* paper parameters {paper['optimum']['dt_star']:.2f}, effective "
              f"{eff['optimum']['dt_star']:.2f} (x{eff['optimum']['dt_star'] / paper['optimum']['dt_star']:.1f})",
              flush=True)
        curves.append({"d": d, "p_stab": e["p_stab"], "paper": paper, "effective": eff})
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "effective.json").write_text(json.dumps(
        {"setup": {"p1": P1, "p_meas": P_MEAS, "rhos": RHOS, "dts": DTS, "idle": "depolarizing, p1 per unit",
                   "rz_noise": True, "basis": "Z", "paper_lam": PAPER_LAM, "paper_b_read": PAPER_B_READ,
                   "T_curve": T_CURVE}, "params": params, "curves": curves}, indent=1))
    print(f"wrote {a.out / 'effective.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
