"""Binomial fits of logical error probability against the sleep interval.

Every `fit_*` script of SG_final_round/src, plus the fit parts of analyze_fixed_sleep_all.py,
report_d3_all_shots.py and plot_g1_stacked.py. Calculations are verbatim (same starts,
bounds, tolerances and seeds); only paths and writes changed. Each function reads committed
inputs from results/sleep/, writes its JSON (and .npz) to results/sleep/, and with plot=True
draws its figure through plots.py (to results/sleep/figures/).

    fixed_sleep_all(u, k, n)    paper-linear + quadratic fits with bootstraps (analysis.emulator_d3.fixed_sleep_all)
    d3_linear_quadratic()       report_d3_all_shots.py `fit`      -> d3_fixed_sleep_linear_quadratic_fit.json
    d3_calibrated_g()           fit_d3_calibrated_g.py            -> d3_calibrated_g_fit.json
    d3_free_idle()              fit_d3_free_idle.py               -> d3_free_idle_g_fit.json        (needs d3_calibrated_g_fit)
    d5_transferred_idle()       fit_d5_transferred_idle.py        -> d5_transferred_idle_g_fit.json (needs d3_free_idle_g_fit)
    d5_free_idle()              fit_d5_free_idle.py               -> d5_free_idle_g_fit.json        (needs d5_transferred_idle_g_fit)
    shared_g_calibrated()       fit_shared_g_calibrated.py        -> d3_d5_calibrated_shared_g_fit.json
    shared_g_no_boundary()      fit_shared_g_no_boundary.py       -> d3_d5_calibrated_shared_g_no_boundary_fit.json
    d5_sleep_dependent(m)       fit_d5_sleep_dependent.py         -> d5_sleep_dependent_linear_quadratic_fit[_n3_plus].*
    g1_stacked()                plot_g1_stacked.py (fit part)     -> d3_d5_g1_stacked_fits.json
    h2_2_g1()                   fit_h2_2_g1.py                    -> h2_2_d3_g1_linear_quadratic_fit.{json,npz}
    h2_2_free_g()               fit_h2_2_free_g.py                -> h2_2_d3_free_g_linear_quadratic_fit.json (needs h2_2_g1)
    h2_2_d5_skip5_g1()          fit_h2_2_d5_skip5_g1.py           -> h2_2_d5_skip5_g1_rounded_n10_fit.json (skip-5 only)

The inputs d3_d5_all_explicit_sleep_logical_comparison.json and zero_sleep_pooled_d3_d5.json
have no generating script; they are fixed inputs.
"""
import hashlib
import json
import math

import numpy as np

from . import paths

R = paths.RESULTS


# --------------------------------------------------------------------------- d=3 all shots (analyze_fixed_sleep_all)

FIXED_SLEEP_ALL_ALPHA = 1.6  # Paper g=.8, d=3; extrapolation, not a calibrated exponent.


def fixed_sleep_all_probability(u, theta, model):
    """Paper low-probability ansatz, or an empirical quadratic-idle extension.

    Bound only for numerical likelihood evaluation. Fits must remain unclipped.
    Both model the experiment probability directly (T_sleep=1), not a hazard.
    """
    ALPHA = FIXED_SLEEP_ALL_ALPHA
    c, a = np.exp(theta[:2])
    if model == 'paper_linear':
        q = c/u*(1+a*u)**ALPHA
    else:
        q = c/u*(1+a*u*u)**ALPHA
    return np.clip(q, 1e-12, 1-1e-12)


def fixed_sleep_all_nll(k, n, p):
    from scipy.special import xlogy
    return -float(np.sum(xlogy(k, p)+xlogy(n-k, 1-p)))


