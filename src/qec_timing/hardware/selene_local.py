"""Run the hardware QIR program locally on Selene, before spending anything on a device.
H2 env ONLY.

The same traced Guppy 0.21 program that `hardware.qir` converts to QIR is built
with Selene and run on its stabilizer simulator with no error model, so the only
noise is what the program injects. Its output tags go through
`hardware.records`, exactly as device results will. Passing the backend contract
on this backend therefore checks the program, its tags and the record
conversion end to end.

Readout and gate noise belong to the device, so specs asking for record flips
are refused here.
"""

from __future__ import annotations

import importlib.metadata as md

from qec_timing.codes.base import checks_of
from qec_timing.hardware.qir import build_program
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.noise.base import PhenomenologicalNoise
from qec_timing.records import RawRecord
from qec_timing.registry import register
from qec_timing.spec import MemorySpec


@register("backend", "selene_qir_program")
class SeleneQirProgramBackend:
    name = "selene_qir_program"
    per_shot_seeded = True               # shot k is seeded seed + k

    def __init__(self) -> None:
        self._built: dict[str, object] = {}

    def versions(self) -> dict[str, str]:
        return {p: md.version(p) for p in ("guppylang", "selene-sim")}

    def supports(self, spec: MemorySpec) -> str | None:
        if spec.code.n_data + 1 > 56:
            return "more qubits than H2's stabilizer simulator"
        if isinstance(spec.noise, PhenomenologicalNoise):
            s = spec.schedule
            rn = {spec.noise.round_noise(t, dt) for t, dt in zip(s.starts, s.dts)}
            if len(rn) != 1:
                return "injection is compile-time: one p_data for all rounds"
            if next(iter(rn)).p_read or spec.noise.final_read():
                return "readout noise is the device's; the program injects data flips only"
        return None

    def run(self, spec: MemorySpec) -> RawRecord:
        from selene_sim import Stim, build

        key = spec.run_id(self.name) + str(spec.shots)
        inst = self._built.get(key) or build(build_program(spec).compile())
        self._built[key] = inst
        n = spec.code.n_data + 1
        shots = [dict(shot) for shot in inst.run_shots(simulator=Stim(), n_qubits=n,
                                                        n_shots=spec.shots, random_seed=spec.seed)]
        syn, dat = bits_from_shots(shots, spec.schedule.n_rounds,
                                   len(checks_of(spec.code, spec.basis)), spec.code.n_data)
        rec = record_from_bits(spec, syn, dat, payload={"base_seed": spec.seed})
        if isinstance(spec.noise, PhenomenologicalNoise):   # report the injected noise
            rn = spec.noise.round_noise(spec.schedule.starts[0], spec.schedule.dts[0])
            rec.rounds["p_data"][:] = rn.p_data
            rec.rounds["p_read"][:] = 0.0
        return rec
