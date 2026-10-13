"""A memory experiment, fully specified.

`MemorySpec` is what a backend runs and what a run id is computed from. It is
validated when built, so an experiment that cannot mean anything (for example a
Z-basis memory under pure dephasing, whose checks cannot see the noise) fails here
rather than producing a flat, misleading curve.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any

from qec_timing.codes.base import Pauli, StabilizerCode, checks_of
from qec_timing.codes.base import describe as describe_code
from qec_timing.noise.base import NoiseModel
from qec_timing.noise.base import describe as describe_noise
from qec_timing.schedule import Schedule

SPEC_VERSION = 1


@dataclass(frozen=True)
class MemorySpec:
    """
    code:     the code (any `StabilizerCode`).
    basis:    memory basis; checks of this type are measured and decoded.
    schedule: round intervals.
    noise:    the noise model; which kinds a backend accepts is up to the backend.
    shots:    number of shots.
    seed:     base seed. Per-shot-seeded backends (Guppy/Selene) give shot k the
              seed seed + k, so runs whose ranges [seed, seed + shots) overlap
              share noise (see `overlapping_seed_ranges`); per-run-seeded
              backends (Stim) need only distinct seeds.
    allow_invisible_noise: permit a basis that cannot see the noise. Only for
              deliberate control runs (showing the blindness itself).
    extra:    backend-specific options that change the result (they enter the id).
    """

    code: StabilizerCode
    basis: Pauli
    schedule: Schedule
    noise: NoiseModel
    shots: int
    seed: int
    allow_invisible_noise: bool = False
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.basis not in ("X", "Z"):
            raise ValueError(f"basis must be 'X' or 'Z', not {self.basis!r}")
        if self.shots <= 0:
            raise ValueError("shots must be positive")
        if self.seed < 0:
            raise ValueError("seed must be non-negative")
        if not checks_of(self.code, self.basis):
            raise ValueError(f"{self.code.name} has no {self.basis} checks to measure")
        # Checks of type B detect errors of the other type. Same-type errors
        # commute with them and are invisible.
        if self.noise.data_pauli is not None and self.noise.data_pauli == self.basis \
                and not self.allow_invisible_noise:
            raise ValueError(
                f"{self.noise.data_pauli} noise is invisible to a {self.basis}-basis memory; "
                f"use basis {'X' if self.basis == 'Z' else 'Z'}, or set allow_invisible_noise "
                "for a deliberate control run")

    @property
    def n_checks(self) -> int:
        return len(checks_of(self.code, self.basis))

    def to_json(self) -> dict[str, Any]:
        return {
            "spec_version": SPEC_VERSION,
            "code": describe_code(self.code),
            "basis": self.basis,
            "schedule": self.schedule.to_json(),
            "noise": describe_noise(self.noise),
            "shots": self.shots,
            "seed": self.seed,
            "allow_invisible_noise": self.allow_invisible_noise,
            "extra": self.extra,
        }

    def run_id(self, backend: str) -> str:
        """Content hash of (spec, backend): equal inputs give equal ids, so a run
        is computed once and found again. The code version is NOT part of the id;
        the store records it and flags runs made by older code."""
        blob = json.dumps({"spec": self.to_json(), "backend": backend},
                          sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(blob.encode()).hexdigest()[:16]


def overlapping_seed_ranges(specs: list[MemorySpec]) -> list[tuple[int, int]]:
    """Pairs (i, j) of specs whose per-shot seed ranges [seed, seed + shots) overlap.

    Backends that seed shot k with seed + k (Guppy/Selene) reuse the same random
    numbers wherever two ranges overlap, which correlates the runs. Any analysis
    that treats runs as independent must check this is empty."""
    ranges = sorted((s.seed, s.seed + s.shots, i) for i, s in enumerate(specs))
    out = []
    for a in range(len(ranges)):
        for b in range(a + 1, len(ranges)):
            if ranges[b][0] >= ranges[a][1]:
                break
            out.append(tuple(sorted((ranges[a][2], ranges[b][2]))))
    return out
