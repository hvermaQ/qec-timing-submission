"""Physical H2-2 g=1 fits, preserving observed counts and fixed policies."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
ROOT=Path(__file__).resolve().parents[1]
d3=json.loads((ROOT/'results/h2_2_d3_g1_linear_quadratic_fit.json').read_text())
d5all=json.loads((ROOT/'results/h2_2_d5_skip5_g1_rounded_n10_fit.json').read_text());d5=d5all['exact_count_sensitivity_fit']
r5=json.loads((ROOT/'results/d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json').read_text())['rows']+[json.loads((ROOT/'runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json').read_text())]
plt.rcParams.update({'font.size':10.5,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig=plt.figure(figsize=(8.27,11.69))
fig.suptitle('Observed logical errors and fitted curves',fontsize=17,fontweight='bold',y=.978)
fig.text(.5,.943,'Physical H2-2 X-memory | Total requested sleep T = 1 s\nSleep-dependent MWPM decoding',ha='center',va='top',fontsize=11,linespacing=1.5)
fig.text(.13,.887,'Logical error model',fontsize=12,fontweight='bold')
fig.text(.13,.849,r'$P_L(d,u)=\frac{C}{u}\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}(au+bu^2)\right]^{g(d+1)/2}$',fontsize=16)
fig.text(.13,.813,r'$u=\Delta t=T/(N-1)$ in seconds; $g=1$; $a,b\geq0$. $C$ absorbs fixed $T=1$ s.',fontsize=10)
for d,fit,rows,pe,color,box in [(3,d3,d3['rows'],.00117,'#176baf',[.13,.565,.83,.18]),(5,d5,r5,.005,'#c45b19',[.13,.18,.83,.18])]:
 ax=fig.add_axes(box);u=np.array([r['interval_seconds'] for r in rows]);p=np.array([r['logical_error_probability'] for r in rows]);ci=np.array([r['logical_wilson_95'] for r in rows])
 assert all(r['decoder_policy']['p_ext']==pe for r in rows) if d==5 else True
 def curve(t):return fit['C']/t*(1+fit['lambda_1']*t+fit['lambda_2']*t*t)**((d+1)/2)
 grid=np.geomspace(.1 if d==5 else .025,1,1000);star=fit['delta_t_star_seconds'];minimum=fit['minimum_fitted_probability']
 assert abs(float(curve(star))-minimum)<1e-10
 ax.errorbar(u,p,yerr=[p-ci[:,0],ci[:,1]-p],fmt='o',mfc='none',color=color,mew=1.2,ms=5,capsize=3,elinewidth=1.1,label='Observed data (95% Wilson interval)',zorder=3)
 ax.plot(grid,curve(grid),lw=2.2,color=color,label='Fit with g = 1')
 ax.axvline(star,color=color,ls='--',lw=1.2)
 ax.annotate(f'Δt* = {star:.5f} s',xy=(star,0),xycoords=ax.get_xaxis_transform(),xytext=(0,-17),textcoords='offset points',ha='center',va='top',fontsize=10,color=color)
 ax.set_xscale('log');ax.set_xlim(.022,1.13);ax.set_ylim(0,.12 if d==3 else .06)
 ax.set_xticks([.025,.05,.1,.2,.5,1]);ax.set_xticklabels(['0.025','0.05','0.1','0.2','0.5','1'])
 ax.set_yticks([0,.04,.08,.12] if d==3 else [0,.02,.04,.06]);ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.grid(alpha=.18)
 ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)',labelpad=29);ax.set_ylabel('Logical error probability')
 shots=sum(r['shots'] for r in rows);title=f'd = {d} | {shots:,} shots'
 ax.set_title(title,loc='left',fontweight='bold',fontsize=14,pad=9);ax.legend(loc='upper left',frameon=False,fontsize=9)
 y=box[1]-(.079 if d==5 else .091)
 summary=(
  rf"Fitted   $C={fit['C']:.8f}\,\mathrm{{s}}$    $a={fit['a_per_second']:.8f}\,\mathrm{{s}}^{{-1}}$    $b={fit['b_per_second_squared']:.8f}\,\mathrm{{s}}^{{-2}}$"
  + '\n' + rf"Fixed    $g=1$    $p_{{\mathrm{{ext}}}}={pe:g}$    $p_{{\mathrm{{read}}}}=0.001$"
  + '\n' + rf"Optimum   $\Delta t^*={star:.5f}\,\mathrm{{s}}$    $P_L(\Delta t^*)={100*minimum:.4f}\%$"
 )
 fig.text(.13,y,summary,fontsize=9.7,va='top',linespacing=1.6)
fig.text(.13,.005,'All finite-sleep settings included; zero-sleep controls excluded. d=5 N=10: 2/160 = 1.25%.\nShot-count binomial fits; dashed lines mark analytical minima. No postselection.\nOptima are model-dependent; fitted idle coefficients are effective, not calibrated physical rates.',fontsize=8.7,color='#444444',linespacing=1.4)
out=ROOT/'outputs/h2_2_d3_d5_skip5_g1_fitted_curves.pdf';out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out);plt.close(fig);print(out)
