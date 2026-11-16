"""Provider options, job records, submission plans and the aqora check/submit/fetch/status code.

Collected from the original builders (single_qubit_sweep.py, d3_sleep_sweep.py,
fixed_sleep_d3.py, fixed_sleep_d5.py) and the H2-2 d=5 scripts now archived in
results/sleep/submission_scripts/ (submit_d5_h2_2_t1_20261113.py, submit_d5_h2_2_t1_skip5_*.py,
the zero-sleep controls).

Safety:
  * aqora is imported only inside the functions that contact it, so this module (and the
    package) imports without aqora installed.
  * Every function that contacts aqora refuses unless called with confirm=True (the CLI's
    --confirm). Nothing in the migration calls them.
  * Plans are pure: `h2_2_d5_plan` computes a batch's plan.json content without writing.
  * Job records are written under results/sleep/runs/ only as new files; an in-flight
    `job.json` is updated through `paths.update_job_record`, which freezes completed records.
    Collection/status summaries go to store/sleep/ (the originals rewrote them in runs/ and
    updated build manifests in programs/).
"""
from __future__ import annotations

import asyncio
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from . import paths

# Emulator options (from single_qubit_sweep.py). Part of the hashed d=3 CONFIGs: keep this dict.
OPTIONS = {'simulator':'stabilizer','noisy_simulation':True,'no_opt':True,
           'error_params':{'idle_dephasing':True,'transport_dephasing':True}}
# Physical H2-2 options (the H2-2 scripts and controls).
H2_2_OPTIONS = {'no_opt': True}
AS_ENTITY = 'q_sq'


def accepted(data):
    return data.get('job',{}).get('status')=='COMPLETED' and bool(data.get('results')) and not any(r.get('error') for r in data['results'])


def completed(data):
    """The weaker check the zero-sleep and H2-2 scripts applied to syntax-check records."""
    return data.get('job',{}).get('status')=='COMPLETED' and not data['job'].get('error')


def syntax_platform(platform: str) -> str:
    """nexus:H2-1E -> nexus:H2-1SC, nexus:H2-2E / nexus:H2-2 -> nexus:H2-2SC."""
    return platform.removesuffix('E') + 'SC'


class NotConfirmed(PermissionError):
    pass


def require_confirm(confirm: bool, action: str) -> None:
    if confirm is not True:
        raise NotConfirmed(f'{action} contacts aqora; refusing without confirm=True (--confirm)')


