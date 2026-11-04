"""Pinned native QIR extraction blocks, repeated at fixed total requested sleep."""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from build_sleep_probe import ROOT, SOURCE, SOURCE_SHA256, BOUNDARY, call_counts
from d3_sleep_sweep import operand
from single_qubit_sweep import OPTIONS, accepted

ROUNDS=[2,5,10,20,40]
SHOTS=500
CONFIG=dict(experiment='d3_X_fixed_total_sleep_1s',distance=3,basis='X',rounds=ROUNDS,
    shots_per_setting=SHOTS,total_requested_sleep_seconds=1.0,sleep_units='seconds as agreed',
    extraction_duration_neglected=True,parallel_sleep_verified=False,
    platform='nexus:H2-1E',as_entity='q_sq',options=OPTIONS,artificial_faults=False)
BASE_CONFIG=CONFIG.copy()


def result_operand(i):
    return '%Result* null' if i==0 else f'%Result* nonnull inttoptr (i64 {i} to %Result*)'


def remap_results(text,offset):
    pattern=r'%Result\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %Result\*\)|null)'
    return re.sub(pattern,lambda m:result_operand(int(m[1] or 0)+offset),text)


def rename_locals(text,prefix):
    text=re.sub(r';[^\n]*','',text)
    labels=re.findall(r'^(\w+):',text,re.M)
    for label in labels:
        text=re.sub(r'\b'+re.escape(label)+r'\b',prefix+label,text)
    return re.sub(r'%(\d+)\b',lambda m:'%'+prefix+'v'+m[1],text)


def qir(n):
    if n not in ROUNDS:
        raise ValueError('Unsupported round count')
    src=SOURCE.with_suffix('.ll').read_text()
    assert hashlib.sha256(src.encode()).hexdigest()==SOURCE_SHA256
    start=src.index('  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9')
    first_end=src.index(BOUNDARY)+len(BOUNDARY)
    last_end=src.index('  tail call void @__quantum__rt__bool_record_output')
    # The last round contains final data-H gates fused/moved by the original compiler.
    # Keep this block as the final round; repeat only the non-final round block.
    first=src[start:first_end]
    last=src[first_end:last_end]
    definition=src.index('define dso_local')
    prefix=src[definition:start]
    header=src[:src.index('@0 =')]
    tags=[f's{r}_{c}' for r in range(n) for c in range(4)]+[f'm{q}' for q in range(9)]
    globals_=''.join(f'@tag_{i} = private constant [{len(t)+1} x i8] c"{t}\\00"\n' for i,t in enumerate(tags))
    u=1.0/(n-1)
    barrier='  call void @__quantum__qis__barrier10__body('+', '.join(operand(q) for q in range(10))+')\n'
    sleep=barrier+''.join(f'  call void @__quantum__qis__sleep__body({operand(q)}, double {u:.17e})\n' for q in range(9))+barrier
    body=prefix
    for r in range(n-1):
        body+=remap_results(rename_locals(first,f'r{r}_'),4*r)+sleep
    body+=remap_results(rename_locals(last,f'r{n-1}_'),4*(n-2))
    for r in range(n):
        for c in range(4):
            i=4*r+c
            v=c+1 if r<n-1 else c+5
            length=len(tags[i])+1
            body+=f'  tail call void @__quantum__rt__bool_record_output(i1 %r{r}_v{v}, i8* getelementptr inbounds ([{length} x i8], [{length} x i8]* @tag_{i}, i64 0, i64 0))\n'
    final_start=src.index('  tail call void @__quantum__qis__mz__body(%Qubit* null',last_end)
    final_end=src.index('\n}\n',final_start)
    final=remap_results(rename_locals(src[final_start:final_end],'final_'),4*(n-2))
    final=re.sub(r'\]([^\n]*?)@(\d+)',lambda m:']'+m[1]+'@tag_'+str(int(m[2])+4*(n-2)),final)
    # First @index occurs after a pointer type's closing bracket, so both uses map above.
    body+=final+'\n}\n'
    tail=src[src.index('declare i64 @___get_current_shot()'):]
    tail=tail.replace('"required_num_results"="17"',f'"required_num_results"="{4*n+9}"')
    tail+='\ndeclare void @__quantum__qis__sleep__body(%Qubit*, double)\n'
    tail+='declare void @__quantum__qis__barrier10__body('+', '.join(['%Qubit*']*10)+')\n'
    return header+globals_+body+tail


