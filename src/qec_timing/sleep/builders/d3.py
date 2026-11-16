"""Pinned native QIR extraction blocks, repeated at fixed total requested sleep (d=3).

Ported from SG_final_round/src/fixed_sleep_d3.py, plus the build code of
d3_h2_2_zero_sleep_control.py (the original is archived in results/sleep/submission_scripts/).
The globals that `configure_refinement()` / `configure_resolution()` used to rewrite are now
the argument of `fixed(kind)`:

    fixed('coarse')      -> d3_fixed_sleep_690baca08b24dfd2
    fixed('refinement')  -> d3_fixed_sleep_refinement_3bb6e107a0ff6de3
    fixed('resolution')  -> d3_fixed_sleep_resolution_c2380924e8c69578
    zero_sleep_h2_2()    -> d3_h2_2_zero_sleep_n2 (fixed name)

check/execute/fetch live in `qec_timing.sleep.jobs`. Builds no longer rewrite
config/sleep/*.json (writing rule); `CONFIG_FILES` names the committed copy of each manifest.
"""
from __future__ import annotations

import hashlib
import json
import re

from .. import paths
from ..jobs import OPTIONS
from ..qir import (BASELINE_D3_SHA256 as SOURCE_SHA256, BOUNDARY, call_counts, operand,
                   remap_results, rename_locals, roundtrip, zero_sleeps)
from . import Build

SOURCE = paths.BASELINE_D3

ROUNDS=[2,5,10,20,40]
SHOTS=500
CONFIG=dict(experiment='d3_X_fixed_total_sleep_1s',distance=3,basis='X',rounds=ROUNDS,
    shots_per_setting=SHOTS,total_requested_sleep_seconds=1.0,sleep_units='seconds as agreed',
    extraction_duration_neglected=True,parallel_sleep_verified=False,
    platform='nexus:H2-1E',as_entity='q_sq',options=OPTIONS,artificial_faults=False)
BASE_CONFIG=CONFIG.copy()
CONFIG_FILES={'coarse':'d3_fixed_sleep_500.json','refinement':'d3_fixed_sleep_refinement.json',
              'resolution':'d3_fixed_sleep_resolution.json'}


def qir(n, rounds=ROUNDS):
    if n not in rounds:
        raise ValueError('Unsupported round count')
    src=paths.read_text(SOURCE.with_suffix('.ll'))
    assert hashlib.sha256(src.encode()).hexdigest()==SOURCE_SHA256
    start=src.index('  tail call void @__quantum__qis__phasedx__body(double 0x3FF921FB54442D18, double 0xBFF921FB54442D18, %Qubit* nonnull inttoptr (i64 9')
    first_end=src.index(BOUNDARY)+len(BOUNDARY)
    last_end=src.index('  tail call void @__quantum__rt__bool_record_output')
    # The last round contains final data-H gates fused/moved by the original compiler.
    # Keep this block as the final round; repeat only the non-final round block.
    first=src[start:first_end]
    last=src[first_end:last_end]
    definition=src.index('define dso_local')
    prefix=src[definition:start]
    header=src[:src.index('@0 =')]
    tags=[f's{r}_{c}' for r in range(n) for c in range(4)]+[f'm{q}' for q in range(9)]
    globals_=''.join(f'@tag_{i} = private constant [{len(t)+1} x i8] c"{t}\\00"\n' for i,t in enumerate(tags))
    u=1.0/(n-1)
    barrier='  call void @__quantum__qis__barrier10__body('+', '.join(operand(q) for q in range(10))+')\n'
    sleep=barrier+''.join(f'  call void @__quantum__qis__sleep__body({operand(q)}, double {u:.17e})\n' for q in range(9))+barrier
    body=prefix
    for r in range(n-1):
        body+=remap_results(rename_locals(first,f'r{r}_'),4*r)+sleep
    body+=remap_results(rename_locals(last,f'r{n-1}_'),4*(n-2))
    for r in range(n):
        for c in range(4):
            i=4*r+c
            v=c+1 if r<n-1 else c+5
            length=len(tags[i])+1
            body+=f'  tail call void @__quantum__rt__bool_record_output(i1 %r{r}_v{v}, i8* getelementptr inbounds ([{length} x i8], [{length} x i8]* @tag_{i}, i64 0, i64 0))\n'
    final_start=src.index('  tail call void @__quantum__qis__mz__body(%Qubit* null',last_end)
    final_end=src.index('\n}\n',final_start)
    final=remap_results(rename_locals(src[final_start:final_end],'final_'),4*(n-2))
    final=re.sub(r'\]([^\n]*?)@(\d+)',lambda m:']'+m[1]+'@tag_'+str(int(m[2])+4*(n-2)),final)
    # First @index occurs after a pointer type's closing bracket, so both uses map above.
    body+=final+'\n}\n'
    tail=src[src.index('declare i64 @___get_current_shot()'):]
    tail=tail.replace('"required_num_results"="17"',f'"required_num_results"="{4*n+9}"')
    tail+='\ndeclare void @__quantum__qis__sleep__body(%Qubit*, double)\n'
    tail+='declare void @__quantum__qis__barrier10__body('+', '.join(['%Qubit*']*10)+')\n'
    return header+globals_+body+tail


