"""Schedule, spec, records, registry and calibration: the plain-data layer."""

import math

import numpy as np
import pytest

from fixtures.toy import FixedNoise, RepetitionCode, SteaneCode
from qec_timing import registry
from qec_timing.hardware import Calibration
from qec_timing.records import DetectorLayout, RawRecord, pack_bits, unpack_bits
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec


# --- schedule ----------------------------------------------------------------

def test_fixed_schedule_has_no_float_drift():
    s = Schedule.fixed(dt=0.1, T=1.0)
    assert s.n_rounds == 10                      # a float accumulator gives 11
    assert s.starts[-1] == pytest.approx(0.9, abs=1e-12)
    assert s.total_time == pytest.approx(1.0, abs=1e-12)


def test_schedule_rejects_off_tick_interval():
    with pytest.raises(ValueError, match="multiple of tick"):
        Schedule.fixed(dt=0.0015, T=1.0, tick=1e-3)


def test_schedule_json_roundtrip_and_constant_form():
    s = Schedule.fixed(dt=0.25, T=2.0)
    assert Schedule.from_json(s.to_json()) == s
    v = Schedule(intervals=(100, 250, 100))
    assert not v.is_constant and Schedule.from_json(v.to_json()) == v


# --- spec --------------------------------------------------------------------

def _spec(**kw):
    base = dict(code=RepetitionCode(3), basis="Z", schedule=Schedule.fixed(1.0, 4.0),
                noise=FixedNoise(0.01, 0.01), shots=10, seed=1)
    base.update(kw)
    return MemorySpec(**base)


def test_spec_refuses_invisible_noise():
    # Z-basis memory measures Z checks; Z-type (dephasing) noise commutes with them.
    with pytest.raises(ValueError, match="invisible"):
        _spec(noise=FixedNoise(0.01, 0.01, pauli="Z"))
    _spec(noise=FixedNoise(0.01, 0.01, pauli="Z"), allow_invisible_noise=True)


def test_spec_refuses_basis_without_checks():
    with pytest.raises(ValueError, match="no X checks"):
        _spec(basis="X", noise=FixedNoise(0.01, 0.01, pauli="Z"))


def test_run_id_is_a_content_hash():
    assert _spec().run_id("b") == _spec().run_id("b")
    assert _spec().run_id("b") != _spec(seed=2).run_id("b")
    assert _spec().run_id("b") != _spec().run_id("other_backend")
    assert _spec().run_id("b") != _spec(code=RepetitionCode(5)).run_id("b")


# --- records -----------------------------------------------------------------

