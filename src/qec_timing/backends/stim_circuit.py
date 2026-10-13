"""Circuit-level Stim backend: the rotated surface code's textbook extraction circuit
(Stim's generated memory circuit: H, four CX layers, H, measure-reset; 7 layers per
round) with `CircuitNoise` placed on it. Notebooks 07 and 08 of the original repo.

Stim's generated circuit labels qubits by coordinates and adds detectors for the
other check type from round 1 on. To give the same record layout as every other
backend (see `qec_timing.records`), the circuit is aligned to `RotatedSurfaceCode`:
the grid symmetry that maps Stim's checks onto ours is found and asserted, only
memory-basis detectors are kept, and they are ordered by our check index. The
other sector's detectors do not change the decoded observable (its faults never
flip it), and the random draws are untouched, so with the same seed this circuit
samples exactly what the original repo's did.

Noise is attached by tagging each noise location of the generated circuit with a
distinct placeholder probability and rewriting it.
"""

from __future__ import annotations

import importlib.metadata as md
from functools import lru_cache

import numpy as np
import stim

from qec_timing.codes.base import checks_of
from qec_timing.noise.circuit import CircuitNoise
from qec_timing.records import DetectorLayout, RawRecord
from qec_timing.registry import register
from qec_timing.spec import MemorySpec

LAYERS = 7                                     # TICKs per round in the generated circuit
_IDLE, _GATE, _MEAS, _RESET = 0.0123457, 0.0234568, 0.0345679, 0.0456781


def _is(x: float, tag: float) -> bool:
    return abs(x - tag) < 1e-9


def _generated(basis: str, d: int, rounds: int) -> stim.Circuit:
    return stim.Circuit.generated(
        f"surface_code:rotated_memory_{basis.lower()}", distance=d, rounds=rounds,
        before_round_data_depolarization=_IDLE, after_clifford_depolarization=_GATE,
        before_measure_flip_probability=_MEAS, after_reset_flip_probability=_RESET)


# --- alignment to RotatedSurfaceCode -------------------------------------------

_SYMMETRIES = [lambda r, c, n: (r, c), lambda r, c, n: (c, r),
               lambda r, c, n: (n - 1 - r, c), lambda r, c, n: (r, n - 1 - c),
               lambda r, c, n: (n - 1 - r, n - 1 - c), lambda r, c, n: (c, n - 1 - r),
               lambda r, c, n: (n - 1 - c, r), lambda r, c, n: (n - 1 - c, n - 1 - r)]


@lru_cache(maxsize=None)
def alignment(d: int, basis: str) -> dict[tuple[float, float], int]:
    """Ancilla coordinate (x, y) -> position in checks_of(RotatedSurfaceCode(d), basis).

    Stim's data qubit at (x, y) (odd coordinates) sits at grid (row, col) =
    ((y - 1) / 2, (x - 1) / 2). Of the 8 symmetries of the square, exactly the ones
    that map Stim's Z and X supports onto ours are accepted; none means the code
    and the circuit disagree, which is an error, never a fallback."""
    from qec_timing.codes.surface import RotatedSurfaceCode

    code = RotatedSurfaceCode(d)
    c = _generated(basis, d, 1)
    coords = c.get_final_qubit_coordinates()
    ancillas, x_anc, partners = set(), set(), {}
    for inst in c.flattened():
        t = [g.value for g in inst.targets_copy() if g.is_qubit_target]
        if inst.name == "MR":
            ancillas.update(t)
        elif inst.name == "H":
            x_anc.update(t)
        elif inst.name == "CX":
            for a, b in zip(t[::2], t[1::2]):
                partners.setdefault(a, set()).add(b)
                partners.setdefault(b, set()).add(a)
    grid = {q: (int((coords[q][1] - 1) / 2), int((coords[q][0] - 1) / 2))
            for q in coords if q not in ancillas}
    ours = {p: {frozenset(ch.support) for ch in checks_of(code, p)} for p in ("X", "Z")}
    position = {ch.support: i for i, ch in enumerate(checks_of(code, basis))}
    for g in _SYMMETRIES:
        sup = {a: tuple(sorted(code.index(*g(*grid[q], d)) for q in partners[a])) for a in ancillas}
        theirs = {p: {frozenset(sup[a]) for a in ancillas if (a in x_anc) == (p == "X")}
                  for p in ("X", "Z")}
        if theirs == ours:
            return {tuple(coords[a][:2]): position[sup[a]] for a in ancillas
                    if (a in x_anc) == (basis == "X")}
    raise AssertionError(f"Stim's rotated d={d} circuit matches RotatedSurfaceCode under no symmetry")


# --- the noisy, aligned circuit ------------------------------------------------

