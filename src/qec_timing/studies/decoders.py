"""Does the decoder matter? (Original notebook 06b.)

The same full-circuit runs (premise study, native gates, uniform idle noise) are
decoded twice:
    full    PyMatching on the circuit's exact detector error model (hook errors,
            mid-round faults, correlated 2q faults: what Stim derives);
    paper   PyMatching on the paper's phenomenological model, with the measured
            p_data(dt) and p_read of the same circuit ("measured once",
            `EffectiveNoise`). A hand-built graph of this kind is what one decodes
            with if the device's error model is not known in detail.
Both DEMs use the standard detector layout, so they decode identical detection
events. The ratio p_L(paper) / p_L(full) is what the simpler decoder loses, and
whether its curve still has the same optimum.

    python -m qec_timing.studies.decoders --distances 3 5 7 --idle "lin 0.3"
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np

from qec_timing.analysis.interval import dt_grid, optimum, rate
from qec_timing.backends.stim_native import StimNativeBackend
from qec_timing.backends.stim_phenom import dem_for as phenom_dem
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.noise.effective import EffectiveNoise
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.store import Store
from qec_timing.studies import runs
from qec_timing.studies.premise import IDLE, R_CAL, SEEDS, SHOTS, SHOTS_CAL, T, circuit_noise


def study(store: Store, d: int, label: str, workers: int) -> dict:
    code, idle, backend = RotatedSurfaceCode(d), IDLE[label], StimNativeBackend()
    noise = circuit_noise(idle)
    cal = runs.edges(store, backend, MemorySpec(code, "X", Schedule.rounds(1.0, R_CAL), noise, SHOTS_CAL, 1))
    eff = EffectiveNoise(cal.params["p_data"].value, cal.params["p_read"].value, wait=idle, pauli="Z")
    specs, dems, keys = [], [], []
    for dt, R in dt_grid(T, d):
        for s in SEEDS:                                  # the premise study's runs: read from the store
            spec = MemorySpec(code, "X", Schedule.rounds(dt, R), noise, SHOTS, s)
            specs.append(spec)
            dems.append({"full": backend.dem(spec),
                         "paper": phenom_dem(MemorySpec(code, "X", spec.schedule, eff, SHOTS, s))})
            keys.append((dt, R))
    res = runs.decode_many(store, backend, specs, dems, workers)
    agg: dict = {}
    for (dt, R), r in zip(keys, res):
        a = agg.setdefault((dt, R), {"full": 0, "paper": 0, "shots": 0})
        a["full"] += r["full"]; a["paper"] += r["paper"]; a["shots"] += r["_shots"]
    pts = []
    for (dt, R), a in sorted(agg.items()):
        rf, sf = rate(a["full"], a["shots"], T)
        rp, sp = rate(a["paper"], a["shots"], T)
        pts.append({"dt": dt, "R": R, "shots": a["shots"], "fails_full": a["full"], "fails_paper": a["paper"],
                    "pL_full": a["full"] / a["shots"], "pL_paper": a["paper"] / a["shots"],
                    "r_full": rf, "sr_full": sf, "r_paper": rp, "sr_paper": sp})
    arr = lambda k: np.array([p[k] for p in pts])           # noqa: E731
    o_full = optimum(arr("dt"), arr("pL_full"), arr("r_full"), arr("sr_full")).as_dict()
    o_paper = optimum(arr("dt"), arr("pL_paper"), arr("r_paper"), arr("sr_paper")).as_dict()
    ratio = arr("pL_paper") / arr("pL_full")
    print(f"d={d} {label}: p_L(paper decoder)/p_L(full) = {ratio.min():.2f}-{ratio.max():.2f}; "
          f"dt* full {o_full['dt_star']:.2f}, paper-decoded {o_paper['dt_star']:.2f}")
    return {"d": d, "idle": label, "points": pts, "optimum_full": o_full, "optimum_paper": o_paper,
            "calibration": {"p_data": eff.p_data, "p_read": eff.p_read}}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--distances", type=int, nargs="+", default=[3, 5, 7])
    ap.add_argument("--idle", nargs="+", default=["lin 0.3"], choices=list(IDLE))
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/decoders"))
    a = ap.parse_args(argv)
    store = Store(a.store)
    rows = [study(store, d, k, a.workers) for d in a.distances for k in a.idle]
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "decoders.json").write_text(json.dumps({"setup": {"gates": "native", "T": T, "shots": SHOTS,
                                                               "seeds": SEEDS}, "rows": rows}, indent=1))
    print(f"wrote {a.out / 'decoders.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
