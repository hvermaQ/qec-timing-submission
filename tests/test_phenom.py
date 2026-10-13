"""Rotated surface code, paper noise, Stim and Guppy backends, PyMatching decoder."""

import math

import pytest

pytest.importorskip("stim")      # needs the main env (envs/main.txt)

import numpy as np  # noqa: E402

from qec_timing.backends.stim_phenom import StimPhenomBackend, dem_for
from qec_timing.codes.base import checks_of
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.decoders.base import logical_failures
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
from qec_timing.noise.paper import PaperNoise, p_data
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.stats import Rate, clopper_pearson, pooled_agreement
from qec_timing.testing import contracts as C

BASES = [("Z", "X"), ("X", "Z")]     # (memory basis, data-noise Pauli)


# --- code --------------------------------------------------------------------

@pytest.mark.parametrize("d", [3, 5, 7, 9])
def test_surface_code_contract_and_counts(d):
    code = RotatedSurfaceCode(d)
    C.check_code(code)
    for p in ("X", "Z"):
        checks = checks_of(code, p)
        assert len(checks) == (d * d - 1) // 2
        # Every data qubit in <= 2 checks of each type: graphlike DEM.
        load = np.zeros(code.n_data, int)
        for c in checks:
            load[list(c.support)] += 1
        assert load.max() <= 2


def test_z_checks_match_original_repo():
    # Original RotatedSurfaceCodeZSector(3).z_checks, flattened row-major, and
    # its logical Z (row 0). Detector indices of validated runs depend on this.
    code = RotatedSurfaceCode(3)
    assert [c.support for c in checks_of(code, "Z")] == [(0, 1, 3, 4), (4, 5, 7, 8), (3, 6), (2, 5)]
    assert code.logical("Z") == (0, 1, 2)


# --- noise -------------------------------------------------------------------

def test_paper_noise_equations():
    assert p_data(0.015, 0.0, 5.0) == pytest.approx(0.015, abs=1e-15)   # p_stab never dropped
    expected = 1 - (1 - 0.015) * math.exp(-0.015 * 1.0 * 0.5)             # Eqs. 1-2 by hand
    rn = PaperNoise(0.015, 1.0, 2.0).round_noise(0.0, 0.5)
    assert rn.p_data == pytest.approx(expected, rel=1e-12)
    assert rn.p_read == pytest.approx(0.03)
    C.check_phenomenological_noise(PaperNoise(0.015, 1.0))
    with pytest.raises(ValueError, match="exceeds 1"):
        PaperNoise(0.6, 1.0, b_read=2.0)


# --- backends ----------------------------------------------------------------

def _pair(d, basis, pauli, shots=4000, rounds=3, **extra):
    sched = Schedule.fixed(1.0, float(rounds))
    quiet = MemorySpec(RotatedSurfaceCode(d), basis, sched, PaperNoise(0.0, 0.0, pauli=pauli),
                       shots=20, seed=3, extra=extra)
    noisy = MemorySpec(RotatedSurfaceCode(d), basis, sched, PaperNoise(0.03, 1.0, pauli=pauli),
                       shots=shots, seed=3, extra=extra)
    return quiet, noisy


@pytest.mark.parametrize("basis,pauli", BASES)
@pytest.mark.parametrize("d", [3, 5])
def test_stim_backend_contract(d, basis, pauli):
    C.check_backend(StimPhenomBackend(), *_pair(d, basis, pauli))


@pytest.mark.parametrize("basis,pauli", BASES)
def test_every_single_fault_is_corrected(basis, pauli):
    # One deterministic flip on any data qubit in the middle round, no noise:
    # the decoder must undo it. Decoder built from a noisy DEM (weights only).
    backend = StimPhenomBackend()
    for q in range(25):
        spec = MemorySpec(RotatedSurfaceCode(5), basis, Schedule.fixed(1.0, 3.0),
                          PaperNoise(0.0, 0.0, pauli=pauli), shots=1, seed=0,
                          extra={"inject": [1, q]})
        rec = backend.run(spec)
        dem = dem_for(MemorySpec(spec.code, basis, spec.schedule,
                                 PaperNoise(0.01, 1.0, pauli=pauli), shots=1, seed=0))
        assert not logical_failures(PyMatchingDecoder(dem), rec.detectors, rec.observables).any(), q


def test_decoder_contract():
    spec = _pair(3, "Z", "X")[1]
    C.check_decoder(PyMatchingDecoder, dem_for(spec))
    quiet = _pair(3, "Z", "X")[0]
    C.check_decoder(PyMatchingDecoder, dem_for(quiet))      # p = 0: no error mechanisms


@pytest.mark.slow
@pytest.mark.parametrize("basis,pauli", BASES)
def test_guppy_backend_contract_and_ordering(basis, pauli):
    from qec_timing.backends.guppy_phenom import GuppyPhenomBackend

    guppy, stim_b = GuppyPhenomBackend(), StimPhenomBackend()
    C.check_backend(guppy, *_pair(3, basis, pauli, shots=3000))
    # Detector ordering: one injected fault on each qubit, no noise, gives
    # identical detectors and observable on both backends.
    for q in range(9):
        spec = _pair(3, basis, pauli, inject=[1, q])[0]
        a, b = stim_b.run(spec), guppy.run(spec)
        assert np.array_equal(a.detectors, b.detectors), q
        assert np.array_equal(a.observables, b.observables), q


# --- stats -------------------------------------------------------------------

def test_clopper_pearson_known_values():
    lo, hi = clopper_pearson(0, 100, 0.95)
    assert lo == 0 and hi == pytest.approx(0.0362, abs=1e-4)      # rule-of-three-like bound


def test_pooled_agreement_finds_a_consistent_bias():
    rng = np.random.default_rng(0)
    same = [(Rate(rng.binomial(2000, 0.1), 2000), Rate(rng.binomial(2000, 0.1), 2000))
            for _ in range(20)]
    biased = [(Rate(rng.binomial(2000, 0.09), 2000), Rate(rng.binomial(2000, 0.1), 2000))
              for _ in range(20)]
    assert abs(pooled_agreement(same)["mean_z_sigma"]) < 3
    assert pooled_agreement(biased)["mean_z_sigma"] < -3


def test_hook_safe_order_matches_original_geometry():
    # Original repo, src/qec_timing/h2/geometry.py at d = 3 (verified there against
    # the circuit-level hook_safe ordering for d = 3-11).
    code = RotatedSurfaceCode(3)
    assert [list(c.extraction_order) for c in checks_of(code, "Z")] == [[0, 3, 1, 4], [4, 7, 5, 8], [3, 6], [2, 5]]
    assert [list(c.extraction_order) for c in checks_of(code, "X")] == [[1, 2, 4, 5], [3, 4, 6, 7], [0, 1], [7, 8]]
