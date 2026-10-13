"""Run-or-load, decode and fit: the steps every study repeats.

Each function looks the run up in the store first, so a study can be rerun for
free and extended point by point. Nothing here knows which experiment it serves.
"""

from __future__ import annotations

from qec_timing.backends.base import Backend, run_checked
from qec_timing.decoders.base import logical_failures
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
from qec_timing.extract.edges import EdgeExtractor
from qec_timing.records import EffectiveModel, RawRecord
from qec_timing.spec import MemorySpec
from qec_timing.store import Store


def record(store: Store, backend: Backend, spec: MemorySpec) -> tuple[str, RawRecord]:
    run_id = spec.run_id(backend.name)
    if store.has_run(run_id):
        return run_id, store.load_run(run_id)[1]
    rec = run_checked(backend, spec)
    store.save_run(spec, backend.name, backend.versions(), rec)
    return run_id, rec


def failures(store: Store, backend: Backend, spec: MemorySpec) -> tuple[str, int, int]:
    """(run_id, logical failures, shots), decoded by PyMatching on the backend's DEM."""
    run_id, rec = record(store, backend, spec)
    fails = logical_failures(PyMatchingDecoder(backend.dem(spec)), rec.detectors, rec.observables)
    return run_id, int(fails.sum()), rec.shots


def edges(store: Store, backend: Backend, spec: MemorySpec) -> EffectiveModel:
    """Effective p_data / p_read of a run, fitted once and stored with it."""
    run_id, rec = record(store, backend, spec)
    try:
        return store.load_model(run_id, EdgeExtractor.name)
    except FileNotFoundError:
        model = EdgeExtractor().extract(spec, rec, run_id)
        store.save_model(run_id, model)
        return model


def _failures_job(args):
    store_root, backend, spec = args
    return failures(Store(store_root), backend, spec)


def failures_many(store: Store, backend: Backend, specs: list[MemorySpec],
                  workers: int = 1) -> list[tuple[str, int, int]]:
    """`failures` for many specs, in parallel processes. Results in input order.

    Runs that are already stored are loaded and decoded in the workers too, since
    decoding is a large share of the cost. Each run writes its own store
    directory, so workers never share a file. Work a backend must do once per
    configuration (e.g. compiling native gates) is done here, before forking, so
    workers only read its cache."""
    if hasattr(backend, "prepare"):
        for spec in specs:
            backend.prepare(spec)
    if workers <= 1 or len(specs) <= 1:
        return [failures(store, backend, s) for s in specs]
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor

    # Most expensive first, so the pool does not end on one long job.
    order = sorted(range(len(specs)),
                   key=lambda i: -specs[i].code.n_data * specs[i].schedule.n_rounds * specs[i].shots)
    out: list = [None] * len(specs)
    with ProcessPoolExecutor(workers, mp_context=mp.get_context("fork")) as pool:
        for i, res in zip(order, pool.map(_failures_job,
                                          [(store.root, backend, specs[i]) for i in order])):
            out[i] = res
    return out
