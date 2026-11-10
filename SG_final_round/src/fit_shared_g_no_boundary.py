"""Fit shared g with fixed physical idle coefficients and no boundary term."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import differential_evolution, least_squares
from scipy.special import xlogy

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'results/d3_d5_all_explicit_sleep_logical_comparison.json'
rows = [r for r in json.loads(source.read_text())['rows'] if r['total_requested_sleep_seconds'] == 1]
controls = json.loads((ROOT / 'results/zero_sleep_pooled_d3_d5.json').read_text())['rows']
p_ext = {r['distance']: r['inferred_p_ext_per_data_qubit_per_round'] for r in controls}
a, b = .006522, .092896
lambdas = {d: ((1-2*p)*a/p, (1-2*p)*b/p) for d,p in p_ext.items()}
distance = np.array([r['distance'] for r in rows])
index = (distance == 5).astype(int)
u = np.array([r['delta_t_seconds'] for r in rows])
shots = np.array([r['shots'] for r in rows])
faults = np.array([r['logical_failures'] for r in rows])
shape = np.array([1+lambdas[d][0]*t+lambdas[d][1]*t*t for d,t in zip(distance,u)])

def prediction(parameters):
    return np.exp(parameters[1:])[index]/u * shape**(parameters[0]*(distance+1)/2)

def residual(parameters):
    raw = prediction(parameters)
    probability = np.clip(raw,1e-15,1-1e-15)
    deviance = 2*(xlogy(faults,faults/(shots*probability)) + xlogy(shots-faults,(shots-faults)/(shots*(1-probability))))
    return np.r_[np.sign(probability-faults/shots)*np.sqrt(np.maximum(deviance,0)),1e5*np.maximum(raw-1,0)]

bounds = [(1e-6,1-1e-6),(-40,0),(-40,0)]
global_fit = differential_evolution(lambda x: np.sum(residual(x)**2),bounds,seed=29,popsize=20,tol=1e-10)
fit = least_squares(residual,global_fit.x,bounds=np.array(bounds).T,xtol=1e-12,ftol=1e-12,gtol=1e-10)
assert fit.success and abs(np.sum(fit.fun**2)-global_fit.fun)<1e-5
settings = []
for j,d in enumerate([3,5]):
    alpha = fit.x[0]*(d+1)/2
    l1,l2 = lambdas[d]
    c1,c2 = (alpha-1)*l1,(2*alpha-1)*l2
    optimum = 2/(c1+np.sqrt(c1*c1+4*c2))
    settings.append(dict(distance=d,p_ext=p_ext[d],lambda_1=l1,lambda_2=l2,C=float(np.exp(fit.x[1+j])),alpha=float(alpha),delta_t_star=float(optimum)))
output = dict(model='P_L=(T/u)*C_d*(1+lambda_1,d*u+lambda_2,d*u^2)^(g*(d+1)/2)',scope='All T=1 second pooled H2-1E rows; no ratio test; no additive boundary term',source=str(source),a=a,b=b,shared_g=float(fit.x[0]),shots=int(shots.sum()),binomial_deviance=float(np.sum(fit.fun**2)),nominal_df=len(rows)-3,settings=settings,rows=[dict(r,predicted_probability=float(p)) for r,p in zip(rows,prediction(fit.x))])
(ROOT/'results/d3_d5_calibrated_shared_g_no_boundary_fit.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k!='rows'},indent=2))
for r,p in zip(rows,prediction(fit.x)):
    print(r['distance'],r['rounds'],r['shots'],r['logical_failures'],round(100*p,4))
