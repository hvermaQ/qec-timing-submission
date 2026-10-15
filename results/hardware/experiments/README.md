# Hardware experiments

All runs go through aqora as organisation `q_sq` to Quantinuum's H2 emulators (no device is
available to this account). Every program is syntax-checked first (H2-1SC / H2-2SC, free);
emulator runs spend credits. Raw job records stay in `store/hardware/` (local, not in git).

| # | Experiment | Machine | Status |
| --- | --- | --- | --- |
| 01 | [Memory with noise injection](01_memory_injection/README.md) | H2-1E | done |
| 02 | [Readout error](02_readout/README.md) | H2-1E | done |
| 03 | [Idle dephasing with spectator qubits](03_idle_spectators/README.md) | H2-1E | done |
| 04 | [Δt sweep, d = 5](04_dt_sweep_d5/README.md) | H2-2E | 3 of 5 points |
| 05 | [Leakage-heralded decoding](05_heralded_leakage/README.md) | — | design only |

Common commands (H2 env): `hardware.cli build | calib-build | aqora-check | aqora-submit --confirm | calib-fit`.

Notebooks: `notebooks/14_emulator_noise_injection.ipynb` (experiments 01, 04) and
`notebooks/15_emulator_idle_parameters.ipynb` (experiments 02, 03).
