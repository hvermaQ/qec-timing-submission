"""What runs produce, at three levels.

    RawRecord       what a backend measured: every detection event, the logical
                    outcome, the per-round noise actually applied, and the
                    backend's own payload verbatim.
    EffectiveModel  parameters fitted from raw records (p_data, p_read, lambda,
                    b_read, a detector error model), with confidence intervals.
    Derived         results computed from one or more runs (dt*, Gamma, a U-curve).

Each level names the runs it came from, so any number can be traced to raw data.

Detector convention (all backends): a memory with R rounds and C checks of the
memory basis has (R + 1) * C detectors. Detector r * C + c is check c in round r,
XORed with the same check in round r - 1 (round -1 is the ideal initial state).
Block R compares the checks recomputed from the final data readout with round
R - 1. Check c is position c in `checks_of(code, basis)`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
from numpy.typing import NDArray

ROUND_FIELDS = ("dt", "t", "p_data", "p_read")


@dataclass(frozen=True)
class DetectorLayout:
    n_rounds: int
    n_checks: int

    @property
    def n_detectors(self) -> int:
        return (self.n_rounds + 1) * self.n_checks

    def index(self, round_: int, check: int) -> int:
        if not (0 <= round_ <= self.n_rounds and 0 <= check < self.n_checks):
            raise IndexError((round_, check))
        return round_ * self.n_checks + check


@dataclass
class RawRecord:
    """
    detectors:   (shots, n_detectors) bool, in the layout above.
    observables: (shots, 1) bool, the raw logical readout parity (not decoded).
    rounds:      per-round arrays of length n_rounds: dt, t, p_data, p_read as
                 actually applied. Decoders take their weights from these.
    payload:     backend output kept verbatim (JSON-able): job ids, versions,
                 configuration, anything needed to audit the run.
    attachments: raw files from the backend (name -> bytes), e.g. hardware result
                 payloads, stored untouched.
    """

    layout: DetectorLayout
    detectors: NDArray[np.bool_]
    observables: NDArray[np.bool_]
    rounds: dict[str, NDArray[np.float64]]
    payload: dict[str, Any] = field(default_factory=dict)
    attachments: dict[str, bytes] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.detectors = np.asarray(self.detectors, dtype=bool)
        self.observables = np.asarray(self.observables, dtype=bool)
        shots = self.detectors.shape[0]
        if self.detectors.shape != (shots, self.layout.n_detectors):
            raise ValueError(f"detectors shape {self.detectors.shape} does not match "
                             f"(shots, {self.layout.n_detectors})")
        if self.observables.shape != (shots, 1):
            raise ValueError(f"observables shape {self.observables.shape} != ({shots}, 1)")
        missing = set(ROUND_FIELDS) - set(self.rounds)
        if missing:
            raise ValueError(f"per-round metadata missing: {sorted(missing)}")
        for k, v in self.rounds.items():
            v = np.asarray(v, dtype=float)
            if v.shape != (self.layout.n_rounds,):
                raise ValueError(f"rounds[{k!r}] has shape {v.shape}, "
                                 f"expected ({self.layout.n_rounds},)")
            self.rounds[k] = v

    @property
    def shots(self) -> int:
        return self.detectors.shape[0]


@dataclass(frozen=True)
class Estimate:
    """A fitted value with its confidence interval and the interval's level."""

    value: float
    low: float
    high: float
    level: float = 0.95


@dataclass
class EffectiveModel:
    """Parameters fitted from raw records.

    name:     which extractor produced it.
    params:   fitted values, e.g. {"p_data": Estimate(...), "p_read": Estimate(...)}.
    dem:      optional detector error model as Stim DEM text (a standard text
              format; no Stim dependency is needed to store it).
    parents:  run ids it was fitted from.
    """

    name: str
    params: dict[str, Estimate]
    parents: tuple[str, ...]
    dem: str | None = None
    info: dict[str, Any] = field(default_factory=dict)


@dataclass
class Derived:
    """A result computed from stored runs or models. `data` must be JSON-able."""

    name: str
    data: dict[str, Any]
    parents: tuple[str, ...]


# --- bit packing -------------------------------------------------------------
# Detection events are stored packed: unsigned 64-bit words, LSB first, ascending
# word order, last word zero-padded. Same format as the Guppy program's output.

def pack_bits(bits: NDArray[np.bool_]) -> NDArray[np.uint64]:
    """(..., n) bool -> (..., ceil(n / 64)) uint64."""
    bits = np.asarray(bits, dtype=bool)
    n = bits.shape[-1]
    n_words = -(-n // 64)
    padded = np.zeros(bits.shape[:-1] + (n_words * 64,), dtype=np.uint64)
    padded[..., :n] = bits
    weights = np.uint64(1) << np.arange(64, dtype=np.uint64)
    return (padded.reshape(bits.shape[:-1] + (n_words, 64)) * weights).sum(
        axis=-1, dtype=np.uint64)


def unpack_bits(words: NDArray[np.uint64], n: int) -> NDArray[np.bool_]:
    """(..., n_words) uint64 -> (..., n) bool. Padding bits must be zero."""
    words = np.asarray(words, dtype=np.uint64)
    bits = ((words[..., None] >> np.arange(64, dtype=np.uint64)) & np.uint64(1)).astype(bool)
    bits = bits.reshape(words.shape[:-1] + (-1,))
    if bits[..., n:].any():
        raise ValueError("non-zero padding bits: wrong n or corrupted data")
    return bits[..., :n]
