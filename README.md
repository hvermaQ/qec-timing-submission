# QEC timing: from model to physical experiment

Team Q_SQUARED (Q_SQ): Harshit Verma, Harshank Shrotriya, and Ilesh Vora.

We investigate **how often to extract error syndromes while storing a logical state**. Longer waits allow memory errors to accumulate; more frequent extraction adds circuit errors. The project developed in stages: first we studied the trade-off in models and simulations, then tested injected-noise programs on H2 emulators, and finally used explicit QIR `sleep` instructions in experiments on emulators and physical H2 hardware.

The earlier results are part of the argument, not a separate project: they establish the model, identify the role of circuit noise and decoding, and motivate the final tests with real wait instructions. The final-round measurements extend that work, with the timing and decoder caveats documented below.

## Research arc

| Step | Question | What it established | Evidence |
| --- | --- | --- | --- |
| 1. Idling in applications | How much time do logical qubits spend idle? | Sequential workloads leave qubits idle for much of their runtime: 84–87% for a ripple-carry adder and 41–51% for a QFT, mostly in long stretches. | `./run_idle_importance.sh`, notebook 01 |
| 2. Paper's model | Can the model of Haug, Bharti & Aolita be reproduced with noise injected inside a device program? | Guppy with injected noise agrees with Stim at 18 of 18 points; the slope of 1/Δt* versus distance is 0.385 ± 0.013, compared with 0.402 in the paper. | `./run_approach_A.sh`, notebook 02 |
| 3. Circuit-level noise | Does an optimal interval survive native gates, gate errors, and linear or quadratic idle dephasing? | An interior optimum appears in all 18 simulated curves at d = 3, 5, 7. A once-calibrated model predicts Δt* within 10–20%; decoder and memory basis matter. | `./run_approach_B.sh`, notebooks 03–07 |
| 4. Regime and payoff | When does waiting pay on H2-like rates, and can it replace code distance? | For short rounds, the optimal interval at distance d can outperform back-to-back extraction at d + 2. The gain fades as idle error per round approaches two-qubit error. | Notebooks 08–09 |
| 5. Injected-noise emulator tests | How do injected-noise programs compare across Stim and H2 emulators? | The d = 5 H2-2E sweep is consistent with a gate-level model; emulator studies also informed the design of the explicit-wait experiments. | [`hardware/`](hardware/README.md), hardware notebooks and reports |
| 6. Final round | How does the timing trade-off appear with explicit waits on emulators and physical H2? | The final-round folder documents the experiments, analyses, decoder choices, and job-level evidence. | [Final-round README](SG_final_round/README.md) |

This progression is important when interpreting the results: the injected-noise work tests models and analysis, while the final round tests explicit sleep instructions. The [final-round README](SG_final_round/README.md) gives the experiment details and interpretation.

## Final-round materials

**Judges:** Start with the [final-round README](SG_final_round/README.md), which guides you through the experiments, results, and execution records.

- **[Final report (PDF)](Quantinuum_SG_challenge_final_report.pdf):** The final written report for the Quantinuum SG challenge.
- **[Final-phase presentation (PowerPoint)](SG%20Grand%20Challenge%20-%20Presentation_16_Nov.pptx):** Slide deck presenting the QEC timing problem, our experimental approach, and final-phase results.
- **[Final-phase one-pager (PDF)](SG_One_Pager_Revised_v6_16_Nov.pdf):** A concise overview of the project and its main findings. The [editable Word version](SG_One_Pager_Revised_v6.docx) is also available.

