"""The syndrome-interval trade-off: grids, rates, and locating the optimum dt*.

Figure of merit (paper): logical error per unit time at fixed total time T,
    R = -ln(1 - 2 p_L) / (2 T)          (paper Eq. A3 inverted)
which equals p_L / T while p_L << 1 and does not reward a failed code as p_L -> 1/2.

dt* is located by a weighted parabola in log(dt) fitted to log R over the points
within `rel` of the lowest (at least 5), never by taking the lowest sampled
point. Its interval is a parametric bootstrap of the rates (16th-84th percentile).
Ported unchanged from the original repo's notebooks 07-09.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np


def dt_grid(T: float, d: int, n: int = 16) -> list[tuple[float, int]]:
    """(dt, R) with dt = T / R on a log grid from 1 to T/d; R integer, so dt is exact
    and R >= d (enough rounds for the figure of merit)."""
    Rs = sorted({int(round(T / x)) for x in np.geomspace(1.0, T / d, n) if round(T / x) >= d},
                reverse=True)
    return [(T / R, R) for R in Rs]


def rate(failures: int, shots: int, T: float) -> tuple[float, float]:
    """(R, sigma_R); NaN once p_L >= 1/2 (saturated: no rate information)."""
    p = failures / shots
    s = math.sqrt(max(p * (1 - p), 1e-12) / shots)
    if p >= 0.5:
        return math.nan, math.nan
    return -math.log1p(-2 * p) / (2 * T), s / ((1 - 2 * p) * T)


@dataclass(frozen=True)
class Optimum:
    dt_star: float
    lo: float              # bootstrap 16th percentile
    hi: float              # bootstrap 84th percentile
    lowest: float          # grid point with the lowest rate
    interior: bool         # the lowest point is not at either end of the grid

    def as_dict(self) -> dict:
        return {"dt_star": self.dt_star, "lo": self.lo, "hi": self.hi,
                "lowest": self.lowest, "interior": self.interior}


def optimum(dt, pL, r, sr, rel: float = 1.3, n_boot: int = 2000, seed: int = 0) -> Optimum:
    dt, pL, r, sr = map(lambda a: np.asarray(a, float), (dt, pL, r, sr))
    ok = (pL < 0.45) & np.isfinite(r)                 # saturated points carry no rate
    x, y, s, dts = np.log(dt[ok]), r[ok], sr[ok], dt[ok]
    i = int(np.argmin(y))
    w = np.where(y <= rel * y[i])[0]
    lo, hi = w.min(), w.max()
    while hi - lo + 1 < 5 and (lo > 0 or hi < len(y) - 1):
        lo, hi = max(lo - 1, 0), min(hi + 1, len(y) - 1)
    sl = slice(lo, hi + 1)

    def vertex(yy):
        a, b, _ = np.polyfit(x[sl], np.log(yy[sl]), 2, w=yy[sl] / s[sl])
        if a <= 0:                                    # no minimum: fall back to the lowest point
            return x[sl][np.argmin(yy[sl])]
        return float(np.clip(-b / (2 * a), x[sl][0], x[sl][-1]))

    rng = np.random.default_rng(seed)
    boots = [vertex(np.maximum(y + rng.normal(0, s), 1e-12)) for _ in range(n_boot)]
    q16, q84 = np.exp(np.percentile(boots, [16, 84]))
    return Optimum(float(np.exp(vertex(y))), float(q16), float(q84), float(dts[i]),
                   bool(0 < i < len(y) - 1))
