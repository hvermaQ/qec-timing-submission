# Claims and their evidence

Every claim the submission makes, where the evidence is, which judging criterion it
serves, and the evidence level on the judges' scale. Levels are our own honest reading:

| level | meaning |
| --- | --- |
| 0 | no evidence |
| 1 | assertion only |
| 2 | plausible, limited proof |
| 3 | demonstrated with direct evidence |
| 4 | measured and repeatable |
| 5 | validated against a benchmark, user need, or external reference |

Labels in the notebooks: *measured* (computed in this repo), *paper* (Haug, Bharti & Aolita
2026), *interp.* (our reading).

## Problem & Value (30%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| V1 | In sequential FT workloads most logical-qubit time is idle, mostly in long stretches (adder 84–87%, 93% in stretches ≥ 10 steps; QFT 41–51%); local workloads (Ising) are not. | notebook 01; `results/idle/idle.json`; `tests/test_apps.py` (equal to original notebook 10) | 4 |
| V2 | Large resource estimates already treat idle storage as a cost to engineer (yoked codes, Gidney 2025). | external: arXiv 2505.15917, 2312.04522 (notebook 01) | 5 (external) |
| V3 | For short rounds (t_R ≤ 4 ms for d = 3→5, ≤ 2 ms for 5→7 on H2-1E rates), the optimal interval at d beats back-to-back extraction at d + 2: time replaces a distance step (16–24 data qubits per logical qubit). For longer rounds the gain (×2–12 up to 30 ms) is smaller than a step. | notebook 09; `results/regime/grid/` | 3 (simulation at emulator rates; device t_R unknown) |
| V4 | The memory extracts Δt* times less often per unit time: proportionally fewer two-qubit gates and measurements (the cost drivers). | notebook 09 (rates); notebook 10 (program size ∝ rounds × checks) | 3; HQC price pending syntax checker |
| V5 | The benefit has a boundary: none once idle error per round approaches p2 (H2-1E: from t_R ≈ 50–150 ms, earlier at larger d). | notebook 08 | 4 |

## Technical Performance & Hardware Use (30%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| T1 | The noise model injected in a Guppy program (as a device program) agrees with Stim on the paper's model: 18/18 points, χ² p = 0.51, no bias (−1.9σ). | notebook 02; `results/crosscheck/`; `python -m qec_timing.validation.crosscheck` | 5 (two independent implementations + original Stage 4a reference, p = 0.92) |
| T2 | Under realistic circuit noise (gates, uniform idle on data and ancillas, native gates), every curve keeps an interior optimum (18/18). | notebook 04; `results/premise/` | 4 |
| T3 | On H2-1E's own rates, waiting pays ×15–45 at t_R = 1–2 ms, ×1.4–1.9 at 30 ms; back to back is best from 50 ms (d = 7), 70 ms (d = 5) and 150 ms (d = 3). The optimal period stays near 50–95 ms while rounds are shorter. | notebook 08; `results/regime/grid/` (39 cells) | 3 (emulator parameters; t_R and the quadratic-rate convention assumed) |
| T4 | The hardware program is built from the code interface, validated as QIR, byte-identical to the original Stage 7a program, and passes the backend contract on local Selene end to end. | notebook 11; `tests/test_hardware.py`; `results/hardware/programs/` | 4 |
| T5 | Submission path used end to end through aqora (organisation `q_sq`): syntax check, submit, fetch, store; every request and response kept verbatim; credit spend gated by `--confirm`. 40+ syntax checks and 30+ emulator jobs on H2-1E / H2-2E. Limits met: a per-job cost cap (largest accepted ~800 two-qubit gates × 1000 shots), one completed job whose result aqora never returned. | `qec_timing.hardware.cli`; `results/hardware/syntax_checks.md`; `results/hardware/experiments/` | 4 |
| T7 | Noise injected inside the device program behaves the same on the H2-1E emulator as in Stim: d = 3 memory, every detector rate and the decoded p_L (6/100 against 7.2%) agree. | notebook 14; `results/hardware/h2_1e_memory_d3.json` | 3 (100 shots) |
| T8 | The trade-off survives device-grade noise: a d = 5 Δt sweep on H2-2E (1000 shots per point) follows a gate-level model of the program with H2-2E's published gate errors within ~1σ at all three returned points; the U-curve is higher and flatter (minimum ≈ 0.16 near Δt ≈ 1, against ≈ 0.13 for the paper's model). | notebook 14; `results/hardware/h2_2e_dt_sweep_d5*.json`; `hardware/program_model.py` | 3 (3 of 5 points; left arm model only) |
| T6 | Program size and cost scale linearly in rounds × checks; d ≤ 7 fits H2's 56 qubits. | notebook 10; `results/hardware/qir_scaling.json` | 4 |

