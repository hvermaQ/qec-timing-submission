"""Explicitly authorized five-job 500-shot retry; preserve original requests."""
import argparse
import hashlib
import json
from fixed_sleep_d5 import BUILD, RUNS, ROOT, CONFIG, accepted

ROUNDS=[7,8,9,10,15]
DEST=ROOT/'runs'/'d5_fixed_sleep_retry_500_7_8_9_10_15'

def submit():
    from aqora import QPU
    manifest=json.loads((BUILD/'manifest.json').read_text())
    for n in ROUNDS:
        assert accepted(json.loads((RUNS/'check'/f'n{n}'/'job.json').read_text()))
        assert hashlib.sha256((BUILD/f'n{n}.bc').read_bytes()).hexdigest()==manifest['bitcode_sha256'][f'n{n}']
    DEST.mkdir(exist_ok=True)
    plan=dict(rounds=ROUNDS,shots_per_setting=500,platform=CONFIG['platform'],as_entity=CONFIG['as_entity'],options=CONFIG['options'],source_build=str(BUILD),estimated_hqc=sum(5+500*(696*n+305)/5000 for n in ROUNDS))
    (DEST/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
    qpu=QPU(platform=CONFIG['platform'],as_entity=CONFIG['as_entity'])
    for n in ROUNDS:
        folder=DEST/f'n{n}';folder.mkdir(exist_ok=True)
        record=folder/'job.json';request=folder/'request.json'
        if record.exists():
            print(f'n{n}: already submitted',flush=True);continue
        if request.exists():raise RuntimeError(f'Unresolved request: {request}; reconcile before retry')
        data=dict(rounds=n,shots=500,delta_t_seconds=1/(n-1),platform=CONFIG['platform'],as_entity=CONFIG['as_entity'],options=CONFIG['options'],program=str(BUILD/f'n{n}.bc'))
        request.write_text(json.dumps(data,indent=2)+'\n')
        job=qpu.run((BUILD/f'n{n}.bc').read_bytes(),shots=500,options=CONFIG['options'])
        record.write_text(json.dumps(dict(data,job_id=job.job_id),indent=2)+'\n')
        print(f'n{n}: {job.job_id}',flush=True)

def fetch():
    from aqora import Client
    import asyncio
    async def run():
        paths=[DEST/f'n{n}'/'job.json' for n in ROUNDS]
        records=[json.loads(p.read_text()) for p in paths]
        client=Client();await client.authenticate()
        query='{ '+' '.join(f'j{i}: node(id: {json.dumps(d["job_id"])}) {{ ... on ProviderJob {{ id status error hqcCost }} }}' for i,d in enumerate(records))+' }'
        result=await client.send(query)
        rows=[]
        for i,(path,data) in enumerate(zip(paths,records)):
            data['job']=result[f'j{i}'];path.write_text(json.dumps(data,indent=2)+'\n')
            row=dict(rounds=data['rounds'],shots=500,job_id=data['job_id'],**{k:data['job'][k] for k in ['status','error','hqcCost']})
            rows.append(row);print(json.dumps(row),flush=True)
        (DEST/'submission_status.json').write_text(json.dumps(rows,indent=2)+'\n')
        report=['# d=5 H2-1E: five 500-shot retry requests','','Explicitly authorized N=7,8,9,10,15, 500 shots each (2,500 shots). Reuses the exact previously validated bitcode and emulator options; preserves all original jobs. Gate-count cost estimate: 3,587.9 HQC if all five are accepted, including five job overheads.','', '| N | Shots | Status | HQC reported | Job ID |','|---:|---:|---|---:|---|']
        for row in rows:
            report.append(f"| {row['rounds']} | 500 | {row['error'] or row['status']} | {row['hqcCost']} | {row['job_id']} |")
        report+=['','No further retries or additional shots submitted. Provider costs for waiting jobs are not final completed-execution billing.','']
        (ROOT/'results/d5_fixed_sleep_retry_500_submission.md').write_text('\n'.join(report))
    asyncio.run(run())

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('action',choices=['submit','fetch']);args=p.parse_args()
    submit() if args.action=='submit' else fetch()
