"""Decode refinement shots and plot the combined fixed-sleep dataset."""
import json,hashlib
from dataclasses import replace
import numpy as np
import fixed_sleep_d3 as f
from analyze_d3_sleep_sweep import unpack
from analyze_single_qubit_pilot import wilson
from qec_timing.hardware.providers import _register_builtins
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.records import bits_from_shots,record_from_bits
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder


def load_batch(run,name,n,expected):
 dest=run/'execute'/name
 job=json.loads((dest/'job.json').read_text())
 assert f.accepted(job) and job['shots']==expected and job['rounds']==n
 path=dest/'result_0.txt'
 col=json.loads((run/'collection_status.json').read_text())
 row=next(x for x in col['jobs'] if x['name']==name)
 digest=hashlib.sha256(path.read_bytes()).hexdigest()
 assert digest==row['raw_sha256']['result_0.txt']
 return unpack(json.loads(path.read_text()),shots=expected,n_rounds=n),dict(job_id=job['job_id'],shots=expected,result_sha256=digest)


def main():
 _register_builtins()
 oldrun=f.RUNS
 original=json.loads((f.ROOT/'results/d3_fixed_sleep_500.json').read_text())
 rows=[r for r in original['rows'] if r['rounds']!=5]
 base=spec_from_json(json.loads(f.SOURCE.with_suffix('.json').read_text())['spec'])
 f.configure_refinement()
 for p in f.PLAN:
  n=p['rounds'];newshots=500 if n==5 else 1000
  shots,meta=load_batch(f.RUNS,f'n{n}_part1',n,newshots)
  sources=[meta]
  if n==5:
   old,meta=load_batch(oldrun,'n5_part1',n,500)
   shots=old+shots;sources.insert(0,meta)
  assert len(shots)==1000
  spec=replace(base,schedule=Schedule.rounds(1/(n-1),n),shots=1000)
  syn,dat=bits_from_shots(shots,n,4,9);rec=record_from_bits(spec,syn,dat)
  counts={}
  for p_data in [.002,.02,.1]:
   dem=dem_for(paper_graph(spec,p_data,0,.001))
   (f.BUILD/f'decoder_n{n}_p{p_data}.dem').write_text(dem)
   pred=PyMatchingDecoder(dem).decode_batch(rec.detectors)
   counts[str(p_data)]=int(np.any(pred!=rec.observables,axis=1).sum())
  k=counts['0.002']
  rows.append(dict(rounds=n,delta_t_seconds=1/(n-1),shots=1000,logical_failures=k,
   logical_error_probability=k/1000,wilson_95=wilson(k,1000),decoder_sensitivity_failures=counts,
   mean_data_error=float(dat.mean()),sources=sources,job_ids=[m['job_id'] for m in sources]))
 rows.sort(key=lambda r:r['delta_t_seconds'])
 result=dict(platform='nexus:H2-1E',distance=3,basis='X',total_requested_sleep_seconds=1,
  extraction_duration_neglected=True,parallel_sleep_verified=False,
  primary_decoder='phenomenological MWPM p_data=.002 per round, p_read=.001, lambda=0; not calibrated gate-level DEM',rows=rows)
 out=f.ROOT/'results/d3_fixed_sleep_combined.json'
 out.write_text(json.dumps(result,indent=2)+'\n')
 lines=['# d=3 fixed requested sleep: combined refinement results','',
  'H2-1E; total requested sleep one second. Extraction duration neglected. Fixed phenomenological PyMatching decoder, p_data=.002, p_read=.001, lambda=0. These are decoder assumptions, not injected noise.','',
  '| N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |',
  '|---|---:|---:|---:|---:|']
 for r in rows:
  lo,hi=r['wilson_95'];lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.9g} | {r['logical_failures']} / {r['shots']} | {100*r['logical_error_probability']:.2f}% | {100*lo:.2f}% - {100*hi:.2f}% |")
 best=min(rows,key=lambda r:r['logical_error_probability'])
 lines+=['',f"Lowest observed probability: N={best['rounds']}, Delta t={best['delta_t_seconds']:.9g} s. This does not establish a unique optimal interval.",'',
  'N=5 pools only its original fixed-sleep 500 shots with the new 500 shots; N=4,6,7,8 use new 1,000-shot batches. N=2,10,20,40 retain original 500-shot results, with both N=40 partitions included. No data are counted twice. All new/refinement packed shots match formatted counts and saved hashes. The original coarse analysis is unchanged. Error bars reflect shot sampling, not systematic decoder mismatch, scheduling uncertainty or run-to-run drift. The refinement was selected after the coarse sweep; minimum comparisons are exploratory.']
 (f.ROOT/'results/d3_fixed_sleep_combined.md').write_text('\n'.join(lines)+'\n')
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.ticker import PercentFormatter
 plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
 fig,ax=plt.subplots(figsize=(10,6),layout='constrained')
 ax.plot([r['delta_t_seconds'] for r in rows],[r['logical_error_probability'] for r in rows],color='#78909c',linestyle='--',linewidth=1.4,label='Guide to the eye',zorder=1)
 for nshots,color,marker in [(1000,'#15689b','o'),(500,'#7a4d94','s')]:
  vals=[r for r in rows if r['shots']==nshots]
  ax.errorbar([r['delta_t_seconds'] for r in vals],[r['logical_error_probability'] for r in vals],yerr=[[r['logical_error_probability']-r['wilson_95'][0] for r in vals],[r['wilson_95'][1]-r['logical_error_probability'] for r in vals]],fmt=marker,color=color,capsize=4,elinewidth=1.5,markersize=7,label=f'{nshots:,} shots per setting',zorder=3)
 for r in rows:
  ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,9),textcoords='offset points',ha='center',fontsize=10)
 ax.set_xscale('log');ax.minorticks_off()
 ax.set_xticks([1/39,1/19,1/9,1/7,1/6,.2,.25,1/3,1]);ax.set_xticklabels(['0.02564','0.05263','0.1111','0.1429','0.1667','0.2','0.25','0.3333','1'],rotation=40,ha='right')
 ax.set_xlim(.020,1.35);ax.set_ylim(0,.18);ax.set_yticks(np.arange(0,.181,.02));ax.yaxis.set_major_formatter(PercentFormatter(1))
 ax.grid(axis='y',alpha=.2)
 ax.set_xlabel('Sleep interval Δt (seconds; logarithmic axis)');ax.set_ylabel('Decoded logical error probability')
 ax.set_title('d=3 X-memory on H2-1E: combined coarse and refinement results\nFixed total requested sleep: 1 second',loc='left',fontsize=14,pad=16)
 ax.legend(loc='upper center',frameon=False,fontsize=10)
 fig.text(.5,-.025,'Error bars: 95% Wilson intervals. Extraction duration neglected. Connecting line is not a fitted model.',ha='center',fontsize=9,color='#4c5660')
 path=f.ROOT/'results/figures/d3_fixed_sleep_combined'
 fig.savefig(path.with_suffix('.png'),dpi=190,bbox_inches='tight');fig.savefig(path.with_suffix('.svg'),bbox_inches='tight')
 for r in sorted(rows,key=lambda r:r['rounds']):print(r['rounds'],r['logical_failures'],r['shots'],r['wilson_95'],r['decoder_sensitivity_failures'])


if __name__=='__main__':main()