def build_circuit(spec: MemorySpec) -> stim.Circuit:
    noise: CircuitNoise = spec.noise
    d, basis, R = spec.code.d, spec.basis, spec.schedule.n_rounds
    dt = spec.schedule.dts[0]
    tagged = _generated(basis, d, R)
    position = alignment(d, basis)
    data = [t.value for t in [i for i in tagged.flattened() if i.name in ("M", "MX")][-1].targets_copy()]
    used = sorted({t.value for i in tagged.flattened() for t in i.targets_copy() if t.is_qubit_target})
    idle = noise.idle
    if noise.placement == "uniform":
        layer, wait = idle.channel(1.0 / LAYERS), idle.channel(dt - 1.0)
    else:
        layer, wait = None, idle.channel(dt)
    nonzero = lambda ch: any(v > 0 for v in ch)          # noqa: E731

    def flush(dets: list, out: stim.Circuit) -> None:
        keep = [(position[tuple(i.gate_args_copy()[:2])], i) for i in dets
                if tuple(i.gate_args_copy()[:2]) in position]
        for _, inst in sorted(keep, key=lambda x: x[0]):
            out.append(inst)
        dets.clear()

    def rewrite(block: stim.Circuit) -> stim.Circuit:
        out, dets = stim.Circuit(), []
        for inst in block:
            if isinstance(inst, stim.CircuitInstruction) and inst.name == "DETECTOR":
                dets.append(inst)
                continue
            flush(dets, out)
            if isinstance(inst, stim.CircuitRepeatBlock):
                out.append(stim.CircuitRepeatBlock(inst.repeat_count, rewrite(inst.body_copy())))
                continue
            name, args, tg = inst.name, inst.gate_args_copy(), inst.targets_copy()
            if name == "TICK":
                out.append(inst)
                if layer is not None and nonzero(layer):
                    out.append("PAULI_CHANNEL_1", used, list(layer))
            elif name == "DEPOLARIZE1" and _is(args[0], _IDLE):
                if noise.placement == "uniform":
                    if nonzero(wait):
                        out.append("PAULI_CHANNEL_1", used, list(wait))
                else:
                    out.append("PAULI_CHANNEL_1", tg, list(wait))
            elif name == "DEPOLARIZE1" and _is(args[0], _GATE):
                out.append("DEPOLARIZE1", tg, [noise.p1])
            elif name == "DEPOLARIZE2" and _is(args[0], _GATE):
                out.append("DEPOLARIZE2", tg, [noise.p2])
            elif name in ("X_ERROR", "Z_ERROR") and _is(args[0], _MEAS):
                out.append(name, tg, [noise.p_meas])
            elif name in ("X_ERROR", "Z_ERROR") and _is(args[0], _RESET):
                out.append(name, tg, [noise.p_init])
            else:
                out.append(inst)
        flush(dets, out)
        return out

    c = rewrite(tagged)
    assert sum(1 for i in c.flattened() if i.name == "TICK") == LAYERS * R
    assert not any(f"{v}" in str(c) for v in (_IDLE, _GATE, _MEAS, _RESET)), "untranslated tag"
    n_checks = len(checks_of(spec.code, basis))
    assert c.num_detectors == (R + 1) * n_checks, (c.num_detectors, R, n_checks)
    assert set(data) and len(data) == spec.code.n_data
    return c


def dem_for(spec: MemorySpec) -> str:
    """The circuit's exact detector error model (hook and correlated faults included),
    decomposed into graphlike parts for matching."""
    return str(build_circuit(spec).detector_error_model(decompose_errors=True))


@register("backend", "stim_circuit")
class StimCircuitBackend:
    name = "stim_circuit"

    def versions(self) -> dict[str, str]:
        return {"stim": md.version("stim")}

    def supports(self, spec: MemorySpec) -> str | None:
        if spec.code.name != "rotated_surface":
            return "builds on Stim's generated rotated surface-code circuit"
        if not isinstance(spec.noise, CircuitNoise):
            return "needs CircuitNoise"
        if not spec.schedule.is_constant:
            return "one interval per run (the generated circuit repeats one round)"
        if spec.noise.placement == "uniform" and spec.schedule.dts[0] < 1.0 - 1e-12:
            return "uniform placement: dt is the full round period, so dt >= 1"
        return None

    def dem(self, spec: MemorySpec) -> str:
        return dem_for(spec)

    def run(self, spec: MemorySpec) -> RawRecord:
        circuit = build_circuit(spec)
        det, obs = circuit.compile_detector_sampler(seed=spec.seed).sample(
            spec.shots, separate_observables=True)
        s = spec.schedule
        nan = np.full(s.n_rounds, np.nan)       # circuit noise has no per-round p_data / p_read;
        rounds = {"dt": np.array(s.dts), "t": np.array(s.starts),   # Extractor measures them
                  "p_data": nan, "p_read": nan.copy()}
        layout = DetectorLayout(s.n_rounds, len(checks_of(spec.code, spec.basis)))
        return RawRecord(layout, det, obs, rounds, payload={"seed": spec.seed, "layers": LAYERS})
