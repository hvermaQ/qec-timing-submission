"""Joint binomial fit of the fixed-total-sleep data with calibrated idle terms."""
import json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares, minimize_scalar
from scipy.special import xlogy

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / 'results/d3_d5_all_explicit_sleep_logical_comparison.json'
rows = [r for r in json.loads(source.read_text())['rows'] if r['total_requested_sleep_seconds'] == 1]
controls = json.loads((ROOT / 'results/zero_sleep_pooled_d3_d5.json').read_text())['rows']
p_ext = {r['distance']: r['inferred_p_ext_per_data_qubit_per_round'] for r in controls}
a, b = .006522, .092896
lambdas = {d: [(1 - 2*p) * a/p, (1 - 2*p) * b/p] for d, p in p_ext.items()}
distance = np.array([r['distance'] for r in rows])
index = (distance == 5).astype(int)
u = np.array([r['delta_t_seconds'] for r in rows])
shots = np.array([r['shots'] for r in rows])
faults = np.array([r['logical_failures'] for r in rows])
shape = np.array([1 + lambdas[d][0]*t + lambdas[d][1]*t*t for d,t in zip(distance,u)])

def predict(parameters):
    g = parameters[0]
    amplitude = np.exp(parameters[1:3])[index]
    boundary = parameters[3:5][index] / 100
    return boundary + amplitude / u * shape**(g*(distance+1)/2)

def residual(parameters):
    raw = predict(parameters)
    probability = np.clip(raw, 1e-15, 1-1e-15)
    deviance = 2*(xlogy(faults, faults/(shots*probability)) + xlogy(shots-faults, (shots-faults)/(shots*(1-probability))))
    return np.r_[np.sign(probability-faults/shots)*np.sqrt(np.maximum(deviance,0)), 1e5*np.maximum(raw-1,0)]

bounds = ([.001,-40,-40,0,0],[5,0,0,49,49])
fits = [least_squares(residual, [g,-8,-8,bound,bound], bounds=bounds, max_nfev=10000, xtol=1e-12, ftol=1e-12, gtol=1e-10) for g in [.3,.8,1.5] for bound in [0,.5]]
fit = min(fits, key=lambda f: np.sum(f.fun**2))
g = fit.x[0]
settings = []
for j,d in enumerate([3,5]):
    l1,l2 = lambdas[d]
    alpha = g*(d+1)/2
    # Positive root of (alpha-1)*l1*u + (2*alpha-1)*l2*u^2 = 1.
    c1, c2 = (alpha-1)*l1, (2*alpha-1)*l2
    optimum = 2/(c1+np.sqrt(c1*c1+4*c2)) if c2>0 else None
    amplitude, boundary = np.exp(fit.x[1+j]),fit.x[3+j]/100
    def curve(t):
        return boundary + amplitude/t*(1+l1*t+l2*t*t)**alpha
    numeric = minimize_scalar(curve,bounds=(.0001,1),method='bounded',options={'xatol':1e-12})
    if optimum is not None and optimum <= 1:
        assert abs(numeric.x-optimum)<1e-6
    integer_n = min(range(2,10001),key=lambda n: curve(1/(n-1)))
    settings.append(dict(distance=d,p_ext=p_ext[d],lambda_1=l1,lambda_2=l2,alpha=alpha,A=amplitude,B=boundary,delta_t_star=optimum,continuous_N_star=1+1/optimum if optimum else None,integer_N_star=integer_n,integer_delta_t=1/(integer_n-1),minimum_probability=curve(optimum) if optimum else None))
output = dict(model='P=B_d+A_d/u*(1+lambda_1,d*u+lambda_2,d*u^2)^(g*(d+1)/2), T=1 second',scope='All pooled H2-1E T=1 second rows, including matching N=2 sleep-sweep shots. Other T excluded.',source=str(source),a=a,b=b,shared_g=g,binomial_deviance=float(np.sum(fit.fun**2)),nominal_df=len(rows)-5,shots=int(shots.sum()),settings=settings,rows=[dict(r,predicted_probability=float(p)) for r,p in zip(rows,predict(fit.x))],optimizer_success=bool(fit.success),multistart_deviances=[float(np.sum(f.fun**2)) for f in fits])
path=ROOT/'results/d3_d5_calibrated_shared_g_fit.json'
path.write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps({k:v for k,v in output.items() if k!='rows'},indent=2))
for r,p in zip(rows,predict(fit.x)):
    print(r['distance'],r['rounds'],r['shots'],r['logical_failures'],round(100*p,4))
