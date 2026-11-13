"""Re-decode all physical H2-2 measurements with the current approved policy."""
import ast
import hashlib
import json
from collections import Counter,defaultdict
from dataclasses import replace
from pathlib import Path
from importlib.metadata import version
import numpy as np
from scipy.stats import chi2_contingency
from analyze_single_qubit_pilot import wilson
from build_sleep_probe import SOURCE
from h2_2_decoder import POLICY,P_EXT,P_READ,round_probabilities
from redecode_d3_sleep_dependent import round_probabilities as old_noise
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots,record_from_bits
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/h2_2_hardware_p_ext_0_00117_10750_shots'
DEMS=OUT.parent/'decoders'/POLICY['policy_version'];DEMS.mkdir(parents=True,exist_ok=True)
src=ROOT/'runs/h2_2_hardware_d3_x_t1_20261111/analyze.py'
node=next(n for n in ast.parse(src.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='unpack_hardware')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(src),'exec'))
BATCHES=['h2_2_hardware_d3_x_t1_20261111','h2_2_hardware_d3_x_t1_additional_20261112','h2_2_hardware_d3_x_t1_n2_n4_20261112','h2_2_hardware_d3_x_t1_n40_n3_n4_20261113']
paths=[p for batch in BATCHES for p in sorted((ROOT/'runs'/batch).glob('n*/job.json'))]
paths += [ROOT/'runs/d3_h2_2_zero_sleep_n2_1000_20261112/execute/job.json']
_register_builtins()
base=spec_from_json(json.loads(SOURCE.with_suffix('.json').read_text())['spec'])
groups=defaultdict(list);seen=set();batchrows=[];arrays={}
for path in paths:
    job=json.loads(path.read_text());jid=job['job_id'];assert jid not in seen;seen.add(jid)
    assert job['platform']=='nexus:H2-2' and job['options']=={'no_opt':True}
    assert job['job']['status']=='COMPLETED' and not job['job'].get('error')
    n,count,u=job['rounds'],job['shots'],job['delta_t_seconds'];total=job['total_requested_sleep_seconds']
    assert abs((n-1)*u-total)<1e-12 and total in [0,1]
    program=ROOT.parent/job['program'];assert hashlib.sha256(program.read_bytes()).hexdigest()==job['program_sha256']
    assert len(job['results'])==1
    result=job['results'][0];assert not result['error'];rawpath=path.parent/f"result_{result['index']}.txt";raw=rawpath.read_bytes()
    digest=hashlib.sha256(raw).hexdigest();assert digest==result['raw_sha256']
    # Positive tick labels round indices only; explicit noise below uses actual u.
    spec=replace(base,schedule=Schedule.rounds(u if u else 1.,n),shots=count)
    syn,data=bits_from_shots(unpack_hardware(json.loads(raw),count,n),n,4,9);rec=record_from_bits(spec,syn,data)
    assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(data[:,[0,3,6]],axis=1))
    dem=dem_for(paper_graph(spec,P_EXT,0,P_READ),noise=round_probabilities(n,u))
    dempath=DEMS/f"T{int(total)}_n{n}.dem"
    if dempath.exists():assert dempath.read_text()==dem
    dempath.write_text(dem)
    pred=PyMatchingDecoder(dem).decode_batch(rec.detectors);fail=np.any(pred!=rec.observables,axis=1)
    olddem=dem_for(paper_graph(spec,.002,0,.001),noise=old_noise(n,u))
    oldpred=PyMatchingDecoder(olddem).decode_batch(rec.detectors);oldfail=np.any(oldpred!=rec.observables,axis=1)
    historical=path.parent/'analysis.json'
    if historical.exists():assert json.loads(historical.read_text())['logical_failures']==int(oldfail.sum())
    row=dict(job_id=jid,provider_id=job['job'].get('providerId'),job_record=str(path),raw_path=str(rawpath),raw_sha256=digest,program_sha256=job['program_sha256'],rounds=n,shots=count,interval_seconds=u,total_requested_sleep_seconds=total,logical_failures=int(fail.sum()),old_decoder_failures=int(oldfail.sum()),changed_predictions=int(np.any(pred!=oldpred,axis=1).sum()),corrected=int((oldfail & ~fail).sum()),harmed=int((~oldfail & fail).sum()),data_bit_errors=int(data.sum()),dem_path=str(dempath),dem_sha256=hashlib.sha256(dem.encode()).hexdigest())
    batchrows.append(row);groups[(total,n)].append((row,data,fail,oldfail))
    arrays[jid+'_failure']=fail;arrays[jid+'_prediction']=pred[:,0]
