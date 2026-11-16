import asyncio,json
from pathlib import Path
from aqora import Client
ROOT=Path(__file__).resolve().parents[3]  # repo root (was /Users/harshank_s/qec-timing-submission)
async def main():
 rows=[]
 for d in [3,5]:
  j=json.loads((ROOT/f'results/sleep/d{d}_free_idle_g_fit.json').read_text())
  for r in j['rows']:
   for s in r['sources']: rows.append(dict(distance=d,rounds=r['rounds'],shots=s['shots'],job_id=s['job_id']))
 assert len({r['job_id'] for r in rows})==len(rows)
 c=Client();await c.authenticate()
 q='{ '+' '.join(f'j{i}: node(id: {json.dumps(r["job_id"])}) {{ ... on ProviderJob {{ id status error hqcCost }} }}' for i,r in enumerate(rows))+' }'
 result=await c.send(q)
 for i,r in enumerate(rows):r['provider']=result[f'j{i}']
 (ROOT/'results/sleep/hardware_budget/job_costs.json').write_text(json.dumps(rows,indent=2),encoding='utf-8',newline='\n')
 for d in [3,5]: print(d,sum(r['provider']['hqcCost'] for r in rows if r['distance']==d))
asyncio.run(main())
