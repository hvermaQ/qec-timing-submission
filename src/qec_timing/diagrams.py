"""Matplotlib circuit diagrams of the hardware programs (notebook 13). Drawing only.

A circuit is a list of operations on named wires; `layer()` packs them greedily into
columns (an operation goes in the first column after the last one touching any of its
wires), and `draw()` renders boxes, CNOTs, measurements, resets and classically
controlled gates. The memory diagram is built from `checks_of(code, basis)`, the same
extraction orders `hardware.qir.build_program` compiles, so it shows that program.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from qec_timing import plotting as P


@dataclass
class Op:
    kind: str                     # "box", "cx", "meas", "reset", "cond", "bracket"
    wires: tuple[int, ...]
    label: str = ""
    color: str | None = None
    col: int = -1


@dataclass
class Circuit:
    wires: list[str]
    ops: list[Op] = field(default_factory=list)
    regions: list[tuple[int, int, int, int, str]] = field(default_factory=list)  # ops i..j, wires a..b

    def region(self, first_op: int, last_op: int, wire_a: int, wire_b: int, label: str):
        self.regions.append((first_op, last_op, wire_a, wire_b, label))
        return self

    def add(self, kind, *wires, label="", color=None):
        self.ops.append(Op(kind, tuple(wires), label, color))
        return self

    def layer(self) -> int:
        last = [-1] * len(self.wires)
        for op in self.ops:
            span = (range(len(self.wires)) if op.kind == "barrier" else
                    range(min(op.wires), max(op.wires) + 1) if op.kind == "cx" else op.wires)
            op.col = max(last[w] for w in span) + 1
            for w in span:
                last[w] = op.col
        return max(last) + 1


def draw(ax, circ: Circuit, title: str = "", dx: float = 0.62):
    ncol = circ.layer()
    n = len(circ.wires)
    y = {i: n - 1 - i for i in range(n)}
    x0, x1 = -0.3, ncol * dx + 0.1
    for i, name in enumerate(circ.wires):
        ax.plot([x0, x1], [y[i], y[i]], color=P.MUTED, lw=0.9, zorder=0)
        ax.text(x0 - 0.12, y[i], name, ha="right", va="center", fontsize=8, color=P.INK)
    box = dict(boxstyle="square,pad=0.18", fc=P.SURFACE, lw=0.9)
    for op in circ.ops:
        x = op.col * dx + 0.2
        c = op.color or P.INK
        if op.kind == "barrier":
            ax.plot([x, x], [-0.5, n - 0.5], color=P.MUTED, lw=0.8, ls=(0, (2, 3)), zorder=0)
            if op.label:
                ax.text(x, -0.55, op.label, ha="center", va="top", fontsize=7, color=P.INK_2)
        elif op.kind == "cx":
            a, b = op.wires
            ax.plot([x, x], [y[a], y[b]], color=c, lw=1.0, zorder=1)
            ax.plot(x, y[a], "o", color=c, ms=4, zorder=2)
            ax.plot(x, y[b], "o", ms=10, mfc=P.SURFACE, mec=c, mew=1.0, zorder=2)
            ax.plot([x, x], [y[b] - 0.17, y[b] + 0.17], color=c, lw=1.0, zorder=3)
            ax.plot([x - 0.1, x + 0.1], [y[b], y[b]], color=c, lw=1.0, zorder=3)
        else:
            for w in op.wires:
                label = {"meas": op.label or "M", "reset": "|0⟩"}.get(op.kind, op.label)
                bs = dict(box, ec=c, ls="--" if op.kind == "cond" else "-")
                ax.text(x, y[w], label, ha="center", va="center", fontsize=7.5, color=c,
                        bbox=bs, zorder=3)
    from matplotlib.patches import FancyBboxPatch
    for i, j, wa, wb, label in circ.regions:
        xa, xb = circ.ops[i].col * dx + 0.2 - 0.3, circ.ops[j].col * dx + 0.2 + 0.3
        ya, yb = y[wb] - 0.4, y[wa] + 0.4
        ax.add_patch(FancyBboxPatch((xa, ya), xb - xa, yb - ya, boxstyle="round,pad=0.02",
                                    fc="none", ec=P.INK_2, ls=":", lw=1.0, zorder=0))
        ax.text((xa + xb) / 2, yb + 0.05, label, ha="center", va="bottom", fontsize=7.5,
                color=P.INK_2)
    ax.set_xlim(x0 - 1.0, x1 + 0.2)
    ax.set_ylim(-1.0, n - 0.2)
    ax.axis("off")
    if title:
        ax.set_title(title, loc="left", fontsize=10)
    return ncol


def memory_circuit(code, basis: str = "X", rounds: int = 2, inject: bool = True) -> Circuit:
    """The hardware memory program: data qubits, ONE reused ancilla, checks in extraction
    order, optional injected Pauli on every data qubit before each round."""
    from qec_timing.codes.base import checks_of

    n = code.n_data
    circ = Circuit([f"d{i}" for i in range(n)] + ["anc"])
    a = n
    x_basis = basis == "X"
    if x_basis:
        for q in range(n):
            circ.add("box", q, label="H")
    pauli = "Z" if x_basis else "X"
    for r in range(rounds):
        circ.add("barrier", 0, label=f"round {r}")
        if inject:
            for q in range(n):
                circ.add("box", q, label=f"{pauli}?", color=P.SERIES[1])
        for ci, ch in enumerate(checks_of(code, basis)):
            if x_basis:
                circ.add("box", a, label="H")
                for i in ch.extraction_order:
                    circ.add("cx", a, i, color=P.SERIES[0])
                circ.add("box", a, label="H")
            else:
                for i in ch.extraction_order:
                    circ.add("cx", i, a, color=P.SERIES[0])
            circ.add("meas", a, label=f"s{r}{ci}")
            circ.add("reset", a)
    circ.add("barrier", 0, label="final readout")
    for q in range(n):
        if x_basis:
            circ.add("box", q, label="H")
        circ.add("meas", q, label=f"m{q}")
    return circ


def readout_circuit(n: int = 8, show: int = 2) -> Circuit:
    """`show` of the n qubits per half, then an ellipsis wire."""
    wires = [f"q{i}" for i in range(show)] + ["⋮"] + [f"q{n + i}" for i in range(show)] + ["⋮ "]
    circ = Circuit(wires)
    for i in range(show):
        circ.add("meas", i, label=f"r0_{i}")
    for i in range(show):
        w = show + 1 + i
        circ.add("box", w, label="X")
        circ.add("meas", w, label=f"r1_{i}")
    return circ


def idle_circuit(basis: str = "X", show_targets: int = 2, spectators: int = 2) -> Circuit:
    """Targets wait while spectators run L layers of H, measure, reset; then a Z on each
    target conditioned on the spectators' parity (feed-forward) forces the order."""
    t = [f"t{i}" for i in range(show_targets)] + ["⋮"]
    s = [f"s{i}" for i in range(spectators)]
    circ = Circuit(t + s)
    tg = list(range(show_targets))
    sp = list(range(len(t), len(t) + spectators))
    x_basis = basis == "X"
    if x_basis:
        for q in tg:
            circ.add("box", q, label="H")
    circ.add("barrier", 0, label="prepared")
    first = len(circ.ops)
    for q in sp:
        circ.add("box", q, label="H")
        circ.add("meas", q, label="M")
        circ.add("reset", q)
    circ.region(first, len(circ.ops) - 1, tg[0], sp[-1],
                "repeat L times (targets idle)")
    circ.add("barrier", 0, label="feed-forward")
    for q in tg:
        circ.add("cond", q, label="Z if parity", color=P.SERIES[1])
    for q in tg:
        if x_basis:
            circ.add("box", q, label="H")
        circ.add("meas", q, label=f"t{q}")
    return circ


