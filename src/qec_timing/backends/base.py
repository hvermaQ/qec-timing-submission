"""The backend interface: anything that turns a `MemorySpec` into a `RawRecord`.

Backends are the simulators (Guppy/Selene, Stim, a pure-numpy sampler) and the
hardware adapters (Nexus, aqora). They differ in which codes and noise models they
accept, which is why `supports` exists: a sweep asks before it runs.

Contract (checked by `qec_timing.testing.contracts.check_backend`):
- output follows the detector layout in `qec_timing.records`;
- with no noise there are no detection events and the logical readout is trivial;
- equal specs give equal records (seeded), different seeds give different ones;
- round metadata reports the noise actually applied.
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

from qec_timing.records import RawRecord
from qec_timing.spec import MemorySpec


@runtime_checkable
class Backend(Protocol):
    @property
    def name(self) -> str:
        ...

    def versions(self) -> dict[str, str]:
        """Package versions that affect results; stored in every manifest."""
        ...

    def supports(self, spec: MemorySpec) -> str | None:
        """None if the spec can be run, otherwise the reason it cannot."""
        ...

    def run(self, spec: MemorySpec) -> RawRecord:
        ...


@runtime_checkable
class ProvidesDem(Protocol):
    """Optional: a backend that can give the detector error model of a spec, in the
    standard detector layout, for decoding its records."""

    def dem(self, spec: MemorySpec) -> str:
        ...


def run_checked(backend: Backend, spec: MemorySpec) -> RawRecord:
    """Run after checking support, and verify the record matches the spec."""
    reason = backend.supports(spec)
    if reason is not None:
        raise ValueError(f"{backend.name} cannot run this spec: {reason}")
    record = backend.run(spec)
    expect: dict[str, Any] = {"shots": spec.shots, "n_rounds": spec.schedule.n_rounds,
                              "n_checks": spec.n_checks}
    got = {"shots": record.shots, "n_rounds": record.layout.n_rounds,
           "n_checks": record.layout.n_checks}
    if got != expect:
        raise RuntimeError(f"{backend.name} returned {got}, spec asked for {expect}")
    return record
