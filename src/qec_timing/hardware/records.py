"""Hardware shots -> `RawRecord`, so device data goes through the same decoders,
extractors and analyses as simulated data. numpy only (imports in every env).

A hardware memory program (`hardware/qir.py`) emits, per shot, the measured
syndrome bit of every check of the memory basis in every round (tag
s{round}_{check}) and the final data readout (tag m{qubit}). Detection events are
computed here, offline, with the standard layout of `qec_timing.records`:
D[r, c] = s[r, c] XOR s[r-1, c] (round -1 ideal), and a final block comparing the
checks recomputed from the data readout with the last round.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

import numpy as np

from qec_timing.codes.base import checks_of
from qec_timing.records import DetectorLayout, RawRecord
from qec_timing.spec import MemorySpec

_SYN = re.compile(r"^s(\d+)_(\d+)$")
_DATA = re.compile(r"^m(\d+)$")


def bits_from_shots(shots: Iterable[Mapping[str, Any]], n_rounds: int, n_checks: int,
                    n_data: int) -> tuple[np.ndarray, np.ndarray]:
    """(syndromes [shots, rounds, checks], data [shots, n_data]) from per-shot tag maps.
    Every expected tag must be present exactly once; anything else is an error."""
    syn, dat = [], []
    for k, shot in enumerate(shots):
        s = np.full((n_rounds, n_checks), -1, dtype=np.int8)
        m = np.full(n_data, -1, dtype=np.int8)
        for tag, value in shot.items():
            v = int(value[0] if isinstance(value, (list, tuple)) else value)
            if (g := _SYN.match(tag)):
                s[int(g[1]), int(g[2])] = v
            elif (g := _DATA.match(tag)):
                m[int(g[1])] = v
        if (s < 0).any() or (m < 0).any():
            raise ValueError(f"shot {k}: missing syndrome or data tags")
        syn.append(s)
        dat.append(m)
    return np.array(syn, dtype=bool), np.array(dat, dtype=bool)


def record_from_bits(spec: MemorySpec, syndromes: np.ndarray, data: np.ndarray,
                     payload: dict | None = None,
                     attachments: dict[str, bytes] | None = None) -> RawRecord:
    checks = checks_of(spec.code, spec.basis)
    shots, R, C = syndromes.shape
    if (R, C) != (spec.schedule.n_rounds, len(checks)) or data.shape != (shots, spec.code.n_data):
        raise ValueError("bit arrays do not match the spec")
    H = np.zeros((C, spec.code.n_data), dtype=np.uint8)
    for i, c in enumerate(checks):
        H[i, list(c.support)] = 1
    final = (data.astype(np.uint8) @ H.T) % 2
    s = np.concatenate([syndromes, final[:, None, :].astype(bool)], axis=1)
    prev = np.concatenate([np.zeros_like(s[:, :1]), s[:, :-1]], axis=1)
    det = (s ^ prev).reshape(shots, -1)
    obs = (data[:, list(spec.code.logical(spec.basis))].sum(axis=1) % 2).astype(bool)[:, None]
    sched = spec.schedule
    nan = np.full(R, np.nan)          # device noise per round is measured, not known
    rounds = {"dt": np.array(sched.dts), "t": np.array(sched.starts), "p_data": nan,
              "p_read": nan.copy()}
    return RawRecord(DetectorLayout(R, C), det, obs, rounds, payload or {}, attachments or {})
