"""Analyze saved H2-2 X-memory shots with the frozen sleep-dependent DEMs."""
import hashlib
import json
from dataclasses import replace
from collections import Counter
from importlib.metadata import version
from pathlib import Path

import numpy as np
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


RUN = Path(__file__).resolve().parent
_register_builtins()
base = spec_from_json(json.loads(SOURCE.with_suffix('.json').read_text())['spec'])
rows = []
rng = np.random.default_rng(20261112)
for folder in sorted(RUN.glob('n*'), key=lambda p: int(p.name[1:])):
    job = json.loads((folder / 'job.json').read_text())
    n, count, u = job['rounds'], job['shots'], job['delta_t_seconds']
    assert job['job']['status'] == 'COMPLETED' and not job['job']['error']
    assert job['job']['platform']['name'] == 'H2-2'
    assert job['options'] == {'no_opt': True}
    assert abs((n - 1) * u - 1) < 1e-14
    assert hashlib.sha256((folder / 'program.bc').read_bytes()).hexdigest() == job['program_sha256']
    assert len(job['results']) == 1 and not job['results'][0]['error']
    result = job['results'][0]
    rawpath = folder / f"result_{result['index']}.txt"
    raw = rawpath.read_bytes()
    raw_hash = hashlib.sha256(raw).hexdigest()
    assert raw_hash == result['raw_sha256']
    spec = replace(base, schedule=Schedule.rounds(u, n), shots=count)
    syndrome, data = bits_from_shots(unpack_hardware(json.loads(raw), shots=count, n_rounds=n), n, 4, 9)
    records = record_from_bits(spec, syndrome, data)
    assert records.detectors.shape == (count, 4 * (n + 1))
    assert np.array_equal(records.observables[:, 0], np.bitwise_xor.reduce(data[:, [0, 3, 6]], axis=1))
    dem = dem_for(paper_graph(spec, P_EXT, 0, P_READ), noise=round_probabilities(n, u))
    reference = RUN.parents[1] / 'results/decoders/d3_sleep_dependent' / f'n{n}.dem'
    assert dem == reference.read_text(), 'Frozen DEM differs from historical reference'
    decoder = PyMatchingDecoder(dem)
    testdata = np.zeros((2, 9), dtype=bool)
    testdata[1, list(base.code.logical('Z'))] = True
    testrecords = record_from_bits(spec, np.zeros((2, n, 4), dtype=bool), testdata)
    assert not testrecords.detectors.any()
    assert testrecords.observables[:, 0].tolist() == [False, True]
    assert not decoder.decode_batch(testrecords.detectors).any()
    prediction = decoder.decode_batch(records.detectors)
    fail = np.any(prediction != records.observables, axis=1)
    k = int(fail.sum())
    errors = int(data.sum())
    # Resample complete shots to retain correlations among the nine data bits.
    histogram = np.bincount(data.sum(axis=1).astype(int), minlength=10)
    draws = rng.multinomial(count, histogram / count, size=10000)
    bootstrap = draws @ np.arange(10) / (count * 9)
    row = dict(rounds=n, interval_seconds=u, shots=count, job_id=job['job_id'],
               provider_id=job['job'].get('providerId'), hqc=job['job']['hqcCost'],
               data_bit_errors=errors, data_bits=int(data.size),
               raw_data_error_probability=errors / data.size,
               raw_data_shot_bootstrap_95=np.quantile(bootstrap, [.025, .975]).tolist(),
               per_qubit_error_counts=data.sum(axis=0).tolist(),
               per_qubit_error_probabilities=data.mean(axis=0).tolist(),
               raw_logical_parity_flips=int(records.observables.sum()),
               raw_logical_parity_probability=float(records.observables.mean()),
               logical_failures=k, logical_error_probability=k/count,
               logical_wilson_95=wilson(k, count), raw_sha256=raw_hash,
               dem_sha256=hashlib.sha256(dem.encode()).hexdigest())
    (folder / 'decoder.dem').write_text(dem)
    (folder / 'analysis.json').write_text(json.dumps(row, indent=2) + '\n')
    rows.append(row)
summary = dict(platform='nexus:H2-2', distance=3, basis='X', total_requested_sleep_seconds=1,
               total_shots=sum(r['shots'] for r in rows), hqc=sum(r['hqc'] for r in rows),
               decoder='Frozen sleep-dependent phenomenological MWPM',
               decoder_parameters=job['decoder'], no_postselection=True,
               raw_error_definition='Fraction of final X-readout data bits equal to one, pooled over nine data qubits',
               versions={name: version(name) for name in ['numpy', 'stim', 'pymatching']}, rows=rows)
(RUN / 'analysis.json').write_text(json.dumps(summary, indent=2) + '\n')
for row in rows:
    print(json.dumps(row), flush=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
fig, axes = plt.subplots(1, 2, figsize=(10, 4.1), layout='constrained')
ordered = sorted(rows, key=lambda r: r['interval_seconds'])
x = np.array([r['interval_seconds'] for r in ordered])
for ax, field, ci, title, color in [
    (axes[0], 'raw_data_error_probability', 'raw_data_shot_bootstrap_95', 'Raw data-qubit errors', '#176baf'),
    (axes[1], 'logical_error_probability', 'logical_wilson_95', 'Decoded logical errors', '#b64e18'),
]:
    y = np.array([r[field] for r in ordered])
    bounds = np.array([r[ci] for r in ordered])
    ax.errorbar(x, y, yerr=np.maximum(np.array([y-bounds[:, 0], bounds[:, 1]-y]), 0),
                fmt='o', mfc='none', color=color, capsize=3, markersize=5)
    ax.set_xscale('log')
    ax.set_xticks(x, [f'{v:.3g}' for v in x], rotation=35)
    ax.set_xlabel('Requested sleep interval Δt (s)')
    ax.set_ylabel('Error probability')
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_ylim(bottom=0)
    ax.set_title(title)
    ax.grid(axis='y', alpha=.2)
    ax.spines[['top', 'right']].set_visible(False)
fig.suptitle('Physical H2-2 · d=3 X-memory · total requested sleep 1 s\n3,150 shots · frozen sleep-dependent MWPM · 95% intervals', fontsize=12)
fig.savefig(RUN / 'error_probabilities.png', dpi=170)
