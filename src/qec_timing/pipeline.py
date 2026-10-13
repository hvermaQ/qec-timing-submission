"""Interfaces for the two steps after a run: fitting a model, and deriving results.

    Extractor:  one raw run          -> EffectiveModel  (e.g. p_data, p_read, DEM)
    Analysis:   several stored items -> Derived         (e.g. dt*, Gamma, a U-curve)

Both read from and write to the `Store`, so every output names its inputs.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, Sequence, runtime_checkable

from qec_timing.records import Derived, EffectiveModel, RawRecord
from qec_timing.spec import MemorySpec

if TYPE_CHECKING:
    from qec_timing.store import Store


@runtime_checkable
class Extractor(Protocol):
    @property
    def name(self) -> str:
        ...

    def extract(self, spec: MemorySpec, record: RawRecord, run_id: str) -> EffectiveModel:
        ...


@runtime_checkable
class Analysis(Protocol):
    @property
    def name(self) -> str:
        ...

    def run(self, store: Store, run_ids: Sequence[str]) -> Derived:
        ...
