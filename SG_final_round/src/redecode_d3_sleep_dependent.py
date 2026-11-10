"""Re-decode the saved fixed-sleep shots with independently specified idle weights.

No provider access, fitting, logical-label training or modification of old results.
"""
import hashlib
import json
import math
from dataclasses import replace
from pathlib import Path
import numpy as np
from scipy.stats import binomtest

import fixed_sleep_d3 as f
from analyze_fixed_sleep_refinement import load_batch
from analyze_single_qubit_pilot import wilson
from qec_timing.hardware.providers import _register_builtins
from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.spec import spec_from_json
from qec_timing.schedule import Schedule
from qec_timing.hardware.collect import paper_graph
from qec_timing.backends.stim_phenom import dem_for
from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
from qec_timing.noise.base import RoundNoise

P_EXT=.002
P_READ=.001
LINEAR_RATE=.0028
QUADRATIC_FREQUENCY_HZ=.043
INCOHERENT_FACTOR=2.0
ROOT=f.ROOT
OLD=ROOT/'results/d3_fixed_sleep_all_shots.json'
OUT=ROOT/'results/d3_sleep_dependent_redecode'
SOURCES=[
 'https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html',
 'https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html']


def xor_probability(a,b):
    return a+b-2*a*b


def idle_probability(u):
    """Independent stochastic Z channels, with frequency converted to rad/s.

    Frequency parameter is in units of 2*pi rad/s; incoherence multiplies
    frequency (not probability). Net Z is odd parity of the two channel faults.
    """
    if not 0<=LINEAR_RATE*u<=1:
        raise ValueError('Duration outside linear-channel probability domain')
    lin=LINEAR_RATE*u
    quad=math.sin(math.pi*QUADRATIC_FREQUENCY_HZ*INCOHERENT_FACTOR*u)**2
    return xor_probability(lin,quad)


def round_probabilities(n,u):
    # N extraction draws, but only N-1 waits; no wait before the first round.
    p=xor_probability(P_EXT,idle_probability(u))
    return [RoundNoise(P_EXT,P_READ)]+[RoundNoise(p,P_READ) for _ in range(n-1)]


