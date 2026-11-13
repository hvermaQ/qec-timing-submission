"""Cancel only saved H2-1 jobs currently reported WAITING, preserving an audit log."""
import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path

from aqora import Client

RUN = Path(__file__).resolve().parent
FIELDS = 'id providerId status error hqcCost resultCount platform { name provider }'


def save(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    temp.replace(path)


async def main():
    paths = [RUN.parent / 'h2_1_hardware_d3_x_n2_t1_250' / 'job.json']
    paths += sorted(RUN.glob('n*/job.json'), key=lambda p: int(p.parent.name[1:]))
    client = Client()
    await client.authenticate()
    audit_path = RUN / 'cancellation_log.json'
    audit = json.loads(audit_path.read_text()) if audit_path.exists() else []
    for path in paths:
        record = json.loads(path.read_text())
        assert record['platform'] == 'nexus:H2-1' and record['as_entity'] == 'q_sq'
        job_id = record['job_id']
        query = '{ node(id: ' + json.dumps(job_id) + ') { ... on ProviderJob { ' + FIELDS + ' } } }'
        current = (await client.send(query))['node']
        assert current['id'] == job_id and current['platform']['name'] == 'H2-1'
        record['job'] = dict(record.get('job', {}), **current)
        save(path, record)
        if current['status'] != 'WAITING':
            print(f"N={record['rounds']}: {current['status']}; retained", flush=True)
            continue
        entry = dict(job_id=job_id, rounds=record['rounds'], before=current,
                     requested_at_utc=datetime.now(timezone.utc).isoformat())
        audit.append(entry)
        save(audit_path, audit)
        mutation = 'mutation { cancelProviderJob(id: ' + json.dumps(job_id) + ') { ' + FIELDS + ' } }'
        try:
            response = (await client.send(mutation))['cancelProviderJob']
            assert response['id'] == job_id
            entry['response'] = response
            record['job'] = dict(record['job'], **response)
            save(path, record)
            print(f"N={record['rounds']}: cancellation response {response['status']}, error={response['error']}", flush=True)
        except Exception as exc:
            entry['request_error'] = str(exc)
            print(f"N={record['rounds']}: cancellation request error {exc}", flush=True)
        save(audit_path, audit)
    rows = []
    for path in paths:
        record = json.loads(path.read_text())
        query = '{ node(id: ' + json.dumps(record['job_id']) + ') { ... on ProviderJob { ' + FIELDS + ' } } }'
        current = (await client.send(query))['node']
        record['job'] = dict(record.get('job', {}), **current)
        save(path, record)
        rows.append(dict(rounds=record['rounds'], shots=record['shots'], **current))
    save(RUN / 'post_cancellation_status.json', rows)
    save(RUN / 'submission_status.json', [row for row in rows if row['rounds'] != 2])
    print(json.dumps(rows), flush=True)


if __name__ == '__main__':
    asyncio.run(main())
