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
| V3 | For short rounds (t_R ≤ 4 ms for d = 3→5, ≤ 2 ms for 5→7 on H2-1E rates), the optimal interval at d beats back-to-back extraction at d + 2: time replaces a distance step (16–24 data qubits per logical qubit). For longer rounds the gain (×2–12 up to 30 ms) is smaller than a step. | notebook 02; `results/regime/grid/` | 3 (simulation at emulator rates; device t_R unknown) |
| V4 | The memory extracts Δt* times less often per unit time: proportionally fewer two-qubit gates and measurements (the cost drivers). | notebook 02 (rates); notebook 04 (program size ∝ rounds × checks) | 3; HQC price pending syntax checker |
| V5 | The benefit has a boundary: none once idle error per round approaches p2 (H2-1E: from t_R ≈ 50–150 ms, earlier at larger d). | notebook 08 | 4 |

## Technical Performance & Hardware Use (30%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| T1 | The noise model injected in a Guppy program (as a device program) agrees with Stim on the paper's model: 18/18 points, χ² p = 0.51, no bias (−1.9σ). | notebook 03; `results/crosscheck/`; `python -m qec_timing.validation.crosscheck` | 5 (two independent implementations + original Stage 4a reference, p = 0.92) |
| T2 | Under realistic circuit noise (gates, uniform idle on data and ancillas, native gates), every curve keeps an interior optimum (18/18). | notebook 06; `results/premise/` | 4 |
| T3 | On H2-1E's own rates, waiting pays ×15–45 at t_R = 1–2 ms, ×1.4–1.9 at 30 ms; back to back is best from 50 ms (d = 7), 70 ms (d = 5) and 150 ms (d = 3). The optimal period stays near 50–95 ms while rounds are shorter. | notebook 08; `results/regime/grid/` (39 cells) | 3 (emulator parameters; t_R and the quadratic-rate convention assumed) |
| T4 | The hardware program is built from the code interface, validated as QIR, byte-identical to the original Stage 7a program, and passes the backend contract on local Selene end to end. | notebook 05; `tests/test_hardware.py`; `results/hardware/programs/` | 4 |
| T5 | Submission path ready: syntax check / cost / submit / fetch / store, every request and response kept verbatim, credit spend gated by `--confirm`. | `qec_timing.hardware.cli`; `results/hardware/README.md` | 2 (not yet executed: provider-side outage) |
| T6 | Program size and cost scale linearly in rounds × checks; d ≤ 7 fits H2's 56 qubits. | notebook 04; `results/hardware/qir_scaling.json` | 4 |

## Scientific Merit (20%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| S1 | Reproduces the paper's thresholds (within 0.5–2%, finite size explained) and 1/Δt* slope (1.0σ). | original research repo: `docs/stub_arc/stage1_report.md`, `stage4a_report.md`; **not re-run in this repo** (the threshold study was not ported) | 4 there; 1 here until ported |
| S2 | Novel beyond the paper: the premise tested under circuit-level noise. The paper's two-parameter model, calibrated **once** at back-to-back rounds, predicts Δt* to +15–20% (d=3), +1–10% (d=5), −5…+3% (d=7); p_read and p_data hold to < 0.8%. | notebook 06; `results/premise/` | 4 |
| S3 | Limits found and stated: the model underestimates p_L more with d (use it for Δt*, not p_L); effective g ≈ 0.70 at small d (paper 0.8); Z-basis memories are blind to trapped-ion idling. | notebooks 06, 07; original Stage 4a | 4 |
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

- Nothing has run on hardware or the hosted emulator yet. Every device number is either an
  emulator default or a scan over an unknown (t_R).
- No adaptive controller (paper Appendix F) or burst λ(t) (Eq. 9).
- Codes beyond CSS with one logical qubit; decoders beyond PyMatching (the interface takes others).
