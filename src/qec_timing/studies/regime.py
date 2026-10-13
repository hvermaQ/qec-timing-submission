"""Is a non-trivial syndrome interval worth it on a given device? (Narrative points 10, 13.)

Input: a `Calibration` file (gate, readout and idle-dephasing parameters, with a
source) and candidate round durations t_R, because t_R is what decides the answer
and is not published for H2. For each (t_R, d) the full circuit is simulated at
the device's own rates (no scaling), over a log grid of intervals dt (in rounds,
>= 1), and the study reports:

    dt*        the optimum interval, in rounds and in seconds;
    gain       R(dt = 1) / R(lowest)  -- what an optimised interval buys over
               extracting back to back, with its significance;
    regime     "wait" if the gain is significant (> 3 sigma), else "back to back".

Rounds per point are fixed (N = `--rounds`), so T = N * dt and the rate is
R = -ln(1 - 2 p_L) / (2 T). Shots are sized per point from a pilot run so each
point has ~`--target` failures (capped by `--max-shots`). Every run is stored.

When new device numbers arrive, write a new calibration file and rerun; nothing
else changes:

    python -m qec_timing.studies.regime --calibration config/h2_1e_emulator.json \\
        --t-round 0.002 0.02 0.1 0.3 --distances 3 5 --workers 12
"""

from __future__ import annotations

import argparse
import json
import math
import time
from pathlib import Path

import numpy as np

from qec_timing.analysis.interval import optimum
from qec_timing.backends.stim_circuit import StimCircuitBackend
from qec_timing.backends.stim_native import StimNativeBackend
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.hardware import Calibration
from qec_timing.noise.circuit import CircuitNoise
from qec_timing.records import Derived
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.stats import rate_per_time
from qec_timing.store import Store
from qec_timing.studies import runs

GATE_BACKENDS = {"textbook": StimCircuitBackend, "native": StimNativeBackend}
SEED_BASE = 31_000_000


def dt_rounds_grid(dt_max: float, n: int) -> list[float]:
    """Log grid of intervals in rounds, from back to back (1) to dt_max."""
    return [float(x) for x in np.geomspace(1.0, dt_max, n)]


