"""Independent ideal Clifford translation of saved native QIR; no hardware calls."""
import re,json,struct,hashlib,subprocess,sys
from pathlib import Path
import numpy as np
import stim
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/circuit_audit'
sys.path.insert(0,str(ROOT.parent/'src'))
from qec_timing.hardware.providers import _register_builtins
from qec_timing.spec import spec_from_json
from qec_timing.codes.base import checks_of
_register_builtins()
X=np.array([[0,1],[1,0]],complex);Y=np.array([[0,-1j],[1j,0]]);Z=np.diag([1,-1])
def num(s):return struct.unpack('>d',bytes.fromhex(s[2:]))[0] if s.startswith('0x') else float(s)
def operands(line,kind):
 if re.search(r'\bptr ',line):
  vals=[int(x or 0) for x in re.findall(r'ptr (?:nonnull )?(?:inttoptr \(i64 (\d+) to ptr\)|null)',line)]
  return vals[-1:] if kind=='Result' else vals[:1] if 'qis__mz__' in line else vals
 return [int(x or 0) for x in re.findall(r'%'+kind+r'\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %'+kind+r'\*\)|null)',line)]
def translate(text,nd):
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
 text=path.read_text();c,tags,sleeps,waits=translate(text,nd)
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
  specpath=ROOT.parent/f'results/hardware/programs/d{int(np.sqrt(nd))}_X_r5_p0.json'
  if not specpath.exists():
   specpath=ROOT.parent/'results/hardware/programs/d3_X_r2_p0.json'
  spec=spec_from_json(json.loads(specpath.read_text())['spec']);checks=checks_of(spec.code,'X')
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
 (OUT/(label+'.stim')).write_text(str(c));print(label,'nonzero/random exact',row['nonzero_or_random_exact_measurements'],'nonzero outputs',bad,flush=True)
 return row

def main():
 rows=[]
 for d,folder in [(5,'d5_h2_2_t1_20261113'),(3,'h2_2_hardware_d3_x_t1_20261111')]:
  paths=list((ROOT/'runs'/folder).glob('execute/n*/job.json')) if d==5 else list((ROOT/'runs'/folder).glob('n*/job.json'))
  for p in sorted(paths):
   j=json.loads(p.read_text());program=Path(j['program']);program=program if program.is_absolute() else ROOT.parent/program
   assert hashlib.sha256(program.read_bytes()).hexdigest()==j['program_sha256']
   ll=OUT/f"d{d}_n{j['rounds']}.ll"
   subprocess.run(['clang','-target','aarch64-unknown-linux-gnu','-S','-emit-llvm','-O0',str(program),'-o',str(ll)],check=True,capture_output=True)
   rows.append(audit(ll,d*d,j['rounds'],f"d{d}_n{j['rounds']}"))
 rows.append(audit(ROOT.parent/'results/hardware/programs/d5_X_r5_p0.ll',25,5,'d5_original_n5'))
 (OUT/'ideal_audit.json').write_text(json.dumps(rows,indent=2)+'\n')
if __name__=='__main__':main()
