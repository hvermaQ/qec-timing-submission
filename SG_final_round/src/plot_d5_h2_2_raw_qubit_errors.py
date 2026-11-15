"""Plot all 25 final-data raw error probabilities for the physical H2-2 sweep."""
import hashlib
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from matplotlib.lines import Line2D

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/d5_h2_2_t1_p_ext_0_004_3500_shots.json'
OUT=ROOT/'results/figures/d5_h2_2_raw_error_by_qubit'
OUT.parent.mkdir(parents=True,exist_ok=True)
s=json.loads(SOURCE.read_text());rows=s['rows']
x=np.array([r['rounds'] for r in rows]);shots=np.array([r['shots'] for r in rows])
counts=np.array([r['data_bit_errors_by_qubit'] for r in rows]);p=counts/shots[:,None]
assert counts.shape==(5,25) and x.tolist()==[2,3,4,6,10]
assert np.array_equal(counts.sum(axis=1),[r['raw_data_bit_errors'] for r in rows])
assert np.allclose(p.mean(axis=1),[r['raw_data_error_probability'] for r in rows])
# Emphasis is descriptive: highlight qubits reaching at least 14%, not a test.
high=set(np.flatnonzero(p.max(axis=0)>=.14).tolist())
colors={i:plt.get_cmap('tab20')(i%20) for i in range(25)}
colors.update({5:'#d14936',6:'#167b8c',7:'#7c4ca5',2:'#d08b16',0:'#2763a2',15:'#48823c'})
markers=['o','s','^','D','v']
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(12.8,7.1));fig.subplots_adjust(left=.085,right=.76,top=.81,bottom=.24)
for q in sorted(range(25),key=lambda q:q in high):
 ax.plot(x,p[:,q],color=colors[q],marker=markers[q//5],markersize=5 if q in high else 3.5,lw=2.2 if q in high else 1,alpha=1 if q in high else .4,zorder=3 if q in high else 1)
ax.set_xticks(x,[f'{n}\n{1/(n-1):.3g} s' for n in x]);ax.set_xlabel('Extraction rounds N / requested sleep interval',labelpad=12)
ax.set_ylabel('Raw final-data error probability');ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,.53);ax.set_xlim(1.7,10.7)
ax.set_yticks(np.arange(0,.51,.05));ax.grid(axis='y',alpha=.18);ax.set_axisbelow(True)
# Direct labels emphasize the largest features without obscuring all 25 traces.
ax.annotate('Q5: 42–48% for N ≥ 3',xy=(6,p[3,5]),xytext=(5,.505),color=colors[5],fontsize=12,fontweight='bold',arrowprops=dict(arrowstyle='-',color=colors[5],lw=1.2))
ax.annotate('Q2: 21.2%',xy=(2,p[0,2]),xytext=(2.65,.275),color=colors[2],arrowprops=dict(arrowstyle='-',color=colors[2]))
for q,dy in [(6,7),(7,6),(15,-1),(0,-8)]:
 ax.annotate(f'Q{q}',xy=(10,p[-1,q]),xytext=(8,dy),textcoords='offset points',color=colors[q],fontweight='bold',fontsize=10)
handles=[Line2D([0],[0],color=colors[q],marker=markers[q//5],lw=2 if q in high else 1,alpha=1 if q in high else .5,markersize=5,label=f'Q{q}') for q in range(25)]
ax.legend(handles=handles,title='Data-qubit index',ncol=2,loc='upper left',bbox_to_anchor=(1.03,1.015),frameon=False,fontsize=9.5,columnspacing=1.2,handlelength=1.6,labelspacing=.8)
fig.text(.085,.94,'Physical H2-2 · d=5 · raw errors by data qubit',fontsize=18,fontweight='bold')
fig.text(.085,.885,'Total requested sleep T = 1 s · all 25 data qubits · no postselection',fontsize=11,color='#444444')
fig.text(.085,.05,'Shots at N = 2, 3, 4, 6, 10: 500, 750, 1,000, 750, 500. Raw rates do not depend on decoder settings.\nEach point is errors / shots for that qubit; lines guide the eye. Bold traces reach ≥14%; this is descriptive, not a statistical outlier test.',fontsize=9,color='#555555',linespacing=1.6)
for suffix in ['.png','.pdf']:fig.savefig(OUT.with_suffix(suffix),dpi=190)
OUT.with_suffix('.json').write_text(json.dumps(dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),rounds=x.tolist(),shots=shots.tolist(),counts=counts.tolist(),probabilities=p.tolist(),highlighted_qubits=sorted(high)),indent=2)+'\n')
print(OUT.with_suffix('.png'))
