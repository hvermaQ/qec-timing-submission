# Reproducing every result

Linux, Python from `uv`. Times are on a 20-core, 31 GB workstation. Every command runs from
the repository root. Every simulation run is written to `store/` (gitignored, about 7 GB
after a full reproduction) and every study summary to `results/` (committed).

The top-level scripts (`run_approach_A.sh`, `run_approach_B.sh`, `run_idle_importance.sh`,
`run_hardware.sh`) run the commands below in groups; see *Running* in `README.md`.

Studies look runs up in the store before running them, so a second invocation only decodes
stored data, and an interrupted study resumes where it stopped.

## 1. Environments

Three, because the hardware toolchain (hugr-qir 0.1.2 → QIR for H2) needs guppylang 0.21 while
the simulations use guppylang 1.x. The package core (numpy only) imports in all three.

```bash
uv venv --python 3.12 .venv && uv pip sync --python .venv/bin/python envs/core.txt && uv pip install --python .venv/bin/python --no-deps -e .
```
```bash
uv venv --python 3.12 .venv-main && uv pip sync --python .venv-main/bin/python envs/main.txt && uv pip install --python .venv-main/bin/python --no-deps -e .
```
```bash
uv venv --python 3.11.13 .venv-h2 && uv pip sync --python .venv-h2/bin/python envs/h2.txt && uv pip install --python .venv-h2/bin/python --no-deps -e .
```

## 2. Tests

| env | command | result | time |
| --- | --- | --- | --- |
| core | `.venv/bin/python -m pytest` | 50 passed, 11 skipped (need other envs) | 2 s |
| main | `.venv-main/bin/python -m pytest` | 100 passed, 5 skipped (H2 env) | 17 s |
| H2 | `.venv-h2/bin/python -m pytest` | 57 passed, 4 skipped (main env) | 9 s |

Dated record of these runs: `results/test_runs/2026-10-13.txt`. The 6 warnings in the main
env are selene-sim leaving its own log files open (ResourceWarning), not ours. `-m "not slow"` skips the tests that
compile Guppy/Selene programs.

What the tests pin, beyond unit behaviour:
- **Contracts on every implementation** (`qec_timing.testing.contracts`), each also run against a deliberately broken implementation, so a contract that passes everything would fail.
- **Exact regressions against the original research repo:**
  - circuit-level failure counts identical at the same seeds (textbook and native gates);
  - the H2 QIR byte-identical to the original Stage 7a program;
  - application idle fractions equal to the original notebook 10.
- **Fits recovering known parameters from synthetic data:** edge extraction, idle calibration, and `calib-fit` end to end.

## 3. Studies (main env unless noted)

| result | command | time | output |
| --- | --- | --- | --- |
| Guppy vs Stim, paper's model | `python -m qec_timing.validation.crosscheck` | 11 min | `results/crosscheck/` |
| premise, textbook gates | `python -m qec_timing.studies.premise --gates textbook --workers 8` | ~5 min | `results/premise/premise_textbook.json` |
| premise, native gates | `python -m qec_timing.studies.premise --gates native --workers 8` | ~15 min | `results/premise/premise_native.json` |
| H2 regime, 5 round durations | `python -m qec_timing.studies.regime --calibration config/h2_1e_emulator.json --t-round 0.002 0.01 0.03 0.1 0.3 --distances 3 5 --workers 8` | 1 min | `results/regime/` |
| H2 regime grid (heatmap) | same, `--t-round 0.001 0.002 0.004 0.007 0.01 0.02 0.03 0.05 0.07 0.1 0.15 0.2 0.3 --distances 3 5 7 --workers 8 --out results/regime/grid` | ~1 h from scratch | `results/regime/grid/` |
| application idle time | `python -m qec_timing.studies.idle` | 5 s | `results/idle/` |
| paper scaling, 1/Δt* vs d | `python -m qec_timing.studies.scaling --workers 8` | 2 min | `results/scaling/` |
| effective λ, b_read (first step) | `python -m qec_timing.studies.effective --workers 8` | ~20 min | `results/effective/` |
| per-qubit error and sources | `python -m qec_timing.studies.per_qubit` | 1 min | `results/per_qubit/` |
| decoder comparison | `python -m qec_timing.studies.decoders --workers 8` (after premise native) | ~10 min | `results/decoders/` |
| Δt* vs idle strength, Δt* map | `python -m qec_timing.studies.idle_scaling --placement uniform --workers 8` | ~20 min | `results/idle_scaling/idle_scaling_uniform.json` |
| same, data-only idle (original notebook 07 reference) | `python -m qec_timing.studies.idle_scaling --workers 8` | ~20 min | `results/idle_scaling/idle_scaling.json` |
| QIR programs and scaling (H2 env) | `.venv-h2/bin/python -m qec_timing.hardware.cli build ...`, `scaling`, `calib-build` | 1 min | `results/hardware/` |
| notebooks | `python notebooks/_build.py notebooks`, then execute | 2 min | `notebooks/*.ipynb` |

**Seeds.**
- Every run's seed is fixed in the study modules, and its run id is a hash of its full specification, so reruns are identical.
- Per-shot-seeded backends (Guppy) are checked for overlapping seed ranges, which would correlate runs.

**Memory.**
- Runs above 256 MB of detection events are split into stored shot chunks.
- Parallel workers are capped by the memory the kernel reports as available.

An earlier unbounded version exhausted memory and was fixed (commits `ca592d3`, `dd884a4`).

## 4. Hardware (H2 env, needs an aqora or Nexus login)

Nothing here has been run on a device yet: access through aqora is blocked by a Nexus
terms challenge on the provider side (aqora issue, since 9 October). The order of use is in
`results/hardware/README.md`. Credit-spending commands refuse to run without `--confirm`.

## 5. Provenance

- **Every stored run:** its manifest records the spec, backend, package versions, the git commit and whether the tree was dirty, and checksums of the raw files.
- **Every derived result:** it names the runs it came from, and `Store.check_lineage` flags any that were made by different code.
