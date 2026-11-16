"""Physical H2-2 d=5 X-memory, T=1 s: decode the saved hardware shots; never submit.

Ported from SG_final_round/src/ (calculations verbatim; only paths and writes changed):

    t1_original()          analyze_d5_h2_2_t1_20261113.py   ORIGINAL mapping, policy h2_2_d5_decoder.json (p_ext .004)
    t1_skip5(n)            analyze_d5_h2_2_t1_skip5.py      SKIP-INDEX-5 mapping, p_ext .005 (policy.update in code)
    p_read_sensitivity()   d5_h2_2_p_read_sensitivity.py    ORIGINAL mapping only

The two d=5 mappings are separate experiments and are never pooled (/AGENTS.md).
"""
import hashlib
import json
from dataclasses import replace
from importlib.metadata import version

import numpy as np

from .. import paths
from ..decoder import POLICY as D3_POLICY, load_policy, round_probabilities
from ..stats import wilson
from ..unpack import unpack_hardware
from .emulator_d3 import base_spec, qec

SOURCE = paths.BASELINE_D5
ORIGINAL_RUN = 'd5_h2_2_t1_20261113'
ORIGINAL_SETTINGS = [(2,500),(3,750),(4,1000),(6,750),(10,500)]
SKIP5_CALIBRATION_RUN = 'd5_h2_2_zero_sleep_n3_skip5_250_20261114'


