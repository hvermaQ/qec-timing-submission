"""Native one-qubit X-memory QIR: the 200-shot pilot and the explicit-sleep 1000-shot sweep.

Ported from SG_final_round/src/single_qubit_pilot.py (`qir`, `build`; its run/fetch code is
archived in results/sleep/submission_scripts/) and single_qubit_sweep.py (`build`). The
sweep's check/execute/fetch live in `qec_timing.sleep.jobs`; its `analyze` moves to the
analysis modules (stage 3 part B).

Pilot folder = 'single_qubit_' + sha256(QIR texts)[:16]; sweep folder =
'single_qubit_sweep_' + sha256(CONFIG + QIR texts)[:16].
"""
from __future__ import annotations

import hashlib
import json

from .. import paths
from ..jobs import OPTIONS
from ..qir import roundtrip
from . import Build

# ----------------------------------------------------------------------------- pilot

PILOT_VARIANTS = {'no_sleep': None, 'sleep_zero': 0.0, 'sleep_0p5': 0.5}


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


def pilot() -> Build:
    identity = hashlib.sha256(''.join(qir(t) for t in PILOT_VARIANTS.values()).encode()).hexdigest()[:16]
    return Build('single_qubit_' + identity, {name: qir(t) for name, t in PILOT_VARIANTS.items()},
                 extra={'variants': PILOT_VARIANTS})


def materialize_pilot(clang: str = 'clang'):
    """The pilot's `build`. Unlike the original it refuses to overwrite committed files (S7)."""
    build = pilot()
    out = build.folder
    for name, duration in PILOT_VARIANTS.items():
        ll = paths.write_text(out / (name + '.ll'), qir(duration))
        rt = roundtrip(ll, clang)
        assert rt.count('call void @__quantum__qis__phasedx__body') == 2
        assert rt.count('call void @__quantum__qis__sleep__body') == int(duration is not None)
        meta = dict(experiment='standalone_X_memory',n_qubits=1,virtual_qubit=0,
                    physical_ion_selection='backend assigned',shots=200,duration_raw=duration,
                    duration_unit='unverified',p_inject=0,expected_noiseless_bit=0,
                    llvm_assembly='passed',sha256=hashlib.sha256(ll.with_suffix('.bc').read_bytes()).hexdigest())
        paths.write_text(ll.with_suffix('.json'), json.dumps(meta,indent=2)+'\n')
    return out


# ----------------------------------------------------------------------------- sweep

VALUES = [0.0, 0.1, 0.5, 0.75, 1.0]
VARIANTS = {'sleep_' + str(t).replace('.', 'p'): t for t in VALUES}
SHOTS = 1000
CONFIG = dict(experiment='single_qubit_explicit_sleep_1000',durations_raw=VALUES,
              duration_unit='unverified',shots=SHOTS,platform='nexus:H2-1E',as_entity='q_sq',options=OPTIONS)


def sweep() -> Build:
    name = 'single_qubit_sweep_' + hashlib.sha256(
        (json.dumps(CONFIG,sort_keys=True)+''.join(qir(t) for t in VALUES)).encode()).hexdigest()[:16]
    return Build(name, {n: qir(t) for n, t in VARIANTS.items()}, config=CONFIG, extra={'variants': VARIANTS})


def materialize_sweep(clang: str = 'clang'):
    """The sweep's `build`: verify an existing build, or write a new one. Never rewrites config/sleep."""
    build = sweep()
    BUILD = build.folder
    if (BUILD/'manifest.json').exists():
        manifest=json.loads(paths.read_text(BUILD/'manifest.json'))
        for name, digest in manifest['bitcode_sha256'].items():
            assert hashlib.sha256((BUILD/(name+'.bc')).read_bytes()).hexdigest()==digest
        return BUILD
    hashes={}
    for name,t in VARIANTS.items():
        ll=paths.write_text(BUILD/(name+'.ll'), qir(t))
        body=roundtrip(ll, clang)
        assert body.count('call void @__quantum__qis__sleep__body')==1
        assert body.count('call void @__quantum__qis__phasedx__body')==2
        assert body.count('call void @__quantum__qis__mz__body')==1
        assert '"required_num_qubits"="1"' in body
        hashes[name]=hashlib.sha256(ll.with_suffix('.bc').read_bytes()).hexdigest()
    paths.write_text(BUILD/'manifest.json', json.dumps(dict(CONFIG,bitcode_sha256=hashes,local_validation='all 5 LLVM assembly and roundtrip checks passed'),indent=2)+'\n')
    return BUILD
