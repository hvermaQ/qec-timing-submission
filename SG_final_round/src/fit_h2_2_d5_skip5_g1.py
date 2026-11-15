"""Fit skip5 d=5 probabilities; user-requested N=10 rounding, shot-weighted likelihood."""
import json,math,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares,minimize_scalar
from scipy.special import xlogy
ROOT=Path(__file__).resolve().parents[1]
sources=[ROOT/'results/d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json',ROOT/'runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json']
rows=json.loads(sources[0].read_text())['rows']+[json.loads(sources[1].read_text())]
assert [r['rounds'] for r in rows]==[2,3,4,6,10]
assert all(r['decoder_policy']['p_ext']==.005 and r['qubit_mapping']['unused_index']==5 for r in rows)
u=np.array([r['interval_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);exact=np.array([r['logical_failures'] for r in rows]);rounded=exact.astype(float);rounded[-1]=.013*n[-1]
starts=[np.array([math.log(c),math.log1p(a),math.log1p(b)]) for c,a,b in [(.0005,1,1),(.001,0,5),(.0001,5,0),(.001,0,0)]]
def predict(x,t=u):
 l1,l2=np.expm1(x[1:]);return np.exp(x[0])/t*(1+l1*t+l2*t*t)**3

def residual(x,k):
 raw=predict(x);p=np.clip(raw,1e-14,1-1e-14)
 dev=2*(xlogy(k,k/(n*p))+xlogy(n-k,(n-k)/(n*(1-p))))
 return np.r_[np.sign(p-k/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
def fit(k):
 fits=[least_squares(residual,s,args=(k,),bounds=([-30,0,0],[-1,10,10]),ftol=1e-12,xtol=1e-12,gtol=1e-10,max_nfev=3000) for s in starts]
 best=min([f for f in fits if f.success],key=lambda f:sum(f.fun**2));x=best.x;l1,l2=np.expm1(x[1:]);pe=.005
 star=2/(2*l1+math.sqrt(4*l1*l1+20*l2))
 num=minimize_scalar(lambda t:predict(x,t),bounds=(.001,3),method='bounded');assert abs(num.x-star)<1e-5
 assert abs(2*l1*star+5*l2*star**2-1)<1e-8
 return dict(C=float(np.exp(x[0])),a_per_second=float(l1*pe/(1-2*pe)),b_per_second_squared=float(l2*pe/(1-2*pe)),lambda_1=float(l1),lambda_2=float(l2),delta_t_star_seconds=float(star),continuous_N_star=float(1+1/star),minimum_fitted_probability=float(predict(x,star)),linear_at_boundary=bool(l1<1e-6),weighted_deviance=float(sum(best.fun**2)),fitted_probabilities=predict(x).tolist())
out=dict(platform='nexus:H2-2',distance=5,g=1,alpha=3,p_ext=.005,p_read=.001,model='P_L(u)=C/u*[1+((1-2*p_ext)/p_ext)*(a*u+b*u^2)]^3; u in seconds',method='Nonnegative a,b; shot-weighted cross-entropy fit. N=10 adjusted to requested 1.3%, giving fractional effective count 2.08/160; observed count remains 2/160. Not an exact binomial count fit.',rounded_fit=fit(rounded),exact_count_sensitivity_fit=fit(exact),rows=[dict(rounds=r['rounds'],interval_seconds=float(t),shots=int(shots),observed_failures=int(k),fit_probability=float(kk/shots)) for r,t,shots,k,kk in zip(rows,u,n,exact,rounded)],sources=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sources],caveat='Empirical curve fit; effective a,b are not calibrated microscopic idle rates. Sparse logical counts do not establish a resolved upturn or precise optimum.')
p=ROOT/'results/h2_2_d5_skip5_g1_rounded_n10_fit.json';p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
