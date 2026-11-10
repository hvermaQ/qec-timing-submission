"""Fit the sleep-dependent d=5 counts with the linear+quadratic idle ansatz.

Binomial MLE, nonnegative idle coefficients, fixed paper-inspired g=.8,
alpha=g(d+1)/2=2.4. No provider access or decoder changes.
"""
import hashlib
import argparse
import json
import math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize,minimize_scalar
from scipy.special import xlogy

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'results/d5_sleep_dependent_redecode.json'
OUT=ROOT/'results/d5_sleep_dependent_linear_quadratic_fit'
ALPHA=.8*(5+1)/2
BOOTSTRAPS=1000
SEED=20261105


def probability(theta,u):
    return np.exp(theta[0])/u*(1+theta[1]*u+theta[2]*u*u)**ALPHA


def optimum(theta):
    a,b=theta[1:]
    denominator=(ALPHA-1)*a+math.sqrt(((ALPHA-1)*a)**2+4*(2*ALPHA-1)*b)
    return 2/denominator if denominator else math.inf


def main(min_rounds=2):
    global OUT
    if min_rounds>2:
        OUT=ROOT/f'results/d5_sleep_dependent_linear_quadratic_fit_n{min_rounds}_plus'
    data=json.loads(SOURCE.read_text())
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
    OUT.with_suffix('.json').write_text(json.dumps(results,indent=2)+'\n')
    np.savez_compressed(OUT.with_suffix('.npz'),optimum_seconds=np.array(opts),deviance=np.array(deviances),theta=np.array(coeffs))
    report(results);plot(results,best.x)
    print(json.dumps({key:results[key] for key in ['C','a','b','alpha','optimum_seconds','conditional_optimum_95','fitted_minimum_probability','binomial_deviance','bootstrap_gof_p']},indent=2),flush=True)


def report(d):
    lo,hi=d['conditional_optimum_95']
    lines=['# d=5 sleep-dependent DEM: linear-plus-quadratic idle fit','',
        f"Uses only T_sleep=1 s sleep-dependent-DEM outcomes: N={d['min_rounds']} through 10, {d['shots']:,} shots. Excluded N settings: {d['excluded_rounds']}. The T_sleep=0.5 s experiment is excluded. No provider submissions, decoder retuning or injected faults.",'',
        '## Model and fitting','',
        'Let x=Delta t/(1 second). P_L(x)=C/x*(1+a*x+b*x^2)^alpha, with g=.8 and alpha=g(d+1)/2=2.4 fixed to match the distance-adjusted convention used in the d=3 methodology. C,a,b are fitted by binomial maximum likelihood on failure/shot counts; a,b>=0. Both idle terms are included in the model even if a fitted coefficient reaches zero.','',
        f"C={d['C']:.10g}; a={d['a']:.10g}; b={d['b']:.10g}. Linear coefficient at boundary: {d['linear_at_boundary']}. This does not imply that the physical linear noise channel is absent.",'',
        'Differentiating log(P_L) gives -1/x + alpha*(a+2*b*x)/(1+a*x+b*x^2)=0. Therefore (alpha-1)*a*x+(2*alpha-1)*b*x^2=1, or 1.4*a*x+3.8*b*x^2=1. The stable positive root is x*=2/[1.4*a+sqrt((1.4*a)^2+15.2*b)].','',
        f"Analytical Delta t*={d['optimum_seconds']:.6g} s. Conditional 95% parametric-bootstrap interval={lo:.6g}–{hi:.6g} s. Fitted minimum P_L={100*d['fitted_minimum_probability']:.4g}%. The root was checked against numerical minimization and the stationary equation.",'',
        f"Binomial deviance={d['binomial_deviance']:.6g}; nominal residual df={d['nominal_residual_df']}. Boundary-aware parametric-bootstrap goodness-of-fit p={d['bootstrap_gof_p']:.6g}, from {d['bootstrap_successes']} successful refits, seed={d['bootstrap_seed']}. Bootstrap intervals are conditional on this chosen model and do not establish a physically calibrated optimum.",'',
        d['caveats'],'',
        '## Inputs','', '| N | Delta t (s) | Failures / shots | Measured P_L | Fitted P_L |','|---:|---:|---:|---:|---:|']
    for r,p in zip(d['rows'],d['fitted_probabilities']):lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['sleep_failures']}/{r['shots']} | {100*r['sleep_probability']:.3f}% | {100*p:.3f}% |")
    OUT.with_suffix('.md').write_text('\n'.join(lines)+'\n')


