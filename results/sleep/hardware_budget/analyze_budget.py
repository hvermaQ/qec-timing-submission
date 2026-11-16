import json,math
from pathlib import Path
import numpy as np
R=Path('/Users/harshank_s/qec-timing-submission')
fits=json.loads((R/'SG_final_round/results/d3_d5_g1_stacked_fits.json').read_text())
records=json.loads((R/'output/hardware_budget/job_costs.json').read_text())
res={'historical':{},'plan':[],'precision':[]}
for d in [3,5]:
 rs=[r for r in records if r['distance']==d]
 assert all(r['provider']['status']=='COMPLETED' and not r['provider']['error'] for r in rs)
 res['historical'][str(d)]={'jobs':len(rs),'shots':sum(r['shots'] for r in rs),'hqc':sum(r['provider']['hqcCost'] for r in rs)}
 for r in rs:
  expected=5+r['shots']*((216*r['rounds']+113) if d==3 else (696*r['rounds']+305))/5000
  assert abs(expected-r['provider']['hqcCost'])<1e-6
for f,shots in zip(fits,[[250,350,1000,1000,500,1000],[250,350,1000,1000,400,600]]):
 d=f['distance'];N=np.array([2,3,5,6,10,20]);s=np.array(shots);u=1/(N-1);a=(d+1)/2;l=(1-2*f['p_ext'])/f['p_ext']*f['b'];p=f['C']/u*(1+l*u*u)**a;c=(216*N+113 if d==3 else 696*N+305)/5000
 for n,ni,ui,pi,ci in zip(N,s,u,p,c):
  jobs=math.ceil(ni/(300 if d==5 and n==20 else 500))
  res['plan'].append(dict(distance=d,rounds=int(n),interval_seconds=float(ui),shots=int(ni),jobs=jobs,hqc=float(jobs*5+ci*ni),predicted_p=float(pi)))
 # Optimistic local precision: pure quadratic with g fixed, two free parameters.
 X=np.array([np.ones(len(u)),a*l*u*u/(1+l*u*u)]).T
 cov=np.linalg.inv(X.T@np.diag(s*p/(1-p))@X)
 se=f['delta_t_star']/2*np.sqrt(cov[1,1])
 # Sensitivity with an additional locally unconstrained linear coefficient.
 X3=np.array([np.ones(len(u)),a*u/(1+l*u*u),a*u*u/(1+l*u*u)]).T
 cov3=np.linalg.inv(X3.T@np.diag(s*p/(1-p))@X3)
 star=f['delta_t_star'];grad=np.array([0,-(a-1)*star/(2*(2*a-1)*l*star),-star/(2*l)])
 res['precision'].append(dict(distance=d,star=star,se_quadratic=float(se),se_linear_quadratic_local=float(np.sqrt(grad@cov3@grad))))
res['plan_hqc']=sum(r['hqc'] for r in res['plan']);res['plan_shots']=sum(r['shots'] for r in res['plan'])
(R/'output/hardware_budget/analysis.json').write_text(json.dumps(res,indent=2))
print(json.dumps(res,indent=2))
