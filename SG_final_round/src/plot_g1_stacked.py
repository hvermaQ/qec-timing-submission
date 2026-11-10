"""Refit at g=1 and create a portrait comparison with stacked panels."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares
from scipy.special import xlogy
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(2,1,figsize=(8.27,11.69))
fig.subplots_adjust(left=.13,right=.96,top=.76,bottom=.19,hspace=1.02)
results=[]
for ax,d,color in zip(axes,[3,5],['#176baf','#c45b19']):
 old=json.loads((ROOT/f'results/d{d}_free_idle_g_fit.json').read_text())
 rows=old['rows'];u=np.array([r['delta_t_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows]);p=k/n
 alpha=(d+1)/2
 def predict(x,t=u):
  c=np.exp(x[0]);l1,l2=np.expm1(x[1:])
  return c/t*(1+l1*t+l2*t*t)**alpha
 def residual(x):
  raw=predict(x);prob=np.clip(raw,1e-15,1-1e-15)
  dev=2*(xlogy(k,k/(n*prob))+xlogy(n-k,(n-k)/(n*(1-prob))))
  return np.r_[np.sign(prob-p)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
 fit=least_squares(residual,[np.log(old['C']),np.log1p(old['lambda_1']),np.log1p(old['lambda_2'])],bounds=([-40,0,0],[0,12,12]),ftol=1e-12,xtol=1e-12,gtol=1e-10)
 assert fit.success
 l1,l2=np.expm1(fit.x[1:]);pe=old['p_ext'];a,b=np.array([l1,l2])*pe/(1-2*pe)
 c1,c2=(alpha-1)*l1,(2*alpha-1)*l2
 star=2/(c1+np.sqrt(c1*c1+4*c2))
 grid=np.geomspace(min(u),max(u),1000)
 ci=np.array([r['wilson_95'] for r in rows]);err=np.array([p-ci[:,0],ci[:,1]-p])
 ax.errorbar(u,p,yerr=err,fmt='o',color=color,mfc='none',mew=1.2,ms=5,capsize=3,elinewidth=1.1,label='Observed data (95% interval)',zorder=3)
 ax.plot(grid,predict(fit.x,grid),color=color,lw=2.2,label='Fit with g = 1')
 ax.axvline(star,color=color,ls='--',lw=1.2)
 ax.annotate(f'Δt* = {star:.5f} s',xy=(star,0),xycoords=ax.get_xaxis_transform(),
             xytext=(0,-20),textcoords='offset points',ha='center',va='top',fontsize=11,color=color)
 ax.set_xscale('log');ax.set_xlim(.022,1.13);ax.set_ylim(0,.18)
 ax.set_xticks([.025,.05,.1,.2,.5,1]);ax.set_xticklabels(['0.025','0.05','0.1','0.2','0.5','1'])
 ax.yaxis.set_major_formatter(PercentFormatter(1,decimals=0));ax.set_yticks([0,.04,.08,.12,.16]);ax.grid(alpha=.18)
 ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)',labelpad=32);ax.set_ylabel('Logical error probability')
 ax.set_title(f'd = {d}  |  {sum(n):,} shots',loc='left',fontsize=15,fontweight='bold',pad=8)
 position=ax.get_position()
 fig.text(position.x0,position.y0-.09,
          f'Fitted   a ≈ 0 s⁻¹     b = {b:.8f} s⁻²     C = {np.exp(fit.x[0]):.9f}\n'
          f'Fixed    g = 1     p_ext = {pe:.11f}',
          fontsize=11,va='top',linespacing=1.5)
 ax.legend(loc='upper left',fontsize=10,frameon=False)
 results.append(dict(distance=d,g=1,a=float(a),b=float(b),p_ext=pe,C=float(np.exp(fit.x[0])),delta_t_star=float(star),deviance=float(np.sum(fit.fun**2))))
fig.suptitle('Observed logical errors and fitted curves',fontsize=17,fontweight='bold',y=.985)
fig.text(.5,.935,'H2-1E X-memory  |  Total requested sleep T = 1 s\nSleep-dependent MWPM decoding',ha='center',fontsize=11,linespacing=1.5)
fig.text(.13,.902,'Logical error model',fontsize=12,fontweight='bold')
fig.text(.13,.866,r'$P_L(d,u)=\frac{T}{u}C\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}\,q(u)\right]^{g(d+1)/2}$',
         fontsize=15)
fig.text(.13,.829,r'$q(u)=au+bu^2$, where $u=\Delta t$ is the sleep interval.',
         fontsize=11)
fig.text(.13,.025,'Error bars are 95% Wilson intervals. Dashed lines mark analytical minima.\nThe idle coefficients are fitted separately for each distance.',fontsize=9.5,color='#444444')
out=ROOT.parent/'output/pdf/d3_d5_g1_stacked_fits.pdf';out.parent.mkdir(parents=True,exist_ok=True)
fig.savefig(out)
fig.savefig(out.with_suffix('.png'),dpi=160)
(ROOT/'results/d3_d5_g1_stacked_fits.json').write_text(json.dumps(results,indent=2)+'\n')
print(json.dumps(results,indent=2))
try:
 import fitz
 doc=fitz.open(out);doc[0].get_pixmap(matrix=fitz.Matrix(1.5,1.5)).save(str(out.with_name('d3_d5_g1_stacked_fits_render.png')))
 print('PDF rendered')
except ImportError:
 print('PyMuPDF unavailable')
