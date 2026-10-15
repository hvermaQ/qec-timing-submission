# 04 · Δt sweep, d = 5 (the trade-off with device noise)

**Question.** Does the optimal syndrome interval survive the emulator's own gate and readout noise?

**Program.** d = 5 memory, X basis, fixed total time T = 10, R = T/Δt rounds. Before each round each
data qubit gets Z with the paper's p_data(Δt) (p = 0.015, λ = 1). Readout flips (p_read = 0.015)
are added to the returned bits afterwards.

**Runs.** H2-2E, 1000 shots per point.

**Result.**

| Δt | Emulator p_L | Model with H2-2E gate noise | Paper model only |
| --- | --- | --- | --- |
| 0.14 (R = 70) | rejected (job cost over the cap) | 0.24 | 0.25 |
| 0.5 (R = 20) | finished, result not returned by aqora | 0.18 | 0.14 |
| 1 (R = 10) | 0.173 | 0.159 | 0.133 |
| 2.5 (R = 4) | 0.172 | 0.173 | 0.156 |
| 5 (R = 2) | 0.191 | 0.208 | 0.198 |

The emulator matches a circuit model of the program that includes its gate noise (within ~1σ).
Each round now costs more, so the U-curve is higher and flatter.

**Files.** `results/hardware/programs/d5_X_r*`, `h2_2e_dt_sweep_d5*.json`, `.png`;
model: `src/qec_timing/hardware/program_model.py`.