def fixed_sleep_all_fit(u, k, n, model, start=None):
    from scipy.optimize import minimize, minimize_scalar
    from scipy.stats import chi2
    ALPHA, probability, nll = FIXED_SLEEP_ALL_ALPHA, fixed_sleep_all_probability, fixed_sleep_all_nll
    starts = [start] if start is not None else [np.log([.0005, a]) for a in [1,10,100,1000]]
    candidates = [minimize(lambda t:nll(k,n,probability(u,t,model)), x,
                           method='L-BFGS-B', bounds=[(-18,0),(-12,18)]) for x in starts]
    best=min(candidates,key=lambda x:x.fun)
    assert best.success, best.message
    p=probability(u,best.x,model)
    dev=2*(best.fun-nll(k,n,np.clip(k/n,1e-12,1-1e-12)))
    c,a=np.exp(best.x)
    optimum=1/(a*(ALPHA-1)) if model=='paper_linear' else 1/np.sqrt(a*(2*ALPHA-1))
    numeric=minimize_scalar(lambda z:float(probability(np.exp(z),best.x,model)),
                            bounds=(-9,4),method='bounded')
    assert abs(np.log(optimum)-numeric.x)<1e-3
    assert np.all((p>1e-10)&(p<.99)), 'Numerical probability clipping active'
    return dict(model=model,C=float(c),a=float(a),alpha=ALPHA,
                optimum_seconds=float(optimum),deviance=float(dev),dof=len(u)-2,
                asymptotic_gof_p=float(chi2.sf(dev,len(u)-2)),nll=best.fun,
                fitted_probabilities=p.tolist(),theta=best.x.tolist())


def fixed_sleep_all(u, k, ns):
    """Both models, each with a 1,000-sample parametric bootstrap (seed 20261103)."""
    fit = fixed_sleep_all_fit
    fits=[fit(u,k,ns,m) for m in ['paper_linear','quadratic_extension']]
    rng=np.random.default_rng(20261103)
    for result in fits:
        # Parametric bootstrap: conditional on model and selected settings/shot counts.
        opts=[];deviances=[]
        for _ in range(1000):
            kb=rng.binomial(ns,result['fitted_probabilities'])
            b=fit(u,kb,ns,result['model'],np.array(result['theta']))
            opts.append(b['optimum_seconds']);deviances.append(b['deviance'])
        result['conditional_optimum_95_bootstrap']=np.quantile(opts,[.025,.975]).tolist()
        result['bootstrap_gof_p']=(1+int(np.count_nonzero(np.array(deviances)>=result['deviance'])))/1001
        print(result,flush=True)
    return fits


# --------------------------------------------------------------------------- d=3 linear + quadratic (report_d3_all_shots fit)

D3_LQ_SOURCE = R/'d3_fixed_sleep_all_shots.json'
D3_LQ_FIT = R/'d3_fixed_sleep_linear_quadratic_fit.json'


def d3_linear_quadratic_predict(t,u,alpha=1.6):
    return np.clip(np.exp(t[0])/u*(1+t[1]*u+t[2]*u*u)**alpha,1e-12,1-1e-12)


def d3_linear_quadratic(plot=True):
    """Combined idle ansatz on the 13,000 d=3 H2-1E shots; 1,000-sample bootstrap (seed 20261104)."""
    from scipy.optimize import minimize
    from scipy.special import xlogy
    SOURCE=D3_LQ_SOURCE
    data=json.loads(paths.read_text(SOURCE));rows=data['rows']
    x=np.array([r['delta_t_seconds'] for r in rows])
    k=np.array([r['logical_failures'] for r in rows]);n=np.array([r['shots'] for r in rows])
    alpha=1.6
    def pred(t,u):
        return d3_linear_quadratic_predict(t,u,alpha)
    def objective(t,counts):
        p=pred(t,x)
        return -float(np.sum(xlogy(counts,p)+xlogy(n-counts,1-p)))
    def fit(counts,starts):
        trials=[minimize(objective,s,args=(counts,),method='L-BFGS-B',
                         bounds=[(-18,0),(0,1000),(0,1000)]) for s in starts]
        success=[r for r in trials if r.success]
        assert success
        return min(success,key=lambda r:r.fun)
    best=fit(k,[[math.log(.0017),a,b] for a,b in [(0,10),(1,10),(10,10),(10,0)]])
    def optimum(t):
        a,b=t[1:]
        return 2/(math.sqrt(((alpha-1)*a)**2+4*(2*alpha-1)*b)+(alpha-1)*a)
    saturated=-float(np.sum(xlogy(k,k/n)+xlogy(n-k,1-k/n)))
    dev=2*(best.fun-saturated)
    rng=np.random.default_rng(20261104)
    opts=[];ds=[];linear=[]
    for i in range(1000):
        kb=rng.binomial(n,pred(best.x,x))
        br=fit(kb,[best.x,[math.log(.0017),0,10]])
        sat=-float(np.sum(xlogy(kb,np.clip(kb/n,1e-12,1-1e-12))+xlogy(n-kb,np.clip(1-kb/n,1e-12,1-1e-12))))
        opts.append(optimum(br.x));ds.append(2*(br.fun-sat));linear.append(float(br.x[1]))
    out=dict(form='P_L(x)=C/x*(1+a*x+b*x^2)^alpha; x=Delta_t/(1 second)',
        source=str(SOURCE),shots=sum(r['shots'] for r in rows),
        C=float(np.exp(best.x[0])),a=float(best.x[1]),b=float(best.x[2]),alpha=alpha,
        nonnegative_coefficients=True,linear_coefficient_at_boundary=bool(best.x[1]<1e-6),
        deviance=float(dev),bootstrap_gof_p=(1+sum(d>=dev for d in ds))/1001,
        bootstrap_replicates=1000,bootstrap_seed=20261104,
        optimum_seconds=optimum(best.x),conditional_optimum_95=np.quantile(opts,[.025,.975]).tolist(),
        fitted_minimum_probability=float(pred(best.x,optimum(best.x))),
        note='Descriptive low-probability ansatz; linear term unresolved, not evidence that the physical linear channel is absent. Bounds and intervals exclude systematic errors.')
    paths.write_json(D3_LQ_FIT, out)
    if plot:
        from . import plots
        plots.d3_linear_quadratic(rows,x,k,n,best.x)
    print(json.dumps(out,indent=2))
    return out


