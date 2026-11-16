"""Skip-index-5 qubit mapping for physical H2-2 d=5 (data 0-4,6-25; ancilla 26; index 5 unused).

One implementation of what was written three times: `mapped_qir` in the three
submit_d5_h2_2_t1_skip5_*.py scripts and the `.ll` remap in d5_h2_2_zero_sleep_n3_skip5.py
(the originals are archived in results/sleep/submission_scripts/). Both worked on QIR text
with the same pattern, forward map, inverse map and checks. Output labels keep the original
code positions. Never pool skip-5 data with original-mapping data (/AGENTS.md).
"""
from __future__ import annotations

import re

from .qir import call_counts

PATTERN = r'%Qubit\* (?:nonnull )?(?:inttoptr \(i64 (\d+) to %Qubit\*\)|null)'
UNUSED_INDEX = 5
DATA_INDICES = list(range(5)) + list(range(6, 26))
ANCILLA_INDEX = 26


def forward_index(q: int) -> int:
    """Submitted index of original qubit q (original 0..25 -> 0-4, 6..26)."""
    return q + (q >= UNUSED_INDEX)


def inverse_index(q: int) -> int:
    """Original index of submitted qubit q (inverse of `forward_index`)."""
    if q == UNUSED_INDEX:
        raise ValueError('index 5 is unused in the skip-5 mapping')
    return q - (q > UNUSED_INDEX)


def _forward(m):
    q=int(m[1] or 0)
    return m[0] if q<5 else m[0].replace(f'i64 {q} ',f'i64 {q+1} ')


def _inverse(m):
    q=int(m[1] or 0)
    return m[0] if q<6 else m[0].replace(f'i64 {q} ',f'i64 {q-1} ')


def unskip5(text: str) -> str:
    """Map skip-5 QIR text back to the original 26-qubit indices."""
    return re.sub(PATTERN,_inverse,text).replace('"required_num_qubits"="27"','"required_num_qubits"="26"')


def skip5(original: str) -> str:
    """Remap original d=5 QIR text (26 qubits) to skip index 5, checking the exact inverse."""
    text=re.sub(PATTERN,_forward,original).replace('"required_num_qubits"="26"','"required_num_qubits"="27"')
    assert {int(m[1] or 0) for m in re.finditer(PATTERN,text)}==set(range(27))-{5}
    assert unskip5(text)==original, 'Remapping changed more than qubit indices and declared range'
    assert call_counts(text)==call_counts(original)
    return text
