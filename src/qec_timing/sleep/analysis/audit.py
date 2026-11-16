"""Circuit and duration audits; no hardware calls.

Ported from SG_final_round/src/ (calculations verbatim; only paths and writes changed):

    native_memory()     audit_native_memory.py: disassembles the submitted .bc (needs clang),
                        translates the native QIR to Stim, runs ideal and single-Z-fault checks
                        -> results/sleep/circuit_audit/{d*_n*.ll, *.stim, ideal_audit.json}
    duration_scales()   review_duration_scales.py: expected idle pZ per raw sleep argument from
                        config/h2_1e_emulator.json -> results/sleep/duration_scales.json
"""
import dataclasses
import hashlib
import json
import re
import struct
import subprocess

import numpy as np

from .. import paths

OUT = paths.RESULTS / 'circuit_audit'


# --------------------------------------------------------------------------- native QIR -> Stim

def _complex():
    X=np.array([[0,1],[1,0]],complex);Y=np.array([[0,-1j],[1j,0]]);Z=np.diag([1,-1])
    return X,Y,Z


def num(s):return struct.unpack('>d',bytes.fromhex(s[2:]))[0] if s.startswith('0x') else float(s)


def operands(line,kind):
 if re.search(r'\bptr ',line):
  vals=[int(x or 0) for x in re.findall(r'ptr (?:nonnull )?(?:inttoptr \(i64 (\d+) to ptr\)|null)',line)]
  return vals[-1:] if kind=='Result' else vals[:1] if 'qis__mz__' in line else vals
 return [int(x or 0) for x in re.findall(r'%'+kind+r'\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %'+kind+r'\*\)|null)',line)]


def translate(text,nd):
 import stim
 X,Y,Z=_complex()
 body=text[text.index('define dso_local'):text.index('\n}\n')]
 # Each conditional restores the measured ancilla, immediately reset again.
 for block in re.findall(r'^\w*cond_\w*case_1:.*?(?=^\w*cond_exit_)',body,re.M|re.S):
  calls=[l for l in block.splitlines() if '@__quantum__qis__' in l]
  assert len(calls)==1 and 'phasedx' in calls[0] and operands(calls[0],'Qubit')==[nd]
  assert 'br label' in block
  exit_label=re.search(r'br label %(\w+)',block)[1]
  tail=body[body.index(exit_label+':'):].splitlines()[1]
  assert 'qis__reset__body' in tail and operands(tail,'Qubit')==[nd]
 c=stim.Circuit();measured={};reads={};tags=dict(re.findall(r'@(\w+) = private .*?constant .*?c"([^"\\]+)\\00"',text));outputs={};sleep=[];wait_positions=[]
 for line in body.splitlines():
  m=re.search(r'@__quantum__qis__(\w+)__body\(',line)
  if m:
   gate=m[1];q=operands(line,'Qubit');angles=[num(v) for v in re.findall(r'double ([^, )]+)',line)]
   if gate in ['sleep','barrier26','barrier10']:
    if gate=='sleep':
     sleep.append((q[0],angles[0]))
     if q[0]==0:wait_positions.append(len(c))
    continue
   if gate=='mz':
    r=operands(line,'Result')[0];assert r not in measured;measured[r]=c.num_measurements;c.append('M',q);continue
   if gate=='reset':assert q==[nd];c.append('R',q);continue
   if gate=='phasedx':a,phi=angles;pauli=np.cos(phi)*X+np.sin(phi)*Y
   elif gate=='rz':a=angles[0];pauli=Z
   elif gate=='rzz':a=angles[0];pauli=np.kron(Z,Z)
   else:raise ValueError(gate)
   u=np.cos(a/2)*np.eye(len(pauli))-1j*np.sin(a/2)*pauli
   small=stim.Tableau.from_unitary_matrix(u,endian='little').to_circuit()
   for inst in small:c.append(inst.name,[q[t.value] for t in inst.targets_copy()],inst.gate_args_copy())
  elif '@__quantum__rt__read_result' in line:
   name=re.search(r'(%[\w]+) =',line)[1];reads[name]=measured[operands(line,'Result')[0]]
  elif '@__quantum__rt__bool_record_output' in line:
   name=re.search(r'\(i1 (%\w+)',line)[1];tag=tags[re.findall(r'@(\w+)',line)[-1]];assert tag not in outputs;outputs[tag]=reads[name]
 return c,outputs,sleep,wait_positions


