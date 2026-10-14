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
