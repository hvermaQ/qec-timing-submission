"""Contract checks: what any implementation of an interface must satisfy.

Use them in tests for a new component:

    from qec_timing.testing import contracts
    contracts.check_code(MyCode(d=5))
    contracts.check_backend(MyBackend(), quiet_spec, noisy_spec)

Each check raises `ContractError` naming the first violation. They are written to
catch the mistakes that are silent in a sweep: a check that anticommutes with a
logical, a detector stream in the wrong order, noise applied at the wrong rate,
a seed that does not change the noise.
"""

from __future__ import annotations

import dataclasses
import json
import math
from typing import Any, Callable

import numpy as np

from qec_timing.apps.base import IdleSource
from qec_timing.backends.base import Backend, run_checked
from qec_timing.codes.base import PAULIS, StabilizerCode, checks_of, other
from qec_timing.decoders.base import Decoder
from qec_timing.noise.base import PhenomenologicalNoise, RoundNoise
from qec_timing.spec import MemorySpec

# z for a two-sided 99.9% interval: a correct implementation fails a rate check
# about once per 1000 checks, so fixed seeds keep the tests deterministic.
Z_999 = 3.2905


class ContractError(AssertionError):
    pass


def _require(cond: bool, msg: str) -> None:
    if not cond:
        raise ContractError(msg)


def _json_ok(obj: Any, what: str) -> None:
    try:
        json.dumps(obj)
    except TypeError as e:
        raise ContractError(f"{what} is not JSON-serialisable: {e}") from None


# --- codes -------------------------------------------------------------------

def gf2_rank(rows: np.ndarray) -> int:
    m = (np.asarray(rows, dtype=np.uint8) & 1).copy()
    rank = 0
    for col in range(m.shape[1] if m.ndim == 2 else 0):
        pivot = next((r for r in range(rank, m.shape[0]) if m[r, col]), None)
        if pivot is None:
            continue
        m[[rank, pivot]] = m[[pivot, rank]]
        for r in range(m.shape[0]):
            if r != rank and m[r, col]:
                m[r] ^= m[rank]
        rank += 1
    return rank


def _indicator(support: tuple[int, ...], n: int) -> np.ndarray:
    v = np.zeros(n, dtype=np.uint8)
    v[list(support)] = 1
    return v


def check_code(code: StabilizerCode) -> None:
    """CSS algebra of a k = 1 code: valid supports, commuting checks, logicals
    that commute with the checks, anticommute with each other, and are not
    themselves stabilizers."""
    _require(isinstance(code, StabilizerCode), "does not implement StabilizerCode")
    _json_ok(code.params(), "params()")
    n = code.n_data
    _require(n > 0 and len(code.checks) > 0, "needs data qubits and checks")

    for i, c in enumerate(code.checks):
        _require(c.pauli in PAULIS, f"check {i}: pauli {c.pauli!r}")
        _require(len(c.support) > 0, f"check {i}: empty support")
        _require(len(set(c.support)) == len(c.support), f"check {i}: repeated qubit")
        _require(all(0 <= q < n for q in c.support), f"check {i}: qubit out of range")
        _require(sorted(c.extraction_order) == sorted(c.support),
                 f"check {i}: extraction order is not a permutation of the support")

    xs, zs = checks_of(code, "X"), checks_of(code, "Z")
    for i, cx in enumerate(xs):
        for j, cz in enumerate(zs):
            _require(len(set(cx.support) & set(cz.support)) % 2 == 0,
                     f"X check {i} and Z check {j} anticommute")

    lx, lz = code.logical("X"), code.logical("Z")
    for p, l in (("X", lx), ("Z", lz)):
        _require(len(l) > 0 and all(0 <= q < n for q in l), f"logical {p}: bad support")
        for j, c in enumerate(checks_of(code, other(p))):
            _require(len(set(l) & set(c.support)) % 2 == 0,
                     f"logical {p} anticommutes with {other(p)} check {j}")
        same = [_indicator(c.support, n) for c in checks_of(code, p)]
        if same:
            base = gf2_rank(np.array(same))
            _require(gf2_rank(np.array(same + [_indicator(l, n)])) > base,
                     f"logical {p} is a product of {p} checks (acts trivially)")
    _require(len(set(lx) & set(lz)) % 2 == 1, "logical X and Z commute (need anticommute)")


# --- noise -------------------------------------------------------------------

