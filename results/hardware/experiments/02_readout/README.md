# 02 · Readout error

**Question.** What are the readout errors p_meas0 (read 1 given 0) and p_meas1 (read 0 given 1)?

**Program.** 8 qubits measured in |0⟩, 8 flipped to |1⟩ and measured (`readout.bc`).

**Runs.** H2-1E, 100 shots (800 samples each).

**Result.** p_meas0 = p_meas1 = 2/800 = 0.25% (± 0.18%), consistent with the emulator's 0.06% / 0.14%.

**Files.** `results/hardware/calibration_programs/readout.*`, `h2_1e_calibration_runs.fit.json`, `.png`.
