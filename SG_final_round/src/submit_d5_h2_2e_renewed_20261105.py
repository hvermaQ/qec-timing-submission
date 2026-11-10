"""Authorized d=5 H2-2E sweep: N=7,8,9,10, 500 shots each."""
import argparse
import asyncio
import hashlib
import json
from fixed_sleep_d5 import BUILD, ROOT, CONFIG, accepted

ROUNDS=[7,8,9,10]
DEST=ROOT/'runs'/'d5_fixed_sleep_h2_2e_renewed_20261105_500_n7_8_9_10'
PLATFORM='nexus:H2-2E'
ESTIMATE=sum(5+500*(696*n+305)/5000 for n in ROUNDS)


def submit(stage):
    from aqora import QPU
    from aqora._provider.client import _run_sync
    manifest=json.loads((BUILD/'manifest.json').read_text())
    for n in ROUNDS:
        assert hashlib.sha256((BUILD/f'n{n}.bc').read_bytes()).hexdigest()==manifest['bitcode_sha256'][f'n{n}']
        if stage=='execute':
            assert accepted(json.loads((DEST/'check'/f'n{n}'/'job.json').read_text()))
    DEST.mkdir(exist_ok=True)
    plan=dict(rounds=ROUNDS,shots_per_setting=500,total_execution_shots=2000,platform=PLATFORM,as_entity=CONFIG['as_entity'],options=CONFIG['options'],source_build=str(BUILD),estimated_hqc=ESTIMATE,total_requested_sleep_seconds=1.0,parallel_sleep_verified=False,extraction_duration_neglected=True)
    (DEST/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    platform='nexus:H2-2SC' if stage=='check' else PLATFORM
    shots=1 if stage=='check' else 500
    qpu=QPU(platform=platform,as_entity=CONFIG['as_entity'])
    qpu._graphql.ensure_authenticated()
    for n in ROUNDS:
        folder=DEST/stage/f'n{n}';folder.mkdir(parents=True,exist_ok=True)
        record=folder/'job.json';request=folder/'request.json'
        if record.exists():
            print(f'n{n}: already submitted',flush=True);continue
        if request.exists():raise RuntimeError(f'Unresolved request: {request}; reconcile before retry')
        data=dict(rounds=n,shots=shots,delta_t_seconds=1/(n-1),platform=platform,as_entity=CONFIG['as_entity'],options=CONFIG['options'],program=str(BUILD/f'n{n}.bc'))
        request.write_text(json.dumps(data,indent=2)+'\n')
        if stage=='execute':
            checker=json.loads((DEST/'check'/f'n{n}'/'job.json').read_text())
            query='query($id: ID!) { node(id: $id) { ... on ProviderJob { providerModel { id } } } }'
            model=_run_sync(lambda:qpu.client.send(query,id=checker['job_id']))['node']['providerModel']['id']
            data['provider_model_id']=model
            request.write_text(json.dumps(data,indent=2)+'\n')
            response=qpu._graphql.create_provider_job(provider_model_id=model,shots=shots,provider_platform=platform,as_entity=CONFIG['as_entity'],options=CONFIG['options'])
            job_id=str(response['id'])
        else:
            job_id=qpu.run((BUILD/f'n{n}.bc').read_bytes(),shots=shots,options=CONFIG['options']).job_id
        record.write_text(json.dumps(dict(data,job_id=job_id),indent=2)+'\n')
        print(f'n{n}: {job_id}',flush=True)


def fetch(stage):
    from aqora import Client, QPUJob
    paths=[DEST/stage/f'n{n}'/'job.json' for n in ROUNDS]
    records=[json.loads(p.read_text()) for p in paths]
    async def query_status():
        client=Client();await client.authenticate()
        query='{ '+' '.join(f'j{i}: node(id: {json.dumps(d["job_id"])}) {{ ... on ProviderJob {{ id status error hqcCost resultCount results(first: 10) {{ nodes {{ index error }} }} }} }}' for i,d in enumerate(records))+' }'
        return await client.send(query)
    result=asyncio.run(query_status());rows=[]
    for i,(path,data) in enumerate(zip(paths,records)):
        data['job']=result[f'j{i}']
        if stage=='check' and data['job']['status']=='COMPLETED' and not data['job']['error']:
            metadata=data['job']['results']['nodes']
            assert len(metadata)==data['job']['resultCount']==1
            data['results']=metadata
            data['validation_evidence']='Completed checker with API per-item error metadata; sample output download unavailable'
        if stage!='check' and data['job']['status']=='COMPLETED' and not data['job']['error'] and not data.get('results'):
            results=QPUJob.from_id(data['job_id']).results(raise_on_item_error=False)
            for item in results:(path.parent/f'result_{item.index}.txt').write_text(item.raw or '')
            data['results']=[dict(index=item.index,format=item.serialization_format,error=getattr(item,'error',None)) for item in results]
        path.write_text(json.dumps(data,indent=2)+'\n')
        row=dict(rounds=data['rounds'],shots=data['shots'],job_id=data['job_id'],**{k:data['job'][k] for k in ['status','error','hqcCost']})
        rows.append(row);print(json.dumps(row),flush=True)
    (DEST/f'{stage}_status.json').write_text(json.dumps(rows,indent=2)+'\n')
    if stage=='execute':
        report=['# d=5 H2-2E: four 500-shot execution requests','','Authorized N=7,8,9,10, 500 shots each (2,000 shots). Uses the exact previously validated native QIR with fixed requested sleep of one second per data qubit, Delta t=1/(N-1), X-memory sector and no artificial injected faults. Noise options: stabilizer, noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true. Existing H2-1E jobs are preserved.', '',f'Gate-count cost estimate: {ESTIMATE:,.1f} HQC if all four are accepted, including four execution-job overheads. H2-2SC validation is required before execution.','', '| N | Shots | Status | HQC reported | Job ID |','|---:|---:|---|---:|---|']
        for row in rows:report.append(f"| {row['rounds']} | {row['shots']} | {row['error'] or row['status']} | {row['hqcCost']} | {row['job_id']} |")
        report+=['','No further retries or additional shots submitted. Provider costs for waiting jobs are not final completed-execution billing.',f'Raw records: `{DEST}`.','']
        (ROOT/'results/d5_fixed_sleep_h2_2e_renewed_20261105_submission.md').write_text('\n'.join(report))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['check','execute','fetch-check','fetch-execute']);a=p.parse_args().action
    fetch(a.split('-',1)[1]) if a.startswith('fetch-') else submit(a)
