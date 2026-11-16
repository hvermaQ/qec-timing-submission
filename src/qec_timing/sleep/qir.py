"""Shared QIR text helpers, moved verbatim from the original builders.

Do not change anything that shapes QIR text: build folder names hash CONFIG + QIR text,
and the regenerated `.ll` must equal the committed `.ll` for every build folder.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

from . import paths

SLEEP = "__quantum__qis__sleep__body"

# Pinned d=3 baseline (results/hardware/programs/d3_X_r2_p0.ll) and its round boundary:
# the join after the fourth syndrome measurement's conditional path, followed by the
# final ancilla reset of round zero. Insertion here executes once regardless of that
# syndrome outcome. (From build_sleep_probe.py.)
BASELINE_D3_SHA256 = "1d76441345a391205fcb9c9898deed404462c26098f58d57a0f0c19385ccd531"
BOUNDARY = (
    "cond_exit_1230:                                   ; preds = %cond_exit_1145, %cond_1230_case_1\n"
    "  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))\n"
)
# Pinned d=5 baseline (results/hardware/programs/d5_X_r5_p0.ll). (From fixed_sleep_d5.py.)
BASELINE_D5_SHA256 = 'fcba655ea3cf9cebd600f9555d703088244459d13128cbe212d70c6a2b694ff0'

CLANG_TARGET = ['-target', 'aarch64-unknown-linux-gnu']


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def folder_hash(config: dict, texts) -> str:
    """The 16-hex build identity: sha256(json.dumps(CONFIG, sort_keys=True) + QIR texts)."""
    return hashlib.sha256((json.dumps(config, sort_keys=True) + ''.join(texts)).encode()).hexdigest()[:16]


def call_counts(ir: str) -> dict:
    return dict(sorted((name, len(re.findall(r"\bcall\b[^\n@]*@" + re.escape(name) + r"\(", ir)))
                       for name in set(re.findall(r"\bcall\b[^\n@]*@([\w.]+)\(", ir))))


# From d3_sleep_sweep.py.
def operand(q):
    return '%Qubit* null' if q == 0 else f'%Qubit* inttoptr (i64 {q} to %Qubit*)'


# From fixed_sleep_d3.py.
def result_operand(i):
    return '%Result* null' if i==0 else f'%Result* nonnull inttoptr (i64 {i} to %Result*)'


def remap_results(text,offset):
    pattern=r'%Result\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %Result\*\)|null)'
    return re.sub(pattern,lambda m:result_operand(int(m[1] or 0)+offset),text)


def rename_locals(text,prefix):
    text=re.sub(r';[^\n]*','',text)
    labels=re.findall(r'^(\w+):',text,re.M)
    for label in labels:
        text=re.sub(r'\b'+re.escape(label)+r'\b',prefix+label,text)
    return re.sub(r'%(\d+)\b',lambda m:'%'+prefix+'v'+m[1],text)


# From d3_h2_2_zero_sleep_control.py / d5_*zero_sleep*_control.py (identical in all four).
ZERO_SLEEP_PATTERN = r'(@__quantum__qis__sleep__body\([^\n]*double )[^)\n]+'


def zero_sleeps(original: str, count: int) -> str:
    """Set every explicit sleep duration to 0 and check nothing else changed."""
    pattern = ZERO_SLEEP_PATTERN
    text, n = re.subn(pattern, r'\g<1>0.00000000000000000e+00', original)
    assert n == count
    assert call_counts(text) == call_counts(original)
    assert re.sub(pattern, r'\g<1>ZERO', text) == re.sub(pattern, r'\g<1>ZERO', original)
    return text


# --------------------------------------------------------------------------- clang (optional)

def roundtrip(ll: Path, clang: str = 'clang') -> str:
    """Assemble `ll` to `.bc` and disassemble to `.roundtrip.ll` (no optimisation); return the latter.

    The checks the original builders ran inline. Needs clang; never run in the migration.
    """
    bc, rt = ll.with_suffix('.bc'), ll.with_suffix('.roundtrip.ll')
    for out in (bc, rt):
        paths.ensure_writable(out)
    subprocess.run([clang, *CLANG_TARGET, '-x', 'ir', '-c', '-emit-llvm', '-O0', str(ll), '-o', str(bc)],
                   check=True, capture_output=True)
    subprocess.run([clang, *CLANG_TARGET, '-S', '-emit-llvm', '-O0', str(bc), '-o', str(rt)],
                   check=True, capture_output=True)
    return paths.read_text(rt)


def assemble(clang: str, ll: Path) -> dict:
    """The probe builder's assembly check (also used by the d=3 two-round sweeps)."""
    bc = ll.with_suffix(".bc")
    paths.ensure_writable(bc)
    # Assemble every variant through the same tool, including no_sleep.
    # No optimization: in particular, retain sleep(0).
    cmd = [clang, "-target", "aarch64-unknown-linux-gnu", "-x", "ir", "-c",
           "-emit-llvm", "-O0", str(ll), "-o", str(bc)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    report = {"command": cmd, "returncode": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr}
    paths.write_text(ll.with_suffix(".assembly.json"), json.dumps(report, indent=2) + "\n")
    if result.returncode:
        raise RuntimeError(f"LLVM assembly failed; see {ll.with_suffix('.assembly.json')}")
    # Read the actual submitted bitcode back and check that calls and entrypoint
    # attributes survived assembly. Keep this representation for inspection.
    out = ll.with_suffix(".roundtrip.ll")
    paths.ensure_writable(out)
    subprocess.run([clang, "-target", "aarch64-unknown-linux-gnu", "-S", "-emit-llvm",
                    "-O0", str(bc), "-o", str(out)], check=True, capture_output=True)
    roundtrip = paths.read_text(out)
    if call_counts(roundtrip) != call_counts(paths.read_text(ll)):
        raise RuntimeError("Assembly changed the quantum/runtime call counts")
    for attr in ('"entry_point"', '"required_num_qubits"="10"',
                 '"required_num_results"="17"', '"qir_profiles"="adaptive_profile"'):
        if attr not in roundtrip:
            raise RuntimeError(f"Assembly lost QIR attribute {attr}")
    return {"llvm_assembly": "passed", "call_counts_preserved": True,
            "quantinuum_qircheck": "not_run", "h2_syntax_check": "not_run",
            "emulator_execution": "not_run"}
