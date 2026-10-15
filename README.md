# Info:

#TEAM Q_SQUARED or Q_SQ for short. Members: Harshit Verma, Harshank Shrotriya and Ilesh Vora.

Full repo available on https://github.com/hvermaQ/qec-timing-submission

Data available on request

# qec-timing

Optimal syndrome-measurement timing for QEC memories, after Haug, Bharti & Aolita (2026).
A package built from interfaces: codes, noise models, backends, decoders and applications
are swappable, and every implementation is checked against the same contracts.

**Status.** Simulation arc complete (notebooks 01–09). Hardware arc: programs built, checked
locally and on the H2 syntax checkers, and run on Quantinuum's H2-1E / H2-2E emulators through
aqora (organisation `q_sq`); no device is available to this account. Results so far:
in-program noise injection agrees with Stim on the emulator; a d = 5 Δt sweep on H2-2E follows a
circuit model of the program that includes H2-2E's gate noise; spectator experiments see no
consistent idle dephasing up to 128 layers (below ~0.5%). Open: two sweep points (one result not
returned by aqora, one over the per-job cost limit), linear vs quadratic idle growth, and a
leakage-heralded decoder (the QIR toolchain cannot compile leakage-aware measurement).

**Start here:** *Claims and evidence* below (every claim, its evidence and its level), the notebooks in
`notebooks/` (figures in `figures/`), the scripts in *Running* below, and `REPRODUCE.md` (one command per result).
The notebooks run in two arcs:
- **simulation, 01–09:** idle in applications (01); the paper's model, Guppy vs Stim (02);
  dephasing needs the X basis (03); realistic circuit noise (04–06); how the optimum moves
  with idle strength (07); the regime on H2-1E rates (08); the payoff, time for space (09);
- **hardware, 10–15:** program size and cost (10), the device program checked end to end
  (11), measuring the device's idle noise and feeding it back (12), the hardware experiments
  drawn, with their syntax checks (13), noise injection on the H2 emulators: injection check and
  the d = 5 Δt sweep (14), gauging the idle parameters with spectator qubits (15).

Retired notebooks (kept for the record, not part of the argument) are in `notebooks/retired/`.
Hardware experiments, one short README each: `results/hardware/experiments/`.

## Running

Four scripts at the top level, one per part of the story. Each runs the studies, then
executes the matching notebooks (figures go to `figures/`). Set up the environments first
(*Setup* below). Simulations are stored in `store/` by a hash of their full specification,
so a rerun only decodes what is already there and an interrupted run resumes.

| Script | What it answers | Notebooks | Time from scratch |
| --- | --- | --- | --- |
| `./run_idle_importance.sh` | Why idling matters: idle share of applications (adder 84–87%, QFT 41–51%); when waiting at d beats back-to-back rounds at d + 2 | 01, 09 | ~1 h |
| `./run_approach_A.sh` | Approach (A): the paper's model with noise injected in a Guppy program, against Stim; 1/Δt* vs d | 02 | ~15 min |
| `./run_approach_B.sh` | Approach (B): native gates, gate noise and idle dephasing (γ, c); the optimum under circuit noise (Fig. 1), the Δt* map (Fig. 2), H2's regime | 03–08 | ~2 h |
| `./run_hardware.sh <step>` | Hardware experiments on the H2 emulators through aqora | 10–15 | see below |

Options, as environment variables: `WORKERS=16` (parallel workers, default 8),
`NOTEBOOKS=0` (studies only), `PY=...` (another interpreter). Examples:

```bash
./run_approach_A.sh
```
```bash
WORKERS=16 NOTEBOOKS=0 ./run_approach_B.sh
```

`run_hardware.sh` runs in steps, so nothing costs credits by accident:

| Step | Does | Needs | Cost |
| --- | --- | --- | --- |
| `build` | every program as QIR, a contract check on local Selene, program-size scaling | H2 env | free |
| `check` | every program through the H2-1SC / H2-2SC syntax checkers (validates, executes nothing) | aqora login | free |
| `submit` | prints the run plan (experiment, program, emulator, shots) and stops | — | free |
| `submit --confirm` | runs the plan: d = 3 memory (H2-1E), d = 5 Δt sweep (H2-2E), anchored idle (H2-1E) | aqora login | **credits** |
| `analyse` | executes notebooks 10–15 on the results in `results/hardware/` | main env | free |

