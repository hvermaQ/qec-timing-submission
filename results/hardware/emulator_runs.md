# H2-1E emulator runs (2026-10-14)

Submitted through aqora as organisation `q_sq` (`hardware.cli aqora-submit --confirm`), 100 shots
each, H2-1E's full noise model (aqora cannot set emulator options). d = 3 rotated surface code,
X basis, 2 rounds, one reused ancilla. Raw job records: `store/hardware/*_H2-1E/` (local).
aqora reports `duration: 2` for both jobs: wall-clock of the emulation, not a physical round time.

| program | injected Z per data qubit per round | detector rate | shots with any detection | logical X flips, undecoded | logical failures, decoded | Stim, injection only (200k shots) |
| --- | --- | --- | --- | --- | --- | --- |
| d3_X_r2_p0 | 0 | 0.005 | 3/100 | 0/100 | 2/100 | — |
| d3_X_r2_p0.05 | 0.05 | 0.085 | 65/100 | 26/100 | 6/100 | p_L 0.072, detector rate 0.091 |

Decoding: PyMatching on the paper's phenomenological graph (p_data = injected p, or 2e-3 with no
injection; p_read = 1e-3). With injection, the emulator agrees with Stim within the statistics
(6/100 against 7.2%; 95% interval for 6/100 is 2–13%), so in-program noise injection works end to
end on the emulator. Without injection, decoding turns 0 raw flips into 2 failures: the emulator's
own errors (readout, hook, leakage) are not on the phenomenological graph, so the decoder needs the
emulator's error model, not this graph.

![H2-1E runs](emulator_runs.png)

## Calibration programs (readout, spectator idle L = 0-64), 100 shots each

All 15 jobs COMPLETED on H2-1E (`q_sq`). Fit: `h2_1e_calibration_runs.fit.json` (`hardware.cli calib-fit`).

| test | result | H2-1E model value |
| --- | --- | --- |
| readout p_meas0 / p_meas1 | 2/800 = 2.5(18)e-3 each | 0.6e-3 / 1.39e-3 (consistent) |
| X-basis idle, L = 0..64 | flip rate 0-0.25% at every L, no growth (0/800 at L = 64: < 0.37%, 95%) | — |
| Z-basis idle, L = 0..64 | 0-0.25%, flat | Z-only idle: flat |

Reading: up to 64 spectator layers produce no detectable dephasing. With the emulator's own rates
(f = 86 mHz, gamma = 2.8e-3 /s) a 1% flip needs about 0.4 s of idling, so 64 layers of
measure-and-reset are far shorter than that, or the layers are not executed as idle time. Neither
can be told apart at this depth; the grid has to reach ~10^3-10^4 layers (or a known layer duration).

![H2-1E calibration runs](h2_1e_calibration_runs.png)

Grey lines: the emulator idle model for an assumed layer duration (1, 3.4, 10 ms). 0/800 at L = 64 rules out
layers of about 3.4 ms or longer (if the layers are executed as idle time).
