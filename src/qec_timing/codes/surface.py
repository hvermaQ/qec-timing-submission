"""Rotated surface code of odd distance d, both check sectors.

Data qubits sit on a d x d grid, index = row * d + col. Plaquette (r, c) acts on
(r, c), (r, c+1), (r+1, c), (r+1, c+1):

    Z checks: plaquettes with r + c even; weight-2 checks on the left column
              (odd r) and the right column (even r).
    X checks: plaquettes with r + c odd; weight-2 checks on the top row (even c)
              and the bottom row (odd c).

The Z-check order and the logical-Z choice (row 0) are those of the original
repo's `RotatedSurfaceCodeZSector`, so detector indices match its validated
Stage 1-4 runs. Logical X is column 0. Every data qubit lies in at most two
checks of each type, so single faults give graphlike detector error models.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import Any

from qec_timing.codes.base import Check, Pauli
from qec_timing.registry import register


@register("code", "rotated_surface")
@dataclass(frozen=True)
class RotatedSurfaceCode:
    d: int

    name = "rotated_surface"

    def __post_init__(self) -> None:
        if self.d < 3 or self.d % 2 == 0:
            raise ValueError(f"distance must be an odd integer >= 3, got {self.d}")

    def params(self) -> dict[str, Any]:
        return {"d": self.d}

    @property
    def n_data(self) -> int:
        return self.d * self.d

    def index(self, r: int, c: int) -> int:
        return r * self.d + c

    def _check(self, pauli: Pauli, cells: list[tuple[int, int]]) -> Check:
        support = tuple(sorted(self.index(r, c) for r, c in cells))
        centre = (sum(r for r, _ in cells) / len(cells), sum(c for _, c in cells) / len(cells))
        return Check(pauli, support, coords=centre)

    @cached_property
    def checks(self) -> tuple[Check, ...]:
        d, out = self.d, []
        plaquette = lambda r, c: [(r, c), (r, c + 1), (r + 1, c), (r + 1, c + 1)]
        # Z sector, in the original repo's order.
        for r in range(d - 1):
            for c in range(d - 1):
                if (r + c) % 2 == 0:
                    out.append(self._check("Z", plaquette(r, c)))
        for r in range(1, d - 1, 2):
            out.append(self._check("Z", [(r, 0), (r + 1, 0)]))
        for r in range(0, d - 1, 2):
            out.append(self._check("Z", [(r, d - 1), (r + 1, d - 1)]))
        # X sector.
        for r in range(d - 1):
            for c in range(d - 1):
                if (r + c) % 2 == 1:
                    out.append(self._check("X", plaquette(r, c)))
        for c in range(0, d - 1, 2):
            out.append(self._check("X", [(0, c), (0, c + 1)]))
        for c in range(1, d - 1, 2):
            out.append(self._check("X", [(d - 1, c), (d - 1, c + 1)]))
        return tuple(out)

    def logical(self, pauli: Pauli) -> tuple[int, ...]:
        if pauli == "Z":
            return tuple(self.index(0, c) for c in range(self.d))     # row 0
        return tuple(self.index(r, 0) for r in range(self.d))         # column 0
