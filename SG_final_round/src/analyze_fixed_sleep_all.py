"""Pool every fixed-sleep H2-1E batch once, retaining the established decoder."""
import json
import hashlib
from dataclasses import replace
from pathlib import Path
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import xlogy
from scipy.stats import chi2, fisher_exact
import fixed_sleep_d3 as f
from analyze_fixed_sleep_refinement import load_batch
from analyze_single_qubit_pilot import wilson
from qec_timing.hardware.providers import _register_builtins
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

OUT = f.ROOT/'results/d3_fixed_sleep_all_shots'
ALPHA = 1.6  # Paper g=.8, d=3; extrapolation, not a calibrated exponent.


def probability(u, theta, model):
    """Paper low-probability ansatz, or an empirical quadratic-idle extension.

    Bound only for numerical likelihood evaluation. Fits must remain unclipped.
    Both model the experiment probability directly (T_sleep=1), not a hazard.
    """
    c, a = np.exp(theta[:2])
    if model == 'paper_linear':
        q = c/u*(1+a*u)**ALPHA
    else:
        q = c/u*(1+a*u*u)**ALPHA
    return np.clip(q, 1e-12, 1-1e-12)


def nll(k, n, p):
    return -float(np.sum(xlogy(k, p)+xlogy(n-k, 1-p)))


def fit(u, k, n, model, start=None):
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


def main():
    _register_builtins()
    runs=[f.ROOT/'runs'/name for name in [
        'd3_fixed_sleep_690baca08b24dfd2',
        'd3_fixed_sleep_refinement_3bb6e107a0ff6de3',
        'd3_fixed_sleep_resolution_c2380924e8c69578']]
    grouped={}; seen=set()
    base=spec_from_json(json.loads(f.SOURCE.with_suffix('.json').read_text())['spec'])
    for run in runs:
        status=json.loads((run/'collection_status.json').read_text())
        assert status['all_results_stored']
        for j in status['jobs']:
            assert j['status']=='COMPLETED' and j['stored']
            assert j['job_id'] not in seen
            seen.add(j['job_id'])
            n=j['rounds']; count=j['shots']
            shots,meta=load_batch(run,j['name'],n,count)
            # Verify eligibility from the source job, not its directory alone.
            job=json.loads((run/'execute'/j['name']/'job.json').read_text())
            assert job['platform']=='nexus:H2-1E'
            assert abs(job['delta_t_seconds']-1/(n-1))<1e-14
            assert job['options']==f.CONFIG['options']
            bitcode_hash=hashlib.sha256(Path(job['program']).read_bytes()).hexdigest()
            grouped.setdefault(n,[]).append((shots,dict(meta,run=str(run),name=j['name'],bitcode_sha256=bitcode_hash)))
    rows=[]
    demdir=f.ROOT/'results/decoders/d3_fixed_sleep_all_shots'
    demdir.mkdir(parents=True,exist_ok=True)
    for n,batches in sorted(grouped.items()):
        assert len({meta['bitcode_sha256'] for _,meta in batches})==1
        total=sum(len(shots) for shots,_ in batches)
        spec=replace(base,schedule=Schedule.rounds(1/(n-1),n),shots=total)
        syn,dat=bits_from_shots([s for shots,_ in batches for s in shots],n,4,9)
        rec=record_from_bits(spec,syn,dat)
        counts={};primary=None
        for p in [.002,.02,.1]:
            dem=dem_for(paper_graph(spec,p,0,.001))
            (demdir/f'n{n}_p{p}.dem').write_text(dem)
            pred=PyMatchingDecoder(dem).decode_batch(rec.detectors)
            fail=np.any(pred!=rec.observables,axis=1)
            counts[str(p)]=int(fail.sum())
            if p==.002: primary=fail
        offset=0;sources=[]
        for shots,meta in batches:
            sources.append(dict(meta,logical_failures=int(primary[offset:offset+len(shots)].sum())))
            offset+=len(shots)
        k=counts['0.002']
        # Check a second implementation of the logical observable (X string q0,3,6).
        assert np.array_equal(rec.observables[:,0], np.bitwise_xor.reduce(dat[:,[0,3,6]],axis=1))
        rows.append(dict(rounds=n,delta_t_seconds=1/(n-1),shots=total,
                         logical_failures=k,logical_error_probability=k/total,
                         wilson_95=wilson(k,total),sources=sources,
                         decoder_sensitivity_failures=counts))
        print(n,k,total,flush=True)
    assert len(seen)==18 and sum(r['shots'] for r in rows)==13000
    u=np.array([r['delta_t_seconds'] for r in rows]);k=np.array([r['logical_failures'] for r in rows]);ns=np.array([r['shots'] for r in rows])
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
    homogeneity_deviance=0.;homogeneity_df=0
    for r in rows:
        sources=r['sources']
        if len(sources)>1:
            sk=np.array([s['logical_failures'] for s in sources])
            sn=np.array([s['shots'] for s in sources])
            homogeneity_deviance+=2*(nll(sk,sn,np.repeat(r['logical_error_probability'],len(sk)))-nll(sk,sn,np.clip(sk/sn,1e-12,1-1e-12)))
            homogeneity_df+=len(sources)-1
    best=min(rows,key=lambda r:r['logical_error_probability'])
    contrasts=[]
    for r in rows:
        if r is best: continue
        _,pv=fisher_exact([[best['logical_failures'],best['shots']-best['logical_failures']],
                          [r['logical_failures'],r['shots']-r['logical_failures']]])
        contrasts.append(dict(reference_N=best['rounds'],other_N=r['rounds'],two_sided_fisher_p=float(pv)))
    result=dict(platform='nexus:H2-1E',distance=3,basis='X',unique_jobs=len(seen),total_shots=13000,
                total_requested_sleep_seconds=1,extraction_duration_neglected=True,
                parallel_sleep_verified=False,primary_decoder='Fixed phenomenological MWPM: p_data=.002, p_read=.001, lambda=0; not calibrated circuit-level DEM',
                paper='https://arxiv.org/html/2608.06242v2',rows=rows,fits=fits,
                batch_homogeneity=dict(deviance=homogeneity_deviance,dof=homogeneity_df,
                                      asymptotic_p=float(chi2.sf(homogeneity_deviance,homogeneity_df))),
                exploratory_minimum_contrasts=contrasts)
    OUT.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    write_report(result)
    plot(result)


