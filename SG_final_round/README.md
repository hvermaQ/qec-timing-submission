# Final round: timing quantum error correction on Quantinuum H2

This folder contains the final-round experiments investigating **how often to extract error syndromes while storing a logical state**. Longer waits allow memory errors to accumulate; more frequent extraction adds circuit errors. We test this tradeoff on Quantinuum emulators and physical hardware using explicit QIR `sleep` instructions between extraction rounds.

This guide reflects the artifacts saved through **15 November 2026**. Job states below are saved snapshots; live provider states may have advanced.

## Start here

- **Distance-3 emulator timing sweep:** [all-shot report](results/d3_fixed_sleep_all_shots.md), with 13,000 shots on H2-1E.
- **Distance-5 emulator timing sweep:** [logical-error report and execution-job ledger](results/d5_h2_1e_sleep_logical_probabilities.md), with 10,167 completed shots on H2-1E across the one-second and half-second protocols.
- **Physical H2-2 distance-3 timing sweep:** [updated-decoder report](results/h2_2_hardware_p_ext_0_00117_10750_shots.md), with 9,750 fixed-sleep shots and 1,000 zero-sleep control shots.
- **Physical H2-2 distance-5, original mapping:** [completed 3,500-shot analysis](results/d5_h2_2_t1_p_ext_0_004_3500_shots.json) and [750-shot zero-sleep calibration](results/d5_h2_2_zero_sleep_pooled_750.json).
- **Physical H2-2 distance-5, skip-index-5 mapping:** [2,000-shot summary for N=2,3,4,6](results/d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json), plus the [160-shot N=10 analysis](runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json). The tables below link every setting to its execution ID and collected raw data.

The main completed sweeps show improved memory performance at intermediate extraction frequencies. Reported minima are sample minima with overlapping uncertainty at nearby settings; they do not establish a unique optimal interval or distance scaling.

## What was measured

The experiments use the X-memory sector of a rotated surface-code geometry. Data qubits start in `|+>`, undergo repeated X-stabilizer extraction using one reused ancilla, and finish with X-basis readout. Distance 3 uses nine data qubits and four checks per round; distance 5 uses 25 data qubits and twelve checks per round. This probes protection against phase errors in this sector, rather than a full two-sector memory experiment for arbitrary logical states.

For the main timing sweeps, `N` extraction rounds have `N−1` intervening wait blocks. Each data qubit receives a requested wait `u = T_sleep/(N−1)` in each block, keeping its total requested sleep fixed while varying extraction frequency. Barriers bracket the all-data wait blocks. No artificial Pauli faults or offline readout flips are added.

The reported logical error probability is the fraction of complete shots for which final logical-X parity disagrees with the minimum-weight perfect matching (MWPM) decoder's predicted correction. It is distinct from the raw data-bit error probability and is not a per-round or per-second rate.

**Timing interpretation:** early instruction probes report raw sleep arguments. Later fixed-sleep protocols adopt seconds as the requested unit, as recorded in their configurations. Extraction duration is neglected, and simultaneous physical overlap of the individual data-qubit sleep calls remains unverified. Thus a “one-second” experiment means one second of requested sleep per data qubit, not a measured one-second wall-clock circuit duration.

## Emulator experiments

Execution platforms ending in **E** (`H2-1E`, `H2-2E`) are emulators. Platforms ending in **SC** are syntax checkers, whose successful jobs validate acceptance rather than provide noisy memory data.

