# qec-timing

Optimal syndrome-measurement timing for QEC memories, after Haug, Bharti & Aolita (2026).
A package built from interfaces: codes, noise models, backends, decoders and applications
are swappable, and every implementation is checked against the same contracts.

**Status:** step 3 of the migration. Interfaces, store and contracts (step 1); the paper's
model on Stim and Guppy/Selene with the cross-check (step 2); circuit-level noise on
textbook and native gates, the effective-model fit, the premise study and the device
regime study (step 3). Hardware adapters and application idle analysis follow.

## Setup

Two environments, both Python 3.12, pinned in `envs/`:

| env | file | contains | runs |
| --- | --- | --- | --- |
| `.venv` | `envs/core.txt` | numpy, pytest | interfaces, store, contracts (tests needing Stim skip) |
| `.venv-main` | `envs/main.txt` | + Guppy/Selene, Stim, PyMatching, scipy | everything in step 2 |

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