def main():
    _register_builtins()
    old=json.loads(OLD.read_text())
    base=spec_from_json(json.loads(f.SOURCE.with_suffix('.json').read_text())['spec'])
    demdir=ROOT/'results/decoders/d3_sleep_dependent'
    demdir.mkdir(parents=True,exist_ok=True)
    seen=set();rows=[];saved={}
    for oldrow in old['rows']:
        n=oldrow['rounds'];u=1/(n-1);shots=[];provenance=[]
        hashes=set()
        for source in oldrow['sources']:
            run=Path(source['run']);name=source['name']
            batch,meta=load_batch(run,name,n,source['shots'])
            assert meta['job_id']==source['job_id'] and meta['result_sha256']==source['result_sha256']
            assert meta['job_id'] not in seen
            seen.add(meta['job_id'])
            job=json.loads((run/'execute'/name/'job.json').read_text())
            assert job['platform']=='nexus:H2-1E' and job['options']==f.CONFIG['options']
            assert abs(job['delta_t_seconds']-u)<1e-14
            bitcode_hash=hashlib.sha256(Path(job['program']).read_bytes()).hexdigest()
            assert bitcode_hash==source['bitcode_sha256'];hashes.add(bitcode_hash)
            provenance.append(dict(meta,run=str(run),name=name,bitcode_sha256=bitcode_hash,offset=len(shots)))
            shots.extend(batch)
        assert len(hashes)==1 and len(shots)==oldrow['shots']
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=len(shots))
        graph=paper_graph(spec,P_EXT,0,P_READ)
        syn,dat=bits_from_shots(shots,n,4,9);rec=record_from_bits(spec,syn,dat)
        assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(dat[:,[0,3,6]],axis=1))
        baseline_dem=dem_for(graph)
        baseline_pred=PyMatchingDecoder(baseline_dem).decode_batch(rec.detectors)
        baseline_fail=np.any(baseline_pred!=rec.observables,axis=1)
        assert int(baseline_fail.sum())==oldrow['logical_failures'], 'Baseline failed to reproduce'
        noise=round_probabilities(n,u)
        # No-idle limit must reproduce the old graph byte-for-byte.
        # Use the original model's evaluated probability to avoid a spurious
        # byte mismatch from 1-(1-p) floating-point roundoff in PaperNoise.
        baseline_round=graph.noise.round_noise(0,u)
        assert dem_for(graph,noise=[baseline_round]*n)==baseline_dem
        dem=dem_for(graph,noise=noise)
        path=demdir/f'n{n}.dem';path.write_text(dem)
        pred=PyMatchingDecoder(dem).decode_batch(rec.detectors)
        fail=np.any(pred!=rec.observables,axis=1)
        corrected=int(np.count_nonzero(baseline_fail & ~fail))
        harmed=int(np.count_nonzero(~baseline_fail & fail))
        k=int(fail.sum());total=len(shots)
        assert k==int(baseline_fail.sum())-corrected+harmed
        disagreements=corrected+harmed
        pv=float(binomtest(corrected,disagreements,.5).pvalue) if disagreements else 1.
        for source in provenance:
            start=source['offset'];stop=start+source['shots']
            source['updated_failures']=int(fail[start:stop].sum())
            source['baseline_failures']=int(baseline_fail[start:stop].sum())
        saved[f'n{n}_baseline_prediction']=baseline_pred[:,0]
        saved[f'n{n}_updated_prediction']=pred[:,0]
        saved[f'n{n}_baseline_failure']=baseline_fail
        saved[f'n{n}_updated_failure']=fail
        rows.append(dict(rounds=n,delta_t_seconds=u,shots=total,
            logical_failures=k,logical_error_probability=k/total,wilson_95=wilson(k,total),
            baseline_failures=int(baseline_fail.sum()),baseline_probability=float(baseline_fail.mean()),
            baseline_wilson_95=oldrow['wilson_95'],p_idle=idle_probability(u),
            p_data_first_round=P_EXT,p_data_after_sleep=noise[-1].p_data,p_read=P_READ,
            corrected_baseline_failures=corrected,new_failures=harmed,
            paired_exact_mcnemar_p=pv,probability_change=(harmed-corrected)/total,
            dem_path=str(path),dem_sha256=hashlib.sha256(dem.encode()).hexdigest(),sources=provenance))
        print(n,k,total,'old',int(baseline_fail.sum()),'corrected/new',corrected,harmed,flush=True)
    assert len(seen)==18 and sum(r['shots'] for r in rows)==13000
    np.savez_compressed(OUT.with_suffix('.npz'),**saved)
    fixed=sum(r['corrected_baseline_failures'] for r in rows);harmed=sum(r['new_failures'] for r in rows)
    result=dict(platform='nexus:H2-1E',distance=3,basis='X',total_shots=13000,unique_jobs=18,
        original_analysis_sha256=hashlib.sha256(OLD.read_bytes()).hexdigest(),
        total_requested_sleep_seconds=1,extraction_duration_neglected=True,parallel_sleep_verified=False,
        decoder_model=dict(p_ext=P_EXT,p_read=P_READ,linear_rate_per_second=LINEAR_RATE,
            quadratic_frequency_cycles_per_second=QUADRATIC_FREQUENCY_HZ,incoherent_frequency_multiplier=INCOHERENT_FACTOR,
            p_linear='0.0028*u',p_quadratic='sin(pi*0.043*2*u)^2',
            p_idle='p_linear + p_quadratic - 2*p_linear*p_quadratic',
            p_data_after_sleep='p_ext + p_idle - 2*p_ext*p_idle',
            placement='p_ext before first extraction; composed p_ext XOR idle before each later extraction; no final sleep',
            readout='symmetric independent p_read=.001 for all syndrome and final data bits, unchanged',
            data_faults='independent Z faults per data qubit/round; ideal product checks',
            source_policy='published H2-1E defaults inspected 2026-11-05; not a snapshot of the actual execution calibration',
            training='none; parameters fixed from published defaults and original baseline, not selected on logical outcomes',
            sources=SOURCES),rows=rows,
        paired_aggregate=dict(corrected=fixed,new_failures=harmed,net_failure_reduction=fixed-harmed,
            exact_mcnemar_p=float(binomtest(fixed,fixed+harmed,.5).pvalue) if fixed+harmed else 1.))
    OUT.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    report(result);plot(result)


