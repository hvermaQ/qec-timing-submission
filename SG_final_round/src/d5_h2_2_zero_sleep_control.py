"""Explicit-zero d=5, two-extraction control, 500 authorized H2-2 shots."""
import argparse
import hashlib
import json
import re
import subprocess

from fixed_sleep_d5 import ROOT, SOURCE, SOURCE_SHA256, qir
from build_sleep_probe import call_counts
OPTIONS = {"no_opt": True}

BUILD = ROOT / 'programs/d5_h2_2_zero_sleep_n2'
RUNS = ROOT / 'runs/d5_h2_2_zero_sleep_n2_500_20261113'


def build():
    original = qir(2)
    pattern = r'(@__quantum__qis__sleep__body\([^\n]*double )[^)\n]+'
    text, count = re.subn(pattern, r'\g<1>0.00000000000000000e+00', original)
    assert count == 25
    assert call_counts(text) == call_counts(original)
    assert re.sub(pattern, r'\g<1>ZERO', text) == re.sub(pattern, r'\g<1>ZERO', original)
    BUILD.mkdir(exist_ok=True)
    program = BUILD / 'n2.bc'
    ll = program.with_suffix('.ll')
    if program.exists():
        manifest = json.loads((BUILD / 'manifest.json').read_text())
        assert ll.read_text() == text
        assert hashlib.sha256(program.read_bytes()).hexdigest() == manifest['bitcode_sha256']['n2']
        return program
    ll.write_text(text)
    subprocess.run(['clang', '-target', 'aarch64-unknown-linux-gnu', '-x', 'ir', '-c',
                    '-emit-llvm', '-O0', str(ll), '-o', str(program)], check=True, capture_output=True)
    roundtrip = BUILD / 'n2.roundtrip.ll'
    subprocess.run(['clang', '-target', 'aarch64-unknown-linux-gnu', '-S', '-emit-llvm',
                    '-O0', str(program), '-o', str(roundtrip)], check=True, capture_output=True)
    assert call_counts(roundtrip.read_text()) == call_counts(text)
    sleep_calls = [line for line in roundtrip.read_text().splitlines()
                   if 'call void @__quantum__qis__sleep__body' in line]
    assert len(sleep_calls) == 25 and all('double 0.000000e+00' in line for line in sleep_calls)
    manifest = dict(distance=5, basis='X', rounds=[2], total_requested_sleep_seconds=0.0,
                    explicit_sleep_calls=25, delta_t_seconds=0.0, shots=500,
                    platform='nexus:H2-2', as_entity='q_sq', options=OPTIONS,
                    source=str(SOURCE), source_sha256=SOURCE_SHA256,
                    bitcode_sha256={'n2': hashlib.sha256(program.read_bytes()).hexdigest()},
                    estimated_hqc=174.7)
    (BUILD / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print('Validated 25 explicit zero sleeps; all other QIR instructions match the T=1 N=2 program.', flush=True)
    return program


def submit(stage):
    from aqora import QPU
    program = build()
    if stage == 'execute':
        checked = json.loads((RUNS / 'check/job.json').read_text())['job']
        assert checked['status'] == 'COMPLETED' and not checked.get('error')
    folder = RUNS / stage
    folder.mkdir(parents=True, exist_ok=True)
    record, request = folder / 'job.json', folder / 'request.json'
    if record.exists():
        print(record.read_text(), flush=True)
        return
    assert not request.exists(), 'Reconcile unresolved request before retrying'
    platform = 'nexus:H2-2SC' if stage == 'check' else 'nexus:H2-2'
    data = dict(platform=platform, as_entity='q_sq', shots=1 if stage == 'check' else 500,
                program=str(program), options=OPTIONS, distance=5, rounds=2,
                delta_t_seconds=0.0, total_requested_sleep_seconds=0.0, basis='X', artificial_faults=False, estimated_hqc=174.7, program_sha256=hashlib.sha256(program.read_bytes()).hexdigest())
    request.write_text(json.dumps(data, indent=2) + '\n')
    job = QPU(platform=platform, as_entity='q_sq').run(program.read_bytes(), shots=data['shots'], options=OPTIONS)
    data['job_id'] = job.job_id
    record.write_text(json.dumps(data, indent=2) + '\n')
    print(stage, job.job_id, flush=True)


def status(stage):
    from aqora import QPUJob
    path = RUNS / stage / 'job.json'
    data = json.loads(path.read_text())
    data['job'] = dict(QPUJob.from_id(data['job_id']).refresh())
    path.write_text(json.dumps(data, indent=2, default=str) + '\n')
    print(json.dumps({key: data['job'].get(key) for key in ['id', 'status', 'error', 'hqcCost']}, indent=2), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('action', choices=['build', 'check', 'execute', 'status-check', 'status-execute'])
    action = parser.parse_args().action
    if action == 'build':
        build()
    elif action.startswith('status-'):
        status(action.removeprefix('status-'))
    else:
        submit(action)
