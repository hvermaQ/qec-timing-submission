"""Explicit-zero d=5, three-extraction control, 250 authorized H2-2 shots."""
import argparse
import hashlib
import json
import re
import subprocess

from fixed_sleep_d5 import ROOT, SOURCE, SOURCE_SHA256, qir
from build_sleep_probe import call_counts
OPTIONS = {"no_opt": True}

BUILD = ROOT / 'programs/d5_h2_2_zero_sleep_n3_skip5'
RUNS = ROOT / 'runs/d5_h2_2_zero_sleep_n3_skip5_250_20261114'


def build():
    source = ROOT / 'programs/d5_h2_2_zero_sleep_n3/n3.ll'
    original = source.read_text()
    pattern = r'%Qubit\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %Qubit\*\)|null)'
    def remap(m):
        old = int(m[1] or 0)
        new = old + (old >= 5)
        return m[0] if old < 5 else m[0].replace(f'i64 {old} ', f'i64 {new} ')
    text = re.sub(pattern, remap, original)
    text = text.replace('"required_num_qubits"="26"', '"required_num_qubits"="27"')
    ids = [int(m[1] or 0) for m in re.finditer(pattern, text)]
    assert set(ids) == set(range(27)) - {5}
    def inverse(m):
        new = int(m[1] or 0)
        return m[0] if new < 6 else m[0].replace(f'i64 {new} ', f'i64 {new-1} ')
    restored = re.sub(pattern, inverse, text).replace('"required_num_qubits"="27"', '"required_num_qubits"="26"')
    assert restored == original, 'Remapping changed more than qubit indices and declared range'
    assert call_counts(text) == call_counts(original)
    BUILD.mkdir(exist_ok=True)
    program = BUILD / 'n3.bc'
    ll = program.with_suffix('.ll')
    if program.exists():
        manifest = json.loads((BUILD/'manifest.json').read_text())
        assert ll.read_text() == text
        assert hashlib.sha256(program.read_bytes()).hexdigest() == manifest['bitcode_sha256']['n3']
        return program
    ll.write_text(text)
    subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-x','ir','-c','-emit-llvm','-O0',str(ll),'-o',str(program)],check=True,capture_output=True)
    rt = BUILD/'n3.roundtrip.ll'
    subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(program),'-o',str(rt)],check=True,capture_output=True)
    assert call_counts(rt.read_text()) == call_counts(text)
    manifest = dict(distance=5,basis='X',rounds=[3],shots=250,platform='nexus:H2-2',options=OPTIONS,
                    total_requested_sleep_seconds=0,delta_t_seconds=0,explicit_sleep_calls=50,
                    data_qubit_indices=list(range(5))+list(range(6,26)),ancilla_qubit_index=26,
                    unused_qubit_index=5,required_num_qubits=27,output_labels='Original code-position labels preserved',
                    source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    bitcode_sha256={'n3':hashlib.sha256(program.read_bytes()).hexdigest()},
                    estimated_hqc=124.90,validation='Exact inverse remapping reproduces audited original QIR; LLVM assembly and roundtrip gate counts pass')
    (BUILD/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('Validated sparse indices: data 0-4,6-25; ancilla 26; index 5 unused; output labels preserved.',flush=True)
    return program


def submit(stage):
    from aqora import QPU
    program = build()
    if stage == 'execute':
        check_record = json.loads((RUNS / 'check/job.json').read_text())
        checked = check_record['job']
        assert checked['status'] == 'COMPLETED' and not checked.get('error')
        assert check_record['program_sha256'] == hashlib.sha256(program.read_bytes()).hexdigest()
    folder = RUNS / stage
    folder.mkdir(parents=True, exist_ok=True)
    record, request = folder / 'job.json', folder / 'request.json'
    if record.exists():
        print(record.read_text(), flush=True)
        return
    assert not request.exists(), 'Reconcile unresolved request before retrying'
    platform = 'nexus:H2-2SC' if stage == 'check' else 'nexus:H2-2'
    data = dict(platform=platform, as_entity='q_sq', shots=1 if stage == 'check' else 250,
                program=str(program), options=OPTIONS, distance=5, rounds=3,
                delta_t_seconds=0.0, total_requested_sleep_seconds=0.0, basis='X', artificial_faults=False, estimated_hqc=124.90, program_sha256=hashlib.sha256(program.read_bytes()).hexdigest())
    data['qubit_mapping'] = dict(data_indices=list(range(5))+list(range(6,26)),ancilla_index=26,unused_index=5,output_labels='Original code positions')
    data['decoder_policy'] = json.loads((ROOT / 'configs/h2_2_d5_decoder.json').read_text())
    if stage == 'execute': data['syntax_check_job_id'] = check_record['job_id']
    request.write_text(json.dumps(data, indent=2) + '\n')
    job = QPU(platform=platform, as_entity='q_sq').run(program.read_bytes(), shots=data['shots'], options=OPTIONS)
    data['job_id'] = job.job_id
    record.write_text(json.dumps(data, indent=2) + '\n')
    print(stage, job.job_id, flush=True)


def status(stage):
    import asyncio
    from aqora import Client
    path = RUNS / stage / 'job.json'
    data = json.loads(path.read_text())
    async def query():
        client = Client()
        await client.authenticate()
        return await client.send('{ node(id: ' + json.dumps(data['job_id']) + ') { ... on ProviderJob { id status error hqcCost platform { name } } } }')
    data['job'] = asyncio.run(query())['node']
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