rows=[];rng=np.random.default_rng(20261113)
for (total,n),batches in sorted(groups.items()):
    data=np.concatenate([b[1] for b in batches]);shots=len(data);k=sum(b[0]['logical_failures'] for b in batches)
    hist=np.bincount(data.sum(axis=1).astype(int),minlength=10)
    boot=rng.multinomial(shots,hist/shots,size=20000)@np.arange(10)/(shots*9)
    r=dict(rounds=n,total_requested_sleep_seconds=total,interval_seconds=total/(n-1),shots=shots,jobs=len(batches),logical_failures=k,logical_error_probability=k/shots,logical_wilson_95=wilson(k,shots),raw_data_bit_errors=int(data.sum()),data_bits=int(data.size),raw_data_error_probability=float(data.mean()),raw_data_shot_bootstrap_95=np.quantile(boot,[.025,.975]).tolist(),per_qubit_error_counts=data.sum(axis=0).tolist(),old_decoder_failures=sum(b[0]['old_decoder_failures'] for b in batches),changed_predictions=sum(b[0]['changed_predictions'] for b in batches),corrected=sum(b[0]['corrected'] for b in batches),harmed=sum(b[0]['harmed'] for b in batches),job_ids=[b[0]['job_id'] for b in batches])
    rows.append(r)
assert len(seen)==16 and sum(r['shots'] for r in rows)==10750
sweep=[r for r in rows if r['total_requested_sleep_seconds']==1];controls=[r for r in rows if r['total_requested_sleep_seconds']==0]
assert sum(r['shots'] for r in sweep)==9750
out=dict(platform='nexus:H2-2',distance=3,basis='X',decoder_policy=POLICY,total_unique_jobs=16,total_shots=10750,fixed_T1_shots=9750,control_shots=1000,no_postselection=True,uncertainty='Wilson 95% for logical probabilities; whole-shot bootstrap 95% for raw bit probabilities. Conditional on frozen decoder, no drift/model uncertainty.',calibration_note='p_ext was selected from the zero-sleep control; that control is not independent validation of its selected parameter.',versions={x:version(x) for x in ['numpy','stim','pymatching']},fixed_T1_rows=sweep,zero_sleep_controls=controls,batches=batchrows)
OUT.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');np.savez_compressed(OUT.with_suffix('.npz'),**arrays)
lines=['# Physical H2-2: all shots with updated sleep-dependent decoder','',f"16 unique jobs, 10,750 shots: 9,750 at total requested sleep T=1 s; 1,000 zero-sleep control shots. p_ext={P_EXT}, p_read={P_READ}. All other decoder constants unchanged. Historical results preserved.",'','| N | u (s) | Shots | Logical failures | Logical error | 95% Wilson | Raw bits / total | Raw error |','|---:|---:|---:|---:|---:|---:|---:|---:|']
for r in sweep:
    lo,hi=r['logical_wilson_95'];lines.append(f"| {r['rounds']} | {r['interval_seconds']:.6g} | {r['shots']} | {r['logical_failures']} | {100*r['logical_error_probability']:.3g}% | {100*lo:.3g}–{100*hi:.3g}% | {r['raw_data_bit_errors']} / {r['data_bits']} | {100*r['raw_data_error_probability']:.3g}% |")
lines+=['','Zero-sleep control: '+str(controls),'','Ranges reflect shot sampling only. The sample minimum does not establish a unique optimum. Control shots are excluded from the fixed-T curve. The control informed p_ext and is not independent validation. JSON records job/raw/program/DEM provenance; NPZ stores per-shot failures and predictions.']
OUT.with_suffix('.md').write_text('\n'.join(lines)+'\n')
for r in rows:print(json.dumps(r),flush=True)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
fig,axes=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
ordered=sorted(sweep,key=lambda r:r['interval_seconds']);x=np.array([r['interval_seconds'] for r in ordered])
for ax,field,ci,title,color in [(axes[0],'raw_data_error_probability','raw_data_shot_bootstrap_95','Raw final data-bit errors','#176baf'),(axes[1],'logical_error_probability','logical_wilson_95','Decoded logical errors','#ad541b')]:
    y=np.array([r[field] for r in ordered]);bounds=np.array([r[ci] for r in ordered])
    ax.errorbar(x,y,yerr=np.maximum([y-bounds[:,0],bounds[:,1]-y],0),fmt='o',mfc='white',color=color,capsize=3)
    ax.set_xscale('log');ax.set_xticks(x,[f'{v:.3g}' for v in x],rotation=40)
    ax.set_xlabel('Requested sleep interval (s)');ax.set_ylabel('Error probability');ax.set_title(title)
    ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,max(bounds[:,1])*1.3);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
    for i,r in enumerate(ordered):
        ax.annotate(f"N={r['rounds']}",(x[i],bounds[i,1]),xytext=(0,5),textcoords='offset points',ha='center',fontsize=8)
fig.suptitle('Physical H2-2 · d=3 X-memory · 9,750 shots · total requested sleep 1 s\nSleep-dependent MWPM: p_ext=0.00117 · 95% sampling intervals',fontsize=12)
fig.savefig(OUT.with_suffix('.png'),dpi=180)
