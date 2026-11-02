"""Build native one-qubit X-memory QIR; submit only the authorized 200-shot pilot."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = {'no_sleep': None, 'sleep_zero': 0.0, 'sleep_0p5': 0.5}


def qir(duration):
    # Ry(pi/2) prepares +X; Ry(-pi/2) rotates X measurement to Z.
    sleep = '' if duration is None else f'  call void @__quantum__qis__sleep__body(%Qubit* null, double {duration:.17e})\n'
    declaration = '' if duration is None else 'declare void @__quantum__qis__sleep__body(%Qubit*, double)\n'
    return '''source_filename = "single_qubit_memory"
target triple = "aarch64-unknown-linux-gnu"
%Qubit = type opaque
%Result = type opaque
@label = private constant [3 x i8] c"m0\\00"
define void @main() #0 {
  call void @__quantum__rt__initialize(i8* null)
  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0x3FF921FB54442D18, %Qubit* null)
''' + sleep + '''  call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* null)
  call void @__quantum__qis__mz__body(%Qubit* null, %Result* null)
  %bit = call i1 @__quantum__rt__read_result(%Result* null)
  call void @__quantum__rt__bool_record_output(i1 %bit, i8* getelementptr ([3 x i8], [3 x i8]* @label, i64 0, i64 0))
  ret void
}
declare void @__quantum__rt__initialize(i8*)
declare void @__quantum__qis__phasedx__body(double, double, %Qubit*)
declare void @__quantum__qis__mz__body(%Qubit*, %Result* writeonly) #1
declare i1 @__quantum__rt__read_result(%Result* readonly)
declare void @__quantum__rt__bool_record_output(i1, i8*)
''' + declaration + '''attributes #0 = { "entry_point" "output_labeling_schema" "qir_profiles"="adaptive_profile" "required_num_qubits"="1" "required_num_results"="1" }
attributes #1 = { "irreversible" }
!llvm.module.flags = !{!0, !1, !2, !3}
!0 = !{i32 1, !"qir_major_version", i32 1}
!1 = !{i32 7, !"qir_minor_version", i32 0}
!2 = !{i32 1, !"dynamic_qubit_management", i1 false}
!3 = !{i32 1, !"dynamic_result_management", i1 false}
'''


def build():
    identity = hashlib.sha256(''.join(qir(t) for t in VARIANTS.values()).encode()).hexdigest()[:16]
    out = ROOT / 'programs' / ('single_qubit_' + identity)
    out.mkdir(exist_ok=True)
    for name, duration in VARIANTS.items():
        ll = out / (name + '.ll')
        ll.write_text(qir(duration))
        for args in [ ['-x','ir','-c','-emit-llvm','-O0',str(ll),'-o',str(ll.with_suffix('.bc'))],
                      ['-S','-emit-llvm','-O0',str(ll.with_suffix('.bc')),'-o',str(out/(name+'.roundtrip.ll'))] ]:
            subprocess.run(['clang','-target','aarch64-unknown-linux-gnu'] + args,check=True,capture_output=True)
        roundtrip = (out/(name+'.roundtrip.ll')).read_text()
        assert roundtrip.count('call void @__quantum__qis__phasedx__body') == 2
        assert roundtrip.count('call void @__quantum__qis__sleep__body') == int(duration is not None)
        meta = dict(experiment='standalone_X_memory',n_qubits=1,virtual_qubit=0,
                    physical_ion_selection='backend assigned',shots=200,duration_raw=duration,
                    duration_unit='unverified',p_inject=0,expected_noiseless_bit=0,
                    llvm_assembly='passed',sha256=hashlib.sha256(ll.with_suffix('.bc').read_bytes()).hexdigest())
        ll.with_suffix('.json').write_text(json.dumps(meta,indent=2)+'\n')
    return out


def run(stage):
    from aqora import QPU
    out = build()
    platform = 'nexus:H2-1SC' if stage == 'check' else 'nexus:H2-1E'
    if stage == 'execute':
        for name in VARIANTS:
            check = json.loads((ROOT/'runs'/out.name/'check'/name/'job.json').read_text())
            if check.get('job',{}).get('status') != 'COMPLETED' or any(r.get('error') for r in check.get('results',[])):
                raise RuntimeError(f'Syntax acceptance not established for {name}')
    base = ROOT / 'runs' / out.name / stage
    base.mkdir(parents=True,exist_ok=True)
    for name in VARIANTS:
        dest = base/name
        dest.mkdir(exist_ok=True)
        record = dest/'job.json'
        if record.exists():
            raise RuntimeError(f'Existing job record: {record}; fetch it, do not resubmit')
        request = dict(platform=platform,as_entity='q_sq',shots=1 if stage=='check' else 200,
                       program=str(out/(name+'.bc')),
                       options={'simulator':'stabilizer','noisy_simulation':True,'no_opt':True,
                                'error_params':{'idle_dephasing':True,'transport_dephasing':True}})
        (dest/'request.json').write_text(json.dumps(request,indent=2)+'\n')
        job = QPU(platform=platform,as_entity='q_sq').run((out/(name+'.bc')).read_bytes(),shots=request['shots'],options=request['options'])
        record.write_text(json.dumps(dict(request,job_id=job.job_id),indent=2)+'\n')
        print(name,job.job_id,flush=True)
        try:
            job.wait(timeout=300,poll_interval=10)
            results=job.results(raise_on_item_error=False)
            for result in results:
                (dest/f'result_{result.index}.txt').write_text(result.raw or '')
            data=dict(request,job_id=job.job_id,job=dict(job.refresh()),results=[dict(index=r.index,format=r.serialization_format,error=getattr(r,'error',None)) for r in results])
        except Exception as error:
            data=dict(request,job_id=job.job_id,error=str(error))
        record.write_text(json.dumps(data,indent=2,default=str)+'\n')
        print(json.dumps(data,default=str),flush=True)


def fetch():
    """Resume existing execution jobs; never submit another job."""
    from aqora import QPUJob
    out=build()
    for name in VARIANTS:
        dest=ROOT/'runs'/out.name/'execute'/name
        record=dest/'job.json'
        data=json.loads(record.read_text())
        if data.get('job',{}).get('status')=='COMPLETED' and 'results' in data:
            continue
        job=QPUJob.from_id(data['job_id'])
        try:
            job.wait(timeout=300,poll_interval=10)
            results=job.results(raise_on_item_error=False)
            for result in results:
                (dest/f'result_{result.index}.txt').write_text(result.raw or '')
            data.update(job=dict(job.refresh()),results=[dict(index=r.index,format=r.serialization_format,error=getattr(r,'error',None)) for r in results])
            data.pop('error',None)
        except Exception as error:
            data.update(job=dict(job.refresh()),error=str(error))
        record.write_text(json.dumps(data,indent=2,default=str)+'\n')
        print(json.dumps(data,default=str),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('action',choices=['build','check','execute','fetch'])
    action=parser.parse_args().action
    print(build()) if action=='build' else fetch() if action=='fetch' else run(action)