def report(result):
    lines=['# Sleep-dependent phenomenological MWPM: all saved H2-1E d=3 shots','',
        '13,000 shots, 18 jobs, N=2,3,4,5,6,7,8,10,20,40. Same fixed-requested-sleep dataset and logical observable as the original PDF. Each raw-file hash and submitted-bitcode hash verified; no duplicate jobs; original baseline failure counts reproduced exactly at every N. No provider access, new jobs, HQCs or injected noise.','',
        '## Fixed model (no training or tuning on outcomes)','',
        'Use published H2-1E linear rate r=.0028/s, quadratic frequency nu=.043 cycles/s (units 2*pi rad/s), and stabilizer incoherence factor m=2. Thus p_lin(u)=r*u, p_quad(u)=sin(pi*nu*m*u)^2. Independent Z channels compose by odd parity, p_idle=p_lin+p_quad-2*p_lin*p_quad; two Z faults cancel.','',
        'Retain original phenomenological extraction floor p_ext=.002 and symmetric syndrome/final-readout flip probability p_read=.001. These are baseline assumptions, not newly derived from gate specifications. First-round p_data=.002, and the remaining N-1 rounds use p_data=p_ext+p_idle-2*p_ext*p_idle. Exactly N-1 modeled sleep intervals, none before first extraction or after last. The independent ideal-product-check model and PyMatching algorithm are unchanged.','',
        'This adds time dependence to matching weights, not to already-recorded shots. The quoted published defaults are not independently confirmed execution-time parameters. Each qubit is assumed to experience exactly u of additional idling per gap; physical parallel overlap and detailed transport/extraction timing remain unverified. Readout asymmetry and gate-correlated faults are not added.','',
        '| N | u (s) | p_idle(u) | p_data after sleep | Baseline P_L | Updated failures / shots | Updated P_L | 95% Wilson interval | Corrected / new failures |',
        '|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in result['rows']:
        lo,hi=r['wilson_95']
        lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.7g} | {r['p_idle']:.7g} | {r['p_data_after_sleep']:.7g} | {100*r['baseline_probability']:.2f}% | {r['logical_failures']}/{r['shots']} | {100*r['logical_error_probability']:.2f}% | {100*lo:.2f}-{100*hi:.2f}% | {r['corrected_baseline_failures']} / {r['new_failures']} |")
    best=min(result['rows'],key=lambda r:r['logical_error_probability'])
    paired=result['paired_aggregate']
    lines+=['',f"Updated sample minimum: N={best['rounds']}, u={best['delta_t_seconds']:.7g} s, {best['logical_failures']}/{best['shots']}={100*best['logical_error_probability']:.2f}%. This sample minimum is not a uniquely established optimum.",'',
        f"Paired comparison across all recorded shots: {paired['corrected']} baseline failures corrected, {paired['new_failures']} new failures introduced, net {paired['net_failure_reduction']} fewer failures. Exact two-sided McNemar p={paired['exact_mcnemar_p']:.6g}, testing symmetric decoder discordances under independent-shot assumptions. This aggregate describes the actual unequal shot allocation across settings, not a uniform-N average or a memory operating point. Per-setting paired comparisons are exploratory and unadjusted for multiple testing.",'',
        'Probabilities are per full experiment. The requested-sleep-normalized rate is P_L/(1 s); actual total-time rates remain unknown because extraction duration is neglected. Wilson intervals cover shot sampling only, not model or scheduling uncertainty. No smooth functional fit is used: plotted connecting lines are guides to the eye. A more realistic DEM need not improve this finite dataset, and improvement here does not identify the true backend noise model. The decoder policy was chosen after inspecting prior experiments, so this is an exploratory comparison, despite no numerical training on logical labels.','',
        '## Sources and artifacts','',
        *[f'- {url}' for url in SOURCES],
        '- JSON: all per-setting parameters, raw/bitcode hashes and per-batch failure counts.',
        '- NPZ: baseline/updated per-shot predictions and failure masks, ordered by JSON sources and offsets.',
        '- results/decoders/d3_sleep_dependent/nN.dem: exact matching models; SHA-256 in JSON.',
        '- Baseline files and PDF were preserved.']
    if paired['corrected']+paired['new_failures']==0:
        lines.insert(4,'Result: the two DEMs have different fault probabilities/weights, but predict identical logical corrections on every recorded shot. Updated probabilities and confidence intervals therefore exactly equal the baseline. This reweighting provides no observed decoding gain; it does not show that the physical idle probability is independent of sleep.\n')
    OUT.with_suffix('.md').write_text('\n'.join(lines)+'\n')


