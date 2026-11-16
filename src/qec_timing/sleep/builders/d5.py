"""d=5 X-memory, fixed one-second requested sleep; pinned native QIR blocks.

Ported from SG_final_round/src/fixed_sleep_d5.py, plus the build code of the scripts now
archived in results/sleep/submission_scripts/:

    fixed()                  fixed_sleep_d5.py                  -> d5_fixed_sleep_9fb82150bc37143a
    half_second()            submit_d5_half_second_500.py       -> d5_fixed_sleep_half_second_n3_4_5_6
    zero_sleep_controls()    d5_zero_sleep_control.py,          -> d5_zero_sleep_n2,
                             d5_h2_2_zero_sleep_control.py,        d5_h2_2_zero_sleep_n2,
                             d5_h2_2_zero_sleep_n3_control.py      d5_h2_2_zero_sleep_n3
                             (one parametrised builder; they differed only in N, shots,
                             platform, options and estimated_hqc)
    zero_sleep_n3_skip5()    d5_h2_2_zero_sleep_n3_skip5.py     -> d5_h2_2_zero_sleep_n3_skip5
    skip5_t1()               submit_d5_h2_2_t1_skip5_*.py       -> d5_h2_2_t1_skip5_{n3_n4,n2_n6,n10}

The skip-5 programs use `qec_timing.sleep.mapping`. Original and skip-5 mappings are
separate experiments; never pool them (/AGENTS.md). Submission plans and provider calls live
in `qec_timing.sleep.jobs`. Builds no longer rewrite config/sleep/*.json (writing rule).
"""
from __future__ import annotations

import functools
import hashlib
import json
import math
import re

from .. import mapping, paths
from ..jobs import OPTIONS
from ..qir import BASELINE_D5_SHA256 as SOURCE_SHA256, call_counts, operand, remap_results, rename_locals, roundtrip, zero_sleeps
from . import Build

SOURCE = paths.BASELINE_D5
ROUNDS = [2,3,4,5,6,7,8,9,10,15,20]
CONFIG = dict(experiment='d5_X_fixed_total_sleep_1s',distance=5,basis='X',
    rounds=ROUNDS,shots_per_setting={str(n):2000 if 6<=n<=10 else 500 for n in ROUNDS},
    total_requested_sleep_seconds=1.0,sleep_units='seconds as agreed',
    extraction_duration_neglected=True,parallel_sleep_verified=False,
    platform='nexus:H2-1E',as_entity='q_sq',options=OPTIONS,artificial_faults=False,
    baseline_sha256=SOURCE_SHA256)
CONFIG_FILE = 'd5_fixed_sleep_13000.json'


@functools.lru_cache(maxsize=None)
def qir(n, include_sleep=True):
    assert n >= 2
    src=paths.read_text(SOURCE)
    assert hashlib.sha256(src.encode()).hexdigest()==SOURCE_SHA256
    boundaries=list(re.finditer(r'^cond_exit_[^\n]+\n  tail call void @__quantum__qis__reset__body[^\n]+\n',src,re.M))
    assert len(boundaries)==60
    start=src.index('  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 25')
    first=src[start:boundaries[11].end()]
    last=src[boundaries[47].end():boundaries[59].end()]
    tags=[f's{r}_{c}' for r in range(n) for c in range(12)]+[f'm{q}' for q in range(25)]
    globals_=''.join(f'@tag_{i} = private constant [{len(t)+1} x i8] c"{t}\\00"\n' for i,t in enumerate(tags))
    prefix=src[src.index('define dso_local'):start]
    barrier='  call void @__quantum__qis__barrier26__body('+', '.join(operand(q) for q in range(26))+')\n'
    sleep=barrier+''.join(f'  call void @__quantum__qis__sleep__body({operand(q)}, double {1/(n-1):.17e})\n' for q in range(25))+barrier if include_sleep else ''
    body=prefix
    for r in range(n-1):
        body+=remap_results(rename_locals(first,f'r{r}_'),12*r)+sleep
    body+=remap_results(rename_locals(last,f'r{n-1}_'),12*(n-5))
    for r in range(n):
        for c in range(12):
            i=12*r+c;v=c+1 if r<n-1 else c+49;length=len(tags[i])+1
            body+=f'  tail call void @__quantum__rt__bool_record_output(i1 %r{r}_v{v}, i8* getelementptr inbounds ([{length} x i8], [{length} x i8]* @tag_{i}, i64 0, i64 0))\n'
    final_start=src.index('  tail call void @__quantum__qis__mz__body(%Qubit* null',boundaries[59].end())
    final_end=src.index('\n}\n',final_start)
    final=remap_results(rename_locals(src[final_start:final_end],'final_'),12*(n-5))
    final=re.sub(r'\]([^\n]*?)@(\d+)',lambda m:']'+m[1]+'@tag_'+str(int(m[2])+12*(n-5)),final)
    body+=final+'\n}\n'
    tail=src[src.index('declare i64 @___get_current_shot()'):]
    tail=tail.replace('"required_num_results"="85"',f'"required_num_results"="{12*n+25}"')
    tail+='\ndeclare void @__quantum__qis__sleep__body(%Qubit*, double)\n'
    tail+='declare void @__quantum__qis__barrier26__body('+', '.join(['%Qubit*']*26)+')\n'
    return src[:src.index('@0 =')]+globals_+body+tail


