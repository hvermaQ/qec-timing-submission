"""Guppy/Selene backend for phenomenological noise: the validation path.

The noise is injected inside the Guppy program, as it would run on a device:
gates and measurements are ideal, and every fault is an explicit, seeded draw.

Rules this program keeps (each one broke something once):
- ONE `RNG` per program, passed borrowed through every helper: a second
  `RNG(seed)` reseeds Selene's global runtime PRNG.
- Shot k is seeded base_seed + k (get_current_shot). A fixed seed would give
  identical noise in every shot. `with_seed` does not reach these draws.
- ONE Bernoulli draw per data qubit per round, at p_data (paper Eq. 2).
- Readout noise flips the classical record, never the qubit.
- Detection events are computed in-program and emitted bit-packed (64-bit words,
  LSB first), one block per round plus the final block.

Extraction is the simplest circuit equivalent to an ideal product measurement:
one fresh ancilla per check, coupled to the check's support in its extraction
order, then measured. Z checks: CX(data -> ancilla). X checks: ancilla in |+>,
CX(ancilla -> data), measured in X. Works for any CSS code via `StabilizerCode`.

Geometry and basis are compile-time (Guppy needs comptime array sizes), so one
binary is compiled per (code, basis) and cached; noise, rounds and seed are
runtime arguments, so a whole dt sweep reuses one binary.
"""

from __future__ import annotations

import importlib.metadata as md
import json
import math
from typing import Any

import numpy as np
from guppylang import guppy
from guppylang.std.array import array
from guppylang.std.builtins import comptime, nat, output
from guppylang.std.qsystem.random import RNG
from guppylang.std.qsystem.utils import get_current_shot
from guppylang.std.quantum import cx, h, measure, measure_array, qubit, x, z

from qec_timing.codes.base import StabilizerCode, checks_of
from qec_timing.noise.base import PhenomenologicalNoise
from qec_timing.records import DetectorLayout, RawRecord, unpack_bits
from qec_timing.registry import register
from qec_timing.spec import MemorySpec

WORD_BITS = 64
# Generic array length. The Python name must equal the string: Guppy resolves
# `range(N)` by that name.
N = guppy.nat_var("N")


# --- noise primitives (RNG borrowed, never owned) ---------------------------

@guppy
def bernoulli(rng: RNG, p: float) -> bool:
    # random_float() is uniform on [0, 1): "< p" fires with probability exactly p.
    return rng.random_float() < p


@guppy
def flip_record(rng: RNG, bit: bool, p: float) -> bool:
    if bernoulli(rng, p):
        return not bit
    return bit


@guppy
def x_noise(rng: RNG, data: array[qubit, N], p: float) -> None:
    for i in range(N):
        if bernoulli(rng, p):
            x(data[i])


@guppy
def z_noise(rng: RNG, data: array[qubit, N], p: float) -> None:
    for i in range(N):
        if bernoulli(rng, p):
            z(data[i])


@guppy
def x_flip(data: array[qubit, N], i: int) -> None:
    x(data[i])


@guppy
def z_flip(data: array[qubit, N], i: int) -> None:
    z(data[i])


# --- program builder ---------------------------------------------------------

