"""Hardware path: bit conversion (any env) and the H2 program (H2 env only)."""

import numpy as np
import pytest

from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.noise.paper import PaperNoise
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec


def _spec(shots=10, p=0.0, basis="X"):
    return MemorySpec(RotatedSurfaceCode(3), basis, Schedule.rounds(1.0, 2),
                      PaperNoise(p, 0.0, b_read=0.0, pauli="Z" if basis == "X" else "X"), shots, 7)


def test_record_from_bits_layout():
    spec = _spec(shots=1)
    syn = np.zeros((1, 2, 4), bool)
    dat = np.zeros((1, 9), bool)
    syn[0, 1, 2] = True                       # check 2 fires in round 1 only
    dat[0, 0] = True                          # data qubit 0 flipped at readout
    rec = record_from_bits(spec, syn, dat)
    det = rec.detectors.reshape(3, 4)
    assert det[1, 2] and det[0].sum() == 0
    # Final block: check 2 back to 0 (fires), checks containing qubit 0 fire.
    assert rec.observables[0, 0]              # qubit 0 is on logical X (column 0)


def test_bits_from_shots_requires_every_tag():
    shot = {f"s{r}_{c}": 0 for r in range(2) for c in range(4)} | {f"m{i}": 0 for i in range(9)}
    syn, dat = bits_from_shots([shot], 2, 4, 9)
    assert syn.shape == (1, 2, 4) and dat.shape == (1, 9)
    del shot["m3"]
    with pytest.raises(ValueError, match="missing"):
        bits_from_shots([shot], 2, 4, 9)


@pytest.mark.h2
@pytest.mark.parametrize("basis", ["X", "Z"])
def test_hardware_program_passes_backend_contract_locally(basis):
    pytest.importorskip("hugr_qir")
    from qec_timing.hardware.selene_local import SeleneQirProgramBackend
    from qec_timing.testing import contracts as C

    C.check_backend(SeleneQirProgramBackend(), _spec(30, 0.0, basis), _spec(3000, 0.04, basis))


@pytest.mark.h2
def test_qir_matches_stage7a_byte_for_byte():
    pytest.importorskip("hugr_qir")
    import hashlib

    from qec_timing.hardware.qir import build_qir

    spec = MemorySpec(RotatedSurfaceCode(3), "X", Schedule.rounds(1.0, 2),
                      PaperNoise(0.05, 0.0, b_read=0.0, pauli="Z"), 100, 7_000_000)
    bc = build_qir(spec)["bitcode"]
    # sha256 of the original repo's validated results/stage7a/d3_r2_X.bc
    assert hashlib.sha256(bc).hexdigest().startswith("e30cc999f544")


@pytest.mark.h2
def test_job_results_become_a_stored_run(tmp_path):
    # A Nexus-style job directory whose result is the hardware program's own output
    # (run locally), turned into a stored run and read back.
    pytest.importorskip("hugr_qir")
    import json

    from qec_timing.hardware.providers import store_results
    from qec_timing.hardware.qir import build_program
    from qec_timing.store import Store
    from selene_sim import Stim, build

    spec = _spec(shots=200, p=0.04)
    inst = build(build_program(spec).compile())
    shots = [{k: [v] for k, v in shot}
             for shot in inst.run_shots(simulator=Stim(), n_qubits=10, n_shots=200, random_seed=7)]
    job = tmp_path / "job"
    job.mkdir()
    (job / "program.json").write_text(json.dumps({"spec": spec.to_json(), "p_inject": 0.04}))
    (job / "job.json").write_text(json.dumps({"provider": "nexus", "job_id": "test"}))
    (job / "result_qsys.json").write_text(json.dumps(shots))
    store = Store(tmp_path / "store")
    run_id = store_results(store, job, "nexus:test")
    manifest, rec = store.load_run(run_id)
    assert rec.shots == 200 and rec.detectors.any()
    assert set(rec.attachments) == {"program.json", "job.json", "result_qsys.json"}
