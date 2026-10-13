"""Measure the paper's two per-round parameters from a run's detection events.

Edge probability between detectors i and j, for independent graphlike errors
(Google, Nature 595, 383 (2021), supplement):

    p_ij = 1/2 - 1/2 sqrt(1 - 4 (<x_i x_j> - <x_i><x_j>) / (1 - 2<x_i> - 2<x_j> + 4<x_i x_j>))

Edges used, bulk rounds only (not round 0, not the final readout block):
    time   (c, r) - (c, r+1)                     a flipped syndrome record   -> p_read
    space  (a, r) - (b, r)                       a flip of the data qubit a and b share
    diag   (a, r) - (b, r+1), (a, r+1) - (b, r)  the same flip, between a's and b's CNOTs
p_data per check pair = space XOR both diagonals: everything that flips the shared
data qubit once per round, wherever in the round it happens.

Works on any `RawRecord` in the standard detector layout, for any code whose
checks of one type share at most one data qubit pairwise.
"""

from __future__ import annotations

import numpy as np

from qec_timing.codes.base import checks_of
from qec_timing.records import EffectiveModel, Estimate, RawRecord
from qec_timing.registry import register
from qec_timing.spec import MemorySpec

Z95 = 1.959964


def xor(*ps):
    """Probability of an odd number of independent flips."""
    q = 1.0
    for p in ps:
        q = q * (1 - 2 * np.asarray(p, dtype=float))
    return (1 - q) / 2


def edge_probability(xi, xj, xij):
    num = 4 * (xij - xi * xj)
    den = 1 - 2 * xi - 2 * xj + 4 * xij
    return 0.5 - 0.5 * np.sqrt(np.clip(1 - num / den, 0.0, None))


def edges(spec: MemorySpec, n_rounds: int) -> dict[str, np.ndarray]:
    """Detector-index pairs per edge class, in the standard layout."""
    checks = checks_of(spec.code, spec.basis)
    C = len(checks)
    sup = [set(c.support) for c in checks]
    pairs = [(a, b) for a in range(C) for b in range(a + 1, C) if sup[a] & sup[b]]
    if any(len(sup[a] & sup[b]) > 1 for a, b in pairs):
        raise ValueError("checks sharing more than one data qubit: space edges are ambiguous")
    at = lambda c, r: r * C + c                                   # noqa: E731
    time_, space, d1, d2 = [], [], [], []
    for r in range(1, n_rounds - 1):                              # r, r+1 both syndrome rounds
        time_ += [(at(c, r), at(c, r + 1)) for c in range(C)]
        for a, b in pairs:
            space.append((at(a, r), at(b, r)))
            d1.append((at(a, r), at(b, r + 1)))
            d2.append((at(a, r + 1), at(b, r)))
    if not time_ or not space:
        raise ValueError("need at least 3 syndrome rounds for bulk edges")
    return {k: np.array(v) for k, v in (("time", time_), ("space", space), ("d1", d1), ("d2", d2))}


@register("extractor", "edges")
class EdgeExtractor:
    name = "edges"

    def extract(self, spec: MemorySpec, record: RawRecord, run_id: str) -> EffectiveModel:
        det = record.detectors
        x = det.mean(0)
        e = {}
        for k, p in edges(spec, record.layout.n_rounds).items():
            xij = (det[:, p[:, 0]] & det[:, p[:, 1]]).mean(0)
            e[k] = edge_probability(x[p[:, 0]], x[p[:, 1]], xij)
        p_data = xor(e["space"], e["d1"], e["d2"])

        def est(a):
            m, se = float(a.mean()), float(a.std(ddof=1) / np.sqrt(len(a)))
            return Estimate(m, m - Z95 * se, m + Z95 * se)

        params = {"p_read": est(e["time"]), "p_data": est(p_data),
                  "p_space": est(e["space"]), "p_diag": est(xor(e["d1"], e["d2"]))}
        params["b_read"] = Estimate(params["p_read"].value / params["p_data"].value,
                                    np.nan, np.nan)         # ratio: no interval claimed
        # A negative MEAN edge means the independent-graphlike assumption has failed
        # (e.g. near saturation) and the estimate is unusable. Single edges may dip
        # below zero by sampling noise when their true value is ~0 (e.g. no
        # mid-round faults), which is not a failure.
        broken = bool(min(params[k].value for k in ("p_read", "p_space", "p_diag")) < 0)
        return EffectiveModel(self.name, params, (run_id,),
                              info={"n_time": int(len(e["time"])), "n_pairs": int(len(e["space"])),
                                    "estimator_broken": broken})
