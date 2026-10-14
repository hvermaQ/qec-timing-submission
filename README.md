# qec-timing

Optimal syndrome-measurement timing for QEC memories, after Haug, Bharti & Aolita (2026).
A package built from interfaces: codes, noise models, backends, decoders and applications
are swappable, and every implementation is checked against the same contracts.

**Status:** step 3 of the migration. Interfaces, store and contracts (step 1); the paper's
model on Stim and Guppy/Selene with the cross-check (step 2); circuit-level noise on
textbook and native gates, the effective-model fit, the premise study and the device
regime study (step 3); application idle analysis and the hardware path: QIR builder,
local Selene check, aqora and Nexus adapters, calibration experiments and fits (step 4);
narrative notebooks, `CLAIMS.md` and `REPRODUCE.md` (step 5).

**Start here:** `CLAIMS.md` (every claim, its evidence and its level), the notebooks in
`notebooks/` (figures in `figures/`), and `REPRODUCE.md` (one command per result).
The notebooks run in two arcs:
- **simulation, 01–09:** idle in applications (01); the paper's model, Guppy vs Stim (02);
  dephasing needs the X basis (03); realistic circuit noise (04–06); how the optimum moves
  with idle strength (07); the regime on H2-1E rates (08); the payoff, time for space (09);
- **hardware, 10–13:** program size and cost (10), the device program checked end to end
  (11), measuring the device's idle noise and feeding it back (12), the hardware experiments
  drawn, with their syntax checks (13).

Retired notebooks (kept for the record, not part of the argument) are in `notebooks/retired/`.

## Setup

Three environments, pinned in `envs/`. Tests that need another env skip.

| env | file | Python | contains | runs |
| --- | --- | --- | --- | --- |
| `.venv` | `envs/core.txt` | 3.12 | numpy, pytest | interfaces, store, contracts, fits |
| `.venv-main` | `envs/main.txt` | 3.12 | + Guppy 1.x/Selene, Stim, PyMatching, scipy, pytket | simulations and studies |
| `.venv-h2` | `envs/h2.txt` | 3.11 | Guppy 0.21, hugr-qir, qnexus, aqora | hardware programs and submission |

The H2 env is separate because hugr-qir 0.1.2 (QIR for H2) needs guppylang 0.21, while the
simulations use guppylang 1.x. The package core (numpy only) imports in all three.

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
| `python -m qec_timing.hardware.cli ...` (H2 env) | Build, check locally, price, submit and fetch hardware programs; fit calibrations | `results/hardware/`, `config/` |

**Regression against the original repo.** The circuit-level backends reproduce the
original notebooks' cached failure counts exactly (same circuits, same seeds): 12/12
sampled runs of notebooks 07/08 (textbook) and 6/6 of 09 (native gates, recompiled with
selene-sim 0.3.2). Two such cases are pinned in `tests/test_circuit.py`.

## Adding a component

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
