# Hardware programs and results

Programs built with the H2 env (`envs/h2.txt`) by `hardware/1_build.sh`; results rebuilt
from the returned emulator jobs by `hardware/4_collect.sh`. Steps, envs and costs:
[`hardware/README.md`](../../hardware/README.md).

`programs/`: memory experiments as validated QIR. `d3_X_r2_p0.05` is byte-identical to the
original repo's Stage 7a `d3_r2_X.bc` and passes the backend contract on local Selene.

`calibration_programs/`: readout and spectator-idle programs, X and Z basis: measure-and-reset
spectators (`idle_`, L = 0-64), transport (`idleT_`, L = 0-16) and anchored transport (`idleA_`,
L = 0-256). No delay instruction exists in Guppy 0.21/1.x or pytket, and this toolchain cannot
lower `barrier` to QIR, so idling is spectator layers, with the targets' measurement ordered
after them by feed-forward (see `hardware/calibration_experiments.py`). The duration of one
layer is not reported by the emulator, so the idle fits stay per layer.

Summaries (all written by `hardware/4_collect.sh`): `h2_1e_memory_d3.json` (noise injection,
d = 3), `h2_2e_dt_sweep_d5*.json` (Δt sweep, d = 5, with the program-model decoder and
curves), `h2_1e_*idle*.json` and `h2_1e_calibration_runs.fit.json` (idle and readout fits),
`syntax_checks.json`. `qir_scaling.json` comes from `hardware.cli scaling` (notebook 10).

Experiment write-ups, one per experiment: [experiments/README.md](experiments/README.md).
