"""Offline sensitivity audit of saved H2-2 shots; no parameter selection/training."""
import ast
import hashlib
import itertools
import json
from collections import Counter
from dataclasses import replace
from pathlib import Path
import numpy as np
from build_sleep_probe import SOURCE
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.noise.base import RoundNoise
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/h2_2_decoder_sensitivity'
# Reuse the validated hardware unpacker without executing the batch analysis.
source=ROOT/'runs/h2_2_hardware_d3_x_t1_20261111/analyze.py'
node=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='unpack_hardware')
exec(compile(ast.Module(body=[node],type_ignores=[]),str(source),'exec'))
_register_builtins()
base=spec_from_json(json.loads(SOURCE.with_suffix('.json').read_text())['spec'])
pooled=json.loads((ROOT/'results/h2_2_hardware_d3_all_shots.json').read_text())
records={}; provenance=[]; seen=set()
for row in pooled['rows']:
    n=row['rounds'];u=row['interval_seconds'];allshots=[]
    for batch in row['batches']:
        folder=ROOT/'runs'/batch['batch']/f'n{n}'
        job=json.loads((folder/'job.json').read_text())
        assert job['job_id'] not in seen;seen.add(job['job_id'])
        result=job['results'][0];path=folder/f"result_{result['index']}.txt";raw=path.read_bytes()
        assert hashlib.sha256(raw).hexdigest()==result['raw_sha256']==batch['raw_sha256']
        allshots.extend(unpack_hardware(json.loads(raw),job['shots'],n))
        provenance.append(dict(job_id=job['job_id'],raw_path=str(path),raw_sha256=result['raw_sha256']))
    spec=replace(base,schedule=Schedule.rounds(u,n),shots=row['shots'])
    syn,data=bits_from_shots(allshots,n,4,9)
    rec=record_from_bits(spec,syn,data)
    reference=(ROOT/f'results/decoders/d3_sleep_dependent/n{n}.dem').read_text()
    baseline=PyMatchingDecoder(reference).decode_batch(rec.detectors)
    assert int(np.any(baseline!=rec.observables,axis=1).sum())==row['logical_failures']
    records[n]=(spec,rec,baseline)
assert len(seen)==10
# Independently vary four effective controls. Frequency multiplier is held at 2:
# nu and multiplier cannot be separately identified by this model.
factors=[.25,.5,1.,2.,4.]
configs=[dict(name='grid',p_ext=.002*a,p_syndrome=.001*b,p_final=.001*b,r=.0028*c,nu=.043*d,factors=[a,b,c,d]) for a,b,c,d in itertools.product(factors,repeat=4)]
configs += [dict(name='no_idle',p_ext=.002,p_syndrome=.001,p_final=.001,r=0.,nu=0.,factors=None)]
for which in ['syndrome','final']:
    for f in [.25,.5,2.,4.]:
        configs.append(dict(name=f'{which}_readout_only_x{f}',p_ext=.002,p_syndrome=.001*(f if which=='syndrome' else 1),p_final=.001*(f if which=='final' else 1),r=.0028,nu=.043,factors=None))
results=[];predictions=[]
for idx,c in enumerate(configs):
    rows=[];preds=[]
    for n,(spec,rec,baseline) in records.items():
        u=1/(n-1);lin=c['r']*u;quad=np.sin(np.pi*c['nu']*2*u)**2
        idle=lin+quad-2*lin*quad;p=c['p_ext']+idle-2*c['p_ext']*idle
        graph=paper_graph(spec,c['p_ext'],0,c['p_final'])
        noise=[RoundNoise(c['p_ext'],c['p_syndrome'])]+[RoundNoise(p,c['p_syndrome'])]*(n-1)
        dem=dem_for(graph,noise=noise)
        pred=PyMatchingDecoder(dem).decode_batch(rec.detectors)
        fail=np.any(pred!=rec.observables,axis=1);oldfail=np.any(baseline!=rec.observables,axis=1)
        if c['factors']==[1.,1.,1.,1.]:
            assert dem==(ROOT/f'results/decoders/d3_sleep_dependent/n{n}.dem').read_text()
            assert np.array_equal(pred,baseline)
        rows.append(dict(rounds=n,shots=len(fail),failures=int(fail.sum()),probability=float(fail.mean()),changed_predictions=int(np.any(pred!=baseline,axis=1).sum()),corrected=int((oldfail & ~fail).sum()),harmed=int((~oldfail & fail).sum()),dem_sha256=hashlib.sha256(dem.encode()).hexdigest()))
        preds.append(pred[:,0])
    minimum=min(r['probability'] for r in rows)
    results.append(dict(index=idx,parameters=c,rows=rows,sample_minimum_N=[r['rounds'] for r in rows if r['probability']==minimum]))
    predictions.append(np.concatenate(preds))
    if idx%100==0: print('Decoded configurations',idx+1,flush=True)