def _build(code: StabilizerCode, basis: str, noise_pauli: str):
    checks = checks_of(code, basis)
    n_data, n_checks = code.n_data, len(checks)
    max_w = max(len(c.support) for c in checks)
    # Supports in extraction order, padded with -1 to a fixed width.
    table = [q for c in checks for q in (list(c.extraction_order) + [-1] * (max_w - len(c.support)))]
    n_words = math.ceil(n_checks / WORD_BITS)
    logical = list(code.logical(basis))
    n_log = len(logical)
    noise_fn = x_noise if noise_pauli == "X" else z_noise
    flip_fn = x_flip if noise_pauli == "X" else z_flip
    x_basis = basis == "X"

    @guppy
    def emit(det: array[bool, N]) -> None:
        words = array(nat(0) for _ in range(comptime(n_words)))
        for ci in range(comptime(n_checks)):
            if det[ci]:
                w = ci // comptime(WORD_BITS)
                words[w] = words[w] | (nat(1) << nat(ci % comptime(WORD_BITS)))
        output("det", words)

    @guppy
    def program(p_data: float, p_read: float, p_final: float, dt: float, n_rounds: int,
                base_seed: int, inject_round: int, inject_qubit: int) -> None:
        rng = RNG(base_seed + int(get_current_shot()))
        data = array(qubit() for _ in range(comptime(n_data)))
        if comptime(x_basis):
            for i in range(comptime(n_data)):
                h(data[i])                                   # |+>^n: +1 for every X check
        prev = array(False for _ in range(comptime(n_checks)))

        j = 0
        while j < n_rounds:
            noise_fn(rng, data, p_data)                       # before extraction, one draw each
            if j == inject_round:
                if inject_qubit >= 0:
                    flip_fn(data, inject_qubit)
            det = array(False for _ in range(comptime(n_checks)))
            for ci in range(comptime(n_checks)):
                anc = qubit()
                if comptime(x_basis):
                    h(anc)
                for k in range(comptime(max_w)):
                    q = comptime(table)[ci * comptime(max_w) + k]
                    if q >= 0:
                        if comptime(x_basis):
                            cx(anc, data[q])
                        else:
                            cx(data[q], anc)
                if comptime(x_basis):
                    h(anc)
                s = flip_record(rng, measure(anc).read(), p_read)
                det[ci] = s != prev[ci]                       # paper Eq. A1
                prev[ci] = s
            emit(det)
            j += 1

        if comptime(x_basis):
            for i in range(comptime(n_data)):
                h(data[i])
        measured = measure_array(data)
        final = array(False for _ in range(comptime(n_data)))
        for i in range(comptime(n_data)):
            final[i] = flip_record(rng, measured[i].read(), p_final)

        last = array(False for _ in range(comptime(n_checks)))
        for ci in range(comptime(n_checks)):
            parity = False
            for k in range(comptime(max_w)):
                q = comptime(table)[ci * comptime(max_w) + k]
                if q >= 0:
                    if final[q]:
                        parity = not parity
            last[ci] = parity != prev[ci]
        emit(last)

        obs = False
        for t in range(comptime(n_log)):
            if final[comptime(logical)[t]]:
                obs = not obs
        output("obs", obs)
        rng.discard()

    return program.emulator(n_qubits=n_data + 1).stabilizer_sim(), n_checks, n_words


@register("backend", "guppy_phenom")
class GuppyPhenomBackend:
    name = "guppy_phenom"
    per_shot_seeded = True               # shot k is seeded seed + k

    def __init__(self) -> None:
        self._cache: dict[str, Any] = {}

    def versions(self) -> dict[str, str]:
        return {p: md.version(p) for p in ("guppylang", "selene-sim")}

    def supports(self, spec: MemorySpec) -> str | None:
        if not isinstance(spec.noise, PhenomenologicalNoise):
            return "needs a phenomenological noise model"
        if not spec.schedule.is_constant:
            return "runtime arguments carry one dt per run; variable schedules not built yet"
        s = spec.schedule
        if len({spec.noise.round_noise(t, dt) for t, dt in zip(s.starts, s.dts)}) != 1:
            return "round noise varies across rounds; the program takes one value per run"
        return None

    def _program(self, spec: MemorySpec):
        key = json.dumps([spec.code.name, spec.code.params(), spec.basis, spec.noise.data_pauli],
                         sort_keys=True)
        if key not in self._cache:
            self._cache[key] = _build(spec.code, spec.basis, spec.noise.data_pauli)
        return self._cache[key]

    def dem(self, spec: MemorySpec) -> str:
        # Same model and detector layout as the Stim phenomenological circuit.
        from qec_timing.backends.stim_phenom import dem_for
        return dem_for(spec)

    def run(self, spec: MemorySpec) -> RawRecord:
        emulator, n_checks, n_words = self._program(spec)
        s = spec.schedule
        rn = spec.noise.round_noise(s.starts[0], s.dts[0])
        inject = spec.extra.get("inject", (-1, -1))
        result = emulator.with_shots(spec.shots).with_seed(spec.seed).run(
            p_data=rn.p_data, p_read=rn.p_read, p_final=spec.noise.final_read(), dt=s.dts[0],
            n_rounds=s.n_rounds, base_seed=spec.seed,
            inject_round=int(inject[0]), inject_qubit=int(inject[1]))

        layout = DetectorLayout(s.n_rounds, n_checks)
        det = np.zeros((spec.shots, layout.n_detectors), dtype=bool)
        obs = np.zeros((spec.shots, 1), dtype=bool)
        for k, shot in enumerate(result.results):
            tags = shot.collate_tags()                   # never as_dict(): it drops repeats
            words = np.asarray(tags["det"], dtype=np.uint64).reshape(s.n_rounds + 1, n_words)
            det[k] = unpack_bits(words, n_checks).reshape(-1)
            obs[k, 0] = bool(tags["obs"][0])
        rounds = {"dt": np.array(s.dts), "t": np.array(s.starts),
                  "p_data": np.full(s.n_rounds, rn.p_data),
                  "p_read": np.full(s.n_rounds, rn.p_read)}
        return RawRecord(layout, det, obs, rounds,
                         payload={"base_seed": spec.seed, "p_final": spec.noise.final_read()})
