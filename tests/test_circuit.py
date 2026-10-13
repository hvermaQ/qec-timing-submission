"""Circuit-level noise, the Stim circuit backend, the edge extractor and dt* analysis."""

import math

import numpy as np
import pytest

pytest.importorskip("stim")      # needs the main env (envs/main.txt)

from qec_timing.analysis.interval import dt_grid, optimum, rate  # noqa: E402
from qec_timing.backends.stim_circuit import StimCircuitBackend, alignment, dem_for  # noqa: E402
from qec_timing.backends.stim_phenom import StimPhenomBackend  # noqa: E402
from qec_timing.codes.base import checks_of  # noqa: E402
from qec_timing.codes.surface import RotatedSurfaceCode  # noqa: E402
from qec_timing.decoders.base import logical_failures  # noqa: E402
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder  # noqa: E402
from qec_timing.extract.edges import EdgeExtractor, xor  # noqa: E402
from qec_timing.hardware import Calibration  # noqa: E402
from qec_timing.noise.circuit import CircuitNoise, IdleNoise  # noqa: E402
from qec_timing.noise.effective import EffectiveNoise  # noqa: E402
from qec_timing.schedule import Schedule  # noqa: E402
from qec_timing.spec import MemorySpec  # noqa: E402
from qec_timing.testing import contracts as C  # noqa: E402

# H2-1E gate rates scaled x4.76 (p2 = 5e-3), as in the original notebooks 07/08.
GATES = dict(p1=8.999999999999999e-05, p2=0.005, p_meas=0.004738095238095238,
             p_init=0.00019047619047619048)


# --- noise -------------------------------------------------------------------

def test_idle_channel_is_z_only_with_expected_probability():
    # Original notebook 07's check: dephasing gives Z only, at gamma t + sin^2(sqrt(c) t) mod 2.
    for g, c in ((3e-3, 0.0), (0.0, 2e-4), (1.5e-3, 5e-5)):
        for t in (1.0, 8.0, 32.0):
            px, py, pz = IdleNoise(gamma=g, c=c).channel(t)
            a, b = g * t, math.sin(math.sqrt(c) * t) ** 2
            assert px == py == 0 and pz == pytest.approx(a + b - 2 * a * b, abs=1e-12)


def test_depolarizing_idle_composes_over_time():
    ch = IdleNoise(depol=0.01).channel(3.0)
    one = 1 - 4 * 0.01 / 3
    assert ch[0] == ch[1] == pytest.approx((1 - one ** 3) / 4)


def test_from_calibration_matches_calibration_idle():
    cal = Calibration(p1=1.89e-5, p2=1.05e-3, p_meas0=6e-4, p_meas1=1.39e-3, p_init=4e-5,
                      gamma=0.0028, quad_rate=0.043, source="H2-1E emulator defaults 2025-07-16")
    n = CircuitNoise.from_calibration(cal, t_round=0.1)
    for k in (1.0, 5.0, 40.0):
        assert n.idle.pz(k) == pytest.approx(cal.idle_pz(k * 0.1), rel=1e-9)
    with pytest.raises(ValueError, match="never assumed"):
        CircuitNoise.from_calibration(cal)


def test_dephasing_refuses_z_basis():
    noise = CircuitNoise(**GATES, idle=IdleNoise(gamma=1e-3))
    with pytest.raises(ValueError, match="invisible"):
        MemorySpec(RotatedSurfaceCode(3), "Z", Schedule.rounds(1.0, 5), noise, 10, 1)


# --- backend -----------------------------------------------------------------

@pytest.mark.parametrize("basis", ["X", "Z"])
@pytest.mark.parametrize("d", [3, 5, 7])
def test_alignment_covers_every_check(d, basis):
    pos = alignment(d, basis)
    assert sorted(pos.values()) == list(range(len(checks_of(RotatedSurfaceCode(d), basis))))


@pytest.mark.parametrize("basis", ["X", "Z"])
def test_circuit_backend_contract(basis):
    quiet = CircuitNoise(0.0, 0.0, 0.0, placement="uniform")
    noisy = CircuitNoise(**GATES, idle=IdleNoise(depol=2e-3), placement="uniform")
    code, sched = RotatedSurfaceCode(3), Schedule.rounds(2.0, 4)
    C.check_backend(StimCircuitBackend(), MemorySpec(code, basis, sched, quiet, 50, 1),
                    MemorySpec(code, basis, sched, noisy, 2000, 1))


