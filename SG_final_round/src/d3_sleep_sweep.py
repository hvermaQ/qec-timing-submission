"""Two X-check extraction rounds with a candidate all-data wait between them.

Barriers constrain ordering, but do not establish simultaneous sleep scheduling.
Execution was explicitly authorized with overlap still unverified.
"""
import argparse
import hashlib
import json
import math

from build_sleep_probe import ROOT, SOURCE, SOURCE_SHA256, BOUNDARY, SLEEP, assemble, call_counts
from single_qubit_sweep import OPTIONS, accepted

VALUES = [0.0, 0.5, 1.0]
SHOTS = 1000
VARIANTS = {'sleep_' + str(t).replace('.', 'p'): t for t in VALUES}
CONFIG = dict(experiment='d3_X_two_round_all_data_sleep', distance=3,
              extraction_rounds=2, check_sector='X only', data_qubits=list(range(9)),
              ancilla_qubit=9, durations_raw=VALUES, duration_unit='unverified',
              shots=SHOTS, platform='nexus:H2-1E', as_entity='q_sq', options=OPTIONS,
              parallel_sleep_verified=False,
              estimated_hqc_per_job=[114.0, 130.4], estimated_hqc_total=[342.0, 391.2],
              estimate_note='Excludes/includes virtual Rz; assumes no extra wait/barrier charge')


def operand(q):
    return '%Qubit* null' if q == 0 else f'%Qubit* inttoptr (i64 {q} to %Qubit*)'


def qir(duration):
    if not math.isfinite(duration) or duration < 0:
        raise ValueError('Invalid raw duration')
    source = SOURCE.with_suffix('.ll').read_text()
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA256 or source.count(BOUNDARY) != 1:
        raise ValueError('Baseline changed; re-inspect extraction boundary')
    barrier = '  call void @__quantum__qis__barrier10__body(' + ', '.join(operand(q) for q in range(10)) + ')\n'
    sleeps = ''.join(f'  call void @{SLEEP}({operand(q)}, double {duration:.17e})\n' for q in range(9))
    declarations = f'declare void @{SLEEP}(%Qubit*, double)\n'
    declarations += 'declare void @__quantum__qis__barrier10__body(' + ', '.join(['%Qubit*'] * 10) + ')\n'
    return source.replace(BOUNDARY, BOUNDARY + barrier + sleeps + barrier, 1).replace(
        'declare i64 @___get_current_shot()', declarations + 'declare i64 @___get_current_shot()', 1)


BUILD = ROOT/'programs'/('d3_sleep_sweep_' + hashlib.sha256(
    (json.dumps(CONFIG, sort_keys=True) + ''.join(qir(t) for t in VALUES)).encode()).hexdigest()[:16])
RUNS = ROOT/'runs'/BUILD.name


def configure_five_point(platform='nexus:H2-1E'):
    """Select a separate fresh five-point run, preserving the previous sweep."""
    global VALUES, VARIANTS, CONFIG, BUILD, RUNS
    if platform not in ('nexus:H2-1E', 'nexus:H2-2E'):
        raise ValueError('Only H2-1E and H2-2E emulator targets are allowed')
    VALUES = [0.0, 0.1, 0.5, 0.75, 1.0]
    VARIANTS = {'sleep_' + str(t).replace('.', 'p'): t for t in VALUES}
    CONFIG = dict(CONFIG, experiment='d3_X_two_round_all_data_sleep_five_point', platform=platform,
                  durations_raw=VALUES, estimated_hqc_total=[570.0, 652.0],
                  analysis_policy='Save raw results only; analyze on user request')
    prefix = 'd3_sleep_five_point_' if platform == 'nexus:H2-1E' else 'd3_sleep_five_point_h2_2e_'
    BUILD = ROOT/'programs'/(prefix + hashlib.sha256(
        (json.dumps(CONFIG, sort_keys=True) + ''.join(qir(t) for t in VALUES)).encode()).hexdigest()[:16])
    RUNS = ROOT/'runs'/BUILD.name


def build():
    if (BUILD/'manifest.json').exists():
        manifest = json.loads((BUILD/'manifest.json').read_text())
        for name, digest in manifest['bitcode_sha256'].items():
            if hashlib.sha256((BUILD/(name+'.bc')).read_bytes()).hexdigest() != digest:
                raise RuntimeError('Saved bitcode hash mismatch')
        return
    BUILD.mkdir(exist_ok=True)
    hashes = {}
    for name, duration in VARIANTS.items():
        ll = BUILD/(name+'.ll')
        if ll.exists() and ll.read_text() != qir(duration):
            raise RuntimeError('Existing program differs')
        ll.write_text(qir(duration))
        assemble('clang', ll)
        hashes[name] = hashlib.sha256(ll.with_suffix('.bc').read_bytes()).hexdigest()
    (BUILD/'manifest.json').write_text(json.dumps(dict(CONFIG, bitcode_sha256=hashes,
        baseline_sha256=SOURCE_SHA256, execution_status='blocked_pending_parallel_sleep_verification'), indent=2)+'\n')
    config_name = 'd3_sleep_five_point_1000.json' if len(VALUES) == 5 else 'd3_sleep_sweep_1000.json'
    if CONFIG['platform'] == 'nexus:H2-2E':
        config_name = 'd3_sleep_five_point_h2_2e_1000.json'
    (ROOT/'configs'/config_name).write_text(json.dumps(CONFIG, indent=2)+'\n')
    print(BUILD, flush=True)