# --------------------------------------------------------------------------- calibrated / free idle fits (fixed inputs)

def d3_calibrated_g():
    """d=3 g fit with calibrated idle noise a=.006522, b=.092896 (differential evolution seed 31)."""
    from scipy.optimize import differential_evolution, least_squares, minimize_scalar
    from scipy.special import xlogy
    source = R/'d3_d5_all_explicit_sleep_logical_comparison.json'
    rows = [r for r in json.loads(paths.read_text(source))['rows'] if r['distance']==3 and r['total_requested_sleep_seconds']==1]
    controls = json.loads(paths.read_text(R/'zero_sleep_pooled_d3_d5.json'))['rows']
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
    paths.write_json(R/'d3_calibrated_g_fit.json', result)
    print(json.dumps({key:value for key,value in result.items() if key!='rows'},indent=2))
    for r,p in zip(rows,predict(fit.x)):
        print(r['rounds'],r['shots'],r['logical_failures'],round(100*p,4))
    print('g needed for u=.2', (1+l1*.2+l2*.2**2)/(2*(l1*.2+2*l2*.2**2)))
    return result


def _free_idle(prior_name, out_name, distance, seed, scope=None):
    """fit_d3_free_idle.py (distance 3, seed 37) and fit_d5_free_idle.py (distance 5, seed 57).

    The two scripts were identical except for their input, the exponent (2g vs 3g, i.e.
    g(d+1)/2), the seed, `scope`, and the d=3 sweep comparison column `sweep_q`.
    """
    from scipy.optimize import differential_evolution, least_squares
    from scipy.special import xlogy
    prior=json.loads(paths.read_text(R/prior_name))
    rows=prior['rows'];pe=prior['p_ext']
    u=np.array([r['delta_t_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows])
    m=(distance+1)//2
    # Log1p parameterization permits exactly zero idle coefficients.
    def prediction(x):
        g,logc,z1,z2=x
        l1,l2=np.expm1([z1,z2])
        return np.exp(logc)/u*(1+l1*u+l2*u*u)**(m*g)
    def residual(x):
        raw=prediction(x);p=np.clip(raw,1e-15,1-1e-15)
        dev=2*(xlogy(k,k/(n*p))+xlogy(n-k,(n-k)/(n*(1-p))))
        return np.r_[np.sign(p-k/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
    bounds=[(.00001,.99999999),(-40,0),(0,12),(0,12)]
    fit0=differential_evolution(lambda x:np.sum(residual(x)**2),bounds,seed=seed,popsize=25,tol=1e-10,maxiter=2000)
    fit=least_squares(residual,fit0.x,bounds=np.array(bounds).T,xtol=1e-12,ftol=1e-12,gtol=1e-10)
    g,logc,z1,z2=fit.x;l1,l2=np.expm1([z1,z2]);a,b=np.array([l1,l2])*pe/(1-2*pe)
    c1,c2=(m*g-1)*l1,(2*m*g-1)*l2
    opt=2/(c1+np.sqrt(c1*c1+4*c2))
    profiles=[]
    for fixed_g in [.3,.4,.5,.6,.7,.8,.9,.99]:
        def rr(z):return residual(np.r_[fixed_g,z])
        candidates=[least_squares(rr,[logc,z1,z2],bounds=([-40,0,0],[0,12,12]),max_nfev=3000),least_squares(rr,[-7,0,2],bounds=([-40,0,0],[0,12,12]),max_nfev=3000)]
        best=min(candidates,key=lambda f:np.sum(f.fun**2))
        profiles.append(dict(g=fixed_g,deviance=float(np.sum(best.fun**2))))
    if distance==3:
        comparison=[dict(u=t,sweep_q=.006522*t+.092896*t*t,fitted_q=float(a*t+b*t*t)) for t in [.1,.25,.5,.75,1]]
    else:
        comparison=[dict(u=t,fitted_q=float(a*t+b*t*t)) for t in [.1,.25,.5,.75,1]]
    result=dict(scope=prior['scope'] if scope is None else scope,shots=prior['shots'],p_ext=pe,g=float(g),C=float(np.exp(logc)),a=float(a),b=float(b),lambda_1=float(l1),lambda_2=float(l2),delta_t_star=float(opt),deviance=float(np.sum(fit.fun**2)),nominal_df=len(rows)-4,profile=profiles,sweep_comparison=comparison,rows=[dict(r,predicted_probability=float(p)) for r,p in zip(rows,prediction(fit.x))])
    paths.write_json(R/out_name, result)
    print(json.dumps({key:v for key,v in result.items() if key!='rows'},indent=2))
    for r,p in zip(rows,prediction(fit.x)):print(r['rounds'],r['logical_error_probability'],p)
    return result


def d3_free_idle():
    """Free nonnegative idle coefficients and exponent at d=3 (needs d3_calibrated_g_fit.json)."""
    return _free_idle('d3_calibrated_g_fit.json','d3_free_idle_g_fit.json',3,37)


def d5_free_idle():
    """Free nonnegative idle coefficients and exponent at d=5 (needs d5_transferred_idle_g_fit.json)."""
    return _free_idle('d5_transferred_idle_g_fit.json','d5_free_idle_g_fit.json',5,57,
                      scope='All pooled d=5 T=1 s rows; free a,b,C,g; fixed pooled zero-sleep p_ext')


def d5_transferred_idle():
    """d=5 with idle coefficients a, b taken from the free d=3 fit (needs d3_free_idle_g_fit.json)."""
    from scipy.optimize import differential_evolution, least_squares, minimize_scalar
    from scipy.special import xlogy
    source=R/'d3_d5_all_explicit_sleep_logical_comparison.json'
    rows=[r for r in json.loads(paths.read_text(source))['rows'] if r['distance']==5 and r['total_requested_sleep_seconds']==1]
    transferred=json.loads(paths.read_text(R/'d3_free_idle_g_fit.json'))
    a,b=transferred['a'],transferred['b']
    controls=json.loads(paths.read_text(R/'zero_sleep_pooled_d3_d5.json'))['rows']
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
    paths.write_json(R/'d5_transferred_idle_g_fit.json', result)
    print(json.dumps({key:value for key,value in result.items() if key!='rows'},indent=2))
    for r,p in zip(rows,prediction(fit.x)):print(r['rounds'],r['logical_error_probability'],p)
    return result


def shared_g_calibrated():
    """Joint d=3 + d=5 fit with calibrated idle terms, shared g and boundary terms (6 multistarts)."""
    from scipy.optimize import least_squares, minimize_scalar
    from scipy.special import xlogy
    source = R / 'd3_d5_all_explicit_sleep_logical_comparison.json'
    rows = [r for r in json.loads(paths.read_text(source))['rows'] if r['total_requested_sleep_seconds'] == 1]
    controls = json.loads(paths.read_text(R / 'zero_sleep_pooled_d3_d5.json'))['rows']
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
    paths.write_json(R/'d3_d5_calibrated_shared_g_fit.json', output)
    print(json.dumps({k:v for k,v in output.items() if k!='rows'},indent=2))
    for r,p in zip(rows,predict(fit.x)):
        print(r['distance'],r['rounds'],r['shots'],r['logical_failures'],round(100*p,4))
    return output


def shared_g_no_boundary():
    """Shared g with fixed physical idle coefficients and no boundary term (seed 29)."""
    from scipy.optimize import differential_evolution, least_squares
    from scipy.special import xlogy
    source = R / 'd3_d5_all_explicit_sleep_logical_comparison.json'
    rows = [r for r in json.loads(paths.read_text(source))['rows'] if r['total_requested_sleep_seconds'] == 1]
    controls = json.loads(paths.read_text(R / 'zero_sleep_pooled_d3_d5.json'))['rows']
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
    paths.write_json(R/'d3_d5_calibrated_shared_g_no_boundary_fit.json', output)
    print(json.dumps({k:v for k,v in output.items() if k!='rows'},indent=2))
    for r,p in zip(rows,prediction(fit.x)):
        print(r['distance'],r['rounds'],r['shots'],r['logical_failures'],round(100*p,4))
    return output


# --------------------------------------------------------------------------- d=5 sleep-dependent (fit_d5_sleep_dependent)

D5_SD_SOURCE=R/'d5_sleep_dependent_redecode.json'
D5_SD_ALPHA=.8*(5+1)/2
D5_SD_BOOTSTRAPS=1000
D5_SD_SEED=20261105


def d5_sleep_dependent_probability(theta,u):
    return np.exp(theta[0])/u*(1+theta[1]*u+theta[2]*u*u)**D5_SD_ALPHA


def d5_sleep_dependent_optimum(theta):
    ALPHA=D5_SD_ALPHA
    a,b=theta[1:]
    denominator=(ALPHA-1)*a+math.sqrt(((ALPHA-1)*a)**2+4*(2*ALPHA-1)*b)
    return 2/denominator if denominator else math.inf


def d5_sleep_dependent_out(min_rounds=2):
    """Output stem: d5_sleep_dependent_linear_quadratic_fit[_n<m>_plus]."""
    return R/('d5_sleep_dependent_linear_quadratic_fit' if min_rounds<=2 else f'd5_sleep_dependent_linear_quadratic_fit_n{min_rounds}_plus')


def d5_sleep_dependent(min_rounds=2, plot=True):
    """Linear+quadratic idle ansatz on the d=5 H2-1E sleep-dependent counts, T=1 s, N>=min_rounds.

    Binomial MLE, nonnegative idle coefficients, fixed paper-inspired g=.8,
    alpha=g(d+1)/2=2.4; 1,000-sample bootstrap (seed 20261105). No provider access or decoder changes.
    """
    from scipy.optimize import minimize,minimize_scalar
    from scipy.special import xlogy
    from . import reports
    assert min_rounds in (2,3)
    SOURCE=D5_SD_SOURCE;ALPHA=D5_SD_ALPHA;BOOTSTRAPS=D5_SD_BOOTSTRAPS;SEED=D5_SD_SEED
    probability=d5_sleep_dependent_probability;optimum=d5_sleep_dependent_optimum
    OUT=d5_sleep_dependent_out(min_rounds)
    data=json.loads(paths.read_text(SOURCE))
    rows=sorted([r for r in data['rows'] if r['total_requested_sleep_seconds']==1 and r['rounds']>=min_rounds],key=lambda r:r['rounds'])
    assert {r['rounds'] for r in rows}==set(range(min_rounds,11))
    x=np.array([r['delta_t_seconds'] for r in rows]);k=np.array([r['sleep_failures'] for r in rows]);n=np.array([r['shots'] for r in rows])
    def nll(theta,counts):
        p=np.clip(probability(theta,x),1e-12,1-1e-12)
        return -float(np.sum(xlogy(counts,p)+xlogy(n-counts,1-p)))
    def fit(counts,starts):
        trials=[minimize(nll,start,args=(counts,),method='L-BFGS-B',bounds=[(-25,-1),(0,1000),(0,1000)],options={'ftol':1e-12,'gtol':1e-7,'maxiter':2000}) for start in starts]
        successful=[r for r in trials if r.success and np.isfinite(r.fun)]
        assert successful,'No converged likelihood fit'
        best=min(successful,key=lambda r:r.fun)
        assert np.all((probability(best.x,x)>1e-10)&(probability(best.x,x)<.99)),'Likelihood clipping active at best fit'
        return best
    def deviance(theta,counts):
        sat=-float(np.sum(xlogy(counts,counts/n)+xlogy(n-counts,1-counts/n)))
        return 2*(nll(theta,counts)-sat)
    starts=[[math.log(c),a,b] for c,a,b in [(0.001,0,5),(0.001,1,5),(.0002,10,5),(.001,0,10),(.0001,20,0)]]
    best=fit(k,starts);u=optimum(best.x);C=float(np.exp(best.x[0]));a,b=map(float,best.x[1:]);dev=deviance(best.x,k)
    numeric=minimize_scalar(lambda z:float(probability(best.x,np.exp(z))),bounds=(-8,3),method='bounded')
    assert abs(math.log(u)-numeric.x)<1e-4
    assert abs((ALPHA-1)*a*u+(2*ALPHA-1)*b*u*u-1)<1e-10
    print('Primary fit:',C,a,b,'optimum',u,'deviance',dev,flush=True)
    rng=np.random.default_rng(SEED);opts=[];deviances=[];coeffs=[];failed=0
    for i in range(BOOTSTRAPS):
        counts=rng.binomial(n,probability(best.x,x))
        try:br=fit(counts,[best.x,[math.log(C),0,max(b,1)],[math.log(C),max(a,1),max(b,1)]])
        except AssertionError:
            failed+=1;continue
        opts.append(optimum(br.x));deviances.append(deviance(br.x,counts));coeffs.append(br.x.tolist())
        if (i+1)%200==0:print('Bootstrap',i+1,'/',BOOTSTRAPS,flush=True)
    assert len(opts)>=.99*BOOTSTRAPS
    ci=np.quantile(opts,[.025,.975]).tolist();gof=(1+sum(v>=dev for v in deviances))/(len(deviances)+1)
    results=dict(source=str(SOURCE),source_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest(),platform='nexus:H2-1E',distance=5,total_requested_sleep_seconds=1,shots=int(n.sum()),
        data='Sleep-dependent DEM outcomes only',min_rounds=min_rounds,excluded_rounds=list(range(2,min_rounds)),form='P_L(x)=C/x*(1+a*x+b*x^2)^alpha; x=Delta_t/(1 second)',
        alpha=ALPHA,g=.8,C=C,a=a,b=b,nonnegative_coefficients=True,linear_at_boundary=bool(a<1e-6),quadratic_at_boundary=bool(b<1e-6),
        optimum_seconds=u,stationary_condition='(alpha-1)*a*x + (2*alpha-1)*b*x^2 = 1',
        analytic_optimum='2 / ((alpha-1)*a + sqrt(((alpha-1)*a)^2 + 4*(2*alpha-1)*b))',
        conditional_optimum_95=ci,fitted_minimum_probability=float(probability(best.x,u)),
        binomial_deviance=dev,nominal_residual_df=len(rows)-3,bootstrap_gof_p=gof,bootstrap_attempts=BOOTSTRAPS,bootstrap_successes=len(opts),bootstrap_failures=failed,bootstrap_seed=SEED,
        fitted_probabilities=probability(best.x,x).tolist(),rows=rows,
        caveats='Descriptive low-probability ansatz with fixed exponent. N rounds but N-1 waits; boundary effects and extraction durations omitted. Conditional bootstrap assumes independent common-probability shots; it excludes batch variation, decoder uncertainty and physical scheduling uncertainty. Coefficients are not microscopic emulator-noise estimates.')
    paths.write_json(OUT.with_suffix('.json'), results)
    paths.save_npz(OUT.with_suffix('.npz'),optimum_seconds=np.array(opts),deviance=np.array(deviances),theta=np.array(coeffs))
    reports.d5_sleep_dependent_md(results,OUT.with_suffix('.md'))
    if plot:
        from . import plots
        plots.d5_sleep_dependent_fit(results,best.x,OUT.name)
    print(json.dumps({key:results[key] for key in ['C','a','b','alpha','optimum_seconds','conditional_optimum_95','fitted_minimum_probability','binomial_deviance','bootstrap_gof_p']},indent=2),flush=True)
    return results


# --------------------------------------------------------------------------- g=1 refits (plot_g1_stacked fit part)

def g1_stacked_predict(x,t,alpha):
    c=np.exp(x[0]);l1,l2=np.expm1(x[1:])
    return c/t*(1+l1*t+l2*t*t)**alpha


def g1_stacked(plot=True):
    """Refit d=3 and d=5 at g=1, starting from the free-idle fits -> results/sleep/d3_d5_g1_stacked_fits.json.

    Returns the per-distance fits; with plot=True draws the stacked portrait figure (plots.g1_stacked).
    """
    from scipy.optimize import least_squares
    from scipy.special import xlogy
    results=[];panels=[]
    for d in [3,5]:
        old=json.loads(paths.read_text(R/f'd{d}_free_idle_g_fit.json'))
        rows=old['rows'];u=np.array([r['delta_t_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows]);p=k/n
        alpha=(d+1)/2
        def predict(x,t=u):
            return g1_stacked_predict(x,t,alpha)
        def residual(x):
            raw=predict(x);prob=np.clip(raw,1e-15,1-1e-15)
            dev=2*(xlogy(k,k/(n*prob))+xlogy(n-k,(n-k)/(n*(1-prob))))
            return np.r_[np.sign(prob-p)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
        fit=least_squares(residual,[np.log(old['C']),np.log1p(old['lambda_1']),np.log1p(old['lambda_2'])],bounds=([-40,0,0],[0,12,12]),ftol=1e-12,xtol=1e-12,gtol=1e-10)
        assert fit.success
        l1,l2=np.expm1(fit.x[1:]);pe=old['p_ext'];a,b=np.array([l1,l2])*pe/(1-2*pe)
        c1,c2=(alpha-1)*l1,(2*alpha-1)*l2
        star=2/(c1+np.sqrt(c1*c1+4*c2))
        results.append(dict(distance=d,g=1,a=float(a),b=float(b),p_ext=pe,C=float(np.exp(fit.x[0])),delta_t_star=float(star),deviance=float(np.sum(fit.fun**2))))
        panels.append(dict(distance=d,rows=rows,u=u,n=n,p=p,alpha=alpha,x=fit.x,pe=pe,b=b,star=star))
    if plot:
        from . import plots
        plots.g1_stacked(panels)
    paths.write_json(R/'d3_d5_g1_stacked_fits.json', results)
    print(json.dumps(results,indent=2))
    return results


# --------------------------------------------------------------------------- physical H2-2 d=3

H2_2_G1_SOURCE=R/'h2_2_hardware_p_ext_0_00117_10750_shots.json'
H2_2_G1_OUT=R/'h2_2_d3_g1_linear_quadratic_fit'


def h2_2_g1_predict(x,t):
    l1,l2=np.expm1(x[1:]);return np.exp(x[0])/t*(1+l1*t+l2*t*t)**2


def h2_2_g1(plot=True):
    """Binomial fit of all pooled H2-2 d=3 T=1 s counts (9,750 shots); fixed d=3, g=1, p_ext.

    Asserts the input was decoded under the approved d=3 policy (decoder.POLICY).
    1,000-sample bootstrap (seed 20261113).
    """
    from scipy.optimize import least_squares,minimize_scalar
    from scipy.special import xlogy
    from .decoder import P_EXT,POLICY
    SOURCE=H2_2_G1_SOURCE;OUT=H2_2_G1_OUT
    data=json.loads(paths.read_text(SOURCE));assert data['decoder_policy']==POLICY
    rows=data['fixed_T1_rows'];u=np.array([r['interval_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows]);assert n.sum()==9750
    # Optimize C, lambda_1, lambda_2. Fixed p_ext maps lambdas to a,b.
    def predict(x,t=u):
        return h2_2_g1_predict(x,t)

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
    paths.write_json(OUT.with_suffix('.json'), r);paths.save_npz(OUT.with_suffix('.npz'),delta_t_star=np.array(stars),deviance=np.array(devs),theta=np.array(params))
    print(json.dumps({key:value for key,value in r.items() if key not in ['rows','decoder_policy']},indent=2),flush=True)
    if plot:
        from . import plots
        plots.h2_2_g1(dict(rows=rows,u=u,n=n,k=k,theta=theta,star=star,a=a,b=b,ci=ci,dev=dev,gof=gof,p_ext=P_EXT))
    return r


H2_2_FREE_G_OUT=R/'h2_2_d3_free_g_linear_quadratic_fit'


def h2_2_free_g_predict(x,t,g=None):
    g=x[3] if g is None else g;l1,l2=np.expm1(x[1:3]);return np.exp(np.clip(x[0]-np.log(t)+2*g*np.log1p(l1*t+l2*t*t),-700,10))


def h2_2_free_g_star(x):
    g=x[3];a,b=np.expm1(x[1:3]);v=(2*g-1)*a;w=(4*g-1)*b
    if w>0:return 2/(v+np.sqrt(v*v+4*w))
    if v>0:return 1/v
    return math.inf


def h2_2_free_g(plot=True):
    """Free-g vs g=1 binomial fits to physical H2-2 d=3 data (needs h2_2_d3_g1_linear_quadratic_fit.json).

    500-sample bootstrap (seed 20261113). g is weakly identified (its bootstrap interval reaches
    the bound 1000), so g, a and b move at the 1e-2 level between environments.
    """
    from scipy.optimize import least_squares
    from scipy.special import xlogy
    OUT=H2_2_FREE_G_OUT;star=h2_2_free_g_star
    fixed=json.loads(paths.read_text(R/'h2_2_d3_g1_linear_quadratic_fit.json'))
    rows=fixed['rows'];u=np.array([r['interval_seconds'] for r in rows]);n=np.array([r['shots'] for r in rows]);k=np.array([r['logical_failures'] for r in rows])
    xfix=np.array([np.log(fixed['C']),np.log1p(fixed['lambda_1']),np.log1p(fixed['lambda_2'])])
    def predict(x,t=u,g=None):
        return h2_2_free_g_predict(x,t,g)
    def residual(x,counts,g=None):
        raw=predict(x,g=g);p=np.clip(raw,1e-14,1-1e-14)
        dev=2*(xlogy(counts,counts/(n*p))+xlogy(n-counts,(n-counts)/(n*(1-p))))
        return np.r_[np.sign(p-counts/n)*np.sqrt(np.maximum(dev,0)),1e5*np.maximum(raw-1,0)]
    def fit(counts,starts,g=None):
        low=[-30,0,0]+([.05] if g is None else []);high=[-1,12,12]+([1000] if g is None else [])
        fits=[least_squares(residual,x,args=(counts,g),bounds=(low,high),ftol=1e-10,xtol=1e-10,gtol=1e-8,max_nfev=1500) for x in starts]
        fits=[f for f in fits if f.success];assert fits
        return min(fits,key=lambda f:float(f.fun@f.fun))
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
    paths.write_json(OUT.with_suffix('.json'), out);print(json.dumps({key:v for key,v in out.items() if key!='profile_g'},indent=2))
    if plot:
        from . import plots
        plots.h2_2_free_g(dict(rows=rows,u=u,n=n,k=k,xfix=xfix,best=best.x,g=g,fixed=fixed))
    return out


# --------------------------------------------------------------------------- physical H2-2 d=5, skip-index-5 only

def h2_2_d5_skip5_g1():
    """Skip-index-5 d=5 g=1 fit; N=10 adjusted to the user-requested 1.3%, plus the exact-count fit.

    Skip-5 only: asserts every row was decoded with p_ext .005 and has unused index 5. Reads
    the committed N=10 run analysis (results/sleep/runs/.../analysis_p_ext_0_005.json).
    -> results/sleep/h2_2_d5_skip5_g1_rounded_n10_fit.json
    """
    from scipy.optimize import least_squares,minimize_scalar
    from scipy.special import xlogy
    sources=[R/'d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json',paths.RUNS/'d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json']
    rows=json.loads(paths.read_text(sources[0]))['rows']+[json.loads(paths.read_text(sources[1]))]
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
    paths.write_json(R/'h2_2_d5_skip5_g1_rounded_n10_fit.json', out);print(json.dumps(out,indent=2))
    return out