@pytest.mark.parametrize("placement,dt,R,seed,gamma,c,expected", [
    # Original repo cache, 07_dephasing_interval and 08_uniform_noise_premise.
    ("data_interval", 21.333333333333332, 9, 2, 0.0, 5e-05, 17652),
    ("uniform", 38.4, 5, 2, 0.0015, 0.0, 26589),
])
def test_reproduces_original_failure_counts_exactly(placement, dt, R, seed, gamma, c, expected):
    noise = CircuitNoise(**GATES, idle=IdleNoise(gamma=gamma, c=c), placement=placement)
    spec = MemorySpec(RotatedSurfaceCode(3), "X", Schedule.rounds(dt, R), noise, 100_000, seed)
    rec = StimCircuitBackend().run(spec)
    fails = logical_failures(PyMatchingDecoder(dem_for(spec)), rec.detectors, rec.observables)
    assert int(fails.sum()) == expected


# --- extractor ---------------------------------------------------------------

def test_edge_extractor_recovers_known_parameters():
    # Phenomenological circuit with known p_data / p_read: the estimator must return them.
    truth = EffectiveNoise(p_data=0.012, p_read=0.008, pauli="Z")
    spec = MemorySpec(RotatedSurfaceCode(5), "X", Schedule.rounds(1.0, 12), truth, 100_000, 3)
    m = EdgeExtractor().extract(spec, StimPhenomBackend().run(spec), "test")
    for k, v in (("p_data", 0.012), ("p_read", 0.008)):
        e = m.params[k]
        assert e.low <= v <= e.high, (k, e)
    assert not m.info["estimator_broken"]


def test_effective_noise_composes_the_wait():
    idle = IdleNoise(gamma=1e-3)
    n = EffectiveNoise(0.01, 0.009, wait=idle)
    assert n.round_noise(0, 1.0).p_data == pytest.approx(0.01)
    assert n.round_noise(0, 5.0).p_data == pytest.approx(float(xor(0.01, 4e-3)))


# --- analysis ----------------------------------------------------------------

def test_dt_grid_and_rate():
    g = dt_grid(192, 5)
    assert all(R >= 5 and dt * R == pytest.approx(192) for dt, R in g)
    assert g[0] == (1.0, 192)
    assert math.isnan(rate(60, 100, 10)[0])                     # saturated
    assert rate(10, 1000, 10)[0] == pytest.approx(-math.log(1 - 0.02) / 20)


def test_optimum_finds_a_parabola_vertex():
    dt = np.geomspace(1, 64, 16)
    r = 1e-3 * np.exp(0.3 * (np.log(dt) - np.log(7.0)) ** 2)
    o = optimum(dt, np.full(16, 0.1), r, r * 0.01)
    assert o.dt_star == pytest.approx(7.0, rel=0.02) and o.interior


# --- native gates (Selene compile: slow) -------------------------------------

@pytest.mark.slow
def test_native_backend_reproduces_original_exactly(tmp_path):
    # Original repo cache, 09_native_uniform_noise: d=3, dt=4, R=48, gamma=0.3 p2, seed 1.
    from qec_timing.backends.stim_native import StimNativeBackend

    b = StimNativeBackend(cache_dir=tmp_path)
    noise = CircuitNoise(**GATES, idle=IdleNoise(gamma=0.0015), placement="uniform")
    spec = MemorySpec(RotatedSurfaceCode(3), "X", Schedule.rounds(4.0, 48), noise, 100_000, 1)
    rec = b.run(spec)
    fails = logical_failures(PyMatchingDecoder(b.dem(spec)), rec.detectors, rec.observables)
    assert int(fails.sum()) == 24500


@pytest.mark.slow
@pytest.mark.parametrize("basis", ["X", "Z"])
def test_native_backend_contract(basis, tmp_path):
    from qec_timing.backends.stim_native import StimNativeBackend

    quiet = CircuitNoise(0.0, 0.0, 0.0, placement="uniform")
    noisy = CircuitNoise(**GATES, idle=IdleNoise(depol=2e-3), placement="uniform")
    code, sched = RotatedSurfaceCode(3), Schedule.rounds(2.0, 4)
    C.check_backend(StimNativeBackend(cache_dir=tmp_path), MemorySpec(code, basis, sched, quiet, 50, 1),
                    MemorySpec(code, basis, sched, noisy, 2000, 1))
