"""d=5 X-memory, fixed one-second requested sleep; pinned native QIR blocks."""
import argparse
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path
from fixed_sleep_d3 import rename_locals, remap_results
from build_sleep_probe import ROOT, call_counts
from d3_sleep_sweep import operand
from single_qubit_sweep import OPTIONS, accepted

SOURCE = ROOT.parent/'results/hardware/programs/d5_X_r5_p0.ll'
SOURCE_SHA256 = 'fcba655ea3cf9cebd600f9555d703088244459d13128cbe212d70c6a2b694ff0'
ROUNDS = [2,3,4,5,6,7,8,9,10,15,20]
CONFIG = dict(experiment='d5_X_fixed_total_sleep_1s',distance=5,basis='X',
    rounds=ROUNDS,shots_per_setting={str(n):2000 if 6<=n<=10 else 500 for n in ROUNDS},
    total_requested_sleep_seconds=1.0,sleep_units='seconds as agreed',
    extraction_duration_neglected=True,parallel_sleep_verified=False,
    platform='nexus:H2-1E',as_entity='q_sq',options=OPTIONS,artificial_faults=False,
    baseline_sha256=SOURCE_SHA256)


def qir(n, include_sleep=True):
    assert n >= 2
    src=SOURCE.read_text()
    assert hashlib.sha256(src.encode()).hexdigest()==SOURCE_SHA256
    boundaries=list(re.finditer(r'^cond_exit_[^\n]+\n  tail call void @__quantum__qis__reset__body[^\n]+\n',src,re.M))
    assert len(boundaries)==60
    start=src.index('  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 25')
    first=src[start:boundaries[11].end()]
    last=src[boundaries[47].end():boundaries[59].end()]
    tags=[f's{r}_{c}' for r in range(n) for c in range(12)]+[f'm{q}' for q in range(25)]
    globals_=''.join(f'@tag_{i} = private constant [{len(t)+1} x i8] c"{t}\\00"\n' for i,t in enumerate(tags))
    prefix=src[src.index('define dso_local'):start]
    barrier='  call void @__quantum__qis__barrier26__body('+', '.join(operand(q) for q in range(26))+')\n'
    sleep=barrier+''.join(f'  call void @__quantum__qis__sleep__body({operand(q)}, double {1/(n-1):.17e})\n' for q in range(25))+barrier if include_sleep else ''
    body=prefix
    for r in range(n-1):
        body+=remap_results(rename_locals(first,f'r{r}_'),12*r)+sleep
    body+=remap_results(rename_locals(last,f'r{n-1}_'),12*(n-5))
    for r in range(n):
        for c in range(12):
            i=12*r+c;v=c+1 if r<n-1 else c+49;length=len(tags[i])+1
            body+=f'  tail call void @__quantum__rt__bool_record_output(i1 %r{r}_v{v}, i8* getelementptr inbounds ([{length} x i8], [{length} x i8]* @tag_{i}, i64 0, i64 0))\n'
    final_start=src.index('  tail call void @__quantum__qis__mz__body(%Qubit* null',boundaries[59].end())
    final_end=src.index('\n}\n',final_start)
    final=remap_results(rename_locals(src[final_start:final_end],'final_'),12*(n-5))
    final=re.sub(r'\]([^\n]*?)@(\d+)',lambda m:']'+m[1]+'@tag_'+str(int(m[2])+12*(n-5)),final)
    body+=final+'\n}\n'
    tail=src[src.index('declare i64 @___get_current_shot()'):]
    tail=tail.replace('"required_num_results"="85"',f'"required_num_results"="{12*n+25}"')
    tail+='\ndeclare void @__quantum__qis__sleep__body(%Qubit*, double)\n'
    tail+='declare void @__quantum__qis__barrier26__body('+', '.join(['%Qubit*']*26)+')\n'
    return src[:src.index('@0 =')]+globals_+body+tail