def write_report(result):
    lines=['# All-shot d=3 X-memory fixed-requested-sleep analysis','',
        'H2-1E, 18 unique execution jobs, 13,000 shots. Only the coarse, refinement and resolution fixed-sleep batches are pooled; no two-round variable-total-sleep sweep or H2-2E shots. Raw hashes and formatted/packed counts verified. Repeated N used identical bitcode across batches; platform, requested interval and emulator options match. No provider jobs submitted or modified.','',
        'Nine data qubits, four X stabilizer checks per extraction round with a reused ancilla, initial logical + state and final X readout. N rounds separated by N-1 sleep blocks. u=Delta t=1/(N-1) seconds, total requested sleep one second per data qubit. Extraction duration is neglected; physical parallel overlap of the nine sleep calls remains unverified.','',
        result['primary_decoder']+'. The same weights are retained for every batch and have not been optimized on these outcomes. Failure is decoder-predicted logical flip XOR final X parity on q0,3,6.','',
        '| N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |',
        '|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        lo,hi=r['wilson_95']
        lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.3f}% | {100*lo:.3f}–{100*hi:.3f}% |")
    best=min(result['rows'],key=lambda r:r['logical_error_probability'])
    lines+=['',f"Sample minimum: N={best['rounds']}, Delta t={best['delta_t_seconds']:.6g} s. Neighboring settings must be compared with sampling uncertainty; selection was adaptive after earlier batches, so minimum claims are exploratory.",'',
        '## Analytical fits','',
        'Binomial maximum likelihood on all ten pooled failure counts; no least-squares fit to percentages. Fix alpha=g(d+1)/2=1.6 using the paper g=.8, extrapolated to d=3. Probabilities are modeled directly using the paper low-probability approximation P_L approximately R T with T_sleep=1 s; no saturation correction. C absorbs all distance/prefactor factors. This is a descriptive fit, not extraction of microscopic error parameters.','',
        'Paper-shaped linear-idle ansatz: P_L(u)=C(1+a u)^1.6/u; u*=1/(.6a). Quadratic-idle extension: P_L(u)=C(1+a u^2)^1.6/u; u*=1/sqrt(2.2a). The latter substitutes quadratic growth for linear growth; it is an empirical extension, not Eq. 6 of the paper or the full Quantinuum noise model. Both have two fitted positive parameters.','']
    for fit_ in result['fits']:
        lo,hi=fit_['conditional_optimum_95_bootstrap']
        lines.append(f"- {fit_['model']}: C={fit_['C']:.8g}, a={fit_['a']:.8g}; u*={fit_['optimum_seconds']:.5g} s (conditional 95% parametric-bootstrap interval {lo:.5g}–{hi:.5g} s); binomial deviance={fit_['deviance']:.4g}, df={fit_['dof']}; asymptotic goodness-of-fit p={fit_['asymptotic_gof_p']:.5g}, bootstrap p={fit_['bootstrap_gof_p']:.5g} (1,000 replicates, seed 20261103). If a model fails goodness of fit, its optimum interval is not a reliable physical confidence interval.")
    h=result['batch_homogeneity']
    lines+=['',f"Pooled-batch homogeneity check: deviance={h['deviance']:.5g}, df={h['dof']}, asymptotic p={h['asymptotic_p']:.5g}. This is a limited check for between-batch differences at repeated N, not proof of independence or stationary noise.",'',
        '## Conclusion','',
        'The sample minimum is 1.20% at N=5 (u=.25 s), while N=6 and N=7 are both 1.40%. These neighboring settings do not establish a unique discrete optimum. Both tails are substantially higher, supporting an interior region of improved memory performance for this implementation and decoder.','',
        'The paper-shaped fit with fixed g=.8 is strongly rejected by the pooled data (deviance 114.51 on 8 degrees of freedom). The quadratic-idle extension gives an acceptable descriptive fit (deviance 9.75 on 8 degrees of freedom) and a smooth optimum near .198 s, conditional 95% bootstrap interval .181–.225 s. Its minimum fitted probability is about 1.63%. The bootstrap bounds are conditional on the chosen curve, fixed exponent, independent binomial shots and neglected extraction duration; they exclude systematic uncertainty.','',
        '[Quantinuum documentation](https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html) describes both linear and quadratic dephasing, with quadratic dephasing represented by stochastic Z faults in stabilizer simulation. This motivates trying a quadratic extension; its success alone does not identify a microscopic noise law.']
    lines+=['','## Comparison with the paper','',
        '[Haug, Bharti and Aolita, arXiv:2608.06242v2](https://arxiv.org/html/2608.06242v2), Eqs. 5–6, predicts u*=2/[lambda(g(d+1)-2)]; d=3, g=.8 gives u*=1/(.6 lambda). Its assumptions include approximately linear idle probability, small logical probability and sufficiently many rounds to suppress time-like faults. The physical idle slope is p lambda, so lambda is relative to extraction noise, not simply an absolute idle rate or the sleep-unit conversion.','',
        'Fitting lambda to these same logical probabilities and substituting it into Eq. 6 is an internal consistency calculation, not an independent prediction. We have no separately calibrated phenomenological p, lambda and g for this circuit/backend. Quantinuum circuit-level noise includes gate/readout/transport contributions and non-linear dephasing; the decoder is deliberately phenomenological and mismatched. Small N has substantial finite-round and boundary effects (N rounds but N-1 intervals). Thus disagreement with the simple paper fit need not contradict its derivation.','',
        'The two tails versus intermediate intervals can support a timing tradeoff within this decoder/setup. They cannot establish the paper 1/d scaling from a single distance, a unique best intermediate N, or a physically calibrated optimum. Error bars cover independent shot sampling only, not decoder mismatch, batching drift, uncertain overlap or extraction duration. The quadratic extension was selected after examining this experiment and its known non-linear idle model; model comparisons are exploratory.','',
        '## Provenance and reproducibility','',
        'The JSON beside this report records each job ID, source directory, raw SHA-256 and per-batch decoded failures. All stored DEMs are under results/decoders/d3_fixed_sleep_all_shots. Run the companion analysis with the established NumPy/Stim/PyMatching/SciPy environment. Preserve earlier reports; this report supersedes their shot totals only for the same fixed-sleep protocol.']
    OUT.with_suffix('.md').write_text('\n'.join(lines)+'\n')


def plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,(ax,zoom)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={'width_ratios':[1.5,1]},layout='constrained')
    rows=sorted(result['rows'],key=lambda x:x['delta_t_seconds'])
    x=np.array([r['delta_t_seconds'] for r in rows]);y=np.array([r['logical_error_probability'] for r in rows])
    err=np.array([[r['logical_error_probability']-r['wilson_95'][0] for r in rows],[r['wilson_95'][1]-r['logical_error_probability'] for r in rows]])
    for a in [ax,zoom]:
        a.errorbar(x,y,yerr=err,fmt='o',color='#17658a',capsize=3,label='Pooled shots; 95% Wilson CI',zorder=4)
        grid=np.geomspace(.024,1.05,500)
        for fit_,color,ls,label in zip(result['fits'],['#ac5352','#23845b'],['--','-'],['Paper linear-idle fit','Quadratic-idle extension']):
            a.plot(grid,probability(grid,np.array(fit_['theta']),fit_['model']),color=color,ls=ls,lw=2,label=label)
        a.yaxis.set_major_formatter(PercentFormatter(1));a.grid(alpha=.18)
        a.set_xlabel('Sleep interval Δt (seconds)')
    for r in rows:
        ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
    ax.set_xscale('log');ax.set_xlim(.022,1.2);ax.set_ylim(0,.17)
    ax.set_ylabel('Logical error probability per experiment')
    ax.set_title('All ten settings (logarithmic interval axis)',loc='left',fontsize=12)
    zoom.set_xlim(.09,.38);zoom.set_ylim(0,.045)
    zoom.set_title('Intermediate intervals',loc='left',fontsize=12)
    for r in rows:
        if .09<r['delta_t_seconds']<.38:
            zoom.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],r['wilson_95'][1]),xytext=(0,6),textcoords='offset points',ha='center',fontsize=9)
    ax.legend(loc='upper center',fontsize=8,frameon=False)
    fig.suptitle('d=3 X-memory on H2-1E • 13,000 shots • total requested sleep = 1 s',fontsize=14)
    fig.supxlabel('Fixed phenomenological decoder. Extraction duration neglected. Fits are descriptive, not independent predictions.',fontsize=9)
    dest=f.ROOT/'results/figures/d3_fixed_sleep_all_shots'
    fig.savefig(dest.with_suffix('.png'),dpi=190,bbox_inches='tight')
    fig.savefig(dest.with_suffix('.svg'),bbox_inches='tight')


if __name__=='__main__':
    main()
