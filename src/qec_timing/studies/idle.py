"""How long do logical qubits idle in compiled applications? (Notebook 01.)

For each application and time model: the idle share of each qubit's active span,
and how that idle time is split into stretches. A stretch of L logical steps is a
memory interval of about L * d syndrome rounds (assumed: d rounds per logical
step, the usual lattice-surgery time unit), which is where the syndrome interval
is chosen. The share of idle time in stretches of at least `--rounds-threshold`
rounds says how much of it an optimised interval can act on.

    python -m qec_timing.studies.idle --d 5 --rounds-threshold 40
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qec_timing.apps.library import QFT, CuccaroAdder, IsingTrotter

APPS = {"QFT-16": QFT(16), "Ising-16x8": IsingTrotter(16, 8), "Adder-8": CuccaroAdder(8)}
STEP_THRESHOLDS = (1, 2, 5, 10, 20, 50)


def summarise(d: int, rounds_threshold: float) -> list[dict]:
    rows = []
    for label, src in APPS.items():
        for tm in ("uniform", "magic"):
            p = src.idle_profile(tm)
            flat = [x for s in p.stretches for x in s]
            rows.append({
                "app": label, "source": src.name, "params": src.params(), "time_model": tm,
                "qubits": p.n_qubits, "steps": p.steps, "idle_fraction": p.idle_fraction,
                "stretches": len(flat), "longest_stretch_steps": max(flat, default=0.0),
                "share_in_stretches_ge_steps": {L: p.share_in_stretches_at_least(L)
                                                for L in STEP_THRESHOLDS},
                "share_in_stretches_ge_rounds": p.share_in_stretches_at_least(rounds_threshold / d),
            })
    return rows


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--d", type=int, default=5, help="code distance: rounds per logical step")
    ap.add_argument("--rounds-threshold", type=float, default=40.0,
                    help="report the idle share in stretches at least this many rounds long")
    ap.add_argument("--out", type=Path, default=Path("results/idle"))
    args = ap.parse_args(argv)
    rows = summarise(args.d, args.rounds_threshold)
    print(f"{'app':<12}{'model':<9}{'idle':>6}{'>=10 steps':>12}{f'>={args.rounds_threshold:g} rounds':>14}"
          f"{'longest':>9}")
    for r in rows:
        print(f"{r['app']:<12}{r['time_model']:<9}{r['idle_fraction']:>6.0%}"
              f"{r['share_in_stretches_ge_steps'][10]:>12.0%}{r['share_in_stretches_ge_rounds']:>14.0%}"
              f"{r['longest_stretch_steps']:>9.0f}")
    args.out.mkdir(parents=True, exist_ok=True)
    out = args.out / "idle.json"
    out.write_text(json.dumps({"d": args.d, "rounds_threshold": args.rounds_threshold,
                               "rows": rows}, indent=1))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