| Experiment | Scope and saved outcome | Evidence |
|---|---|---|
| Instruction-support probes | Hash-pinned native QIR was modified to compare no sleep, explicit zero sleep, and finite arguments. These builds isolate sleep-instruction support and LLVM compatibility. | [Builder](src/build_sleep_probe.py); historical builds in `programs/98ff453353750ae5/`, `programs/5944c048c1dfdc80/`, and `programs/8cca8353b3f06d18/` |
| Single-qubit H2-1E memory | A 200-shot-per-setting pilot compared no sleep, sleep(0), and sleep(0.5). A subsequent 1,000-shot-per-setting sweep at arguments 0, 0.1, 0.5, 0.75, 1 recorded 0, 1, 21, 55, 92 errors. | [Pilot](results/single_qubit_pilot.md); [sweep](results/single_qubit_sweep_1000.md) |
| Distance-3, two-round H2-1E memory | An initial three-point all-data sweep at 0, 0.5, 1 used 1,000 shots each and recorded 3, 13, 115 decoded failures. A fresh five-point sweep at 0, 0.1, 0.5, 0.75, 1 recorded 3, 4, 16, 46, 115 failures per 1,000 shots. | [Three-point report](results/d3_sleep_sweep_1000.md); [fresh five-point report](results/d3_sleep_five_point_h2_1e_analysis.md) |
| Distance-3 H2-2E replica | The same five-point, two-round protocol recorded 2, 5, 17, 48, 140 decoded failures per 1,000 shots. Detector growth was concentrated across the inserted wait. | [Report](results/d3_sleep_five_point_h2_2e_analysis.md); [comparison PDF](results/sleep_sweep_H2-1e-2e_d_3_results.pdf) |
| Distance-3 H2-1E fixed-sleep sweep | Coarse, refinement, and resolution batches pooled 18 unique jobs and 13,000 shots at `T_sleep=1 s`, with `N=2,3,4,5,6,7,8,10,20,40`. The historical fixed decoder gives a sample minimum of 24/2,000 (1.20%) at N=5, versus 59/500 (11.8%) at N=2 and 43/500 (8.6%) at N=40. | [All-shot report](results/d3_fixed_sleep_all_shots.md); [methodology PDF](results/d3_h2_1e_full_methodology_all_shots.pdf) |
| Distance-5 H2-1E fixed-sleep sweep | Completed one-second data cover N=2 through 10. A half-second sweep requested N=3,4,5,6; only N=3 completed in the report. Across both protocols, 20 execution jobs completed and 34 attempts were rejected. The one-second sample minimum is 17/1,500 (1.13%) at N=5 under the sleep-dependent decoder. | [Report, intervals, and all attempt IDs](results/d5_h2_1e_sleep_logical_probabilities.md) |
| Distance-5 H2-2E requests | One-second sweeps requested N=5,6,7,8,10 and later N=7,8,9,10. All nine execution requests were rejected for exceeding allowed cost; these are not completed measurements. | [First batch](results/d5_fixed_sleep_h2_2e_500_submission.md); [later batch](results/d5_fixed_sleep_h2_2e_renewed_20261105_submission.md) |
| Zero-sleep controls | Repeated N=2 H2-1E controls characterize the extraction/readout background: pooled distance-3 controls contain 3,000 shots and distance-5 controls 2,000 shots. | [Pooled controls and source IDs](results/zero_sleep_pooled_d3_d5.json) |

Noisy emulator execution requested stabilizer simulation with `noisy_simulation=true`, `no_opt=true`, and idle and transport dephasing enabled. Exact options belong to each saved job record. Rejected requests and planned shot allocations are excluded from measured totals.

## Physical hardware experiments

Physical execution platforms are **`nexus:H2-1` and `nexus:H2-2`**, without an E or SC suffix. Hardware jobs request `no_opt=true`; emulator noise switches are not hardware calibration parameters.

