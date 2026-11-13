"""Reproduce the H2-1 pilot error rates from a saved provider result."""
import argparse
from collections import Counter
import hashlib
import json
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path

import numpy as np
from analyze_d3_sleep_sweep import unpack
from analyze_single_qubit_pilot import wilson
from build_sleep_probe import SOURCE
from redecode_d3_sleep_dependent import P_EXT, P_READ, round_probabilities
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
from qec_timing.hardware.collect import paper_graph
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.schedule import Schedule
from qec_timing.spec import spec_from_json


def unpack_hardware(raw, shots, n_rounds):
    packed = np.asarray(raw['shots']['array'], dtype=np.uint8)
    bits = np.unpackbits(packed, axis=1)[:, :raw['shots']['width']]
    assert bits.shape == (shots, len(raw['bits']))
    reported = Counter()
    for row in raw['counts_formatted']:
        reported[row['bitstring']] += row['count']
    assert Counter(''.join(map(str, row)) for row in bits) == reported
    expected = {f'm{i}' for i in range(9)} | {f's{r}_{c}' for r in range(n_rounds) for c in range(4)}
    bookkeeping = {'JOB_total_shots', 'JOB_shotnum', 'JOB_chunk_total_shots', 'JOB_chunk_shotnum'}
    columns = {}
    for column, (tag, indices) in enumerate(raw['bits']):
        assert tag in expected | bookkeeping and len(indices) == 1
        if tag in expected:
            if indices == [0]:
                assert tag not in columns
                columns[tag] = column
            else:
                assert not bits[:, column].any(), 'Nonboolean measurement register'
    assert set(columns) == expected
    return [{tag: int(bits[i, column]) for tag, column in columns.items()} for i in range(shots)]

def analyze(raw_path, shots):
    _register_builtins()
    base = spec_from_json(json.loads(SOURCE.with_suffix('.json').read_text())['spec'])
    spec = replace(base, schedule=Schedule.rounds(1.0, 2), shots=shots)
    raw = raw_path.read_bytes()
    payload = json.loads(raw)
    unpacker = unpack_hardware if any(tag.startswith('JOB_') for tag, _ in payload['bits']) else unpack
    syndrome, data = bits_from_shots(unpacker(payload, shots=shots, n_rounds=2), 2, 4, 9)
    records = record_from_bits(spec, syndrome, data)
    assert records.detectors.shape == (shots, 12)
    assert np.array_equal(records.observables[:, 0], np.bitwise_xor.reduce(data[:, [0, 3, 6]], axis=1))
    dem = dem_for(paper_graph(spec, P_EXT, 0, P_READ), noise=round_probabilities(2, 1.0))
    reference = SOURCE.parents[3] / 'SG_final_round/results/decoders/d3_sleep_dependent/n2.dem'
    assert dem == reference.read_text()
    decoded = PyMatchingDecoder(dem).decode_batch(records.detectors)
    failures = int(np.any(decoded != records.observables, axis=1).sum())
    errors = int(data.sum())
    summary = dict(shots=shots, data_bit_errors=errors, data_bits=int(data.size),
                   raw_data_error_probability=errors / data.size,
                   data_bit_errors_by_qubit=data.sum(axis=0).tolist(),
                   raw_logical_parity_flips=int(records.observables.sum()),
                   logical_failures=failures, logical_error_probability=failures / shots,
                   logical_wilson_95=wilson(failures, shots),
                   raw_sha256=hashlib.sha256(raw).hexdigest(),
                   dem_sha256=hashlib.sha256(dem.encode()).hexdigest(),
                   versions={name: version(name) for name in ['numpy', 'stim', 'pymatching']})
    return summary, dem


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--verify', type=Path, help='Analyze a 500-shot historical sample without writing results')
    args = parser.parse_args()
    if args.verify:
        summary, _ = analyze(args.verify, 500)
    else:
        run = Path(__file__).resolve().parent
        job = json.loads((run / 'job.json').read_text())
        assert job['job']['status'] == 'COMPLETED' and not job['job']['error']
        assert job['job']['platform']['name'] == 'H2-1'
        assert hashlib.sha256((run / 'program.bc').read_bytes()).hexdigest() == job['program_sha256']
        assert len(job['results']) == 1 and not job['results'][0]['error']
        result = job['results'][0]
        summary, dem = analyze(run / f"result_{result['index']}.txt", job['shots'])
        assert summary['raw_sha256'] == result['raw_sha256']
        summary.update(job_id=job['job_id'], platform='H2-1', hqc=job['job']['hqcCost'])
        (run / 'decoder.dem').write_text(dem)
        (run / 'analysis.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
