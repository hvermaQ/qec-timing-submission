"""The code interface: what a QEC code must provide to be simulated and analysed.

Scope: CSS stabilizer codes with one logical qubit (k = 1). A memory experiment in
basis B prepares the logical B eigenstate, measures the checks of type B every
round, and reads the data qubits out in basis B at the end. Errors of the *other*
Pauli type are the ones those checks see (X errors flip Z checks and vice versa).

A code is plain data: qubit count, checks with their extraction order, and the
logical operators. Turning it into a circuit is the backend's job, so one code
definition serves every backend. `qec_timing.testing.contracts.check_code` verifies
the algebra (commutation, independence of the logicals) for any implementation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Protocol, runtime_checkable

Pauli = Literal["X", "Z"]
PAULIS: tuple[Pauli, ...] = ("X", "Z")


def other(pauli: Pauli) -> Pauli:
    return "Z" if pauli == "X" else "X"


@dataclass(frozen=True)
class Check:
    """One stabilizer generator.

    pauli:   the check's Pauli type; it detects data errors of the other type.
    support: data-qubit indices the check acts on.
    order:   the order in which the extraction circuit couples the ancilla to the
             support (e.g. a hook-safe CNOT order). None means "as in support".
    coords:  optional position, used only for plotting and geometric decoders.
    """

    pauli: Pauli
    support: tuple[int, ...]
    order: tuple[int, ...] | None = None
    coords: tuple[float, ...] | None = None

    @property
    def extraction_order(self) -> tuple[int, ...]:
        return self.support if self.order is None else self.order


@runtime_checkable
class StabilizerCode(Protocol):
    """A CSS code with one logical qubit."""

    @property
    def name(self) -> str:
        """Registry name, e.g. "rotated_surface"."""
        ...

    def params(self) -> dict[str, Any]:
        """JSON-serialisable parameters that, with `name`, fully determine the code.
        They enter the run id, so two different codes must never share them."""
        ...

    @property
    def n_data(self) -> int:
        ...

    @property
    def checks(self) -> tuple[Check, ...]:
        ...

    def logical(self, pauli: Pauli) -> tuple[int, ...]:
        """Support of the logical operator of type `pauli` (data-qubit indices)."""
        ...


def checks_of(code: StabilizerCode, pauli: Pauli) -> tuple[Check, ...]:
    """The checks of one type, in the order that defines the detector index."""
    return tuple(c for c in code.checks if c.pauli == pauli)


def describe(code: StabilizerCode) -> dict[str, Any]:
    """Identity of a code, as stored in run manifests."""
    return {"name": code.name, "params": code.params()}
