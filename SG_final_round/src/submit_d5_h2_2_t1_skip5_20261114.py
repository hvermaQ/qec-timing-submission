"""User-authorized physical H2-2 d=5 T=1 s sweep: 1000 shots, two settings, submitted index 5 skipped."""
import argparse
import asyncio
import hashlib
import json
import re
import subprocess
from pathlib import Path
from fixed_sleep_d5 import ROOT, qir
from build_sleep_probe import call_counts

SETTINGS = [(3,500),(4,500)]
BUILD = ROOT / 'programs/d5_h2_2_t1_skip5_n3_n4'
RUN = ROOT / 'runs/d5_h2_2_t1_skip5_20261114'
OPTIONS = {'no_opt': True}
POLICY_PATH = ROOT / 'configs/h2_2_d5_decoder.json'


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(data, indent=2, default=str)+'\n')
    temp.replace(path)



def mapped_qir(n):
    original=qir(n)
    pattern=r'%Qubit\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %Qubit\*\)|null)'
    def forward(m):
        q=int(m[1] or 0)
        return m[0] if q<5 else m[0].replace(f'i64 {q} ',f'i64 {q+1} ')
    text=re.sub(pattern,forward,original).replace('"required_num_qubits"="26"','"required_num_qubits"="27"')
    assert {int(m[1] or 0) for m in re.finditer(pattern,text)}==set(range(27))-{5}
    def inverse(m):
        q=int(m[1] or 0)
        return m[0] if q<6 else m[0].replace(f'i64 {q} ',f'i64 {q-1} ')
    assert re.sub(pattern,inverse,text).replace('"required_num_qubits"="27"','"required_num_qubits"="26"')==original
    return text


def build():
    BUILD.mkdir(exist_ok=True)
    hashes={}
    for n,_ in SETTINGS:
        text=mapped_qir(n);ll=BUILD/f'n{n}.ll';bc=ll.with_suffix('.bc');rt=BUILD/f'n{n}.roundtrip.ll'
        if bc.exists():
            manifest=json.loads((BUILD/'manifest.json').read_text())
            assert ll.read_text()==text and hashlib.sha256(bc.read_bytes()).hexdigest()==manifest['bitcode_sha256'][f'n{n}']
        else:
            ll.write_text(text)
            subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-x','ir','-c','-emit-llvm','-O0',str(ll),'-o',str(bc)],check=True,capture_output=True)
            subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(bc),'-o',str(rt)],check=True,capture_output=True)
        assert call_counts(rt.read_text())==call_counts(text)
        hashes[f'n{n}']=hashlib.sha256(bc.read_bytes()).hexdigest()
    save(BUILD/'manifest.json',dict(distance=5,basis='X',artificial_faults=False,total_requested_sleep_seconds=1,bitcode_sha256=hashes,data_indices=list(range(5))+list(range(6,26)),ancilla_index=26,unused_index=5,output_labels='Original code positions preserved'))


def plan():
    build()
    policy = json.loads(POLICY_PATH.read_text())
    assert policy['distance'] == 5 and policy['p_ext'] == .004
    manifest = json.loads((BUILD/'manifest.json').read_text())
    assert not manifest['artificial_faults'] and manifest['total_requested_sleep_seconds'] == 1
    rows=[]
    for n,shots in SETTINGS:
        program=BUILD/f'n{n}.bc'; digest=hashlib.sha256(program.read_bytes()).hexdigest()
        assert digest==manifest['bitcode_sha256'][f'n{n}']
        text=(BUILD/f'n{n}.ll').read_text(); assert text==mapped_qir(n)
        rt=(BUILD/f'n{n}.roundtrip.ll').read_text()
        assert call_counts(rt)==call_counts(text)
        sleeps=re.findall(r'call void @__quantum__qis__sleep__body\([^\n]*double ([^)]+)\)',text)
        assert len(sleeps)==25*(n-1) and all(abs(float(u)-1/(n-1))<1e-14 for u in sleeps)
        rows.append(dict(platform='nexus:H2-2',as_entity='q_sq',options=OPTIONS,distance=5,basis='X',rounds=n,shots=shots,total_requested_sleep_seconds=1.0,delta_t_seconds=1/(n-1),artificial_faults=False,parallel_sleep_verified=False,extraction_duration_neglected=True,program=str(program),program_sha256=digest,estimated_hqc=5+shots*((696*n+305)/5000+.001),decoder_policy=policy,qubit_mapping=dict(data_indices=list(range(5))+list(range(6,26)),ancilla_index=26,unused_index=5),matching_calibration=str(ROOT/'runs/d5_h2_2_zero_sleep_n3_skip5_250_20261114/execute/raw_analysis.json')))
    assert sum(r['shots'] for r in rows)==1000
    assert abs(sum(r['estimated_hqc'] for r in rows)-559.2)<1e-9
    save(RUN/'plan.json',dict(settings=rows,total_shots=1000,estimated_hqc=559.2))
    return rows


