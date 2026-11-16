"""Authorized d=5 H2-1E sweep: T_sleep=0.5 seconds; N=3,4,5,6, 500 shots each."""
import argparse
import asyncio
import hashlib
import json
from fixed_sleep_d5 import ROOT, CONFIG, accepted, qir
from build_sleep_probe import call_counts
import re
import subprocess

ROUNDS=[3,4,5,6]
BUILD=ROOT/'programs'/'d5_fixed_sleep_half_second_n3_4_5_6'
DEST=ROOT/'runs'/'d5_fixed_sleep_half_second_h2_1e_500_n3_4_5_6'
PLATFORM='nexus:H2-1E'
ESTIMATE=sum(5+500*(696*n+305)/5000 for n in ROUNDS)



def half_second_qir(n):
    original=qir(n)
    pattern=r'(@__quantum__qis__sleep__body\([^\n]*, double )([^\n)]+)(\))'
    text,count=re.subn(pattern,lambda m:m[1]+f'{0.5/(n-1):.17e}'+m[3],original)
    assert count==25*(n-1)
    assert re.sub(pattern,r'\1DURATION\3',text)==re.sub(pattern,r'\1DURATION\3',original)
    durations=[float(m[1]) for m in re.finditer(r'@__quantum__qis__sleep__body\([^\n]*, double ([^\n)]+)\)',text)]
    assert len(durations)==25*(n-1) and all(abs(v*(n-1)-0.5)<1e-12 for v in durations)
    return text