| Experiment | Scope and saved outcome | Evidence |
|---|---|---|
| H2-1 distance-3 pilot | N=2, one second of requested sleep, 250 completed shots; 26 decoded failures (10.4%) under its recorded sleep-dependent decoder. | [Job record](runs/h2_1_hardware_d3_x_n2_t1_250/job.json); [analysis](runs/h2_1_hardware_d3_x_n2_t1_250/analysis.json) |
| H2-1 follow-up requests | N=3,5,6,10,20 were requested. The latest saved status snapshot has N=3 running and N=5,6,10,20 cancelled. These settings are not a completed timing curve. | [Status snapshot](runs/h2_1_live_status_20261112.json); [follow-up records](runs/h2_1_hardware_d3_x_t1_followup_20261111/) |
| H2-2 distance-3 timing sweep | Multiple batches completed at N=2,3,4,5,6,10,20,40 with one second of requested sleep: 15 jobs, 9,750 shots. With the updated distance-3 decoder, errors are 4.2% at N=2, a sample minimum of 1.05% at N=4, and 4.8% at N=40. | [10,750-shot report including control](results/h2_2_hardware_p_ext_0_00117_10750_shots.md); [machine-readable provenance](results/h2_2_hardware_p_ext_0_00117_10750_shots.json) |
| H2-2 distance-3 zero-sleep control | N=2, 1,000 shots; 4 logical failures and 21 erroneous data bits out of 9,000. This control informed the current distance-3 decoder baseline. | [Control job](runs/d3_h2_2_zero_sleep_n2_1000_20261112/execute/job.json); control row in the report above |
| H2-2 distance-5 zero-sleep controls | N=2, 500 shots plus a 250-shot repeat. All 25 data qubits are retained without postselection; 157 erroneous data bits out of 18,750 informed the distance-5 decoder baseline. | [Pooled calibration and both job IDs](results/d5_h2_2_zero_sleep_pooled_750.json) |
| H2-2 distance-5 timing sweep, original mapping | All five settings N=2,3,4,6,10 completed: 3,500 shots decoded with p_ext=0.004. Data indices 0–24, ancilla 25; no postselection. | [Analysis and provenance](results/d5_h2_2_t1_p_ext_0_004_3500_shots.json); [execution status](runs/d5_h2_2_t1_20261113/execute_status.json) |
| H2-2 distance-5 timing sweep, skip-index-5 mapping | N=2,3,4,6 completed with 500 shots each, plus N=10 with 160 shots: 2,160 collected shots decoded with p_ext=0.005. Data indices 0–4 and 6–25, ancilla 26; no postselection. | [Four-setting summary](results/d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json); [N=10 analysis](runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json) |
| H2-2 distance-5 N=3 zero-sleep mapping controls | Separate 250-shot controls recorded 220/6,250 raw data-bit errors on the original mapping and 98/6,250 on the skip-index-5 mapping. These diagnostics are separate from the finite-sleep curves and historical N=2 calibration. | [Original mapping](runs/d5_h2_2_zero_sleep_n3_250_20261114/execute/raw_analysis.json); [skip-index-5 mapping](runs/d5_h2_2_zero_sleep_n3_skip5_250_20261114/execute/raw_analysis.json) |

## Distance-5 data collected on the physical H2-2 device

Both datasets below used `nexus:H2-2`, X-memory circuits, and one second of total requested sleep per data qubit. **Keep the mappings and their decoder policies separate.** Index numbers are QIR qubit indices; the mapping change does not establish that a particular physical ion was excluded. Original code-position output labels are preserved: `m5` in the skip-index-5 dataset is still code position 5, mapped to QIR index 6.

### Original mapping: 3,500 shots, p_ext=0.004

Data indices 0–24 and ancilla 25. The [analysis JSON](results/d5_h2_2_t1_p_ext_0_004_3500_shots.json) records each raw/program/DEM hash; the [NPZ](results/d5_h2_2_t1_p_ext_0_004_3500_shots.npz) stores per-shot analysis arrays. Raw data and job metadata are under [runs/d5_h2_2_t1_20261113/execute/](runs/d5_h2_2_t1_20261113/execute/).

| N | Requested interval (s) | Logical failures / shots | Logical error (95% Wilson) | Aqora execution job ID | Job record / collected data |
|---:|---:|---:|---|---|---|
| 2 | 1 | 11/500 | 2.20% (1.23–3.90%) | `AFByb3ZpZGVySm9iAaHUTQhGcgGO8fSCbisVAg` | [job.json](runs/d5_h2_2_t1_20261113/execute/n2/job.json) · [result_0.txt](runs/d5_h2_2_t1_20261113/execute/n2/result_0.txt) |
| 3 | 0.5 | 30/750 | 4.00% (2.82–5.65%) | `AFByb3ZpZGVySm9iAaHUTROCfcK48eiP0_O8zw` | [job.json](runs/d5_h2_2_t1_20261113/execute/n3/job.json) · [result_0.txt](runs/d5_h2_2_t1_20261113/execute/n3/result_0.txt) |
| 4 | 0.333333 | 40/1000 | 4.00% (2.95–5.40%) | `AFByb3ZpZGVySm9iAaHUTRpndcKAy2T8HalnHQ` | [job.json](runs/d5_h2_2_t1_20261113/execute/n4/job.json) · [result_0.txt](runs/d5_h2_2_t1_20261113/execute/n4/result_0.txt) |
| 6 | 0.2 | 12/750 | 1.60% (0.92–2.78%) | `AFByb3ZpZGVySm9iAaHUTSLLenG5kvm2SFFPMQ` | [job.json](runs/d5_h2_2_t1_20261113/execute/n6/job.json) · [result_0.txt](runs/d5_h2_2_t1_20261113/execute/n6/result_0.txt) |
| 10 | 0.111111 | 19/500 | 3.80% (2.45–5.86%) | `AFByb3ZpZGVySm9iAaHUTStFcSCuXIxn3LlfWA` | [job.json](runs/d5_h2_2_t1_20261113/execute/n10/job.json) · [result_0.txt](runs/d5_h2_2_t1_20261113/execute/n10/result_0.txt) |

