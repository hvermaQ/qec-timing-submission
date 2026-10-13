"""Study plumbing: parallel runs agree with serial ones; the regime study runs end to end."""

import json

import pytest

pytest.importorskip("stim")      # needs the main env (envs/main.txt)

from qec_timing.backends.stim_phenom import StimPhenomBackend  # noqa: E402
from qec_timing.codes.surface import RotatedSurfaceCode  # noqa: E402
from qec_timing.noise.paper import PaperNoise  # noqa: E402
from qec_timing.schedule import Schedule  # noqa: E402
from qec_timing.spec import MemorySpec  # noqa: E402
from qec_timing.store import Store  # noqa: E402
from qec_timing.studies import runs  # noqa: E402


def _specs():
    return [MemorySpec(RotatedSurfaceCode(3), "Z", Schedule.rounds(dt, 6), PaperNoise(0.02, 1.0),
                       2000, 100 + i) for i, dt in enumerate((0.5, 1.0, 2.0, 4.0))]


def test_parallel_runs_match_serial(tmp_path):
    serial = runs.failures_many(Store(tmp_path / "a"), StimPhenomBackend(), _specs(), workers=1)
    parallel = runs.failures_many(Store(tmp_path / "b"), StimPhenomBackend(), _specs(), workers=3)
    assert serial == parallel
    # Second call reads the store instead of running again.
    again = runs.failures_many(Store(tmp_path / "b"), StimPhenomBackend(), _specs(), workers=3)
    assert again == parallel


@pytest.mark.slow
def test_regime_study_end_to_end(tmp_path):
    from qec_timing.studies import regime

    out = tmp_path / "out"
    regime.main(["--calibration", "config/h2_1e_emulator.json", "--t-round", "0.002",
                 "--distances", "3", "--points", "6", "--dt-max", "64", "--target", "50",
                 "--max-shots", "40000", "--store", str(tmp_path / "store"), "--out", str(out)])
    data = json.loads(next(out.glob("*.json")).read_text())
    row = data["rows"][0]
    assert row["d"] == 3 and len(row["points"]) == 6
    assert row["regime"] in ("wait", "back to back")


def test_large_runs_are_split_into_bounded_chunks(tmp_path, monkeypatch):
    monkeypatch.setattr(runs, "MAX_RUN_BYTES", 4000)             # (6 + 1) rounds x 4 checks = 28 B/shot
    spec = _specs()[0]                                           # 2000 shots
    parts = runs.chunks(spec)
    assert sum(p.shots for p in parts) == 2000 and all(runs.detector_bytes(p) <= 4000 for p in parts)
    assert len({p.seed for p in parts}) == len(parts) and min(p.seed for p in parts) > 2**20
    guppy_like = runs.chunks(spec, per_shot_seeded=True)          # contiguous seed ranges
    assert [p.seed for p in guppy_like] == [spec.seed + sum(q.shots for q in guppy_like[:i])
                                            for i in range(len(guppy_like))]
    ids, f, n = runs.failures(Store(tmp_path), StimPhenomBackend(), spec)
    assert n == 2000 and len(ids) == len(parts) and len(set(ids)) == len(ids)


def test_workers_are_capped_by_available_memory():
    small = _specs()
    assert 1 <= runs.memory_workers(64, small) <= 64
    huge = [MemorySpec(RotatedSurfaceCode(3), "Z", Schedule.rounds(1.0, 6), PaperNoise(0.02, 1.0),
                       10**9, 1)]
    assert runs.memory_workers(64, huge) < 64