def fixed(kind: str = 'coarse') -> Build:
    """One fixed-total-sleep batch (was: module globals after configure_refinement/resolution)."""
    if kind == 'coarse':
        rounds, config, prefix = ROUNDS, CONFIG, 'd3_fixed_sleep_'
        plan=[dict(name=f'n{n}',rounds=n,parts=[500] if n<40 else [250,250],delta_t_seconds=1/(n-1),delta_t_exact=f'1/{n-1}') for n in rounds]
    elif kind == 'refinement':
        # Fresh refinement jobs; keep original run IDs and data unchanged.
        rounds=[4,5,6,7,8]
        config=dict(BASE_CONFIG,experiment='d3_X_fixed_total_sleep_1s_refinement',rounds=rounds,
            shots_per_setting={str(n):500 if n==5 else 1000 for n in rounds},
            existing_n5_run='d3_fixed_sleep_690baca08b24dfd2',
            existing_n5_shots=500,planned_combined_shots_per_setting=1000)
        prefix='d3_fixed_sleep_refinement_'
        plan=[dict(name=f'n{n}',rounds=n,parts=[500 if n==5 else 1000],
            delta_t_seconds=1/(n-1),delta_t_exact=f'1/{n-1}') for n in rounds]
    elif kind == 'resolution':
        # Second independent refinement batch with explicitly requested new shots.
        rounds=[3,4,5,6,7,8,10]
        allocation={str(n):500 if n in (3,10) else 1000 for n in rounds}
        config=dict(BASE_CONFIG,experiment='d3_X_fixed_total_sleep_1s_resolution',rounds=rounds,
            shots_per_setting=allocation,shot_allocation_interpretation='additional new shots',
            prior_runs=['d3_fixed_sleep_690baca08b24dfd2','d3_fixed_sleep_refinement_3bb6e107a0ff6de3'])
        prefix='d3_fixed_sleep_resolution_'
        plan=[dict(name=f'n{n}',rounds=n,parts=[allocation[str(n)]],
            delta_t_seconds=1/(n-1),delta_t_exact=f'1/{n-1}') for n in rounds]
    else:
        raise ValueError(f'Unknown batch {kind!r}')
    texts={f'n{n}':qir(n,rounds) for n in rounds}
    name=prefix+hashlib.sha256((json.dumps(config,sort_keys=True)+''.join(texts.values())).encode()).hexdigest()[:16]
    return Build(name, texts, config=config, plan=plan, extra={'rounds': rounds, 'config_file': CONFIG_FILES[kind]})


def materialize(build: Build, clang: str = 'clang'):
    """The original `build`: verify an existing build folder, or write a new one."""
    BUILD = build.folder
    if (BUILD/'manifest.json').exists():
        old=json.loads(paths.read_text(BUILD/'manifest.json'))
        for name in build.texts:
            assert hashlib.sha256((BUILD/(name+'.bc')).read_bytes()).hexdigest()==old['bitcode_sha256'][name]
        return BUILD
    hashes={}
    for name,text in build.texts.items():
        ll=paths.write_text(BUILD/(name+'.ll'), text);bc=ll.with_suffix('.bc')
        assert call_counts(roundtrip(ll, clang))==call_counts(text)
        hashes[name]=hashlib.sha256(bc.read_bytes()).hexdigest()
    manifest=dict(build.config,plan=build.plan,bitcode_sha256=hashes,baseline_sha256=SOURCE_SHA256,
        note='Pinned Guppy native non-final and final round blocks reused directly in QIR')
    paths.write_text(BUILD/'manifest.json', json.dumps(manifest,indent=2)+'\n')
    return BUILD


# ----------------------------------------------------------------------------- d=3 zero-sleep control (H2-2)

ZERO_SLEEP_OPTIONS = {"no_opt": True}


def zero_sleep_h2_2() -> Build:
    """Explicit-zero d=3, two-extraction control, 1000 authorized H2-2 shots."""
    text = zero_sleeps(qir(2), 9)
    return Build('d3_h2_2_zero_sleep_n2', {'n2': text}, hashed=False,
                 extra={'run': 'd3_h2_2_zero_sleep_n2_1000_20261112', 'options': ZERO_SLEEP_OPTIONS})


def materialize_zero_sleep_h2_2(clang: str = 'clang'):
    """The original `build` of d3_h2_2_zero_sleep_control.py: verify, or write a new folder."""
    build = zero_sleep_h2_2()
    text = build.texts['n2']
    BUILD = build.folder
    program = BUILD / 'n2.bc'
    ll = program.with_suffix('.ll')
    if program.exists():
        manifest = json.loads(paths.read_text(BUILD / 'manifest.json'))
        assert paths.read_text(ll) == text
        assert hashlib.sha256(program.read_bytes()).hexdigest() == manifest['bitcode_sha256']['n2']
        return program
    paths.write_text(ll, text)
    rt = roundtrip(ll, clang)
    assert call_counts(rt) == call_counts(text)
    sleep_calls = [line for line in rt.splitlines()
                   if 'call void @__quantum__qis__sleep__body' in line]
    assert len(sleep_calls) == 9 and all('double 0.000000e+00' in line for line in sleep_calls)
    manifest = dict(distance=3, basis='X', rounds=[2], total_requested_sleep_seconds=0.0,
                    explicit_sleep_calls=9, delta_t_seconds=0.0, shots=1000,
                    platform='nexus:H2-2', as_entity='q_sq', options=ZERO_SLEEP_OPTIONS,
                    source=str(SOURCE), source_sha256=SOURCE_SHA256,
                    bitcode_sha256={'n2': hashlib.sha256(program.read_bytes()).hexdigest()},
                    estimated_hqc=114.0)
    paths.write_text(BUILD / 'manifest.json', json.dumps(manifest, indent=2) + '\n')
    return program