The sample minimum is 12/750 (1.60%) at N=6. The curve is not monotonic, and these samples do not establish a unique optimum. [Per-qubit raw-error diagnostics](results/figures/d5_h2_2_raw_error_by_qubit.png) and [readout-weight sensitivity analysis](results/d5_h2_2_p_read_sensitivity.md) provide additional context; every data qubit remains included.

### Skip-index-5 mapping: 2,160 shots, p_ext=0.005

Data indices 0–4 and 6–25, unused index 5, and ancilla 26. The [2,000-shot summary](results/d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json) covers N=2,3,4,6 only. The later [N=10 analysis](runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/analysis_p_ext_0_005.json) adds 160 shots; it is not included in that summary file. Each setting's directory contains its own analysis JSON, per-shot NPZ, and exact DEM.

| N | Requested interval (s) | Logical failures / shots | Logical error (95% Wilson) | Aqora execution job ID | Job record / collected data |
|---:|---:|---:|---|---|---|
| 2 | 1 | 12/500 | 2.40% (1.38–4.15%) | `AFByb3ZpZGVySm9iAaHaHrJFdSGVyItCrNYa1Q` | [job.json](runs/d5_h2_2_t1_skip5_n2_n6_20261114/execute/n2/job.json) · [result_0.txt](runs/d5_h2_2_t1_skip5_n2_n6_20261114/execute/n2/result_0.txt) |
| 3 | 0.5 | 5/500 | 1.00% (0.43–2.32%) | `AFByb3ZpZGVySm9iAaHZoizmfhGQ-SDLribvtA` | [job.json](runs/d5_h2_2_t1_skip5_20261114/execute/n3/job.json) · [result_0.txt](runs/d5_h2_2_t1_skip5_20261114/execute/n3/result_0.txt) |
| 4 | 0.333333 | 6/500 | 1.20% (0.55–2.59%) | `AFByb3ZpZGVySm9iAaHZojNudBKadSwOPUbSaA` | [job.json](runs/d5_h2_2_t1_skip5_20261114/execute/n4/job.json) · [result_0.txt](runs/d5_h2_2_t1_skip5_20261114/execute/n4/result_0.txt) |
| 6 | 0.2 | 6/500 | 1.20% (0.55–2.59%) | `AFByb3ZpZGVySm9iAaHaHrnLciGksuSuRYKSIQ` | [job.json](runs/d5_h2_2_t1_skip5_n2_n6_20261114/execute/n6/job.json) · [result_0.txt](runs/d5_h2_2_t1_skip5_n2_n6_20261114/execute/n6/result_0.txt) |
| 10 | 0.111111 | 2/160 | 1.25% (0.34–4.44%) | `AFByb3ZpZGVySm9iAaHdiQNadvGeCDUnixjk7g` | [job.json](runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/job.json) · [result_0.txt](runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/result_0.txt) |

N=10 has only two observed failures and a wide sampling interval. Earlier N=10 submission/retry records without collected payloads are not additional data. In particular, the batch's `execute_status.json` describes the original rejected 250-shot attempt; the completed 160-shot result is in `shots160/n10/`. Follow the exact record links above rather than inferring completion from a batch name or planned allocation.

The zero-sleep controls can be audited independently:

