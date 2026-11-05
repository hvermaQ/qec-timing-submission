# Hardware runs (notebooks 11–15)

Separate from the simulations (notebooks 01–10, the `run_*.sh` scripts at the top level): these
steps build programs for Quantinuum H2, check and run them on the H2 emulators through aqora, and
turn the returned jobs into the summaries the hardware notebooks read. Each step is its own
script, so the one that spends credits can't run by accident. Run them from anywhere.

| Step | Does | Env | Needs | Cost |
| --- | --- | --- | --- | --- |
| `hardware/1_build.sh` | every program as QIR (`results/hardware/programs/`, `calibration_programs/`), contract check on local Selene | H2 | — | free |
| `hardware/2_check.sh [exp ...]` | the planned programs through the H2-1SC / H2-2SC syntax checkers (validate, execute nothing) | H2 | aqora login | free |
| `hardware/3_submit.sh [exp ...]` | prints the run plan (experiment, program, emulator, shots) and stops | — | — | free |
| `hardware/3_submit.sh --confirm [exp ...]` | runs it on H2-1E / H2-2E; raw jobs go to `store/hardware/` | H2 | aqora login | **credits** |
| `hardware/4_collect.sh` | `store/hardware/` → the summaries in `results/hardware/` (decoding, idle fits, model predictions, syntax checks) | main | the returned jobs | free, ~20 s |
| `hardware/5_analyse.sh` | executes notebooks 11–15 on those summaries | main | — | free |

`[exp ...]` restricts a step to some experiments of the plan: `memory_d3`, `dt_sweep_d5`, `readout`,
`idle_measure_reset`, `idle_transport`, `idle_anchored`, `idle_anchored_long`. The plan, in
[`config.sh`](config.sh), is the 47 emulator jobs the committed results come from. It leaves out
two that went over aqora's per-job cost cap (d = 5 at R = 70; anchored idle at L = 256).

Settings, as environment variables: `ENTITY` (aqora organisation, default `q_sq`), `OPTIONS`
(emulator options as JSON, e.g. `'{"no_opt": true, "error_params": {"idle_dephasing": true}}'`;
empty by default, which is how every committed job ran: the platform's defaults), `PY_H2`,
`PY_MAIN` (interpreters). Log in once with `.venv-h2/bin/aqora login`.

```bash
hardware/1_build.sh
hardware/2_check.sh dt_sweep_d5
hardware/3_submit.sh dt_sweep_d5              # what would run
hardware/3_submit.sh --confirm dt_sweep_d5    # run it (credits)
hardware/4_collect.sh && hardware/5_analyse.sh
```

**What `collect` reproduces** (`src/qec_timing/hardware/collect.py`; checked by
`tests/test_hardware.py::test_collect_reproduces_committed_hardware_results`):
- Everything computed from returned shots is exact: detector rates, raw and decoded logical failures,
  idle flip counts, fits and syntax-check outputs. The d = 5 sweep adds the paper's record flips
  offline, seeded 700 + R.
- Model predictions (`stim_*` keys, model curves) are seeded Stim samples. The seeds were recovered
  from the original results, which they reproduce, except the H2-2E-gate model curve, which agrees
  within shot noise.
- Fit floats differ from H2-env runs in the 6th digit (numpy 2.5 against 2.4).

One check from the original analysis isn't regenerated: local Selene shots decoded with the
program DEM (`emulator_runs.md`). It needs both environments and isn't read by any notebook.
