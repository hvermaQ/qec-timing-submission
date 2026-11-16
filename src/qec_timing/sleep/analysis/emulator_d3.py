"""d=3 X-memory on the H2-1E / H2-2E emulators: decode saved shots; never submit jobs.

Ported from SG_final_round/src/ (calculations verbatim; only paths and writes changed):

    sweep(kind, platform)        analyze_d3_sleep_sweep.py          HISTORICAL
    characterize(platform)       characterize_h2_2e_sleep.py
    fixed_sleep_500(partial)     analyze_fixed_sleep_d3.py          HISTORICAL
    load_batch, fixed_sleep_combined()  analyze_fixed_sleep_refinement.py  HISTORICAL
    fixed_sleep_all()            analyze_fixed_sleep_all.py (fits in fits.py, figure in plots.py)
    redecode_sleep_dependent()   redecode_d3_sleep_dependent.py (constants in decoder.py)

Decoders: the two-round sweeps and the fixed-sleep analyses use the fixed historical
phenomenological MWPM (p_data=0.002 per round, p_read=0.001, lambda=0, with sensitivity
counts at p_data=0.02 and 0.1). The re-decode uses the legacy sleep-dependent H2-1E policy
(`decoder.legacy_round_probabilities`, p_ext=0.002).

Writing: top-level results go to results/sleep/ (`paths.RESULTS`), figures to
results/sleep/figures/. DEMs, manifest and collection-status updates that the originals wrote
into programs/ and runs/ go to the store/sleep/ mirror (`paths.store`).
"""
import hashlib
import importlib.metadata
import json
from dataclasses import replace

import numpy as np

from .. import paths
from ..builders import d3 as d3_builder, d3_sweep
from ..decoder import (LEGACY_P_EXT as P_EXT, LEGACY_P_READ as P_READ, LINEAR_RATE, QUADRATIC_FREQUENCY_HZ,
                       INCOHERENT_FACTOR, LEGACY_SOURCES as SOURCES, idle_probability,
                       legacy_round_probabilities as round_probabilities)
from ..jobs import accepted
from ..stats import wilson
from ..unpack import unpack

SOURCE = paths.BASELINE_D3   # pinned d=3 baseline; .json holds the spec
FIXED_RUNS = ['d3_fixed_sleep_690baca08b24dfd2',
              'd3_fixed_sleep_refinement_3bb6e107a0ff6de3',
              'd3_fixed_sleep_resolution_c2380924e8c69578']


def qec():
    """The main-repo pieces the decoders need (imported lazily: stim/pymatching)."""
    from qec_timing.backends.stim_phenom import dem_for
    from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
    from qec_timing.hardware.collect import paper_graph
    from qec_timing.hardware.providers import _register_builtins
    from qec_timing.hardware.records import bits_from_shots, record_from_bits
    from qec_timing.schedule import Schedule
    from qec_timing.spec import spec_from_json
    return dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json


def base_spec(spec_from_json, source=SOURCE):
    """The spec stored with a pinned baseline program (`<source>.json`)."""
    return spec_from_json(json.loads(paths.read_text(source.with_suffix('.json')))['spec'])


# --------------------------------------------------------------------------- two-round sweeps