def plot(d,theta):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter,NullFormatter
    rows=d['rows'];fig,axes=plt.subplots(1,2,figsize=(11.4,4.8),layout='constrained')
    lo,hi=d['conditional_optimum_95']
    for ax,zoom in zip(axes,[False,True]):
        selected=[r for r in rows if not zoom or r['rounds']>=4]
        x=np.array([r['delta_t_seconds'] for r in selected]);y=np.array([r['sleep_probability'] for r in selected])
        err=np.array([[r['sleep_probability']-r['sleep_wilson_95'][0] for r in selected],[r['sleep_wilson_95'][1]-r['sleep_probability'] for r in selected]])
        maximum=max(r['delta_t_seconds'] for r in rows)
        grid=np.linspace(.10,.37,500) if zoom else np.geomspace(.1,maximum*1.03,700)
        ax.plot(grid,probability(theta,grid),color='#21836b',lw=2,label='Linear + quadratic idle fit')
        ax.errorbar(x,y,yerr=err,fmt='o',color='#185e87',ms=5.5,capsize=3,label='Sleep-dependent DEM; 95% Wilson CI',zorder=3)
        ax.axvline(d['optimum_seconds'],color='#ad6d19',ls='--',lw=1.2,label=f"Analytical Δt* = {d['optimum_seconds']:.3f} s")
        if zoom:ax.axvspan(lo,hi,color='#ad6d19',alpha=.10,label='Conditional 95% interval for Δt*')
        for r in selected:
            if not zoom and r['rounds']>=7:continue
            ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['sleep_wilson_95'][1]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
        ax.yaxis.set_major_formatter(PercentFormatter(1));ax.grid(alpha=.17);ax.spines['top'].set_visible(False);ax.spines['right'].set_visible(False)
        ax.set_xlabel('Sleep interval Δt (s)');ax.set_ylabel('Logical error probability per experiment')
        if zoom:
            ax.set_xlim(.10,.37);ax.set_ylim(0,.052);ax.set_title('Intermediate intervals',loc='left',fontsize=11)
        else:
            ax.set_xscale('log');ax.set_xlim(.095,maximum*1.1)
            top=max(r['sleep_wilson_95'][1] for r in rows)
            ax.set_ylim(0,top*1.25)
            ticks=[v for v in [1/9,1/6,.25,.5,1] if v<=maximum]
            ax.set_xticks(ticks);ax.set_xticklabels([f'{v:.3g}' for v in ticks]);ax.xaxis.set_minor_formatter(NullFormatter());ax.set_title('Fitted range · logarithmic horizontal axis',loc='left',fontsize=11)
        ax.legend(frameon=False,fontsize=7.5,loc='upper left' if not zoom else 'upper right')
    fig.suptitle(f"d=5 H2-1E · sleep-dependent DEM · N≥{d['min_rounds']} fit · T_sleep=1 s",fontsize=14,fontweight='bold')
    fig.supxlabel('Descriptive binomial fit; optimum interval excludes batch and decoder uncertainty.',fontsize=9)
    for suffix in ['png','svg']:fig.savefig(ROOT/f'results/figures/{OUT.name}.{suffix}',dpi=220)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--min-rounds',type=int,choices=[2,3],default=2)
    main(parser.parse_args().min_rounds)
