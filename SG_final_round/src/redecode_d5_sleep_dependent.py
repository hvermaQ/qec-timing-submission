"""Pool d=5 H2-1E raw measurements and compare fixed/sleep-dependent DEMs.

Uses the existing d=3 sleep-weight policy unchanged. No provider submissions,
logical-label training, noise injection, postselection, or alteration of raw files.
"""
import hashlib
import json
from collections import defaultdict
from dataclasses import replace
from pathlib import Path
import numpy as np
from scipy.stats import binomtest
from analyze_d5_sleep_results import unpack
from analyze_single_qubit_pilot import wilson
from single_qubit_sweep import OPTIONS
from redecode_d3_sleep_dependent import (
    P_EXT,P_READ,LINEAR_RATE,QUADRATIC_FREQUENCY_HZ,INCOHERENT_FACTOR,
    idle_probability,round_probabilities)
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots,record_from_bits
from qec_timing.hardware.collect import paper_graph
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/d5_sleep_dependent_redecode'
PREVIOUS=ROOT/'results/d5_fixed_baseline_before_sleep_redecode_d5d743d35114.json'


def main():
    _register_builtins()
    previous=json.loads(PREVIOUS.read_text())
    previous_jobs={s['job_id']:s for r in previous['rows'] for s in r['sources']}
    inventory=json.loads((ROOT/'results/d5_h2_1e_all_job_status.json').read_text())
    assert len({r['job_id'] for r in inventory})==len(inventory)
    base=spec_from_json(json.loads((ROOT.parent/'results/hardware/programs/d5_X_r5_p0.json').read_text())['spec'])
    grouped=defaultdict(list)
    for item in inventory:
        if item['status']!='COMPLETED' or item['error']:continue
        assert item['results'] and all(r['error'] is None for r in item['results'])
        path=Path(item['path']);job=json.loads(path.read_text())
        assert job['platform']=='nexus:H2-1E' and job['options']==OPTIONS
        assert job['as_entity']=='q_sq'
        n=job['rounds'];u=job['delta_t_seconds'];total=round((n-1)*u,12)
        assert total in [.5,1.] and item['shots']==job['shots']
        rawpath=path.parent/'result_0.txt';rawhash=hashlib.sha256(rawpath.read_bytes()).hexdigest()
        assert rawhash==item['raw_sha256']['result_0.txt']
        program=Path(job['program']);programhash=hashlib.sha256(program.read_bytes()).hexdigest()
        manifest=json.loads((program.parent/'manifest.json').read_text())
        assert manifest['bitcode_sha256'][f'n{n}']==programhash
        assert manifest['total_requested_sleep_seconds']==total
        shots=unpack(json.loads(rawpath.read_text()),job['shots'],n)
        metadata=dict(job_id=job['job_id'],shots=len(shots),source=str(path),raw_sha256=rawhash,program_sha256=programhash)
        if job['job_id'] in previous_jobs:
            old=previous_jobs[job['job_id']]
            assert rawhash==old['raw_sha256'] and programhash==old['program_sha256']
        grouped[(total,n,u)].append((shots,metadata))
    # Confirm all completed locally recorded sleep jobs enter the pooled inventory.
    local_ids=set()
    for p in (ROOT/'runs').rglob('job.json'):
        if 'd5_' not in str(p):continue
        j=json.loads(p.read_text())
        if j.get('platform')=='nexus:H2-1E' and j.get('job',{}).get('status')=='COMPLETED' and not j['job'].get('error'):
            local_ids.add(j['job_id'])
    included={meta['job_id'] for batches in grouped.values() for _,meta in batches}
    assert included==local_ids and set(previous_jobs)<=included
    rows=[];raw_arrays={};paired_arrays={};demdir=ROOT/'results/decoders/d5_sleep_dependent'
    demdir.mkdir(parents=True,exist_ok=True)
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
            from qec_timing.codes.base import checks_of
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
        fixed_path.write_text(fixed_dem);sleep_path.write_text(sleep_dem)
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
    np.savez_compressed(ROOT/'results/d5_h2_1e_pooled_raw_measurements.npz',**raw_arrays)
    np.savez_compressed(OUT.with_suffix('.npz'),**paired_arrays)
    corrected=sum(r['corrected_baseline_failures'] for r in rows);introduced=sum(r['introduced_failures'] for r in rows)
    result=dict(platform='nexus:H2-1E',distance=5,basis='X',unique_jobs=len(included),total_shots=sum(r['shots'] for r in rows),
        previous_report=str(PREVIOUS),previous_report_sha256=hashlib.sha256(PREVIOUS.read_bytes()).hexdigest(),previous_jobs_reproduced=len(reproduced),
        model=dict(policy='Same sleep-dependent phenomenological model as the existing d=3 re-decode, with d=5 topology',
            p_ext=P_EXT,p_read=P_READ,linear_rate_per_second=LINEAR_RATE,quadratic_frequency_cycles_per_second=QUADRATIC_FREQUENCY_HZ,incoherent_frequency_multiplier=INCOHERENT_FACTOR,
            p_linear='0.0028*u',p_quadratic='sin(pi*0.043*2*u)^2',p_idle='p_linear+p_quadratic-2*p_linear*p_quadratic',
            p_data_after_sleep='p_ext+p_idle-2*p_ext*p_idle',placement='p_ext before first extraction; p_ext XOR idle before each of remaining N-1 extractions; no final sleep',
            training='None; no parameters selected using d=5 logical outcomes',limitation='Transferred published-default assumptions used by d=3 model, not an execution-time calibrated d=5 circuit-level DEM',
            policy_source=str(ROOT/'src/redecode_d3_sleep_dependent.py'),policy_source_sha256=hashlib.sha256((ROOT/'src/redecode_d3_sleep_dependent.py').read_bytes()).hexdigest()),
        raw_measurements_npz=str(ROOT/'results/d5_h2_1e_pooled_raw_measurements.npz'),rows=rows,
        paired_aggregate=dict(corrected=corrected,introduced=introduced,net_failure_change=introduced-corrected,exact_mcnemar_p=float(binomtest(corrected,corrected+introduced,.5).pvalue) if corrected+introduced else 1.),
        checks='No duplicate jobs; raw hashes and bitcode hashes verified; packed shots match formatted joint counts; previous per-job baseline failures reproduced exactly; no postselection',
        extraction_duration_neglected=True,parallel_sleep_verified=False)
    by_total=[]
    for total in sorted({r['total_requested_sleep_seconds'] for r in rows}):
        selected=[r for r in rows if r['total_requested_sleep_seconds']==total]
        c=sum(r['corrected_baseline_failures'] for r in selected);h=sum(r['introduced_failures'] for r in selected)
        by_total.append(dict(total_requested_sleep_seconds=total,shots=sum(r['shots'] for r in selected),fixed_failures=sum(r['fixed_failures'] for r in selected),sleep_failures=sum(r['sleep_failures'] for r in selected),corrected=c,introduced=h,net_failure_change=h-c,exact_mcnemar_p=float(binomtest(c,c+h,.5).pvalue) if c+h else 1.))
    result['paired_by_total_sleep']=by_total
    OUT.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    report(result)
    print('TOTAL',result['total_shots'],'JOBS',len(included),'PAIRED',result['paired_aggregate'])


