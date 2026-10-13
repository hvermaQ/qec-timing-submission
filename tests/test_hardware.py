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


# --- calibration experiments -------------------------------------------------

def test_idle_fit_recovers_known_rates():
    from qec_timing.hardware.calibration_experiments import Rate, fit_idle

    rng = np.random.default_rng(3)
    gamma, c, spam, n = 2e-3, 4e-5, 0.01, 200_000
    layers = [0, 4, 8, 16, 32, 48, 64]
    rates = []
    for L in layers:
        lin, quad = gamma * L, np.sin(np.sqrt(c) * L) ** 2
        pz = lin + quad - 2 * lin * quad
        P = 0.5 * (1 - (1 - 2 * spam) * (1 - 2 * pz))
        rates.append(Rate(int(rng.binomial(n, P)), n))
    fit = fit_idle(layers, rates)
    assert abs(fit["gamma_per_layer"] - gamma) < 4 * fit["gamma_per_layer_se"]
    assert abs(fit["c_per_layer"] - c) < 4 * fit["c_per_layer_se"]
    assert fit["chi2_per_dof"] < 3


def test_calibration_fields_invert_the_emulator_convention():
    import math

    from qec_timing.hardware import Calibration
    from qec_timing.hardware.calibration_experiments import to_calibration_fields

    # Emulator rates -> per-layer (c_L, gamma_L) at tau = 5 ms -> back to the same rates.
    cal = Calibration(p1=0, p2=0, p_meas0=0, p_meas1=0, p_init=0, gamma=0.0028,
                      quad_rate=0.043, source="H2-1E defaults")
    tau = 5e-3
    c_layer = (cal.omega * tau / 2) ** 2
    f = to_calibration_fields({"gamma_per_layer": cal.gamma * tau, "c_per_layer": c_layer}, tau)
    assert f["gamma"] == pytest.approx(0.0028) and f["quad_rate"] == pytest.approx(0.043)
    assert math.isclose(Calibration(**{**cal.__dict__, **f}).idle_pz(0.1), cal.idle_pz(0.1))


@pytest.mark.h2
def test_calibration_programs_build_and_run_locally():
    pytest.importorskip("hugr_qir")
    from hugr_qir.output import OutputFormat
    from selene_sim import Stim, build

    from qec_timing.hardware.calibration_experiments import (fit_readout, flips, idle_program,
                                                             readout_program)
    from qec_timing.hardware.qir import _convert

    ro = readout_program(4)
    shots = [{k: [v] for k, v in s} for s in
             build(ro.compile()).run_shots(simulator=Stim(), n_qubits=8, n_shots=20, random_seed=1)]
    fit = fit_readout(shots)
    assert fit["p_meas0"] == 0 and fit["p_meas1"] == 0           # ideal simulator
    for basis in ("X", "Z"):
        prog = idle_program(2, 2, 6, basis)
        shots = [{k: [v] for k, v in s} for s in
                 build(prog.compile()).run_shots(simulator=Stim(), n_qubits=4, n_shots=40, random_seed=1)]
        assert flips(shots, basis).k == 0                        # no idle noise locally
        assert {int(s["par"][0]) for s in shots} == {0, 1}       # feed-forward exercised
        assert len(_convert(prog.compile(), OutputFormat.BITCODE)) > 0   # QIR, validated


def test_calib_fit_end_to_end_recovers_device_rates(tmp_path):
    import json

    from qec_timing.hardware import Calibration
    from qec_timing.hardware.cli import main

    truth = Calibration(p1=1.89e-5, p2=1.05e-3, p_meas0=6e-4, p_meas1=1.39e-3, p_init=4e-5,
                        gamma=0.05, quad_rate=0.4, source="synthetic")
    tau, rng = 0.01, np.random.default_rng(5)                  # 10 ms per spectator layer
    truth.__class__(**{**truth.__dict__, "source": "base"}).save(tmp_path / "base.json")

    def job(name, meta, shots):
        d = tmp_path / name
        d.mkdir()
        (d / "program.json").write_text(json.dumps(meta))
        (d / "result_qsys.json").write_text(json.dumps(shots))
        return d

    n = 4000
    ro = job("ro", {"experiment": "readout"},
             [{**{f"r0_{i}": [int(rng.random() < truth.p_meas0)] for i in range(4)},
               **{f"r1_{i}": [int(rng.random() > truth.p_meas1)] for i in range(4)}} for _ in range(n)])
    idle = []
    for L in (0, 4, 8, 16, 32, 48):
        pz = truth.idle_pz(L * tau)
        p_flip = 0.5 * (1 - (1 - 2 * 0.003) * (1 - 2 * pz))     # 0.3% SPAM floor
        shots = []
        for _ in range(n):
            par = int(rng.random() < 0.5)
            shots.append({"par": [par], **{f"t{i}": [int(rng.random() < p_flip) ^ par] for i in range(8)}})
        idle.append(job(f"idle{L}", {"experiment": "idle", "basis": "X", "layers": L}, shots))
    out = tmp_path / "measured.json"
    main(["calib-fit", "--readout", str(ro), "--idle", *map(str, idle), "--layer-seconds", str(tau),
          "--base", str(tmp_path / "base.json"), "--out", str(out)])
    got = Calibration.load(out)
    assert got.gamma == pytest.approx(truth.gamma, rel=0.25)
    assert got.quad_rate == pytest.approx(truth.quad_rate, rel=0.25)
    assert got.p_meas1 == pytest.approx(truth.p_meas1, abs=4e-4)
    assert got.p2 == truth.p2 and "measured" in got.source
