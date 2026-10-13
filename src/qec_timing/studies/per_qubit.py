"""Per-data-qubit error of one extraction round, and where it comes from.
(Original notebooks 04/04c: per-qubit cost, own vs propagated faults.)

The paper's model gives every data qubit the same flip probability per round. A
real extraction circuit does not: a qubit's error depends on how many CNOTs it
sits in, at which end, and on faults that spread to it from ancillas. Here this is
computed directly, without inverting measured rates: one round of the actual noisy
circuit (textbook or native gates) is run in Stim's Pauli-frame simulator, cut right
after the round's last ancilla measurement, and the frame on each data qubit is
read. The error that matters for an X-basis memory is a Z component (Z or Y).

The total is split by source, by keeping only one class of noise channels:
    idle     the idle channel (PAULI_CHANNEL_1);
    data     noise acting on the data qubits themselves: their 1q noise, and the
             components of each 2q gate's depolarizing channel that act on data;
    ancilla  noise acting only on ancillas (1q noise, reset and pre-measurement
             flips, and the ancilla-only components of 2q channels), which reaches
             data only by propagating through later CNOTs (hook errors).
The parts compose (XOR) to about the total; the difference is their overlap.

    python -m qec_timing.studies.per_qubit --distances 3 5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import stim

from qec_timing.backends.stim_circuit import _generated, build_circuit
from qec_timing.backends.stim_native import StimNativeBackend, stim_layout
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.noise.circuit import CircuitNoise, IdleNoise
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.studies.premise import GATES, P2

_PAIRS = [(a, b) for a in "IXYZ" for b in "IXYZ"][1:]     # PAULI_CHANNEL_2 argument order
NOISE_OPS = {"DEPOLARIZE1", "DEPOLARIZE2", "PAULI_CHANNEL_1", "X_ERROR", "Z_ERROR", "Y_ERROR"}


def one_round(spec: MemorySpec, gates: str) -> tuple[stim.Circuit, list[int], list[tuple[float, float]]]:
    """(circuit up to the end of round 1, data qubit ids, data (row, col) on Stim's grid)."""
    d, basis = spec.code.d, spec.basis
    L = stim_layout(d, basis)
    coords = _generated(basis, d, 1).get_final_qubit_coordinates()
    grid = [((coords[q][1] - 1) / 2, (coords[q][0] - 1) / 2) for q in L["data"]]
    if gates == "textbook":
        c, data = build_circuit(spec), list(L["data"])
    else:
        b = StimNativeBackend()
        c = b.circuit(spec)
        ops = b.native_ops(d, basis, spec.schedule.n_rounds)
        data = [o["qubit"] for o in ops if o["op"] == "Reset"][: len(L["data"])]
        # Selene allocates the data array first: qs[i] is qubit i, in Stim's data order.
        assert data == list(range(len(L["data"]))), "unexpected native data qubit ids"
    n_anc = len(L["zanc"]) + len(L["xanc"])
    dataset, out, seen = set(data), stim.Circuit(), 0
    for inst in c.flattened():
        if inst.name in ("DETECTOR", "OBSERVABLE_INCLUDE"):
            continue
        out.append(inst)
        if inst.name in ("M", "MR", "MX", "MRX"):
            seen += sum(1 for t in inst.targets_copy() if t.value not in dataset)
            if seen >= n_anc:
                break
    return out, data, grid


def keep_noise(c: stim.Circuit, data: set[int], kind: str) -> stim.Circuit:
    """The circuit with only one class of noise channels (see module docstring)."""
    out = stim.Circuit()
    for inst in c:
        if inst.name not in NOISE_OPS:
            out.append(inst)
            continue
        t = [x.value for x in inst.targets_copy()]
        args = inst.gate_args_copy()
        if inst.name == "PAULI_CHANNEL_1":
            if kind == "idle":
                out.append(inst)
        elif inst.name == "DEPOLARIZE2":
            # Split each pair's channel into the Pauli components that act on the data
            # qubit ("data") and those acting only on the ancilla ("ancilla": they reach
            # data only by propagating through later CNOTs, e.g. hooks).
            for q1, q2 in zip(t[::2], t[1::2]):
                probs = []
                for a, b in _PAIRS:
                    on_data = (a != "I" and q1 in data) or (b != "I" and q2 in data)
                    probs.append(args[0] / 15 if on_data == (kind == "data") else 0.0)
                if kind in ("data", "ancilla") and any(probs):
                    out.append("PAULI_CHANNEL_2", [q1, q2], probs)
        else:
            sel = [q for q in t if (q in data) == (kind == "data")]
            if kind in ("data", "ancilla") and sel:
                out.append(inst.name, sel, args)
    return out


def frame_rates(c: stim.Circuit, data: list[int], shots: int, seed: int) -> dict[str, np.ndarray]:
    sim = stim.FlipSimulator(batch_size=shots, disable_stabilizer_randomization=True, seed=seed)
    sim.do(c)
    xs, zs = sim.to_numpy(output_xs=True, output_zs=True)[:2]     # (xs, zs, None, None, None)
    return {"x": xs[data].mean(axis=1), "z": zs[data].mean(axis=1)}


def study(d: int, gates: str, idle: IdleNoise, shots: int, seed: int) -> dict:
    noise = CircuitNoise(**GATES, idle=idle, placement="uniform")
    spec = MemorySpec(RotatedSurfaceCode(d), "X", Schedule.rounds(1.0, 1), noise, 1, seed)
    c, data, grid = one_round(spec, gates)
    parts = {"total": frame_rates(c, data, shots, seed)}
    for kind in ("idle", "data", "ancilla"):
        parts[kind] = frame_rates(keep_noise(c, set(data), kind), data, shots, seed + 1)
    z = {k: v["z"] for k, v in parts.items()}
    print(f"d={d} {gates:<8} Z flip per round: mean {z['total'].mean():.2e}, "
          f"min {z['total'].min():.2e}, max {z['total'].max():.2e} "
          f"(max/min {z['total'].max() / max(z['total'].min(), 1e-12):.1f}); "
          f"share propagated from ancillas {z['ancilla'].sum() / z['total'].sum():.0%}")
    return {"d": d, "gates": gates, "grid": grid,
            "z": {k: v.tolist() for k, v in z.items()},
            "x_total": parts["total"]["x"].tolist(), "shots": shots}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--distances", type=int, nargs="+", default=[3, 5])
    ap.add_argument("--shots", type=int, default=400_000)
    ap.add_argument("--out", type=Path, default=Path("results/per_qubit"))
    a = ap.parse_args(argv)
    idle = IdleNoise(gamma=0.3 * P2)          # premise study's linear idle noise, one round (dt = 1)
    rows = [study(d, g, idle, a.shots, 51_000_000 + 10 * d) for d in a.distances
            for g in ("textbook", "native")]
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "per_qubit.json").write_text(json.dumps(
        {"setup": {"gates": GATES, "idle": idle.__dict__, "basis": "X", "rounds": 1,
                   "shots": a.shots}, "rows": rows}, indent=1))
    print(f"wrote {a.out / 'per_qubit.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
