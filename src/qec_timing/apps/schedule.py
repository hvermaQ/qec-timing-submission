"""Idle stretches of logical qubits in a compiled logical circuit. Pure Python.

A circuit is a list of `LogicalGate`s (qubits, is it non-Clifford). It is
scheduled as soon as possible; each gate's duration depends on the time model:

    "uniform"  every gate takes one logical step;
    "magic"    only non-Clifford gates take a step. Cliffords take no time
               (absorbed by frame tracking / lattice surgery) but still order
               the gates around them, and do not interrupt an idle stretch.

Idle = steps between a qubit's first and last operation in which it has no gate
that takes time. Time before the first and after the last operation is excluded
(late allocation / early measurement could avoid it), so this is a lower bound.
Not modelled: routing, magic-state factory throughput, rotation synthesis; each
makes qubits wait longer.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from qec_timing.apps.base import IdleProfile, TimeModel


@dataclass(frozen=True)
class LogicalGate:
    qubits: tuple[int, ...]
    non_clifford: bool


def profile(gates: list[LogicalGate], n_qubits: int, time_model: TimeModel) -> IdleProfile:
    if time_model not in ("uniform", "magic"):
        raise ValueError(f"unknown time model {time_model!r}")
    t: dict[int, float] = defaultdict(float)
    busy: dict[int, list[tuple[float, float]]] = defaultdict(list)
    for g in gates:
        dur = 1.0 if (time_model == "uniform" or g.non_clifford) else 0.0
        start = max(t[q] for q in g.qubits)
        for q in g.qubits:
            t[q] = start + dur
            busy[q].append((start, start + dur))       # zero-length: activity, no time
    active, stretches = [], []
    for q in range(n_qubits):
        iv = busy.get(q)
        if not iv:
            active.append(0.0)
            stretches.append(())
            continue
        first, last = min(s for s, _ in iv), max(e for _, e in iv)
        runs, cur = [], first
        for s, e in sorted(x for x in iv if x[1] > x[0]):
            if s > cur + 1e-12:
                runs.append(s - cur)
            cur = max(cur, e)
        if last > cur + 1e-12:
            runs.append(last - cur)
        active.append(last - first)
        stretches.append(tuple(runs))
    return IdleProfile(n_qubits=n_qubits, steps=max(t.values(), default=0.0),
                       active=tuple(active), stretches=tuple(stretches), time_model=time_model)