summary=[]
for j,row in enumerate(pooled['rows']):
    ns=[]
    for label,subset in [('moderate', [x for x in results if x['parameters']['factors'] and all(.5<=f<=2 for f in x['parameters']['factors'])]),('broad',[x for x in results if x['parameters']['name']=='grid'])]:
        values=[x['rows'][j] for x in subset]
        ns.append(dict(range=label,configurations=len(values),minimum_failures=min(v['failures'] for v in values),maximum_failures=max(v['failures'] for v in values),max_changed_predictions=max(v['changed_predictions'] for v in values)))
    summary.append(dict(rounds=row['rounds'],shots=row['shots'],baseline_failures=row['logical_failures'],ranges=ns))
output=dict(description='Exploratory offline sensitivity; parameter ranges are stress tests, not calibrated confidence regions. No optimization or adoption of a decoder.',total_shots=6750,grid_factors=factors,frequency_multiplier=2,provenance=provenance,summary=summary,configurations=results)
OUT.with_suffix('.json').write_text(json.dumps(output,indent=2)+'\n')
np.savez_compressed(OUT.with_suffix('.npz'),predictions=np.asarray(predictions,dtype=bool),rounds=np.array(list(records)),shots=np.array([r['shots'] for r in pooled['rows']]))
print(json.dumps(summary,indent=2))
print('Minimum counts:',Counter(tuple(x['sample_minimum_N']) for x in results if x['parameters']['name']=='grid'))

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
fig,ax=plt.subplots(figsize=(8,4.8),layout='constrained')
x=np.arange(len(summary));shots=np.array([r['shots'] for r in summary])
for rangeidx,color,label in [(0,'#82b1d5','Joint factors 0.5–2 (81 combinations)')]:
    lo=np.array([r['ranges'][rangeidx]['minimum_failures'] for r in summary])/shots
    hi=np.array([r['ranges'][rangeidx]['maximum_failures'] for r in summary])/shots
    ax.vlines(x,lo,hi,color=color,lw=16 if rangeidx==1 else 8,label=label)
y=np.array([r['baseline_failures'] for r in summary])/shots
ax.plot(x,y,'o',color='#172c40',label='Frozen decoder')
ax.set_xticks(x,[f"N={r['rounds']}\n{1/(r['rounds']-1):.3g} s" for r in summary])
ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylabel('Logical error probability');ax.set_xlabel('Extraction rounds and requested sleep interval')
ax.set_title('H2-2 · d=3 X-memory · decoder sensitivity on 6,750 saved shots')
ax.plot(x,[next(c for c in results if c['parameters']['name']=='no_idle')['rows'][j]['probability'] for j in range(len(summary))], 'x', color='#bd5c25',label='No idle contribution');ax.legend(frameon=False);ax.grid(axis='y',alpha=.2);ax.spines[['top','right']].set_visible(False)
fig.subplots_adjust(bottom=.23) if not fig.get_constrained_layout() else None
fig.text(.5,-.045,'Ranges show parameter sensitivity, not statistical confidence intervals. No additional hardware runs.',ha='center',fontsize=9)
fig.savefig(OUT.with_suffix('.png'),dpi=180,bbox_inches='tight')