def t1_original():
    """The five physical H2-2 d=5 T=1 s jobs (3,500 shots), ORIGINAL qubit mapping.

    Decoder: policy h2_2_d5_p_ext_0_004_20261113 (config/sleep/decoders/h2_2_d5_decoder.json:
    p_ext=0.004, p_read=0.001); asserts each job's stored policy equals that file.
    -> results/sleep/d5_h2_2_t1_p_ext_0_004_3500_shots.{json,npz,md},
    results/sleep/decoders/h2_2_d5_p_ext_0_004_20261113/.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    RUN=paths.RUNS/ORIGINAL_RUN
    OUT=paths.RESULTS/'d5_h2_2_t1_p_ext_0_004_3500_shots'
    _register_builtins()
    policy=load_policy('d5')
    assert policy['distance']==5 and policy['p_ext']==.004
    # Explicit policy must not change historical/default d=3 probabilities.
    assert round_probabilities(2,0)[0].p_data==D3_POLICY['p_ext']==.00117
    assert all(v.p_data==.004 for v in round_probabilities(2,0,policy=policy))
    base=base_spec(spec_from_json,SOURCE)
    assert base.code.n_data==25 and base.basis=='X'
    demdir=paths.RESULTS/'decoders'/policy['policy_version']
    rows=[];arrays={};seen=set()
    for n,count in ORIGINAL_SETTINGS:
        path=RUN/'execute'/f'n{n}'/'job.json';job=json.loads(paths.read_text(path));u=job['delta_t_seconds']
        assert job['platform']=='nexus:H2-2' and job['options']=={'no_opt':True}
        assert job['job']['status']=='COMPLETED' and not job['job'].get('error')
        assert job['decoder_policy']==policy and job['shots']==count and job['rounds']==n
        assert job['total_requested_sleep_seconds']==1 and abs(u*(n-1)-1)<1e-12
        assert not job['artificial_faults'] and job['job_id'] not in seen;seen.add(job['job_id'])
        assert hashlib.sha256(paths.resolve_recorded(job['program']).read_bytes()).hexdigest()==job['program_sha256']
        assert len(job['results'])==1 and not job['results'][0]['error']
        result=job['results'][0];rawpath=path.parent/f"result_{result['index']}.txt";raw=rawpath.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==result['raw_sha256']
        syn,data=bits_from_shots(unpack_hardware(json.loads(raw),count,n,distance=5),n,12,25)
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=count)
        rec=record_from_bits(spec,syn,data)
        assert rec.detectors.shape==(count,12*(n+1))
        assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(data[:,[0,5,10,15,20]],axis=1))
        noise=round_probabilities(n,u,policy=policy)
        assert len(noise)==n and noise[0].p_data==.004
        dem=dem_for(paper_graph(spec,policy['p_ext'],0,policy['p_read']),noise=noise)
        dempath=demdir/f'T1_n{n}.dem'
        if dempath.exists():assert paths.read_text(dempath)==dem
        paths.write_text(dempath, dem);decoder=PyMatchingDecoder(dem)
        # Check ideal and logical-string records before decoding hardware shots.
        testdata=np.zeros((2,25),dtype=bool);testdata[1,list(base.code.logical('Z'))]=True
        testrec=record_from_bits(spec,np.zeros((2,n,12),dtype=bool),testdata)
        assert not testrec.detectors.any() and testrec.observables[:,0].tolist()==[False,True]
        assert not decoder.decode_batch(testrec.detectors).any()
        pred=decoder.decode_batch(rec.detectors);fail=np.any(pred!=rec.observables,axis=1);k=int(fail.sum())
        row=dict(rounds=n,interval_seconds=u,shots=count,logical_failures=k,logical_error_probability=k/count,logical_wilson_95=wilson(k,count),raw_data_bit_errors=int(data.sum()),data_bits=int(data.size),raw_data_error_probability=float(data.mean()),data_bit_errors_by_qubit=data.sum(axis=0).tolist(),job_id=job['job_id'],hqc=job['job'].get('hqcCost'),job_record=str(path),raw_path=str(rawpath),raw_sha256=result['raw_sha256'],program_sha256=job['program_sha256'],dem_path=str(dempath),dem_sha256=hashlib.sha256(dem.encode()).hexdigest(),round_data_probabilities=[v.p_data for v in noise])
        rows.append(row)
        for key,value in dict(data=data,syndrome=syn,detectors=rec.detectors,observable=rec.observables,prediction=pred,failure=fail).items():arrays[f'n{n}_{key}']=value
    assert len(seen)==5 and sum(r['shots'] for r in rows)==3500
    out=dict(platform='nexus:H2-2',distance=5,basis='X',total_requested_sleep_seconds=1,shots=3500,decoder_policy=policy,no_postselection=True,rows=rows,versions={x:version(x) for x in ['numpy','stim','pymatching']},uncertainty='95% Wilson intervals for logical shot probabilities, conditional on the frozen decoder; excludes calibration/drift/model uncertainty. All 25 data qubits included, including qubit 7.')
    paths.write_json(OUT.with_suffix('.json'), out);paths.save_npz(OUT.with_suffix('.npz'),**arrays)
    lines=['# Physical H2-2 d=5 T=1 s logical errors','',f"Frozen policy: {policy['policy_version']}; p_ext=0.004, p_read=0.001. All 25 data qubits included; no postselection.",'','| N | Interval (s) | Logical failures / shots | Logical error | 95% Wilson | Raw data error |','|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lo,hi=r['logical_wilson_95'];lines.append(f"| {r['rounds']} | {r['interval_seconds']:.6g} | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% | {100*r['raw_data_error_probability']:.3f}% |")
    lines+=['','Intervals reflect shot sampling under the fixed decoder. These observations alone do not establish a unique optimum.']
    paths.write_text(OUT.with_suffix('.md'), '\n'.join(lines)+'\n')
    print('\n'.join(lines),flush=True)
    return out


def skip5_run(n):
    """The committed run folder of the skip-index-5 T=1 s job with N=n rounds."""
    batch='d5_h2_2_t1_skip5_n2_n6_20261114' if n in [2,6] else 'd5_h2_2_t1_skip5_20261114'
    return (paths.RUNS/'d5_h2_2_t1_skip5_n10_20261115/shots160/n10') if n==10 else paths.RUNS/f'{batch}/execute/n{n}'


def t1_skip5(n):
    """One completed SKIP-INDEX-5 T=1 s job (N=2,3,4,6: 500 shots; N=10: 160 of 250 completed).

    Decoder: config/sleep/decoders/h2_2_d5_skip5_decoder.json with fields overridden in code
    exactly as the original did (p_ext=0.005, policy_version h2_2_d5_skip5_p_ext_0_005_20261114,
    the N=3 skip-5 zero-sleep calibration). The N=3,4 job records the original-mapping policy
    (p_ext .004): that is how it was submitted; analysis uses .005.
    -> store/sleep/<run>/analysis_p_ext_0_005.{json,npz}, decoder_p_ext_0_005.dem (the committed
    copies stay in results/sleep/runs/).
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    assert n in [2,3,4,6,10]
    run=skip5_run(n)
    job=json.loads(paths.read_text(run/'job.json'))
    assert job['job']['status']=='COMPLETED' and not job['job'].get('error')
    assert job['platform']=='nexus:H2-2' and job['rounds']==n and job['shots']==(160 if n==10 else 500)
    shots=job['shots']
    assert job['qubit_mapping']['unused_index']==5
    assert hashlib.sha256(paths.resolve_recorded(job['program']).read_bytes()).hexdigest()==job['program_sha256']
    assert len(job['results'])==1 and not job['results'][0]['error']
    result=job['results'][0];rawpath=run/f"result_{result['index']}.txt";raw=rawpath.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==result['raw_sha256']
    policy=load_policy('d5_skip5')
    policy.update(p_ext=.005,policy_version='h2_2_d5_skip5_p_ext_0_005_20261114',selection='User-requested p_ext=0.005 for skip-index-5 finite-sleep decoding',calibration_job_ids=['AFByb3ZpZGVySm9iAaHZaESAcwCVLDEccgwFew'],calibration_result=str(paths.RUNS/SKIP5_CALIBRATION_RUN/'execute/raw_analysis.json'))
    _register_builtins();base=base_spec(spec_from_json,SOURCE)
    u=job['delta_t_seconds'];assert abs(u*(n-1)-1)<1e-12
    spec=replace(base,schedule=Schedule.rounds(u,n),shots=shots)
    syn,data=bits_from_shots(unpack_hardware(json.loads(raw),shots,n,distance=5),n,12,25)
    rec=record_from_bits(spec,syn,data)
    assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(data[:,[0,5,10,15,20]],axis=1))
    dem=dem_for(paper_graph(spec,.005,0,policy['p_read']),noise=round_probabilities(n,u,policy=policy))
    pred=PyMatchingDecoder(dem).decode_batch(rec.detectors);fail=np.any(pred!=rec.observables,axis=1);k=int(fail.sum())
    stem=paths.store(run/'analysis_p_ext_0_005');dempath=paths.store(run/'decoder_p_ext_0_005.dem');paths.write_text(dempath, dem)
    out=dict(platform=job['platform'],distance=5,rounds=n,shots=shots,interval_seconds=u,total_requested_sleep_seconds=1,job_id=job['job_id'],qubit_mapping=job['qubit_mapping'],decoder_policy=policy,logical_failures=k,logical_error_probability=k/shots,logical_wilson_95=wilson(k,shots),data_bit_errors=int(data.sum()),data_bits=int(data.size),raw_data_error_probability=float(data.mean()),data_bit_errors_by_qubit=data.sum(axis=0).tolist(),syndrome_one_counts_by_round_check=syn.sum(axis=0).tolist(),raw_sha256=result['raw_sha256'],program_sha256=job['program_sha256'],dem_sha256=hashlib.sha256(dem.encode()).hexdigest(),dem_path=str(dempath),no_postselection=True)
    paths.write_json(stem.with_suffix('.json'), out)
    paths.save_npz(stem.with_suffix('.npz'),syndrome=syn,data=data,detectors=rec.detectors,observable=rec.observables,prediction=pred,failure=fail)
    print(json.dumps(out,indent=2))
    return out


