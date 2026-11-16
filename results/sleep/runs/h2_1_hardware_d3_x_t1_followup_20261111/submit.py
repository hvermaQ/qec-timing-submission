"""Submit the approved five-job H2-1 sweep or refresh its saved job records."""
import argparse
import asyncio
import hashlib
import json
import subprocess
from importlib.metadata import version
from pathlib import Path

RUN = Path(__file__).resolve().parent
ROOT = RUN.parents[2]
SG = ROOT / 'SG_final_round'
PILOT = RUN.parent / 'h2_1_hardware_d3_x_n2_t1_250' / 'request.json'
PLATFORM = 'nexus:H2-1'
ENTITY = 'q_sq'
OPTIONS = {'no_opt': True}
COARSE = 'd3_fixed_sleep_690baca08b24dfd2'
RESOLUTION = 'd3_fixed_sleep_resolution_c2380924e8c69578'
SETTINGS = [(3, 350, RESOLUTION), (5, 1000, COARSE), (6, 1000, RESOLUTION),
            (10, 500, COARSE), (20, 500, COARSE)]


def save(path, record):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(record, indent=2, default=str) + '\n')
    temp.replace(path)


def plan():
    pilot = json.loads(PILOT.read_text())
    if (pilot['platform'], pilot['as_entity'], pilot['options']) != (PLATFORM, ENTITY, OPTIONS):
        raise ValueError('Pilot hardware settings differ from the approved sweep')
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    requests = []
    for rounds, shots, build in SETTINGS:
        stem = f'n{rounds}'
        program = SG / 'programs' / build / f'{stem}.bc'
        digest = hashlib.sha256(program.read_bytes()).hexdigest()
        manifest = json.loads(program.with_name('manifest.json').read_text())
        if digest != manifest['bitcode_sha256'][stem] or manifest['artificial_faults']:
            raise ValueError(f'Unexpected circuit for {stem}')
        check_path = SG / 'runs' / build / 'check' / stem / 'job.json'
        check = json.loads(check_path.read_text())
        if check['job']['status'] != 'COMPLETED' or check['job']['error']:
            raise ValueError(f'Prior syntax check failed for {stem}')
        requests.append(dict(
            platform=PLATFORM, as_entity=ENTITY, options=OPTIONS, distance=3, basis='X',
            rounds=rounds, shots=shots, total_requested_sleep_seconds=1.0,
            delta_t_seconds=1 / (rounds - 1), parallel_sleep_verified=False,
            artificial_faults=False, program=str(program.relative_to(ROOT)),
            program_sha256=digest, prior_syntax_check_job_id=check['job_id'],
            estimated_hqc=5 + shots * (216 * rounds + 113) / 5000,
            git_commit=commit, aqora_version=version('aqora'), decoder=pilot['decoder'],
        ))
    return requests


def submit(requests):
    from aqora import QPU

    qpu = QPU(platform=PLATFORM, as_entity=ENTITY)
    qpu._graphql.ensure_authenticated()
    matches = [p for p in qpu._graphql.get_provider_platforms()
               if p['provider'].lower() == 'nexus' and p['name'] == 'H2-1']
    if len(matches) != 1:
        raise ValueError(f'Expected one physical H2-1 target, found {len(matches)}')
    save(RUN / 'plan.json', requests)
    for request in requests:
        folder = RUN / f"n{request['rounds']}"
        job_path = folder / 'job.json'
        if job_path.exists():
            print(f"Existing {folder.name}: {json.loads(job_path.read_text())['job_id']}", flush=True)
            continue
        # An existing folder without a saved ID may represent an accepted request.
        folder.mkdir()
        bitcode = (ROOT / request['program']).read_bytes()
        if hashlib.sha256(bitcode).hexdigest() != request['program_sha256']:
            raise ValueError(f'Circuit changed after preflight: {folder.name}')
        (folder / 'program.bc').write_bytes(bitcode)
        request = dict(request, resolved_platform=dict(matches[0]))
        save(folder / 'request.json', request)
        job = qpu.run(bitcode, shots=request['shots'], options=OPTIONS)
        save(job_path, dict(request, job_id=job.job_id))
        print(f"{folder.name}, {request['shots']} shots: {job.job_id}", flush=True)


async def refresh():
    from aqora import Client

    files = sorted(RUN.glob('n*/job.json'), key=lambda path: int(path.parent.name[1:]))
    if not files:
        raise ValueError('No saved jobs to refresh')
    records = [json.loads(path.read_text()) for path in files]
    client = Client()
    await client.authenticate()
    fields = 'id status error hqcCost resultCount createdAt duration platform { name provider }'
    query = '{ ' + ' '.join(
        f"j{i}: node(id: {json.dumps(record['job_id'])}) {{ ... on ProviderJob {{ {fields} }} }}"
        for i, record in enumerate(records)
    ) + ' }'
    response = await client.send(query)
    rows = []
    for i, (path, record) in enumerate(zip(files, records)):
        job = response[f'j{i}']
        if job['id'] != record['job_id'] or job['platform']['name'] != 'H2-1':
            raise ValueError(f'Unexpected status response for {path.parent.name}')
        save(path, dict(record, job=job))
        rows.append(dict(rounds=record['rounds'], shots=record['shots'], **job))
    save(RUN / 'submission_status.json', rows)
    print(json.dumps(rows), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['plan', 'submit', 'status'])
    args = parser.parse_args()
    if args.action == 'status':
        asyncio.run(refresh())
    else:
        requests = plan()
        print(f"{sum(r['shots'] for r in requests)} shots, "
              f"{sum(r['estimated_hqc'] for r in requests):,.2f} estimated HQC", flush=True)
        if args.action == 'submit':
            submit(requests)
            asyncio.run(refresh())