| What you want to review | Where to go |
| --- | --- |
| Experiment design, measured quantity, and timing interpretation | [What was measured](SG_final_round/README.md#what-was-measured) |
| Emulator experiments and supporting reports | [Emulator experiments](SG_final_round/README.md#emulator-experiments) |
| Physical H2-1 and H2-2 experiments | [Physical hardware experiments](SG_final_round/README.md#physical-hardware-experiments) |
| Physical H2-2 distance-5 results, with per-setting job IDs and raw data | [Distance-5 hardware data](SG_final_round/README.md#distance-5-data-collected-on-the-physical-h2-2-device) |
| Decoder policies and interpretation of results | [Decoding and interpretation](SG_final_round/README.md#decoding-and-interpretation) |
| Verify execution IDs, platforms, raw payloads, and hashes | [How judges can verify job IDs](SG_final_round/README.md#how-judges-can-verify-job-ids) |
| Find code, configurations, programs, and saved results | [Final-round folder guide](SG_final_round/README.md#folder-guide) |
| Run local structural checks | [Local checks](SG_final_round/README.md#local-checks) |

### Simple emulator example

[`run_simple_emulator.py`](SG_final_round/src/run_simple_emulator.py) runs an end-to-end **T_sleep=1 s, N=2, d=3 X-memory** experiment on H2-1E: build the circuit, syntax-check it, execute it, collect shots, and decode logical errors. It saves job records, raw results, and an analysis summary.

```sh
python3 SG_final_round/src/run_simple_emulator.py --shots 100
```

Requires authenticated Aqora, NumPy, Stim, PyMatching, and clang. Execution uses emulator credits; add `--build-only` for a local build without submission. See the [full instructions](SG_final_round/README.md#simple-end-to-end-emulator-example).

### Selected final-round reports

- **Distance-3 emulator sweep:** [13,000-shot report](SG_final_round/results/d3_fixed_sleep_all_shots.md).
- **Distance-5 emulator sweep:** [logical-error report and execution-job ledger](SG_final_round/results/d5_h2_1e_sleep_logical_probabilities.md).
- **Physical H2-2 distance-3 sweep:** [updated-decoder report, including the zero-sleep control](SG_final_round/results/h2_2_hardware_p_ext_0_00117_10750_shots.md).
- **Physical H2-2 distance-5 sweeps:** [original-mapping analysis](SG_final_round/results/d5_h2_2_t1_p_ext_0_004_3500_shots.json), [skip-index-5 summary for N=2,3,4,6](SG_final_round/results/d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json), and [later N=10 analysis](SG_final_round/runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json). The final-round README explains the separate mappings and decoder policies.

## Earlier-phase methods and evidence

The sections below document the models, software, and analyses behind steps 1–5. The work continues in [`SG_final_round/`](SG_final_round/), which records the explicit-sleep experiments on emulators and physical H2.

The [final report](Quantinuum_SG_challenge_final_report.pdf) presents these stages as one account. One command per earlier result is listed in [`REPRODUCE.md`](REPRODUCE.md).

## The `qec-timing` package

Optimal syndrome-measurement timing for QEC memories, after Haug, Bharti & Aolita (2026).
A package built from interfaces: codes, noise models, backends, decoders and applications
are swappable, and every implementation is checked against the same contracts.

The simulation and emulator studies established the modeling and analysis used in the final
round. In-program noise injection agreed with Stim, the d = 5 emulator sweep was consistent with
a gate-level model, and spectator-qubit studies informed the later explicit-wait experiments.
See [`SG_final_round/`](SG_final_round/) for the emulator and physical-H2 results.

**Start here:** *Claims and evidence* below (every claim, its evidence and its level), the notebooks in
`notebooks/` (figures in `figures/`), the scripts in *Running* below, and `REPRODUCE.md` (one command per result).
The notebooks run in two arcs:
- **simulation, 01–10 (run locally):** idle in applications (01); the paper's model, Guppy vs Stim (02);
  dephasing needs the X basis (03); realistic circuit noise (04–06); how the optimum moves
  with idle strength (07); the regime on H2-1E rates (08); the payoff, time for space (09);
  the program's size and cost as QIR (10);
- **hardware, 11–15 (H2 emulators, `hardware/`):** the device program checked end to end
  (11), measuring the device's idle noise and feeding it back (12), the hardware experiments
  drawn, with their syntax checks (13), noise injection on the H2 emulators: injection check and
  the d = 5 Δt sweep (14), gauging the idle parameters with spectator qubits (15).

Retired notebooks (kept for the record, not part of the argument) are in `notebooks/retired/`.
Hardware experiments, one short README each: `results/hardware/experiments/`.

## Running

**Simulations (notebooks 01–10): three scripts at the top level**, one per part of the story,
all local. Each runs the studies, then executes the matching notebooks (figures go to
`figures/`). Set up the environments first (*Setup* below). Simulations are stored in `store/`
by a hash of their full specification, so a rerun only decodes what is already there and an
interrupted run resumes.

| Script | What it answers | Notebooks | Time from scratch |
| --- | --- | --- | --- |
| `./run_idle_importance.sh` | Why idling matters: idle share of applications (adder 84–87%, QFT 41–51%); when waiting at d beats back-to-back rounds at d + 2 | 01, 09 | ~1 h |
| `./run_approach_A.sh` | Approach (A): the paper's model with noise injected in a Guppy program, against Stim; 1/Δt* vs d; what the program costs as QIR | 02, 10 | ~15 min |
| `./run_approach_B.sh` | Approach (B): native gates, gate noise and idle dephasing (γ, c); the optimum under circuit noise (Fig. 1), the Δt* map (Fig. 2), H2's regime | 03–08 | ~2 h |

Options, as environment variables: `WORKERS=16` (parallel workers, default 8),
`NOTEBOOKS=0` (studies only), `PY=...` (another interpreter). Examples:

```bash
./run_approach_A.sh
```
```bash
WORKERS=16 NOTEBOOKS=0 ./run_approach_B.sh
```

**Hardware (notebooks 11–15): [`hardware/`](hardware/README.md)**, one script per step, so the
one that spends credits can't run by accident:

| Step | Does | Cost |
| --- | --- | --- |
| `hardware/1_build.sh` | every program as QIR (byte for byte the committed ones), contract check on local Selene | free |
| `hardware/2_check.sh` | the planned programs through the H2-1SC / H2-2SC syntax checkers | free |
| `hardware/3_submit.sh [--confirm]` | prints the run plan (47 emulator jobs); with `--confirm`, runs it on H2-1E / H2-2E | **credits** |
| `hardware/4_collect.sh` | returned jobs in `store/hardware/` → the summaries in `results/hardware/` | free |
| `hardware/5_analyse.sh` | executes notebooks 11–15 on those summaries | free |

Each step after 1 takes experiment names to run part of the plan (`hardware/3_submit.sh
dt_sweep_d5`). `collect` reproduces the committed hardware summaries from the stored jobs; what
is exact and what is a seeded model prediction is listed in [`hardware/README.md`](hardware/README.md).

## Claims and evidence

Every claim the repo makes, where the evidence is, which judging criterion it
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

### Problem & Value (30%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| V1 | In sequential FT workloads most logical-qubit time is idle, mostly in long stretches (adder 84–87%, 93% in stretches ≥ 10 steps; QFT 41–51%); local workloads (Ising) are not. | notebook 01; `results/idle/idle.json`; `tests/test_apps.py` (equal to original notebook 10) | 4 |
| V2 | Large resource estimates already treat idle storage as a cost to engineer (yoked codes, Gidney 2025). | external: arXiv 2505.15917, 2312.04522 (notebook 01) | 5 (external) |
| V3 | For short rounds (t_R ≤ 4 ms for d = 3→5, ≤ 2 ms for 5→7 on H2-1E rates), the optimal interval at d beats back-to-back extraction at d + 2: time replaces a distance step (16–24 data qubits per logical qubit). For longer rounds the gain (×2–12 up to 30 ms) is smaller than a step. | notebook 09; `results/regime/grid/` | 3 (simulation at emulator rates) |
| V4 | The memory extracts Δt* times less often per unit time: proportionally fewer two-qubit gates and measurements (the cost drivers). | notebook 09 (rates); notebook 10 (program size ∝ rounds × checks) | 3 |
| V5 | The benefit has a boundary: none once idle error per round approaches p2 (H2-1E: from t_R ≈ 50–150 ms, earlier at larger d). | notebook 08 | 4 |

### Technical Performance & Hardware Use (30%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| T1 | The noise model injected in a Guppy program (as a device program) agrees with Stim on the paper's model: 18/18 points, χ² p = 0.51, no bias (−1.9σ). | notebook 02; `results/crosscheck/`; `python -m qec_timing.validation.crosscheck` | 5 (two independent implementations + original Stage 4a reference, p = 0.92) |
| T2 | Under realistic circuit noise (gates, uniform idle on data and ancillas, native gates), every curve keeps an interior optimum (18/18). | notebook 04; `results/premise/` | 4 |
| T3 | On H2-1E's own rates, waiting pays ×15–45 at t_R = 1–2 ms, ×1.4–1.9 at 30 ms; back to back is best from 50 ms (d = 7), 70 ms (d = 5) and 150 ms (d = 3). The optimal period stays near 50–95 ms while rounds are shorter. | notebook 08; `results/regime/grid/` (39 cells) | 3 (emulator parameters; t_R and the quadratic-rate convention assumed) |
| T4 | The hardware program is built from the code interface, validated as QIR, byte-identical to the original Stage 7a program, and passes the backend contract on local Selene end to end. | notebook 11; `tests/test_hardware.py`; `results/hardware/programs/` | 4 |
| T5 | Submission path used end to end through aqora (organisation `q_sq`): syntax check, submit, fetch, store; every request and response kept verbatim; credit spend gated by `--confirm`. ~55 syntax-check and ~50 emulator job records on H2-1E / H2-2E (in `store/hardware/`). The submission path enforces the per-job cost cap (largest accepted ~800 two-qubit gates × 1000 shots). | `qec_timing.hardware.cli`; `results/hardware/syntax_checks.md`; `results/hardware/experiments/` | 4 |
| T6 | Program size and cost scale linearly in rounds × checks; d ≤ 7 fits H2's 56 qubits. | notebook 10; `results/hardware/qir_scaling.json` | 4 |
| T7 | Noise injected inside the device program behaves the same on the H2-1E emulator as in Stim: d = 3 memory, every detector rate and the decoded p_L (6/100 against 7.2%) agree. | notebook 14; `results/hardware/h2_1e_memory_d3.json` | 3 (100 shots) |
| T8 | The trade-off persists under device-grade emulator noise: at the three measured points of a d = 5 H2-2E sweep (1000 shots per point), logical error rates are within ~1σ of the gate-level model with H2-2E's published gate errors; the U-curve is higher and flatter (minimum ≈ 0.16 near Δt ≈ 1, against ≈ 0.13 for the paper's model). | notebook 14; `results/hardware/h2_2e_dt_sweep_d5*.json`; `hardware/program_model.py` | 3 (three-point emulator comparison) |

### Scientific Merit (20%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| S1 | Reproduces the paper's central scaling: 1/Δt* = (0.385 ± 0.013) d − 0.92 for d = 5–11, against the paper's slope 0.402 (1.3σ); Δt* approaches Eq. 6 as d grows (+38% at d = 5 to +11% at d = 11). | notebook 02; `results/scaling/`; `tests/test_new_studies.py` | 5 (paper as benchmark) |
| S2 | Novel beyond the paper: the premise tested under circuit-level noise. The paper's two-parameter model, calibrated **once** at back-to-back rounds, predicts Δt* to +15–20% (d=3), +1–10% (d=5), −5…+3% (d=7); p_read and p_data hold to < 0.8%. | notebook 04; `results/premise/` | 4 |
| S3 | Limits found and stated: the model underestimates p_L more with d (use it for Δt*, not p_L); effective g ≈ 0.54–0.74 at d = 3–7 (paper 0.8, fitted at d = 11–27); Z-basis memories are blind to trapped-ion idling. | notebooks 03, 04, 07 | 4 |
| S3b | Data qubits are not equal: per-round error varies ~3× across the lattice; 16–17% spreads from ancillas with native gates (7–9% textbook). | notebook 05; `results/per_qubit/` | 4 |
| S3c | The decoder decides the answer: the paper's phenomenological graph raises p_L up to 3.1× (d = 7) and moves Δt* about threefold; all circuit-level results decode with the full DEM. | notebook 06; `results/decoders/` | 4 |
| S3d | Δt* follows the power laws the ansatz implies (slopes −1.00…−1.05 against −1, −0.48…−0.49 against −0.5) with idle noise on every qubit; with the idle term composed as the circuit applies it, the calibrated ansatz predicts a held-out mixed-noise simulation to within 1.6–3.2%, giving the Δt* map over the idle plane. Idle on every qubit lengthens Δt* by 1–16% against data-only idle. | notebook 07; `results/idle_scaling/idle_scaling_uniform.json` (data-only reference equal to original notebook 07) | 5 (held-out test) |
| S3e | On emulator data too, the decoder must know the circuit: decoding the d = 3 noise-only run on the paper's graph creates 2/100 failures where the raw data have none; a gate-level model of the hardware program (one reused ancilla, serial checks) gives the DEM used for the d = 5 sweep. | notebook 14; `results/hardware/h2_1e_memory_d3.json`, `h2_2e_dt_sweep_d5_circuit_decoder.json` | 3 |
| S3f | Spectator-qubit studies tested anchored waits on the emulator; measured X- and Z-basis error rates were ≈1.2% and ≈0.45%, respectively, and informed the explicit-sleep experiments in the final round. | notebook 15; `results/hardware/h2_1e_*idle*.json`; [final-round experiments](SG_final_round/README.md) | 2 |
| S4 | Exact regressions against prior results: circuit-level failure counts identical at the same seeds (18/18), full-circuit Δt* identical at all 18 settings. | `tests/test_circuit.py`; `results/premise/README.md` | 5 |
| S5 | A statistical pitfall found and fixed: overlapping per-shot seeds faked a −3.5σ bias; the package now refuses them. | `results/crosscheck/README.md`; `tests/test_core.py` | 4 |

### Engineering & Reproducibility (20%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| E1 | Package built on interfaces (codes, noise, backends, decoders, extractors, idle sources); a new code needs only the code interface (repetition and Steane codes run through the same sampler). | `README.md`; `src/qec_timing/`; `tests/fixtures/toy.py` | 4 |
| E2 | Contract tests for every interface, each tested against a deliberately broken implementation. | `qec_timing.testing.contracts`; `tests/test_contracts.py` | 4 |
| E3 | Three pinned environments; tests pass in each (core, main, H2). | `envs/`; `REPRODUCE.md`; `results/test_runs/` | 4 |
| E4 | Every run stored with manifest, versions, git commit, checksums; derived results name their inputs; atomic writes. | `qec_timing.store`; `tests/test_store.py` | 4 |
| E5 | One command per result; notebooks are thin clients over stored results. | `REPRODUCE.md`; `notebooks/` | 4 |

## Final-round hardware experiments

The final round takes the modeling and emulator work to explicit QIR sleep experiments on
emulators and physical H2 hardware. See [`SG_final_round/`](SG_final_round/) for experiment
protocols, results, decoder policies, and job-level records.

## Where results and data live

| What | Where | In git? |
| --- | --- | --- |
| Summary of each study (numbers behind every figure) | `results/<study>/` (`crosscheck`, `scaling`, `premise`, `per_qubit`, `decoders`, `idle_scaling`, `regime`, `idle`, `effective`) | yes |
| Hardware programs (QIR bitcode + metadata) | `results/hardware/programs/`, `results/hardware/calibration_programs/` | yes |
| Hardware results and fits | `results/hardware/*.json`, `results/hardware/syntax_checks.md`, `emulator_runs.md`, `job_ids.md` (top level) | yes |
| Hardware write-ups, one per experiment | `results/hardware/experiments/` | yes |
| Figures | `figures/` (written by the notebooks) | yes |
| Raw simulation runs (detection events, manifests, checksums) | `store/runs/<run_id>/` | no (`store/` is gitignored) |
| Derived results with lineage | `store/derived/<id>/` | no |
| Raw hardware jobs (program sent, job record, provider result verbatim) | `store/hardware/<time>_<provider>_<program>_<platform>/` | no |
| Device parameters | `config/*.json` (with sources) | yes |

The local, gitignored `store/` directory (64 GB in the original experiment workspace) holds
4,768 simulation runs. **These raw runs are not included in a repository clone.** Each run keeps
every shot's detection events
(`raw/detectors.npy`) and logical outcomes (`raw/observables.npy`), along with a manifest that
records the full spec, the seed, the code commit, the package versions and a SHA-256 checksum
for every file. The local store also contains 81 returned emulator jobs with the program that
was sent and the provider's result verbatim (`store/hardware/*/result_0.txt`). Tracked summaries
and selected analysis artifacts are under `results/`. Because decoding is a separate step,
**any other decoder** (another matching weighting, belief propagation, union-find, a
leakage-aware or neural decoder) can be run on the same shots without simulating or
submitting anything again.

## Experiments on the role of the decoder

| Experiment | Finding | Where |
| --- | --- | --- |
| Paper's graph vs the circuit's full DEM, same detection events (simulation) | the simple graph raises p_L up to 3.1× (d = 7) and moves Δt* about threefold | notebook 06; `results/decoders/` |
| One-calibration model vs full circuit (simulation) | the model places Δt* well but underestimates p_L more with d; all circuit-level results decode with the full DEM | notebook 04; `results/premise/` |
| Per-qubit error sources (simulation) | errors differ ~3× across the lattice and spread from ancillas: structure a uniform model misses | notebook 05; `results/per_qubit/` |
| Emulator, noise-only memory (H2-1E) | decoding on the paper's graph creates 2/100 failures where the raw data have none | notebook 14; `results/hardware/h2_1e_memory_d3.json` |
| Emulator, d = 5 sweep (H2-2E) | a gate-level model of the hardware program supplies the DEM; decoder choice moves p_L by ≤ 0.006 there, the device's gate noise explains the rest | notebook 14; `results/hardware/h2_2e_dt_sweep_d5_circuit_decoder.json`; `hardware/program_model.py` |

## Setup

Three environments, pinned in `envs/`. Tests that need another env skip.

| env | file | Python | contains | runs |
| --- | --- | --- | --- | --- |
| `.venv` | `envs/core.txt` | 3.12 | numpy, pytest | interfaces, store, contracts, fits |
| `.venv-main` | `envs/main.txt` | 3.12 | + Guppy 1.x/Selene, Stim, PyMatching, scipy, pytket | simulations and studies |
| `.venv-h2` | `envs/h2.txt` | 3.11 | Guppy 0.21, hugr-qir, qnexus, aqora | hardware programs and submission |

The H2 env is separate because hugr-qir 0.1.2 (QIR for H2) needs guppylang 0.21, while the
simulations use guppylang 1.x. The package core (numpy only) imports in all three.

Hardware access: log in once with `.venv-h2/bin/aqora login`; submissions run as an aqora
organisation (`--as-entity`). Syntax checkers (`*SC`) execute nothing; emulator runs spend credits
and need `--confirm`.

```bash
uv venv --python 3.12 .venv-main
uv pip sync --python .venv-main/bin/python envs/main.txt
uv pip install --python .venv-main/bin/python --no-deps -e .
.venv-main/bin/python -m pytest              # add -m "not slow" to skip Guppy builds
```

## Architecture

```
MemorySpec ──Backend──▶ RawRecord ──Extractor──▶ EffectiveModel ──Analysis──▶ Derived
(code, basis,             (detectors,               (p_data, p_read,            (dt*, Γ,
 schedule, noise,          observables,              λ, b_read, DEM)             U-curves)
 shots, seed)              per-round noise)
                    every arrow writes to the Store, and every output names its inputs
```

| Module | Interface | What it is |
| --- | --- | --- |
| `codes/base.py` | `StabilizerCode`, `Check` | CSS code, k = 1: checks with extraction order, logicals |
| `noise/base.py` | `NoiseModel`, `PhenomenologicalNoise` | per-round p_data / p_read (paper Eqs. 1–3), or circuit-level |
| `schedule.py` | `Schedule` | round intervals as integer ticks (no float drift) |
| `spec.py` | `MemorySpec` | one experiment; validated on construction; content-hashed run id |
| `backends/base.py` | `Backend` | simulator or hardware adapter: spec in, raw record out |
| `decoders/base.py` | `Decoder`, `DecoderFactory` | DEM in, logical-flip predictions out |
| `pipeline.py` | `Extractor`, `Analysis` | raw → effective model; stored items → derived result |
| `records.py` | `RawRecord`, `EffectiveModel`, `Derived` | the three data levels; detector layout; bit packing |
| `store.py` | `Store` | run directories with manifest, checksums and lineage |
| `hardware/calibration.py` | `Calibration` | device parameters: the hand-off from hardware to the regime study |
| `apps/base.py` | `IdleSource`, `IdleProfile` | idle stretches of logical qubits in an application |
| `registry.py` | `register`, `create` | name → factory, per kind |
| `testing/contracts.py` | `check_*` | what every implementation must satisfy |

Notebooks and scripts are clients of the package: they call it, read the store and plot.
They hold no logic of their own.

## Implementations

| Kind | Name | Module | Notes |
| --- | --- | --- | --- |
| code | `rotated_surface` | `codes/surface.py` | both sectors; Z checks and logical Z identical to the original repo |
| noise | `paper` | `noise/paper.py` | Eqs. 1-3, static λ; X (bit-flip) or Z (dual sector) |
| backend | `stim_phenom` | `backends/stim_phenom.py` | production path; any CSS code, either basis |
| backend | `guppy_phenom` | `backends/guppy_phenom.py` | validation path; noise injected in-program; either basis; constant dt |
| decoder | `pymatching` | `decoders/pymatching_decoder.py` | MWPM from the run's own DEM |
| noise | `circuit` | `noise/circuit.py` | gate, readout, reset + idle (linear/quadratic dephasing, depolarizing); `from_calibration` |
| noise | `effective` | `noise/effective.py` | the paper's model with measured p_data(1), p_read and an idle wait |
| backend | `stim_circuit` | `backends/stim_circuit.py` | textbook circuit (Stim generated), aligned to `RotatedSurfaceCode` |
| backend | `stim_native` | `backends/stim_native.py` | Selene's native gates mirrored into Stim |
| extractor | `edges` | `extract/edges.py` | p_data, p_read (and space / diagonal parts) from detection events |
| hardware | memory program | `hardware/qir.py` | Guppy 0.21 memory experiment → validated QIR; in-program injection of p_data(Δt) |
| hardware | idle programs | `hardware/calibration_experiments.py` | readout, spectator idle (measure-reset, transport, anchored), fits |
| hardware | program model | `hardware/program_model.py` | the hardware program in Stim gate for gate: decoder (DEM) and p_L prediction |
| hardware | record flips | `hardware/records.py` | `add_record_flips`: the paper's p_read added to returned bits |
| plotting | circuit diagrams | `diagrams.py` | schematic and circuit drawings of the hardware programs |

## Studies

Each is a module with a CLI; every run goes to the store, the summary to `results/`.

| Command | Question | Output |
| --- | --- | --- |
| `python -m qec_timing.validation.crosscheck` | Do Guppy (noise injected in-program) and Stim agree on the paper's model? | `results/crosscheck/` |
| `python -m qec_timing.studies.premise --gates textbook\|native` | Does a circuit with realistic noise reduce to the paper's model, and is dt* predictable from one calibration? | `results/premise/` |
| `python -m qec_timing.studies.regime --calibration FILE --t-round ...` | On a device with these parameters, does waiting between rounds pay, and how much? | `results/regime/` |
| `python -m qec_timing.studies.idle` | How much time do logical qubits idle in compiled applications, in what stretches? | `results/idle/` |
| `python -m qec_timing.studies.scaling` | Does 1/Δt* grow linearly with d with the paper's slope? | `results/scaling/` |
| `python -m qec_timing.studies.effective` | What λ and b_read does a real extraction circuit have, against the paper's assumed values? | `results/effective/` |
| `python -m qec_timing.studies.per_qubit` | How unequal are data qubits' errors per round, and where do they come from? | `results/per_qubit/` |
| `python -m qec_timing.studies.decoders` | Does decoding with the paper's graph instead of the circuit's full error model change the answer? | `results/decoders/` |
| `python -m qec_timing.studies.idle_scaling` | How does Δt* move with idle strength (power laws, calibrated ansatz, Δt* map with a held-out test)? | `results/idle_scaling/` |
| `python -m qec_timing.hardware.cli ...` (H2 env) | Build (`build`, `calib-build --transport\|--anchored`), check locally, syntax-check (`aqora-check`), run (`aqora-submit --confirm`), fit (`calib-fit`) | `results/hardware/`, `config/` |
| `python -m qec_timing.hardware.cli collect` (main env) | What do the returned emulator jobs give: decoded failures, idle fits, model predictions? | `results/hardware/` |

**Regression against the original repo.** The circuit-level backends reproduce the
original notebooks' cached failure counts exactly (same circuits, same seeds): 12/12
sampled runs of notebooks 07/08 (textbook) and 6/6 of 09 (native gates, recompiled with
selene-sim 0.3.2). Two such cases are pinned in `tests/test_circuit.py`.

## Extending the repo

The package is modular: each piece of the experiment is an interface, so it can be swapped
without touching the others. The same studies, store and notebooks then run on:
- **other codes**: any CSS code with one logical qubit (colour codes, other surface-code
  layouts, small qLDPC patches) through the code interface;
- **other noise models**: new idle laws, correlated or time-dependent noise (e.g. bursts);
- **other decoders**: union-find, belief propagation, leakage-aware or neural decoders,
  also on the stored raw shots without re-simulating;
- **other backends and devices**: further simulators, or another provider's hardware behind
  the backend interface;
- **other applications**: new idle profiles for the idle-fraction study.

To add a component:

1. Implement the protocol in a new module (e.g. `codes/color.py`).
2. Register it: `@register("code", "color")`.
3. Add a test that runs the contract: `contracts.check_code(ColorCode(d=5))`.

Example: `tests/fixtures/toy.py` implements a repetition code and the Steane code. The
same generic sampler runs both with no code-specific logic. That is the test of the
code interface.

| Contract | Catches |
| --- | --- |
| `check_code` | anticommuting checks, logicals that anticommute with a check or act trivially, bad extraction orders |
| `check_backend` | detections without noise, a seed that doesn't reach the noise, detectors out of layout order, noise applied at a different rate than reported (e.g. two draws instead of one) |
| `check_phenomenological_noise` | non-deterministic or non-probability outputs |
| `check_decoder` | wrong shapes or types, flips predicted from silence |
| `check_idle_source` | inconsistent profiles |

Each contract is also tested against a deliberately broken implementation
(`tests/test_contracts.py`), so a contract that silently passes everything would fail.

## Data

`Store(root)` writes `runs/<run_id>/{manifest.json, raw/, model/}` and
`derived/<id>/derived.json`. Raw data is written once, with checksums. Manifests
record the spec, backend versions and code commit. `check_lineage` flags results
built on runs from different code. `store/` is gitignored; canonical runs are added
explicitly.

## References

Device specifications (Quantinuum):
- [Performance validation](https://docs.quantinuum.com/systems/user_guide/hardware_user_guide/performance_validation.html):
  per-machine benchmarks for H2-1, H2-2 and Helios-1, including memory (idle) error per depth-1
  circuit time, gate, SPAM, leakage and crosstalk errors.
- [H2 product data sheet](https://docs.quantinuum.com/systems/_static/assets/data_sheets/Quantinuum%20H2%20Product%20Data%20Sheet.pdf).
