"""250-shot physical H2-2 repeat of the validated d=5 N=2 zero-sleep control."""
import argparse
import hashlib
import json
from pathlib import Path
import d5_h2_2_zero_sleep_control as control

ORIGINAL_RUNS = control.RUNS
RUNS = control.ROOT / 'runs/d5_h2_2_zero_sleep_n2_250_repeat_20261113'


def execute():
    from aqora import QPU
    program = control.build()
    digest = hashlib.sha256(program.read_bytes()).hexdigest()
    checker_path = ORIGINAL_RUNS / 'check/job.json'
    checker = json.loads(checker_path.read_text())
    assert checker['platform'] == 'nexus:H2-2SC'
    assert checker['job']['status'] == 'COMPLETED' and not checker['job'].get('error')
    assert checker['program_sha256'] == digest
    folder = RUNS / 'execute'
    folder.mkdir(parents=True, exist_ok=True)
    record, request = folder / 'job.json', folder / 'request.json'
    if record.exists():
        print(record.read_text(), flush=True)
        return
    assert not request.exists(), 'Reconcile unresolved request before retrying'
    data = dict(platform='nexus:H2-2', as_entity='q_sq', shots=250,
                program=str(program), program_sha256=digest, options=control.OPTIONS,
                distance=5, rounds=2, delta_t_seconds=0.0,
                total_requested_sleep_seconds=0.0, basis='X', artificial_faults=False,
                estimated_hqc=89.85, validation_job_id=checker['job_id'],
                validation_record=str(checker_path), repeat_of_job_id=json.loads(
                    (ORIGINAL_RUNS / 'execute/job.json').read_text())['job_id'])
    request.write_text(json.dumps(data, indent=2) + '\n')
    job = QPU(platform=data['platform'], as_entity=data['as_entity']).run(
        program.read_bytes(), shots=data['shots'], options=data['options'])
    data['job_id'] = job.job_id
    record.write_text(json.dumps(data, indent=2) + '\n')
    print('execute', job.job_id, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['build', 'execute', 'status-execute'])
    action = parser.parse_args().action
    if action == 'build':
        control.build()
    elif action == 'execute':
        execute()
    else:
        control.RUNS = RUNS
        control.status('execute')
