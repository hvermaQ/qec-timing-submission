"""Decode the five physical H2-2 d=5 T=1 s jobs with the selected d=5 policy."""
import hashlib
import json
from dataclasses import replace
from importlib.metadata import version
from pathlib import Path
import numpy as np
from analyze_d5_h2_2_zero_sleep_control import unpack_hardware
from analyze_single_qubit_pilot import wilson
from h2_2_decoder import POLICY as D3_POLICY, round_probabilities
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'runs/d5_h2_2_t1_20261113'
OUT=ROOT/'results/d5_h2_2_t1_p_ext_0_004_3500_shots'
SETTINGS=[(2,500),(3,750),(4,1000),(6,750),(10,500)]


def main():
    _register_builtins()
    policy=json.loads((ROOT/'configs/h2_2_d5_decoder.json').read_text())
    assert policy['distance']==5 and policy['p_ext']==.004
    # Explicit policy must not change historical/default d=3 probabilities.
    assert round_probabilities(2,0)[0].p_data==D3_POLICY['p_ext']==.00117
    assert all(v.p_data==.004 for v in round_probabilities(2,0,policy=policy))
    base=spec_from_json(json.loads((ROOT.parent/'results/hardware/programs/d5_X_r5_p0.json').read_text())['spec'])
    assert base.code.n_data==25 and base.basis=='X'
    demdir=ROOT/'results/decoders'/policy['policy_version'];demdir.mkdir(parents=True,exist_ok=True)
    rows=[];arrays={};seen=set()
    for n,count in SETTINGS:
        path=RUN/'execute'/f'n{n}'/'job.json';job=json.loads(path.read_text());u=job['delta_t_seconds']
        assert job['platform']=='nexus:H2-2' and job['options']=={'no_opt':True}
        assert job['job']['status']=='COMPLETED' and not job['job'].get('error')
        assert job['decoder_policy']==policy and job['shots']==count and job['rounds']==n
        assert job['total_requested_sleep_seconds']==1 and abs(u*(n-1)-1)<1e-12
        assert not job['artificial_faults'] and job['job_id'] not in seen;seen.add(job['job_id'])
        assert hashlib.sha256(Path(job['program']).read_bytes()).hexdigest()==job['program_sha256']
        assert len(job['results'])==1 and not job['results'][0]['error']
        result=job['results'][0];rawpath=path.parent/f"result_{result['index']}.txt";raw=rawpath.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==result['raw_sha256']
        syn,data=bits_from_shots(unpack_hardware(json.loads(raw),count,n),n,12,25)
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=count)
        rec=record_from_bits(spec,syn,data)
        assert rec.detectors.shape==(count,12*(n+1))
        assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(data[:,[0,5,10,15,20]],axis=1))
        noise=round_probabilities(n,u,policy=policy)
        assert len(noise)==n and noise[0].p_data==.004
        dem=dem_for(paper_graph(spec,policy['p_ext'],0,policy['p_read']),noise=noise)
        dempath=demdir/f'T1_n{n}.dem'
        if dempath.exists():assert dempath.read_text()==dem
        dempath.write_text(dem);decoder=PyMatchingDecoder(dem)
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
    OUT.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');np.savez_compressed(OUT.with_suffix('.npz'),**arrays)
    lines=['# Physical H2-2 d=5 T=1 s logical errors','',f"Frozen policy: {policy['policy_version']}; p_ext=0.004, p_read=0.001. All 25 data qubits included; no postselection.",'','| N | Interval (s) | Logical failures / shots | Logical error | 95% Wilson | Raw data error |','|---:|---:|---:|---:|---:|---:|']
    for r in rows:
        lo,hi=r['logical_wilson_95'];lines.append(f"| {r['rounds']} | {r['interval_seconds']:.6g} | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% | {100*r['raw_data_error_probability']:.3f}% |")
    lines+=['','Intervals reflect shot sampling under the fixed decoder. These observations alone do not establish a unique optimum.']
    OUT.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines),flush=True)


if __name__=='__main__':main()
