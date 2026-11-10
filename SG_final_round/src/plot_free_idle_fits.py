"""Compare separate d=3 and d=5 free-idle fits and analytical minima."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,2,figsize=(15.8,7.8))
fig.subplots_adjust(left=.065,right=.98,top=.86,bottom=.35,wspace=.22)
styles={3:('#176baf','o'),5:('#c45b19','s')}
handles=[];labels=[]
for d in [3,5]:
 result=json.loads((ROOT/f'results/d{d}_free_idle_g_fit.json').read_text())
 color,marker=styles[d]
 rows=result['rows'];u=np.array([r['delta_t_seconds'] for r in rows]);p=np.array([r['logical_error_probability'] for r in rows])
 ci=np.array([r['wilson_95'] for r in rows]);err=np.array([p-ci[:,0],ci[:,1]-p])
 g=result['g'];a=result['a'];b=result['b'];pe=result['p_ext'];c=result['C'];l1=result['lambda_1'];l2=result['lambda_2'];star=result['delta_t_star']
 def curve(t):return c/t*(1+l1*t+l2*t*t)**(g*(d+1)/2)
 grid=np.geomspace(min(u),max(u),1200)
 for ax in axes:
  ax.errorbar(u,p,yerr=err,fmt=marker,color=color,mfc='white',mew=1.4,ms=6,capsize=3,elinewidth=1.1,zorder=3)
  line,=ax.plot(grid,curve(grid),color=color,lw=2.2)
  ax.axvline(star,color=color,ls='--',lw=1.2,alpha=.8)
  ax.plot(star,curve(star),marker='*',ms=15,color=color,mec='white',mew=.7,zorder=5)
 handles.append(line)
 labels.append(f'd = {d}  ({marker} data markers)\n'
               f'g = {g:.8f} (upper bound);  a = {a:.8e} s⁻¹ (≈ 0)\n'
               f'b = {b:.8f} s⁻²;  p_ext = {pe:.11f}\n'
               f'C = {c:.9f};  analytical Δt* = {star:.8f} s')
 axes[1].annotate(f'd = {d}: Δt* = {star:.5f} s',xy=(star,curve(star)),xytext=(.29,.030 if d==3 else .025),color=color,fontsize=10,arrowprops=dict(arrowstyle='->',color=color,lw=1),ha='left')
for ax in axes:
 ax.yaxis.set_major_formatter(PercentFormatter(1))
 ax.grid(alpha=.2)
 ax.set_xlabel('Sleep interval Δt (s)')
 ax.set_ylabel('Decoded logical error probability')
axes[0].set_xscale('log');axes[0].set_xlim(.022,1.12);axes[0].set_ylim(0,.18)
axes[0].set_title('All measured intervals',loc='left',fontweight='bold')
axes[1].set_xlim(.1,.55);axes[1].set_ylim(.005,.055)
axes[1].set_title('Detail around the fitted minima',loc='left',fontweight='bold')
fig.suptitle('H2-1E X-memory · d = 3 and d = 5\nFixed total requested sleep T = 1 s · sleep-dependent MWPM decoding',fontsize=16,y=.97)
fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.075),ncol=2,frameon=False,fontsize=10,handlelength=2.5,columnspacing=3)
fig.text(.5,.025,'Error bars: 95% Wilson intervals. Stars and dashed lines mark analytical minima.\nSeparate binomial fits; 0 < g < 1 and a, b ≥ 0. Both g estimates reach the numerical upper bound. Coefficients are effective logical-fit parameters.',ha='center',fontsize=9,color='#444444')
out=ROOT/'results/figures/d3_d5_free_idle_fit_comparison'
out.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(out.with_suffix('.png'),dpi=190)
fig.savefig(out.with_suffix('.pdf'))
print(out.with_suffix('.png'))
