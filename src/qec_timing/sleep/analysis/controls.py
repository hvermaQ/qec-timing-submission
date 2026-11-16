"""Control experiments: single-qubit X memory and the zero-sleep d=5 H2-2 controls.

Ported from SG_final_round/src/ (calculations verbatim; only paths and writes changed):

    single_qubit_pilot()          analyze_single_qubit_pilot.py      (no decoder: raw counts)
    single_qubit_sweep()          single_qubit_sweep.py `analyze`    (no decoder: raw counts;
                                  taken from git history, commit 4b4b92d)
    d5_zero_sleep(raw, shots)     analyze_d5_h2_2_zero_sleep_control.py `analyze`   HISTORICAL
    d5_zero_sleep_control(verify) analyze_d5_h2_2_zero_sleep_control.py `main`      HISTORICAL
    d5_zero_sleep_n3(mapping)     analyze_d5_h2_2_zero_sleep_n3.py ('original') and
                                  analyze_d5_h2_2_zero_sleep_n3_skip5.py ('skip5')  (no decoder)

Per-run outputs the originals wrote into results/sleep/runs/ go to the store/sleep/ mirror.
"""
import hashlib
import json
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path

import numpy as np

from .. import paths
from ..builders import single_qubit
from ..decoder import POLICY, P_EXT, P_READ, round_probabilities
from ..jobs import accepted
from ..stats import wilson
from ..unpack import unpack
from .emulator_d3 import base_spec, qec

SOURCE = paths.BASELINE_D5


# --------------------------------------------------------------------------- single qubit

def single_qubit_pilot():
    """Summarize returned Aqora pilot counts without decoding syntax placeholders.

    -> results/sleep/single_qubit_pilot_counts.json
    """
    base=paths.RUNS/'single_qubit_2c64d96fea4bbbac/execute'
    rows=[]
    for name,duration in single_qubit.PILOT_VARIANTS.items():
        folder=base/name
        job=json.loads(paths.read_text(folder/'job.json'))
        row=dict(variant=name,duration_raw=duration,job_id=job['job_id'],status=job.get('job',{}).get('status'),error=job.get('error'))
        if row['status']=='COMPLETED' and not any(r.get('error') for r in job.get('results',[])):
            raw=json.loads(paths.read_text(folder/'result_0.txt'))
            assert all(b[0]=='m0' for b in raw['bits'])
            counts=raw['counts_formatted']
            assert all(int(c['bitstring'],2) in [0,1] for c in counts)
            n=sum(c['count'] for c in counts)
            k=sum(c['count'] for c in counts if int(c['bitstring'],2)==1)
            assert n==200
            # Independently cross-check packed shot records against formatted counts.
            packed=raw['shots']['array']
            assert len(packed)==n
            assert sum(any(byte != 0 for byte in shot) for shot in packed)==k
            row.update(shots=n,errors=k,error_rate=k/n,wilson_95=wilson(k,n))
        rows.append(row)
    data=dict(experiment='standalone_X_memory',platform='nexus:H2-1E',virtual_qubit=0,physical_ion='backend assigned',duration_unit='unverified',rows=rows)
    paths.write_json(paths.RESULTS/'single_qubit_pilot_counts.json', data)
    print(json.dumps(data,indent=2))
    return data


def single_qubit_sweep():
    """Counts of the 5-point 1,000-shot single-qubit sleep sweep (the original `analyze` action).

    -> results/sleep/single_qubit_sweep_1000.json
    """
    build=single_qubit.sweep()
    RUNS=build.runs;SHOTS=single_qubit.SHOTS;CONFIG=build.config
    rows=[]
    for name,t in build.extra['variants'].items():
        dest=RUNS/'execute'/name
        job=json.loads(paths.read_text(dest/'job.json'))
        assert accepted(job), f'Incomplete: {name}'
        raw=json.loads(paths.read_text(dest/'result_0.txt'))
        assert all(b[0]=='m0' for b in raw['bits'])
        counts=raw['counts_formatted']
        assert all(int(c['bitstring'],2) in [0,1] for c in counts)
        n=sum(c['count'] for c in counts)
        k=sum(c['count'] for c in counts if int(c['bitstring'],2)==1)
        assert n==SHOTS==len(raw['shots']['array'])
        assert sum(any(b for b in shot) for shot in raw['shots']['array'])==k
        rows.append(dict(duration_raw=t,shots=n,errors=k,error_rate=k/n,wilson_95=wilson(k,n),job_id=job['job_id']))
    # `build` stays relative to the original SG_final_round root, as in the committed result.
    data=dict(CONFIG,build='programs/'+build.name,rows=rows,estimated_hqc=37.0,actual_billed_hqc=None)
    paths.write_json(paths.RESULTS/'single_qubit_sweep_1000.json', data)
    print(json.dumps(data,indent=2))
    return data


# --------------------------------------------------------------------------- d=5 zero-sleep controls (H2-2)

