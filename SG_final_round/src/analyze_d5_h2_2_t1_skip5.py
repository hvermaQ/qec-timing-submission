"""Decode a completed skip-index-5 T=1 s job with requested p_ext=0.005."""
import argparse,hashlib,json
from dataclasses import replace
from pathlib import Path
import numpy as np
from analyze_d5_h2_2_zero_sleep_control import unpack_hardware
from analyze_single_qubit_pilot import wilson
from h2_2_decoder import round_probabilities
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots,record_from_bits
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
ROOT=Path(__file__).resolve().parents[1]

def main(n):
    batch='d5_h2_2_t1_skip5_n2_n6_20261114' if n in [2,6] else 'd5_h2_2_t1_skip5_20261114'
    run=(ROOT/'runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10') if n==10 else ROOT/f'runs/{batch}/execute/n{n}'
    job=json.loads((run/'job.json').read_text())
    assert job['job']['status']=='COMPLETED' and not job['job'].get('error')
    assert job['platform']=='nexus:H2-2' and job['rounds']==n and job['shots']==(160 if n==10 else 500)
    shots=job['shots']
    assert job['qubit_mapping']['unused_index']==5
    assert hashlib.sha256(Path(job['program']).read_bytes()).hexdigest()==job['program_sha256']
    assert len(job['results'])==1 and not job['results'][0]['error']
    result=job['results'][0];rawpath=run/f"result_{result['index']}.txt";raw=rawpath.read_bytes()
    assert hashlib.sha256(raw).hexdigest()==result['raw_sha256']
    policy=json.loads((ROOT/'configs/h2_2_d5_skip5_decoder.json').read_text())
    policy.update(p_ext=.005,policy_version='h2_2_d5_skip5_p_ext_0_005_20261114',selection='User-requested p_ext=0.005 for skip-index-5 finite-sleep decoding',calibration_job_ids=['AFByb3ZpZGVySm9iAaHZaESAcwCVLDEccgwFew'],calibration_result=str(ROOT/'runs/d5_h2_2_zero_sleep_n3_skip5_250_20261114/execute/raw_analysis.json'))
    _register_builtins();base=spec_from_json(json.loads((ROOT.parent/'results/hardware/programs/d5_X_r5_p0.json').read_text())['spec'])
    u=job['delta_t_seconds'];assert abs(u*(n-1)-1)<1e-12
    spec=replace(base,schedule=Schedule.rounds(u,n),shots=shots)
    syn,data=bits_from_shots(unpack_hardware(json.loads(raw),shots,n),n,12,25)
    rec=record_from_bits(spec,syn,data)
    assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(data[:,[0,5,10,15,20]],axis=1))
    dem=dem_for(paper_graph(spec,.005,0,policy['p_read']),noise=round_probabilities(n,u,policy=policy))
    pred=PyMatchingDecoder(dem).decode_batch(rec.detectors);fail=np.any(pred!=rec.observables,axis=1);k=int(fail.sum())
    stem=run/'analysis_p_ext_0_005';dempath=run/'decoder_p_ext_0_005.dem';dempath.write_text(dem)
    out=dict(platform=job['platform'],distance=5,rounds=n,shots=shots,interval_seconds=u,total_requested_sleep_seconds=1,job_id=job['job_id'],qubit_mapping=job['qubit_mapping'],decoder_policy=policy,logical_failures=k,logical_error_probability=k/shots,logical_wilson_95=wilson(k,shots),data_bit_errors=int(data.sum()),data_bits=int(data.size),raw_data_error_probability=float(data.mean()),data_bit_errors_by_qubit=data.sum(axis=0).tolist(),syndrome_one_counts_by_round_check=syn.sum(axis=0).tolist(),raw_sha256=result['raw_sha256'],program_sha256=job['program_sha256'],dem_sha256=hashlib.sha256(dem.encode()).hexdigest(),dem_path=str(dempath),no_postselection=True)
    stem.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n')
    np.savez_compressed(stem.with_suffix('.npz'),syndrome=syn,data=data,detectors=rec.detectors,observable=rec.observables,prediction=pred,failure=fail)
    print(json.dumps(out,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--rounds',type=int,choices=[2,3,4,6,10],default=3);main(p.parse_args().rounds)