def sweep(kind='three_point', platform='nexus:H2-1E'):
    """HISTORICAL. Decode a two-round d=3 sleep sweep (3-point H2-1E; 5-point H2-1E/H2-2E).

    Decoder: fixed historical phenomenological MWPM, p_data=0.002, p_read=0.001, lambda=0
    (sensitivity counts at p_data=0.02, 0.1). Was `analyze_d3_sleep_sweep.main(five_point, platform)`.
    -> results/sleep/d3_sleep_sweep_1000.json or d3_sleep_five_point_<platform>_1000.json;
    DEMs, the manifest and collection-status updates -> store/sleep/.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, _, spec_from_json = qec()
    five_point = kind == 'five_point'
    build = d3_sweep.sweep(kind, platform)
    RUNS, BUILD, CONFIG, VARIANTS = build.runs, build.folder, build.config, build.extra['variants']
    SHOTS = d3_sweep.SHOTS
    output_name = ('d3_sleep_five_point_' + platform.split(':')[1].lower().replace('-', '_') + '_1000.json'
                   if five_point else 'd3_sleep_sweep_1000.json')
    _register_builtins()
    spec = base_spec(spec_from_json)
    # Freeze the historical d3 decoder across settings; no fitting to returned data.
    decoder_specs = {str(p): dict(p_data=p, p_read=.001, lam=0) for p in [.002, .02, .1]}
    decoders = {}
    for key, params in decoder_specs.items():
        dem = dem_for(paper_graph(spec, params['p_data'], 0, params['p_read']))
        paths.write_text(paths.store(BUILD/f'decoder_p{key}.dem'), dem)
        params['dem_sha256'] = hashlib.sha256(dem.encode()).hexdigest()
        decoders[key] = PyMatchingDecoder(dem)
    rows = []
    for name, duration in VARIANTS.items():
        folder = RUNS/'execute'/name
        job = json.loads(paths.read_text(folder/'job.json'))
        assert accepted(job), f'Job not completed successfully: {name}'
        raw = json.loads(paths.read_text(folder/'result_0.txt'))
        syndromes, data = bits_from_shots(unpack(raw, SHOTS, 2), 2, 4, 9)
        rec = record_from_bits(spec, syndromes, data)
        failures = {key: int(np.any(decoder.decode_batch(rec.detectors) != rec.observables, axis=1).sum())
                    for key, decoder in decoders.items()}
        k = failures['0.002']
        rows.append(dict(duration_raw=duration, shots=rec.shots, logical_failures=k,
                         logical_error_rate=k/rec.shots, wilson_95=wilson(k, rec.shots),
                         raw_logical_flips=int(rec.observables.sum()),
                         per_data_qubit_flips=data.sum(axis=0).tolist(),
                         inter_round_syndrome_changes=(syndromes[:, 1] ^ syndromes[:, 0]).sum(axis=0).tolist(),
                         detector_rates=rec.detectors.mean(axis=0).tolist(),
                         decoder_sensitivity_failures=failures, job_id=job['job_id'],
                         result_sha256=hashlib.sha256((folder/'result_0.txt').read_bytes()).hexdigest(),
                         returned_properties=raw.get('properties')))
    comparisons = []
    from scipy.stats import fisher_exact
    for row in rows[1:]:
        comparisons.append(dict(duration_raw=row['duration_raw'],
            difference_vs_zero=row['logical_error_rate']-rows[0]['logical_error_rate'],
            fisher_two_sided_p=float(fisher_exact([[row['logical_failures'], SHOTS-row['logical_failures']],
                 [rows[0]['logical_failures'], SHOTS-rows[0]['logical_failures']]]).pvalue)))
    # `build` stays relative to the original SG_final_round root, as in the committed results.
    result = dict(CONFIG, build='programs/' + build.name, rows=rows,
                  primary_decoder='Fixed historical phenomenological MWPM: p_data=.002, p_read=.001, lam=0',
                  decoder_models=decoder_specs, comparisons=comparisons,
                  versions={m: importlib.metadata.version(m) for m in ['numpy', 'stim', 'pymatching']},
                  actual_billed_hqc=None, all_packed_shots_match_formatted_counts=True,
                  logical_observable='X on data qubits 0,3,6; failure after predicted logical correction')
    paths.write_json(paths.RESULTS/output_name, result)
    manifest = json.loads(paths.read_text(BUILD/'manifest.json'))
    manifest['execution_status'] = 'completed_with_parallel_sleep_unverified'
    manifest['analysis'] = 'results/' + output_name
    paths.write_json(paths.store(BUILD/'manifest.json'), manifest)
    collection_path = RUNS/'collection_status.json'
    if collection_path.exists():
        collection = json.loads(paths.read_text(collection_path))
        collection['analysis_status'] = 'completed_on_user_request'
        collection['analysis'] = manifest['analysis']
        paths.write_json(paths.store(collection_path), collection)
    print(json.dumps(result, indent=2))
    return result


def characterize(platform='nexus:H2-2E'):
    """Shot-level uncertainty and descriptive growth in the five-point sweeps' data errors.

    No decoder (raw final data bits). -> results/sleep/d3_sleep_five_point_<platform>_noise_characterization.json
    """
    build = d3_sweep.sweep('five_point', platform)
    VARIANTS = build.extra['variants']
    rng = np.random.default_rng(20261102)
    rows, bootstraps = [], []
    for name, u in VARIANTS.items():
        raw = json.loads(paths.read_text(build.runs/'execute'/name/'result_0.txt'))
        shots = unpack(raw, d3_sweep.SHOTS, 2)
        data = np.array([[s[f'm{i}'] for i in range(9)] for s in shots], dtype=float)
        weight = data.sum(axis=1).astype(int)
        hist = np.bincount(weight, minlength=10)
        # Resample complete shots: retain dependence among the nine qubits.
        draws = rng.multinomial(len(shots), hist/len(shots), size=10000)
        boot = draws @ np.arange(10) / (len(shots)*9)
        bootstraps.append(boot)
        rows.append(dict(duration_raw=u, mean_data_error=float(data.mean()),
            shot_bootstrap_95=np.quantile(boot, [.025, .975]).tolist(),
            shot_mean_standard_error=float((weight/9).std(ddof=1)/np.sqrt(len(shots))),
            per_qubit_error=data.mean(axis=0).tolist(), fault_weight_histogram=hist.tolist()))
    p0 = rows[0]['mean_data_error']
    for row, boot in zip(rows, bootstraps):
        # Under an independent XOR composition of background and added flip channels.
        row['effective_extra_flip_probability'] = (row['mean_data_error']-p0)/(1-2*p0)
        extra_boot = (boot-bootstraps[0])/(1-2*bootstraps[0])
        row['effective_extra_flip_bootstrap_95'] = np.quantile(extra_boot, [.025, .975]).tolist()
    # Descriptive fit in RAW argument units; no inference of physical seconds.
    u = np.array(list(VARIANTS.values()))
    p = np.array([r['mean_data_error'] for r in rows])
    # Fix the measured background; coefficients may be negative in this unconstrained diagnostic.
    a,b = np.linalg.lstsq(np.column_stack([u, u*u]), p-p0, rcond=None)[0]
    result = dict(rows=rows, bootstrap_repetitions=10000, bootstrap_seed=20261102,
        extra_channel_assumption='p(u)=p0+(1-2*p0)*q(u); background unchanged, added XOR flip channel',
        descriptive_fit=dict(form='mean_data_error(u) = measured_p0 + a*u + b*u^2',
            p0=p0, a_per_raw_argument=float(a), b_per_raw_argument_squared=float(b),
            fitted_values=(p0+a*u+b*u*u).tolist(),
            status='descriptive only; no physical rate calibration or model identification'),
        uncertainty_note='Shot bootstrap retains within-shot qubit correlation; assumes independent shots, no run-to-run variability measured')
    target = platform.split(':')[1].lower().replace('-', '_')
    paths.write_json(paths.RESULTS/f'd3_sleep_five_point_{target}_noise_characterization.json', result)
    print(json.dumps(result, indent=2))
    return result


# --------------------------------------------------------------------------- fixed total sleep

def _execute_parts(build):
    """The original `fixed_sleep_d3.jobs('execute')`: (plan row, run folder name, shots)."""
    for p in build.plan:
        for i, shots in enumerate(p['parts']):
            yield p, p['name']+f'_part{i+1}', shots


def fixed_sleep_500(allow_partial=False):
    """HISTORICAL (superseded by fixed_sleep_all). Decode the coarse 500-shot fixed-sleep batch.

    Decoder: fixed historical phenomenological MWPM, p_data=0.002, p_read=0.001, lambda=0
    (sensitivity at 0.02, 0.1). Was `analyze_fixed_sleep_d3.main(allow_partial)`.
    -> results/sleep/d3_fixed_sleep_500[_partial].{json,md}; decoder_n*_p*.dem -> store/sleep/.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    f = d3_builder.fixed('coarse')
    _register_builtins()
    base=base_spec(spec_from_json)
    rows=[]
    for p in f.plan:
        n=p['rounds'];shots=[];ids=[]
        for plan,name,count in _execute_parts(f):
            if plan['rounds']!=n:continue
            dest=f.runs/'execute'/name
            j=json.loads(paths.read_text(dest/'job.json'))
            if not accepted(j):
                if allow_partial:continue
                raise RuntimeError(f'Incomplete {name}')
            shots+=unpack(json.loads(paths.read_text(dest/'result_0.txt')),count,n)
            ids.append(j['job_id'])
        if not shots:continue
        if not allow_partial:assert len(shots)==500
        total=len(shots)
        spec=replace(base,schedule=Schedule.rounds(p['delta_t_seconds'],n),shots=total)
        syn,dat=bits_from_shots(shots,n,4,9);rec=record_from_bits(spec,syn,dat)
        counts={}
        for assumed_p in [.002,.02,.1]:
            dem=dem_for(paper_graph(spec,assumed_p,0,.001))
            paths.write_text(paths.store(f.folder/f'decoder_n{n}_p{assumed_p}.dem'), dem)
            predicted=PyMatchingDecoder(dem).decode_batch(rec.detectors)
            counts[str(assumed_p)]=int(np.any(predicted!=rec.observables,axis=1).sum())
        k=counts['0.002']
        rows.append(dict(rounds=n,delta_t_seconds=p['delta_t_seconds'],total_requested_sleep_seconds=1,
            shots=total,complete=(total==500),logical_failures=k,logical_error_probability=k/total,wilson_95=wilson(k,total),
            raw_logical_parity_flips=int(rec.observables.sum()),decoder_sensitivity_failures=counts,
            mean_data_error=float(dat.mean()),detector_rates=rec.detectors.mean(axis=0).tolist(),job_ids=ids))
    result=dict(f.config,rows=rows,primary_decoder='fixed historical MWPM p_data=.002 p_read=.001; same prescription across N',
        interpretation='Fixed requested sleep only; extraction duration neglected; no minimum presumed')
    suffix='_partial' if allow_partial else ''
    paths.write_json(paths.RESULTS/('d3_fixed_sleep_500'+suffix+'.json'), result)
    lines=['# d=3 X memory: fixed requested sleep of one second','',
        'H2-1E through Aqora; 500 shots planned per setting; available-shot denominators shown below. Extraction duration is neglected. Sleep arguments are treated as seconds; overlap remains unverified. Logical probabilities are per complete experiment.','',
        '| Rounds N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |',
        '|---|---:|---:|---:|---:|']
    for r in rows:
        lo,hi=r['wilson_95'];lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.9g} | {r['logical_failures']} / {r['shots']} | {r['logical_error_probability']:.4f} | {lo:.4f} - {hi:.4f} |")
    best=min(rows,key=lambda r:r['logical_error_probability'])
    lines+=['',f"Lowest observed probability: N={best['rounds']}, Delta t={best['delta_t_seconds']:.9g} s. This is a sample minimum, not automatically a statistically resolved interior optimum.",'',
        'Decode with the same phenomenological MWPM prescription across N; compare sensitivity counts in JSON. All packed shots cross-checked against formatted counts. No postselection or artificial faults. One job per setting except N=40 split into two 250-shot jobs; these samples do not establish run-to-run stability. Interpretation must account for unequal extraction durations, decoder mismatch and uncertainty. Do not claim a U-shaped curve unless both sides are supported by data.']
    paths.write_text(paths.RESULTS/('d3_fixed_sleep_500'+suffix+'.md'), '\n'.join(lines)+'\n')
    print(json.dumps(result,indent=2))
    return result