PLAN=[]
for n in ROUNDS:
    shots=CONFIG['shots_per_setting'][str(n)]
    count=math.ceil(shots*(800*n+355)/5000/995)
    parts=[shots//count+(i<shots%count) for i in range(count)]
    PLAN.append(dict(name=f'n{n}',rounds=n,parts=parts,shots=shots,delta_t_seconds=1/(n-1),
        estimated_hqc=[5*count+shots*(696*n+305)/5000,5*count+shots*(800*n+355)/5000]))
del n, shots, count, parts


def fixed() -> Build:
    texts={f'n{n}':qir(n) for n in ROUNDS}
    name='d5_fixed_sleep_'+hashlib.sha256((json.dumps(CONFIG,sort_keys=True)+''.join(texts.values())).encode()).hexdigest()[:16]
    return Build(name, texts, config=CONFIG, plan=PLAN, extra={'rounds': ROUNDS, 'config_file': CONFIG_FILE})


def materialize(clang: str = 'clang'):
    """The original `build`: verify the existing build folder, or write a new one."""
    build = fixed()
    BUILD = build.folder
    if (BUILD/'manifest.json').exists():
        manifest=json.loads(paths.read_text(BUILD/'manifest.json'))
        for name,digest in manifest['bitcode_sha256'].items():
            assert hashlib.sha256((BUILD/(name+'.bc')).read_bytes()).hexdigest()==digest
        return BUILD
    hashes={}
    for name,text in build.texts.items():
        ll=paths.write_text(BUILD/(name+'.ll'), text);bc=ll.with_suffix('.bc')
        assert call_counts(roundtrip(ll, clang))==call_counts(text)
        hashes[name]=hashlib.sha256(bc.read_bytes()).hexdigest()
    manifest=dict(CONFIG,plan=PLAN,bitcode_sha256=hashes,source=str(SOURCE),
        estimated_hqc_total=[sum(p['estimated_hqc'][i] for p in PLAN) for i in range(2)],
        estimate_assumptions='Excludes/includes virtual Rz; no extra sleep/barrier charge; 5 HQC per split job',
        analysis_policy='Collect raw results; no automatic decoder retuning or further submissions')
    paths.write_text(BUILD/'manifest.json', json.dumps(manifest,indent=2)+'\n')
    return BUILD


# ----------------------------------------------------------------------------- half-second sweep (H2-1E)

HALF_SECOND_ROUNDS=[3,4,5,6]
HALF_SECOND_PLATFORM='nexus:H2-1E'
HALF_SECOND_ESTIMATE=sum(5+500*(696*n+305)/5000 for n in HALF_SECOND_ROUNDS)


def half_second_qir(n):
    original=qir(n)
    pattern=r'(@__quantum__qis__sleep__body\([^\n]*, double )([^\n)]+)(\))'
    text,count=re.subn(pattern,lambda m:m[1]+f'{0.5/(n-1):.17e}'+m[3],original)
    assert count==25*(n-1)
    assert re.sub(pattern,r'\1DURATION\3',text)==re.sub(pattern,r'\1DURATION\3',original)
    durations=[float(m[1]) for m in re.finditer(r'@__quantum__qis__sleep__body\([^\n]*, double ([^\n)]+)\)',text)]
    assert len(durations)==25*(n-1) and all(abs(v*(n-1)-0.5)<1e-12 for v in durations)
    return text


def half_second() -> Build:
    """Authorized d=5 H2-1E sweep: T_sleep=0.5 seconds; N=3,4,5,6, 500 shots each."""
    return Build('d5_fixed_sleep_half_second_n3_4_5_6', {f'n{n}': half_second_qir(n) for n in HALF_SECOND_ROUNDS},
                 hashed=False, extra={'rounds': HALF_SECOND_ROUNDS, 'run': 'd5_fixed_sleep_half_second_h2_1e_500_n3_4_5_6',
                                      'config_file': 'd5_fixed_sleep_half_second_2000.json'})


def materialize_half_second(clang: str = 'clang'):
    """The original `build` of submit_d5_half_second_500.py: verify, or write a new folder."""
    BUILD = half_second().folder
    if (BUILD/'manifest.json').exists():
        manifest=json.loads(paths.read_text(BUILD/'manifest.json'))
        for n in HALF_SECOND_ROUNDS:
            assert paths.read_text(BUILD/f'n{n}.ll')==half_second_qir(n)
            assert hashlib.sha256((BUILD/f'n{n}.bc').read_bytes()).hexdigest()==manifest['bitcode_sha256'][f'n{n}']
        return BUILD
    hashes={}
    for n in HALF_SECOND_ROUNDS:
        text=half_second_qir(n);ll=paths.write_text(BUILD/f'n{n}.ll', text);bc=ll.with_suffix('.bc')
        rt=roundtrip(ll, clang)
        assert call_counts(rt)==call_counts(text)
        assert f'"required_num_results"="{12*n+25}"' in rt
        hashes[f'n{n}']=hashlib.sha256(bc.read_bytes()).hexdigest()
    manifest=dict(distance=5,basis='X',rounds=HALF_SECOND_ROUNDS,shots_per_setting=500,total_requested_sleep_seconds=0.5,platform=HALF_SECOND_PLATFORM,options=CONFIG['options'],as_entity=CONFIG['as_entity'],bitcode_sha256=hashes,estimated_hqc=HALF_SECOND_ESTIMATE,local_validation='Only sleep durations changed; all four LLVM assembly/roundtrip checks passed',parallel_sleep_verified=False,extraction_duration_neglected=True)
    paths.write_text(BUILD/'manifest.json', json.dumps(manifest,indent=2)+'\n')
    return BUILD


# ----------------------------------------------------------------------------- zero-sleep controls

H2_2_OPTIONS = {"no_opt": True}
# Folder -> what differed between the three original scripts. All else is shared.
ZERO_SLEEP = {
    'd5_zero_sleep_n2': dict(rounds=2, shots=1000, platform='nexus:H2-1E', options=OPTIONS,
                             estimated_hqc=344.4, run='d5_zero_sleep_n2_1000_20261106'),
    'd5_h2_2_zero_sleep_n2': dict(rounds=2, shots=500, platform='nexus:H2-2', options=H2_2_OPTIONS,
                                  estimated_hqc=174.7, run='d5_h2_2_zero_sleep_n2_500_20261113',
                                  # d5_h2_2_zero_sleep_control_repeat_250.py reran this program.
                                  repeat_runs=['d5_h2_2_zero_sleep_n2_250_repeat_20261113']),
    'd5_h2_2_zero_sleep_n3': dict(rounds=3, shots=250, platform='nexus:H2-2', options=H2_2_OPTIONS,
                                  estimated_hqc=124.65, run='d5_h2_2_zero_sleep_n3_250_20261114'),
}


def zero_sleep(folder: str) -> Build:
    """Explicit-zero d=5 control: the T=1 N-round program with every sleep set to 0."""
    spec = ZERO_SLEEP[folder]
    n = spec['rounds']
    return Build(folder, {f'n{n}': zero_sleeps(qir(n), 25*(n-1))}, hashed=False, extra=dict(spec))


def zero_sleep_controls() -> dict:
    return {folder: zero_sleep(folder) for folder in ZERO_SLEEP}


def materialize_zero_sleep(folder: str, clang: str = 'clang'):
    """The shared `build` of the three d=5 zero-sleep control scripts: verify, or write new."""
    build = zero_sleep(folder)
    spec = build.extra
    n = spec['rounds']
    (name, text), = build.texts.items()
    BUILD = build.folder
    program = BUILD / f'{name}.bc'
    ll = program.with_suffix('.ll')
    if program.exists():
        manifest = json.loads(paths.read_text(BUILD / 'manifest.json'))
        assert paths.read_text(ll) == text
        assert hashlib.sha256(program.read_bytes()).hexdigest() == manifest['bitcode_sha256'][name]
        return program
    paths.write_text(ll, text)
    rt = roundtrip(ll, clang)
    assert call_counts(rt) == call_counts(text)
    sleep_calls = [line for line in rt.splitlines()
                   if 'call void @__quantum__qis__sleep__body' in line]
    assert len(sleep_calls) == 25*(n-1) and all('double 0.000000e+00' in line for line in sleep_calls)
    manifest = dict(distance=5, basis='X', rounds=[n], total_requested_sleep_seconds=0.0,
                    explicit_sleep_calls=25*(n-1), delta_t_seconds=0.0, shots=spec['shots'],
                    platform=spec['platform'], as_entity='q_sq', options=spec['options'],
                    source=str(SOURCE), source_sha256=SOURCE_SHA256,
                    bitcode_sha256={name: hashlib.sha256(program.read_bytes()).hexdigest()},
                    estimated_hqc=spec['estimated_hqc'])
    paths.write_text(BUILD / 'manifest.json', json.dumps(manifest, indent=2) + '\n')
    return program


# ----------------------------------------------------------------------------- skip-index-5 programs (H2-2)

ZERO_SLEEP_N3_SOURCE = paths.PROGRAMS / 'd5_h2_2_zero_sleep_n3' / 'n3.ll'


def zero_sleep_n3_skip5() -> Build:
    """The committed zero-sleep N=3 program remapped to skip index 5 (250 H2-2 shots)."""
    text = mapping.skip5(paths.read_text(ZERO_SLEEP_N3_SOURCE))
    return Build('d5_h2_2_zero_sleep_n3_skip5', {'n3': text}, hashed=False,
                 extra={'rounds': [3], 'run': 'd5_h2_2_zero_sleep_n3_skip5_250_20261114', 'options': H2_2_OPTIONS})


def materialize_zero_sleep_n3_skip5(clang: str = 'clang'):
    """The original `build` of d5_h2_2_zero_sleep_n3_skip5.py: verify, or write a new folder."""
    build = zero_sleep_n3_skip5()
    source, text = ZERO_SLEEP_N3_SOURCE, build.texts['n3']
    BUILD = build.folder
    program = BUILD / 'n3.bc'
    ll = program.with_suffix('.ll')
    if program.exists():
        manifest = json.loads(paths.read_text(BUILD/'manifest.json'))
        assert paths.read_text(ll) == text
        assert hashlib.sha256(program.read_bytes()).hexdigest() == manifest['bitcode_sha256']['n3']
        return program
    paths.write_text(ll, text)
    assert call_counts(roundtrip(ll, clang)) == call_counts(text)
    manifest = dict(distance=5,basis='X',rounds=[3],shots=250,platform='nexus:H2-2',options=H2_2_OPTIONS,
                    total_requested_sleep_seconds=0,delta_t_seconds=0,explicit_sleep_calls=50,
                    data_qubit_indices=list(range(5))+list(range(6,26)),ancilla_qubit_index=26,
                    unused_qubit_index=5,required_num_qubits=27,output_labels='Original code-position labels preserved',
                    source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                    bitcode_sha256={'n3':hashlib.sha256(program.read_bytes()).hexdigest()},
                    estimated_hqc=124.90,validation='Exact inverse remapping reproduces audited original QIR; LLVM assembly and roundtrip gate counts pass')
    paths.write_text(BUILD/'manifest.json', json.dumps(manifest,indent=2)+'\n')
    return program


# Folder -> rounds of the T=1 s skip-5 batches (submission details: jobs.H2_2_D5_BATCHES).
SKIP5_T1 = {'d5_h2_2_t1_skip5_n3_n4': [3, 4], 'd5_h2_2_t1_skip5_n2_n6': [2, 6], 'd5_h2_2_t1_skip5_n10': [10]}


def mapped_qir(n):
    return mapping.skip5(qir(n))


def skip5_t1(folder: str | None = None):
    """The T=1 s skip-5 build `folder`, or {folder: Build} for all three."""
    if folder is None:
        return {f: skip5_t1(f) for f in SKIP5_T1}
    return Build(folder, {f'n{n}': mapped_qir(n) for n in SKIP5_T1[folder]}, hashed=False,
                 extra={'rounds': SKIP5_T1[folder]})


def skip5_t1_manifest(hashes: dict) -> dict:
    return dict(distance=5,basis='X',artificial_faults=False,total_requested_sleep_seconds=1,bitcode_sha256=hashes,data_indices=list(range(5))+list(range(6,26)),ancilla_index=26,unused_index=5,output_labels='Original code positions preserved')


def materialize_skip5_t1(folder: str, clang: str = 'clang'):
    """The skip-5 scripts' `build`. For an existing folder it only verifies: the original
    rewrote manifest.json every time; here an existing manifest must already equal it."""
    build = skip5_t1(folder)
    BUILD = build.folder
    hashes={}
    for n in build.extra['rounds']:
        text=build.texts[f'n{n}'];ll=BUILD/f'n{n}.ll';bc=ll.with_suffix('.bc');rt=BUILD/f'n{n}.roundtrip.ll'
        if bc.exists():
            manifest=json.loads(paths.read_text(BUILD/'manifest.json'))
            assert paths.read_text(ll)==text and hashlib.sha256(bc.read_bytes()).hexdigest()==manifest['bitcode_sha256'][f'n{n}']
            assert call_counts(paths.read_text(rt))==call_counts(text)
        else:
            paths.write_text(ll, text)
            assert call_counts(roundtrip(ll, clang))==call_counts(text)
        hashes[f'n{n}']=hashlib.sha256(bc.read_bytes()).hexdigest()
    manifest = skip5_t1_manifest(hashes)
    path = BUILD/'manifest.json'
    if path.exists():
        if json.loads(paths.read_text(path)) != manifest:
            raise RuntimeError(f'{path} differs from the manifest this build would write')
    else:
        paths.write_json(path, manifest)
    return BUILD
