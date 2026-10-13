"""When syndrome rounds happen.

Time is kept as an integer count of ticks, never as an accumulated float: adding
dt = 0.1 ten times does not give 1.0, and a float loop silently adds a round. Every
interval is an integer number of ticks; t_j is the exact sum of the previous ones.
Total time T is fixed by the caller and the number of rounds follows from dt.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

DEFAULT_TICK = 1e-3


@dataclass(frozen=True)
class Schedule:
    """Round intervals in ticks. Round j lasts intervals[j] * tick."""

    intervals: tuple[int, ...]
    tick: float = DEFAULT_TICK

    def __post_init__(self) -> None:
        if not self.intervals:
            raise ValueError("a schedule needs at least one round")
        if any((not isinstance(n, int)) or n <= 0 for n in self.intervals):
            raise ValueError("intervals must be positive integers (ticks)")
        if not self.tick > 0:
            raise ValueError("tick must be positive")

    @classmethod
    def fixed(cls, dt: float, T: float, tick: float = DEFAULT_TICK) -> "Schedule":
        """Constant interval dt over total time T: n_rounds = round(T / dt)."""
        n_ticks = dt / tick
        if not math.isclose(n_ticks, round(n_ticks), rel_tol=0, abs_tol=1e-9 * max(1, n_ticks)):
            raise ValueError(f"dt = {dt} is not a multiple of tick = {tick}")
        n_rounds = round(T / dt)
        if n_rounds < 1:
            raise ValueError(f"T = {T} is shorter than one interval dt = {dt}")
        return cls(intervals=(int(round(n_ticks)),) * n_rounds, tick=tick)

    @property
    def n_rounds(self) -> int:
        return len(self.intervals)

    @property
    def dts(self) -> tuple[float, ...]:
        return tuple(n * self.tick for n in self.intervals)

    @property
    def starts(self) -> tuple[float, ...]:
        """t_j = (sum of earlier intervals) * tick, from an exact integer sum."""
        out, acc = [], 0
        for n in self.intervals:
            out.append(acc * self.tick)
            acc += n
        return tuple(out)

    @property
    def total_time(self) -> float:
        return sum(self.intervals) * self.tick

    @property
    def is_constant(self) -> bool:
        return len(set(self.intervals)) == 1

    def to_json(self) -> dict[str, Any]:
        # A constant schedule is stored compactly; the run id must not depend on
        # which form produced it, so both forms map to the same dict.
        if self.is_constant:
            return {"tick": self.tick, "interval": self.intervals[0], "n_rounds": self.n_rounds}
        return {"tick": self.tick, "intervals": list(self.intervals)}

    @classmethod
    def from_json(cls, d: dict[str, Any]) -> "Schedule":
        if "interval" in d:
            return cls(intervals=(int(d["interval"]),) * int(d["n_rounds"]), tick=d["tick"])
        return cls(intervals=tuple(int(n) for n in d["intervals"]), tick=d["tick"])