def d5_zero_sleep(raw_path, shots):
    """HISTORICAL. Decode one d=5 N=2 zero-sleep result; returns (summary, dem). Writes nothing.

    Decoder: the d=3 physical H2-2 policy h2_2_p_ext_0_00117_20261112 (p_ext=0.00117,
    p_read=0.001) applied to d=5, before a d=5 policy existed. Raw-error p_ext estimates
    with a whole-shot bootstrap. Emulator payloads (no JOB_* registers) use the strict
    emulator unpacker, hardware payloads the hardware one.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    _register_builtins()
    base = base_spec(spec_from_json, SOURCE)
    # Schedule requires positive ticks; this labels two rounds only.
    # All DEM noise below explicitly uses u=0; no schedule-derived idle noise.
    spec = replace(base, schedule=Schedule.rounds(1.0, 2), shots=shots)
    raw = Path(raw_path).read_bytes()
    payload = json.loads(raw)
    hardware = any(tag.startswith('JOB_') for tag, _ in payload['bits'])
    syndrome, data = bits_from_shots(unpack(payload, shots, 2, distance=5, hardware=hardware), 2, 12, 25)
    records = record_from_bits(spec, syndrome, data)
    assert records.detectors.shape == (shots, 36)
    assert np.array_equal(records.observables[:, 0], np.bitwise_xor.reduce(data[:, [0, 5, 10, 15, 20]], axis=1))
    dem = dem_for(paper_graph(spec, P_EXT, 0, P_READ), noise=round_probabilities(2, 0.0))
    assert round_probabilities(2, 0.0)[-1].p_data == P_EXT
    decoded = PyMatchingDecoder(dem).decode_batch(records.detectors)
    failures = int(np.any(decoded != records.observables, axis=1).sum())
    errors = int(data.sum())
    summary = dict(shots=shots, rounds=2, delta_t_seconds=0.0, data_bit_errors=errors, data_bits=int(data.size),
                   raw_data_error_probability=errors / data.size,
                   data_bit_errors_by_qubit=data.sum(axis=0).tolist(),
                   raw_logical_parity_flips=int(records.observables.sum()),
                   logical_failures=failures, logical_error_probability=failures / shots,
                   logical_wilson_95=wilson(failures, shots),
                   raw_sha256=hashlib.sha256(raw).hexdigest(),
                   dem_sha256=hashlib.sha256(dem.encode()).hexdigest(),
                   decoder_policy=POLICY, distance=5,
                   versions={name: version(name) for name in ['numpy', 'stim', 'pymatching']})
    # Whole-shot resampling preserves correlations between the 25 data bits.
    histogram = np.bincount(data.sum(axis=1).astype(int), minlength=26)
    rng = np.random.default_rng(20261113)
    draws = rng.multinomial(shots, histogram / shots, size=20000)
    qs = draws @ np.arange(26) / (shots * 25)
    q = errors / data.size
    def extraction(q, boundary=0.0):
        return (1 - np.sqrt(np.clip((1-2*q)/(1-2*boundary), 0, 1))) / 2
    summary['raw_data_shot_bootstrap_95'] = np.quantile(qs, [.025, .975]).tolist()
    summary['p_ext_effective_zero_boundary'] = float(extraction(q))
    summary['p_ext_effective_zero_boundary_bootstrap_95'] = np.quantile(extraction(qs), [.025,.975]).tolist()
    summary['p_ext_effective_assuming_final_readout_0_001'] = float(extraction(q, .001))
    summary['p_ext_by_qubit_zero_boundary'] = extraction(data.mean(axis=0)).tolist()
    summary['syndrome_one_counts_by_round_check'] = syndrome.sum(axis=0).tolist()
    summary['syndrome_change_counts_by_check'] = np.logical_xor(syndrome[:,0,:],syndrome[:,1,:]).sum(axis=0).tolist()
    summary['estimation_assumptions'] = 'Two equal independent extraction flip channels, no added sleep. Zero-boundary estimate attributes all raw error to extraction; preparation/readout and circuit correlations are not separately calibrated. Bootstrap resamples complete shots.'
    return summary, dem


def d5_zero_sleep_control(verify=None):
    """HISTORICAL. The d=5 N=2 zero-sleep H2-2 control (500 shots), or `verify` a 500-shot sample.

    Decoder: the d=3 policy h2_2_p_ext_0_00117_20261112 applied to d=5 (see d5_zero_sleep).
    -> store/sleep/runs/d5_h2_2_zero_sleep_n2_500_20261113/execute/{analysis.json,decoder.dem}
    (the committed copies stay in results/sleep/runs/). With `verify`, writes nothing.
    """
    if verify:
        summary, _ = d5_zero_sleep(verify, 500)
    else:
        run = paths.RUNS / 'd5_h2_2_zero_sleep_n2_500_20261113/execute'
        job = json.loads(paths.read_text(run / 'job.json'))
        assert job['job']['status'] == 'COMPLETED' and not job['job']['error']
        assert job['job']['platform']['name'] == 'H2-2'
        assert hashlib.sha256(paths.resolve_recorded(job['program']).read_bytes()).hexdigest() == job['program_sha256']
        assert len(job['results']) == 1 and not job['results'][0]['error']
        result = job['results'][0]
        summary, dem = d5_zero_sleep(run / f"result_{result['index']}.txt", job['shots'])
        assert summary['raw_sha256'] == result['raw_sha256']
        summary.update(job_id=job['job_id'], platform='H2-2', hqc=job['job'].get('hqcCost'))
        paths.write_text(paths.store(run / 'decoder.dem'), dem)
        paths.write_json(paths.store(run / 'analysis.json'), summary)
    print(json.dumps(summary, indent=2))
    return summary


N3_RUNS = {'original': 'd5_h2_2_zero_sleep_n3_250_20261114', 'skip5': 'd5_h2_2_zero_sleep_n3_skip5_250_20261114'}


def d5_zero_sleep_n3(mapping='original'):
    """Raw N=3 zero-sleep d=5 H2-2 control (250 shots); extraction estimate uses three channels.

    No decoder: a raw-data calibration diagnostic, not a decoder-policy update. The two
    mappings are separate runs and are never pooled. 'original' compares with the pooled N=2
    control (results/sleep/d5_h2_2_zero_sleep_pooled_750.json); 'skip5' compares with the
    committed original-mapping N=3 analysis and records the qubit mapping.
    Loads circuit_audit/all_stabilizer_syndrome_comparison.json, as the originals did, without using it.
    -> store/sleep/runs/<run>/execute/raw_analysis.json (the committed copy stays in results/sleep/runs/).
    """
    from qec_timing.hardware.records import bits_from_shots
    run=paths.RUNS/N3_RUNS[mapping]/'execute'
    j=json.loads(paths.read_text(run/'job.json'));assert j['job']['status']=='COMPLETED' and not j['job'].get('error');assert len(j['results'])==1
    r=j['results'][0];assert not r['error'];raw=(run/f"result_{r['index']}.txt").read_bytes();assert hashlib.sha256(raw).hexdigest()==r['raw_sha256']
    assert hashlib.sha256(paths.resolve_recorded(j['program']).read_bytes()).hexdigest()==j['program_sha256']
    syn,data=bits_from_shots(unpack(json.loads(raw),250,3,distance=5,hardware=True),3,12,25)
    counts=data.sum(axis=0);q=float(data.mean());ext=lambda q:(1-np.power(1-2*q,1/3))/2
    assert abs((1-(1-2*ext(q))**3)/2-q)<1e-14
    rng=np.random.default_rng(20261114);hist=np.bincount(data.sum(axis=1).astype(int),minlength=26);qs=rng.multinomial(250,hist/250,size=20000)@np.arange(26)/6250
    if mapping=='original':
        previous=json.loads(paths.read_text(paths.RESULTS/'d5_h2_2_zero_sleep_pooled_750.json'))
    else:
        previous=json.loads(paths.read_text(paths.RUNS/N3_RUNS['original']/'execute/raw_analysis.json'))
    finite=json.loads(paths.read_text(paths.RESULTS/'circuit_audit/all_stabilizer_syndrome_comparison.json'))
    prev=np.concatenate([np.zeros_like(syn[:,:1]),syn[:,:-1]],axis=1)
    out=dict(job_id=j['job_id'],platform=j['platform'],distance=5,rounds=3,shots=250,interval_seconds=0,raw_sha256=r['raw_sha256'],program_sha256=j['program_sha256'],data_bit_errors=int(data.sum()),data_bits=6250,raw_error_probability=q,raw_shot_bootstrap_95=np.quantile(qs,[.025,.975]).tolist(),p_ext_effective_zero_boundary=float(ext(q)),p_ext_effective_bootstrap_95=np.quantile(ext(qs),[.025,.975]).tolist(),per_qubit_error_counts=counts.tolist(),syndrome_one_counts_by_round_check=syn.sum(axis=0).tolist(),detection_event_counts_by_round_check=(syn^prev).sum(axis=0).tolist())
    if mapping=='original':
        out.update(previous_N2_raw=previous['raw_data_error_probability'],previous_N2_p_ext=previous['p_ext_effective_zero_boundary'])
    else:
        out.update(previous_N3_raw=previous['raw_error_probability'],previous_N3_p_ext=previous['p_ext_effective_zero_boundary'],qubit_mapping=j['qubit_mapping'])
    out['assumptions']='Three equal independent extraction flip channels, no added sleep; preparation/readout absorbed into effective baseline. Whole-shot bootstrap only; excludes drift and model uncertainty. No postselection or exclusion of qubits. This is a raw-data calibration diagnostic, not a decoder-policy update.'
    paths.write_json(paths.store(run/'raw_analysis.json'), out)
    print(json.dumps(out,indent=2))
    return out