TEXTS={f'n{n}':qir(n) for n in ROUNDS}
BUILD=ROOT/'programs'/('d5_fixed_sleep_'+hashlib.sha256((json.dumps(CONFIG,sort_keys=True)+''.join(TEXTS.values())).encode()).hexdigest()[:16])
RUNS=ROOT/'runs'/BUILD.name
PLAN=[]
for n in ROUNDS:
    shots=CONFIG['shots_per_setting'][str(n)]
    count=math.ceil(shots*(800*n+355)/5000/995)
    parts=[shots//count+(i<shots%count) for i in range(count)]
    PLAN.append(dict(name=f'n{n}',rounds=n,parts=parts,shots=shots,delta_t_seconds=1/(n-1),
        estimated_hqc=[5*count+shots*(696*n+305)/5000,5*count+shots*(800*n+355)/5000]))


def build():
    BUILD.mkdir(exist_ok=True)
    hashes={}
    if (BUILD/'manifest.json').exists():
        manifest=json.loads((BUILD/'manifest.json').read_text())
        for name,digest in manifest['bitcode_sha256'].items():
            assert hashlib.sha256((BUILD/(name+'.bc')).read_bytes()).hexdigest()==digest
        return
    for name,text in TEXTS.items():
        ll=BUILD/(name+'.ll');ll.write_text(text);bc=ll.with_suffix('.bc')
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-x','ir','-c','-emit-llvm','-O0',str(ll),'-o',str(bc)],check=True,capture_output=True)
        rt=ll.with_suffix('.roundtrip.ll')
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(bc),'-o',str(rt)],check=True,capture_output=True)
        assert call_counts(rt.read_text())==call_counts(text)
        hashes[name]=hashlib.sha256(bc.read_bytes()).hexdigest()
    manifest=dict(CONFIG,plan=PLAN,bitcode_sha256=hashes,source=str(SOURCE),
        estimated_hqc_total=[sum(p['estimated_hqc'][i] for p in PLAN) for i in range(2)],
        estimate_assumptions='Excludes/includes virtual Rz; no extra sleep/barrier charge; 5 HQC per split job',
        analysis_policy='Collect raw results; no automatic decoder retuning or further submissions')
    (BUILD/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'configs/d5_fixed_sleep_13000.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(BUILD,flush=True)


def jobs(stage):
    for p in PLAN:
        for i,shots in enumerate([1] if stage=='check' else p['parts']):
            yield p,p['name'] if stage=='check' else f"{p['name']}_part{i+1}",shots


def submit(stage):
    from aqora import QPU
    build()
    if stage=='execute':
        assert all(accepted(json.loads((RUNS/'check'/p['name']/'job.json').read_text())) for p in PLAN)
    platform='nexus:H2-1SC' if stage=='check' else CONFIG['platform']
    qpu=QPU(platform=platform,as_entity=CONFIG['as_entity'])
    for p,name,shots in jobs(stage):
        dest=RUNS/stage/name;dest.mkdir(parents=True,exist_ok=True)
        record=dest/'job.json';request=dest/'request.json'
        if record.exists():
            print(name,'already submitted',flush=True);continue
        if request.exists():raise RuntimeError('Unresolved submission attempt; reconcile before retry')
        program=BUILD/(p['name']+'.bc')
        assert hashlib.sha256(program.read_bytes()).hexdigest()==json.loads((BUILD/'manifest.json').read_text())['bitcode_sha256'][p['name']]
        data=dict(platform=platform,as_entity=CONFIG['as_entity'],shots=shots,options=OPTIONS,
            program=str(program),rounds=p['rounds'],delta_t_seconds=p['delta_t_seconds'])
        request.write_text(json.dumps(data,indent=2)+'\n')
        job=qpu.run(program.read_bytes(),shots=shots,options=OPTIONS)
        record.write_text(json.dumps(dict(data,job_id=job.job_id),indent=2)+'\n')
        print(name,job.job_id,flush=True)


def fetch(stage):
    from aqora import QPUJob
    rows=[]
    for p,name,shots in jobs(stage):
        dest=RUNS/stage/name;record=dest/'job.json'
        if not record.exists():
            print(name,'not submitted',flush=True);continue
        data=json.loads(record.read_text())
        if not accepted(data):
            job=QPUJob.from_id(data['job_id']);data['job']=dict(job.refresh())
            if data['job'].get('status')=='COMPLETED':
                results=job.results(raise_on_item_error=False)
                for r in results:(dest/f'result_{r.index}.txt').write_text(r.raw or '')
                data['results']=[dict(index=r.index,format=r.serialization_format,error=getattr(r,'error',None)) for r in results]
            record.write_text(json.dumps(data,indent=2,default=str)+'\n')
        rows.append(dict(name=name,shots=shots,job_id=data['job_id'],status=data['job'].get('status'),error=data['job'].get('error'),stored=accepted(data),raw_sha256={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in dest.glob('result_*.txt')}))
        print(name,data['job'].get('status'),data['job'].get('error'),flush=True)
    (RUNS/f'{stage}_collection_status.json').write_text(json.dumps(dict(all_results_stored=len(rows)==len(list(jobs(stage))) and all(r['stored'] for r in rows),jobs=rows),indent=2)+'\n')


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['build','check','execute','fetch-check','fetch-execute'])
    action=parser.parse_args().action
    if action=='build':build()
    elif action.startswith('fetch-'):fetch(action.split('-',1)[1])
    else:submit(action)
