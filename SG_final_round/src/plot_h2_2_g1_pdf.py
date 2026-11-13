"""Render the saved fixed-g hardware fit in the emulator report style."""
import json
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
ROOT=Path(__file__).resolve().parents[1]
r=json.loads((ROOT/'results/h2_2_d3_g1_linear_quadratic_fit.json').read_text())
assert r['g']==1 and r['distance']==3 and r['p_ext']==.00117
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False,'pdf.fonttype':42})
fig,ax=plt.subplots(figsize=(8.27,11.69));fig.subplots_adjust(left=.13,right=.96,top=.70,bottom=.32)
fig.suptitle('Observed logical errors and fitted curve',fontsize=17,fontweight='bold',y=.975)
fig.text(.5,.91,'Physical H2-2 X-memory | d = 3 | 9,750 shots\nTotal requested sleep T = 1 s | Sleep-dependent MWPM decoding',ha='center',fontsize=11,linespacing=1.6)
fig.text(.13,.845,'Logical error model',fontsize=12,fontweight='bold')
fig.text(.13,.80,r'$P_L(d,u)=\frac{T}{u}C\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}\,q(u)\right]^{g(d+1)/2}$',fontsize=15)
fig.text(.13,.762,r'$q(u)=au+bu^2$, where $u=\Delta t$ is the sleep interval.',fontsize=11)
rows=r['rows'];u=np.array([x['interval_seconds'] for x in rows]);p=np.array([x['logical_error_probability'] for x in rows]);ci=np.array([x['logical_wilson_95'] for x in rows]);color='#176baf'
def curve(t):return r['C']/t*(1+r['lambda_1']*t+r['lambda_2']*t*t)**2
ax.errorbar(u,p,yerr=[p-ci[:,0],ci[:,1]-p],fmt='o',color=color,mfc='none',mew=1.2,ms=5,capsize=3,elinewidth=1.1,label='Observed data (95% Wilson interval)',zorder=3)
grid=np.geomspace(min(u),max(u),1000);ax.plot(grid,curve(grid),color=color,lw=2.2,label='Fit with g = 1')
star=r['delta_t_star_seconds'];ax.axvline(star,color=color,ls='--',lw=1.2)
ax.annotate(f'Δt* = {star:.5f} s',xy=(star,0),xycoords=ax.get_xaxis_transform(),xytext=(0,-21),textcoords='offset points',ha='center',va='top',fontsize=11,color=color)
ax.set_xscale('log');ax.set_xlim(.022,1.13);ax.set_ylim(0,.09);ax.set_xticks([.025,.05,.1,.2,.5,1],['0.025','0.05','0.1','0.2','0.5','1']);ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.set_yticks([0,.02,.04,.06,.08]);ax.grid(alpha=.18);ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)',labelpad=32);ax.set_ylabel('Logical error probability');ax.set_title('d = 3 | Physical H2-2',loc='left',fontsize=15,fontweight='bold',pad=8);ax.legend(loc='upper center',fontsize=10,frameon=False)
lo,hi=r['delta_t_star_conditional_95_seconds']
fig.text(.13,.215,f"Fitted   a = {r['a_per_second']:.8f} s⁻¹     b = {r['b_per_second_squared']:.8f} s⁻²\n            C = {r['C']:.10f}\nFixed    g = 1     d = 3     p_ext = {r['p_ext']:.5f}",fontsize=11,va='top',linespacing=1.6)
fig.text(.13,.127,f'Δt* = {star:.5f} s (conditional 95% bootstrap: {lo:.5f}-{hi:.5f} s)\nFitted minimum logical error = {100*r["minimum_fitted_probability"]:.3f}%\nBinomial deviance = {r["binomial_deviance"]:.3f}; nominal df = 5; bootstrap GOF p = {r["parametric_bootstrap_gof_p"]:.3f}',fontsize=10,va='top',linespacing=1.6)
fig.text(.13,.035,'All eight fixed-T settings included; zero-sleep control excluded.\nIntervals condition on the model and fixed parameters; calibration and drift uncertainty\nare excluded. Fitted a and b are effective coefficients, not calibrated physical idle rates.',fontsize=9,color='#444444',linespacing=1.5)
out=ROOT.parent/'output/pdf/h2_2_d3_g1_fixed_fit.pdf';out.parent.mkdir(parents=True,exist_ok=True);fig.savefig(out);fig.savefig(out.with_suffix('.png'),dpi=180);print(out)
