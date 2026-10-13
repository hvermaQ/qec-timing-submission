"""The paper's analytic ansatz (Haug, Bharti & Aolita 2026, Eqs. 5-7, D1-D9).

    alpha = g (d + 1) / 2                                         (D2)
    R(dt) = (1/dt) (A / d^beta) (p / p_th)^((d+1)/2) (1 + lam dt)^alpha   (Eq. 5)
    dt*   = 1 / (lam (alpha - 1))                                 (Eq. 6)
    Gamma(dt) = R(dt) / R(dt*) = (1 + lam dt)^alpha / (lam dt K_alpha)   (Eq. 7)
    K_alpha = alpha^alpha / (alpha - 1)^(alpha - 1)               (D8)

Fitted constants (paper): g = 0.8 (b_read = 1, 2), beta = 2, p_th = 0.029 (b_read = 1),
fitted on d = 11-27. Ported from the original repo's ansatz.py.
"""

from __future__ import annotations

import numpy as np

G_DEFAULT, BETA_DEFAULT, P_TH_BREAD_1 = 0.8, 2.0, 0.029
PAPER_SLOPE = 0.402            # Fig. 2: 1/dt* ~ 0.402 d + z (p = 0.015, lam = 1, d = 11-27)


def alpha(d, g: float = G_DEFAULT):
    return g * (np.asarray(d, dtype=float) + 1.0) / 2.0


def K_alpha(a):
    a = np.asarray(a, dtype=float)
    if np.any(a <= 1.0):
        raise ValueError("K_alpha requires alpha > 1")
    return np.exp(a * np.log(a) - (a - 1.0) * np.log(a - 1.0))


def logical_rate(dt, *, d: int, p: float, lam: float, A: float, p_th: float = P_TH_BREAD_1,
                 beta: float = BETA_DEFAULT, g: float = G_DEFAULT):
    dt = np.asarray(dt, dtype=float)
    return (A / d ** beta) * (p / p_th) ** ((d + 1) / 2.0) * (1.0 + lam * dt) ** alpha(d, g) / dt


def optimal_interval(*, d: int, lam: float, g: float = G_DEFAULT) -> float:
    a = float(alpha(d, g))
    if lam <= 0 or a <= 1:
        raise ValueError("no interior optimum: needs lam > 0 and alpha > 1")
    return 1.0 / (lam * (a - 1.0))


def gamma_opt(dt, *, d: int, lam: float, g: float = G_DEFAULT):
    dt = np.asarray(dt, dtype=float)
    a = alpha(d, g)
    return (1.0 + lam * dt) ** a / (lam * dt * K_alpha(a))