def load_batch(run,name,n,expected):
    """Shots of one execute job, checked against its record and the run's collection status."""
    dest=run/'execute'/name
    job=json.loads(paths.read_text(dest/'job.json'))
    assert accepted(job) and job['shots']==expected and job['rounds']==n
    path=dest/'result_0.txt'
    col=json.loads(paths.read_text(run/'collection_status.json'))
    row=next(x for x in col['jobs'] if x['name']==name)
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    assert digest==row['raw_sha256']['result_0.txt']
    return unpack(json.loads(paths.read_text(path)),expected,n),dict(job_id=job['job_id'],shots=expected,result_sha256=digest)


def fixed_sleep_combined(plot=True):
    """HISTORICAL (superseded by fixed_sleep_all). Coarse + refinement batches combined.

    Decoder: fixed historical phenomenological MWPM, p_data=0.002, p_read=0.001, lambda=0.
    Was `analyze_fixed_sleep_refinement.main()`; `configure_refinement()` is now the explicit
    refinement build. -> results/sleep/d3_fixed_sleep_combined.{json,md} + figure;
    refinement decoder_n*_p*.dem -> store/sleep/.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    _register_builtins()
    oldrun=d3_builder.fixed('coarse').runs
    original=json.loads(paths.read_text(paths.RESULTS/'d3_fixed_sleep_500.json'))
    rows=[r for r in original['rows'] if r['rounds']!=5]
    base=base_spec(spec_from_json)
    f=d3_builder.fixed('refinement')
    for p in f.plan:
        n=p['rounds'];newshots=500 if n==5 else 1000
        shots,meta=load_batch(f.runs,f'n{n}_part1',n,newshots)
        sources=[meta]
        if n==5:
            old,meta=load_batch(oldrun,'n5_part1',n,500)
            shots=old+shots;sources.insert(0,meta)
        assert len(shots)==1000
        spec=replace(base,schedule=Schedule.rounds(1/(n-1),n),shots=1000)
        syn,dat=bits_from_shots(shots,n,4,9);rec=record_from_bits(spec,syn,dat)
        counts={}
        for p_data in [.002,.02,.1]:
            dem=dem_for(paper_graph(spec,p_data,0,.001))
            paths.write_text(paths.store(f.folder/f'decoder_n{n}_p{p_data}.dem'), dem)
            pred=PyMatchingDecoder(dem).decode_batch(rec.detectors)
            counts[str(p_data)]=int(np.any(pred!=rec.observables,axis=1).sum())
        k=counts['0.002']
        rows.append(dict(rounds=n,delta_t_seconds=1/(n-1),shots=1000,logical_failures=k,
            logical_error_probability=k/1000,wilson_95=wilson(k,1000),decoder_sensitivity_failures=counts,
            mean_data_error=float(dat.mean()),sources=sources,job_ids=[m['job_id'] for m in sources]))
    rows.sort(key=lambda r:r['delta_t_seconds'])
    result=dict(platform='nexus:H2-1E',distance=3,basis='X',total_requested_sleep_seconds=1,
        extraction_duration_neglected=True,parallel_sleep_verified=False,
        primary_decoder='phenomenological MWPM p_data=.002 per round, p_read=.001, lambda=0; not calibrated gate-level DEM',rows=rows)
    paths.write_json(paths.RESULTS/'d3_fixed_sleep_combined.json', result)
    lines=['# d=3 fixed requested sleep: combined refinement results','',
        'H2-1E; total requested sleep one second. Extraction duration neglected. Fixed phenomenological PyMatching decoder, p_data=.002, p_read=.001, lambda=0. These are decoder assumptions, not injected noise.','',
        '| N | Delta t (s) | Failures / shots | Logical error probability | 95% Wilson interval |',
        '|---|---:|---:|---:|---:|']
    for r in rows:
        lo,hi=r['wilson_95'];lines.append(f"| {r['rounds']} | {r['delta_t_seconds']:.9g} | {r['logical_failures']} / {r['shots']} | {100*r['logical_error_probability']:.2f}% | {100*lo:.2f}% - {100*hi:.2f}% |")
    best=min(rows,key=lambda r:r['logical_error_probability'])
    lines+=['',f"Lowest observed probability: N={best['rounds']}, Delta t={best['delta_t_seconds']:.9g} s. This does not establish a unique optimal interval.",'',
        'N=5 pools only its original fixed-sleep 500 shots with the new 500 shots; N=4,6,7,8 use new 1,000-shot batches. N=2,10,20,40 retain original 500-shot results, with both N=40 partitions included. No data are counted twice. All new/refinement packed shots match formatted counts and saved hashes. The original coarse analysis is unchanged. Error bars reflect shot sampling, not systematic decoder mismatch, scheduling uncertainty or run-to-run drift. The refinement was selected after the coarse sweep; minimum comparisons are exploratory.']
    paths.write_text(paths.RESULTS/'d3_fixed_sleep_combined.md', '\n'.join(lines)+'\n')
    if plot:
        from .. import plots
        plots.fixed_sleep_combined(rows)
    for r in sorted(rows,key=lambda r:r['rounds']):print(r['rounds'],r['logical_failures'],r['shots'],r['wilson_95'],r['decoder_sensitivity_failures'])
    return result


def fixed_sleep_all(plot=True):
    """Pool every fixed-sleep H2-1E batch once (18 jobs, 13,000 shots), retaining the established decoder.

    Decoder: fixed phenomenological MWPM, p_data=0.002, p_read=0.001, lambda=0 (sensitivity
    at 0.02, 0.1). Paper-linear and quadratic fits with 1,000-sample bootstraps (fits.py).
    -> results/sleep/d3_fixed_sleep_all_shots.{json,md}, results/sleep/decoders/d3_fixed_sleep_all_shots/,
    figure. Records each batch's run directory (`run`), which redecode_sleep_dependent re-opens.
    """
    from scipy.stats import chi2, fisher_exact
    from .. import fits, reports
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    _register_builtins()
    runs=[paths.RUNS/name for name in FIXED_RUNS]
    options=d3_builder.fixed('coarse').config['options']
    grouped={}; seen=set()
    base=base_spec(spec_from_json)
    for run in runs:
        status=json.loads(paths.read_text(run/'collection_status.json'))
        assert status['all_results_stored']
        for j in status['jobs']:
            assert j['status']=='COMPLETED' and j['stored']
            assert j['job_id'] not in seen
            seen.add(j['job_id'])
            n=j['rounds']; count=j['shots']
            shots,meta=load_batch(run,j['name'],n,count)
            # Verify eligibility from the source job, not its directory alone.
            job=json.loads(paths.read_text(run/'execute'/j['name']/'job.json'))
            assert job['platform']=='nexus:H2-1E'
            assert abs(job['delta_t_seconds']-1/(n-1))<1e-14
            assert job['options']==options
            bitcode_hash=hashlib.sha256(paths.resolve_recorded(job['program']).read_bytes()).hexdigest()
            grouped.setdefault(n,[]).append((shots,dict(meta,run=str(run),name=j['name'],bitcode_sha256=bitcode_hash)))
    rows=[]
    demdir=paths.RESULTS/'decoders/d3_fixed_sleep_all_shots'
    for n,batches in sorted(grouped.items()):
        assert len({meta['bitcode_sha256'] for _,meta in batches})==1
        total=sum(len(shots) for shots,_ in batches)
        spec=replace(base,schedule=Schedule.rounds(1/(n-1),n),shots=total)
        syn,dat=bits_from_shots([s for shots,_ in batches for s in shots],n,4,9)
        rec=record_from_bits(spec,syn,dat)
        counts={};primary=None
        for p in [.002,.02,.1]:
            dem=dem_for(paper_graph(spec,p,0,.001))
            paths.write_text(demdir/f'n{n}_p{p}.dem', dem)
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
    all_fits=fits.fixed_sleep_all(u,k,ns)
    nll=fits.fixed_sleep_all_nll
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
                paper='https://arxiv.org/html/2608.06242v2',rows=rows,fits=all_fits,
                batch_homogeneity=dict(deviance=homogeneity_deviance,dof=homogeneity_df,
                                      asymptotic_p=float(chi2.sf(homogeneity_deviance,homogeneity_df))),
                exploratory_minimum_contrasts=contrasts)
    paths.write_json(paths.RESULTS/'d3_fixed_sleep_all_shots.json', result)
    reports.fixed_sleep_all_md(result)
    if plot:
        from .. import plots
        plots.fixed_sleep_all(result)
    return result


# --------------------------------------------------------------------------- sleep-dependent re-decode

def redecode_sleep_dependent(plot=True):
    """Re-decode the 13,000 saved fixed-sleep shots with independently specified idle weights.

    Decoder: legacy sleep-dependent phenomenological MWPM (decoder.legacy_round_probabilities:
    p_ext=0.002, p_read=0.001, p_lin=0.0028*u, p_quad=sin(pi*0.043*2*u)^2; published H2-1E
    defaults), compared shot by shot with the fixed baseline. No provider access, fitting,
    logical-label training or modification of old results. Re-opens the `run` directories
    recorded in d3_fixed_sleep_all_shots.json via `paths.resolve_recorded`.
    -> results/sleep/d3_sleep_dependent_redecode.{json,md,npz}, results/sleep/decoders/d3_sleep_dependent/, figure.
    """
    from scipy.stats import binomtest
    from .. import reports
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    OLD=paths.RESULTS/'d3_fixed_sleep_all_shots.json'
    OUT=paths.RESULTS/'d3_sleep_dependent_redecode'
    options=d3_builder.fixed('coarse').config['options']
    _register_builtins()
    old=json.loads(paths.read_text(OLD))
    base=base_spec(spec_from_json)
    demdir=paths.RESULTS/'decoders/d3_sleep_dependent'
    seen=set();rows=[];saved={}
    for oldrow in old['rows']:
        n=oldrow['rounds'];u=1/(n-1);shots=[];provenance=[]
        hashes=set()
        for source in oldrow['sources']:
            run=paths.resolve_recorded(source['run']);name=source['name']
            batch,meta=load_batch(run,name,n,source['shots'])
            assert meta['job_id']==source['job_id'] and meta['result_sha256']==source['result_sha256']
            assert meta['job_id'] not in seen
            seen.add(meta['job_id'])
            job=json.loads(paths.read_text(run/'execute'/name/'job.json'))
            assert job['platform']=='nexus:H2-1E' and job['options']==options
            assert abs(job['delta_t_seconds']-u)<1e-14
            bitcode_hash=hashlib.sha256(paths.resolve_recorded(job['program']).read_bytes()).hexdigest()
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
        path=demdir/f'n{n}.dem';paths.write_text(path, dem)
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
    paths.save_npz(OUT.with_suffix('.npz'),**saved)
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
    paths.write_json(OUT.with_suffix('.json'), result)
    reports.redecode_d3_md(result)
    if plot:
        from .. import plots
        plots.redecode_d3(result)
    return result
