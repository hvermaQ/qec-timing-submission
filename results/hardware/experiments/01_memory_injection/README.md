# 01 · Memory with noise injection

**Question.** Does noise injected inside a Guppy program behave the same on the emulator as in Stim?

**Program.** d = 3 surface-code memory, X basis, 2 rounds, one reused ancilla.
Two versions: `d3_X_r2_p0` (no injection) and `d3_X_r2_p0.05` (Z on each data qubit with p = 0.05 per round).

**Runs.** H2-1E, 100 shots each.

**Result.**

| Program | Logical failures | Stim |
| --- | --- | --- |
| p0 | 0/100 raw, 2/100 decoded | — |
| p0.05 | 6/100 decoded | 7.2% |

Injection works end to end. The 2/100 with no injection came from a decoder that did not know
the emulator's own noise.

**Files.** `results/hardware/programs/d3_X_r2_*`, `results/hardware/emulator_runs.md`, `emulator_runs.png`.