## Scientific Merit (20%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| S1 | Reproduces the paper's central scaling: 1/Δt* = (0.385 ± 0.013) d − 0.92 for d = 5–11, against the paper's slope 0.402 (1.3σ); Δt* approaches Eq. 6 as d grows (+38% at d = 5 to +11% at d = 11). | notebook 02; `results/scaling/`; `tests/test_new_studies.py` | 5 (paper as benchmark) |
| S1b | Reproduces the paper's thresholds (within 0.5–2%, finite size explained). | original research repo, `docs/stub_arc/stage1_report.md`; not ported here | 4 there; 1 here |
| S2 | Novel beyond the paper: the premise tested under circuit-level noise. The paper's two-parameter model, calibrated **once** at back-to-back rounds, predicts Δt* to +15–20% (d=3), +1–10% (d=5), −5…+3% (d=7); p_read and p_data hold to < 0.8%. | notebook 04; `results/premise/` | 4 |
| S3 | Limits found and stated: the model underestimates p_L more with d (use it for Δt*, not p_L); effective g ≈ 0.54–0.74 at d = 3–7 (paper 0.8, fitted at d = 11–27); Z-basis memories are blind to trapped-ion idling. | notebooks 03, 04, 07 | 4 |
| S3b | Data qubits are not equal: per-round error varies ~3× across the lattice; 16–17% spreads from ancillas with native gates (7–9% textbook). | notebook 05; `results/per_qubit/` | 4 |
| S3c | The decoder decides the answer: the paper's phenomenological graph raises p_L up to 3.1× (d = 7) and moves Δt* about threefold; all circuit-level results decode with the full DEM. | notebook 06; `results/decoders/` | 4 |
| S3e | On emulator data too, the decoder must know the circuit: decoding the d = 3 noise-only run on the paper's graph creates 2/100 failures where the raw data have none; a gate-level model of the hardware program (one reused ancilla, serial checks) gives the DEM used for the d = 5 sweep. | notebook 14; `results/hardware/h2_1e_memory_d3.json`, `h2_2e_dt_sweep_d5_circuit_decoder.json` | 3 |
| S3f | Idling on the emulator, measured with spectator qubits: targets must be anchored to the start of the wait (otherwise a scheduler can prepare them late and they never idle in |+⟩); anchored targets show no consistent dephasing up to 128 spectator layers (X basis ≈ 1.2%, Z ≈ 0.45%; any idle error < 0.5%). γ and c are not yet resolved. | notebook 15; `results/hardware/h2_1e_*idle*.json` | 2 (an upper bound; longer waits refused by the cost cap) |
| S3d | Δt* follows the power laws the ansatz implies (slopes −1.00…−1.05 against −1, −0.48…−0.49 against −0.5) with idle noise on every qubit; with the idle term composed as the circuit applies it, the calibrated ansatz predicts a held-out mixed-noise simulation to within 1.6–3.2%, giving the Δt* map over the idle plane. Idle on every qubit lengthens Δt* by 1–16% against data-only idle. | notebook 07; `results/idle_scaling/idle_scaling_uniform.json` (data-only reference equal to original notebook 07) | 5 (held-out test) |
| S4 | Exact regressions against prior results: circuit-level failure counts identical at the same seeds (18/18), full-circuit Δt* identical at all 18 settings. | `tests/test_circuit.py`; `results/premise/README.md` | 5 |
| S5 | A statistical pitfall found and fixed: overlapping per-shot seeds faked a −3.5σ bias; the package now refuses them. | `results/crosscheck/README.md`; `tests/test_core.py` | 4 |
| S6 | Related work: optimal number of rounds for an idling patch (arXiv 2408.07529). | to be compared in the write-up | 1 |

## Engineering & Reproducibility (20%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| E1 | Package built on interfaces (codes, noise, backends, decoders, extractors, idle sources); a new code needs only the code interface (repetition and Steane codes run through the same sampler). | `README.md`; `src/qec_timing/`; `tests/fixtures/toy.py` | 4 |
| E2 | Contract tests for every interface, each tested against a deliberately broken implementation. | `qec_timing.testing.contracts`; `tests/test_contracts.py` | 4 |
| E3 | Three pinned environments; tests pass in each (core, main, H2). | `envs/`; `REPRODUCE.md`; `results/test_runs/` | 4 |
| E4 | Every run stored with manifest, versions, git commit, checksums; derived results name their inputs; atomic writes. | `qec_timing.store`; `tests/test_store.py` | 4 |
| E5 | One command per result; notebooks are thin clients over stored results. | `REPRODUCE.md`; `notebooks/` | 4 |

## Not claimed

- Nothing has run on a device: this account sees only emulators (H2-1E, H2-2E) and syntax
  checkers. Device numbers are emulator defaults, or a scan over the unknown round time t_R,
  which aqora does not report. Published depth-one times (55–68 ms on H2 / Helios) suggest
  current surface-code rounds of ~100–250 ms, at or past the back-to-back boundary of T3: an
  estimate, not a measurement.
- No leakage-heralded decoding: the QIR toolchain (hugr-qir 0.1.2, 0.3.0) cannot compile
  leakage-aware measurement; the gate-level leakage gadget is designed, not built.
- No adaptive controller (paper Appendix F) or burst λ(t) (Eq. 9).
- Codes beyond CSS with one logical qubit; decoders beyond PyMatching (the interface takes others).
