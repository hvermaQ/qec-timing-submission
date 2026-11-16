"""Physical H2-2 d=3 X-memory: pool and re-decode the saved hardware shots; never submit.

Ported from SG_final_round/src/ (calculations verbatim; only paths and writes changed):

    pooled()                 analyze_h2_2_hardware_pooled.py      HISTORICAL
    combine()                combine_h2_2_updated_decoder.py
    decoder_sensitivity()    test_h2_2_decoder_sensitivity.py (not a test, despite its old name)

The original combine and sensitivity scripts exec'd `unpack_hardware` out of
results/sleep/runs/h2_2_hardware_d3_x_t1_20261111/analyze.py; they now use the package copy
(`qec_timing.sleep.unpack.unpack_hardware`). That runs/ script is untouched.

Physical H2-2 decoder policy: /AGENTS.md (d=3: config/sleep/decoders/h2_2_decoder.json).
"""
import hashlib
import itertools
import json
from collections import Counter, defaultdict
from dataclasses import replace
from importlib.metadata import version

import numpy as np

from .. import paths
from ..decoder import POLICY, P_EXT, P_READ, legacy_round_probabilities as old_noise, round_probabilities
from ..stats import wilson
from ..unpack import unpack_hardware
from .emulator_d3 import base_spec, qec

POOLED_BATCHES = ['h2_2_hardware_d3_x_t1_20261111', 'h2_2_hardware_d3_x_t1_additional_20261112']
ALL_BATCHES = POOLED_BATCHES + ['h2_2_hardware_d3_x_t1_n2_n4_20261112', 'h2_2_hardware_d3_x_t1_n40_n3_n4_20261113']
ZERO_SLEEP_RUN = 'd3_h2_2_zero_sleep_n2_1000_20261112'


def pooled(plot=True):
    """HISTORICAL (superseded by combine). Pool the first two H2-2 d=3 batches (6,750 shots).

    Decoder: the legacy sleep-dependent phenomenological MWPM (p_ext=0.002, p_read=0.001,
    H2-1E published defaults), frozen in each batch's run-local analysis.json; that predates
    policy h2_2_p_ext_0_00117_20261112. Its output feeds decoder_sensitivity().
    -> results/sleep/h2_2_hardware_d3_all_shots.json + figure.
    """
    from scipy.stats import fisher_exact
    grouped = defaultdict(list)
    seen = set()
    for batch in POOLED_BATCHES:
        source = paths.RUNS / batch / 'analysis.json'
        analysis = json.loads(paths.read_text(source))
        assert analysis['platform'] == 'nexus:H2-2'
        for row in analysis['rows']:
            assert row['job_id'] not in seen
            seen.add(row['job_id'])
            grouped[row['rounds']].append(dict(batch=batch, **row))
    rows = []
    for n, batches in sorted(grouped.items()):
        assert len({r['dem_sha256'] for r in batches}) == 1
        shots = sum(r['shots'] for r in batches)
        failures = sum(r['logical_failures'] for r in batches)
        raw_errors = sum(r['data_bit_errors'] for r in batches)
        row = dict(rounds=n, interval_seconds=1/(n-1), shots=shots,
                   logical_failures=failures, logical_error_probability=failures/shots,
                   logical_wilson_95=wilson(failures, shots),
                   raw_data_bit_errors=raw_errors, data_bits=shots*9,
                   raw_data_error_probability=raw_errors/(shots*9),
                   per_qubit_error_counts=np.sum([r['per_qubit_error_counts'] for r in batches], axis=0).tolist(),
                   batches=batches)
        if len(batches) == 2:
            table = [[r['logical_failures'], r['shots']-r['logical_failures']] for r in batches]
            row['batch_difference_fisher_two_sided_p'] = float(fisher_exact(table)[1])
        rows.append(row)
    assert len(seen) == 10 and sum(r['shots'] for r in rows) == 6750
    summary = dict(platform='nexus:H2-2', distance=3, basis='X', total_requested_sleep_seconds=1,
                   total_shots=6750, total_jobs=len(seen),
                   decoder='Frozen sleep-dependent phenomenological MWPM', no_postselection=True,
                   mixed_schedule_total_failures=sum(r['logical_failures'] for r in rows), rows=rows)
    paths.write_json(paths.RESULTS / 'h2_2_hardware_d3_all_shots.json', summary)
    for r in rows:
        print(json.dumps({k:v for k,v in r.items() if k != 'batches'}), flush=True)
    print('Mixed-schedule failures:', summary['mixed_schedule_total_failures'])
    if plot:
        from .. import plots
        plots.h2_2_hardware_pooled(rows)
    return summary


