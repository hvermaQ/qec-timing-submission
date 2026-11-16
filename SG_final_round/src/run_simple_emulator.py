"""Build, check, run, collect and decode one T_sleep=1 s, N=2, d=3 job.

Run from the repository root with an Aqora-authenticated Python environment:
    python SG_final_round/src/run_simple_emulator.py --shots 100
Use --build-only for a local LLVM check without provider access.
"""
import argparse
import hashlib
import json
import subprocess
import time
from pathlib import Path

from fixed_sleep_d3 import ROOT, SOURCE, SOURCE_SHA256, call_counts, qir
from single_qubit_sweep import OPTIONS, accepted


def save(path, data):
    path.write_text(json.dumps(data, indent=2, default=str) + '\n')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build(folder, shots, entity):
    """Keep this example's artifacts separate from the archived sweeps."""
    folder.mkdir(parents=True, exist_ok=True)
    text = qir(2)
    config = dict(distance=3, basis='X', rounds=2, shots=shots,
                  total_requested_sleep_seconds=1.0, delta_t_seconds=1.0,
                  platform='nexus:H2-1E', as_entity=entity, options=OPTIONS,
                  baseline_sha256=SOURCE_SHA256,
                  qir_sha256=hashlib.sha256(text.encode()).hexdigest())
    manifest_path = folder / 'manifest.json'
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())
        if manifest['config'] != config:
            raise RuntimeError('Settings changed; choose a new --output directory')
        if digest(folder / 'program.bc') != manifest['bitcode_sha256']:
            raise RuntimeError('Saved bitcode hash mismatch')
        return manifest
    (folder / 'program.ll').write_text(text)
    common = ['clang', '-target', 'aarch64-unknown-linux-gnu', '-emit-llvm', '-O0']
    subprocess.run(common + ['-x', 'ir', '-c', str(folder / 'program.ll'),
                             '-o', str(folder / 'program.bc')], check=True)
    subprocess.run(common + ['-S', str(folder / 'program.bc'),
                             '-o', str(folder / 'program.roundtrip.ll')], check=True)
    if call_counts((folder / 'program.roundtrip.ll').read_text()) != call_counts(text):
        raise RuntimeError('LLVM roundtrip changed the instruction counts')
    manifest = dict(config=config, bitcode_sha256=digest(folder / 'program.bc'))
    save(manifest_path, manifest)
    return manifest


def run_job(folder, platform, shots, entity, poll_seconds, timeout):
    """Resume a recorded job; never blindly retry an unresolved submission."""
    from aqora import QPU, QPUJob

    folder.mkdir(parents=True, exist_ok=True)
    record = folder / 'job.json'
    if record.exists():
        data = json.loads(record.read_text())
    else:
        request = folder / 'request.json'
        if request.exists():
            raise RuntimeError(f'Unresolved submission: reconcile {request} before retrying')
        data = dict(platform=platform, shots=shots, as_entity=entity, options=OPTIONS,
                    bitcode_sha256=digest(folder.parent / 'program.bc'))
        save(request, data)
        job = QPU(platform=platform, as_entity=entity).run(
            (folder.parent / 'program.bc').read_bytes(), shots=shots, options=OPTIONS)
        data['job_id'] = job.job_id
        save(record, data)
    deadline = time.monotonic() + timeout
    while not accepted(data):
        job = QPUJob.from_id(data['job_id'])
        data['job'] = dict(job.refresh())
        status = data['job'].get('status')
        save(record, data)
        print(f"{platform}: {data['job_id']} {status}", flush=True)
        if status == 'COMPLETED':
            results = list(job.results(raise_on_item_error=False))
            data['results'] = []
            for result in results:
                path = folder / f'result_{result.index}.txt'
                path.write_text(result.raw or '')
                data['results'].append(dict(index=result.index,
                    format=result.serialization_format, error=getattr(result, 'error', None),
                    raw_sha256=digest(path)))
            save(record, data)
            if not accepted(data) or data['job'].get('error'):
                raise RuntimeError(f'Job returned errors: {record}')
            break
        if data['job'].get('error') or status in {
                'FAILED', 'ERROR', 'CANCELLED', 'CANCELED', 'REJECTED', 'DELETED'}:
            raise RuntimeError(f'Job did not succeed: {record}')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError(f'Job still pending; rerun the same command to resume: {record}')
        time.sleep(min(poll_seconds, remaining))
    for result in data['results']:
        if digest(folder / f"result_{result['index']}.txt") != result['raw_sha256']:
            raise RuntimeError(f'Saved result hash mismatch: {record}')
    return data


