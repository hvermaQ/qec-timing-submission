"""Compare fixed and sleep-dependent decoding on the same pooled d=5 shots."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter,NullFormatter
ROOT=Path(__file__).resolve().parents[1]
d=json.loads((ROOT/'results/d5_sleep_dependent_redecode.json').read_text())
rows=sorted([r for r in d['rows'] if r['total_requested_sleep_seconds']==1],key=lambda r:r['delta_t_seconds'])
fig,axes=plt.subplots(1,2,figsize=(11.5,4.8),layout='constrained')
for ax,zoom in zip(axes,[False,True]):
 selected=[r for r in rows if not zoom or r['rounds']>=4]
 x=np.array([r['delta_t_seconds'] for r in selected])
 for field,interval,color,marker,label in [('fixed_probability','fixed_wilson_95','#8b9299','s','Fixed DEM'),('sleep_probability','sleep_wilson_95','#147c68','o','Sleep-dependent DEM')]:
  y=np.array([r[field] for r in selected]);lo=np.array([r[interval][0] for r in selected]);hi=np.array([r[interval][1] for r in selected])
  assert np.all(lo<=y) and np.all(y<=hi)
  ax.errorbar(x,y,yerr=[y-lo,hi-y],fmt=marker,color=color,mfc='white' if marker=='s' else color,ms=5.5,capsize=3,elinewidth=1,label=label,alpha=.9,zorder=2 if marker=='s' else 3)
 for r in selected:
  if not zoom and r['rounds']>=7:continue
  ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],max(r['fixed_wilson_95'][1],r['sleep_wilson_95'][1])),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
 ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.18);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
 ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability per experiment')
 if zoom:
  ax.set_xlim(.10,.36);ax.set_ylim(0,max(max(r['fixed_wilson_95'][1],r['sleep_wilson_95'][1]) for r in selected)*1.25);ax.set_title('Intermediate intervals',loc='left',fontsize=11)
 else:
  ax.set_xscale('log');ax.set_xlim(.095,1.15);ax.set_ylim(0,.21);ax.set_xticks([1/9,1/6,.25,.5,1]);ax.set_xticklabels(['0.111','0.167','0.25','0.50','1.00']);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_title('Full range · logarithmic horizontal axis',loc='left',fontsize=11);ax.legend(frameon=False,fontsize=9,loc='upper left')
fig.suptitle('d=5 H2-1E · same pooled 7,667 shots · T_sleep=1 s',fontweight='bold',fontsize=14)
fig.supxlabel('95% Wilson intervals; decoder and batch uncertainty are excluded.',fontsize=9)
for suffix in ['png','svg']:fig.savefig(ROOT/f'results/figures/d5_sleep_dependent_comparison.{suffix}',dpi=220)
print('Plot uses',sum(r['shots'] for r in rows),'shots')
