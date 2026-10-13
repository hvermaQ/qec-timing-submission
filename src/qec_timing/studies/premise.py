"""Does a realistic circuit reduce to the paper's model? (Original notebooks 08, 09.)

Circuit: rotated surface code, X-basis memory, the SAME idle noise on every qubit
through the round and the wait ("uniform" placement), with either
    --gates textbook   Stim's generated circuit, one CX per CNOT (notebook 08), or
    --gates native     Selene's native gates, Rzz + single-qubit rotations (notebook 09). Gate rates are H2-1E's, scaled x4.76 so p2 = 5e-3 and
logical failures are frequent enough to measure.

Three claims are tested per (d, idle noise):
  P1  an interior optimum dt* exists for the full circuit;
  P2  p_read is flat in dt, and p_data(dt) = p_data(1) XOR q_wait(dt - 1);
  P3  dt* is predicted by the paper's model from ONE calibration at dt = 1
      ("measured once": EffectiveNoise with the idle channel as the wait).

Every run (full-circuit curves, calibrations, phenomenological predictions) is
written to the store; the summary goes to results/premise/premise_<gates>.json.

    python -m qec_timing.studies.premise --gates native --distances 3 5 7
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from qec_timing.analysis.interval import dt_grid, optimum, rate
from qec_timing.backends.stim_circuit import StimCircuitBackend
from qec_timing.backends.stim_native import StimNativeBackend
from qec_timing.backends.stim_phenom import StimPhenomBackend
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.extract.edges import xor
from qec_timing.noise.circuit import CircuitNoise, IdleNoise
from qec_timing.noise.effective import EffectiveNoise
from qec_timing.records import Derived
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.store import Store
from qec_timing.studies import runs

# H2-1E emulator noise (2025-07-16 table), scaled so p2 = 5e-3.
H2 = dict(p1=1.89e-5, p2=1.05e-3, p_meas0=6e-4, p_meas1=1.39e-3, p_init=4e-5)
P2 = 5e-3
SCALE = P2 / H2["p2"]
GATES = dict(p1=H2["p1"] * SCALE, p2=P2, p_meas=0.5 * (H2["p_meas0"] + H2["p_meas1"]) * SCALE,
             p_init=H2["p_init"] * SCALE)
T = 192
SHOTS, SEEDS = 100_000, (1, 2)
R_CAL, SHOTS_CAL = 20, 400_000
# Idle noise relative to p2: linear gamma, quadratic c, and one mixed point.
IDLE = {"lin 0.3": IdleNoise(gamma=0.3 * P2), "quad 0.01": IdleNoise(c=0.01 * P2),
        "mixed": IdleNoise(gamma=0.3 * P2, c=0.01 * P2)}


def circuit_noise(idle: IdleNoise) -> CircuitNoise:
    return CircuitNoise(**GATES, idle=idle, placement="uniform")


def curve(store: Store, backend, make_spec, d: int, workers: int = 1) -> dict:
    """Rate curve over dt_grid(T, d), pooled over SEEDS. make_spec(dt, R, seed)."""
    grid = dt_grid(T, d)
    specs = [make_spec(dt, R, seed) for dt, R in grid for seed in SEEDS]
    results = iter(runs.failures_many(store, backend, specs, workers))
    rows, ids = [], []
    for dt, R in grid:
        F = N = 0
        for _ in SEEDS:
            rids, f, n = next(results)
            F, N, ids = F + f, N + n, ids + rids
        r, sr = rate(F, N, T)
        rows.append({"dt": dt, "R": R, "failures": F, "shots": N, "pL": F / N, "r": r, "sr": sr})
    a = {k: np.array([row[k] for row in rows]) for k in ("dt", "pL", "r", "sr")}
    return {"points": rows, "optimum": optimum(a["dt"], a["pL"], a["r"], a["sr"]).as_dict(),
            "run_ids": ids}


GATE_BACKENDS = {"textbook": StimCircuitBackend, "native": StimNativeBackend}


def one(store: Store, d: int, label: str, gates: str = "textbook", workers: int = 1,
        log=print) -> dict:
    code, idle = RotatedSurfaceCode(d), IDLE[label]
    full_b, phen_b = GATE_BACKENDS[gates](), StimPhenomBackend()
    noise = circuit_noise(idle)
    full = curve(store, full_b, lambda dt, R, s: MemorySpec(code, "X", Schedule.rounds(dt, R),
                                                             noise, SHOTS, s), d, workers)
    # One calibration at back-to-back rounds.
    cal_spec = MemorySpec(code, "X", Schedule.rounds(1.0, R_CAL), noise, SHOTS_CAL, 1)
    cal = runs.edges(store, full_b, cal_spec)
    p1, pr = cal.params["p_data"].value, cal.params["p_read"].value
    once = EffectiveNoise(p_data=p1, p_read=pr, wait=idle, pauli="Z")
    pred = curve(store, phen_b, lambda dt, R, s: MemorySpec(code, "X", Schedule.rounds(dt, R),
                                                             once, SHOTS, s), d, workers)
    # P2: measured edges at a few longer intervals against the one-calibration model.
    flat = []
    for dt in (2.0, 4.0, 8.0):
        e = runs.edges(store, full_b, MemorySpec(code, "X", Schedule.rounds(dt, R_CAL), noise,
                                                  SHOTS_CAL, 1))
        flat.append({"dt": dt,
                     "p_read / p_read(1)": e.params["p_read"].value / pr,
                     "p_data / [p_data(1) xor q_wait]":
                         e.params["p_data"].value / float(xor(p1, idle.pz(dt - 1.0)))})
    fo, po = full["optimum"], pred["optimum"]
    log(f"d={d} {label:<9}  dt* circuit {fo['dt_star']:6.2f} [{fo['lo']:.2f}, {fo['hi']:.2f}]"
        f"{'' if fo['interior'] else ' (edge)'}   predicted {po['dt_star']:6.2f} "
        f"({po['dt_star'] / fo['dt_star'] - 1:+.0%})   b_read {pr / p1:.3f}")
    return {"d": d, "idle": label, "idle_params": idle.__dict__, "full": full, "predicted": pred,
            "calibration": {"run_id": cal.parents[0], "p_data": p1, "p_read": pr,
                            "b_read": pr / p1, "estimator_broken": cal.info["estimator_broken"]},
            "p2_checks": flat}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gates", choices=list(GATE_BACKENDS), default="textbook")
    ap.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7])
    ap.add_argument("--idle", nargs="+", default=list(IDLE), choices=list(IDLE))
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/premise"))
    args = ap.parse_args(argv)
    store, t0 = Store(args.store), time.perf_counter()
    rows = [one(store, d, k, args.gates, args.workers) for d in args.distances for k in args.idle]
    parents = tuple(sorted({i for r in rows for part in ("full", "predicted")
                            for i in r[part]["run_ids"]} | {r["calibration"]["run_id"] for r in rows}))
    data = {"setup": {"gates": GATES, "T": T, "shots": SHOTS, "seeds": SEEDS, "R_cal": R_CAL,
                      "shots_cal": SHOTS_CAL, "placement": "uniform", "basis": "X",
                      "gates": args.gates},
            "rows": rows}
    did = store.save_derived(Derived(f"premise_{args.gates}_uniform", data, parents))
    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / f"premise_{args.gates}.json"
    out.write_text(json.dumps({"derived_id": did, **data}, indent=1))
    print(f"wrote {out} (derived {did}) in "
          f"{(time.perf_counter() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
