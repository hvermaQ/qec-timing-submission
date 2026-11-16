"""Fetch and preserve raw payloads for the six existing H2-2 jobs."""
import hashlib
import json
from pathlib import Path
from aqora import QPUJob

run = Path(__file__).resolve().parent
for folder in sorted(run.glob('n*'), key=lambda p: int(p.name[1:])):
    path = folder / 'job.json'
    record = json.loads(path.read_text())
    assert record['platform'] == 'nexus:H2-2'
    job = QPUJob.from_id(record['job_id'])
    record['job'] = dict(record.get('job', {}), **dict(job.refresh()))
    assert record['job']['platform']['name'] == 'H2-2'
    assert record['job']['status'] == 'COMPLETED' and not record['job']['error']
    metadata = []
    for result in job.results(raise_on_item_error=False):
        assert not result.error and result.raw
        rawpath = folder / f'result_{result.index}.txt'
        if rawpath.exists():
            assert rawpath.read_text() == result.raw, 'Previously saved result changed'
        else:
            rawpath.write_text(result.raw)
        metadata.append(dict(index=result.index, error=result.error,
                             format=result.serialization_format,
                             raw_sha256=hashlib.sha256(rawpath.read_bytes()).hexdigest()))
    assert len(metadata) == 1
    record['results'] = metadata
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(record, indent=2, default=str) + '\n')
    temp.replace(path)
    print(folder.name, record['shots'], record['job_id'], metadata[0]['raw_sha256'], flush=True)