def sha256(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


# --------------------------------------------------------------------------- job lists

@dataclass(frozen=True)
class Job:
    folder: str               # under <run>/<stage>/; '' for single-program runs
    program: Path             # .bc to submit
    shots: int
    fields: dict = field(default_factory=dict)   # extra request fields
    check: str | None = None  # <run>/check/<check> must pass before execute ('' = <run>/check)


def variant_jobs(build, stage, shots, **fields):
    """Sweeps: one job per variant (single_qubit_sweep, d3_sleep_sweep)."""
    return [Job(name, build.folder/(name+'.bc'), 1 if stage=='check' else shots, fields, check=name)
            for name in build.texts]


def part_jobs(build, stage):
    """Fixed-sleep batches: the original `jobs(stage)` (check per setting, execute per part)."""
    out=[]
    for p in build.plan:
        for i,shots in enumerate([1] if stage=='check' else p['parts']):
            name=p['name'] if stage=='check' else f"{p['name']}_part{i+1}"
            out.append(Job(name, build.folder/(p['name']+'.bc'), shots,
                           dict(rounds=p['rounds'],delta_t_seconds=p['delta_t_seconds']), check=p['name']))
    return out


def single_job(build, stage, shots, **fields):
    """Single-program controls (the zero-sleep runs): records at <run>/<stage>/job.json."""
    (name,) = build.texts
    return [Job('', build.folder/(name+'.bc'), 1 if stage=='check' else shots, fields, check='')]


# --------------------------------------------------------------------------- physical H2-2 d=5 plans

# Run folder -> batch. Policies are as recorded at submission: the N=3,4 skip-5 batch recorded
# the original-mapping policy (p_ext .004); its analysis later used .005 (see /AGENTS.md).
H2_2_D5_BATCHES = {
    'd5_h2_2_t1_20261113': dict(mapping='original', build=None,
        settings=[(2,500),(3,750),(4,1000),(6,750),(10,500)], policy='h2_2_d5_decoder.json', p_ext=.004,
        total_shots=3500, estimated_hqc=2570.1),
    'd5_h2_2_t1_skip5_20261114': dict(mapping='skip5', build='d5_h2_2_t1_skip5_n3_n4',
        settings=[(3,500),(4,500)], policy='h2_2_d5_decoder.json', p_ext=.004,
        total_shots=1000, estimated_hqc=559.2),
    'd5_h2_2_t1_skip5_n2_n6_20261114': dict(mapping='skip5', build='d5_h2_2_t1_skip5_n2_n6',
        settings=[(2,500),(6,500)], policy='h2_2_d5_skip5_decoder.json', p_ext=.005,
        total_shots=1000, estimated_hqc=628.8),
    'd5_h2_2_t1_skip5_n10_20261115': dict(mapping='skip5', build='d5_h2_2_t1_skip5_n10',
        settings=[(10,250)], policy='h2_2_d5_skip5_decoder.json', p_ext=.005,
        total_shots=250, estimated_hqc=368.5),
}
SKIP5_MATCHING_CALIBRATION = 'd5_h2_2_zero_sleep_n3_skip5_250_20261114/execute/raw_analysis.json'


def h2_2_d5_plan(run: str) -> dict:
    """The `plan` step of a physical H2-2 d=5 batch: validate the circuits, return plan.json content.

    Reads only (committed .ll/.bc/.roundtrip.ll/manifest and the decoder policy); writes nothing.
    `program` and `matching_calibration` are this checkout's paths; the committed plan.json
    holds the paths recorded at submission (compare via `paths.resolve_recorded`).
    """
    from .builders import d5
    from .qir import call_counts
    batch = H2_2_D5_BATCHES[run]
    skip5 = batch['mapping'] == 'skip5'
    if skip5:
        build = d5.skip5_t1(batch['build'])
        d5.materialize_skip5_t1(batch['build'])   # existing folder: verification only, no writes
    else:
        build = d5.fixed()
    BUILD = build.folder
    policy = json.loads(paths.read_text(paths.DECODERS / batch['policy']))
    assert policy['distance'] == 5 and policy['p_ext'] == batch['p_ext']
    manifest = json.loads(paths.read_text(BUILD/'manifest.json'))
    assert not manifest['artificial_faults'] and manifest['total_requested_sleep_seconds'] == 1
    rows=[]
    for n,shots in batch['settings']:
        program=BUILD/f'n{n}.bc'; digest=sha256(program)
        assert digest==manifest['bitcode_sha256'][f'n{n}']
        text=paths.read_text(BUILD/f'n{n}.ll'); assert text==build.texts[f'n{n}']
        rt=paths.read_text(BUILD/f'n{n}.roundtrip.ll')
        assert call_counts(rt)==call_counts(text)
        sleeps=re.findall(r'call void @__quantum__qis__sleep__body\([^\n]*double ([^)]+)\)',text)
        assert len(sleeps)==25*(n-1) and all(abs(float(u)-1/(n-1))<1e-14 for u in sleeps)
        row=dict(platform='nexus:H2-2',as_entity=AS_ENTITY,options=H2_2_OPTIONS,distance=5,basis='X',rounds=n,shots=shots,total_requested_sleep_seconds=1.0,delta_t_seconds=1/(n-1),artificial_faults=False,parallel_sleep_verified=False,extraction_duration_neglected=True,program=str(program),program_sha256=digest)
        if skip5:
            row.update(estimated_hqc=5+shots*((696*n+305)/5000+.001),decoder_policy=policy,qubit_mapping=dict(data_indices=list(range(5))+list(range(6,26)),ancilla_index=26,unused_index=5),matching_calibration=str(paths.RUNS/SKIP5_MATCHING_CALIBRATION))
        else:
            row.update(estimated_hqc=5+shots*(696*n+305)/5000,decoder_policy=policy)
        rows.append(row)
    assert sum(r['shots'] for r in rows)==batch['total_shots']
    assert abs(sum(r['estimated_hqc'] for r in rows)-batch['estimated_hqc'])<1e-9
    return dict(settings=rows,total_shots=batch['total_shots'],estimated_hqc=batch['estimated_hqc'])


def write_h2_2_d5_plan(run: str, dest: Path | None = None) -> Path:
    """Write the plan to `dest` (default: <runs>/<run>/plan.json, which refuses if it exists)."""
    return paths.write_json(dest or paths.RUNS/run/'plan.json', h2_2_d5_plan(run))


def h2_2_d5_jobs(run: str, stage: str) -> list[Job]:
    plan = h2_2_d5_plan(run)
    out = []
    for row in plan['settings']:
        fields = {k: v for k, v in row.items() if k not in ('platform', 'as_entity', 'options', 'shots', 'program')}
        out.append(Job(f"n{row['rounds']}", Path(row['program']), 1 if stage=='check' else row['shots'],
                       fields, check=f"n{row['rounds']}"))
    return out


# --------------------------------------------------------------------------- aqora (gated)

def submit(run_dir: Path, stage: str, jobs: list[Job], *, platform: str, options: dict,
           as_entity: str = AS_ENTITY, check_ok=accepted, resolve_platform: bool = False,
           confirm: bool = False) -> list[str]:
    """Submit `jobs` for `stage` ('check' on the syntax checker, or 'execute' on `platform`).

    Execute requires every job's check record to pass `check_ok` with the same program sha256
    (where recorded). Existing job records are skipped; a request without a job record means
    an unresolved attempt and stops the run. Returns the new job ids.
    """
    require_confirm(confirm, 'submit')
    if stage not in ('check', 'execute'):
        raise ValueError(stage)
    run_dir = Path(run_dir)
    target = syntax_platform(platform) if stage == 'check' else platform
    checks = {}
    if stage == 'execute':
        for job in jobs:
            record = json.loads(paths.read_text(run_dir/'check'/job.check/'job.json'))
            assert check_ok(record), f'Syntax check not accepted: {job.check or run_dir.name}'
            if 'program_sha256' in record:
                assert record['program_sha256'] == sha256(job.program)
            checks[job.folder] = record['job_id']
    from aqora import QPU
    qpu = QPU(platform=target, as_entity=as_entity)
    resolved = None
    if resolve_platform:   # as the H2-2 d=5 scripts did (private aqora API)
        qpu._graphql.ensure_authenticated()
        matches=[p for p in qpu._graphql.get_provider_platforms() if p['provider'].lower()=='nexus' and p['name']==target.split(':')[1]]
        assert len(matches)==1
        resolved = dict(matches[0])
    ids = []
    for job in jobs:
        dest = run_dir/stage/job.folder
        record, request = dest/'job.json', dest/'request.json'
        if record.exists():
            print(job.folder or stage, 'already submitted', flush=True)
            continue
        if request.exists():
            raise RuntimeError(f'Unresolved submission attempt: {request}; reconcile before retry')
        bitcode = job.program.read_bytes()
        data = dict(platform=target, as_entity=as_entity, shots=job.shots, options=options,
                    program=str(job.program), **job.fields)
        data['program_sha256'] = hashlib.sha256(bitcode).hexdigest()
        if resolved:
            data['resolved_platform'] = resolved
        if stage == 'execute':
            data['syntax_check_job_id'] = checks[job.folder]
        paths.write_json(request, data)
        qjob = qpu.run(bitcode, shots=job.shots, options=options)
        paths.write_json(record, dict(data, job_id=qjob.job_id))
        ids.append(qjob.job_id)
        print(job.folder or stage, qjob.job_id, flush=True)
    return ids


def fetch(run_dir: Path, stage: str, folders: list[str], *, confirm: bool = False) -> dict:
    """Refresh each job and store its raw results; never submits. Returns the collection status
    (also written to store/sleep/<run>/<stage>_collection_status.json)."""
    require_confirm(confirm, 'fetch')
    from aqora import QPUJob
    run_dir = Path(run_dir)
    for folder in folders:
        dest = run_dir/stage/folder; record = dest/'job.json'
        if not record.exists():
            print(folder, 'not submitted', flush=True); continue
        data = json.loads(paths.read_text(record))
        raw_missing = any(not (dest/f"result_{r['index']}.txt").is_file() for r in data.get('results', []))
        if accepted(data) and not raw_missing:
            print(folder, 'COMPLETED (saved)', flush=True); continue
        qjob = QPUJob.from_id(data['job_id'])
        data['job'] = dict(qjob.refresh())
        if data['job'].get('status') == 'COMPLETED':
            results = qjob.results(raise_on_item_error=False)
            for r in results:
                path = dest/f'result_{r.index}.txt'
                if not path.exists():
                    paths.write_text(path, r.raw or '')
            data['results'] = [dict(index=r.index, format=r.serialization_format,
                                    error=getattr(r, 'error', None)) for r in results]
        paths.update_job_record(record, data)
        print(folder, data['job'].get('status'), data['job'].get('error'), flush=True)
    summary = collection_status(run_dir, stage, folders)
    paths.write_json(paths.STORE/run_dir.name/f'{stage}_collection_status.json', summary)
    return summary


async def _query_status(job_ids: list[str]) -> list[dict]:
    from aqora import Client
    client = Client(); await client.authenticate()
    fields = 'id status error hqcCost resultCount platform { name provider }'
    query = '{ '+' '.join(f'j{i}: node(id: {json.dumps(j)}) {{ ... on ProviderJob {{ {fields} }} }}' for i, j in enumerate(job_ids))+' }'
    response = await client.send(query)
    return [response[f'j{i}'] for i in range(len(job_ids))]


def status(run_dir: Path, stage: str, folders: list[str], *, confirm: bool = False) -> list[dict]:
    """Provider status of submitted jobs (GraphQL), stored in each in-flight record and in
    store/sleep/<run>/<stage>_status.json."""
    require_confirm(confirm, 'status')
    run_dir = Path(run_dir)
    records = {f: run_dir/stage/f/'job.json' for f in folders if (run_dir/stage/f/'job.json').exists()}
    data = {f: json.loads(paths.read_text(p)) for f, p in records.items()}
    jobs = asyncio.run(_query_status([d['job_id'] for d in data.values()]))
    rows = []
    for (folder, record), job in zip(data.items(), jobs):
        assert job['id'] == record['job_id']
        if not record.get('results'):
            paths.update_job_record(records[folder], dict(record, job=job))
        rows.append(dict(folder=folder, shots=record['shots'], **job))
    paths.write_json(paths.STORE/run_dir.name/f'{stage}_status.json', rows)
    return rows


# --------------------------------------------------------------------------- summaries (no aqora)

def collection_status(run_dir: Path, stage: str, folders: list[str]) -> dict:
    """Job states and raw-file integrity only; no outcome analysis (from d3_sleep_sweep.py)."""
    rows = []
    for folder in folders:
        dest = Path(run_dir)/stage/folder
        if not (dest/'job.json').exists():
            rows.append(dict(folder=folder, status='NOT_SUBMITTED', stored_successfully=False)); continue
        data = json.loads(paths.read_text(dest/'job.json'))
        files = {}
        for result in data.get('results', []):
            path = dest/f"result_{result['index']}.txt"
            if path.is_file():
                files[path.name] = dict(bytes=path.stat().st_size, sha256=sha256(path))
        rows.append(dict(folder=folder, job_id=data['job_id'],
                         status=data.get('job', {}).get('status', 'SUBMITTED'), raw_files=files,
                         stored_successfully=accepted(data) and len(files) == len(data.get('results', []))))
    return dict(run=Path(run_dir).name, stage=stage,
                all_results_stored=all(r['stored_successfully'] for r in rows), jobs=rows)