def check():
    from aqora import QPU
    build()
    syntax_platform = CONFIG['platform'].removesuffix('E') + 'SC'
    qpu = QPU(platform=syntax_platform, as_entity='q_sq')
    for name in VARIANTS:
        dest = RUNS/'check'/name
        dest.mkdir(parents=True, exist_ok=True)
        if (dest/'job.json').exists():
            print(name, 'already submitted', flush=True)
            continue
        request_path = dest/'request.json'
        if request_path.exists():
            raise RuntimeError('Reconcile previous submission attempt before retry')
        request = dict(platform=syntax_platform, as_entity='q_sq', shots=1,
                       options=OPTIONS, program=str(BUILD/(name+'.bc')))
        request_path.write_text(json.dumps(request, indent=2)+'\n')
        job = qpu.run((BUILD/(name+'.bc')).read_bytes(), shots=1, options=OPTIONS)
        (dest/'job.json').write_text(json.dumps(dict(request, job_id=job.job_id), indent=2)+'\n')
        print(name, job.job_id, flush=True)


def execute():
    from aqora import QPU
    build()
    for name in VARIANTS:
        if not accepted(json.loads((RUNS/'check'/name/'job.json').read_text())):
            raise RuntimeError(f'Syntax check not accepted: {name}')
    qpu = QPU(platform=CONFIG['platform'], as_entity='q_sq')
    for name in VARIANTS:
        dest = RUNS/'execute'/name
        dest.mkdir(parents=True, exist_ok=True)
        if (dest/'job.json').exists():
            print(name, 'already submitted', flush=True)
            continue
        request_path = dest/'request.json'
        if request_path.exists():
            raise RuntimeError('Reconcile previous submission attempt before retry')
        request = dict(platform=CONFIG['platform'], as_entity='q_sq', shots=SHOTS,
                       options=OPTIONS, program=str(BUILD/(name+'.bc')),
                       parallel_sleep_verified=False,
                       authorization='User explicitly authorized submission with timing unresolved')
        request_path.write_text(json.dumps(request, indent=2)+'\n')
        job = qpu.run((BUILD/(name+'.bc')).read_bytes(), shots=SHOTS, options=OPTIONS)
        (dest/'job.json').write_text(json.dumps(dict(request, job_id=job.job_id), indent=2)+'\n')
        print(name, job.job_id, flush=True)
    manifest_path = BUILD/'manifest.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['execution_status'] = 'submitted_with_parallel_sleep_unverified'
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')


def fetch(stage='check'):
    from aqora import QPUJob
    for name in VARIANTS:
        dest = RUNS/stage/name
        record = dest/'job.json'
        data = json.loads(record.read_text())
        raw_missing = any(not (dest/f"result_{r['index']}.txt").is_file()
                          for r in data.get('results', []))
        if not accepted(data) or raw_missing:
            job = QPUJob.from_id(data['job_id'])
            data['job'] = dict(job.refresh())
            if data['job'].get('status') == 'COMPLETED':
                results = job.results(raise_on_item_error=False)
                for r in results:
                    (dest/f'result_{r.index}.txt').write_text(r.raw or '')
                data['results'] = [dict(index=r.index, format=r.serialization_format,
                    error=getattr(r, 'error', None)) for r in results]
            record.write_text(json.dumps(data, indent=2, default=str)+'\n')
        print(name, data['job'].get('status'), data['job'].get('error'), flush=True)
    if stage == 'execute' and len(VALUES) == 5:
        save_collection_status()


def save_collection_status():
    """Store job states and raw-file integrity only; do not analyze outcomes."""
    rows = []
    for name in VARIANTS:
        dest = RUNS/'execute'/name
        data = json.loads((dest/'job.json').read_text())
        files = {}
        for result in data.get('results', []):
            path = dest/f"result_{result['index']}.txt"
            if path.is_file():
                files[path.name] = dict(bytes=path.stat().st_size,
                    sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        rows.append(dict(variant=name, job_id=data['job_id'],
            status=data.get('job', {}).get('status', 'SUBMITTED'), raw_files=files,
            stored_successfully=accepted(data) and len(files)==len(data.get('results', []))))
    complete = all(row['stored_successfully'] for row in rows)
    summary = dict(build=str(BUILD), analysis_status='not_started_user_requested_deferral',
                   all_results_stored=complete, jobs=rows)
    path = RUNS/'collection_status.json'
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(summary, indent=2)+'\n')
    temp.replace(path)
    if complete:
        manifest_path = BUILD/'manifest.json'
        manifest = json.loads(manifest_path.read_text())
        manifest['execution_status'] = 'completed_raw_results_stored_awaiting_user_analysis_request'
        manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'check', 'fetch-check', 'execute', 'fetch-execute'])
    parser.add_argument('--five-point', action='store_true', help='Fresh 0, 0.1, 0.5, 0.75, 1 sweep')
    parser.add_argument('--platform', choices=['nexus:H2-1E', 'nexus:H2-2E'], default='nexus:H2-1E')
    args = parser.parse_args()
    if args.five_point:
        configure_five_point(args.platform)
    elif args.platform != 'nexus:H2-1E':
        parser.error('--platform requires --five-point')
    action = args.action
    if action.startswith('fetch-'):
        fetch(action.split('-', 1)[1])
    else:
        {'build': build, 'check': check, 'execute': execute}[action]()
