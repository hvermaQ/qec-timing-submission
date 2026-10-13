"""The run store: round trip, immutability, integrity and lineage."""

import json

import numpy as np
import pytest

from fixtures.toy import FixedNoise, NumpySampler, RepetitionCode
from qec_timing.records import Derived, EffectiveModel, Estimate
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.store import Store


@pytest.fixture
def stored(tmp_path):
    spec = MemorySpec(RepetitionCode(5), "Z", Schedule.fixed(1.0, 6.0),
                      FixedNoise(0.05, 0.02), shots=200, seed=11)
    backend = NumpySampler()
    record = backend.run(spec)
    record.attachments["result_0.txt"] = b"verbatim backend payload"
    store = Store(tmp_path)
    run_id = store.save_run(spec, backend.name, backend.versions(), record)
    return store, spec, record, run_id


def test_run_roundtrip(stored):
    store, spec, record, run_id = stored
    manifest, back = store.load_run(run_id)
    assert manifest["spec"] == spec.to_json()
    assert np.array_equal(back.detectors, record.detectors)
    assert np.array_equal(back.observables, record.observables)
    for k in record.rounds:
        assert np.array_equal(back.rounds[k], record.rounds[k])
    assert back.attachments == {"result_0.txt": b"verbatim backend payload"}
    assert store.runs() == [run_id]


def test_raw_data_is_never_rewritten(stored):
    store, spec, record, _ = stored
    with pytest.raises(FileExistsError):
        store.save_run(spec, NumpySampler.name, {}, record)


def test_tampered_raw_data_is_detected(stored):
    store, _, _, run_id = stored
    path = store.run_dir(run_id) / "raw" / "observables.npy"
    blob = bytearray(path.read_bytes())
    blob[-1] ^= 1
    path.write_bytes(bytes(blob))
    with pytest.raises(IOError, match="checksum"):
        store.load_run(run_id)


def test_model_and_derived_with_lineage(stored):
    store, _, _, run_id = stored
    model = EffectiveModel("edge_fit", {"p_data": Estimate(0.05, 0.04, 0.06)}, (run_id,),
                           dem="error(0.05) D0 D1\n")
    store.save_model(run_id, model)
    back = store.load_model(run_id, "edge_fit")
    assert back.params == model.params and back.dem == model.dem

    did = store.save_derived(Derived("dt_star", {"dt_star": 1.7}, (run_id,)))
    assert store.load_derived(did).data == {"dt_star": 1.7}
    # Same commit for run and result here; only a dirty tree can be reported.
    assert all("dirty" in i for i in store.check_lineage(did))

    # A run made by other code is flagged.
    path = store.run_dir(run_id) / "manifest.json"
    m = json.loads(path.read_text())
    m["code"] = {"commit": "0" * 40, "dirty": False}
    path.write_text(json.dumps(m))
    assert any("made by commit 0000" in i for i in store.check_lineage(did))

    with pytest.raises(KeyError, match="parents not in store"):
        store.save_derived(Derived("orphan", {}, ("0" * 16,)))