Log in once with `.venv-h2/bin/aqora login`; jobs run as the organisation in `ENTITY`
(default `q_sq`). `build` rewrites the committed programs byte for byte. Two limits are known:
R = 70 at 1000 shots exceeds aqora's per-job cost cap, and the returned jobs land in
`store/hardware/`, but turning them into the summary files in `results/hardware/` is not
yet scripted (notebooks 14–15 read those summaries).

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
| V3 | For short rounds (t_R ≤ 4 ms for d = 3→5, ≤ 2 ms for 5→7 on H2-1E rates), the optimal interval at d beats back-to-back extraction at d + 2: time replaces a distance step (16–24 data qubits per logical qubit). For longer rounds the gain (×2–12 up to 30 ms) is smaller than a step. | notebook 09; `results/regime/grid/` | 3 (simulation at emulator rates; device t_R unknown) |
| V4 | The memory extracts Δt* times less often per unit time: proportionally fewer two-qubit gates and measurements (the cost drivers). | notebook 09 (rates); notebook 10 (program size ∝ rounds × checks) | 3; HQC price pending syntax checker |
| V5 | The benefit has a boundary: none once idle error per round approaches p2 (H2-1E: from t_R ≈ 50–150 ms, earlier at larger d). | notebook 08 | 4 |

### Technical Performance & Hardware Use (30%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| T1 | The noise model injected in a Guppy program (as a device program) agrees with Stim on the paper's model: 18/18 points, χ² p = 0.51, no bias (−1.9σ). | notebook 02; `results/crosscheck/`; `python -m qec_timing.validation.crosscheck` | 5 (two independent implementations + original Stage 4a reference, p = 0.92) |
| T2 | Under realistic circuit noise (gates, uniform idle on data and ancillas, native gates), every curve keeps an interior optimum (18/18). | notebook 04; `results/premise/` | 4 |
| T3 | On H2-1E's own rates, waiting pays ×15–45 at t_R = 1–2 ms, ×1.4–1.9 at 30 ms; back to back is best from 50 ms (d = 7), 70 ms (d = 5) and 150 ms (d = 3). The optimal period stays near 50–95 ms while rounds are shorter. | notebook 08; `results/regime/grid/` (39 cells) | 3 (emulator parameters; t_R and the quadratic-rate convention assumed) |
| T4 | The hardware program is built from the code interface, validated as QIR, byte-identical to the original Stage 7a program, and passes the backend contract on local Selene end to end. | notebook 11; `tests/test_hardware.py`; `results/hardware/programs/` | 4 |
| T5 | Submission path used end to end through aqora (organisation `q_sq`): syntax check, submit, fetch, store; every request and response kept verbatim; credit spend gated by `--confirm`. ~55 syntax-check and ~50 emulator job records on H2-1E / H2-2E (in `store/hardware/`). Limits met: a per-job cost cap (largest accepted ~800 two-qubit gates × 1000 shots), one completed job whose result aqora never returned. | `qec_timing.hardware.cli`; `results/hardware/syntax_checks.md`; `results/hardware/experiments/` | 4 |
| T6 | Program size and cost scale linearly in rounds × checks; d ≤ 7 fits H2's 56 qubits. | notebook 10; `results/hardware/qir_scaling.json` | 4 |
| T7 | Noise injected inside the device program behaves the same on the H2-1E emulator as in Stim: d = 3 memory, every detector rate and the decoded p_L (6/100 against 7.2%) agree. | notebook 14; `results/hardware/h2_1e_memory_d3.json` | 3 (100 shots) |
| T8 | The trade-off survives device-grade noise: a d = 5 Δt sweep on H2-2E (1000 shots per point) follows a gate-level model of the program with H2-2E's published gate errors within ~1σ at all three returned points; the U-curve is higher and flatter (minimum ≈ 0.16 near Δt ≈ 1, against ≈ 0.13 for the paper's model). | notebook 14; `results/hardware/h2_2e_dt_sweep_d5*.json`; `hardware/program_model.py` | 3 (3 of 5 points; left arm model only) |

