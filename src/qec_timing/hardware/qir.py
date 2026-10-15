"""Memory experiment as QIR for Quantinuum H2 (Nexus / aqora). H2 env ONLY
(guppylang 0.21, hugr-qir 0.1.2; see envs/h2.txt).

The program is built from any `StabilizerCode` through its interface: checks of
the memory basis in their extraction order (hook-safe for the surface code), and
the logical of that basis. Shaped for hugr-qir 0.1.2's limits (original repo,
Stage 7a):
  - the entrypoint is traced (`@guppy.comptime`): every Python loop is unrolled
    into straight-line code; qubits live in a Python list, never a Guppy array;
  - one ancilla, allocated once and reused via project_z + reset;
  - no arguments: distance, rounds, injection and seed are compile-time;
  - outputs with result(): s{round}_{check} (syndrome bit), m{i} (final data
    readout in the memory basis). `hardware.records` turns them into a RawRecord.

Optional noise injection (the stub-to-device path, notebook 11): before
each round's extraction, each data qubit gets the noise's Pauli with
probability p, from ONE RNG seeded base_seed + get_current_shot(). The Bernoulli
is random_int_bounded(2^20) < round(p * 2^20): hugr-qir 0.1.2 cannot lower
RandomFloat. The effective p (quantised by at most 5e-7) is recorded.

QIR validation stays ON. quantinuum_qircheck recurses once per basic block and
every injected flip adds blocks, so conversion runs in a thread with a large
stack and a high recursion limit.
"""

from __future__ import annotations

import importlib.metadata as md
import re
import sys
import threading
import time
from collections import Counter

from qec_timing.codes.base import checks_of
from qec_timing.noise.base import PhenomenologicalNoise
from qec_timing.spec import MemorySpec

BOUND = 1 << 20
H2_STABILIZER_QUBITS = 56          # H2-1E emulator, stabilizer simulator
RECURSION_LIMIT = 1_000_000
THREAD_STACK = 1 << 26             # 64 MiB


def injection_probability(spec: MemorySpec) -> float:
    """Constant per-round data-flip probability to inject (0 for device noise only)."""
    if not isinstance(spec.noise, PhenomenologicalNoise):
        return 0.0
    s = spec.schedule
    ps = {spec.noise.round_noise(t, dt).p_data for t, dt in zip(s.starts, s.dts)}
    if len(ps) != 1:
        raise ValueError("injection is compile-time: one p_data for all rounds")
    return ps.pop()


def build_program(spec: MemorySpec, herald: bool = False):
    """The traced Guppy 0.21 entrypoint for `spec` (no arguments).

    herald=True: every measurement is leakage-aware (`measure_leaked`, LazyMeasureLeaked):
    each recorded value is 0, 1, or 2 = leaked. That measurement is destructive, so each
    check gets a FRESH ancilla instead of reset reuse. Default False keeps the program
    byte-identical to the validated non-heralded build."""
    from guppylang import guppy
    from guppylang.std.builtins import comptime, owned, result
    from guppylang.std.qsystem.random import RNG
    from guppylang.std.qsystem.utils import get_current_shot
    from guppylang.std.quantum import cx, discard, h, measure, project_z, qubit, reset, x, z

    code, basis = spec.code, spec.basis
    orders = [list(c.extraction_order) for c in checks_of(code, basis)]
    n_data, n_rounds, x_basis = code.n_data, spec.schedule.n_rounds, basis == "X"
    p = injection_probability(spec)
    threshold = round(p * BOUND)
    inject = threshold > 0
    pauli = spec.noise.data_pauli
    seed = spec.seed

    if pauli == "Z":
        @guppy
        def maybe_flip(rng: RNG, q: qubit) -> None:
            if rng.random_int_bounded(comptime(BOUND)) < comptime(threshold):
                z(q)
    else:
        @guppy
        def maybe_flip(rng: RNG, q: qubit) -> None:
            if rng.random_int_bounded(comptime(BOUND)) < comptime(threshold):
                x(q)

    if herald:
        from guppylang.std.qsystem import _measure_leaked

        @guppy
        def meas3(q: qubit @ owned) -> int:
            return _measure_leaked(q).read()

    @guppy.comptime
    def main() -> None:
        rng = RNG(seed + get_current_shot())
        data = [qubit() for _ in range(n_data)]
        anc = qubit()
        if x_basis:
            for q in data:
                h(q)
        for r in range(n_rounds):
            if inject:
                for q in data:
                    maybe_flip(rng, q)
            for ci, order in enumerate(orders):
                if x_basis:
                    h(anc)
                    for i in order:
                        cx(anc, data[i])
                    h(anc)
                else:
                    for i in order:
                        cx(data[i], anc)
                if herald:
                    result(f"s{r}_{ci}", meas3(anc))
                    anc = qubit()
                else:
                    result(f"s{r}_{ci}", project_z(anc))
                    reset(anc)
        for i, q in enumerate(data):
            if x_basis:
                h(q)
            if herald:
                result(f"m{i}", meas3(q))
            else:
                result(f"m{i}", measure(q))
        discard(anc)
        rng.discard()

    return main


def _convert(pkg, fmt):
    from hugr_qir.hugr_to_qir import hugr_to_qir

    box = {}

    def work():
        sys.setrecursionlimit(RECURSION_LIMIT)
        try:
            box["out"] = hugr_to_qir(pkg, validate_qir=True, output_format=fmt)
        except BaseException as e:   # noqa: BLE001  re-raised below
            box["err"] = e

    old = threading.stack_size(THREAD_STACK)
    try:
        t = threading.Thread(target=work)
        t.start()
        t.join()
    finally:
        threading.stack_size(old)
    if "err" in box:
        raise box["err"]
    return box["out"]


def build_qir(spec: MemorySpec, herald: bool = False) -> dict:
    """Validated QIR for `spec`: {'bitcode': bytes, 'll': str, 'meta': dict}."""
    from hugr_qir.output import OutputFormat

    n_qubits = spec.code.n_data + 1
    if n_qubits > H2_STABILIZER_QUBITS:
        raise ValueError(f"{n_qubits} qubits exceed H2's {H2_STABILIZER_QUBITS}")
    t0 = time.perf_counter()
    pkg = build_program(spec, herald).compile()
    t_hugr = time.perf_counter() - t0
    t1 = time.perf_counter()
    bc = _convert(pkg, OutputFormat.BITCODE)
    t_qir = time.perf_counter() - t1
    ll = _convert(pkg, OutputFormat.LLVM_IR)
    p = injection_probability(spec)
    meta = {"spec": spec.to_json(), "n_qubits": n_qubits,
            "p_inject": p, "p_inject_effective": round(p * BOUND) / BOUND, "herald": herald,
            "hugr_bytes": len(pkg.to_bytes()), "qir_bitcode_bytes": len(bc),
            "seconds_hugr": t_hugr, "seconds_qir": t_qir,
            "qir_calls": dict(Counter(re.findall(r"call [^@]*@([\w.]+)", ll))),
            "versions": {k: md.version(k) for k in ("guppylang", "hugr", "hugr-qir", "pyqir",
                                                    "quantinuum-qircheck")}}
    return {"bitcode": bc, "ll": ll, "meta": meta}