| Mapping / control | Shots | Aqora execution job ID | Job record / collected data |
|---|---:|---|---|
| Original, N=2 | 500 | `AFByb3ZpZGVySm9iAaHTkCk8cmCs3HYizx6LiQ` | [job.json](runs/d5_h2_2_zero_sleep_n2_500_20261113/execute/job.json) · [result_0.txt](runs/d5_h2_2_zero_sleep_n2_500_20261113/execute/result_0.txt) |
| Original, N=2 repeat | 250 | `AFByb3ZpZGVySm9iAaHT7TgXfYOpdKlZsyUfeg` | [job.json](runs/d5_h2_2_zero_sleep_n2_250_repeat_20261113/execute/job.json) · [result_0.txt](runs/d5_h2_2_zero_sleep_n2_250_repeat_20261113/execute/result_0.txt) |
| Original, N=3 | 250 | `AFByb3ZpZGVySm9iAaHZOpqEddO2XFOSuLeXNA` | [job.json](runs/d5_h2_2_zero_sleep_n3_250_20261114/execute/job.json) · [result_0.txt](runs/d5_h2_2_zero_sleep_n3_250_20261114/execute/result_0.txt) |
| Skip-index-5, N=3 | 250 | `AFByb3ZpZGVySm9iAaHZaESAcwCVLDEccgwFew` | [job.json](runs/d5_h2_2_zero_sleep_n3_skip5_250_20261114/execute/job.json) · [result_0.txt](runs/d5_h2_2_zero_sleep_n3_skip5_250_20261114/execute/result_0.txt) |

## Decoding and interpretation

Historical reports retain the decoder used for that analysis. The early distance-3 reports use fixed phenomenological weights (`p_data=0.002`, `p_read=0.001`). Later analyses also use sleep-dependent weights, combining extraction noise with linear and quadratic idle contributions. These are decoder assumptions, not additional faults injected into the experiment. Fit and redecoding scripts in `src/` explore model dependence; their outputs are separately labeled in `results/`.

For new **physical H2-2** analyses, the current policies are:

| Distance | Policy version | Extraction baseline | Configuration |
|---|---|---|---|
| 3 | `h2_2_p_ext_0_00117_20261112` | `p_ext=0.00117` | [h2_2_decoder.json](configs/h2_2_decoder.json), loaded by [h2_2_decoder.py](src/h2_2_decoder.py) |
| 5, original mapping | `h2_2_d5_p_ext_0_004_20261113` | `p_ext=0.004` | [h2_2_d5_decoder.json](configs/h2_2_d5_decoder.json) |
| 5, skip-index-5 mapping | `h2_2_d5_skip5_p_ext_0_005_20261114` | `p_ext=0.005` | [h2_2_d5_skip5_decoder.json](configs/h2_2_d5_skip5_decoder.json) |

All three retain `p_read=0.001`, linear coefficient `0.0028`, frequency `0.043`, and frequency multiplier `2`. The baselines include unseparated preparation/readout contributions. Each new analysis must record its distance- and mapping-specific policy version and exact detector error model (DEM) SHA-256. Preserve submission-time metadata and historical analyses; keep different mappings separate and do not pool decoded results across policies without explicit redecoding and labeling. These H2-2 policies do not apply to H2-1 or emulators.

The completed sweeps support a timing tradeoff for these circuits and decoders. Sampling intervals exclude systematic uncertainty from decoder mismatch, backend drift, and unresolved scheduling. Calibration controls used to select decoder weights are not independent validation. Descriptive linear/quadratic fits and adaptively refined minima do not by themselves establish a microscopic noise law, calibrated coherence time, or a universal optimal interval.

## Folder guide

All paths below are relative to `SG_final_round/`.

| Folder | Contents and purpose |
|---|---|
| `configs/` | Experiment settings, requested shot allocations, and current distance-specific physical H2-2 decoder policies. Planned allocations need not equal completed shots. |
| `env/` | Python/Aqora environment records and local environment support. See [environment notes](env/README.md) and [pilot versions](env/pilot_environment.json); saved pilot records identify Python 3.11.18 and Aqora 0.36.0. |
| `src/` | QIR builders, submission/collection utilities, decoders, analysis, fitting, plotting, and report-generation scripts. These reuse `qec_timing` code and pinned native QIR from the parent repository. |
| `programs/` | Generated textual QIR (`.ll`), executable bitcode (`.bc`), round-trip assembly checks, manifests, hashes, and historical decoder models. Build names distinguish experiment families and variants. |
| `runs/` | Submission requests, Aqora job IDs, platform/options metadata, provider responses, status snapshots, raw result payloads, and some run-specific scripts/DEMs. This is the primary job audit trail. |
| `results/` | Human-readable reports, JSON provenance and fitted parameters, NPZ per-shot arrays, figures, PDFs, and saved DEMs in `results/decoders/`. Earlier reports remain as historical snapshots. |
| `tests/` | Local structural checks for QIR transformations, gate/output mapping, wait placement, and experiment allocation. Passing these checks does not prove backend timing semantics. |

