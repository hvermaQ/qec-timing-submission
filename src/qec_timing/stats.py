"""Statistics shared by analyses: binomial intervals, logical error rates, and the
comparison of two estimates of the same rate."""

from __future__ import annotations

import math
from dataclasses import dataclass

from scipy.stats import beta, chi2


def clopper_pearson(k: int, n: int, level: float = 0.999) -> tuple[float, float]:
    """Exact binomial interval. Used over normal approximations because logical
    error rates reach 1e-4 and below, where those fail."""
    if n <= 0 or not 0 <= k <= n:
        raise ValueError(f"need 0 <= k <= n, n > 0; got k={k}, n={n}")
    a = (1 - level) / 2
    lo = 0.0 if k == 0 else float(beta.ppf(a, k, n - k + 1))
    hi = 1.0 if k == n else float(beta.ppf(1 - a, k + 1, n - k))
    return lo, hi


@dataclass(frozen=True)
class Rate:
    k: int
    n: int

    @property
    def p(self) -> float:
        return self.k / self.n

    @property
    def var(self) -> float:
        return self.p * (1 - self.p) / self.n

    def ci(self, level: float = 0.999) -> tuple[float, float]:
        return clopper_pearson(self.k, self.n, level)


def rate_per_time(p_L: float, T: float) -> float:
    """Logical error rate per unit time, paper Eq. A3 inverted:
    R = -ln(1 - 2 p_L) / (2 T). Undefined once p_L >= 1/2 (saturated)."""
    if p_L >= 0.5:
        return math.inf
    return -math.log1p(-2 * p_L) / (2 * T)


def two_rate_z(a: Rate, b: Rate) -> float:
    """z-score of the difference of two independent binomial rates."""
    pooled = (a.k + b.k) / (a.n + b.n)
    se = math.sqrt(pooled * (1 - pooled) * (1 / a.n + 1 / b.n))
    return (a.p - b.p) / se if se > 0 else 0.0


def pooled_agreement(pairs: list[tuple[Rate, Rate]]) -> dict[str, float]:
    """Joint test over many points, stronger than counting per-point overlaps.

    chi2: sum of z^2 over points, chi-squared with len(pairs) dof under
          "the two estimators agree everywhere".
    mean_z: average signed z, which catches a consistent bias that no single
          point resolves (e.g. one side lower by 10% at every point).
    """
    zs = [two_rate_z(a, b) for a, b in pairs]
    stat = sum(z * z for z in zs)
    mean_z = sum(zs) / len(zs)
    return {"n_points": len(zs), "chi2": stat, "chi2_p": float(chi2.sf(stat, len(zs))),
            "mean_z": mean_z, "mean_z_sigma": mean_z * math.sqrt(len(zs))}
