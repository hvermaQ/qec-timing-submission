"""The paper's phenomenological noise model (Haug, Bharti & Aolita 2026, Eqs. 1-3).

    Eq. 1  p_idle = 1 - exp(-p * lam * dt)
    Eq. 2  p_data = 1 - (1 - p_stab)(1 - p_idle),   p_stab = p
    Eq. 3  p_read = b_read * p

p_stab is never dropped: at lam = 0 it still gives p_data = p, and it is the term
that makes frequent extraction costly, i.e. what creates the dt trade-off.
lam is static here; a time-dependent lam(t) (paper Eq. 9) would be a new model
with the same interface, since `round_noise` already receives t.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from qec_timing.codes.base import Pauli
from qec_timing.noise.base import RoundNoise
from qec_timing.registry import register


def p_idle(p: float, lam: float, dt: float) -> float:
    """Eq. 1. expm1 keeps precision at the small-dt end of a sweep."""
    return -math.expm1(-p * lam * dt)


def p_data(p: float, lam: float, dt: float) -> float:
    """Eq. 2, one combined probability (applied as ONE draw per qubit per round)."""
    return 1.0 - (1.0 - p) * (1.0 - p_idle(p, lam, dt))


@register("noise", "paper")
@dataclass(frozen=True)
class PaperNoise:
    """p: physical error rate; lam: idling rate (static); b_read: readout ratio.
    pauli: type of the data flips. "X" is the paper's bit-flip model; "Z" is the
    same model in the dual sector, for X-basis memories."""

    p: float
    lam: float
    b_read: float = 1.0
    pauli: Pauli = "X"

    name = "paper"

    def __post_init__(self) -> None:
        if not 0.0 <= self.p <= 1.0:
            raise ValueError(f"p = {self.p} is not a probability")
        if self.lam < 0 or self.b_read < 0:
            raise ValueError("lam and b_read must be non-negative")
        if self.b_read * self.p > 1.0:
            raise ValueError(f"p_read = b_read * p = {self.b_read * self.p} exceeds 1")
        if self.pauli not in ("X", "Z"):
            raise ValueError("pauli must be 'X' or 'Z'")

    def params(self) -> dict[str, Any]:
        return {"p": self.p, "lam": self.lam, "b_read": self.b_read}

    @property
    def data_pauli(self) -> Pauli:
        return self.pauli

    def round_noise(self, t: float, dt: float) -> RoundNoise:
        return RoundNoise(p_data(self.p, self.lam, dt), self.b_read * self.p)

    def final_read(self) -> float:
        # The final data readout has the same classical flip rate as a syndrome bit.
        return self.b_read * self.p
