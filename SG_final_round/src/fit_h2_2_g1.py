"""Binomial fit of all pooled H2-2 T=1 s counts; fixed d=3, g=1, p_ext."""
import hashlib,json,math
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares,minimize_scalar
from scipy.special import xlogy
from h2_2_decoder import P_EXT,POLICY
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/h2_2_hardware_p_ext_0_00117_10750_shots.json'
OUT=ROOT/'results/h2_2_d3_g1_linear_quadratic_fit'
data=json.loads(SOURCE.read_text());assert data['decoder_policy']==POLICY
rows=data['fixed_T1_rows'];u=np.array([r['interval_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows]);assert n.sum()==9750
# Optimize C, lambda_1, lambda_2. Fixed p_ext maps lambdas to a,b.
def predict(x,t=u):
 l1,l2=np.expm1(x[1:]);return np.exp(x[0])/t*(1+l1*t+l2*t*t)**2

def residual(x,counts):
 raw=predict(x);p=np.clip(raw,1e-14,1-1e-14)
 dev=2*(xlogy(counts,counts/(n*p))+xlogy(n-counts,(n-counts)/(n*(1-p))))
 return np.r_[np.sign(p-counts/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]

def fit(counts,starts):
 fits=[least_squares(residual,start,args=(counts,),bounds=([-30,0,0],[-1,10,10]),ftol=1e-10,xtol=1e-10,gtol=1e-8,max_nfev=500) for start in starts]
 fits=[f for f in fits if f.success];assert fits
 return min(fits,key=lambda f:np.sum(f.fun*f.fun))

def optimum(x):
 l1,l2=np.expm1(x[1:]);den=l1+np.sqrt(l1*l1+12*l2)
 return 2/den if den else math.inf
starts=[np.array([math.log(c),math.log1p(a),math.log1p(b)]) for c,a,b in [(.001,0,5),(.001,1,5),(.0005,5,0),(.0005,0,20)]]
best=fit(k,starts);theta=best.x;pred=predict(theta);assert np.all((pred>0)&(pred<1))
star=optimum(theta);dev=float(np.sum(best.fun**2));print('Fit',theta,'star',star,'deviance',dev,flush=True)
num=minimize_scalar(lambda z:predict(theta,np.exp(z)),bounds=(math.log(.001),math.log(10)),method='bounded');assert abs(math.log(star)-num.x)<1e-4
rng=np.random.default_rng(20261113);stars=[];devs=[];params=[]
for i in range(1000):
 counts=rng.binomial(n,pred)
 f=fit(counts,[theta,starts[0]])
 stars.append(optimum(f.x));devs.append(float(np.sum(f.fun**2)));params.append(f.x)
 if (i+1)%200==0:print('Bootstrap',i+1,flush=True)
l1,l2=np.expm1(theta[1:]);a,b=np.array([l1,l2])*P_EXT/(1-2*P_EXT)
ci=np.quantile(stars,[.025,.975]);gof=(1+sum(d>=dev for d in devs))/1001
integer_ns=np.arange(2,101);integer_u=1/(integer_ns-1);ib=int(np.argmin(predict(theta,integer_u)))
r=dict(platform='nexus:H2-2',distance=3,g=1,alpha=2,p_ext=P_EXT,total_requested_sleep_seconds=1,shots=int(n.sum()),model='P_L(u)=C/u*[1+((1-2*p_ext)/p_ext)*(a*u+b*u^2)]^2; u in seconds',C=float(np.exp(theta[0])),a_per_second=float(a),b_per_second_squared=float(b),lambda_1=float(l1),lambda_2=float(l2),linear_coefficient_at_boundary=bool(l1<1e-6),delta_t_star_seconds=float(star),delta_t_star_conditional_95_seconds=ci.tolist(),continuous_N_star=float(1+1/star),best_integer_N_2_to_100=int(integer_ns[ib]),minimum_fitted_probability=float(predict(theta,star)),binomial_deviance=dev,nominal_residual_df=len(rows)-3,parametric_bootstrap_gof_p=gof,bootstrap_replicates=1000,bootstrap_seed=20261113,source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),decoder_policy=POLICY,rows=[dict(row,fitted_probability=float(p)) for row,p in zip(rows,pred)],caveats='Conditional on the empirical ansatz, fixed g and p_ext, independent common-probability shots, and neglected extraction duration. Zero-sleep control excluded. Bootstrap does not include calibration uncertainty, drift, model uncertainty, or adaptive setting selection. a,b describe the logical curve and are not independently measured physical idle rates.')
OUT.with_suffix('.json').write_text(json.dumps(r,indent=2)+'\n');np.savez_compressed(OUT.with_suffix('.npz'),delta_t_star=np.array(stars),deviance=np.array(devs),theta=np.array(params))
print(json.dumps({key:value for key,value in r.items() if key not in ['rows','decoder_policy']},indent=2),flush=True)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
plt.rcParams.update({'font.size':12,'axes.spines.top':False,'axes.spines.right':False})
fig,ax=plt.subplots(figsize=(8.27,8.8));fig.subplots_adjust(left=.13,right=.96,top=.69,bottom=.25)
fig.suptitle('Observed logical errors and fitted curve',fontsize=17,fontweight='bold',y=.98)
fig.text(.5,.92,'Physical H2-2 X-memory | d = 3 | 9,750 shots\nTotal requested sleep T = 1 s | Sleep-dependent MWPM',ha='center',fontsize=11,linespacing=1.5)
fig.text(.13,.835,r'$P_L(u)=\frac{T}{u}C\left[1+\frac{1-2p_{\rm ext}}{p_{\rm ext}}(au+bu^2)\right]^2$',fontsize=16)
fig.text(.13,.785,f'Fixed: d = 3, g = 1, p_ext = {P_EXT:.5f}. Fit: C, a, b; a,b >= 0.',fontsize=11)
p=k/n;bounds=np.array([row['logical_wilson_95'] for row in rows]);color='#176baf'
ax.errorbar(u,p,yerr=[p-bounds[:,0],bounds[:,1]-p],fmt='o',mfc='white',color=color,capsize=3,label='Observed (95% Wilson intervals)')
grid=np.geomspace(min(u),max(u),1000);ax.plot(grid,predict(theta,grid),color=color,lw=2,label='Binomial likelihood fit')
ax.axvline(star,color=color,ls='--',label=f'Minimum: {star:.4f} s')
ax.set_xscale('log');ax.set_xlim(.022,1.15);ax.set_ylim(0,.095);ax.set_xticks([.025,.05,.1,.2,.5,1],['0.025','0.05','0.1','0.2','0.5','1']);ax.yaxis.set_major_formatter(PercentFormatter(1));ax.set_xlabel('Sleep interval Δt (s, logarithmic scale)');ax.set_ylabel('Logical error probability');ax.grid(alpha=.18);ax.legend(frameon=False,fontsize=10)
fig.text(.13,.17,f'Fitted: a = {a:.5g} s⁻¹, b = {b:.6g} s⁻², C = {np.exp(theta[0]):.7g}\nΔt* = {star:.4f} s; conditional 95% bootstrap: {ci[0]:.4f}-{ci[1]:.4f} s\nBinomial deviance = {dev:.3f}; nominal df = 5; bootstrap GOF p = {gof:.3f}',fontsize=11,linespacing=1.6,va='top')
fig.text(.13,.035,'All eight fixed-T settings included; zero-sleep control excluded.\nUncertainty is conditional on the model and fixed parameters; drift and calibration\nuncertainty are excluded. Curve parameters are effective, not calibrated idle rates.',fontsize=9,color='#444444',linespacing=1.5)
fig.savefig(OUT.with_suffix('.png'),dpi=180)
