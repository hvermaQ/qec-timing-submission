"""The figure-producing studies: their core calculations, on known inputs."""

import numpy as np
import pytest

pytest.importorskip("stim")      # needs the main env (envs/main.txt)

from qec_timing.backends.stim_phenom import StimPhenomBackend  # noqa: E402
from qec_timing.codes.surface import RotatedSurfaceCode  # noqa: E402
from qec_timing.noise.paper import PaperNoise, p_data  # noqa: E402
from qec_timing.schedule import Schedule  # noqa: E402
from qec_timing.spec import MemorySpec  # noqa: E402
from qec_timing.store import Store  # noqa: E402
from qec_timing.studies import runs  # noqa: E402


def test_scaling_fit_recovers_a_known_slope():
    from qec_timing.studies.scaling import fit_inverse

    rows = [{"d": d, "optimum": {"dt_star": 1 / (0.4 * d - 1), "lo": 1 / (0.4 * d - 1) * 0.99,
                                 "hi": 1 / (0.4 * d - 1) * 1.01}} for d in (5, 7, 9, 11)]
    f = fit_inverse(rows)
    assert f["eta"] == pytest.approx(0.4, abs=1e-6) and f["z"] == pytest.approx(-1.0, abs=1e-5)


def test_effective_lambda_fit_inverts_the_paper_equations():
    from qec_timing.studies.effective import fit_lambda

    dts = (1.0, 2.0, 4.0, 8.0)
    p_stab, lam = fit_lambda(dts, [p_data(2.5e-3, 0.13, dt) for dt in dts])
    assert p_stab == pytest.approx(2.5e-3, rel=1e-9) and lam == pytest.approx(0.13, rel=1e-9)


def test_idle_scaling_ansatz_gives_the_predicted_power_laws():
    from qec_timing.studies.idle_scaling import dt_star_gc

    fit = {"p_e": 1.5e-2, "alpha": 2.0}
    g = np.array([1e-4, 2e-4, 4e-4])
    lin = [dt_star_gc(x, 0.0, fit) for x in g]
    quad = [dt_star_gc(0.0, x, fit) for x in g * 1e-2]
    assert np.polyfit(np.log(g), np.log(lin), 1)[0] == pytest.approx(-1.0, abs=0.01)
    assert np.polyfit(np.log(g), np.log(quad), 1)[0] == pytest.approx(-0.5, abs=0.01)


def test_decode_many_agrees_with_failures(tmp_path):
    store, b = Store(tmp_path), StimPhenomBackend()
    specs = [MemorySpec(RotatedSurfaceCode(3), "Z", Schedule.rounds(dt, 6), PaperNoise(0.03, 1.0), 3000, 7 + i)
             for i, dt in enumerate((0.5, 1.0))]
    plain = runs.failures_many(store, b, specs)
    multi = runs.decode_many(store, b, specs, [{"full": b.dem(s)} for s in specs])
    assert [m["full"] for m in multi] == [f for _, f, _ in plain]


def test_per_qubit_sources_add_up_to_the_total():
    from qec_timing.studies.per_qubit import study

    r = study(3, "textbook", __import__("qec_timing.noise.circuit", fromlist=["IdleNoise"]).IdleNoise(gamma=1.5e-3),
              60_000, 5)
    z = {k: np.array(v) for k, v in r["z"].items()}
    parts = 0.5 * (1 - (1 - 2 * z["data"]) * (1 - 2 * z["ancilla"]) * (1 - 2 * z["idle"]))   # XOR of independent parts
    assert len(r["grid"]) == 9 and np.allclose(parts, z["total"], atol=4e-3)
    assert z["total"].max() / z["total"].min() > 2                                         # qubits are not equal
