"""QIR program builders for the sleep experiments.

Each builder returns a `Build`: the folder name under results/sleep/programs/ and the QIR
text of every variant, computed in memory exactly as the original scripts did (CONFIG
literals and QIR code are verbatim). `Build.verify()` compares that text with the committed
`.ll` files without writing anything; `materialize` functions in each module write a *new*
build folder (and need clang) but never touch an existing one.

    probe          build_sleep_probe.py: one sleep in the pinned d=3 baseline (5944..., 8cca...)
    single_qubit   single_qubit_pilot.py / single_qubit_sweep.py
    d3_sweep       d3_sleep_sweep.py: two-round d=3, all-data sleep block (3- and 5-point)
    d3             fixed_sleep_d3.py (coarse / refinement / resolution) and the d=3 H2-2 zero-sleep control
    d5             fixed_sleep_d5.py, the d=5 zero-sleep controls, the half-second sweep and
                   the skip-index-5 H2-2 programs
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .. import paths


@dataclass(frozen=True)
class Build:
    name: str                                   # folder under results/sleep/programs/
    texts: dict                                 # variant -> QIR text (variant.ll)
    config: dict | None = None                  # hashed CONFIG, where the folder name has one
    plan: list | None = None                    # job split, where the original had a PLAN
    hashed: bool = True                         # False: fixed folder name (no hash to reproduce)
    extra: dict = field(default_factory=dict)   # builder-specific facts (rounds, run folder, ...)

    @property
    def folder(self) -> Path:
        return paths.PROGRAMS / self.name

    @property
    def runs(self) -> Path:
        """Run folder of the sweeps whose runs are named after the build."""
        return paths.RUNS / self.name

    def verify(self) -> dict:
        """{variant: True/False/None}: regenerated text == committed .ll (None: .ll missing)."""
        out = {}
        for variant, text in self.texts.items():
            ll = self.folder / (variant + '.ll')
            out[variant] = paths.read_text(ll) == text if ll.exists() else None
        return out


def all_builds() -> list[Build]:
    """One Build per folder in results/sleep/programs/ (probe 98ff... has text only; see probe)."""
    from . import d3, d3_sweep, d5, probe, single_qubit
    builds = [single_qubit.pilot(), single_qubit.sweep(),
              d3_sweep.sweep('three_point'), d3_sweep.sweep('five_point', 'nexus:H2-1E'),
              d3_sweep.sweep('five_point', 'nexus:H2-2E'),
              d3.fixed('coarse'), d3.fixed('refinement'), d3.fixed('resolution'), d3.zero_sleep_h2_2(),
              d5.fixed(), d5.half_second(), *d5.zero_sleep_controls().values(),
              d5.zero_sleep_n3_skip5(), *d5.skip5_t1().values()]
    builds += [probe.from_folder(folder) for folder in probe.FOLDERS]
    return builds