## How judges can verify job IDs

### 1. Identify the execution record and platform

Find the job in the linked report or under `runs/**/job.json`. Emulator records usually live under `execute/<setting>/`; physical distance-3 batches also use direct `n<rounds>/` directories. Records contain `job_id`, requested shots, platform, options, and usually the program path/hash. Adjacent status files provide batch-level views.

Check both the requested `platform` and returned `job.platform.name`: **H2-1E/H2-2E = emulator; H2-1/H2-2 = physical hardware; H2-1SC/H2-2SC = syntax check only**. A completed syntax-check job is not evidence of hardware execution. Require a completed execution job and its result payload before counting shots.

Representative records:

| Kind | Aqora job ID | Local evidence |
|---|---|---|
| H2-2E emulator, distance 3, sleep argument 1, 1,000 shots | `AFByb3ZpZGVySm9iAaGb-GmmcFCF0koVMVevlQ` | [Execution record](runs/d3_sleep_five_point_h2_2e_67d11d0348065703/execute/sleep_1p0/job.json) |
| Physical H2-1, distance 3, N=2, 250 shots | `AFByb3ZpZGVySm9iAaHFSvfOekGOcDeSfSprbg` | [Execution record](runs/h2_1_hardware_d3_x_n2_t1_250/job.json) |
| Physical H2-2, distance 3, N=4, 1,000 shots | `AFByb3ZpZGVySm9iAaHSzbhqcxK89zYMHqgYfQ` | [Execution record](runs/h2_2_hardware_d3_x_t1_n40_n3_n4_20261113/n4/job.json) |
| Physical H2-2, distance 5, zero sleep, 500 shots | `AFByb3ZpZGVySm9iAaHTkCk8cmCs3HYizx6LiQ` | [Execution record](runs/d5_h2_2_zero_sleep_n2_500_20261113/execute/job.json) |

The opaque `AFBy...` strings are **Aqora job IDs**. Where returned, `providerId` is the separate Nexus provider UUID. For example, the physical H2-2 N=4 job above maps to `655711c4-746a-46f6-9f0c-3c8ab4dc72e7`. Use the Aqora ID for Aqora lookups; use the provider UUID when cross-checking an accessible Nexus record. Some historical records do not include a provider UUID.

To list locally collected **physical H2-2** payloads across both distances, run this from `SG_final_round/`. It selects completed H2-2 records with saved results, excludes emulator/syntax-check records, and prints the data directory beside each unique job ID:

```sh
python3 - <<'PY'
import json
from pathlib import Path

seen = set()
for path in sorted(Path('runs').rglob('job.json')):
    record = json.loads(path.read_text())
    job = record.get('job', {})
    job_id = record.get('job_id')
    if (record.get('platform') != 'nexus:H2-2'
            or job.get('platform', {}).get('name') != 'H2-2'
            or job.get('status') != 'COMPLETED' or job.get('error')
            or not job_id or job_id in seen):
        continue
    raw = sorted(path.parent.glob('result_*.txt'))
    if raw:
        seen.add(job_id)
        print(job_id, record.get('shots'), path.parent)
PY
```

Some analysis JSONs preserve absolute paths from the collecting workstation. In another checkout, use the portion starting at `runs/`, `programs/`, or `results/` relative to this folder; the links in this README already use portable relative paths.

### 2. Independently query an existing job through Aqora

Live verification requires an Aqora login with access to the submitting entity (`q_sq`). In an authenticated environment with the recorded Aqora SDK, the following read-only lookup prints current provider metadata for one emulator and three hardware jobs. It does not submit jobs or write artifacts:

```sh
python - <<'PY'
import json
from aqora import QPUJob

for job_id in (
    'AFByb3ZpZGVySm9iAaGb-GmmcFCF0koVMVevlQ',  # H2-2E emulator
    'AFByb3ZpZGVySm9iAaHSzbhqcxK89zYMHqgYfQ',  # physical H2-2, d=3
    'AFByb3ZpZGVySm9iAaHUTRpndcKAy2T8HalnHQ',  # physical H2-2, d=5 original
    'AFByb3ZpZGVySm9iAaHdiQNadvGeCDUnixjk7g',  # physical H2-2, d=5 skip-index-5
):
    job = QPUJob.from_id(job_id)
    print(job_id)
    print(json.dumps(dict(job.refresh()), indent=2, default=str))
PY
```

