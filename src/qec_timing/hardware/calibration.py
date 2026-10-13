"""Device parameters: the hand-off between hardware adapters and the regime study.

A hardware adapter measures (or a data sheet supplies) these numbers and writes a
calibration file. The regime study reads only that file. So the same analysis runs
today on data-sheet values and later, unchanged, on measured ones.

Idle-noise convention follows Quantinuum's emulator noise model (Z only):
    linear:    p = gamma * t                        gamma in 1/s, t in s
    quadratic: p = sin^2(omega * t / 2)             omega = 2*pi*f*k ("cycles")
                                                    omega = f*k      ("radians")
with f = quad_rate and k = coherent_to_incoherent_factor. The docs' units for f
("2 pi radians per second") are ambiguous; the two readings differ by (2 pi)^2 in
the quadratic term, so the reading is part of the calibration, never implicit.
"""

from __future__ import annotations

import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Literal

CALIBRATION_VERSION = 1


@dataclass(frozen=True)
class Calibration:
    """
    p1, p2:         1- and 2-qubit gate error (depolarizing parameter).
    p_meas0/1:      readout error for outcome 0 / 1.
    p_init:         preparation error.
    gamma:          linear dephasing rate, 1/s.
    quad_rate:      quadratic dephasing rate f (see module docstring).
    quad_factor:    coherent_to_incoherent_factor k.
    quad_convention:"cycles" or "radians".
    t_round:        duration of one syndrome round, s. None = not known; analyses
                    that need it must refuse rather than assume.
    source:         where the numbers come from (data sheet + date, run ids, ...).
    """

    p1: float
    p2: float
    p_meas0: float
    p_meas1: float
    p_init: float
    gamma: float
    quad_rate: float
    quad_factor: float = 2.0
    quad_convention: Literal["cycles", "radians"] = "cycles"
    t_round: float | None = None
    source: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for name in ("p1", "p2", "p_meas0", "p_meas1", "p_init"):
            v = getattr(self, name)
            if not 0.0 <= v <= 1.0:
                raise ValueError(f"{name} = {v} is not a probability")
        for name in ("gamma", "quad_rate", "quad_factor"):
            if getattr(self, name) < 0:
                raise ValueError(f"{name} must be non-negative")
        if self.quad_convention not in ("cycles", "radians"):
            raise ValueError("quad_convention must be 'cycles' or 'radians'")
        if self.t_round is not None and not self.t_round > 0:
            raise ValueError("t_round must be positive or None")
        if not self.source:
            raise ValueError("a calibration must say where its numbers come from")

    @property
    def omega(self) -> float:
        """Quadratic-term angular frequency, rad/s."""
        f = self.quad_rate * self.quad_factor
        return 2 * math.pi * f if self.quad_convention == "cycles" else f

    def idle_pz(self, t: float) -> float:
        """Z-flip probability after idling t seconds: linear and quadratic terms
        composed as independent Z channels."""
        lin = min(self.gamma * t, 1.0)
        quad = math.sin(self.omega * t / 2) ** 2
        return lin + quad - 2 * lin * quad

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({"calibration_version": CALIBRATION_VERSION,
                                          **asdict(self)}, indent=2, sort_keys=True))

    @classmethod
    def load(cls, path: str | Path) -> "Calibration":
        d = json.loads(Path(path).read_text())
        version = d.pop("calibration_version", None)
        if version != CALIBRATION_VERSION:
            raise ValueError(f"calibration version {version}, expected {CALIBRATION_VERSION}")
        return cls(**d)
