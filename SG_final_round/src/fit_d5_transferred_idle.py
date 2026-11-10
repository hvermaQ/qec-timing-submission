"""Fit d=5 with idle coefficients transferred from the free d=3 logical fit."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution, least_squares, minimize_scalar
from scipy.special import xlogy
ROOT=Path(__file__).resolve().parents[1]
source=ROOT/'results/d3_d5_all_explicit_sleep_logical_comparison.json'
rows=[r for r in json.loads(source.read_text())['rows'] if r['distance']==5 and r['total_requested_sleep_seconds']==1]
transferred=json.loads((ROOT/'results/d3_free_idle_g_fit.json').read_text())
a,b=transferred['a'],transferred['b']
controls=json.loads((ROOT/'results/zero_sleep_pooled_d3_d5.json').read_text())['rows']
pe=next(r['inferred_p_ext_per_data_qubit_per_round'] for r in controls if r['distance']==5)
l1,l2=(1-2*pe)*a/pe,(1-2*pe)*b/pe
u=np.array([r['delta_t_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows])
def prediction(x):return np.exp(x[1])/u*(1+l1*u+l2*u*u)**(3*x[0])
def residual(x):
 raw=prediction(x);p=np.clip(raw,1e-15,1-1e-15)
 dev=2*(xlogy(k,k/(n*p))+xlogy(n-k,(n-k)/(n*(1-p))))
 return np.r_[np.sign(p-k/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
bounds=[(1e-6,1-1e-8),(-40,0)]
global_fit=differential_evolution(lambda x:np.sum(residual(x)**2),bounds,seed=41,tol=1e-11)
fit=least_squares(residual,global_fit.x,bounds=np.array(bounds).T,xtol=1e-12,ftol=1e-12,gtol=1e-10)
assert fit.success and abs(np.sum(fit.fun**2)-global_fit.fun)<1e-5
g,logc=fit.x;alpha=3*g
c1,c2=(alpha-1)*l1,(2*alpha-1)*l2
opt=2/(c1+np.sqrt(c1*c1+4*c2))
def curve(t):return np.exp(logc)/t*(1+l1*t+l2*t*t)**alpha
numeric=minimize_scalar(curve,bounds=(.001,1),method='bounded',options={'xatol':1e-12})
assert abs(numeric.x-opt)<1e-6
result=dict(model='P_L=C_5/u*(1+lambda_1*u+lambda_2*u^2)^(3*g)',scope='All d=5 T=1 s rows; a,b fixed to free d=3 logical fit; p_ext fixed to pooled zero-sleep estimate; 0<g<1',source=str(source),shots=int(n.sum()),a=a,b=b,p_ext=pe,lambda_1=l1,lambda_2=l2,g=float(g),C=float(np.exp(logc)),alpha=float(alpha),delta_t_star=float(opt),N_star=float(1+1/opt),minimum_probability=float(curve(opt)),binomial_deviance=float(np.sum(fit.fun**2)),nominal_df=len(rows)-2,rows=[dict(r,predicted_probability=float(p)) for r,p in zip(rows,prediction(fit.x))])
(ROOT/'results/d5_transferred_idle_g_fit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:value for key,value in result.items() if key!='rows'},indent=2))
for r,p in zip(rows,prediction(fit.x)):print(r['rounds'],r['logical_error_probability'],p)
