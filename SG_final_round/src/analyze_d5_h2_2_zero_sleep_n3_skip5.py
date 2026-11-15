"""Analyze raw N=3 zero-sleep control; extraction estimate uses three channels."""
import json,hashlib
from pathlib import Path
import numpy as np
from analyze_d5_h2_2_zero_sleep_control import unpack_hardware
from qec_timing.hardware.records import bits_from_shots
ROOT=Path(__file__).resolve().parents[1]
run=ROOT/'runs/d5_h2_2_zero_sleep_n3_skip5_250_20261114/execute'
j=json.loads((run/'job.json').read_text());assert j['job']['status']=='COMPLETED' and not j['job'].get('error');assert len(j['results'])==1
r=j['results'][0];assert not r['error'];raw=(run/f"result_{r['index']}.txt").read_bytes();assert hashlib.sha256(raw).hexdigest()==r['raw_sha256']
assert hashlib.sha256(Path(j['program']).read_bytes()).hexdigest()==j['program_sha256']
syn,data=bits_from_shots(unpack_hardware(json.loads(raw),250,3),3,12,25)
counts=data.sum(axis=0);q=float(data.mean());ext=lambda q:(1-np.power(1-2*q,1/3))/2
assert abs((1-(1-2*ext(q))**3)/2-q)<1e-14
rng=np.random.default_rng(20261114);hist=np.bincount(data.sum(axis=1).astype(int),minlength=26);qs=rng.multinomial(250,hist/250,size=20000)@np.arange(26)/6250
previous=json.loads((ROOT/'runs/d5_h2_2_zero_sleep_n3_250_20261114/execute/raw_analysis.json').read_text())
finite=json.loads((ROOT/'results/circuit_audit/all_stabilizer_syndrome_comparison.json').read_text())
prev=np.concatenate([np.zeros_like(syn[:,:1]),syn[:,:-1]],axis=1)
out=dict(job_id=j['job_id'],platform=j['platform'],distance=5,rounds=3,shots=250,interval_seconds=0,raw_sha256=r['raw_sha256'],program_sha256=j['program_sha256'],data_bit_errors=int(data.sum()),data_bits=6250,raw_error_probability=q,raw_shot_bootstrap_95=np.quantile(qs,[.025,.975]).tolist(),p_ext_effective_zero_boundary=float(ext(q)),p_ext_effective_bootstrap_95=np.quantile(ext(qs),[.025,.975]).tolist(),per_qubit_error_counts=counts.tolist(),syndrome_one_counts_by_round_check=syn.sum(axis=0).tolist(),detection_event_counts_by_round_check=(syn^prev).sum(axis=0).tolist(),previous_N3_raw=previous['raw_error_probability'],previous_N3_p_ext=previous['p_ext_effective_zero_boundary'],qubit_mapping=j['qubit_mapping'],assumptions='Three equal independent extraction flip channels, no added sleep; preparation/readout absorbed into effective baseline. Whole-shot bootstrap only; excludes drift and model uncertainty. No postselection or exclusion of qubits. This is a raw-data calibration diagnostic, not a decoder-policy update.')
(run/'raw_analysis.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
