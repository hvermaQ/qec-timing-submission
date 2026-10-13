"""Circuit-level noise: gate, readout and reset errors plus a time-based idle channel.

Time is in units of the round duration t_R. A schedule interval dt is the full
round period (extraction + wait), as in the original repo's notebooks 07-09.

Idle channel over a duration t (Quantinuum emulator form, Pauli-twirled):
    linear dephasing     Z with probability gamma * t
    quadratic dephasing  Z with probability sin^2(sqrt(c) * t)
    depolarizing         X, Y, Z each at depol/3 per unit time, composed over t
The three compose exactly through their Pauli eigenvalues.

Placement (where the idle channel acts), the two models of the notebook arc:
    "data_interval"  notebook 07: data qubits only, idle(dt) once per round.
    "uniform"        notebooks 08/09: every qubit, ancillas included; idle(1/L)
                     after each of the L layers of a round, and idle(dt - 1) for
                     the wait before it. Requires dt >= 1.
Gate noise: DEPOLARIZE1(p1) after single-qubit Cliffords, DEPOLARIZE2(p2) after
every two-qubit gate, record flip p_meas before each measurement, flip p_init
after each reset.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from typing import Any, Literal

from qec_timing.codes.base import Pauli
from qec_timing.registry import register

Placement = Literal["data_interval", "uniform"]


@dataclass(frozen=True)
class IdleNoise:
    gamma: float = 0.0     # linear dephasing, per t_R
    c: float = 0.0         # quadratic dephasing: sin^2(sqrt(c) t)
    depol: float = 0.0     # depolarizing, per t_R

    def __post_init__(self) -> None:
        if min(self.gamma, self.c, self.depol) < 0:
            raise ValueError("idle rates must be non-negative")

    def channel(self, t: float) -> tuple[float, float, float]:
        """(pX, pY, pZ) of idling for time t."""
        if t < 0:
            raise ValueError("idle time must be non-negative")
        e = (1 - 4 * self.depol / 3) ** t                   # depolarizing eigenvalue
        lin = min(self.gamma * t, 0.5)
        quad = math.sin(math.sqrt(self.c) * t) ** 2
        pz = lin + quad - 2 * lin * quad                      # two Z flips, mod 2
        lx = ly = e * (1 - 2 * pz)                            # Z dephases the X and Y axes
        lz = e
        return tuple(max(v, 0.0) for v in ((1 + lx - ly - lz) / 4,
                                           (1 - lx + ly - lz) / 4,
                                           (1 - lx - ly + lz) / 4))

    def pz(self, t: float) -> float:
        return self.channel(t)[2]


@register("noise", "circuit")
@dataclass(frozen=True)
class CircuitNoise:
    p1: float
    p2: float
    p_meas: float
    p_init: float = 0.0
    idle: IdleNoise = field(default_factory=IdleNoise)
    placement: Placement = "uniform"

    name = "circuit"

    def __post_init__(self) -> None:
        for k in ("p1", "p2", "p_meas", "p_init"):
            if not 0.0 <= getattr(self, k) <= 1.0:
                raise ValueError(f"{k} is not a probability")
        if self.placement not in ("data_interval", "uniform"):
            raise ValueError(f"unknown placement {self.placement!r}")

    def params(self) -> dict[str, Any]:
        out = asdict(self)
        out["idle"] = asdict(self.idle)
        return out

    @property
    def data_pauli(self) -> Pauli | None:
        # The type of the IDLE error, which is what an interval study is about.
        # Pure dephasing is Z only: a Z-basis memory sees the gate noise but not
        # the idling, so it would show no trade-off at all (notebook 07 §9).
        if self.idle.depol == 0 and (self.idle.gamma or self.idle.c):
            return "Z"
        return None

    @classmethod
    def from_calibration(cls, cal, t_round: float | None = None,
                         placement: Placement = "uniform") -> "CircuitNoise":
        """Device calibration (seconds) -> circuit noise in units of t_R.

        Linear: gamma [1/s] * t_R. Quadratic: sin^2(omega t / 2) = sin^2(sqrt(c) t_rounds)
        with t = t_rounds * t_R, so sqrt(c) = omega * t_R / 2. Readout is the mean of
        the two outcome errors (the circuit model has symmetric readout)."""
        t_r = cal.t_round if t_round is None else t_round
        if t_r is None:
            raise ValueError("t_round unknown: pass it explicitly; it is never assumed")
        return cls(p1=cal.p1, p2=cal.p2, p_meas=(cal.p_meas0 + cal.p_meas1) / 2,
                   p_init=cal.p_init, placement=placement,
                   idle=IdleNoise(gamma=cal.gamma * t_r, c=(cal.omega * t_r / 2) ** 2))
