"""The paper's central scaling: 1/dt* grows linearly with d. (Original Stage 4a; Fig. 2.)

The paper's phenomenological model (p = 0.015, lam = 1, b_read = 1) on the rotated
surface code, Z basis, total time T = 10, sampled with Stim on a fine grid of
intervals around Eq. 6's prediction at each distance. dt* is located by the
package's parabola-in-log fit with a bootstrap interval (`analysis.interval`), and
1/dt* = eta d + z is fitted by weighted least squares, against the paper's slope
0.402 (fitted there on d = 11-27) and Eq. 6 with g = 0.8.

    python -m qec_timing.studies.scaling --distances 5 7 9 11
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from qec_timing.analysis import ansatz
from qec_timing.analysis.interval import optimum
from qec_timing.backends.stim_phenom import StimPhenomBackend
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.noise.paper import PaperNoise
from qec_timing.records import Derived
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.stats import rate_per_time
from qec_timing.store import Store
from qec_timing.studies import runs

P, LAM, B_READ, T, TICK = 0.015, 1.0, 1.0, 10.0, 1e-5
SEED = 41_000_000


def grid(d: int, n: int) -> list[float]:
    """Log grid from 0.2x to 4x Eq. 6's dt*, snapped to the tick, distinct round counts."""
    star = ansatz.optimal_interval(d=d, lam=LAM)
    out, seen = [], set()
    for x in np.geomspace(0.2 * star, 4.0 * star, n):
        dt = round(x / TICK) * TICK
        R = round(T / dt)
        if R >= 1 and R not in seen:
            seen.add(R)
            out.append(dt)
    return out


def study(store: Store, d: int, n: int, shots: int, workers: int, log=print) -> dict:
    specs = [MemorySpec(RotatedSurfaceCode(d), "Z", Schedule.fixed(dt, T, tick=TICK),
                        PaperNoise(P, LAM, B_READ), shots, SEED + 1000 * d + i)
             for i, dt in enumerate(grid(d, n))]
    res = runs.failures_many(store, StimPhenomBackend(), specs, workers)
    pts = []
    for spec, (ids, f, k) in zip(specs, res):
        Ta = spec.schedule.total_time                       # n_rounds * dt, the time actually run
        pL = f / k
        r = rate_per_time(pL, Ta)
        sr = math.sqrt(max(pL * (1 - pL), 1e-12) / k) / ((1 - 2 * pL) * Ta)
        pts.append({"dt": spec.schedule.dts[0], "n_rounds": spec.schedule.n_rounds, "T": Ta,
                    "failures": f, "shots": k, "pL": pL, "r": r, "sr": sr, "run_ids": ids})
    a = {k: np.array([p[k] for p in pts]) for k in ("dt", "pL", "r", "sr")}
    o = optimum(a["dt"], a["pL"], a["r"], a["sr"]).as_dict()
    eq6 = ansatz.optimal_interval(d=d, lam=LAM)
    log(f"d={d}: dt* = {o['dt_star']:.4f} [{o['lo']:.4f}, {o['hi']:.4f}]   Eq. 6 (g=0.8) {eq6:.4f} "
        f"({o['dt_star'] / eq6 - 1:+.0%})")
    return {"d": d, "points": pts, "optimum": o, "eq6": eq6}


def fit_inverse(rows: list[dict]) -> dict:
    """Weighted fit 1/dt* = eta d + z; sigma(1/dt*) from the bootstrap 16-84% interval."""
    d = np.array([r["d"] for r in rows], float)
    y = np.array([1 / r["optimum"]["dt_star"] for r in rows])
    s = np.array([max((1 / r["optimum"]["lo"] - 1 / r["optimum"]["hi"]) / 2, 1e-6) for r in rows])
    W = 1 / s ** 2
    A = np.stack([d, np.ones_like(d)], 1)
    cov = np.linalg.inv(A.T @ (A * W[:, None]))
    eta, z = cov @ (A.T @ (W * y))
    chi2 = float(((y - A @ [eta, z]) ** 2 * W).sum())
    dof = max(len(d) - 2, 1)
    scale = max(chi2 / dof, 1.0)
    return {"eta": float(eta), "eta_se": float(math.sqrt(cov[0, 0] * scale)),
            "z": float(z), "z_se": float(math.sqrt(cov[1, 1] * scale)), "chi2_dof": chi2 / dof,
            "paper_eta": ansatz.PAPER_SLOPE,
            "sigma_from_paper": float((eta - ansatz.PAPER_SLOPE) / math.sqrt(cov[0, 0] * scale))}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--distances", type=int, nargs="+", default=[5, 7, 9, 11])
    ap.add_argument("--points", type=int, default=15)
    ap.add_argument("--shots", type=int, default=200_000)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/scaling"))
    a = ap.parse_args(argv)
    store, t0 = Store(a.store), time.perf_counter()
    rows = [study(store, d, a.points, a.shots, a.workers) for d in a.distances]
    fit = fit_inverse(rows)
    print(f"1/dt* = ({fit['eta']:.3f} +/- {fit['eta_se']:.3f}) d + ({fit['z']:.3f} +/- {fit['z_se']:.3f}); "
          f"paper slope {fit['paper_eta']} ({fit['sigma_from_paper']:+.1f} sigma)")
    data = {"setup": {"p": P, "lam": LAM, "b_read": B_READ, "T": T, "basis": "Z",
                      "shots": a.shots, "backend": "stim_phenom"}, "rows": rows, "fit": fit}
    did = store.save_derived(Derived("scaling_paper_model", data,
                                     tuple(i for r in rows for p in r["points"] for i in p["run_ids"])))
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "scaling.json").write_text(json.dumps({"derived_id": did, **data}, indent=1))
    print(f"wrote {a.out / 'scaling.json'} in {(time.perf_counter() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
