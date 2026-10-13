# Regime study: H2-1E emulator parameters

`regime_h2_1e_emulator_textbook.json`, from
`python -m qec_timing.studies.regime --calibration config/h2_1e_emulator.json --t-round 0.002 0.01 0.03 0.1 0.3 --distances 3 5`.
Textbook gates, uniform idle placement, H2-1E gate/readout/idle rates unscaled,
"cycles" reading of the quadratic rate. t_R (seconds per extraction round) is not
published; it is the study parameter.

| t_R | idle error / round | d=3: dt* (gain) | d=5: dt* (gain) |
| --- | --- | --- | --- |
| 2 ms | 5.9e-6 | 43 rounds = 86 ms (x22.5) | 32 rounds = 64 ms (x19.1) |
| 10 ms | 3.5e-5 | 9.0 = 90 ms (x5.0) | 6.5 = 65 ms (x3.7) |
| 30 ms | 1.5e-4 | 3.1 = 94 ms (x1.9) | 2.5 = 76 ms (x1.8) |
| 100 ms | 1.0e-3 (~p2) | 1.4 = 135 ms (x1.27, 3.3 sigma) | back to back |
| 300 ms | 7.4e-3 | back to back | back to back |

Waiting pays while idle error per round is well below p2; the crossover is near
idle per round ~ p2 (t_R ~ 0.1 s). The optimal wait in seconds stays near
65-95 ms while the round is shorter than that. The 2 ms row reproduces the
Stage 7a twin estimate (44.1 rounds, x23 at d=3; 35.9, x20 at d=5) from an
independent implementation.

Model validity: the quadratic idle term sin^2(omega t / 2) is a twirled coherent
rotation and is periodic. Points with omega * dt * t_R >= pi are outside the model
("model_valid": false) and, with all points after the first saturated one, are
not used (`points_used` per row). Without this cut, a rephasing artefact at
t_R = 300 ms produced a spurious minimum at 19.8 rounds.
