"""d=5 X-memory on the H2-1E emulator: pool completed sleep jobs and decode; never submit.

Ported from SG_final_round/src/ (calculations verbatim; only paths and writes changed):

    sleep_results()              analyze_d5_sleep_results.py      HISTORICAL
    redecode_sleep_dependent()   redecode_d5_sleep_dependent.py

Both re-open the job records listed in results/sleep/d5_h2_1e_all_job_status.json (recorded
as absolute /Users/harshank_s/... paths) through `paths.resolve_recorded`.
"""
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import replace

import numpy as np

from .. import decoder, paths
from ..decoder import (LEGACY_P_EXT as P_EXT, LEGACY_P_READ as P_READ, LINEAR_RATE, QUADRATIC_FREQUENCY_HZ,
                       INCOHERENT_FACTOR, idle_probability, legacy_round_probabilities as round_probabilities)
from ..jobs import OPTIONS
from ..stats import wilson
from ..unpack import unpack
from .emulator_d3 import base_spec, qec

SOURCE = paths.BASELINE_D5   # pinned d=5 baseline (.ll); .json holds the spec


def sleep_results():
    """HISTORICAL (superseded by redecode_sleep_dependent). Decode completed d=5 H2-1E sleep jobs.

    Decoder: legacy sleep-dependent phenomenological MWPM, p_ext=0.002, p_read=0.001, H2-1E
    published defaults (decoder.legacy_round_probabilities), with fixed-DEM sensitivity counts
    at p_data=0.002, 0.02, 0.1. -> results/sleep/d5_h2_1e_sleep_logical_probabilities.{json,md},
    results/sleep/decoders/d5_h2_1e_sleep/.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    OUT=paths.RESULTS/'d5_h2_1e_sleep_logical_probabilities'
    _register_builtins()
    inventory=json.loads(paths.read_text(paths.RESULTS/'d5_h2_1e_all_job_status.json'))
    assert len({r['job_id'] for r in inventory})==len(inventory)
    base=base_spec(spec_from_json,SOURCE)
    assert base.code.n_data==25 and len(base.code.logical('X'))==5
    demdir=paths.RESULTS/'decoders/d5_h2_1e_sleep'
    grouped=defaultdict(list)
    for item in inventory:
        if item['status']!='COMPLETED' or item['error']:continue
        assert item['results'] and all(r['error'] is None for r in item['results'])
        path=paths.resolve_recorded(item['path']);job=json.loads(paths.read_text(path))
        assert job['platform']=='nexus:H2-1E'
        assert job['options']==OPTIONS
        rawpath=path.parent/'result_0.txt'
        assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==item['raw_sha256']['result_0.txt']
        n=item['rounds'];u=item['delta_t_seconds'];total=round(u*(n-1),12)
        program=paths.resolve_recorded(job['program']);digest=hashlib.sha256(program.read_bytes()).hexdigest()
        manifest=json.loads(paths.read_text(program.parent/'manifest.json'))
        assert manifest['bitcode_sha256'][f'n{n}']==digest
        shots=unpack(json.loads(paths.read_text(rawpath)),item['shots'],n,distance=5)
        grouped[(total,n,u)].append((shots,dict(job_id=item['job_id'],shots=item['shots'],raw_sha256=item['raw_sha256']['result_0.txt'],program_sha256=digest,source=str(path))))
    rows=[]
    for (total,n,u),batches in sorted(grouped.items()):
        assert len({m['program_sha256'] for _,m in batches})==1
        shots=[shot for batch,_ in batches for shot in batch];count=len(shots)
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=count)
        syn,dat=bits_from_shots(shots,n,12,25);rec=record_from_bits(spec,syn,dat)
        assert rec.detectors.shape==(count,12*(n+1))
        assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(dat[:,[0,5,10,15,20]],axis=1))
        sensitivity={};primary=None
        for p in [.002,.02,.1]:
            dem=dem_for(paper_graph(spec,p,0,.001))
            dempath=demdir/f't{total}_n{n}_p{p}.dem';paths.write_text(dempath, dem)
            decoder_=PyMatchingDecoder(dem)
            # Independent boundary checks: ideal readout and a logical Z string.
            testdat=np.zeros((2,25),dtype=bool);testdat[1,list(base.code.logical('Z'))]=True
            testrec=record_from_bits(spec,np.zeros((2,n,12),dtype=bool),testdat)
            assert not testrec.detectors.any() and testrec.observables[:,0].tolist()==[False,True]
            assert not decoder_.decode_batch(testrec.detectors).any()
            prediction=decoder_.decode_batch(rec.detectors)
            failure=np.any(prediction!=rec.observables,axis=1)
            sensitivity[str(p)]=int(failure.sum())
            if p==.002:primary=failure
        sleep_dem=dem_for(paper_graph(spec,P_EXT,0,P_READ),noise=round_probabilities(n,u))
        paths.write_text(demdir/f't{total}_n{n}_sleep.dem', sleep_dem)
        prediction=PyMatchingDecoder(sleep_dem).decode_batch(rec.detectors)
        primary=np.any(prediction!=rec.observables,axis=1)
        k=int(primary.sum());offset=0;sources=[]
        for batch,meta in batches:
            sources.append(dict(meta,logical_failures=int(primary[offset:offset+len(batch)].sum())))
            offset+=len(batch)
        row=dict(total_requested_sleep_seconds=total,rounds=n,delta_t_seconds=u,shots=count,logical_failures=k,logical_error_probability=k/count,wilson_95=wilson(k,count),raw_logical_parity_flips=int(rec.observables.sum()),decoder_sensitivity_failures=sensitivity,mean_data_error=float(dat.mean()),sources=sources)
        rows.append(row);print(json.dumps(row),flush=True)
    status=Counter(r['status'] if not r['error'] else 'REJECTED' for r in inventory)
    result=dict(platform='nexus:H2-1E',distance=5,basis='X',submission_attempts=len(inventory),job_status_counts=dict(status),completed_shots=sum(r['shots'] for r in rows),rows=rows,primary_decoder='Sleep-dependent phenomenological MWPM: p_ext=.002, p_read=.001, p_lin=.0028*u, p_quad=sin(pi*.043*2*u)^2; independent flip composition; first extraction has no sleep; d=5 topology',logical_observable=[0,5,10,15,20],all_packed_shots_match_joint_formatted_counts=True,no_postselection=True,extraction_duration_neglected=True,parallel_sleep_verified=False)
    paths.write_json(OUT.with_suffix('.json'), result)
    lines=['# d=5 H2-1E sleep experiments: logical error probabilities','',f"Status: {dict(status)} across {len(inventory)} unique execution attempts. Completed shots: {result['completed_shots']}. Rejected requests are not counted as zero-failure experiments. Waiting jobs have no logical estimate. No provider submissions were made during analysis.",'',result['primary_decoder']+'. No weights were optimized using these outcomes. These are probabilities per complete experiment, not per-round or per-second rates.','', '| Requested sleep T (s) | N | Delta t (s) | Failures / shots | P_L | 95% Wilson interval |','|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lo,hi=r['wilson_95'];lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% |")
    lines+=['','Raw packed shots match provider-formatted joint counts; all outputs are Boolean with the expected 25 data tags and 12 syndrome tags per round. Bitcode and raw-result hashes were verified. The measured logical parity was independently checked on q0,q5,q10,q15,q20. Ideal and logical-Z boundary cases were checked for every decoder. Fixed-DEM sensitivity counts at p_data=.002,.02,.1 are retained in JSON.','', 'Extraction duration is neglected; physical overlap of the all-data sleeps is unverified. The decoder is phenomenological, not a calibrated circuit-level model. Wilson intervals cover independent shot sampling only. T=1 and T=0.5 experiments are kept separate. Nearby settings have few failures and overlapping sampling intervals; the observed minimum does not establish a unique optimum.','', '## All execution attempts','', '| N | Requested sleep T (s) | Shots | State | Job ID |','|---:|---:|---:|---|---|']
    for r in inventory:lines.append(f"| {r['rounds']} | {r['delta_t_seconds']*(r['rounds']-1):.4g} | {r['shots']} | {r['error'] or r['status']} | {r['job_id']} |")
    paths.write_text(OUT.with_suffix('.md'), '\n'.join(lines)+'\n')
    print('STATUS',dict(status),'COMPLETED SHOTS',result['completed_shots'])
    return result


def redecode_sleep_dependent():
    """Pool d=5 H2-1E raw measurements and compare fixed/sleep-dependent DEMs.

    Decoders: fixed phenomenological MWPM p_data=0.002 vs the legacy sleep-dependent H2-1E
    policy (decoder.legacy_round_probabilities, p_ext=0.002), unchanged from the d=3
    re-decode. No provider submissions, logical-label training, noise injection,
    postselection, or alteration of raw files. `policy_source` now records decoder.py, where
    that policy lives (it recorded SG_final_round/src/redecode_d3_sleep_dependent.py).
    -> results/sleep/d5_sleep_dependent_redecode.{json,md,npz},
    results/sleep/d5_h2_1e_pooled_raw_measurements.npz, results/sleep/decoders/d5_sleep_dependent/.
    """
    from scipy.stats import binomtest
    from qec_timing.codes.base import checks_of
    from .. import reports
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    OUT=paths.RESULTS/'d5_sleep_dependent_redecode'
    PREVIOUS=paths.RESULTS/'d5_fixed_baseline_before_sleep_redecode_d5d743d35114.json'
    POLICY_SOURCE=paths.SOURCE_MOVES['redecode_d3_sleep_dependent.py']
    assert POLICY_SOURCE.samefile(decoder.__file__)
    _register_builtins()
    previous=json.loads(paths.read_text(PREVIOUS))
    previous_jobs={s['job_id']:s for r in previous['rows'] for s in r['sources']}
    inventory=json.loads(paths.read_text(paths.RESULTS/'d5_h2_1e_all_job_status.json'))
    assert len({r['job_id'] for r in inventory})==len(inventory)
    base=base_spec(spec_from_json,SOURCE)
    grouped=defaultdict(list)
    for item in inventory:
        if item['status']!='COMPLETED' or item['error']:continue
        assert item['results'] and all(r['error'] is None for r in item['results'])
        path=paths.resolve_recorded(item['path']);job=json.loads(paths.read_text(path))
        assert job['platform']=='nexus:H2-1E' and job['options']==OPTIONS
        assert job['as_entity']=='q_sq'
        n=job['rounds'];u=job['delta_t_seconds'];total=round((n-1)*u,12)
        assert total in [.5,1.] and item['shots']==job['shots']
        rawpath=path.parent/'result_0.txt';rawhash=hashlib.sha256(rawpath.read_bytes()).hexdigest()
        assert rawhash==item['raw_sha256']['result_0.txt']
        program=paths.resolve_recorded(job['program']);programhash=hashlib.sha256(program.read_bytes()).hexdigest()
        manifest=json.loads(paths.read_text(program.parent/'manifest.json'))
        assert manifest['bitcode_sha256'][f'n{n}']==programhash
        assert manifest['total_requested_sleep_seconds']==total
        shots=unpack(json.loads(paths.read_text(rawpath)),job['shots'],n,distance=5)
        metadata=dict(job_id=job['job_id'],shots=len(shots),source=str(path),raw_sha256=rawhash,program_sha256=programhash)
        if job['job_id'] in previous_jobs:
            old=previous_jobs[job['job_id']]
            assert rawhash==old['raw_sha256'] and programhash==old['program_sha256']
        grouped[(total,n,u)].append((shots,metadata))
    # Confirm all completed locally recorded sleep jobs enter the pooled inventory.
    # (The original tested 'd5_' in the absolute path; its root contained no 'd5_'.)
    local_ids=set()
    for p in paths.RUNS.rglob('job.json'):
        if 'd5_' not in p.relative_to(paths.RUNS).as_posix():continue
        j=json.loads(paths.read_text(p))
        if j.get('platform')=='nexus:H2-1E' and j.get('job',{}).get('status')=='COMPLETED' and not j['job'].get('error'):
            local_ids.add(j['job_id'])
    included={meta['job_id'] for batches in grouped.values() for _,meta in batches}
    assert included==local_ids and set(previous_jobs)<=included
    rows=[];raw_arrays={};paired_arrays={};demdir=paths.RESULTS/'decoders/d5_sleep_dependent'
    reproduced=set()
    for (total,n,u),batches in sorted(grouped.items()):
        assert len({m['program_sha256'] for _,m in batches})==1
        shots=[shot for batch,_ in batches for shot in batch];count=len(shots)
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=count)
        syn,dat=bits_from_shots(shots,n,12,25);rec=record_from_bits(spec,syn,dat)
        assert rec.detectors.shape==(count,12*(n+1))
        assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(dat[:,[0,5,10,15,20]],axis=1))
        graph=paper_graph(spec,P_EXT,0,P_READ)
        fixed_dem=dem_for(graph);fixed_decoder=PyMatchingDecoder(fixed_dem)
        fixed_prediction=fixed_decoder.decode_batch(rec.detectors)
        fixed_failure=np.any(fixed_prediction!=rec.observables,axis=1)
        noise=round_probabilities(n,u)
        assert len(noise)==n and noise[0].p_data==P_EXT
        original_round=graph.noise.round_noise(0,u)
        assert dem_for(graph,noise=[original_round]*n)==fixed_dem
        sleep_dem=dem_for(graph,noise=noise);sleep_decoder=PyMatchingDecoder(sleep_dem)
        sleep_prediction=sleep_decoder.decode_batch(rec.detectors)
        sleep_failure=np.any(sleep_prediction!=rec.observables,axis=1)
        # Check ideal/logical strings and every single-data-fault detector signature.
        testdat=np.zeros((2,25),dtype=bool);testdat[1,list(base.code.logical('Z'))]=True
        testrec=record_from_bits(spec,np.zeros((2,n,12),dtype=bool),testdat)
        assert not testrec.detectors.any() and testrec.observables[:,0].tolist()==[False,True]
        assert not fixed_decoder.decode_batch(testrec.detectors).any()
        assert not sleep_decoder.decode_batch(testrec.detectors).any()
        for r in [0,n-1]:
            one_syn=np.zeros((25,n,12),dtype=bool);one_dat=np.eye(25,dtype=bool)
            H=np.zeros((12,25),dtype=bool)
            for c,chk in enumerate(checks_of(base.code,'X')):H[c,list(chk.support)]=True
            one_syn[:,r:,:]=np.broadcast_to(H.T[:,None,:],(25,n-r,12))
            events=record_from_bits(spec,one_syn,one_dat)
            assert events.detectors.sum()==int(H.sum())
            assert np.array_equal(events.detectors.reshape(25,n+1,12)[:,r,:],H.T)
        corrected=int(np.count_nonzero(fixed_failure & ~sleep_failure))
        introduced=int(np.count_nonzero(~fixed_failure & sleep_failure))
        kb=int(fixed_failure.sum());ks=int(sleep_failure.sum())
        assert ks==kb-corrected+introduced
        discordant=corrected+introduced
        pv=float(binomtest(corrected,discordant,.5).pvalue) if discordant else 1.
        key=f't{str(total).replace(".","p")}_n{n}'
        raw_arrays[key+'_syndromes']=syn;raw_arrays[key+'_data']=dat
        raw_arrays[key+'_job_index']=np.concatenate([np.full(len(batch),i,dtype=np.int16) for i,(batch,_) in enumerate(batches)])
        for name,array in [('fixed_prediction',fixed_prediction),('sleep_prediction',sleep_prediction),('fixed_failure',fixed_failure),('sleep_failure',sleep_failure)]:paired_arrays[key+'_'+name]=array
        sources=[];offset=0
        for batch,meta in batches:
            end=offset+len(batch);bk=int(fixed_failure[offset:end].sum());sk=int(sleep_failure[offset:end].sum())
            if meta['job_id'] in previous_jobs:
                assert bk==previous_jobs[meta['job_id']]['logical_failures'],'Previous fixed count did not reproduce'
                reproduced.add(meta['job_id'])
            sources.append(dict(meta,offset=offset,fixed_failures=bk,sleep_failures=sk,
                corrected=int(np.count_nonzero(fixed_failure[offset:end] & ~sleep_failure[offset:end])),
                introduced=int(np.count_nonzero(~fixed_failure[offset:end] & sleep_failure[offset:end]))))
            offset=end
        fixed_path=demdir/(key+'_fixed.dem');sleep_path=demdir/(key+'_sleep.dem')
        paths.write_text(fixed_path, fixed_dem);paths.write_text(sleep_path, sleep_dem)
        prev=next((r for r in previous['rows'] if r['total_requested_sleep_seconds']==total and r['rounds']==n),None)
        row=dict(total_requested_sleep_seconds=total,rounds=n,delta_t_seconds=u,shots=count,
            fixed_failures=kb,fixed_probability=kb/count,fixed_wilson_95=wilson(kb,count),
            sleep_failures=ks,sleep_probability=ks/count,sleep_wilson_95=wilson(ks,count),
            failure_count_change=ks-kb,probability_change=ks/count-kb/count,
            corrected_baseline_failures=corrected,introduced_failures=introduced,paired_exact_mcnemar_p=pv,
            p_idle=idle_probability(u),p_data_first_round=P_EXT,p_data_after_sleep=noise[-1].p_data,
            previous_report_failures=prev['logical_failures'] if prev else None,
            previous_report_shots=prev['shots'] if prev else None,
            newly_added_shots=count-(prev['shots'] if prev else 0),
            fixed_dem_path=str(fixed_path),sleep_dem_path=str(sleep_path),
            fixed_dem_sha256=hashlib.sha256(fixed_dem.encode()).hexdigest(),sleep_dem_sha256=hashlib.sha256(sleep_dem.encode()).hexdigest(),
            pooled_raw_key=key,sources=sources)
        rows.append(row)
        print('T',total,'N',n,'fixed',kb,'sleep',ks,'shots',count,'corrected/new',corrected,introduced,flush=True)
    assert reproduced==set(previous_jobs)
    raw_npz=paths.RESULTS/'d5_h2_1e_pooled_raw_measurements.npz'
    paths.save_npz(raw_npz,**raw_arrays)
    paths.save_npz(OUT.with_suffix('.npz'),**paired_arrays)
    corrected=sum(r['corrected_baseline_failures'] for r in rows);introduced=sum(r['introduced_failures'] for r in rows)
    result=dict(platform='nexus:H2-1E',distance=5,basis='X',unique_jobs=len(included),total_shots=sum(r['shots'] for r in rows),
        previous_report=str(PREVIOUS),previous_report_sha256=hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),previous_jobs_reproduced=len(reproduced),
        model=dict(policy='Same sleep-dependent phenomenological model as the existing d=3 re-decode, with d=5 topology',
            p_ext=P_EXT,p_read=P_READ,linear_rate_per_second=LINEAR_RATE,quadratic_frequency_cycles_per_second=QUADRATIC_FREQUENCY_HZ,incoherent_frequency_multiplier=INCOHERENT_FACTOR,
            p_linear='0.0028*u',p_quadratic='sin(pi*0.043*2*u)^2',p_idle='p_linear+p_quadratic-2*p_linear*p_quadratic',
            p_data_after_sleep='p_ext+p_idle-2*p_ext*p_idle',placement='p_ext before first extraction; p_ext XOR idle before each of remaining N-1 extractions; no final sleep',
            training='None; no parameters selected using d=5 logical outcomes',limitation='Transferred published-default assumptions used by d=3 model, not an execution-time calibrated d=5 circuit-level DEM',
            policy_source=str(POLICY_SOURCE),policy_source_sha256=hashlib.sha256(POLICY_SOURCE.read_bytes()).hexdigest()),
        raw_measurements_npz=str(raw_npz),rows=rows,
        paired_aggregate=dict(corrected=corrected,introduced=introduced,net_failure_change=introduced-corrected,exact_mcnemar_p=float(binomtest(corrected,corrected+introduced,.5).pvalue) if corrected+introduced else 1.),
        checks='No duplicate jobs; raw hashes and bitcode hashes verified; packed shots match formatted joint counts; previous per-job baseline failures reproduced exactly; no postselection',
        extraction_duration_neglected=True,parallel_sleep_verified=False)
    by_total=[]
    for total in sorted({r['total_requested_sleep_seconds'] for r in rows}):
        selected=[r for r in rows if r['total_requested_sleep_seconds']==total]
        c=sum(r['corrected_baseline_failures'] for r in selected);h=sum(r['introduced_failures'] for r in selected)
        by_total.append(dict(total_requested_sleep_seconds=total,shots=sum(r['shots'] for r in selected),fixed_failures=sum(r['fixed_failures'] for r in selected),sleep_failures=sum(r['sleep_failures'] for r in selected),corrected=c,introduced=h,net_failure_change=h-c,exact_mcnemar_p=float(binomtest(c,c+h,.5).pvalue) if c+h else 1.))
    result['paired_by_total_sleep']=by_total
    paths.write_json(OUT.with_suffix('.json'), result)
    reports.redecode_d5_md(result)
    print('TOTAL',result['total_shots'],'JOBS',len(included),'PAIRED',result['paired_aggregate'])
    return result
