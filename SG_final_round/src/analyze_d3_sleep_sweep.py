"""Decode saved emulator shots; never submit jobs or inject faults into data."""
import argparse
import hashlib
import importlib.metadata
import json
from collections import Counter

import numpy as np
import d3_sleep_sweep as sweep
from d3_sleep_sweep import ROOT, SHOTS, accepted
from analyze_single_qubit_pilot import wilson
from build_sleep_probe import SOURCE
from qec_timing.hardware.collect import paper_graph
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
from qec_timing.spec import spec_from_json


def unpack(raw, shots=SHOTS, n_rounds=2):
    """Cross-check packed joint shots against provider-formatted joint counts."""
    packed = np.asarray(raw['shots']['array'], dtype=np.uint8)
    bits = np.unpackbits(packed, axis=1)[:, :raw['shots']['width']]
    assert bits.shape == (shots, len(raw['bits']))
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
    expected = {f'm{i}' for i in range(9)} | {f's{r}_{c}' for r in range(n_rounds) for c in range(4)}
    assert set(tags) == expected
    return [{tag: int(values[i]) for tag, values in tags.items()} for i in range(shots)]


def main(five_point=False, platform='nexus:H2-1E'):
    if five_point:
        sweep.configure_five_point(platform)
    RUNS, BUILD, CONFIG, VARIANTS = sweep.RUNS, sweep.BUILD, sweep.CONFIG, sweep.VARIANTS
    output_name = ('d3_sleep_five_point_' + platform.split(':')[1].lower().replace('-', '_') + '_1000.json'
                   if five_point else 'd3_sleep_sweep_1000.json')
    _register_builtins()
    spec = spec_from_json(json.loads(SOURCE.with_suffix('.json').read_text())['spec'])
    # Freeze the historical d3 decoder across settings; no fitting to returned data.
    decoder_specs = {str(p): dict(p_data=p, p_read=.001, lam=0) for p in [.002, .02, .1]}
    decoders = {}
    for key, params in decoder_specs.items():
        dem = dem_for(paper_graph(spec, params['p_data'], 0, params['p_read']))
        (BUILD/f'decoder_p{key}.dem').write_text(dem)
        params['dem_sha256'] = hashlib.sha256(dem.encode()).hexdigest()
        decoders[key] = PyMatchingDecoder(dem)
    rows = []
    for name, duration in VARIANTS.items():
        folder = RUNS/'execute'/name
        job = json.loads((folder/'job.json').read_text())
        assert accepted(job), f'Job not completed successfully: {name}'
        raw = json.loads((folder/'result_0.txt').read_text())
        syndromes, data = bits_from_shots(unpack(raw), 2, 4, 9)
        rec = record_from_bits(spec, syndromes, data)
        failures = {key: int(np.any(decoder.decode_batch(rec.detectors) != rec.observables, axis=1).sum())
                    for key, decoder in decoders.items()}
        k = failures['0.002']
        rows.append(dict(duration_raw=duration, shots=rec.shots, logical_failures=k,
                         logical_error_rate=k/rec.shots, wilson_95=wilson(k, rec.shots),
                         raw_logical_flips=int(rec.observables.sum()),
                         per_data_qubit_flips=data.sum(axis=0).tolist(),
                         inter_round_syndrome_changes=(syndromes[:, 1] ^ syndromes[:, 0]).sum(axis=0).tolist(),
                         detector_rates=rec.detectors.mean(axis=0).tolist(),
                         decoder_sensitivity_failures=failures, job_id=job['job_id'],
                         result_sha256=hashlib.sha256((folder/'result_0.txt').read_bytes()).hexdigest(),
                         returned_properties=raw.get('properties')))
    comparisons = []
    from scipy.stats import fisher_exact
    for row in rows[1:]:
        comparisons.append(dict(duration_raw=row['duration_raw'],
            difference_vs_zero=row['logical_error_rate']-rows[0]['logical_error_rate'],
            fisher_two_sided_p=float(fisher_exact([[row['logical_failures'], SHOTS-row['logical_failures']],
                 [rows[0]['logical_failures'], SHOTS-rows[0]['logical_failures']]]).pvalue)))
    result = dict(CONFIG, build=str(BUILD.relative_to(ROOT)), rows=rows,
                  primary_decoder='Fixed historical phenomenological MWPM: p_data=.002, p_read=.001, lam=0',
                  decoder_models=decoder_specs, comparisons=comparisons,
                  versions={m: importlib.metadata.version(m) for m in ['numpy', 'stim', 'pymatching']},
                  actual_billed_hqc=None, all_packed_shots_match_formatted_counts=True,
                  logical_observable='X on data qubits 0,3,6; failure after predicted logical correction')
    (ROOT/'results'/output_name).write_text(json.dumps(result, indent=2)+'\n')
    manifest_path = BUILD/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['execution_status'] = 'completed_with_parallel_sleep_unverified'
    manifest['analysis'] = 'results/' + output_name
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
    collection_path = RUNS/'collection_status.json'
    if collection_path.exists():
        collection = json.loads(collection_path.read_text())
        collection['analysis_status'] = 'completed_on_user_request'
        collection['analysis'] = manifest['analysis']
        collection_path.write_text(json.dumps(collection, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--five-point', action='store_true')
    parser.add_argument('--platform', choices=['nexus:H2-1E', 'nexus:H2-2E'], default='nexus:H2-1E')
    args = parser.parse_args()
    if not args.five_point and args.platform != 'nexus:H2-1E':
        parser.error('--platform requires --five-point')
    main(args.five_point, args.platform)