@pytest.mark.parametrize("n", [1, 63, 64, 65, 200])
def test_pack_unpack_roundtrip(n):
    bits = np.random.default_rng(n).random((7, n)) < 0.5
    words = pack_bits(bits)
    assert words.shape == (7, -(-n // 64)) and words.dtype == np.uint64
    assert np.array_equal(unpack_bits(words, n), bits)


def test_pack_is_lsb_first():
    bits = np.zeros(70, dtype=bool)
    bits[[0, 63, 64]] = True
    w = pack_bits(bits)
    assert w[0] == np.uint64(1) | (np.uint64(1) << np.uint64(63)) and w[1] == 1


def test_unpack_rejects_dirty_padding():
    with pytest.raises(ValueError, match="padding"):
        unpack_bits(np.array([1 << 10], dtype=np.uint64), 5)


def test_raw_record_validates_shapes():
    layout = DetectorLayout(n_rounds=2, n_checks=3)
    rounds = {k: np.zeros(2) for k in ("dt", "t", "p_data", "p_read")}
    RawRecord(layout, np.zeros((4, 9), bool), np.zeros((4, 1), bool), rounds)
    with pytest.raises(ValueError, match="detectors shape"):
        RawRecord(layout, np.zeros((4, 8), bool), np.zeros((4, 1), bool), rounds)
    with pytest.raises(ValueError, match="missing"):
        RawRecord(layout, np.zeros((4, 9), bool), np.zeros((4, 1), bool), {"dt": np.zeros(2)})


# --- registry ----------------------------------------------------------------

def test_registry_create_and_duplicate():
    registry.register("code", "_test_rep")(RepetitionCode)
    try:
        assert registry.create("code", "_test_rep", d=5).n_data == 5
        with pytest.raises(ValueError, match="already registered"):
            registry.register("code", "_test_rep")(SteaneCode)
        with pytest.raises(KeyError, match="available"):
            registry.create("code", "_missing")
    finally:
        registry.unregister("code", "_test_rep")


# --- calibration -------------------------------------------------------------

def _h2(**kw):
    # H2-1E emulator defaults (2025-07-16 table), as in the original repo's Stage 7a.
    base = dict(p1=1.89e-5, p2=1.05e-3, p_meas0=6e-4, p_meas1=1.39e-3, p_init=4e-5,
                gamma=0.0028, quad_rate=0.043, source="H2-1E emulator defaults 2025-07-16")
    base.update(kw)
    return Calibration(**base)


def test_calibration_idle_matches_stage7a_numbers():
    # Stage 7a report: p_z over one 2 ms round = 5.9e-6 (cycles), 5.6e-6 (radians).
    assert _h2().idle_pz(2e-3) == pytest.approx(5.89e-6, rel=1e-2)
    assert _h2(quad_convention="radians").idle_pz(2e-3) == pytest.approx(5.61e-6, rel=1e-2)
    assert _h2().omega == pytest.approx(2 * math.pi * 0.086)


def test_calibration_roundtrip_and_validation(tmp_path):
    c = _h2(t_round=0.1)
    c.save(tmp_path / "cal.json")
    assert Calibration.load(tmp_path / "cal.json") == c
    with pytest.raises(ValueError, match="where its numbers"):
        _h2(source="")
    with pytest.raises(ValueError, match="not a probability"):
        _h2(p2=1.5)


def test_overlapping_seed_ranges():
    from qec_timing.spec import overlapping_seed_ranges
    a, b, c = _spec(seed=0, shots=100), _spec(seed=50, shots=10), _spec(seed=100, shots=5)
    assert overlapping_seed_ranges([a, b, c]) == [(0, 1)]      # [0,100) meets [50,60)
    assert overlapping_seed_ranges([a, c]) == []                 # [0,100) and [100,105) touch only


def test_spec_json_roundtrip_through_registry():
    from qec_timing.codes.surface import RotatedSurfaceCode
    from qec_timing.noise.circuit import CircuitNoise, IdleNoise
    from qec_timing.noise.paper import PaperNoise
    from qec_timing.spec import spec_from_json

    for noise, basis in ((PaperNoise(0.01, 1.0, pauli="Z"), "X"),
                         (CircuitNoise(1e-4, 1e-3, 1e-3, idle=IdleNoise(gamma=1e-3)), "X")):
        spec = MemorySpec(RotatedSurfaceCode(3), basis, Schedule.rounds(2.0, 4), noise, 10, 3)
        back = spec_from_json(spec.to_json())
        assert back.to_json() == spec.to_json() and back.run_id("b") == spec.run_id("b")


def test_pack_bits_matches_the_original_definition():
    # The first implementation (padded uint64, 64x memory) defined the stored format;
    # the packbits version must give identical words.
    def original(bits):
        n = bits.shape[-1]
        nw = -(-n // 64)
        pad = np.zeros(bits.shape[:-1] + (nw * 64,), np.uint64)
        pad[..., :n] = bits
        w = np.uint64(1) << np.arange(64, dtype=np.uint64)
        return (pad.reshape(bits.shape[:-1] + (nw, 64)) * w).sum(-1, dtype=np.uint64)

    rng = np.random.default_rng(0)
    for n in (1, 63, 64, 65, 200, 1464):
        b = rng.random((40, n)) < 0.3
        assert np.array_equal(pack_bits(b), original(b))
