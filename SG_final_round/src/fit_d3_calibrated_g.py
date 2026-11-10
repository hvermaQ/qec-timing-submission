"""Binomial fit of d=3 fixed-total-sleep counts with calibrated idle noise."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution, least_squares, minimize_scalar
from scipy.special import xlogy

ROOT = Path(__file__).resolve().parents[1]
source = ROOT/'results/d3_d5_all_explicit_sleep_logical_comparison.json'
rows = [r for r in json.loads(source.read_text())['rows'] if r['distance']==3 and r['total_requested_sleep_seconds']==1]
controls = json.loads((ROOT/'results/zero_sleep_pooled_d3_d5.json').read_text())['rows']
p_ext = next(r['inferred_p_ext_per_data_qubit_per_round'] for r in controls if r['distance']==3)
a,b = .006522,.092896
l1,l2 = (1-2*p_ext)*a/p_ext,(1-2*p_ext)*b/p_ext
u = np.array([r['delta_t_seconds'] for r in rows])
n = np.array([r['shots'] for r in rows]); k = np.array([r['logical_failures'] for r in rows])
shape = 1+l1*u+l2*u*u

def predict(parameters):
    g,log_c = parameters
    return np.exp(log_c)/u*shape**(2*g)

def residual(parameters):
    raw = predict(parameters)
    p = np.clip(raw,1e-15,1-1e-15)
    dev = 2*(xlogy(k,k/(n*p))+xlogy(n-k,(n-k)/(n*(1-p))))
    return np.r_[np.sign(p-k/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]

bounds = [(1e-6,1-1e-6),(-40,0)]
global_fit = differential_evolution(lambda x:np.sum(residual(x)**2),bounds,seed=31,tol=1e-11)
fit = least_squares(residual,global_fit.x,bounds=np.array(bounds).T,xtol=1e-12,ftol=1e-12,gtol=1e-10)
assert fit.success and abs(np.sum(fit.fun**2)-global_fit.fun)<1e-5
g,log_c = fit.x
alpha = 2*g
c1,c2 = (alpha-1)*l1,(2*alpha-1)*l2
optimum = 2/(c1+np.sqrt(c1*c1+4*c2))
def curve(t):return np.exp(log_c)/t*(1+l1*t+l2*t*t)**alpha
numeric = minimize_scalar(curve,bounds=(.001,1),method='bounded',options={'xatol':1e-12})
assert abs(numeric.x-optimum)<1e-6
result = dict(model='P_L=C_3/u*(1+lambda_1*u+lambda_2*u^2)^(2*g), T=1 s',source=str(source),scope='All pooled d=3 T=1 s rows including matching N=2 sleep-sweep shots',shots=int(n.sum()),a=a,b=b,p_ext=p_ext,lambda_1=l1,lambda_2=l2,g=float(g),C=float(np.exp(log_c)),alpha=float(alpha),delta_t_star=float(optimum),N_star=float(1+1/optimum),minimum_probability=float(curve(optimum)),binomial_deviance=float(np.sum(fit.fun**2)),nominal_df=len(rows)-2,rows=[dict(r,predicted_probability=float(p)) for r,p in zip(rows,predict(fit.x))])
(ROOT/'results/d3_calibrated_g_fit.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({key:value for key,value in result.items() if key!='rows'},indent=2))
for r,p in zip(rows,predict(fit.x)):
    print(r['rounds'],r['shots'],r['logical_failures'],round(100*p,4))
print('g needed for u=.2', (1+l1*.2+l2*.2**2)/(2*(l1*.2+2*l2*.2**2)))
