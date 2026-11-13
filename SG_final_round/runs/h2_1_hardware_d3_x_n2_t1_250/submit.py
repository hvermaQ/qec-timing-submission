import hashlib
import json
import shutil
import subprocess
from importlib.metadata import version
from pathlib import Path

from aqora import QPU

root = Path.cwd()
program = root / 'SG_final_round/programs/d3_fixed_sleep_690baca08b24dfd2/n2.bc'
bitcode = program.read_bytes()
digest = hashlib.sha256(bitcode).hexdigest()
assert digest == '84ae4a804445d0355299912ffd6868f91edd30e0ff7a7bf2719eec6e3058f599'
run = root / 'SG_final_round/runs/h2_1_hardware_d3_x_n2_t1_250'
if run.exists():
    raise SystemExit(f'Run directory already exists. Reconcile its request before retrying: {run}')

platform = 'nexus:H2-1'
entity = 'q_sq'
shots = 250
options = {'no_opt': True}
qpu = QPU(platform=platform, as_entity=entity)
qpu._graphql.ensure_authenticated()
matches = [p for p in qpu._graphql.get_provider_platforms()
           if p['provider'].lower() == 'nexus' and p['name'] == 'H2-1']
if len(matches) != 1:
    raise SystemExit(f'Expected one physical {platform} target, found {len(matches)}. No job submitted.')
print(f'Confirmed {platform}. Estimated cost: 32.25 HQC.', flush=True)
request = dict(platform=platform, resolved_platform=dict(matches[0]), as_entity=entity,
               shots=shots, options=options, distance=3, basis='X', rounds=2,
               total_requested_sleep_seconds=1.0, delta_t_seconds=1.0,
               program=str(program.relative_to(root)), program_sha256=digest,
               estimated_hqc=32.25, parallel_sleep_verified=False,
               git_commit=subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
               aqora_version=version('aqora'),
               decoder=dict(type='sleep-dependent MWPM', p_ext=.002, p_read=.001,
                            linear_rate_per_second=.0028, frequency_hz=.043,
                            frequency_multiplier=2.0))
run.mkdir()
(run / 'program.bc').write_bytes(bitcode)
shutil.copyfile(__file__, run / 'submit.py')
(run / 'request.json').write_text(json.dumps(request, indent=2, default=str) + '\n')
job = qpu.run(bitcode, shots=shots, options=options)
record = dict(request, job_id=job.job_id)
job_file = run / 'job.json'
job_file.write_text(json.dumps(record, indent=2, default=str) + '\n')
print(f'Job ID: {job.job_id}', flush=True)
record['job'] = dict(job.refresh())
job_file.write_text(json.dumps(record, indent=2, default=str) + '\n')
print(json.dumps(record['job'], default=str), flush=True)
