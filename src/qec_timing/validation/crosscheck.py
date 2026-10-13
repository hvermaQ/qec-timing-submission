"""Cross-check: the Guppy (validation) and Stim (production) backends must give the
same logical error rate for the same experiment.

This is what licenses running sweeps on Stim: Guppy injects the noise as a device
program would, Stim is ~orders of magnitude faster, and the two agree. Rerun this
whenever either backend, the code or the noise model changes.

Setup (as the original repo's Stage 4a, for comparability): rotated surface code,
Z-basis memory, paper noise p = 0.015, lam = 1, b_read = 1, total time T = 10, the
same six dt values per distance d = 5, 7, 9. Both backends' records are decoded
by the same PyMatching decoder built from each run's own DEM.

Agreement is judged three ways:
  per point:  the two 99.9% Clopper-Pearson intervals overlap;
  jointly:    chi^2 of the per-point z-scores (no point may be singled out);
  bias:       mean signed z, which catches a small consistent offset that no
              single point resolves.
The original Stage 4a numbers are compared the same way, as a regression check
of the port.

    python -m qec_timing.validation.crosscheck --store store --out results/crosscheck
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np

from qec_timing.backends.base import run_checked
from qec_timing.backends.guppy_phenom import GuppyPhenomBackend
from qec_timing.backends.stim_phenom import StimPhenomBackend, dem_for
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.decoders.base import logical_failures
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
from qec_timing.noise.paper import PaperNoise
from qec_timing.records import Derived
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec, overlapping_seed_ranges
from qec_timing.stats import Rate, pooled_agreement, rate_per_time
from qec_timing.store import Store

P, LAM, B_READ, T, TICK = 0.015, 1.0, 1.0, 10.0, 1e-5
BASE_SEED = 20261013
# Guppy seeds shot k with base + k, so two runs share noise wherever their ranges
# [base, base + shots) overlap. Correlated points would fake (or hide) a common
# bias in the joint test. Every Guppy run gets its own block of this size.
SEED_BLOCK = 10**7

# Original Stage 4a: (d, dt) -> (guppy failures, shots, reference failures, shots).
ORIGINAL = {
    (5, 0.14286): (98, 362, 4942, 20000), (5, 0.26008): (95, 473, 3551, 20000),
    (5, 0.47349): (87, 559, 2878, 20000), (5, 0.86203): (86, 558, 2702, 20000),
    (5, 1.56937): (81, 524, 2634, 20000), (5, 2.85714): (76, 349, 3668, 20000),
    (7, 0.09091): (77, 510, 3379, 20000), (7, 0.16551): (82, 803, 2374, 20000),
    (7, 0.30131): (73, 996, 1789, 20000), (7, 0.54856): (71, 1041, 1667, 20000),
    (7, 0.99869): (67, 850, 1800, 20000), (7, 1.81818): (64, 522, 2554, 20000),
    (9, 0.06667): (19, 225, 1123, 11110), (9, 0.12137): (24, 413, 1368, 20000),
    (9, 0.22096): (36, 752, 1072, 20000), (9, 0.40228): (68, 1355, 958, 20000),
    (9, 0.73237): (85, 1548, 1083, 20000), (9, 1.33333): (71, 873, 1595, 20000),
}


def spec_for(d: int, dt: float, shots: int, seed: int) -> MemorySpec:
    return MemorySpec(RotatedSurfaceCode(d), "Z", Schedule.fixed(dt, T, tick=TICK),
                      PaperNoise(P, LAM, B_READ), shots=shots, seed=seed)


def measure(store: Store, backend, spec: MemorySpec) -> tuple[str, Rate, float]:
    """Run (or reuse a stored run), decode, return (run_id, failures/shots, seconds)."""
    run_id = spec.run_id(backend.name)
    t0 = time.perf_counter()
    if store.has_run(run_id):
        _, record = store.load_run(run_id)
    else:
        record = run_checked(backend, spec)
        store.save_run(spec, backend.name, backend.versions(), record)
    fails = logical_failures(PyMatchingDecoder(dem_for(spec)), record.detectors,
                             record.observables)
    return run_id, Rate(int(fails.sum()), record.shots), time.perf_counter() - t0


def run(store: Store, target_failures: int, stim_shots: int, budget_s: float,
        log=print) -> Derived:
    guppy, stim_b = GuppyPhenomBackend(), StimPhenomBackend()
    rows, parents, guppy_specs = [], [], []
    for i, (d, dt) in enumerate(sorted(ORIGINAL)):
        # Stim first: its p_L sizes the Guppy run (one run() call per point, shots
        # chosen up front; per-call overhead makes sample-until-N wasteful).
        sid, s_rate, s_sec = measure(store, stim_b, spec_for(d, dt, stim_shots, BASE_SEED + 2 * i))
        # Per-shot Guppy cost, from a small calibration run, caps shots by time.
        cal = spec_for(d, dt, 20, BASE_SEED + (100 + i) * SEED_BLOCK)
        t0 = time.perf_counter()
        run_checked(guppy, cal)
        per_shot = (time.perf_counter() - t0) / cal.shots
        want = int(np.ceil(target_failures / max(s_rate.p, 1e-6)))
        shots = min(SEED_BLOCK, max(50, min(want, int(budget_s / per_shot))))
        g_spec = spec_for(d, dt, shots, BASE_SEED + (1 + i) * SEED_BLOCK)
        guppy_specs.append(g_spec)
        if overlapping_seed_ranges(guppy_specs):
            raise RuntimeError("Guppy seed ranges overlap: runs would share noise")
        gid, g_rate, g_sec = measure(store, guppy, g_spec)

        o = ORIGINAL[(d, dt)]
        n_rounds = spec_for(d, dt, 1, 0).schedule.n_rounds
        row = {"d": d, "dt": dt, "n_rounds": n_rounds,
               "guppy": {"run_id": gid, "failures": g_rate.k, "shots": g_rate.n,
                         "p_L": g_rate.p, "ci": g_rate.ci(), "seconds": g_sec,
                         "capped_by_time": shots < want},
               "stim": {"run_id": sid, "failures": s_rate.k, "shots": s_rate.n,
                        "p_L": s_rate.p, "ci": s_rate.ci(), "seconds": s_sec},
               "R_stim": rate_per_time(s_rate.p, n_rounds * dt),
               "original": {"guppy": [o[0], o[1]], "reference": [o[2], o[3]]}}
        lo_g, hi_g = row["guppy"]["ci"]
        lo_s, hi_s = row["stim"]["ci"]
        row["overlap"] = lo_g <= hi_s and lo_s <= hi_g
        rows.append(row)
        parents += [sid, gid]
        log(f"d={d} dt={dt:<8} rounds={n_rounds:<4} guppy {g_rate.p:.4f} ({g_rate.k}/{g_rate.n}) "
            f"stim {s_rate.p:.4f} ({s_rate.k}/{s_rate.n}) "
            f"{'OK' if row['overlap'] else 'DISAGREE'}  [{g_sec:.0f}s guppy]")

    pair = lambda a, b: (Rate(*a), Rate(*b))
    summary = {
        "guppy_vs_stim": pooled_agreement([pair((r["guppy"]["failures"], r["guppy"]["shots"]),
                                                (r["stim"]["failures"], r["stim"]["shots"]))
                                           for r in rows]),
        "stim_vs_original_reference": pooled_agreement(
            [pair((r["stim"]["failures"], r["stim"]["shots"]), r["original"]["reference"])
             for r in rows]),
        "original_guppy_vs_original_reference": pooled_agreement(
            [pair(r["original"]["guppy"], r["original"]["reference"]) for r in rows]),
        "points_overlapping": sum(r["overlap"] for r in rows),
        "points": len(rows),
    }
    return Derived("crosscheck_guppy_stim",
                   {"setup": {"p": P, "lam": LAM, "b_read": B_READ, "T": T, "basis": "Z",
                              "code": "rotated_surface", "decoder": "pymatching",
                              "target_failures": target_failures, "stim_shots": stim_shots,
                              "guppy_budget_s_per_point": budget_s},
                    "summary": summary, "rows": rows},
                   tuple(parents))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", type=Path, default=Path("store"))
    ap.add_argument("--out", type=Path, default=Path("results/crosscheck"))
    ap.add_argument("--target-failures", type=int, default=300)
    ap.add_argument("--stim-shots", type=int, default=200_000)
    ap.add_argument("--budget", type=float, default=240.0, help="Guppy seconds per point")
    args = ap.parse_args(argv)

    store = Store(args.store)
    t0 = time.perf_counter()
    derived = run(store, args.target_failures, args.stim_shots, args.budget)
    did = store.save_derived(derived)
    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / "crosscheck.json"
    out.write_text(json.dumps({"derived_id": did, **derived.data}, indent=2))
    s = derived.data["summary"]
    print(f"\n{s['points_overlapping']}/{s['points']} points overlap at 99.9%")
    for k in ("guppy_vs_stim", "stim_vs_original_reference", "original_guppy_vs_original_reference"):
        v = s[k]
        print(f"{k}: chi2 = {v['chi2']:.1f} on {v['n_points']} dof (p = {v['chi2_p']:.3f}), "
              f"mean z = {v['mean_z']:+.2f} ({v['mean_z_sigma']:+.1f} sigma)")
    print(f"wrote {out} (derived {did}) in {(time.perf_counter() - t0) / 60:.1f} min")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
