"""Plot reviewed d=5, T_sleep=1 s logical probabilities without fitting a curve."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter,NullFormatter

ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'results/d5_h2_1e_sleep_logical_probabilities.json'
d=json.loads(source.read_text())
rows=sorted([r for r in d['rows'] if r['total_requested_sleep_seconds']==1 and 2<=r['rounds']<=10],key=lambda r:r['delta_t_seconds'])
assert {r['rounds'] for r in rows}==set(range(2,11))
fig,axes=plt.subplots(1,2,figsize=(11,4.6),layout='constrained')
for ax,zoom in zip(axes,[False,True]):
 selected=[r for r in rows if not zoom or r['rounds']>=4]
 x=np.array([r['delta_t_seconds'] for r in selected]);y=np.array([r['logical_error_probability'] for r in selected])
 lo=np.array([r['wilson_95'][0] for r in selected]);hi=np.array([r['wilson_95'][1] for r in selected])
 assert np.all(lo<=y) and np.all(y<=hi)
 ax.errorbar(x,y,yerr=[y-lo,hi-y],fmt='o',markersize=5.5,capsize=3,color='#176385',label='Measurements; 95% Wilson intervals')
 for r in selected:
  if not zoom and r['rounds']>=7:continue
  ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
 ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.18);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
 ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability per experiment')
 if zoom:
  ax.set_xlim(.10,.36);ax.set_ylim(0,max(hi)*1.3);ax.set_title('Near the expected minimum',loc='left',fontsize=11)
 else:
  ax.set_xscale('log');ax.set_xlim(.095,1.15);ax.set_ylim(0,max(hi)*1.18);ax.set_xticks([.111111,.166667,.25,.5,1]);ax.set_xticklabels(['0.111','0.167','0.25','0.50','1.00']);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_title('Full range · logarithmic horizontal axis',loc='left',fontsize=11)
  ax.legend(frameon=False,fontsize=8,loc='upper left')
fig.suptitle('d=5 H2-1E · total requested sleep T=1 s',fontweight='bold',fontsize=14)
figures=ROOT/'results/figures';figures.mkdir(exist_ok=True)
for suffix in ['png','svg']:fig.savefig(figures/f'd5_h2_1e_t1_n2_to_n10.{suffix}',dpi=220)
summary=dict(source=str(source),total_requested_sleep_seconds=1,total_shots=sum(r['shots'] for r in rows),total_failures=sum(r['logical_failures'] for r in rows),rows=rows,primary_decoder=d['primary_decoder'])
(ROOT/'results/d5_h2_1e_t1_n2_to_n10.json').write_text(json.dumps(summary,indent=2)+'\n')
print('T=1 s:',summary['total_shots'],'shots;',summary['total_failures'],'failures')
