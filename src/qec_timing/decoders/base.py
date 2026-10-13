"""The decoder interface.

A decoder is built from a detector error model (DEM, in Stim's text format) and
predicts, per shot, whether the logical observable was flipped. The DEM carries the
edge weights log((1 - p) / p) of paper Eq. A2, computed from the noise a run
reports per round. A decoder that should follow a *believed* noise level rather
than the true one (the adaptive controller of paper Appendix F) is simply built
from a DEM made with the believed probabilities.

Same shape as the original repo's `reference.decoder.Decoder`, so existing
decoders (and the teammate's) plug in unchanged.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

import numpy as np
from numpy.typing import NDArray


@runtime_checkable
class Decoder(Protocol):
    @property
    def num_detectors(self) -> int:
        ...

    @property
    def num_observables(self) -> int:
        ...

    def decode_batch(self, detectors: NDArray[np.bool_]) -> NDArray[np.bool_]:
        """(shots, num_detectors) bool -> (shots, num_observables) bool flips."""
        ...


class DecoderFactory(Protocol):
    """What the registry stores for decoders: DEM text in, decoder out."""

    def __call__(self, dem: str, **options: object) -> Decoder:
        ...


def logical_failures(decoder: Decoder, detectors: NDArray[np.bool_],
                     observables: NDArray[np.bool_]) -> NDArray[np.bool_]:
    """Per shot: did the decoder's correction leave the logical flipped?"""
    predicted = np.asarray(decoder.decode_batch(detectors), dtype=bool)
    if predicted.shape != observables.shape:
        raise ValueError(f"decoder returned {predicted.shape}, expected {observables.shape}")
    return (predicted ^ observables).any(axis=1)
