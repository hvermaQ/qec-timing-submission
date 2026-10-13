"""The contract checks accept correct implementations and reject broken ones.

A contract that never fails proves nothing, so every check is also run against a
deliberately broken implementation.
"""

import dataclasses
from dataclasses import dataclass

import numpy as np
import pytest

from fixtures.toy import (FixedIdle, FixedNoise, NullDecoder, NumpySampler, RepetitionCode,
                          SteaneCode)
from qec_timing.codes.base import Check
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.testing import ContractError
from qec_timing.testing import contracts as C

# --- codes -------------------------------------------------------------------

@pytest.mark.parametrize("code", [RepetitionCode(3), RepetitionCode(7), SteaneCode()])
def test_valid_codes_pass(code):
    C.check_code(code)


@dataclass(frozen=True)
class _Mutated:
    """Wrap a valid code and replace its checks or one logical."""
    base: object
    checks_: tuple | None = None
    logical_: dict | None = None
    name = "mutated"

    def params(self):
        return {}

    @property
    def n_data(self):
        return self.base.n_data

    @property
    def checks(self):
        return self.checks_ if self.checks_ is not None else self.base.checks

    def logical(self, p):
        return (self.logical_ or {}).get(p, self.base.logical(p))


def test_anticommuting_checks_fail():
    steane = SteaneCode()
    bad = steane.checks[:-1] + (Check("Z", (0, 1, 2)),)          # odd overlap with X checks
    with pytest.raises(ContractError, match="anticommute"):
        C.check_code(_Mutated(steane, checks_=bad))


def test_logical_that_is_a_stabilizer_fails():
    with pytest.raises(ContractError, match="acts trivially|commute"):
        C.check_code(_Mutated(RepetitionCode(3), logical_={"Z": (0, 1)}))


def test_logical_anticommuting_with_check_fails():
    with pytest.raises(ContractError, match="anticommutes"):
        C.check_code(_Mutated(SteaneCode(), logical_={"Z": (0,)}))


def test_bad_extraction_order_fails():
    bad = (Check("Z", (0, 1), order=(0, 2)), Check("Z", (1, 2)))
    with pytest.raises(ContractError, match="permutation"):
        C.check_code(_Mutated(RepetitionCode(3), checks_=bad))


# --- backends ----------------------------------------------------------------

def _specs(code=None, basis="Z", pauli="X", shots=4000):
    code = code or RepetitionCode(5)
    sched = Schedule.fixed(1.0, 3.0)
    quiet = MemorySpec(code, basis, sched, FixedNoise(0.0, 0.0, pauli), shots=50, seed=5)
    noisy = MemorySpec(code, basis, sched, FixedNoise(0.03, 0.02, pauli), shots=shots, seed=5)
    return quiet, noisy


@pytest.mark.parametrize("code,basis,pauli", [(RepetitionCode(5), "Z", "X"),
                                              (SteaneCode(), "Z", "X"),
                                              (SteaneCode(), "X", "Z")])
def test_sampler_passes_backend_contract(code, basis, pauli):
    C.check_backend(NumpySampler(), *_specs(code, basis, pauli))


class _IgnoresSeed(NumpySampler):
    def run(self, spec):
        return super().run(dataclasses.replace(spec, seed=0))


class _DoublesNoise(NumpySampler):
    """Applies p_data twice per round but reports it once: the 'two draws' bug."""
    def run(self, spec):
        n = spec.noise
        doubled = FixedNoise(1 - (1 - n.p_data) ** 2, n.p_read, n.pauli)
        rec = super().run(dataclasses.replace(spec, noise=doubled))
        rec.rounds["p_data"] = np.full_like(rec.rounds["p_data"], n.p_data)
        return rec


class _ReversedDetectors(NumpySampler):
    """Writes rounds in reverse order: detectors no longer follow the layout."""
    def run(self, spec):
        rec = super().run(spec)
        C_ = rec.layout.n_checks
        blocks = rec.detectors.reshape(rec.shots, -1, C_)[:, ::-1]
        rec.detectors = blocks.reshape(rec.shots, -1)
        return rec


@pytest.mark.parametrize("broken,match", [(_IgnoresSeed, "seed"),
                                          (_DoublesNoise, "rate"),
                                          (_ReversedDetectors, "rate")])
def test_broken_backends_fail(broken, match):
    with pytest.raises(ContractError, match=match):
        C.check_backend(broken(), *_specs())


# --- noise, decoders, idle sources -------------------------------------------

def test_noise_contract():
    C.check_phenomenological_noise(FixedNoise(0.01, 0.02))


def test_decoder_contract():
    C.check_decoder(NullDecoder, dem="")

    class Flips(NullDecoder):
        def decode_batch(self, detectors):
            return np.ones((len(detectors), 1), dtype=bool)

    with pytest.raises(ContractError, match="no detection events"):
        C.check_decoder(Flips, dem="")


def test_idle_source_contract():
    C.check_idle_source(FixedIdle())
    prof = FixedIdle().idle_profile("uniform")
    assert prof.idle_fraction == pytest.approx(7 / 16)
    assert prof.share_in_stretches_at_least(4) == pytest.approx(4 / 7)


def test_wilson_interval_covers_and_narrows():
    lo, hi = C.wilson(50, 1000)
    assert lo < 0.05 < hi and hi - lo < 0.05
    assert C.wilson(0, 0) == (0.0, 1.0)
