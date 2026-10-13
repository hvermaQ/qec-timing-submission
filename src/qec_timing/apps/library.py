"""Small applications as `IdleSource`s, built and compiled with pytket.

Each is rebased by pytket to {CX, H, S, Sdg, T, Tdg, X, Z, Rz} at the logical level.
An Rz is Clifford at multiples of pi/2; otherwise (T-like or arbitrary) it is
non-Clifford. Original repo: notebooks/10_application_idle_fraction.ipynb.

    qft         n qubits; each qubit is a target once, then only a control.
    ising       n-qubit 1D transverse-field Ising chain, `steps` Trotter steps:
                local and uniform, every qubit busy every step.
    adder       Cuccaro ripple-carry adder on n bits (2n + 2 qubits): a carry
                wave runs up the register and back; Toffoli-heavy.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

from qec_timing.apps.base import IdleProfile, TimeModel
from qec_timing.apps.schedule import LogicalGate, profile
from qec_timing.registry import register


def _pytket():
    from pytket import Circuit, OpType
    from pytket.passes import AutoRebase, DecomposeBoxes
    return Circuit, OpType, AutoRebase, DecomposeBoxes


def to_gates(circ) -> list[LogicalGate]:
    """Rebase to Clifford + T + Rz and classify each gate."""
    _, OpType, AutoRebase, DecomposeBoxes = _pytket()
    c = circ.copy()
    DecomposeBoxes().apply(c)
    AutoRebase({OpType.CX, OpType.H, OpType.S, OpType.Sdg, OpType.T, OpType.Tdg,
                OpType.X, OpType.Z, OpType.Rz}).apply(c)
    out = []
    for cmd in c.get_commands():
        t = cmd.op.type
        if t in (OpType.T, OpType.Tdg):
            nc = True
        elif t == OpType.Rz:
            half_turns = (float(cmd.op.params[0]) * 2) % 1.0     # pytket angles: units of pi
            nc = not (math.isclose(half_turns, 0.0, abs_tol=1e-9)
                      or math.isclose(half_turns, 1.0, abs_tol=1e-9))
        else:
            nc = False
        out.append(LogicalGate(tuple(q.index[0] for q in cmd.qubits), nc))
    return out


def qft_circuit(n: int):
    Circuit = _pytket()[0]
    c = Circuit(n)
    for j in range(n):
        c.H(j)
        for k in range(j + 1, n):
            c.CU1(1 / 2 ** (k - j), k, j)
    return c                                    # final reversal swaps omitted (a relabelling)


def ising_circuit(n: int, steps: int, theta: float = 0.1, phi: float = 0.07):
    Circuit = _pytket()[0]
    c = Circuit(n)
    for _ in range(steps):
        for parity in (0, 1):
            for i in range(parity, n - 1, 2):
                c.ZZPhase(theta, i, i + 1)
        for i in range(n):
            c.Rx(phi, i)
    return c


def adder_circuit(nbits: int):
    """Cuccaro ripple-carry adder: qubit 0 carry-in, then (b_i, a_i), last carry-out.
    Computes b <- a + b. Returns (circuit, a indices, b indices, carry-out)."""
    Circuit = _pytket()[0]
    n = 2 * nbits + 2
    c = Circuit(n)
    b = [1 + 2 * i for i in range(nbits)]
    a = [2 + 2 * i for i in range(nbits)]
    z = n - 1
    carry = [0] + a[:-1]
    for i in range(nbits):                       # MAJ
        c.CX(a[i], b[i]); c.CX(a[i], carry[i]); c.CCX(carry[i], b[i], a[i])
    c.CX(a[-1], z)
    for i in reversed(range(nbits)):             # UMA
        c.CCX(carry[i], b[i], a[i]); c.CX(a[i], carry[i]); c.CX(carry[i], b[i])
    return c, a, b, z


@dataclass(frozen=True)
class _PytketSource:
    def _circuit(self):
        raise NotImplementedError

    def idle_profile(self, time_model: TimeModel) -> IdleProfile:
        c = self._circuit()
        return profile(to_gates(c), c.n_qubits, time_model)


@register("idle_source", "qft")
@dataclass(frozen=True)
class QFT(_PytketSource):
    n: int
    name = "qft"

    def params(self) -> dict[str, Any]:
        return {"n": self.n}

    def _circuit(self):
        return qft_circuit(self.n)


@register("idle_source", "ising")
@dataclass(frozen=True)
class IsingTrotter(_PytketSource):
    n: int
    steps: int
    name = "ising"

    def params(self) -> dict[str, Any]:
        return {"n": self.n, "steps": self.steps}

    def _circuit(self):
        return ising_circuit(self.n, self.steps)


@register("idle_source", "adder")
@dataclass(frozen=True)
class CuccaroAdder(_PytketSource):
    nbits: int
    name = "adder"

    def params(self) -> dict[str, Any]:
        return {"nbits": self.nbits}

    def _circuit(self):
        return adder_circuit(self.nbits)[0]