def build():
    BUILD.mkdir(exist_ok=True)
    if (BUILD/'manifest.json').exists():
        manifest=json.loads((BUILD/'manifest.json').read_text())
        for n in ROUNDS:
            assert (BUILD/f'n{n}.ll').read_text()==half_second_qir(n)
            assert hashlib.sha256((BUILD/f'n{n}.bc').read_bytes()).hexdigest()==manifest['bitcode_sha256'][f'n{n}']
        return
    hashes={}
    for n in ROUNDS:
        text=half_second_qir(n);ll=BUILD/f'n{n}.ll';bc=ll.with_suffix('.bc');rt=ll.with_suffix('.roundtrip.ll')
        ll.write_text(text)
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-x','ir','-c','-emit-llvm','-O0',str(ll),'-o',str(bc)],check=True,capture_output=True)
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(bc),'-o',str(rt)],check=True,capture_output=True)
        assert call_counts(rt.read_text())==call_counts(text)
        assert f'"required_num_results"="{12*n+25}"' in rt.read_text()
        hashes[f'n{n}']=hashlib.sha256(bc.read_bytes()).hexdigest()
    manifest=dict(distance=5,basis='X',rounds=ROUNDS,shots_per_setting=500,total_requested_sleep_seconds=0.5,platform=PLATFORM,options=CONFIG['options'],as_entity=CONFIG['as_entity'],bitcode_sha256=hashes,estimated_hqc=ESTIMATE,local_validation='Only sleep durations changed; all four LLVM assembly/roundtrip checks passed',parallel_sleep_verified=False,extraction_duration_neglected=True)
    (BUILD/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    (ROOT/'configs/d5_fixed_sleep_half_second_2000.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(BUILD,flush=True)


def submit(stage):
    from aqora import QPU
    build()
    manifest=json.loads((BUILD/'manifest.json').read_text())
    for n in ROUNDS:
        assert hashlib.sha256((BUILD/f'n{n}.bc').read_bytes()).hexdigest()==manifest['bitcode_sha256'][f'n{n}']
        if stage=='execute':
            assert accepted(json.loads((DEST/'check'/f'n{n}'/'job.json').read_text()))
    DEST.mkdir(exist_ok=True)
    plan=dict(rounds=ROUNDS,shots_per_setting=500,total_execution_shots=2000,platform=PLATFORM,as_entity=CONFIG['as_entity'],options=CONFIG['options'],source_build=str(BUILD),estimated_hqc=ESTIMATE,total_requested_sleep_seconds=0.5,parallel_sleep_verified=False,extraction_duration_neglected=True)
    (DEST/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    platform='nexus:H2-1SC' if stage=='check' else PLATFORM
    shots=1 if stage=='check' else 500
    qpu=QPU(platform=platform,as_entity=CONFIG['as_entity'])
    for n in ROUNDS:
        folder=DEST/stage/f'n{n}';folder.mkdir(parents=True,exist_ok=True)
        record=folder/'job.json';request=folder/'request.json'
        if record.exists():
            print(f'n{n}: already submitted',flush=True);continue
        if request.exists():raise RuntimeError(f'Unresolved request: {request}; reconcile before retry')
        data=dict(rounds=n,shots=shots,delta_t_seconds=0.5/(n-1),platform=platform,as_entity=CONFIG['as_entity'],options=CONFIG['options'],program=str(BUILD/f'n{n}.bc'))
        request.write_text(json.dumps(data,indent=2)+'\n')
        job=qpu.run((BUILD/f'n{n}.bc').read_bytes(),shots=shots,options=CONFIG['options'])
        record.write_text(json.dumps(dict(data,job_id=job.job_id),indent=2)+'\n')
        print(f'n{n}: {job.job_id}',flush=True)


def fetch(stage):
    from aqora import Client, QPUJob
    paths=[DEST/stage/f'n{n}'/'job.json' for n in ROUNDS]
    records=[json.loads(p.read_text()) for p in paths]
    async def query_status():
        client=Client();await client.authenticate()
        query='{ '+' '.join(f'j{i}: node(id: {json.dumps(d["job_id"])}) {{ ... on ProviderJob {{ id status error hqcCost }} }}' for i,d in enumerate(records))+' }'
        return await client.send(query)
    result=asyncio.run(query_status());rows=[]
    for i,(path,data) in enumerate(zip(paths,records)):
        data['job']=result[f'j{i}']
        if data['job']['status']=='COMPLETED' and not data['job']['error'] and not data.get('results'):
            results=QPUJob.from_id(data['job_id']).results(raise_on_item_error=False)
            for item in results:(path.parent/f'result_{item.index}.txt').write_text(item.raw or '')
            data['results']=[dict(index=item.index,format=item.serialization_format,error=getattr(item,'error',None)) for item in results]
        path.write_text(json.dumps(data,indent=2)+'\n')
        row=dict(rounds=data['rounds'],shots=data['shots'],job_id=data['job_id'],**{k:data['job'][k] for k in ['status','error','hqcCost']})
        rows.append(row);print(json.dumps(row),flush=True)
    (DEST/f'{stage}_status.json').write_text(json.dumps(rows,indent=2)+'\n')
    if stage=='execute':
        report=['# d=5 H2-1E: half-second fixed-sleep sweep','','Authorized N=3,4,5,6, 500 shots each (2,000 shots). Uses the pinned native extraction circuit with fixed requested sleep of 0.5 seconds per data qubit, Delta t=0.5/(N-1), X-memory sector and no artificial injected faults. Noise options: stabilizer, noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true. Existing H2-1E jobs are preserved.', '',f'Gate-count cost estimate: {ESTIMATE:,.1f} HQC if all four are accepted, including four execution-job overheads. H2-1SC validation is required before execution.','', '| N | Shots | Status | HQC reported | Job ID |','|---:|---:|---|---:|---|']
        for row in rows:report.append(f"| {row['rounds']} | {row['shots']} | {row['error'] or row['status']} | {row['hqcCost']} | {row['job_id']} |")
        report+=['','No further retries or additional shots submitted. Provider costs for waiting jobs are not final completed-execution billing.',f'Raw records: `{DEST}`.','']
        (ROOT/'results/d5_fixed_sleep_half_second_h2_1e_500_submission.md').write_text('\n'.join(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['build','check','execute','fetch-check','fetch-execute']);a=p.parse_args().action
    if a=='build':build()
    elif a.startswith('fetch-'):fetch(a.split('-',1)[1])
    else:submit(a)
