"""Run-or-load, decode and fit: the steps every study repeats.

Each function looks the run up in the store first, so a study can be rerun for
free and extended point by point. Nothing here knows which experiment it serves.

Memory is bounded twice, because an unbounded run once exhausted the machine's
memory and the kernel killed the session along with it:
  - a spec whose detection events would exceed MAX_RUN_BYTES (as booleans) is run
    as several shot chunks, each stored as its own run, and their failures summed;
  - parallel workers are capped by the memory the kernel reports as available.
"""

from __future__ import annotations

import dataclasses

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


MAX_RUN_BYTES = 256 * 2**20          # detection events per stored run, one byte per bit
JOB_FACTOR = 4                         # peak memory of a run + decode, in units of its detectors
JOB_OVERHEAD = 400 * 2**20             # interpreter, circuit, DEM, matching graph


def detector_bytes(spec: MemorySpec) -> int:
    return spec.shots * (spec.schedule.n_rounds + 1) * spec.n_checks


def chunks(spec: MemorySpec, per_shot_seeded: bool = False) -> list[MemorySpec]:
    """`spec` itself if small enough, else shot chunks under MAX_RUN_BYTES.

    Seeds: a per-shot-seeded backend (shot k uses seed + k) gets contiguous ranges,
    so the chunks draw exactly what one run would. A per-run-seeded backend (Stim)
    gets seeds (seed << 20) + i, far from any seed a study assigns directly."""
    per_shot = (spec.schedule.n_rounds + 1) * spec.n_checks
    size = max(1, MAX_RUN_BYTES // per_shot)
    if spec.shots <= size:
        return [spec]
    out, done, i = [], 0, 0
    while done < spec.shots:
        n = min(size, spec.shots - done)
        seed = spec.seed + done if per_shot_seeded else (spec.seed << 20) + i
        out.append(dataclasses.replace(spec, shots=n, seed=seed))
        done, i = done + n, i + 1
    return out


def failures(store: Store, backend: Backend, spec: MemorySpec) -> tuple[list[str], int, int]:
    """(run ids, logical failures, shots), decoded by PyMatching on the backend's DEM.
    One run id unless the spec was split into chunks."""
    ids, fails, shots = [], 0, 0
    dem = None
    for part in chunks(spec, getattr(backend, "per_shot_seeded", False)):
        run_id, rec = record(store, backend, part)
        dem = dem or backend.dem(part)          # the DEM does not depend on shots or seed
        f = logical_failures(PyMatchingDecoder(dem), rec.detectors, rec.observables)
        ids, fails, shots = ids + [run_id], fails + int(f.sum()), shots + rec.shots
        del rec
    return ids, fails, shots


def memory_workers(requested: int, specs: list[MemorySpec]) -> int:
    """Workers that fit in the memory the kernel reports available (with headroom)."""
    try:
        avail = next(int(line.split()[1]) * 1024 for line in open("/proc/meminfo")
                     if line.startswith("MemAvailable"))
    except (OSError, StopIteration):
        return 1
    job = max(min(detector_bytes(s), MAX_RUN_BYTES) for s in specs) * JOB_FACTOR + JOB_OVERHEAD
    return max(1, min(requested, int(0.6 * avail) // job))


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
                  workers: int = 1) -> list[tuple[list[str], int, int]]:
    """`failures` for many specs, in parallel processes. Results in input order.

    Runs that are already stored are loaded and decoded in the workers too, since
    decoding is a large share of the cost. Each run writes its own store
    directory, so workers never share a file. Work a backend must do once per
    configuration (e.g. compiling native gates) is done here, before forking, so
    workers only read its cache."""
    if hasattr(backend, "prepare"):
        for spec in specs:
            backend.prepare(spec)
    if not specs:
        return []
    workers = memory_workers(workers, specs)
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


def _decode_job(args):
    store_root, backend, spec, dems = args
    out = {}
    for part in chunks(spec, getattr(backend, "per_shot_seeded", False)):
        _, rec = record(Store(store_root), backend, part)
        for name, dem in dems.items():
            f = logical_failures(PyMatchingDecoder(dem), rec.detectors, rec.observables)
            out[name] = out.get(name, 0) + int(f.sum())
        out["_shots"] = out.get("_shots", 0) + rec.shots
        del rec
    return out


def decode_many(store: Store, backend: Backend, specs: list[MemorySpec],
                dems: list[dict[str, str]], workers: int = 1) -> list[dict[str, int]]:
    """Decode each spec's stored (or new) runs with several detector error models.

    dems[i] maps a decoder label to DEM text for specs[i]; every DEM must use the
    standard detector layout. Returns per spec {label: failures, "_shots": shots}."""
    if hasattr(backend, "prepare"):
        for spec in specs:
            backend.prepare(spec)
    jobs = [(store.root, backend, s, d) for s, d in zip(specs, dems)]
    workers = memory_workers(workers, specs) if specs else 1
    if workers <= 1:
        return [_decode_job(j) for j in jobs]
    import multiprocessing as mp
    from concurrent.futures import ProcessPoolExecutor

    with ProcessPoolExecutor(workers, mp_context=mp.get_context("fork")) as pool:
        return list(pool.map(_decode_job, jobs))