def report(result):
    lines=['# d=5 H2-1E: pooled raw data and sleep-dependent DEM comparison','',
        f"{result['unique_jobs']} unique completed jobs; {result['total_shots']} total shots. All completed d=5 H2-1E sleep runs recorded locally are included once. Total requested sleep is retained as a grouping key; T=1 and T=0.5 are never pooled together. No jobs submitted.",'',
        '## Decoder policy','',
        'Fixed baseline: p_data=.002 before each ideal extraction round; syndrome and final data readout flips .001. Sleep-dependent: retain p_ext=.002 and readout .001; p_lin(u)=.0028u, p_quad(u)=sin(pi*.043*2*u)^2, p_idle=p_lin+p_quad-2*p_lin*p_quad. First extraction has p_ext only; each later extraction has p_ext+p_idle-2*p_ext*p_idle. There are exactly N-1 sleep contributions. This reproduces the existing d=3 sleep-dependent prescription with d=5 code geometry, with no fitting to d=5 logical labels. Published-default assumptions transferred by this policy are not execution-time calibration parameters. Gate correlations, detailed transport/extraction durations and readout asymmetry are omitted.','',
        '## Paired comparison on the same expanded dataset','',
        '| T (s) | N | Delta t (s) | Shots | Fixed failures | Fixed P_L | Sleep failures | Sleep P_L | Sleep 95% Wilson CI | Change in failures | Corrected / introduced |','|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        lo,hi=r['sleep_wilson_95']
        lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['shots']} | {r['fixed_failures']} | {100*r['fixed_probability']:.3f}% | {r['sleep_failures']} | {100*r['sleep_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% | {r['failure_count_change']:+d} | {r['corrected_baseline_failures']} / {r['introduced_failures']} |")
    lines+=['','## Distinguishing new shots from new decoder weights','',
        'All downloaded repeats are pooled by requested total sleep and extraction count. Differences between the earlier report and the new fixed column are due to this additional data. Differences between fixed and sleep-dependent columns above are solely from re-decoding identical shots. Every previously reported per-job fixed count was reproduced exactly.','',
        '| T (s) | N | Earlier reported fixed failures / shots | Added shots | Expanded fixed failures / shots |','|---:|---:|---:|---:|---:|']
    for r in result['rows']:lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {r['previous_report_failures']}/{r['previous_report_shots']} | {r['newly_added_shots']} | {r['fixed_failures']}/{r['shots']} |")
    a=result['paired_aggregate'];lines+=['',f"Across all groups, {a['corrected']} fixed-decoder failures were corrected and {a['introduced']} failures were introduced; net failure-count change {a['net_failure_change']:+d}. Exact paired McNemar p={a['exact_mcnemar_p']:.6g}. This aggregate reflects this shot allocation across different N and T; it is not an operating-point probability. Per-N paired tests are exploratory and unadjusted for multiple comparisons.",'',
        'Probabilities are per complete experiment. Wilson intervals assume independent common-probability shots and exclude decoder/calibration uncertainty and batch drift. The N=6 original/repeat discrepancy remains relevant after pooling; all per-batch counts are retained below. The model is more sleep-aware but is not guaranteed to improve every setting or match the backend. A sample minimum is not a resolved optimum.','',
        '## Per-batch provenance','', '| T (s) | N | Job ID | Shots | Fixed failures | Sleep failures |','|---:|---:|---|---:|---:|---:|']
    for r in result['rows']:
        for s in r['sources']:lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {s['job_id']} | {s['shots']} | {s['fixed_failures']} | {s['sleep_failures']} |")
    lines+=['','Artifacts: JSON contains all parameters, per-job provenance, offsets, hashes, DEM paths and paired tests. NPZ contains paired per-shot predictions and failure masks. The separate pooled-raw NPZ contains syndrome arrays, final data readouts and per-shot source-job indices. Original provider payload files and earlier analysis snapshot were preserved.','']
    OUT.with_suffix('.md').write_text('\n'.join(lines))

if __name__=='__main__':main()