TEXTS={f'n{n}':qir(n) for n in ROUNDS}
BUILD=ROOT/'programs'/('d3_fixed_sleep_'+hashlib.sha256((json.dumps(CONFIG,sort_keys=True)+''.join(TEXTS.values())).encode()).hexdigest()[:16])
RUNS=ROOT/'runs'/BUILD.name
PLAN=[dict(name=f'n{n}',rounds=n,parts=[500] if n<40 else [250,250],delta_t_seconds=1/(n-1),delta_t_exact=f'1/{n-1}') for n in ROUNDS]


def configure_refinement():
    """Fresh refinement jobs; keep original run IDs and data unchanged."""
    global ROUNDS, CONFIG, TEXTS, BUILD, RUNS, PLAN
    ROUNDS=[4,5,6,7,8]
    CONFIG=dict(BASE_CONFIG,experiment='d3_X_fixed_total_sleep_1s_refinement',rounds=ROUNDS,
        shots_per_setting={str(n):500 if n==5 else 1000 for n in ROUNDS},
        existing_n5_run='d3_fixed_sleep_690baca08b24dfd2',
        existing_n5_shots=500,planned_combined_shots_per_setting=1000)
    TEXTS={f'n{n}':qir(n) for n in ROUNDS}
    BUILD=ROOT/'programs'/('d3_fixed_sleep_refinement_'+hashlib.sha256(
        (json.dumps(CONFIG,sort_keys=True)+''.join(TEXTS.values())).encode()).hexdigest()[:16])
    RUNS=ROOT/'runs'/BUILD.name
    PLAN=[dict(name=f'n{n}',rounds=n,parts=[500 if n==5 else 1000],
        delta_t_seconds=1/(n-1),delta_t_exact=f'1/{n-1}') for n in ROUNDS]


def configure_resolution():
    """Second independent refinement batch with explicitly requested new shots."""
    global ROUNDS, CONFIG, TEXTS, BUILD, RUNS, PLAN
    ROUNDS=[3,4,5,6,7,8,10]
    allocation={str(n):500 if n in (3,10) else 1000 for n in ROUNDS}
    CONFIG=dict(BASE_CONFIG,experiment='d3_X_fixed_total_sleep_1s_resolution',rounds=ROUNDS,
        shots_per_setting=allocation,shot_allocation_interpretation='additional new shots',
        prior_runs=['d3_fixed_sleep_690baca08b24dfd2','d3_fixed_sleep_refinement_3bb6e107a0ff6de3'])
    TEXTS={f'n{n}':qir(n) for n in ROUNDS}
    BUILD=ROOT/'programs'/('d3_fixed_sleep_resolution_'+hashlib.sha256(
        (json.dumps(CONFIG,sort_keys=True)+''.join(TEXTS.values())).encode()).hexdigest()[:16])
    RUNS=ROOT/'runs'/BUILD.name
    PLAN=[dict(name=f'n{n}',rounds=n,parts=[allocation[str(n)]],
        delta_t_seconds=1/(n-1),delta_t_exact=f'1/{n-1}') for n in ROUNDS]