def combine(plot=True):
    """Re-decode all 16 H2-2 d=3 jobs (10,750 shots) with the current approved policy.

    Decoder: policy h2_2_p_ext_0_00117_20261112 (config/sleep/decoders/h2_2_decoder.json),
    compared shot by shot with the legacy sleep-dependent decoder (p_ext=0.002).
    -> results/sleep/h2_2_hardware_p_ext_0_00117_10750_shots.{json,npz,md}, figure,
    results/sleep/decoders/h2_2_p_ext_0_00117_20261112/.
    """
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    OUT=paths.RESULTS/'h2_2_hardware_p_ext_0_00117_10750_shots'
    DEMS=paths.RESULTS/'decoders'/POLICY['policy_version']
    records=[p for batch in ALL_BATCHES for p in sorted((paths.RUNS/batch).glob('n*/job.json'))]
    records += [paths.RUNS/ZERO_SLEEP_RUN/'execute/job.json']
    _register_builtins()
    base=base_spec(spec_from_json)
    groups=defaultdict(list);seen=set();batchrows=[];arrays={}
    for path in records:
        job=json.loads(paths.read_text(path));jid=job['job_id'];assert jid not in seen;seen.add(jid)
        assert job['platform']=='nexus:H2-2' and job['options']=={'no_opt':True}
        assert job['job']['status']=='COMPLETED' and not job['job'].get('error')
        n,count,u=job['rounds'],job['shots'],job['delta_t_seconds'];total=job['total_requested_sleep_seconds']
        assert abs((n-1)*u-total)<1e-12 and total in [0,1]
        program=paths.resolve_recorded(job['program']);assert hashlib.sha256(program.read_bytes()).hexdigest()==job['program_sha256']
        assert len(job['results'])==1
        result=job['results'][0];assert not result['error'];rawpath=path.parent/f"result_{result['index']}.txt";raw=rawpath.read_bytes()
        digest=hashlib.sha256(raw).hexdigest();assert digest==result['raw_sha256']
        # Positive tick labels round indices only; explicit noise below uses actual u.
        spec=replace(base,schedule=Schedule.rounds(u if u else 1.,n),shots=count)
        syn,data=bits_from_shots(unpack_hardware(json.loads(raw),count,n),n,4,9);rec=record_from_bits(spec,syn,data)
        assert np.array_equal(rec.observables[:,0],np.bitwise_xor.reduce(data[:,[0,3,6]],axis=1))
        dem=dem_for(paper_graph(spec,P_EXT,0,P_READ),noise=round_probabilities(n,u))
        dempath=DEMS/f"T{int(total)}_n{n}.dem"
        if dempath.exists():assert paths.read_text(dempath)==dem
        paths.write_text(dempath, dem)
        pred=PyMatchingDecoder(dem).decode_batch(rec.detectors);fail=np.any(pred!=rec.observables,axis=1)
        olddem=dem_for(paper_graph(spec,.002,0,.001),noise=old_noise(n,u))
        oldpred=PyMatchingDecoder(olddem).decode_batch(rec.detectors);oldfail=np.any(oldpred!=rec.observables,axis=1)
        historical=path.parent/'analysis.json'
        if historical.exists():assert json.loads(paths.read_text(historical))['logical_failures']==int(oldfail.sum())
        row=dict(job_id=jid,provider_id=job['job'].get('providerId'),job_record=str(path),raw_path=str(rawpath),raw_sha256=digest,program_sha256=job['program_sha256'],rounds=n,shots=count,interval_seconds=u,total_requested_sleep_seconds=total,logical_failures=int(fail.sum()),old_decoder_failures=int(oldfail.sum()),changed_predictions=int(np.any(pred!=oldpred,axis=1).sum()),corrected=int((oldfail & ~fail).sum()),harmed=int((~oldfail & fail).sum()),data_bit_errors=int(data.sum()),dem_path=str(dempath),dem_sha256=hashlib.sha256(dem.encode()).hexdigest())
        batchrows.append(row);groups[(total,n)].append((row,data,fail,oldfail))
        arrays[jid+'_failure']=fail;arrays[jid+'_prediction']=pred[:,0]
    rows=[];rng=np.random.default_rng(20261113)
    for (total,n),batches in sorted(groups.items()):
        data=np.concatenate([b[1] for b in batches]);shots=len(data);k=sum(b[0]['logical_failures'] for b in batches)
        hist=np.bincount(data.sum(axis=1).astype(int),minlength=10)
        boot=rng.multinomial(shots,hist/shots,size=20000)@np.arange(10)/(shots*9)
        r=dict(rounds=n,total_requested_sleep_seconds=total,interval_seconds=total/(n-1),shots=shots,jobs=len(batches),logical_failures=k,logical_error_probability=k/shots,logical_wilson_95=wilson(k,shots),raw_data_bit_errors=int(data.sum()),data_bits=int(data.size),raw_data_error_probability=float(data.mean()),raw_data_shot_bootstrap_95=np.quantile(boot,[.025,.975]).tolist(),per_qubit_error_counts=data.sum(axis=0).tolist(),old_decoder_failures=sum(b[0]['old_decoder_failures'] for b in batches),changed_predictions=sum(b[0]['changed_predictions'] for b in batches),corrected=sum(b[0]['corrected'] for b in batches),harmed=sum(b[0]['harmed'] for b in batches),job_ids=[b[0]['job_id'] for b in batches])
        rows.append(r)
    assert len(seen)==16 and sum(r['shots'] for r in rows)==10750
    sweep=[r for r in rows if r['total_requested_sleep_seconds']==1];controls=[r for r in rows if r['total_requested_sleep_seconds']==0]
    assert sum(r['shots'] for r in sweep)==9750
    out=dict(platform='nexus:H2-2',distance=3,basis='X',decoder_policy=POLICY,total_unique_jobs=16,total_shots=10750,fixed_T1_shots=9750,control_shots=1000,no_postselection=True,uncertainty='Wilson 95% for logical probabilities; whole-shot bootstrap 95% for raw bit probabilities. Conditional on frozen decoder, no drift/model uncertainty.',calibration_note='p_ext was selected from the zero-sleep control; that control is not independent validation of its selected parameter.',versions={x:version(x) for x in ['numpy','stim','pymatching']},fixed_T1_rows=sweep,zero_sleep_controls=controls,batches=batchrows)
    paths.write_json(OUT.with_suffix('.json'), out);paths.save_npz(OUT.with_suffix('.npz'),**arrays)
    lines=['# Physical H2-2: all shots with updated sleep-dependent decoder','',f"16 unique jobs, 10,750 shots: 9,750 at total requested sleep T=1 s; 1,000 zero-sleep control shots. p_ext={P_EXT}, p_read={P_READ}. All other decoder constants unchanged. Historical results preserved.",'','| N | u (s) | Shots | Logical failures | Logical error | 95% Wilson | Raw bits / total | Raw error |','|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in sweep:
        lo,hi=r['logical_wilson_95'];lines.append(f"| {r['rounds']} | {r['interval_seconds']:.6g} | {r['shots']} | {r['logical_failures']} | {100*r['logical_error_probability']:.3g}% | {100*lo:.3g}–{100*hi:.3g}% | {r['raw_data_bit_errors']} / {r['data_bits']} | {100*r['raw_data_error_probability']:.3g}% |")
    lines+=['','Zero-sleep control: '+str(controls),'','Ranges reflect shot sampling only. The sample minimum does not establish a unique optimum. Control shots are excluded from the fixed-T curve. The control informed p_ext and is not independent validation. JSON records job/raw/program/DEM provenance; NPZ stores per-shot failures and predictions.']
    paths.write_text(OUT.with_suffix('.md'), '\n'.join(lines)+'\n')
    for r in rows:print(json.dumps(r),flush=True)
    if plot:
        from .. import plots
        plots.h2_2_combined(sweep)
    return out


def decoder_sensitivity(plot=True):
    """Offline sensitivity audit of the 6,750 pooled H2-2 d=3 shots; no parameter selection/training.

    Decoders: 630 phenomenological MWPM configurations around the legacy sleep-dependent
    decoder (p_ext=0.002, p_read=0.001, r=0.0028/s, nu=0.043 Hz, multiplier 2), whose DEMs
    must equal results/sleep/decoders/d3_sleep_dependent/n*.dem at factors (1,1,1,1).
    -> results/sleep/h2_2_decoder_sensitivity.{json,npz} + figure.
    """
    from qec_timing.noise.base import RoundNoise
    dem_for, PyMatchingDecoder, paper_graph, _register_builtins, bits_from_shots, record_from_bits, Schedule, spec_from_json = qec()
    OUT=paths.RESULTS/'h2_2_decoder_sensitivity'
    _register_builtins()
    base=base_spec(spec_from_json)
    pooled_=json.loads(paths.read_text(paths.RESULTS/'h2_2_hardware_d3_all_shots.json'))
    records={}; provenance=[]; seen=set()
    for row in pooled_['rows']:
        n=row['rounds'];u=row['interval_seconds'];allshots=[]
        for batch in row['batches']:
            folder=paths.RUNS/batch['batch']/f'n{n}'
            job=json.loads(paths.read_text(folder/'job.json'))
            assert job['job_id'] not in seen;seen.add(job['job_id'])
            result=job['results'][0];path=folder/f"result_{result['index']}.txt";raw=path.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==result['raw_sha256']==batch['raw_sha256']
            allshots.extend(unpack_hardware(json.loads(raw),job['shots'],n))
            provenance.append(dict(job_id=job['job_id'],raw_path=str(path),raw_sha256=result['raw_sha256']))
        spec=replace(base,schedule=Schedule.rounds(u,n),shots=row['shots'])
        syn,data=bits_from_shots(allshots,n,4,9)
        rec=record_from_bits(spec,syn,data)
        reference=paths.read_text(paths.RESULTS/f'decoders/d3_sleep_dependent/n{n}.dem')
        baseline=PyMatchingDecoder(reference).decode_batch(rec.detectors)
        assert int(np.any(baseline!=rec.observables,axis=1).sum())==row['logical_failures']
        records[n]=(spec,rec,baseline)
    assert len(seen)==10
    # Independently vary four effective controls. Frequency multiplier is held at 2:
    # nu and multiplier cannot be separately identified by this model.
    factors=[.25,.5,1.,2.,4.]
    configs=[dict(name='grid',p_ext=.002*a,p_syndrome=.001*b,p_final=.001*b,r=.0028*c,nu=.043*d,factors=[a,b,c,d]) for a,b,c,d in itertools.product(factors,repeat=4)]
    configs += [dict(name='no_idle',p_ext=.002,p_syndrome=.001,p_final=.001,r=0.,nu=0.,factors=None)]
    for which in ['syndrome','final']:
        for f in [.25,.5,2.,4.]:
            configs.append(dict(name=f'{which}_readout_only_x{f}',p_ext=.002,p_syndrome=.001*(f if which=='syndrome' else 1),p_final=.001*(f if which=='final' else 1),r=.0028,nu=.043,factors=None))
    results=[];predictions=[]
    for idx,c in enumerate(configs):
        rows=[];preds=[]
        for n,(spec,rec,baseline) in records.items():
            u=1/(n-1);lin=c['r']*u;quad=np.sin(np.pi*c['nu']*2*u)**2
            idle=lin+quad-2*lin*quad;p=c['p_ext']+idle-2*c['p_ext']*idle
            graph=paper_graph(spec,c['p_ext'],0,c['p_final'])
            noise=[RoundNoise(c['p_ext'],c['p_syndrome'])]+[RoundNoise(p,c['p_syndrome'])]*(n-1)
            dem=dem_for(graph,noise=noise)
            pred=PyMatchingDecoder(dem).decode_batch(rec.detectors)
            fail=np.any(pred!=rec.observables,axis=1);oldfail=np.any(baseline!=rec.observables,axis=1)
            if c['factors']==[1.,1.,1.,1.]:
                assert dem==paths.read_text(paths.RESULTS/f'decoders/d3_sleep_dependent/n{n}.dem')
                assert np.array_equal(pred,baseline)
            rows.append(dict(rounds=n,shots=len(fail),failures=int(fail.sum()),probability=float(fail.mean()),changed_predictions=int(np.any(pred!=baseline,axis=1).sum()),corrected=int((oldfail & ~fail).sum()),harmed=int((~oldfail & fail).sum()),dem_sha256=hashlib.sha256(dem.encode()).hexdigest()))
            preds.append(pred[:,0])
        minimum=min(r['probability'] for r in rows)
        results.append(dict(index=idx,parameters=c,rows=rows,sample_minimum_N=[r['rounds'] for r in rows if r['probability']==minimum]))
        predictions.append(np.concatenate(preds))
        if idx%100==0: print('Decoded configurations',idx+1,flush=True)
    summary=[]
    for j,row in enumerate(pooled_['rows']):
        ns=[]
        for label,subset in [('moderate', [x for x in results if x['parameters']['factors'] and all(.5<=f<=2 for f in x['parameters']['factors'])]),('broad',[x for x in results if x['parameters']['name']=='grid'])]:
            values=[x['rows'][j] for x in subset]
            ns.append(dict(range=label,configurations=len(values),minimum_failures=min(v['failures'] for v in values),maximum_failures=max(v['failures'] for v in values),max_changed_predictions=max(v['changed_predictions'] for v in values)))
        summary.append(dict(rounds=row['rounds'],shots=row['shots'],baseline_failures=row['logical_failures'],ranges=ns))
    output=dict(description='Exploratory offline sensitivity; parameter ranges are stress tests, not calibrated confidence regions. No optimization or adoption of a decoder.',total_shots=6750,grid_factors=factors,frequency_multiplier=2,provenance=provenance,summary=summary,configurations=results)
    paths.write_json(OUT.with_suffix('.json'), output)
    paths.save_npz(OUT.with_suffix('.npz'),predictions=np.asarray(predictions,dtype=bool),rounds=np.array(list(records)),shots=np.array([r['shots'] for r in pooled_['rows']]))
    print(json.dumps(summary,indent=2))
    print('Minimum counts:',Counter(tuple(x['sample_minimum_N']) for x in results if x['parameters']['name']=='grid'))
    if plot:
        from .. import plots
        plots.h2_2_decoder_sensitivity(summary,results)
    return output