def check_phenomenological_noise(noise: PhenomenologicalNoise) -> None:
    _require(isinstance(noise, PhenomenologicalNoise), "does not implement PhenomenologicalNoise")
    _json_ok(noise.params(), "params()")
    _require(noise.data_pauli in PAULIS, f"data_pauli {noise.data_pauli!r}")
    for t in (0.0, 0.5, 3.0):
        for dt in (0.01, 0.5, 2.0):
            r = noise.round_noise(t, dt)
            _require(isinstance(r, RoundNoise), "round_noise must return RoundNoise")
            _require(r == noise.round_noise(t, dt), "round_noise is not deterministic")
    _require(0.0 <= noise.final_read() <= 1.0, "final_read is not a probability")


# --- backends ----------------------------------------------------------------

def wilson(k: int, n: int, z: float = Z_999) -> tuple[float, float]:
    """Wilson score interval for a binomial rate k / n."""
    if n == 0:
        return 0.0, 1.0
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centre - half, centre + half


def first_round_rate(weight: int, noise: RoundNoise) -> float:
    """P(first-round detector fires) for a check of `weight` under phenomenological
    noise: odd number of data flips on its support, XOR one record flip."""
    return 0.5 * (1 - (1 - 2 * noise.p_data) ** weight * (1 - 2 * noise.p_read))


def check_backend(backend: Backend, quiet: MemorySpec, noisy: MemorySpec) -> None:
    """`quiet`: a spec with zero noise. `noisy`: the same experiment with noise
    strong enough that detectors fire (thousands of shots for the rate check)."""
    _require(isinstance(backend, Backend), "does not implement Backend")
    _json_ok(backend.versions(), "versions()")

    rec = run_checked(backend, quiet)
    _require(not rec.detectors.any(), "detection events without noise")
    _require(not rec.observables.any(), "logical readout flipped without noise")

    rec = run_checked(backend, noisy)
    _require(rec.detectors.any(), "no detection events under noise")
    sched = noisy.schedule
    _require(np.allclose(rec.rounds["dt"], sched.dts), "rounds['dt'] differs from the schedule")
    _require(np.allclose(rec.rounds["t"], sched.starts), "rounds['t'] differs from the schedule")

    again = run_checked(backend, noisy)
    _require(np.array_equal(rec.detectors, again.detectors), "same spec, different detectors")
    shifted = run_checked(backend, dataclasses.replace(noisy, seed=noisy.seed + noisy.shots))
    _require(not np.array_equal(rec.detectors, shifted.detectors),
             "different seed, identical detectors: the seed does not reach the noise")

    if isinstance(noisy.noise, PhenomenologicalNoise):
        _check_phenomenological_rates(noisy, rec)


def _check_phenomenological_rates(spec: MemorySpec, rec) -> None:
    rn = spec.noise.round_noise(spec.schedule.starts[0], spec.schedule.dts[0])
    _require(np.allclose(rec.rounds["p_data"][0], rn.p_data)
             and np.allclose(rec.rounds["p_read"][0], rn.p_read),
             "round metadata does not report the noise model's p_data / p_read")
    # Round 0 detectors compare against the ideal initial state, so their rate
    # follows from p_data, p_read and the check weight alone. Pool equal weights.
    checks = checks_of(spec.code, spec.basis)
    first = rec.detectors[:, : len(checks)]
    for w in sorted({len(c.support) for c in checks}):
        cols = [i for i, c in enumerate(checks) if len(c.support) == w]
        k, n = int(first[:, cols].sum()), first[:, cols].size
        lo, hi = wilson(k, n)
        target = first_round_rate(w, rn)
        _require(lo <= target <= hi,
                 f"weight-{w} first-round detector rate {k / n:.5f} "
                 f"(99.9% CI [{lo:.5f}, {hi:.5f}]) excludes the model's {target:.5f}")


# --- decoders ----------------------------------------------------------------

def check_decoder(factory: Callable[..., Decoder], dem: str, shots: int = 16) -> None:
    dec = factory(dem)
    _require(isinstance(dec, Decoder), "factory did not return a Decoder")
    zeros = np.zeros((shots, dec.num_detectors), dtype=bool)
    out = np.asarray(dec.decode_batch(zeros))
    _require(out.shape == (shots, dec.num_observables), f"output shape {out.shape}")
    _require(out.dtype == bool, f"output dtype {out.dtype}, expected bool")
    _require(not out.any(), "predicts a logical flip from no detection events")


# --- idle sources ------------------------------------------------------------

def check_idle_source(source: IdleSource) -> None:
    _require(isinstance(source, IdleSource), "does not implement IdleSource")
    _json_ok(source.params(), "params()")
    for tm in ("uniform", "magic"):
        prof = source.idle_profile(tm)
        _require(prof.time_model == tm, f"profile reports time model {prof.time_model!r}")
        _require(0.0 <= prof.idle_fraction <= 1.0, "idle fraction outside [0, 1]")