Compare the returned ID, platform, status, error, and result count with the saved record. A pending or cancelled job is not a zero-error observation; a cost-rejected attempt is not a completed experiment. Use the per-job record and latest applicable status snapshot when older submission summaries disagree.

### 3. Trace a result back to its circuit and decoder

For completed jobs, inspect adjacent `result_0.txt` payloads and the record's `results` metadata. Where recorded, compare raw-result and bitcode SHA-256 values with the corresponding report JSON and program manifest. Analysis JSON files also identify pooled source jobs and decoder hashes; NPZ files retain per-shot outputs for selected analyses. For example, from this folder:

```sh
shasum -a 256 runs/h2_2_hardware_d3_x_t1_n40_n3_n4_20261113/n4/result_0.txt
```

That payload's saved SHA-256 is `c80cca2158ca26692821c22451a9211f8a0c42b6c164564614bdb20086502d22`. Hash agreement establishes consistency with the archived artifact; authenticated provider lookup supplies the independent job/platform check.

For a distance-5 example, this offline check verifies the completed N=10 skip-index-5 payload against both the job record and analysis, and checks its exact DEM hash:

```sh
python3 - <<'PY'
import hashlib
import json
from pathlib import Path

folder = Path('runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10')
record = json.loads((folder / 'job.json').read_text())
analysis = json.loads((folder / 'analysis_p_ext_0_005.json').read_text())
assert record['job_id'] == analysis['job_id']
assert record['platform'] == 'nexus:H2-2'
assert record['job']['platform']['name'] == 'H2-2'
assert record['job']['status'] == 'COMPLETED' and not record['job'].get('error')
raw_hash = hashlib.sha256((folder / 'result_0.txt').read_bytes()).hexdigest()
assert raw_hash == record['results'][0]['raw_sha256'] == analysis['raw_sha256']
assert hashlib.sha256((folder / 'decoder_p_ext_0_005.dem').read_bytes()).hexdigest() == analysis['dem_sha256']
print(record['job_id'], analysis['shots'], 'shots: raw and DEM hashes verified')
PY
```

## Simple end-to-end emulator example

[`src/run_simple_emulator.py`](src/run_simple_emulator.py) builds, syntax-checks,
executes, collects, and decodes one **T_sleep=1 s, N=2, d=3 X-memory** experiment
on **H2-1E**, using the existing pinned circuit and noisy stabilizer options.
The default is 100 shots. Run from the repository root in a Python environment
with `aqora`, NumPy, Stim, and PyMatching installed, with `clang` on PATH and
the Aqora CLI authenticated (`aqora login`):

```sh
python SG_final_round/src/run_simple_emulator.py --shots 100 --as-entity q_sq
```

This command submits a one-shot H2-1SC syntax check followed by the emulator job,
which uses emulator credits. It polls until completion and writes the QIR,
bitcode, manifest, job IDs, raw results, decoder DEM, and `analysis.json` under
`SG_final_round/runs/simple_d3_t1_n2/`. Analysis reports logical failures,
logical error probability, and a 95% Wilson interval with the historical fixed
emulator decoder (`p_data=.002`, `p_read=.001`, `lam=0`).

For a local build without submission:

```sh
python SG_final_round/src/run_simple_emulator.py --build-only
```

Rerun the same command to resume saved jobs after a timeout (default: one hour
per job). Use `--output PATH` for a fresh experiment or different shot count;
an existing output directory resumes its recorded jobs. A submission attempt
without a saved job ID requires reconciliation before retrying. T_sleep=1 means
one requested one-second wait per data qubit between the two rounds; extraction
duration and physical sleep overlap have the same limitations described above.

## Local checks

Run from `SG_final_round/` within the parent repository checkout:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
```

The structural suite uses the parent repository's archived circuit sources; full decoding additionally needs NumPy, Stim, PyMatching, and, for fitting, SciPy. Environment versions are recorded in the relevant analysis artifacts. Existing reports and raw records can be inspected without submitting anything. Scripts named `submit_*` and builder execution actions can create provider jobs; they are not needed to verify the archived experiments.