def study(store, cal, t_round, d, gates, grid, n_rounds, target, max_shots, workers, log=print):
    code = RotatedSurfaceCode(d)
    noise = CircuitNoise.from_calibration(cal, t_round, placement="uniform")
    backend = GATE_BACKENDS[gates]()
    seeds = [SEED_BASE + 10 * i + 1000 * d for i in range(len(grid))]
    # Pilots for every point in parallel, then the sized runs in parallel.
    pilots = runs.failures_many(store, backend, [
        MemorySpec(code, "X", Schedule.rounds(dt, n_rounds), noise, 20_000, s)
        for dt, s in zip(grid, seeds)], workers)
    sized = []
    for (dt, s), (_, f, n) in zip(zip(grid, seeds), pilots):
        extra = int(min(max_shots, max(0, math.ceil(target / max(f / n, 1 / n)) - n)))
        if extra:
            sized.append(MemorySpec(code, "X", Schedule.rounds(dt, n_rounds), noise, extra, s + 1))
    more = {(sp.schedule.dts[0], sp.seed - 1): r
            for sp, r in zip(sized, runs.failures_many(store, backend, sized, workers))}
    rows = []
    for (dt, s), (rid, f, n) in zip(zip(grid, seeds), pilots):
        ids = [rid]
        if (dt, s) in more:
            rid2, f2, n2 = more[(dt, s)]
            f, n, ids = f + f2, n + n2, ids + [rid2]
        T = n_rounds * dt
        pL = f / n
        r = rate_per_time(pL, T)
        sr = math.sqrt(max(pL * (1 - pL), 1e-12) / n) / ((1 - 2 * pL) * T) if pL < 0.5 else math.nan
        rows.append({"dt": dt, "failures": f, "shots": n, "pL": pL,
                     "r": r if math.isfinite(r) else math.nan, "sr": sr, "run_ids": ids})
    a = {k: np.array([x[k] for x in rows]) for k in ("dt", "pL", "r", "sr")}
    # Usable points:
    #  - valid: the quadratic idle term sin^2(omega t / 2) is a twirled coherent
    #    rotation and is periodic; past omega * t = pi it "rephases", which no real
    #    decohering qubit does. Points with omega * dt * t_R >= pi are outside the
    #    model and are reported but never used.
    #  - unsaturated: p_L < 0.45, and nothing after the first saturated point (a
    #    later dip below 0.45 is the rephasing artefact or noise, not recovery).
    omega = cal.omega
    valid = omega * a["dt"] * t_round < math.pi
    saturated = ~(np.isfinite(a["r"]) & (a["pL"] < 0.45))
    first_sat = int(np.argmax(saturated)) if saturated.any() else len(rows)
    ok = valid & ~saturated & (np.arange(len(rows)) < first_sat)
    for x, v, u in zip(rows, valid, ok):
        x["model_valid"], x["used"] = bool(v), bool(u)
    i = int(np.nanargmin(np.where(ok, a["r"], np.nan)))
    gain = a["r"][0] / a["r"][i]
    z = (a["r"][0] - a["r"][i]) / math.hypot(a["sr"][0], a["sr"][i]) if i else 0.0
    opt = (optimum(a["dt"][ok], a["pL"][ok], a["r"][ok], a["sr"][ok]).as_dict()
           if i and ok.sum() >= 5 else None)
    regime = "wait" if (i and z > 3) else "back to back"
    n_used = int(ok.sum())
    dt_star = opt["dt_star"] if opt else 1.0
    log(f"t_R={t_round * 1e3:7.1f} ms  d={d}  idle/round {noise.idle.pz(1.0):.2e} "
        f"(p2 {cal.p2:.2e})  lowest dt {a['dt'][i]:6.1f}  dt* {dt_star:6.1f} rounds "
        f"= {dt_star * t_round * 1e3:7.1f} ms  gain x{gain:.2f} ({z:.1f} sigma)  -> {regime}"
        f"  [{n_used}/{len(rows)} points used]")
    return {"t_round": t_round, "d": d, "idle_per_round": noise.idle.pz(1.0),
            "idle_over_p2": noise.idle.pz(1.0) / cal.p2, "points": rows,
            "lowest_dt": float(a["dt"][i]), "optimum": opt, "dt_star_rounds": dt_star,
            "dt_star_seconds": dt_star * t_round, "gain": float(gain), "gain_sigma": float(z),
            "regime": regime, "points_used": n_used}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--calibration", type=Path, required=True)
    ap.add_argument("--t-round", type=float, nargs="+", required=True, help="seconds per round")
    ap.add_argument("--distances", type=int, nargs="+", default=[3, 5])
    ap.add_argument("--gates", choices=list(GATE_BACKENDS), default="textbook")
    ap.add_argument("--dt-max", type=float, default=256.0, help="longest interval, rounds")
    ap.add_argument("--points", type=int, default=14)
    ap.add_argument("--rounds", type=int, default=60, help="rounds per run (T = rounds * dt)")
    ap.add_argument("--target", type=int, default=400, help="failures per point")
    ap.add_argument("--max-shots", type=int, default=2_000_000)
    ap.add_argument("--workers", type=int, default=1)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/regime"))
    args = ap.parse_args(argv)

    cal = Calibration.load(args.calibration)
    store, t0 = Store(args.store), time.perf_counter()
    grid = dt_rounds_grid(args.dt_max, args.points)
    rows = [study(store, cal, t, d, args.gates, grid, args.rounds, args.target, args.max_shots,
                  args.workers) for t in args.t_round for d in args.distances]
    data = {"calibration": {"file": str(args.calibration), **json.loads(args.calibration.read_text())},
            "setup": {k: getattr(args, k) for k in ("gates", "dt_max", "points", "rounds", "target",
                                                    "max_shots")},
            "rows": rows}
    parents = tuple(sorted({i for r in rows for p in r["points"] for i in p["run_ids"]}))
    did = store.save_derived(Derived("regime", data, parents))
    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / f"regime_{args.calibration.stem}_{args.gates}.json"
    out.write_text(json.dumps({"derived_id": did, **data}, indent=1, default=float))
    print(f"wrote {out} (derived {did}) in {(time.perf_counter() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
