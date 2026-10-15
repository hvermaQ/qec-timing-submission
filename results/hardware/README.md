# Hardware programs (nothing submitted yet)

Built with the H2 env (`envs/h2.txt`). See `python -m qec_timing.hardware.cli --help`.

`programs/`: memory experiments as validated QIR. `d3_X_r2_p0.05` is byte-identical to the
original repo's Stage 7a `d3_r2_X.bc` and passes the backend contract on local Selene.

`calibration_programs/`: readout (T2) and spectator-idle (T3/T4) programs, X and Z basis,
layers 0-64. No delay instruction exists in Guppy 0.21/1.x or pytket, and this toolchain
cannot lower `barrier` to QIR, so idling is spectator layers of mid-circuit measurement,
with the targets' measurement ordered after them by feed-forward (see
`hardware/calibration_experiments.py`). Not yet confirmed on a device: that Nexus's
compiler keeps these programs as written, and the duration of one layer (needed for a
Calibration in seconds; read it from the job's duration report).

Order of use once access returns:
1. `aqora-list` (or Nexus login) to see the platforms.
2. `aqora-check` / `nexus-cost` on each program: validates and prices, executes nothing.
3. `nexus-submit --confirm` on the emulator (H2-1E) first, then the device.
4. `nexus-fetch`, then `store` (memory) or `calib-fit` (calibration) -> `config/*.json`.
5. `python -m qec_timing.studies.regime --calibration config/<measured>.json --t-round <t_R>`.

Experiment write-ups, one per experiment: [experiments/README.md](experiments/README.md).