### Scientific Merit (20%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| S1 | Reproduces the paper's central scaling: 1/Δt* = (0.385 ± 0.013) d − 0.92 for d = 5–11, against the paper's slope 0.402 (1.3σ); Δt* approaches Eq. 6 as d grows (+38% at d = 5 to +11% at d = 11). | notebook 02; `results/scaling/`; `tests/test_new_studies.py` | 5 (paper as benchmark) |
| S1b | Reproduces the paper's thresholds (within 0.5–2%, finite size explained). | original research repo, `docs/stub_arc/stage1_report.md`; not ported here | 4 there; 1 here |
| S2 | Novel beyond the paper: the premise tested under circuit-level noise. The paper's two-parameter model, calibrated **once** at back-to-back rounds, predicts Δt* to +15–20% (d=3), +1–10% (d=5), −5…+3% (d=7); p_read and p_data hold to < 0.8%. | notebook 04; `results/premise/` | 4 |
| S3 | Limits found and stated: the model underestimates p_L more with d (use it for Δt*, not p_L); effective g ≈ 0.54–0.74 at d = 3–7 (paper 0.8, fitted at d = 11–27); Z-basis memories are blind to trapped-ion idling. | notebooks 03, 04, 07 | 4 |
| S3b | Data qubits are not equal: per-round error varies ~3× across the lattice; 16–17% spreads from ancillas with native gates (7–9% textbook). | notebook 05; `results/per_qubit/` | 4 |
| S3c | The decoder decides the answer: the paper's phenomenological graph raises p_L up to 3.1× (d = 7) and moves Δt* about threefold; all circuit-level results decode with the full DEM. | notebook 06; `results/decoders/` | 4 |
| S3d | Δt* follows the power laws the ansatz implies (slopes −1.00…−1.05 against −1, −0.48…−0.49 against −0.5) with idle noise on every qubit; with the idle term composed as the circuit applies it, the calibrated ansatz predicts a held-out mixed-noise simulation to within 1.6–3.2%, giving the Δt* map over the idle plane. Idle on every qubit lengthens Δt* by 1–16% against data-only idle. | notebook 07; `results/idle_scaling/idle_scaling_uniform.json` (data-only reference equal to original notebook 07) | 5 (held-out test) |
| S3e | On emulator data too, the decoder must know the circuit: decoding the d = 3 noise-only run on the paper's graph creates 2/100 failures where the raw data have none; a gate-level model of the hardware program (one reused ancilla, serial checks) gives the DEM used for the d = 5 sweep. | notebook 14; `results/hardware/h2_1e_memory_d3.json`, `h2_2e_dt_sweep_d5_circuit_decoder.json` | 3 |
| S3f | Idling on the emulator, measured with spectator qubits: targets must be anchored to the start of the wait (otherwise a scheduler can prepare them late and they never idle in |+⟩); anchored targets show no consistent dephasing up to 128 spectator layers (X basis ≈ 1.2%, Z ≈ 0.45%; any idle error < 0.5%). γ and c are not yet resolved. | notebook 15; `results/hardware/h2_1e_*idle*.json` | 2 (an upper bound; longer waits refused by the cost cap) |
| S4 | Exact regressions against prior results: circuit-level failure counts identical at the same seeds (18/18), full-circuit Δt* identical at all 18 settings. | `tests/test_circuit.py`; `results/premise/README.md` | 5 |
| S5 | A statistical pitfall found and fixed: overlapping per-shot seeds faked a −3.5σ bias; the package now refuses them. | `results/crosscheck/README.md`; `tests/test_core.py` | 4 |
| S6 | Related work: optimal number of rounds for an idling patch (arXiv 2408.07529). | to be compared in the write-up | 1 |

### Engineering & Reproducibility (20%)

| # | Claim | Evidence | Level |
| --- | --- | --- | --- |
| E1 | Package built on interfaces (codes, noise, backends, decoders, extractors, idle sources); a new code needs only the code interface (repetition and Steane codes run through the same sampler). | `README.md`; `src/qec_timing/`; `tests/fixtures/toy.py` | 4 |
| E2 | Contract tests for every interface, each tested against a deliberately broken implementation. | `qec_timing.testing.contracts`; `tests/test_contracts.py` | 4 |
| E3 | Three pinned environments; tests pass in each (core, main, H2). | `envs/`; `REPRODUCE.md`; `results/test_runs/` | 4 |
| E4 | Every run stored with manifest, versions, git commit, checksums; derived results name their inputs; atomic writes. | `qec_timing.store`; `tests/test_store.py` | 4 |
| E5 | One command per result; notebooks are thin clients over stored results. | `REPRODUCE.md`; `notebooks/` | 4 |

### Not claimed

- Nothing has run on a device: this account sees only emulators (H2-1E, H2-2E) and syntax
  checkers. Device numbers are emulator defaults, or a scan over the unknown round time t_R,
  which aqora does not report. Published depth-one times (55–68 ms on H2 / Helios) suggest
  current surface-code rounds of ~100–250 ms, at or past the back-to-back boundary of T3: an
  estimate, not a measurement.
- No leakage-heralded decoding: the QIR toolchain (hugr-qir 0.1.2, 0.3.0) cannot compile
  leakage-aware measurement; the gate-level leakage gadget is designed, not built.
