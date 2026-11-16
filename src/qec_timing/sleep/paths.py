"""Every path the sleep package uses, the recorded-path resolver, and the write helpers.

Writing rule (MIGRATION.md §2): the package never overwrites an existing file under
PROGRAMS, RUNS or CONFIG. New experiments may add new files there. Regenerated per-run
analyses go to STORE (gitignored) instead. Every file is written with newline='\\n' and
encoding='utf-8', so output is byte-identical on Windows and macOS/Linux.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path, PurePosixPath
from typing import Any

REPO = Path(__file__).resolve().parents[3]

CONFIG = REPO / 'config' / 'sleep'
DECODERS = CONFIG / 'decoders'
RESULTS = REPO / 'results' / 'sleep'
PROGRAMS = RESULTS / 'programs'
RUNS = RESULTS / 'runs'
FIGURES = RESULTS / 'figures'
ENV = RESULTS / 'env'
HARDWARE_BUDGET = RESULTS / 'hardware_budget'
ARCHIVE = RESULTS / 'submission_scripts'
STORE = REPO / 'store' / 'sleep'

# Pinned main-repo baselines the builders patch (hash-checked by the builders).
BASELINE_D3 = REPO / 'results' / 'hardware' / 'programs' / 'd3_X_r2_p0'   # stem: .ll .bc .json
BASELINE_D5 = REPO / 'results' / 'hardware' / 'programs' / 'd5_X_r5_p0.ll'

# The original probe builder, kept byte for byte: probe folder names hash its bytes (S1).
PROBE_BUILDER = ARCHIVE / 'build_sleep_probe.py'

PROTECTED = (PROGRAMS, RUNS, CONFIG)


# --------------------------------------------------------------------------- recorded paths

_DECODER_JSONS = {'h2_2_decoder.json', 'h2_2_d5_decoder.json', 'h2_2_d5_skip5_decoder.json'}
# outputs/d3_d5_g1_stacked_fits.pdf was a byte-identical duplicate of the results/ copy.
_DROPPED_DUPLICATES = {'d3_d5_g1_stacked_fits.pdf': RESULTS / 'd3_d5_g1_stacked_fits.pdf'}
_SG = re.compile(r'(?:^|/)SG_final_round/(programs|runs|results|outputs|configs|env)(?:/(.*))?$')
_SG_SRC = re.compile(r'(?:^|/)SG_final_round/src/([\w.]+\.py)$')
_SG_OTHER = re.compile(r'(?:^|/)SG_final_round(?:/|$)')
_PACKAGE = REPO / 'src' / 'qec_timing' / 'sleep'
# SG_final_round/src scripts whose code moved into this package (scripts moved unchanged are
# found in ARCHIVE first). redecode_d3_sleep_dependent.py is recorded (by redecode_d5) as the
# source of the legacy H2-1E decoder policy, which now lives in decoder.py.
SOURCE_MOVES = {
    'redecode_d3_sleep_dependent.py': _PACKAGE / 'decoder.py',
    'h2_2_decoder.py': _PACKAGE / 'decoder.py',
    'single_qubit_sweep.py': _PACKAGE / 'builders' / 'single_qubit.py',
    'd3_sleep_sweep.py': _PACKAGE / 'builders' / 'd3_sweep.py',
    'fixed_sleep_d3.py': _PACKAGE / 'builders' / 'd3.py',
    'fixed_sleep_d5.py': _PACKAGE / 'builders' / 'd5.py',
    'analyze_d3_sleep_sweep.py': _PACKAGE / 'analysis' / 'emulator_d3.py',
    'analyze_fixed_sleep_d3.py': _PACKAGE / 'analysis' / 'emulator_d3.py',
    'analyze_fixed_sleep_refinement.py': _PACKAGE / 'analysis' / 'emulator_d3.py',
    'analyze_fixed_sleep_all.py': _PACKAGE / 'analysis' / 'emulator_d3.py',
    'characterize_h2_2e_sleep.py': _PACKAGE / 'analysis' / 'emulator_d3.py',
    'analyze_d5_sleep_results.py': _PACKAGE / 'analysis' / 'emulator_d5.py',
    'redecode_d5_sleep_dependent.py': _PACKAGE / 'analysis' / 'emulator_d5.py',
    'analyze_h2_2_hardware_pooled.py': _PACKAGE / 'analysis' / 'h2_2_d3.py',
    'combine_h2_2_updated_decoder.py': _PACKAGE / 'analysis' / 'h2_2_d3.py',
    'test_h2_2_decoder_sensitivity.py': _PACKAGE / 'analysis' / 'h2_2_d3.py',
    'analyze_d5_h2_2_t1_20261113.py': _PACKAGE / 'analysis' / 'h2_2_d5.py',
    'analyze_d5_h2_2_t1_skip5.py': _PACKAGE / 'analysis' / 'h2_2_d5.py',
    'd5_h2_2_p_read_sensitivity.py': _PACKAGE / 'analysis' / 'h2_2_d5.py',
    'analyze_single_qubit_pilot.py': _PACKAGE / 'analysis' / 'controls.py',
    'analyze_d5_h2_2_zero_sleep_control.py': _PACKAGE / 'analysis' / 'controls.py',
    'analyze_d5_h2_2_zero_sleep_n3.py': _PACKAGE / 'analysis' / 'controls.py',
    'analyze_d5_h2_2_zero_sleep_n3_skip5.py': _PACKAGE / 'analysis' / 'controls.py',
    'audit_native_memory.py': _PACKAGE / 'analysis' / 'audit.py',
    'review_duration_scales.py': _PACKAGE / 'analysis' / 'audit.py',
    **{name: _PACKAGE / 'fits.py' for name in [
        'fit_d3_calibrated_g.py', 'fit_d3_free_idle.py', 'fit_d5_free_idle.py', 'fit_d5_sleep_dependent.py',
        'fit_d5_transferred_idle.py', 'fit_h2_2_d5_skip5_g1.py', 'fit_h2_2_free_g.py', 'fit_h2_2_g1.py',
        'fit_shared_g_calibrated.py', 'fit_shared_g_no_boundary.py']},
    **{name: _PACKAGE / 'plots.py' for name in [
        'plot_d5_h2_2_raw_qubit_errors.py', 'plot_d5_sleep_dependent.py', 'plot_d5_sleep_results.py',
        'plot_free_idle_fits.py', 'plot_g1_stacked.py', 'plot_h2_2_d3_d5_skip5_g1.py', 'plot_h2_2_g1_pdf.py']},
    **{name: _PACKAGE / 'reports.py' for name in [
        'report_d3_all_shots.py', 'create_combined_sleep_pdf.py', 'create_h2_2e_summary_pdf.py',
        'create_sleep_explanation_pdf.py']},
}
_OUTPUT = re.compile(r'(?:^|/)output/(hardware_budget|pdf)(?:/(.*))?$')
# The machine the data were taken on; paths under it that did not move map to REPO.
_RECORDED_REPO = '/Users/harshank_s/qec-timing-submission/'


def _join(base: Path, rest: str | None) -> Path:
    return base.joinpath(*PurePosixPath(rest).parts) if rest else base


def resolve_recorded(path: str | os.PathLike) -> Path:
    """Map a path recorded in a historical JSON to where that file lives now.

    Handles absolute (/Users/harshank_s/...) and relative (SG_final_round/...) forms:
      SG_final_round/programs/X  -> results/sleep/programs/X
      SG_final_round/runs/X      -> results/sleep/runs/X
      SG_final_round/results/X   -> results/sleep/X          (results/figures -> results/sleep/figures)
      SG_final_round/outputs/X   -> results/sleep/figures/X  (the dropped duplicate -> its kept copy)
      SG_final_round/configs/X   -> config/sleep/X           (decoder policies -> config/sleep/decoders/X)
      SG_final_round/env/X       -> results/sleep/env/X
      output/hardware_budget/X   -> results/sleep/hardware_budget/X
      output/pdf/X               -> results/sleep/figures/X
      SG_final_round/src/X.py    -> results/sleep/submission_scripts/X.py if archived there,
                                    else the package module that now holds its code (SOURCE_MOVES)
    Other paths under the recorded repo root (the pinned results/hardware baselines) map to
    the same place under REPO. Any other path is returned unchanged. A recorded path into a
    part of SG_final_round that has no new location (e.g. src/) raises ValueError.
    The JSON files themselves are never edited.
    """
    text = os.fspath(path).replace('\\', '/')
    match = _SG.search(text)
    if match:
        kind, rest = match[1], match[2]
        if kind == 'programs':
            return _join(PROGRAMS, rest)
        if kind == 'runs':
            return _join(RUNS, rest)
        if kind == 'results':
            return _join(RESULTS, rest)
        if kind == 'env':
            return _join(ENV, rest)
        if kind == 'outputs':
            if rest in _DROPPED_DUPLICATES:
                return _DROPPED_DUPLICATES[rest]
            return _join(FIGURES, rest)
        if rest in _DECODER_JSONS:
            return DECODERS / rest
        return _join(CONFIG, rest)
    match = _SG_SRC.search(text)
    if match:
        if (ARCHIVE / match[1]).exists():
            return ARCHIVE / match[1]
        if match[1] in SOURCE_MOVES:
            return SOURCE_MOVES[match[1]]
    if _SG_OTHER.search(text):
        raise ValueError(f'No new location for recorded path {path!r}')
    match = _OUTPUT.search(text)
    if match:
        return _join(HARDWARE_BUDGET if match[1] == 'hardware_budget' else FIGURES, match[2])
    if text.startswith(_RECORDED_REPO):
        return _join(REPO, text[len(_RECORDED_REPO):])
    return Path(path)


# --------------------------------------------------------------------------- writing

def protected_root(path: str | os.PathLike) -> Path | None:
    """The protected root (PROGRAMS, RUNS or CONFIG) that contains `path`, if any."""
    resolved = Path(path).resolve()
    for root in PROTECTED:
        if resolved.is_relative_to(root.resolve()):
            return root
    return None


def ensure_writable(path: str | os.PathLike) -> None:
    """Raise FileExistsError if `path` exists under PROGRAMS, RUNS or CONFIG."""
    path = Path(path)
    if path.exists() and protected_root(path) is not None:
        raise FileExistsError(
            f'Refusing to overwrite {path}: existing files under results/sleep/programs, '
            'results/sleep/runs and config/sleep are never rewritten (write to STORE instead)')


def write_text(path: str | os.PathLike, text: str) -> Path:
    """Write text with LF line endings and UTF-8, refusing to overwrite protected files."""
    path = Path(path)
    ensure_writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', newline='\n', encoding='utf-8') as handle:
        handle.write(text)
    return path


def write_bytes(path: str | os.PathLike, data: bytes) -> Path:
    """Write bytes, refusing to overwrite protected files."""
    path = Path(path)
    ensure_writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return path


def dumps(data: Any) -> str:
    """JSON text in the format the original scripts wrote: indent=2 plus a final newline."""
    return json.dumps(data, indent=2, default=str) + '\n'


def write_json(path: str | os.PathLike, data: Any) -> Path:
    """`write_text(path, dumps(data))`."""
    return write_text(path, dumps(data))


def update_job_record(path: str | os.PathLike, data: dict) -> Path:
    """Rewrite a provider job record (`job.json` under RUNS) that is still in flight.

    The only sanctioned in-place update under a protected root, used by `jobs.fetch` and
    `jobs.status` for jobs submitted by this package. Refuses unless the existing record has
    the same job_id and holds no stored results yet, so completed (measured) records are frozen.
    """
    path = Path(path)
    if path.name != 'job.json' or protected_root(path) != RUNS:
        raise ValueError(f'Not a job record under results/sleep/runs: {path}')
    old = json.loads(path.read_text(encoding='utf-8'))
    if old.get('job_id') != data.get('job_id'):
        raise ValueError(f'job_id changed in {path}')
    if old.get('results'):
        raise FileExistsError(f'Refusing to rewrite completed job record {path}')
    temp = path.with_suffix('.tmp')
    with open(temp, 'w', newline='\n', encoding='utf-8') as handle:
        handle.write(dumps(data))
    temp.replace(path)
    return path


def read_text(path: str | os.PathLike) -> str:
    """Read UTF-8 text (universal newlines, as `Path.read_text` does)."""
    return Path(path).read_text(encoding='utf-8')


def store(path: str | os.PathLike) -> Path:
    """Where a per-run file the original scripts wrote into PROGRAMS or RUNS is written now.

    STORE mirrors the layout under results/sleep/, so `store(RUNS/'x'/'analysis.json')` is
    `store/sleep/runs/x/analysis.json` and the committed copy is the argument itself.
    """
    path = Path(path)
    if protected_root(path) not in (PROGRAMS, RUNS):
        raise ValueError(f'Not under results/sleep/programs or results/sleep/runs: {path}')
    return STORE / path.resolve().relative_to(RESULTS.resolve())


def save_npz(path: str | os.PathLike, **arrays) -> Path:
    """`np.savez_compressed`, refusing to overwrite protected files."""
    import numpy as np
    path = Path(path)
    ensure_writable(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(path, **arrays)
    return path


def figure(name: str) -> Path:
    """FIGURES/name (created if needed): every figure and PDF the package makes goes here."""
    FIGURES.mkdir(parents=True, exist_ok=True)
    return FIGURES / name