def schematic(ax, blocks: list[tuple[str, str]], title: str = "", repeat: tuple[int, int, str] | None = None):
    """A row of labelled stages joined by arrows. blocks: (heading, detail); `repeat`
    = (first, last, label) draws a bracket over blocks first..last."""
    from matplotlib.patches import FancyBboxPatch
    w, gap = 2.3, 0.45
    for k, (head, detail) in enumerate(blocks):
        x = k * (w + gap)
        ax.add_patch(FancyBboxPatch((x, 0), w, 1.0, boxstyle="round,pad=0.04", fc=P.SURFACE,
                                    ec=P.SERIES[0], lw=1.2))
        ax.text(x + w / 2, 0.72, head, ha="center", va="center", fontsize=8.5, color=P.INK,
                weight="bold")
        ax.text(x + w / 2, 0.33, detail, ha="center", va="center", fontsize=7.2, color=P.INK_2)
        if k:
            ax.annotate("", (x, 0.5), (x - gap, 0.5),
                        arrowprops=dict(arrowstyle="->", color=P.MUTED, lw=1.2))
    if repeat:
        a, b, label = repeat
        xa, xb = a * (w + gap) - 0.08, b * (w + gap) + w + 0.08
        ax.plot([xa, xa, xb, xb], [1.12, 1.25, 1.25, 1.12], color=P.INK_2, lw=1.0)
        ax.text((xa + xb) / 2, 1.3, label, ha="center", va="bottom", fontsize=8, color=P.INK_2)
    ax.set_xlim(-0.2, len(blocks) * (w + gap))
    ax.set_ylim(-0.15, 1.6)
    ax.axis("off")
    if title:
        ax.set_title(title, loc="left", fontsize=10)
