"""Figure style for the notebooks. Presentation only: no analysis lives here.

Colours from the validated reference palette (dataviz skill, references/palette.md):
categorical slots 1-3 (blue, orange, aqua) for d = 3, 5, 7. Only the first three
slots are validated for all pairs, which scatter-like overlays need; with more
series, facet instead. Sequential: the blue ramp, light (small) to dark (large).
Thin lines, recessive grid and axes, text in ink colours (never series colours).
"""

from __future__ import annotations

from pathlib import Path

SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]            # categorical slots 1-3
D_COLOR = {3: SERIES[0], 5: SERIES[1], 7: SERIES[2]}
SEQUENTIAL = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#184f95", "#0d366b"]
INK, INK_2, MUTED, GRID, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#fcfcfb"


def style() -> None:
    """Apply the house style to matplotlib (call once per notebook)."""
    import matplotlib as mpl

    mpl.rcParams.update({
        "figure.facecolor": SURFACE, "axes.facecolor": SURFACE, "savefig.facecolor": SURFACE,
        "axes.edgecolor": MUTED, "axes.labelcolor": INK_2, "axes.titlecolor": INK,
        "axes.titlesize": 11, "axes.labelsize": 10, "axes.spines.top": False,
        "axes.spines.right": False, "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.6,
        "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK_2,
        "ytick.labelcolor": INK_2, "lines.linewidth": 2.0, "lines.markersize": 5,
        "legend.frameon": False, "legend.labelcolor": INK_2, "font.size": 10,
        "mathtext.fontset": "cm", "figure.dpi": 110,
    })


def sequential_cmap():
    from matplotlib.colors import LinearSegmentedColormap

    return LinearSegmentedColormap.from_list("seq_blue", SEQUENTIAL)


def label_end(ax, x, y, text: str, color: str = INK_2, dx: float = 4) -> None:
    """Direct label at the end of a line, in ink colour (identity is the marker)."""
    ax.annotate(text, (x, y), xytext=(dx, 0), textcoords="offset points", va="center",
                color=color, fontsize=9)


FIGURES = Path(__file__).resolve().parents[2] / "figures"    # repo-root figures/


def save(fig, name: str, directory: str | Path | None = None) -> None:
    """Write a figure as PNG to the repo's figures/ folder (figures/<name>.png), whatever
    the working directory; pass `directory` to write elsewhere."""
    out = Path(directory) if directory is not None else FIGURES
    out.mkdir(parents=True, exist_ok=True)
    fig.savefig(out / f"{name}.png", dpi=150, bbox_inches="tight")


# --- labels: mathtext throughout, as in the original repo's figures ---------------

DT = r"$\Delta t$"
DT_TR = r"$\Delta t / t_R$"
DT_STAR = r"$\Delta t^*$"
PL = r"$p_L$"
RATE = r"logical error rate per unit time $R$"


def dl(d: int) -> str:
    """Distance label, e.g. '$d = 5$'."""
    return rf"$d = {d}$"


def idle_label(key: str) -> str:
    """Premise-study idle keys -> readable mathtext."""
    return {"lin 0.3": r"linear, $\gamma = 0.3\,p_2$",
            "quad 0.01": r"quadratic, $c = 0.01\,p_2$",
            "mixed": r"mixed, $\gamma = 0.3\,p_2,\ c = 0.01\,p_2$"}.get(key, key)
