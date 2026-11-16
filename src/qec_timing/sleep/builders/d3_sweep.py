"""Two X-check extraction rounds with a candidate all-data wait between them.

Barriers constrain ordering, but do not establish simultaneous sleep scheduling.
Execution was explicitly authorized with overlap still unverified.

Ported from SG_final_round/src/d3_sleep_sweep.py. The module globals that
`configure_five_point()` used to rewrite are now the arguments of `sweep(kind, platform)`:

    sweep('three_point')                    -> d3_sleep_sweep_f219bffeea86811d
    sweep('five_point', 'nexus:H2-1E')      -> d3_sleep_five_point_a2588f7078f6e696
    sweep('five_point', 'nexus:H2-2E')      -> d3_sleep_five_point_h2_2e_67d11d0348065703

check/execute/fetch live in `qec_timing.sleep.jobs`. The build no longer rewrites
config/sleep/*.json (writing rule); `CONFIG_FILES` names the committed copy of each CONFIG.
"""
from __future__ import annotations

import hashlib
import json
import math

from .. import paths
from ..jobs import OPTIONS
from ..qir import BASELINE_D3_SHA256 as SOURCE_SHA256, BOUNDARY, SLEEP, assemble, operand
from . import Build

SOURCE = paths.BASELINE_D3
SHOTS = 1000
THREE_POINT = [0.0, 0.5, 1.0]
FIVE_POINT = [0.0, 0.1, 0.5, 0.75, 1.0]
CONFIG = dict(experiment='d3_X_two_round_all_data_sleep', distance=3,
              extraction_rounds=2, check_sector='X only', data_qubits=list(range(9)),
              ancilla_qubit=9, durations_raw=THREE_POINT, duration_unit='unverified',
              shots=SHOTS, platform='nexus:H2-1E', as_entity='q_sq', options=OPTIONS,
              parallel_sleep_verified=False,
              estimated_hqc_per_job=[114.0, 130.4], estimated_hqc_total=[342.0, 391.2],
              estimate_note='Excludes/includes virtual Rz; assumes no extra wait/barrier charge')
CONFIG_FILES = {('three_point', 'nexus:H2-1E'): 'd3_sleep_sweep_1000.json',
                ('five_point', 'nexus:H2-1E'): 'd3_sleep_five_point_1000.json',
                ('five_point', 'nexus:H2-2E'): 'd3_sleep_five_point_h2_2e_1000.json'}


def qir(duration):
    if not math.isfinite(duration) or duration < 0:
        raise ValueError('Invalid raw duration')
    source = paths.read_text(SOURCE.with_suffix('.ll'))
    if hashlib.sha256(source.encode()).hexdigest() != SOURCE_SHA256 or source.count(BOUNDARY) != 1:
        raise ValueError('Baseline changed; re-inspect extraction boundary')
    barrier = '  call void @__quantum__qis__barrier10__body(' + ', '.join(operand(q) for q in range(10)) + ')\n'
    sleeps = ''.join(f'  call void @{SLEEP}({operand(q)}, double {duration:.17e})\n' for q in range(9))
    declarations = f'declare void @{SLEEP}(%Qubit*, double)\n'
    declarations += 'declare void @__quantum__qis__barrier10__body(' + ', '.join(['%Qubit*'] * 10) + ')\n'
    return source.replace(BOUNDARY, BOUNDARY + barrier + sleeps + barrier, 1).replace(
        'declare i64 @___get_current_shot()', declarations + 'declare i64 @___get_current_shot()', 1)


def sweep(kind: str = 'three_point', platform: str = 'nexus:H2-1E') -> Build:
    """The build for one sweep (was: module globals, optionally after configure_five_point)."""
    if kind == 'three_point':
        if platform != 'nexus:H2-1E':
            raise ValueError('The three-point sweep ran on nexus:H2-1E only')
        values, config, prefix = THREE_POINT, CONFIG, 'd3_sleep_sweep_'
    elif kind == 'five_point':
        if platform not in ('nexus:H2-1E', 'nexus:H2-2E'):
            raise ValueError('Only H2-1E and H2-2E emulator targets are allowed')
        values = FIVE_POINT
        config = dict(CONFIG, experiment='d3_X_two_round_all_data_sleep_five_point', platform=platform,
                      durations_raw=values, estimated_hqc_total=[570.0, 652.0],
                      analysis_policy='Save raw results only; analyze on user request')
        prefix = 'd3_sleep_five_point_' if platform == 'nexus:H2-1E' else 'd3_sleep_five_point_h2_2e_'
    else:
        raise ValueError(f'Unknown sweep {kind!r}')
    variants = {'sleep_' + str(t).replace('.', 'p'): t for t in values}
    name = prefix + hashlib.sha256(
        (json.dumps(config, sort_keys=True) + ''.join(qir(t) for t in values)).encode()).hexdigest()[:16]
    return Build(name, {n: qir(t) for n, t in variants.items()}, config=config,
                 extra={'variants': variants, 'values': values, 'config_file': CONFIG_FILES[kind, platform]})


def materialize(build: Build, clang: str = 'clang'):
    """The original `build`: verify an existing build folder, or write a new one."""
    BUILD = build.folder
    if (BUILD/'manifest.json').exists():
        manifest = json.loads(paths.read_text(BUILD/'manifest.json'))
        for name, digest in manifest['bitcode_sha256'].items():
            if hashlib.sha256((BUILD/(name+'.bc')).read_bytes()).hexdigest() != digest:
                raise RuntimeError('Saved bitcode hash mismatch')
        return BUILD
    hashes = {}
    for name, text in build.texts.items():
        ll = BUILD/(name+'.ll')
        if ll.exists() and paths.read_text(ll) != text:
            raise RuntimeError('Existing program differs')
        if not ll.exists():
            paths.write_text(ll, text)
        assemble(clang, ll)
        hashes[name] = hashlib.sha256(ll.with_suffix('.bc').read_bytes()).hexdigest()
    paths.write_text(BUILD/'manifest.json', json.dumps(dict(build.config, bitcode_sha256=hashes,
        baseline_sha256=SOURCE_SHA256, execution_status='blocked_pending_parallel_sleep_verification'), indent=2)+'\n')
    return BUILD
