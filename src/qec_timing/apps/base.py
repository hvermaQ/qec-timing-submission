"""How long logical qubits idle inside an application.

An `IdleSource` is any compiled logical circuit (QFT, adder, Trotter step, ...)
that can report, per logical qubit, the stretches in which it waits. A stretch of
L logical steps is a memory interval of about L * d syndrome rounds, which is where
the syndrome interval is chosen.

Time models are named so results say which one they used:
    "uniform":  every logical gate takes one step.
    "magic":    only non-Clifford gates take a step; Cliffords order operations
                but take no time (frame tracking / lattice surgery picture).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol, runtime_checkable

TimeModel = Literal["uniform", "magic"]


@dataclass(frozen=True)
class IdleProfile:
    """
    n_qubits:    logical qubits.
    steps:       makespan in logical steps.
    active:      per qubit, steps from its first to its last operation.
    stretches:   per qubit, lengths of idle stretches inside that span. Time
                 before the first and after the last operation is excluded (it
                 could be avoided by late allocation / early measurement).
    """

    n_qubits: int
    steps: float
    active: tuple[float, ...]
    stretches: tuple[tuple[float, ...], ...]
    time_model: TimeModel

    def __post_init__(self) -> None:
        if not (len(self.active) == len(self.stretches) == self.n_qubits):
            raise ValueError("active and stretches need one entry per qubit")
        for a, s in zip(self.active, self.stretches):
            if any(x <= 0 for x in s) or sum(s) > a + 1e-9:
                raise ValueError("idle stretches must be positive and fit in the active span")

    @property
    def idle_fraction(self) -> float:
        total = sum(self.active)
        return sum(map(sum, self.stretches)) / total if total else 0.0

    def share_in_stretches_at_least(self, length: float) -> float:
        """Share of all idle time that lies in stretches of >= `length` steps."""
        flat = [x for s in self.stretches for x in s]
        total = sum(flat)
        return sum(x for x in flat if x >= length) / total if total else 0.0


@runtime_checkable
class IdleSource(Protocol):
    @property
    def name(self) -> str:
        ...

    def params(self) -> dict[str, Any]:
        ...

    def idle_profile(self, time_model: TimeModel) -> IdleProfile:
        ...
