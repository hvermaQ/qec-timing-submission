"""Decode completed d=5 H2-1E sleep jobs; never submit or alter raw outcomes."""
import hashlib
import json
from collections import Counter, defaultdict
from dataclasses import replace
from pathlib import Path
import numpy as np
from analyze_single_qubit_pilot import wilson
from qec_timing.hardware.providers import _register_builtins
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.records import bits_from_shots,record_from_bits
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/d5_h2_1e_sleep_logical_probabilities'


def unpack(raw,shots,n):
    packed=np.asarray(raw['shots']['array'],dtype=np.uint8)
    bits=np.unpackbits(packed,axis=1)[:,:raw['shots']['width']]
    assert bits.shape==(shots,len(raw['bits']))
    observed=Counter(''.join(map(str,row)) for row in bits)
    reported=Counter()
    for row in raw['counts_formatted']:reported[row['bitstring']]+=row['count']
    assert observed==reported,'Packed shots disagree with formatted joint counts'
    tags={}
    for column,(tag,indices) in enumerate(raw['bits']):
        assert len(indices)==1
        if indices[0]==0:
            assert tag not in tags
            tags[tag]=bits[:,column]
        else:assert not bits[:,column].any(),'Non-Boolean output register'
    assert set(tags)=={f'm{q}' for q in range(25)}|{f's{r}_{c}' for r in range(n) for c in range(12)}
    return [{tag:int(values[i]) for tag,values in tags.items()} for i in range(shots)]


def main():
    _register_builtins()
    inventory=json.loads((ROOT/'results/d5_h2_1e_all_job_status.json').read_text())
    assert len({r['job_id'] for r in inventory})==len(inventory)
    base=spec_from_json(json.loads((ROOT.parent/'results/hardware/programs/d5_X_r5_p0.json').read_text())['spec'])
    assert base.code.n_data==25 and len(base.code.logical('X'))==5
    demdir=ROOT/'results/decoders/d5_h2_1e_sleep';demdir.mkdir(parents=True,exist_ok=True)
    grouped=defaultdict(list)
    for item in inventory:
        if item['status']!='COMPLETED' or item['error']:continue
        assert item['results'] and all(r['error'] is None for r in item['results'])
        path=Path(item['path']);job=json.loads(path.read_text())
        assert job['platform']=='nexus:H2-1E'
        rawpath=path.parent/'result_0.txt'
        assert hashlib.sha256(rawpath.read_bytes()).hexdigest()==item['raw_sha256']['result_0.txt']
        n=item['rounds'];u=item['delta_t_seconds'];total=round(u*(n-1),12)
        program=Path(job['program']);digest=hashlib.sha256(program.read_bytes()).hexdigest()
        manifest=json.loads((program.parent/'manifest.json').read_text())
        assert manifest['bitcode_sha256'][f'n{n}']==digest
        shots=unpack(json.loads(rawpath.read_text()),item['shots'],n)
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
            dempath=demdir/f't{total}_n{n}_p{p}.dem';dempath.write_text(dem)
            decoder=PyMatchingDecoder(dem)
            # Independent boundary checks: ideal readout and a logical Z string.
            testdat=np.zeros((2,25),dtype=bool);testdat[1,list(base.code.logical('Z'))]=True
            testrec=record_from_bits(spec,np.zeros((2,n,12),dtype=bool),testdat)
            assert not testrec.detectors.any() and testrec.observables[:,0].tolist()==[False,True]
            assert not decoder.decode_batch(testrec.detectors).any()
            prediction=decoder.decode_batch(rec.detectors)
            failure=np.any(prediction!=rec.observables,axis=1)
            sensitivity[str(p)]=int(failure.sum())
            if p==.002:primary=failure
        k=sensitivity['0.002'];offset=0;sources=[]
        for batch,meta in batches:
            sources.append(dict(meta,logical_failures=int(primary[offset:offset+len(batch)].sum())))
            offset+=len(batch)
        row=dict(total_requested_sleep_seconds=total,rounds=n,delta_t_seconds=u,shots=count,logical_failures=k,logical_error_probability=k/count,wilson_95=wilson(k,count),raw_logical_parity_flips=int(rec.observables.sum()),decoder_sensitivity_failures=sensitivity,mean_data_error=float(dat.mean()),sources=sources)
        rows.append(row);print(json.dumps(row),flush=True)
    status=Counter(r['status'] if not r['error'] else 'REJECTED' for r in inventory)
    result=dict(platform='nexus:H2-1E',distance=5,basis='X',submission_attempts=len(inventory),job_status_counts=dict(status),completed_shots=sum(r['shots'] for r in rows),rows=rows,primary_decoder='Fixed phenomenological MWPM: p_data=.002, p_read=.001, lambda=0, final readout .001; d=5 topology',logical_observable=[0,5,10,15,20],all_packed_shots_match_joint_formatted_counts=True,no_postselection=True,extraction_duration_neglected=True,parallel_sleep_verified=False)
    OUT.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    lines=['# d=5 H2-1E sleep experiments: logical error probabilities','',f"Status: {dict(status)} across {len(inventory)} unique execution attempts. Completed shots: {result['completed_shots']}. Rejected requests are not counted as zero-failure experiments. Waiting jobs have no logical estimate. No provider submissions were made during analysis.",'',result['primary_decoder']+'. No weights were optimized using these outcomes. These are probabilities per complete experiment, not per-round or per-second rates.','', '| Requested sleep T (s) | N | Delta t (s) | Failures / shots | P_L | 95% Wilson interval |','|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lo,hi=r['wilson_95'];lines.append(f"| {r['total_requested_sleep_seconds']} | {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% |")
    lines+=['','Raw packed shots match provider-formatted joint counts; all outputs are Boolean with the expected 25 data tags and 12 syndrome tags per round. Bitcode and raw-result hashes were verified. The measured logical parity was independently checked on q0,q5,q10,q15,q20. Ideal and logical-Z boundary cases were checked for every decoder. Sensitivity counts at p_data=.02,.1 are retained in JSON.','', 'Extraction duration is neglected; physical overlap of the all-data sleeps is unverified. The decoder is phenomenological, not a calibrated circuit-level model. Wilson intervals cover independent shot sampling only. T=1 and T=0.5 experiments are kept separate. Missing settings near 0.15 s prevent a resolved optimum claim.','', '## All execution attempts','', '| N | Requested sleep T (s) | Shots | State | Job ID |','|---:|---:|---:|---|---|']
    for r in inventory:lines.append(f"| {r['rounds']} | {r['delta_t_seconds']*(r['rounds']-1):.4g} | {r['shots']} | {r['error'] or r['status']} | {r['job_id']} |")
    OUT.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print('STATUS',dict(status),'COMPLETED SHOTS',result['completed_shots'])

if __name__=='__main__':main()
