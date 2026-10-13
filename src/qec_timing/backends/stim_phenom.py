"""Stim backend for phenomenological noise: the fast (production) path for sweeps.

Circuit per round j, for a memory in basis B:
  1. data flips of the noise's Pauli type with probability p_data_j;
  2. ideal product measurement (MPP) of every B check, whose RECORD is flipped
     with probability p_read_j (MPP(p) flips the reported bit, not the state);
  3. detectors s_j XOR s_{j-1}; round 0 compares with the ideal initial value.
Then a final data readout in basis B with record flips, final detectors (check
parity of the readout vs the last syndrome) and the logical observable.

Works for any CSS code through the `StabilizerCode` interface. Optional
`spec.extra["inject"] = [round, qubit]` applies one deterministic data flip
before extraction in that round (used to prove detector ordering across backends).
"""

from __future__ import annotations

import importlib.metadata as md

import numpy as np
import stim

from qec_timing.codes.base import checks_of
from qec_timing.noise.base import PhenomenologicalNoise
from qec_timing.records import DetectorLayout, RawRecord
from qec_timing.registry import register
from qec_timing.spec import MemorySpec

_ERROR = {"X": "X_ERROR", "Z": "Z_ERROR"}
_TARGET = {"X": stim.target_x, "Z": stim.target_z}
_MEASURE = {"X": "MX", "Z": "M"}
_RESET = {"X": "RX", "Z": "R"}


def round_noise(spec: MemorySpec):
    s = spec.schedule
    return [spec.noise.round_noise(t, dt) for t, dt in zip(s.starts, s.dts)]


def build_circuit(spec: MemorySpec, noise=None) -> stim.Circuit:
    """The memory circuit of `spec`. `noise` overrides the per-round noise, e.g. to
    build a decoder from believed rather than true probabilities."""
    code, basis = spec.code, spec.basis
    noise = round_noise(spec) if noise is None else noise
    checks = checks_of(code, basis)
    C, n = len(checks), code.n_data
    data = list(range(n))
    err = _ERROR[spec.noise.data_pauli]
    inject = spec.extra.get("inject")

    c = stim.Circuit()
    c.append(_RESET[basis], data)                    # logical B eigenstate (+1 for all B checks)
    for j, rn in enumerate(noise):
        c.append(err, data, rn.p_data)              # one draw per qubit per round
        if inject is not None and inject[0] == j:
            c.append(err, [inject[1]], 1.0)
        for chk in checks:
            targets = []
            for k, q in enumerate(chk.support):
                if k:
                    targets.append(stim.target_combiner())
                targets.append(_TARGET[basis](q))
            c.append("MPP", targets, rn.p_read)     # record flip only
        for i, chk in enumerate(checks):
            recs = [stim.target_rec(-C + i)] + ([stim.target_rec(-2 * C + i)] if j else [])
            c.append("DETECTOR", recs, [*(chk.coords or ()), j])
        c.append("TICK")

    c.append(_MEASURE[basis], data, spec.noise.final_read())
    for i, chk in enumerate(checks):
        recs = [stim.target_rec(-n + q) for q in chk.support] + [stim.target_rec(-n - C + i)]
        c.append("DETECTOR", recs, [*(chk.coords or ()), len(noise)])
    c.append("OBSERVABLE_INCLUDE", [stim.target_rec(-n + q) for q in code.logical(basis)], 0)
    return c


def dem_for(spec: MemorySpec, noise=None) -> str:
    """Detector error model text; every phenomenological fault flips <= 2 detectors
    for codes like the surface code, so no decomposition is needed."""
    return str(build_circuit(spec, noise).detector_error_model(decompose_errors=False))


@register("backend", "stim_phenom")
class StimPhenomBackend:
    name = "stim_phenom"

    def versions(self) -> dict[str, str]:
        return {"stim": md.version("stim")}

    def supports(self, spec: MemorySpec) -> str | None:
        if not isinstance(spec.noise, PhenomenologicalNoise):
            return "needs a phenomenological noise model"
        return None

    def run(self, spec: MemorySpec) -> RawRecord:
        noise = round_noise(spec)
        circuit = build_circuit(spec, noise)
        # One stream per run, seeded by spec.seed. (Stim cannot seed per shot;
        # runs that must not share noise need different seeds.)
        sampler = circuit.compile_detector_sampler(seed=spec.seed)
        det, obs = sampler.sample(shots=spec.shots, separate_observables=True)
        s = spec.schedule
        rounds = {"dt": np.array(s.dts), "t": np.array(s.starts),
                  "p_data": np.array([r.p_data for r in noise]),
                  "p_read": np.array([r.p_read for r in noise])}
        layout = DetectorLayout(s.n_rounds, len(checks_of(spec.code, spec.basis)))
        return RawRecord(layout, det, obs, rounds, payload={"seed": spec.seed})