def audit(path,nd,n,label):
 import stim
 from qec_timing.codes.base import checks_of
 from qec_timing.spec import spec_from_json
 text=paths.read_text(path);c,tags,sleeps,waits=translate(text,nd)
 expected={f'm{i}' for i in range(nd)}|{f's{r}_{i}' for r in range(n) for i in range((nd-1)//2)}
 assert set(tags)==expected and len(set(tags.values()))==len(tags)
 # Exact expectations, then 4096 ideal shots as a separate sampler check.
 sim=stim.TableauSimulator();expect=[]
 for inst in c:
  if inst.name=='M':
   for t in inst.targets_copy():expect.append(sim.peek_z(t.value));sim.measure(t.value)
  else:sim.do(inst)
 sample=c.compile_sampler(seed=20261114).sample(4096)
 rates={tag:float(sample[:,idx].mean()) for tag,idx in tags.items()}
 bad={tag:v for tag,v in rates.items() if v!=0}
 row=dict(label=label,path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),distance=int(np.sqrt(nd)),rounds=n,measurement_count=c.num_measurements,output_count=len(tags),sleep_calls=len(sleeps),sleep_sum_by_qubit={str(q):sum(u for k,u in sleeps if k==q) for q in range(nd)},nonzero_or_random_exact_measurements=sum(v!=1 for v in expect),nonzero_ideal_outputs=bad)
 # Every single Z fault at every inter-round wait must produce the known
 # X-check parities and the corresponding final-data bit, with no randomness.
 fault_tests=0
 if waits:
  specpath=paths.REPO/f'results/hardware/programs/d{int(np.sqrt(nd))}_X_r5_p0.json'
  if not specpath.exists():
   specpath=paths.REPO/'results/hardware/programs/d3_X_r2_p0.json'
  spec=spec_from_json(json.loads(paths.read_text(specpath))['spec']);checks=checks_of(spec.code,'X')
  for w,pos in enumerate(waits):
   for q in range(nd):
    sim=stim.TableauSimulator();sim.do(c[:pos]);sim.z(q);sim.do(c[pos:]);bits=sim.current_measurement_record()
    for tag,idx in tags.items():
     if tag.startswith('m'):expected_bit=int(tag[1:])==q
     else:
      r,ci=map(int,tag[1:].split('_'));expected_bit=r>w and q in checks[ci].support
     assert bits[idx]==expected_bit,(label,w,q,tag,bits[idx],expected_bit)
    fault_tests+=1
 row['single_Z_wait_fault_tests_passed']=fault_tests
 paths.write_text(OUT/(label+'.stim'), str(c));print(label,'nonzero/random exact',row['nonzero_or_random_exact_measurements'],'nonzero outputs',bad,flush=True)
 return row


def native_memory(clang='clang'):
 """Ideal Clifford audit of the submitted physical H2-2 programs. Needs clang (not on Windows here)."""
 from qec_timing.hardware.providers import _register_builtins
 _register_builtins()
 rows=[]
 for d,folder in [(5,'d5_h2_2_t1_20261113'),(3,'h2_2_hardware_d3_x_t1_20261111')]:
  records=list((paths.RUNS/folder).glob('execute/n*/job.json')) if d==5 else list((paths.RUNS/folder).glob('n*/job.json'))
  for p in sorted(records):
   j=json.loads(paths.read_text(p));program=paths.resolve_recorded(j['program'])
   assert hashlib.sha256(program.read_bytes()).hexdigest()==j['program_sha256']
   ll=OUT/f"d{d}_n{j['rounds']}.ll"
   OUT.mkdir(parents=True,exist_ok=True)
   subprocess.run([clang,'-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(program),'-o',str(ll)],check=True,capture_output=True)
   rows.append(audit(ll,d*d,j['rounds'],f"d{d}_n{j['rounds']}"))
 rows.append(audit(paths.BASELINE_D5,25,5,'d5_original_n5'))
 paths.write_json(OUT/'ideal_audit.json', rows)
 return rows


# --------------------------------------------------------------------------- duration scales

def duration_scales():
    """Reproduce conditional wait-noise estimates from the saved H2 calibration.

    These are estimates for an isolated idle channel, not measured sleep durations,
    predictions of logical failure, or a verified configuration of an aqora job.
    Relative paths are recorded with '/' separators, as on the machine that made the
    committed result.
    """
    from qec_timing.hardware.calibration import Calibration
    REPO = paths.REPO
    path = REPO / "config/h2_1e_emulator.json"
    cal = Calibration.load(path)
    config = json.loads(paths.read_text(paths.CONFIG / "sleep_probe.json"))
    durations = config["finite_durations_raw"]
    rows = []
    for duration in durations + [t for t in [0.5, 1.0] if t not in durations]:
        p = cal.idle_pz(duration)
        rows.append({
            "raw_argument_if_seconds": duration,
            "milliseconds_if_seconds": duration * 1000,
            "included_in_current_sweep": duration in durations,
            "p_z_saved_cycles_convention": p,
            "expected_target_z_faults_per_1000_shots": p * 1000,
            "p_z_alternative_radians_convention": dataclasses.replace(cal, quad_convention="radians").idle_pz(duration),
            "p_z_without_stabilizer_multiplier": dataclasses.replace(cal, quad_factor=1.0).idle_pz(duration),
        })
    previous = REPO / "results/hardware/h2_1e_anchored_idle_long.json"
    data = {
        "calibration_source": path.relative_to(REPO).as_posix(),
        "calibration_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "gamma_per_second_assumed": cal.gamma,
        "quadratic_rate_cycles_per_second_assumed": cal.quad_rate,
        "coherent_to_incoherent_factor_assumed": cal.quad_factor,
        "omega_radians_per_second": cal.omega,
        "linear_quadratic_small_time_crossover_seconds": cal.gamma / (cal.omega / 2) ** 2,
        "assumptions": [
            "raw sleep argument interpreted as seconds for this calculation ONLY",
            "saved cycles convention and factor 2; job simulator mode is unverified",
            "one uninterrupted idle channel on q4; no DD; no extra channel splitting",
            "expected faults exclude gate/readout/preparation errors and correction",
        ],
        "rows": rows,
        "previous_anchored_run_source": previous.relative_to(REPO).as_posix(),
        "previous_anchored_run_sha256": hashlib.sha256(previous.read_bytes()).hexdigest(),
        "previous_anchored_counts": json.loads(paths.read_text(previous)),
        "previous_fit_status": "3.6 ms/layer estimate withdrawn after L=128; no confirmed layer-to-seconds conversion",
        "sleep_unit_status": "unverified",
        "new_emulator_jobs_submitted": 0,
    }
    out = paths.RESULTS / "duration_scales.json"
    paths.write_json(out, data)
    for row in rows:
        print(f"{row['milliseconds_if_seconds']:6g} ms: "
              f"pZ={100 * row['p_z_saved_cycles_convention']:.6f}%, "
              f"{row['expected_target_z_faults_per_1000_shots']:.4f} faults/1000")
    print(f"Linear/quadratic crossover: {data['linear_quadratic_small_time_crossover_seconds'] * 1000:.2f} ms")
    print(out)
    return data
