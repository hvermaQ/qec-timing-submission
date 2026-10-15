"""A Stim model of the HARDWARE memory program (`hardware.qir.build_program`), gate for gate.

The hardware program differs from the textbook memory circuit: ONE ancilla is reused for
every check (measure, reset), checks run one after another in their extraction order,
and the injected data error p_data(dt) is applied to every data qubit before each round.
This module rebuilds that program in Stim with circuit-level noise at a device's rates,
so its detector error model can (1) decode shots returned by an emulator or device with
the right edge weights, hooks included, and (2) predict p_L for that device.

Noise placed (all optional, rates from a data sheet or emulator page):
    p1      DEPOLARIZE1 after each single-qubit gate (H here; the native decomposition
            has more single-qubit gates at the same small rate, not modelled one by one)
    p2      DEPOLARIZE2 after each CX (one native ZZ each)
    p_meas  record flip before each measurement (ancilla and final data readout)
    p_init  X flip after each reset / preparation
    p_read  extra record flip on every recorded bit (the paper's b_read p, which the
            hardware analysis adds offline); composed with p_meas
Not modelled: idle dephasing in real time (the round's duration on the device is
unknown), leakage, crosstalk. Detectors and observable follow `records.record_from_bits`
exactly, so a returned shot's detection events decode against this model's DEM.
"""

from __future__ import annotations

import stim

from qec_timing.codes.base import checks_of
from qec_timing.extract.edges import xor
from qec_timing.hardware.qir import injection_probability
from qec_timing.spec import MemorySpec


def program_circuit(spec: MemorySpec, p1: float = 0.0, p2: float = 0.0, p_meas: float = 0.0,
                    p_init: float = 0.0, p_read: float = 0.0) -> stim.Circuit:
    code, basis = spec.code, spec.basis
    if basis != "X":
        raise ValueError("written for the X-basis memory the hardware runs use")
    checks = checks_of(code, basis)
    n, R, C = code.n_data, spec.schedule.n_rounds, len(checks)
    anc = n
    p_data = injection_probability(spec)
    q_read = float(xor(p_meas, p_read))
    c = stim.Circuit()
    c.append("R", range(n + 1))
    if p_init:
        c.append("X_ERROR", range(n + 1), p_init)
    c.append("H", range(n))
    if p1:
        c.append("DEPOLARIZE1", range(n), p1)
    for r in range(R):
        if p_data:
            c.append("Z_ERROR", range(n), p_data)
        for ch in checks:
            c.append("H", [anc])
            if p1:
                c.append("DEPOLARIZE1", [anc], p1)
            for i in ch.extraction_order:
                c.append("CX", [anc, i])
                if p2:
                    c.append("DEPOLARIZE2", [anc, i], p2)
            c.append("H", [anc])
            if p1:
                c.append("DEPOLARIZE1", [anc], p1)
            if q_read:
                c.append("X_ERROR", [anc], q_read)
            c.append("M", [anc])
            c.append("R", [anc])
            if p_init:
                c.append("X_ERROR", [anc], p_init)
    c.append("H", range(n))
    if p1:
        c.append("DEPOLARIZE1", range(n), p1)
    if q_read:
        c.append("X_ERROR", range(n), q_read)
    c.append("M", range(n))
    # Detectors in record_from_bits order: round r, check k (r = 0 against the ideal 0),
    # then the final block (data parity of each check against the last syndrome).
    n_meas = R * C + n
    syn = lambda r, k: stim.target_rec(r * C + k - n_meas)          # noqa: E731
    dat = lambda i: stim.target_rec(R * C + i - n_meas)             # noqa: E731
    for r in range(R):
        for k in range(C):
            c.append("DETECTOR", [syn(r, k)] + ([syn(r - 1, k)] if r else []))
    for k, ch in enumerate(checks):
        c.append("DETECTOR", [dat(i) for i in ch.support] + [syn(R - 1, k)])
    c.append("OBSERVABLE_INCLUDE", [dat(i) for i in code.logical(basis)], 0)
    return c
