"""Noise-model interfaces.

Two levels, because backends consume noise at two levels:

- `NoiseModel`: what every model provides. A name, parameters (for the run id),
  and the Pauli type of the error it puts on data qubits, so a memory experiment
  can refuse a basis that cannot see it.
- `PhenomenologicalNoise`: the paper's level. Per round, a data-flip probability
  and a record-flip probability (paper Eqs. 1-3). Circuit-level models (gate,
  idle and readout noise on a compiled circuit) extend `NoiseModel` directly and
  are interpreted by the backends that support them.

Time is dimensionless (the paper's t), as in the schedule.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable

from qec_timing.codes.base import Pauli


@dataclass(frozen=True)
class RoundNoise:
    """Noise of one syndrome round.

    p_data: probability of a `data_pauli` flip on each data qubit, drawn ONCE per
            qubit per round before extraction (paper Eq. 2: p_stab and p_idle
            composed into one draw, never two independent ones).
    p_read: probability of flipping each recorded syndrome bit; the classical
            record only, never the qubit (paper Eq. 3).
    """

    p_data: float
    p_read: float

    def __post_init__(self) -> None:
        for name in ("p_data", "p_read"):
            v = getattr(self, name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{name} = {v} is not a probability")


@runtime_checkable
class NoiseModel(Protocol):
    @property
    def name(self) -> str:
        ...

    def params(self) -> dict[str, Any]:
        """JSON-serialisable parameters; with `name` they determine the model."""
        ...

    @property
    def data_pauli(self) -> Pauli:
        """Pauli type of the dominant data error ("X" for bit flips, "Z" for
        dephasing). A memory in the same basis is blind to it."""
        ...


@runtime_checkable
class PhenomenologicalNoise(NoiseModel, Protocol):
    def round_noise(self, t: float, dt: float) -> RoundNoise:
        """Noise of the round that starts at time t and lasts dt."""
        ...

    def final_read(self) -> float:
        """Record-flip probability of the final data-qubit readout."""
        ...


def describe(noise: NoiseModel) -> dict[str, Any]:
    """Identity of a noise model, as stored in run manifests."""
    return {"name": noise.name, "params": noise.params(), "data_pauli": noise.data_pauli}