def build():
    BUILD.mkdir(exist_ok=True)
    hashes={}
    for name,text in TEXTS.items():
        ll=BUILD/(name+'.ll');bc=ll.with_suffix('.bc')
        if (BUILD/'manifest.json').exists():
            old=json.loads((BUILD/'manifest.json').read_text())
            assert hashlib.sha256(bc.read_bytes()).hexdigest()==old['bitcode_sha256'][name]
            continue
        ll.write_text(text)
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-x','ir','-c','-emit-llvm','-O0',str(ll),'-o',str(bc)],capture_output=True,check=True)
        rt=BUILD/(name+'.roundtrip.ll')
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(bc),'-o',str(rt)],capture_output=True,check=True)
        assert call_counts(rt.read_text())==call_counts(text)
        hashes[name]=hashlib.sha256(bc.read_bytes()).hexdigest()
    if hashes:
        manifest=dict(CONFIG,plan=PLAN,bitcode_sha256=hashes,baseline_sha256=SOURCE_SHA256,
            note='Pinned Guppy native non-final and final round blocks reused directly in QIR')
        (BUILD/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
        config_name='d3_fixed_sleep_refinement.json' if 'refinement' in CONFIG['experiment'] else 'd3_fixed_sleep_500.json'
        if 'resolution' in CONFIG['experiment']:config_name='d3_fixed_sleep_resolution.json'
        (ROOT/'configs'/config_name).write_text(json.dumps(manifest,indent=2)+'\n')
    print(BUILD,flush=True)


def jobs(stage):
    for p in PLAN:
        for i,shots in enumerate([1] if stage=='check' else p['parts']):
            yield p, p['name'] if stage=='check' else p['name']+f'_part{i+1}', shots


def submit(stage):
    from aqora import QPU
    build()
    if stage=='execute':
        assert all(accepted(json.loads((RUNS/'check'/p['name']/'job.json').read_text())) for p in PLAN)
    platform='nexus:H2-1SC' if stage=='check' else CONFIG['platform']
    qpu=QPU(platform=platform,as_entity='q_sq')
    for p,name,shots in jobs(stage):
        dest=RUNS/stage/name;dest.mkdir(parents=True,exist_ok=True)
        record=dest/'job.json';request=dest/'request.json'
        if record.exists():
            print(name,'already submitted',flush=True);continue
        if request.exists():raise RuntimeError('Unresolved attempt; reconcile before retry')
        data=dict(platform=platform,as_entity='q_sq',shots=shots,options=OPTIONS,
            program=str(BUILD/(p['name']+'.bc')),rounds=p['rounds'],delta_t_seconds=p['delta_t_seconds'])
        request.write_text(json.dumps(data,indent=2)+'\n')
        job=qpu.run((BUILD/(p['name']+'.bc')).read_bytes(),shots=shots,options=OPTIONS)
        record.write_text(json.dumps(dict(data,job_id=job.job_id),indent=2)+'\n')
        print(name,job.job_id,flush=True)


def fetch(stage):
    from aqora import QPUJob
    rows=[]
    for p,name,shots in jobs(stage):
        dest=RUNS/stage/name;record=dest/'job.json';data=json.loads(record.read_text())
        if not accepted(data):
            job=QPUJob.from_id(data['job_id']);data['job']=dict(job.refresh())
            if data['job'].get('status')=='COMPLETED':
                results=job.results(raise_on_item_error=False)
                for r in results:(dest/f'result_{r.index}.txt').write_text(r.raw or '')
                data['results']=[dict(index=r.index,format=r.serialization_format,error=getattr(r,'error',None)) for r in results]
            record.write_text(json.dumps(data,indent=2,default=str)+'\n')
        files={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in dest.glob('result_*.txt')}
        rows.append(dict(name=name,rounds=p['rounds'],shots=shots,job_id=data['job_id'],status=data['job'].get('status'),raw_sha256=files,stored=accepted(data) and bool(files)))
        print(name,data['job'].get('status'),data['job'].get('error'),flush=True)
    if stage=='execute':
        (RUNS/'collection_status.json').write_text(json.dumps(dict(all_results_stored=all(x['stored'] for x in rows),jobs=rows),indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['build','check','execute','fetch-check','fetch-execute'])
    group=parser.add_mutually_exclusive_group()
    group.add_argument('--refinement',action='store_true')
    group.add_argument('--resolution',action='store_true')
    args=parser.parse_args()
    if args.refinement:configure_refinement()
    elif args.resolution:configure_resolution()
    action=args.action
    if action=='build':build()
    elif action.startswith('fetch-'):fetch(action.split('-',1)[1])
    else:submit(action)