def p_read_sensitivity():
    """Offline p_read sensitivity on the five ORIGINAL-mapping H2-2 d=5 jobs (3,500 shots).

    Decoder: policy h2_2_d5_decoder.json (p_ext=0.004) with p_read varied jointly for syndrome
    and final readout over 7 values; p_read=0.001 must reproduce t1_original exactly. Re-opens
    the recorded `raw_path`/`dem_path` via `paths.resolve_recorded`.
    -> results/sleep/d5_h2_2_p_read_sensitivity.{json,npz,md}, results/sleep/decoders/d5_h2_2_p_read_sensitivity/.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    SOURCE_=paths.RESULTS/'d5_h2_2_t1_p_ext_0_004_3500_shots'
    OUT=paths.RESULTS/'d5_h2_2_p_read_sensitivity'
    VALUES=[.0001,.00025,.0005,.001,.002,.004,.01]
    _register_builtins()
    baseline=json.loads(paths.read_text(SOURCE_.with_suffix('.json')));saved=np.load(SOURCE_.with_suffix('.npz'))
    policy=load_policy('d5')
    assert baseline['decoder_policy']==policy and policy['p_ext']==.004 and policy['p_read']==.001
    base=base_spec(spec_from_json,SOURCE)
    records={};provenance=[]
    for row in baseline['rows']:
        n,count,u=row['rounds'],row['shots'],row['interval_seconds'];path=paths.resolve_recorded(row['raw_path']);raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==row['raw_sha256']
        syn,data=bits_from_shots(unpack_hardware(json.loads(raw),count,n,distance=5),n,12,25)
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=count);rec=record_from_bits(spec,syn,data)
        assert np.array_equal(rec.detectors,saved[f'n{n}_detectors']) and np.array_equal(data,saved[f'n{n}_data'])
        records[n]=(spec,rec,saved[f'n{n}_prediction'],saved[f'n{n}_failure'])
        provenance.append(dict(job_id=row['job_id'],raw_sha256=row['raw_sha256'],raw_path=row['raw_path']))
    configs=[];predictions={}
    demdir=paths.RESULTS/'decoders/d5_h2_2_p_read_sensitivity'
    for pr in VALUES:
        varied=dict(policy,p_read=pr);rows=[]
        for row in baseline['rows']:
            n,u=row['rounds'],row['interval_seconds'];spec,rec,oldpred,oldfail=records[n]
            noise=round_probabilities(n,u,policy=varied)
            assert [x.p_data for x in noise]==row['round_data_probabilities']
            dem=dem_for(paper_graph(spec,.004,0,pr),noise=noise)
            dempath=demdir/f'p_read_{pr:g}_n{n}.dem';paths.write_text(dempath, dem)
            pred=PyMatchingDecoder(dem).decode_batch(rec.detectors);fail=np.any(pred!=rec.observables,axis=1)
            if pr==.001:
                assert dem==paths.read_text(paths.resolve_recorded(row['dem_path'])) and np.array_equal(pred,oldpred)
                assert int(fail.sum())==row['logical_failures']
            rows.append(dict(rounds=n,shots=len(fail),logical_failures=int(fail.sum()),logical_error_probability=float(fail.mean()),changed_predictions=int(np.any(pred!=oldpred,axis=1).sum()),corrected=int((oldfail & ~fail).sum()),harmed=int((~oldfail & fail).sum()),dem_path=str(dempath),dem_sha256=hashlib.sha256(dem.encode()).hexdigest()))
            predictions[f'p_read_{pr:g}_n{n}']=pred
        configs.append(dict(p_read=pr,rows=rows))
        print('Decoded p_read',pr,':',[r['logical_failures'] for r in rows],flush=True)
    rawrows=[{k:r[k] for k in ['rounds','shots','interval_seconds','raw_data_bit_errors','data_bits','raw_data_error_probability','data_bit_errors_by_qubit']} for r in baseline['rows']]
    out=dict(description='Offline decoder-weight sensitivity, varying syndrome and final-readout p_read together. No added record flips, postselection, or new hardware jobs. Parameter range is a stress test, not calibrated uncertainty; baseline remains p_read=0.001.',baseline_policy=policy,source=str(SOURCE_.with_suffix('.json')),source_sha256=hashlib.sha256(SOURCE_.with_suffix('.json').read_bytes()).hexdigest(),provenance=provenance,configurations=configs,raw_errors=rawrows)
    paths.write_json(OUT.with_suffix('.json'), out);paths.save_npz(OUT.with_suffix('.npz'),**predictions)
    lines=['# d=5 physical H2-2 readout-weight sensitivity','','p_ext=0.004; fixed sleep model; p_read varied jointly for syndrome and final readout. All data qubits retained.','', '| N | '+' | '.join(f'p_read={v:g}' for v in VALUES)+' |','|---:|'+'---:|'*len(VALUES)]
    for i,r in enumerate(rawrows):lines.append('| '+str(r['rounds'])+' | '+' | '.join(f"{100*c['rows'][i]['logical_error_probability']:.3f}% ({c['rows'][i]['logical_failures']})" for c in configs)+' |')
    paths.write_text(OUT.with_suffix('.md'), '\n'.join(lines)+'\n')
    print(json.dumps(rawrows,indent=2),flush=True)
    return out