def submit(stage):
    from aqora import QPU
    rows=plan()
    if stage=='execute':
        # Both must pass before any paid submission.
        for row in rows:
            checked=json.loads((RUN/'check'/f"n{row['rounds']}"/'job.json').read_text())
            assert checked['job']['status']=='COMPLETED' and not checked['job'].get('error')
            assert checked['program_sha256']==row['program_sha256']
    platform='nexus:H2-2SC' if stage=='check' else 'nexus:H2-2'
    qpu=QPU(platform=platform,as_entity='q_sq')
    qpu._graphql.ensure_authenticated()
    matches=[p for p in qpu._graphql.get_provider_platforms() if p['provider'].lower()=='nexus' and p['name']==platform.split(':')[1]]
    assert len(matches)==1
    for row in rows:
        folder=RUN/stage/f"n{row['rounds']}"; record=folder/'job.json'
        if record.exists():
            print('Existing',stage,row['rounds'],json.loads(record.read_text())['job_id'],flush=True);continue
        folder.mkdir(parents=True,exist_ok=True)
        request=folder/'request.json'; assert not request.exists(),f'Reconcile unresolved request: {request}'
        data=dict(row,platform=platform,shots=1 if stage=='check' else row['shots'],resolved_platform=dict(matches[0]))
        if stage=='execute':
            data['syntax_check_job_id']=json.loads((RUN/'check'/f"n{row['rounds']}"/'job.json').read_text())['job_id']
        bitcode=Path(row['program']).read_bytes();assert hashlib.sha256(bitcode).hexdigest()==row['program_sha256']
        save(request,data)
        job=qpu.run(bitcode,shots=data['shots'],options=OPTIONS)
        save(record,dict(data,job_id=job.job_id))
        print(stage,'N='+str(row['rounds']),data['shots'],'shots:',job.job_id,flush=True)


async def status(stage):
    from aqora import Client
    paths=sorted((RUN/stage).glob('n*/job.json'),key=lambda p:int(p.parent.name[1:]));assert paths
    records=[json.loads(p.read_text()) for p in paths]
    client=Client();await client.authenticate()
    fields='id status error hqcCost resultCount platform { name provider }'
    query='{ '+' '.join(f'j{i}: node(id: {json.dumps(r["job_id"])}) {{ ... on ProviderJob {{ {fields} }} }}' for i,r in enumerate(records))+' }'
    response=await client.send(query);rows=[]
    for i,(path,record) in enumerate(zip(paths,records)):
        job=response[f'j{i}']; assert job['id']==record['job_id'] and job['platform']['name']==record['platform'].split(':')[1]
        save(path,dict(record,job=job))
        rows.append(dict(rounds=record['rounds'],shots=record['shots'],**job))
    save(RUN/f'{stage}_status.json',rows);print(json.dumps(rows,indent=2),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['plan','check','execute','status-check','status-execute']);a=p.parse_args().action
    if a=='plan':
        rows=plan();print('Validated two circuits; 1000 shots; 559.20 estimated HQC')
    elif a.startswith('status-'):asyncio.run(status(a.removeprefix('status-')))
    else:submit(a)