- No adaptive controller (paper Appendix F) or burst λ(t) (Eq. 9).
- Codes beyond CSS with one logical qubit; decoders beyond PyMatching. Both interfaces take
  others, and the stored raw shots can be re-decoded (see *Where results and data live*).

## Next experiments on hardware

Ordered: each step needs the one before it. Programs for 1–3 reuse the spectator builders in
`hardware/calibration_experiments.py`; 5–6 reuse the memory program in `hardware/qir.py`.

1. **Confirm the qubits really idle.** A scheduler can move gates so that a "waiting" qubit is
   prepared late (as soon as possible, ASAP) or measured early (as late as possible, ALAP), so it never
   waits in a sensitive state. Run the same wait in three forms: anchored at the start (prepare,
   entangle with an anchor, wait), anchored at the end (wait, then entangle before measuring),
   and both. If the scheduler removes the wait, the singly anchored forms show less error
   than the doubly anchored one. Where the toolchain offers an explicit delay or sleep
   instruction, compare it to the spectator-layer wait, and check the compiled circuit
   returned by the provider for the wait.
2. **Separate linear from quadratic idle noise.** Once the wait is confirmed, sweep the wait
   length L over a wide range and fit the X-basis error to γτ ⊕ sin²(√c τ): the log-log slope
   is 1 for linear (Markovian) noise and 2 for quadratic (coherent drift) at short times. Add
   an echo (an X halfway through the wait): it cancels slow coherent phase drift but not
   Markovian dephasing, so echo vs no echo splits c from γ directly. Z-basis spectators
   are the control (no dephasing expected).
3. **Measure the round time t_R.** Time the memory program from job metadata, or from runs of
   1, 2, 4, … rounds on a device. This places the device on the Δt* map (notebook 07) and
   fixes the regime (notebook 08).
4. **Finish the d = 5 Δt sweep.** Recover the R = 20 result (aqora did not return it); split
   R = 70 into jobs under the cost cap.
5. **Real waits instead of injected noise.** Repeat the sweep with no injection: the wait
   between rounds is a real idle (spectator layers or a delay instruction), so the device's own
   idle noise sets p_data(Δt). Compare the measured Δt* with the map's prediction from 1–3.
6. **Leakage-aware decoding.** Build the gate-level leakage-detection gadget (the QIR
   toolchain cannot compile `measure_leaked`), herald leaked qubits per round, and give the
   decoder those erasures.
7. **Error surges (the paper's burst model, Eq. 9).** Bursts of raised noise λ(t) over a
   window: first injected in-program with a time-dependent p_data (the injection path already
   takes per-round rates), then searched for on a device as jumps in the detection-event
   rate over a long run. With bursts present, test the paper's adaptive controller
   (Appendix F): shorten the interval when the detection rate rises, against a fixed Δt.
8. **Larger distance.** d = 7 needs 50 qubits with the one-ancilla program (H2: 56), so the
   1/Δt* ∝ d scaling can be checked on H2 or Helios.

## Where results and data live

| What | Where | In git? |
| --- | --- | --- |
| Summary of each study (numbers behind every figure) | `results/<study>/` (`crosscheck`, `scaling`, `premise`, `per_qubit`, `decoders`, `idle_scaling`, `regime`, `idle`, `effective`) | yes |
| Hardware programs (QIR bitcode + metadata) | `results/hardware/programs/`, `results/hardware/calibration_programs/` | yes |
| Hardware results and fits | `results/hardware/*.json`, `emulator_runs.md`, `syntax_checks.md` | yes |
| Hardware write-ups, one per experiment | `results/hardware/experiments/` | yes |
| Figures | `figures/` (written by the notebooks) | yes |
| Raw simulation runs (detection events, manifests, checksums) | `store/runs/<run_id>/` | no (`store/` is gitignored) |
| Derived results with lineage | `store/derived/<id>/` | no |
| Raw hardware jobs (program sent, job record, provider result verbatim) | `store/hardware/<time>_<provider>_<program>_<platform>/` | no |
| Device parameters | `config/*.json` (with sources) | yes |

**All raw data are kept, so every result can be reproduced or re-decoded.** `store/` (64 GB, not
in git) holds 4,768 simulation runs. Each run keeps every shot's detection events
(`raw/detectors.npy`) and logical outcomes (`raw/observables.npy`), along with a manifest that
records the full spec, the seed, the code commit, the package versions and a SHA-256 checksum
for every file. The 81 returned emulator jobs keep the program that was sent and the provider's
result verbatim (`store/hardware/*/result_0.txt`). Because decoding is a separate step,
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
Neither hugr-qir 0.1.2 nor 0.3.0 can lower leakage-aware measurement (`measure_leaked`) to QIR.

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
