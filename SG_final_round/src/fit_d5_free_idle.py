"""Fit d=5 logical counts with free nonnegative idle coefficients and shared exponent."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution, least_squares
from scipy.special import xlogy
ROOT=Path(__file__).resolve().parents[1]
prior=json.loads((ROOT/'results/d5_transferred_idle_g_fit.json').read_text())
rows=prior['rows'];pe=prior['p_ext']
u=np.array([r['delta_t_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows])
# Log1p parameterization permits exactly zero idle coefficients.
def prediction(x):
 g,logc,z1,z2=x
 l1,l2=np.expm1([z1,z2])
 return np.exp(logc)/u*(1+l1*u+l2*u*u)**(3*g)
def residual(x):
 raw=prediction(x);p=np.clip(raw,1e-15,1-1e-15)
 dev=2*(xlogy(k,k/(n*p))+xlogy(n-k,(n-k)/(n*(1-p))))
 return np.r_[np.sign(p-k/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
bounds=[(.00001,.99999999),(-40,0),(0,12),(0,12)]
fit0=differential_evolution(lambda x:np.sum(residual(x)**2),bounds,seed=57,popsize=25,tol=1e-10,maxiter=2000)
fit=least_squares(residual,fit0.x,bounds=np.array(bounds).T,xtol=1e-12,ftol=1e-12,gtol=1e-10)
g,logc,z1,z2=fit.x;l1,l2=np.expm1([z1,z2]);a,b=np.array([l1,l2])*pe/(1-2*pe)
c1,c2=(3*g-1)*l1,(6*g-1)*l2
opt=2/(c1+np.sqrt(c1*c1+4*c2))
profiles=[]
for fixed_g in [.3,.4,.5,.6,.7,.8,.9,.99]:
 def rr(z):return residual(np.r_[fixed_g,z])
 candidates=[least_squares(rr,[logc,z1,z2],bounds=([-40,0,0],[0,12,12]),max_nfev=3000),least_squares(rr,[-7,0,2],bounds=([-40,0,0],[0,12,12]),max_nfev=3000)]
 best=min(candidates,key=lambda f:np.sum(f.fun**2))
 profiles.append(dict(g=fixed_g,deviance=float(np.sum(best.fun**2))))
comparison=[dict(u=t,fitted_q=float(a*t+b*t*t)) for t in [.1,.25,.5,.75,1]]
result=dict(scope='All pooled d=5 T=1 s rows; free a,b,C,g; fixed pooled zero-sleep p_ext',shots=prior['shots'],p_ext=pe,g=float(g),C=float(np.exp(logc)),a=float(a),b=float(b),lambda_1=float(l1),lambda_2=float(l2),delta_t_star=float(opt),deviance=float(np.sum(fit.fun**2)),nominal_df=len(rows)-4,profile=profiles,sweep_comparison=comparison,rows=[dict(r,predicted_probability=float(p)) for r,p in zip(rows,prediction(fit.x))])
(ROOT/'results/d5_free_idle_g_fit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:v for key,v in result.items() if key!='rows'},indent=2))
for r,p in zip(rows,prediction(fit.x)):print(r['rounds'],r['logical_error_probability'],p)
