"""Unpack provider result payloads into per-shot {tag: bit} records.

One parametrised implementation of the four copies in the original scripts, each call
site keeping its own strictness:

    emulator (hardware=False)   analyze_d3_sleep_sweep.unpack (d=3), analyze_d5_sleep_results.unpack (d=5):
                                every register must be a single bit; registers at index 0 are
                                outputs and must be exactly the expected tags (so JOB_* bookkeeping
                                outputs are rejected); other registers must be all zero.
    hardware (hardware=True)    unpack_hardware from results/sleep/runs/h2_2_hardware_d3_x_t1_20261111/analyze.py
                                (d=3; that script stays untouched) and from
                                analyze_d5_h2_2_zero_sleep_control.py (d=5): the JOB_* bookkeeping
                                registers are allowed and ignored; every other tag must be expected.

Both check the packed shots against the provider-formatted joint counts.
"""
from collections import Counter

import numpy as np

BOOKKEEPING = {'JOB_total_shots', 'JOB_shotnum', 'JOB_chunk_total_shots', 'JOB_chunk_shotnum'}


def expected_tags(distance, n_rounds):
    n_data = distance * distance
    n_checks = (n_data - 1) // 2
    return {f'm{i}' for i in range(n_data)} | {f's{r}_{c}' for r in range(n_rounds) for c in range(n_checks)}


def unpack(raw, shots, n_rounds, *, distance=3, hardware=False):
    """Per-shot records from a provider payload (see the module docstring for the two modes)."""
    packed = np.asarray(raw['shots']['array'], dtype=np.uint8)
    bits = np.unpackbits(packed, axis=1)[:, :raw['shots']['width']]
    assert bits.shape == (shots, len(raw['bits']))
    expected = expected_tags(distance, n_rounds)
    if not hardware:
        observed = Counter(''.join(map(str, row)) for row in bits)
        reported = Counter()
        for row in raw['counts_formatted']:
            reported[row['bitstring']] += row['count']
        assert observed == reported, 'Packed shots disagree with formatted counts'
        tags = {}
        for column, (tag, indices) in enumerate(raw['bits']):
            assert len(indices) == 1
            if indices[0] == 0:
                assert tag not in tags
                tags[tag] = bits[:, column]
            else:
                assert not bits[:, column].any(), 'Nonboolean register output'
        assert set(tags) == expected
        return [{tag: int(values[i]) for tag, values in tags.items()} for i in range(shots)]
    reported = Counter()
    for row in raw['counts_formatted']:
        reported[row['bitstring']] += row['count']
    assert Counter(''.join(map(str, row)) for row in bits) == reported
    columns = {}
    for column, (tag, indices) in enumerate(raw['bits']):
        assert tag in expected | BOOKKEEPING and len(indices) == 1
        if tag in expected:
            if indices == [0]:
                assert tag not in columns
                columns[tag] = column
            else:
                assert not bits[:, column].any(), 'Nonboolean measurement register'
    assert set(columns) == expected
    return [{tag: int(bits[i, column]) for tag, column in columns.items()} for i in range(shots)]


def unpack_hardware(raw, shots, n_rounds, distance=3):
    """The physical-hardware unpacker (`unpack_hardware` of the original scripts).

    With distance=3 this is the function the original combine/sensitivity scripts exec'd out
    of results/sleep/runs/h2_2_hardware_d3_x_t1_20261111/analyze.py; stage 6 tests that the two agree.
    """
    return unpack(raw, shots, n_rounds, distance=distance, hardware=True)