def analyze(folder, manifest, job):
    """Use the historical emulator MWPM prescription, fixed before execution."""
    import numpy as np
    from dataclasses import replace
    from analyze_d3_sleep_sweep import unpack
    from analyze_single_qubit_pilot import wilson
    from qec_timing.hardware.providers import _register_builtins
    from qec_timing.spec import spec_from_json
    from qec_timing.schedule import Schedule
    from qec_timing.hardware.records import bits_from_shots, record_from_bits
    from qec_timing.hardware.collect import paper_graph
    from qec_timing.backends.stim_phenom import dem_for
    from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder

    _register_builtins()
    count = manifest['config']['shots']
    raw_path = folder / 'execute' / 'result_0.txt'
    shots = unpack(json.loads(raw_path.read_text()), shots=count, n_rounds=2)
    base = spec_from_json(json.loads(SOURCE.with_suffix('.json').read_text())['spec'])
    spec = replace(base, schedule=Schedule.rounds(1.0, 2), shots=count)
    syndromes, data = bits_from_shots(shots, 2, 4, 9)
    record = record_from_bits(spec, syndromes, data)
    dem = dem_for(paper_graph(spec, .002, 0, .001))
    dem_path = folder / 'decoder.dem'
    dem_path.write_text(dem)
    predicted = PyMatchingDecoder(dem).decode_batch(record.detectors)
    failures = int(np.any(predicted != record.observables, axis=1).sum())
    result = dict(manifest, job_id=job['job_id'], shots=count,
                  logical_failures=failures, logical_error_probability=failures/count,
                  wilson_95=wilson(failures, count), raw_sha256=digest(raw_path),
                  dem_sha256=digest(dem_path),
                  decoder=dict(model='historical fixed phenomenological MWPM',
                               p_data=.002, p_read=.001, lam=0),
                  extraction_duration_neglected=True, parallel_sleep_verified=False)
    save(folder / 'analysis.json', result)
    print(f'Logical failures: {failures}/{count} (P_L={failures/count:.6f})')
    print(f'Results: {folder / "analysis.json"}')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--shots', type=int, default=100)
    parser.add_argument('--as-entity', default='q_sq')
    parser.add_argument('--output', type=Path, default=ROOT / 'runs/simple_d3_t1_n2')
    parser.add_argument('--build-only', action='store_true')
    parser.add_argument('--poll-seconds', type=float, default=10)
    parser.add_argument('--timeout', type=float, default=3600,
                        help='Maximum wait in seconds per job; rerun to resume')
    args = parser.parse_args()
    if args.shots <= 0 or not 0 < args.poll_seconds <= 60 or not 0 < args.timeout < float('inf'):
        parser.error('shots and timeout must be positive; poll-seconds must be in (0, 60]')
    folder = args.output.resolve()
    manifest = build(folder, args.shots, args.as_entity)
    print(f'Built T_sleep=1 s, N=2, d=3: {folder}', flush=True)
    if args.build_only:
        return
    # Fail on missing dependencies before spending emulator credits.
    import aqora  # noqa: F401
    import numpy  # noqa: F401
    import stim  # noqa: F401
    import pymatching  # noqa: F401
    run_job(folder / 'check', 'nexus:H2-1SC', 1, args.as_entity,
            args.poll_seconds, args.timeout)
    job = run_job(folder / 'execute', 'nexus:H2-1E', args.shots, args.as_entity,
                  args.poll_seconds, args.timeout)
    analyze(folder, manifest, job)


if __name__ == '__main__':
    main()
