"""Compare free-g and g=1 binomial fits to physical H2-2 data."""
import json,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares,minimize_scalar
from scipy.special import xlogy
ROOT=Path(__file__).resolve().parents[1]
fixed=json.loads((ROOT/'results/h2_2_d3_g1_linear_quadratic_fit.json').read_text())
rows=fixed['rows'];u=np.array([r['interval_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows])
OUT=ROOT/'results/h2_2_d3_free_g_linear_quadratic_fit'
xfix=np.array([np.log(fixed['C']),np.log1p(fixed['lambda_1']),np.log1p(fixed['lambda_2'])])
def predict(x,t=u,g=None):
 g=x[3] if g is None else g;l1,l2=np.expm1(x[1:3]);return np.exp(np.clip(x[0]-np.log(t)+2*g*np.log1p(l1*t+l2*t*t),-700,10))
def residual(x,counts,g=None):
 raw=predict(x,g=g);p=np.clip(raw,1e-14,1-1e-14)
 dev=2*(xlogy(counts,counts/(n*p))+xlogy(n-counts,(n-counts)/(n*(1-p))))
 return np.r_[np.sign(p-counts/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
def fit(counts,starts,g=None):
 low=[-30,0,0]+([.05] if g is None else []);high=[-1,12,12]+([1000] if g is None else [])
 fits=[least_squares(residual,x,args=(counts,g),bounds=(low,high),ftol=1e-10,xtol=1e-10,gtol=1e-8,max_nfev=1500) for x in starts]
 fits=[f for f in fits if f.success];assert fits
 return min(fits,key=lambda f:float(f.fun@f.fun))
def star(x):
 g=x[3];a,b=np.expm1(x[1:3]);v=(2*g-1)*a;w=(4*g-1)*b
 if w>0:return 2/(v+np.sqrt(v*v+4*w))
 if v>0:return 1/v
 return math.inf
starts=[np.r_[xfix,g] for g in [.3,.5,.8,1,1.5,3,6]]
best=fit(k,starts);dev=float(best.fun@best.fun);delta=fixed['binomial_deviance']-dev
print('FREE',best.x,'deviance',dev,'LR',delta,'star',star(best.x),flush=True)
profiles=[]
for g in np.r_[np.arange(.3,2.01,.05),[2.5,3,4,6,8,10,20,50,100,300,1000]]:
 scaled=best.x[:3].copy();scaled[1:]=np.log1p(np.expm1(scaled[1:])*best.x[3]/g)
 f=fit(k,[scaled],g=float(g));profiles.append(dict(g=float(g),deviance=float(f.fun@f.fun)))
rng=np.random.default_rng(20261113);lr=[];gvals=[];stars=[];free_devs=[]
for i in range(500):
 # LR calibration under g=1; re-fit both nested models.
 counts=rng.binomial(n,predict(xfix,g=1));f0=fit(counts,[xfix],g=1);f1=fit(counts,[np.r_[f0.x,1],best.x])
 lr.append(max(0,float(f0.fun@f0.fun-f1.fun@f1.fun)))
 # Uncertainty and goodness of fit under free-g model.
 counts=rng.binomial(n,predict(best.x));f=fit(counts,[best.x,np.r_[xfix,1]])
 gvals.append(float(f.x[3]));stars.append(star(f.x));free_devs.append(float(f.fun@f.fun))
 if (i+1)%100==0:print('Bootstrap',i+1,flush=True)
g=float(best.x[3]);l1,l2=np.expm1(best.x[1:3]);pe=fixed['p_ext'];a,b=np.array([l1,l2])*pe/(1-2*pe)
out=dict(platform='nexus:H2-2',distance=3,p_ext=pe,g=g,C=float(np.exp(best.x[0])),lambda_1=float(l1),lambda_2=float(l2),a_per_second=float(a),b_per_second_squared=float(b),linear_at_boundary=bool(l1<1e-6),delta_t_star_seconds=star(best.x),delta_t_star_bootstrap_95=np.quantile(stars,[.025,.975]).tolist(),g_bootstrap_95=np.quantile(gvals,[.025,.975]).tolist(),binomial_deviance=dev,fixed_g_deviance=fixed['binomial_deviance'],deviance_improvement=delta,bootstrap_LR_p=(1+sum(v>=delta for v in lr))/501,free_g_bootstrap_gof_p=(1+sum(v>=dev for v in free_devs))/501,AIC_difference_free_minus_fixed=2-delta,bootstrap_replicates=500,profile_g=profiles,optimization_bounds_g=[.05,1000],bootstrap_g_upper_bound_hits=sum(v>999.9 for v in gvals),source=fixed['source'],source_sha256=fixed['source_sha256'],caveats=fixed['caveats'])
OUT.with_suffix('.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({key:v for key,v in out.items() if key!='profile_g'},indent=2))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
fig,ax=plt.subplots(figsize=(8,5),layout='constrained');p=k/n;ci=np.array([r['logical_wilson_95'] for r in rows]);grid=np.geomspace(min(u),max(u),1000)
ax.errorbar(u,p,yerr=[p-ci[:,0],ci[:,1]-p],fmt='o',mfc='white',color='#333333',capsize=3,label='Observed (95% Wilson)')
ax.plot(grid,predict(xfix,grid,g=1),label=f"g=1: Δt*={fixed['delta_t_star_seconds']:.3f} s",color='#176baf')
ax.plot(grid,predict(best.x,grid),label=f'g={g:.3f}: Δt*={star(best.x):.3f} s',color='#b45c21',ls='--')
ax.set_xscale('log');ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability');ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_ylim(0,.095);ax.grid(alpha=.2);ax.spines[['top','right']].set_visible(False);ax.legend(frameon=False)
ax.set_title('Physical H2-2 · d=3 · p_ext=0.00117 · 9,750 shots\nLinear + quadratic idle model: fixed versus fitted g',fontsize=12)
fig.savefig(OUT.with_suffix('.png'),dpi=180)
