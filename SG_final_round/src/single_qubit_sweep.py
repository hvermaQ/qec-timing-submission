"""Explicit-sleep 1000-shot sweep; reuse the validated one-qubit pilot QIR."""
import argparse
import hashlib
import json
import subprocess
from single_qubit_pilot import ROOT, qir
from analyze_single_qubit_pilot import wilson

VALUES = [0.0, 0.1, 0.5, 0.75, 1.0]
VARIANTS = {'sleep_' + str(t).replace('.', 'p'): t for t in VALUES}
SHOTS = 1000
OPTIONS = {'simulator':'stabilizer','noisy_simulation':True,'no_opt':True,
           'error_params':{'idle_dephasing':True,'transport_dephasing':True}}
CONFIG = dict(experiment='single_qubit_explicit_sleep_1000',durations_raw=VALUES,
              duration_unit='unverified',shots=SHOTS,platform='nexus:H2-1E',as_entity='q_sq',options=OPTIONS)
BUILD = ROOT/'programs'/('single_qubit_sweep_'+hashlib.sha256(
    (json.dumps(CONFIG,sort_keys=True)+''.join(qir(t) for t in VALUES)).encode()).hexdigest()[:16])
RUNS = ROOT/'runs'/BUILD.name


def build():
    if (BUILD/'manifest.json').exists():
        manifest=json.loads((BUILD/'manifest.json').read_text())
        for name, digest in manifest['bitcode_sha256'].items():
            assert hashlib.sha256((BUILD/(name+'.bc')).read_bytes()).hexdigest()==digest
        return
    BUILD.mkdir(exist_ok=True)
    hashes={}
    for name,t in VARIANTS.items():
        ll=BUILD/(name+'.ll')
        ll.write_text(qir(t))
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-x','ir','-c','-emit-llvm','-O0',str(ll),'-o',str(ll.with_suffix('.bc'))],check=True,capture_output=True)
        rt=BUILD/(name+'.roundtrip.ll')
        subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(ll.with_suffix('.bc')),'-o',str(rt)],check=True,capture_output=True)
        body=rt.read_text()
        assert body.count('call void @__quantum__qis__sleep__body')==1
        assert body.count('call void @__quantum__qis__phasedx__body')==2
        assert body.count('call void @__quantum__qis__mz__body')==1
        assert '"required_num_qubits"="1"' in body
        hashes[name]=hashlib.sha256(ll.with_suffix('.bc').read_bytes()).hexdigest()
    (BUILD/'manifest.json').write_text(json.dumps(dict(CONFIG,bitcode_sha256=hashes,local_validation='all 5 LLVM assembly and roundtrip checks passed'),indent=2)+'\n')
    (ROOT/'configs/single_qubit_sweep_1000.json').write_text(json.dumps(CONFIG,indent=2)+'\n')
    print(BUILD,flush=True)


def accepted(data):
    return data.get('job',{}).get('status')=='COMPLETED' and bool(data.get('results')) and not any(r.get('error') for r in data['results'])


def submit(stage):
    from aqora import QPU
    build()
    if stage=='execute':
        for name in VARIANTS:
            assert accepted(json.loads((RUNS/'check'/name/'job.json').read_text())), f'Check not accepted: {name}'
    platform='nexus:H2-1SC' if stage=='check' else CONFIG['platform']
    qpu=QPU(platform=platform,as_entity='q_sq')
    for name in VARIANTS:
        dest=RUNS/stage/name
        dest.mkdir(parents=True,exist_ok=True)
        record=dest/'job.json'
        if record.exists():
            print('Already submitted:',name,flush=True)
            continue
        request_path=dest/'request.json'
        if request_path.exists():
            raise RuntimeError(f'Unresolved submission attempt: {request_path}; reconcile before retry')
        request=dict(platform=platform,as_entity='q_sq',shots=1 if stage=='check' else SHOTS,
                     options=OPTIONS,program=str(BUILD/(name+'.bc')))
        request_path.write_text(json.dumps(request,indent=2)+'\n')
        job=qpu.run((BUILD/(name+'.bc')).read_bytes(),shots=request['shots'],options=OPTIONS)
        record.write_text(json.dumps(dict(request,job_id=job.job_id),indent=2)+'\n')
        print(name,job.job_id,flush=True)


def fetch(stage):
    from aqora import QPUJob
    for name in VARIANTS:
        dest=RUNS/stage/name
        record=dest/'job.json'
        if not record.exists():
            print(name,'not submitted',flush=True)
            continue
        data=json.loads(record.read_text())
        if accepted(data):
            print(name,'COMPLETED (saved)',flush=True)
            continue
        job=QPUJob.from_id(data['job_id'])
        state=dict(job.refresh())
        data['job']=state
        if state.get('status')=='COMPLETED':
            results=job.results(raise_on_item_error=False)
            for r in results:
                (dest/f'result_{r.index}.txt').write_text(r.raw or '')
            data['results']=[dict(index=r.index,format=r.serialization_format,error=getattr(r,'error',None)) for r in results]
        record.write_text(json.dumps(data,indent=2,default=str)+'\n')
        print(name,state.get('status'),state.get('error'),flush=True)


def analyze():
    rows=[]
    for name,t in VARIANTS.items():
        dest=RUNS/'execute'/name
        job=json.loads((dest/'job.json').read_text())
        assert accepted(job), f'Incomplete: {name}'
        raw=json.loads((dest/'result_0.txt').read_text())
        assert all(b[0]=='m0' for b in raw['bits'])
        counts=raw['counts_formatted']
        assert all(int(c['bitstring'],2) in [0,1] for c in counts)
        n=sum(c['count'] for c in counts)
        k=sum(c['count'] for c in counts if int(c['bitstring'],2)==1)
        assert n==SHOTS==len(raw['shots']['array'])
        assert sum(any(b for b in shot) for shot in raw['shots']['array'])==k
        rows.append(dict(duration_raw=t,shots=n,errors=k,error_rate=k/n,wilson_95=wilson(k,n),job_id=job['job_id']))
    data=dict(CONFIG,build=str(BUILD.relative_to(ROOT)),rows=rows,estimated_hqc=37.0,actual_billed_hqc=None)
    (ROOT/'results/single_qubit_sweep_1000.json').write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(data,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('action',choices=['build','check','execute','fetch-check','fetch-execute','analyze'])
    a=p.parse_args().action
    if a=='build': build()
    elif a=='analyze': analyze()
    elif a.startswith('fetch-'): fetch(a.split('-',1)[1])
    else: submit(a)
