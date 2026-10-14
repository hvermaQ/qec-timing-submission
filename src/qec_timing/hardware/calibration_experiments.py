"""Device calibration experiments and their fits (notebook 13; the original
repo's docs/notebook_arc/hardware_tests.md, tests T2-T4).

There is no user-controlled delay in Guppy (0.21 or 1.x) or pytket, so idle time
is made by SPECTATOR IDLING: target qubits wait while spectators run L layers of
mid-circuit measurement, with the ordering forced by feed-forward (see
`idle_program`). Idle time is then counted in layers; converting to seconds needs
the duration of a layer (from the job's duration report, or Quantinuum).

    readout   (T2)  half the qubits in |0>, half in |1>, measured: p_meas0, p_meas1.
    idle      (T3/T4) targets in |+> (basis X: sees dephasing) or |0> (basis Z:
                    should see nothing if idling is Z only), L spectator layers,
                    then measured in the same basis. Fitted, per layer, with the
                    emulator's exact form: linear gamma_L * L and quadratic
                    sin^2(sqrt(c_L) * L), composed, on top of the L = 0 floor.

Programs are Guppy 0.21 traced entrypoints (H2 env) producing QIR through the
same path as the memory experiment. Fits are numpy only (any env), and turn into
a `Calibration` once the layer duration is known.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

# --- programs (H2 env) ---------------------------------------------------------


def readout_program(n: int, seed: int = 0):
    """n qubits in |0> then n in |1>, all measured: tags r0_{i}, r1_{i}."""
    from guppylang import guppy
    from guppylang.std.builtins import result
    from guppylang.std.quantum import measure, qubit, x

    @guppy.comptime
    def main() -> None:
        zeros = [qubit() for _ in range(n)]
        ones = [qubit() for _ in range(n)]
        for q in ones:
            x(q)
        for i, q in enumerate(zeros):
            result(f"r0_{i}", measure(q))
        for i, q in enumerate(ones):
            result(f"r1_{i}", measure(q))

    return main


def idle_program(n_targets: int, n_spectators: int, layers: int, basis: str = "X"):
    """Targets wait while spectators run `layers` layers of mid-circuit measurement.

    No barrier: Guppy 0.21's traced mode consumes barrier arguments and hugr-qir
    0.1.2 cannot lower it. Ordering is forced by data dependencies instead:
      - a layer is H, measure (project_z), reset on every spectator. A measurement
        whose outcome is used cannot be removed or merged by the compiler;
      - after the last layer each target gets Z conditioned on the parity of all
        spectator outcomes (feed-forward), so its measurement cannot move before
        them. Z is virtual (error-free) on H2. In basis X the conditional Z flips the
        outcome, and the analysis XORs the recorded parity back out; in basis Z it
        acts trivially on |0>.
    Tags: t{i} (target outcome), par (spectator parity)."""
    from guppylang import guppy
    from guppylang.std.builtins import result
    from guppylang.std.quantum import discard, h, measure, project_z, qubit, reset, z

    if basis not in ("X", "Z"):
        raise ValueError("basis must be X or Z")
    if n_spectators < 1:
        raise ValueError("need at least one spectator")
    x_basis = basis == "X"

    @guppy
    def xor_(a: bool, b: bool) -> bool:
        return a != b

    @guppy
    def cond_z(q: qubit, flip: bool) -> None:
        if flip:
            z(q)

    @guppy.comptime
    def main() -> None:
        targets = [qubit() for _ in range(n_targets)]
        spect = [qubit() for _ in range(n_spectators)]
        if x_basis:
            for q in targets:
                h(q)
        par = False
        for _ in range(layers):
            for s in spect:
                h(s)
                par = xor_(par, project_z(s))
                reset(s)
        for q in targets:
            cond_z(q, par)
        result("par", par)
        for i, q in enumerate(targets):
            if x_basis:
                h(q)
            result(f"t{i}", measure(q))
        for s in spect:
            discard(s)

    return main


# --- fits (numpy) --------------------------------------------------------------

@dataclass(frozen=True)
class Rate:
    k: int
    n: int

    @property
    def p(self) -> float:
        return self.k / self.n

    @property
    def se(self) -> float:
        return math.sqrt(max(self.p * (1 - self.p), 1 / self.n) / self.n)


def fit_readout(shots: list[dict]) -> dict:
    """p_meas0 = P(read 1 | prepared 0), p_meas1 = P(read 0 | prepared 1)."""
    k0 = n0 = k1 = n1 = 0
    for s in shots:
        for tag, v in s.items():
            bit = int(v[0] if isinstance(v, (list, tuple)) else v)
            if tag.startswith("r0_"):
                k0, n0 = k0 + bit, n0 + 1
            elif tag.startswith("r1_"):
                k1, n1 = k1 + (1 - bit), n1 + 1
    r0, r1 = Rate(k0, n0), Rate(k1, n1)
    return {"p_meas0": r0.p, "p_meas0_se": r0.se, "p_meas1": r1.p, "p_meas1_se": r1.se,
            "shots": len(shots)}


def flips(shots: list[dict], basis: str) -> Rate:
    """Pooled target flips. Targets start in the measured basis' 0 state; in basis X
    the feed-forward Z flipped them iff the spectator parity was 1, so it is undone."""
    val = lambda v: int(v[0] if isinstance(v, (list, tuple)) else v)      # noqa: E731
    k = n = 0
    for s in shots:
        par = val(s.get("par", 0)) if basis == "X" else 0
        for tag, v in s.items():
            if tag.startswith("t"):
                k += val(v) ^ par
                n += 1
    return Rate(k, n)


def idle_pz(L, gamma: float, c: float):
    """Exact emulator form per layer: linear and quadratic Z channels composed."""
    lin = np.minimum(gamma * L, 0.5)
    quad = np.sin(np.sqrt(max(c, 0.0)) * L) ** 2
    return lin + quad - 2 * lin * quad


def fit_idle(layers: list[int], rates: list[Rate], iterations: int = 50) -> dict:
    """Fit gamma_L (linear) and c_L (quadratic) per layer to the target flip rates.

    Model: P(L) = 1/2 [1 - (1 - 2 P0)(1 - 2 pz(L))], P0 the L = 0 floor (state prep
    and measurement), pz the exact composed idle channel (`idle_pz`). Weighted
    Gauss-Newton, started from the small-angle linear solution pz ~ gamma L + c L^2.
    Uncertainties from the final Jacobian, scaled up by chi^2/dof when it exceeds 1."""
    L = np.asarray(layers, float)
    if L[0] != 0:
        raise ValueError("the first layer count must be 0 (the SPAM floor)")
    P = np.array([r.p for r in rates])
    se = np.array([r.se for r in rates])
    floor = 1 - 2 * P[0]
    model = lambda th: 0.5 * (1 - floor * (1 - 2 * idle_pz(L[1:], *th)))   # noqa: E731
    w = 1 / se[1:] ** 2
    # Start: small-angle linear least squares on the floor-corrected idle part.
    pz = (1 - (1 - 2 * P[1:]) / floor) / 2
    A = np.stack([L[1:], L[1:] ** 2], axis=1)
    th = np.linalg.lstsq(A * np.sqrt(w)[:, None], pz * np.sqrt(w), rcond=None)[0]
    th = np.maximum(th, 1e-12)
    for _ in range(iterations):
        r = P[1:] - model(th)
        J = np.stack([(model(th + dv) - model(th - dv)) / (2 * dv[i])
                      for i, dv in enumerate(np.diag(np.maximum(1e-6 * th, 1e-12)))], axis=1)
        step = np.linalg.solve(J.T @ (J * w[:, None]), J.T @ (w * r))
        th = np.maximum(th + step, 0.0)
        if np.all(np.abs(step) <= 1e-10 + 1e-8 * np.abs(th)):
            break
    r = P[1:] - model(th)
    dof = max(len(r) - 2, 1)
    chi2 = float(r @ (w * r) / dof)
    cov = np.linalg.inv(J.T @ (J * w[:, None])) * max(chi2, 1.0)
    return {"spam_floor": float(P[0]), "gamma_per_layer": float(th[0]),
            "gamma_per_layer_se": float(math.sqrt(cov[0, 0])), "c_per_layer": float(th[1]),
            "c_per_layer_se": float(math.sqrt(cov[1, 1])), "chi2_per_dof": chi2,
            "layers": [int(x) for x in L], "P": [float(x) for x in P]}


def to_calibration_fields(idle_fit: dict, layer_seconds: float, factor: float = 2.0,
                          convention: str = "cycles") -> dict:
    """Per-layer idle fit -> Calibration's gamma [1/s] and quadratic rate, given the
    duration of one spectator layer. sin^2(sqrt(c_L) L) = sin^2(omega t / 2) with
    t = L * tau gives omega = 2 sqrt(c_L) / tau; quad_rate f = omega / (2 pi k) in the
    'cycles' reading (k = coherent_to_incoherent_factor), omega / k in 'radians'."""
    tau = layer_seconds
    c = max(idle_fit["c_per_layer"], 0.0)
    omega = 2 * math.sqrt(c) / tau
    f = omega / (2 * math.pi * factor) if convention == "cycles" else omega / factor
    return {"gamma": max(idle_fit["gamma_per_layer"], 0.0) / tau, "quad_rate": f,
            "quad_factor": factor, "quad_convention": convention}