def plot(result):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter
    plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    rows=sorted(result['rows'],key=lambda r:r['delta_t_seconds'])
    x=np.array([r['delta_t_seconds'] for r in rows])
    fig,(ax,zoom)=plt.subplots(1,2,figsize=(12,5.8),gridspec_kw={'width_ratios':[1.4,1]},layout='constrained')
    for a in [ax,zoom]:
        for field,interval,color,marker,label in [
            ('baseline_probability','baseline_wilson_95','#8a9097','s','Original fixed DEM'),
            ('logical_error_probability','wilson_95','#147c68','o','Sleep-dependent DEM')]:
            y=np.array([r[field] for r in rows]);error=np.array([[r[field]-r[interval][0] for r in rows],[r[interval][1]-r[field] for r in rows]])
            a.plot(x,y,ls=':',color=color,alpha=.65,lw=1)
            a.errorbar(x,y,yerr=error,fmt=marker,mfc='white' if field=='baseline_probability' else color,color=color,
                       ms=6,capsize=3,elinewidth=1.1,label=label,zorder=3 if field=='baseline_probability' else 4)
        a.set_xlabel('Sleep interval Delta t (seconds)');a.grid(axis='y',alpha=.2)
        a.yaxis.set_major_formatter(PercentFormatter(1))
    ax.set_xscale('log');ax.set_xlim(.022,1.25);ax.set_ylim(0,.17)
    ax.set_ylabel('Logical error probability per experiment')
    ax.set_title('All settings (logarithmic interval axis)',loc='left',fontsize=12)
    ax.legend(frameon=False,loc='upper center',fontsize=10)
    if result['paired_aggregate']['corrected']+result['paired_aggregate']['new_failures']==0:
        ax.text(.5,.77,'Both decoders agree on all recorded shots',transform=ax.transAxes,
                ha='center',fontsize=9,color='#52636c')
    zoom.set_xlim(.09,.38)
    top=max(r['wilson_95'][1] for r in rows if .09<r['delta_t_seconds']<.38)
    zoom.set_ylim(0,max(.042,top*1.25))
    zoom.set_title('Intermediate intervals',loc='left',fontsize=12)
    for r in rows:
        v=max(r['baseline_wilson_95'][1],r['wilson_95'][1])
        ax.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],v),xytext=(0,7),textcoords='offset points',ha='center',fontsize=8)
        if .09<r['delta_t_seconds']<.38:
            zoom.annotate(f"N={r['rounds']}",(r['delta_t_seconds'],v),xytext=(0,7),textcoords='offset points',ha='center',fontsize=9)
    fig.suptitle('d=3 X-memory on H2-1E: re-decoding the same 13,000 shots',fontsize=14)
    fig.supxlabel('95% Wilson intervals. Dotted lines: guides only. Requested sleep = 1 s; extraction duration neglected.',fontsize=9)
    path=ROOT/'results/figures/d3_sleep_dependent_redecode'
    fig.savefig(path.with_suffix('.png'),dpi=200,bbox_inches='tight')
    fig.savefig(path.with_suffix('.svg'),bbox_inches='tight')


if __name__=='__main__':main()
