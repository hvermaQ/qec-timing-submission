"""Minimum-weight perfect matching (PyMatching) from a detector error model.

A DEM with no error mechanisms (p = 0) cannot build a matching graph; the
correct decoder then predicts no flip, which is what this one does.
"""

from __future__ import annotations

import numpy as np
import pymatching
import stim
from numpy.typing import NDArray

from qec_timing.registry import register


@register("decoder", "pymatching")
class PyMatchingDecoder:
    def __init__(self, dem: str) -> None:
        model = stim.DetectorErrorModel(dem)
        self._n_det, self._n_obs = model.num_detectors, model.num_observables
        trivial = not any(i.type == "error" for i in model.flattened())
        self._matching = None if trivial else pymatching.Matching.from_detector_error_model(model)

    @property
    def num_detectors(self) -> int:
        return self._n_det

    @property
    def num_observables(self) -> int:
        return self._n_obs

    def decode_batch(self, detectors: NDArray[np.bool_]) -> NDArray[np.bool_]:
        detectors = np.asarray(detectors, dtype=bool)
        if detectors.ndim != 2 or detectors.shape[1] != self._n_det:
            raise ValueError(f"expected (shots, {self._n_det}) detectors, got {detectors.shape}")
        if self._matching is None:
            return np.zeros((len(detectors), self._n_obs), dtype=bool)
        return self._matching.decode_batch(detectors).astype(bool)
