"""TEST FIXTURES, not product code: the smallest implementations of each interface.

They exist to exercise the interfaces and the contract checks end to end. The
sampler is generic over any CSS code under phenomenological noise, which is also
what shows that a new code needs nothing but the `StabilizerCode` interface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from qec_timing.apps.base import IdleProfile
from qec_timing.codes.base import Check, Pauli, checks_of
from qec_timing.noise.base import RoundNoise
from qec_timing.records import DetectorLayout, RawRecord
from qec_timing.spec import MemorySpec


@dataclass(frozen=True)
class RepetitionCode:
    """Bit-flip repetition code: Z_i Z_{i+1} checks, logical Z = Z_0, logical X = X^n."""

    d: int

    name = "repetition"

    def params(self) -> dict[str, Any]:
        return {"d": self.d}

    @property
    def n_data(self) -> int:
        return self.d

    @property
    def checks(self) -> tuple[Check, ...]:
        return tuple(Check("Z", (i, i + 1)) for i in range(self.d - 1))

    def logical(self, pauli: Pauli) -> tuple[int, ...]:
        return (0,) if pauli == "Z" else tuple(range(self.d))


@dataclass(frozen=True)
class SteaneCode:
    """[[7,1,3]] Steane code: a second code, to show the interface is not
    repetition- or surface-specific."""

    name = "steane"

    def params(self) -> dict[str, Any]:
        return {}

    n_data = 7
    _supports = ((0, 1, 2, 3), (1, 2, 4, 5), (2, 3, 5, 6))

    @property
    def checks(self) -> tuple[Check, ...]:
        return tuple(Check(p, s) for p in ("X", "Z") for s in self._supports)

    def logical(self, pauli: Pauli) -> tuple[int, ...]:
        return (0, 1, 4)    # weight-3 representative; same support for X and Z


@dataclass(frozen=True)
class FixedNoise:
    """Constant per-round noise (no time dependence)."""

    p_data: float
    p_read: float
    pauli: Pauli = "X"

    name = "fixed"

    def params(self) -> dict[str, Any]:
        return {"p_data": self.p_data, "p_read": self.p_read}

    @property
    def data_pauli(self) -> Pauli:
        return self.pauli

    def round_noise(self, t: float, dt: float) -> RoundNoise:
        return RoundNoise(self.p_data, self.p_read)

    def final_read(self) -> float:
        return self.p_read


class NumpySampler:
    """Phenomenological sampler for any CSS code. Shot k uses rng(seed + k)."""

    name = "numpy_sampler"

    def versions(self) -> dict[str, str]:
        return {"numpy": np.__version__}

    def supports(self, spec: MemorySpec) -> str | None:
        if not hasattr(spec.noise, "round_noise"):
            return "needs a phenomenological noise model"
        return None

    def run(self, spec: MemorySpec) -> RawRecord:
        code, basis = spec.code, spec.basis
        checks = checks_of(code, basis)
        H = np.zeros((len(checks), code.n_data), dtype=np.uint8)
        for i, c in enumerate(checks):
            H[i, list(c.support)] = 1
        L = np.zeros(code.n_data, dtype=np.uint8)
        L[list(code.logical(basis))] = 1

        sched = spec.schedule
        noise = [spec.noise.round_noise(t, dt) for t, dt in zip(sched.starts, sched.dts)]
        layout = DetectorLayout(sched.n_rounds, len(checks))
        det = np.zeros((spec.shots, layout.n_detectors), dtype=bool)
        obs = np.zeros((spec.shots, 1), dtype=bool)
        C = len(checks)
        for k in range(spec.shots):
            rng = np.random.default_rng(spec.seed + k)
            e = np.zeros(code.n_data, dtype=np.uint8)
            prev = np.zeros(C, dtype=np.uint8)
            for j, rn in enumerate(noise):
                e ^= (rng.random(code.n_data) < rn.p_data).astype(np.uint8)   # one draw per qubit
                s = (H @ e) % 2 ^ (rng.random(C) < rn.p_read)                 # record flip only
                det[k, j * C:(j + 1) * C] = s ^ prev
                prev = s
            m = e ^ (rng.random(code.n_data) < spec.noise.final_read())
            det[k, sched.n_rounds * C:] = ((H @ m) % 2) ^ prev
            obs[k, 0] = (L @ m) % 2
        rounds = {"dt": np.array(sched.dts), "t": np.array(sched.starts),
                  "p_data": np.array([r.p_data for r in noise]),
                  "p_read": np.array([r.p_read for r in noise])}
        return RawRecord(layout, det, obs, rounds, payload={"sampler": self.name})


class NullDecoder:
    """Predicts no flip, ever. Enough to exercise the decoder contract."""

    def __init__(self, dem: str, n_detectors: int = 4):
        self._n = n_detectors

    @property
    def num_detectors(self) -> int:
        return self._n

    @property
    def num_observables(self) -> int:
        return 1

    def decode_batch(self, detectors):
        return np.zeros((len(detectors), 1), dtype=bool)


@dataclass(frozen=True)
class FixedIdle:
    """An idle source with a hand-written profile."""

    name = "fixed_idle"

    def params(self) -> dict[str, Any]:
        return {}

    def idle_profile(self, time_model):
        return IdleProfile(n_qubits=2, steps=10, active=(10, 6), stretches=((3, 4), ()),
                           time_model=time_model)
