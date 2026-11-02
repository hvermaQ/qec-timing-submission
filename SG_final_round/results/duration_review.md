# Sleep-duration review

The current build is `../programs/5944c048c1dfdc80/`: no sleep, sleep(0), and raw
arguments **0.01, 0.05, 0.1, 0.2, 0.5**. All target data qubit 4 once between
the two extraction rounds. These are candidates for syntax checking; units,
endpoint support, simulator mode, and scheduling semantics remain unverified.
The earlier three-variant build is retained.

## What was actually used in the previous emulator runs

The H2-1E spectator tests varied layer counts, not explicit sleep durations:

- Measure/reset spectators: L = 0, 2, 4, 8, 16, 32, 64.
- Transport spectators: L = 0, 2, 4, 8, 16.
- Longer anchored experiments: L = 0, 16, 32, 64, 128.

The final anchored X-basis counts were:

| Layers | Flips / recorded target outcomes | Rate |
|---|---|---|
| 0 | 82 / 8000 | 1.025% |
| 16 | 93 / 8000 | 1.1625% |
| 32 | 112 / 8000 | 1.400% |
| 64 | 120 / 8000 | 1.500% |
| 128 | 89 / 8000 | 1.1125% |

There were eight targets per shot; the 8000 outcomes are not 8000 separate
submitted shots. The earlier 3.6 ms/layer fit was withdrawn when L=128 returned
to the floor. Therefore these data provide **no established conversion from
spectator layers to seconds**. L=256 was refused under the job cost limit.

Sources: `results/hardware/h2_1e_anchored_idle_long.json`,
`results/hardware/h2_1e_anchored_idle_long_fit.json`,
`results/hardware/experiments/03_idle_spectators/README.md` in the repository root.
The new `duration_scales.json` preserves the historical counts and source hashes.

The H2-2E d=5 injection sweep used nominal dt values approximately 0.14, 0.5, 1,
2.5, 5 with R=70,20,10,4,2 at nominal T=10. Those were model-time labels for
injected errors, **not commanded waits in seconds**, so they are not a calibration
for this sleep sweep. Source: `results/hardware/experiments/04_dt_sweep_d5/README.md`.

## Conditional physical scales

Using the repository's saved `config/h2_1e_emulator.json`, gamma=0.0028 /s,
quadratic rate f=0.043 with the stored **cycles** convention, and multiplier k=2:

    a = gamma * t
    b = sin(pi * f * k * t)^2
    pZ(t) = a + b - 2*a*b

For this calculation ONLY, assume the sleep argument is in seconds, the
stabilizer convention k=2 applies, and it becomes one uninterrupted idle channel
with no dynamical decoupling. The present aqora job configuration has not verified
these assumptions. These estimates exclude preparation, readout, gate faults,
other background idle exposure, and correction. They are not logical failure rates.

| Raw argument, if seconds | Duration | Estimated Z-error probability on q4 | Expected q4 wait faults / 1000 shots |
|---|---|---|---|
| 0.01 | 10 ms | 0.003530% | 0.0353 |
| 0.05 | 50 ms | 0.032243% | 0.3224 |
| 0.1 | 100 ms | 0.100937% | 1.0094 |
| 0.2 | 200 ms | 0.347372% | 3.4737 |
| 0.5 | 500 ms | 1.948737% | 19.4874 |

The small-time linear/quadratic crossover is about **38 ms**, so this candidate
range spans the transition. The 10 ms point provides a short-duration
control but have very little expected signal at 1000 shots. At 100-200 ms the
signal is larger, still small compared with the gate/readout background of a
complete memory circuit. Detector rates and a companion uncorrected X-basis
probe are more informative than decoded logical errors alone for this test.

Recommendation: use the updated five requested arguments, including 0.5, but do
not call them physical durations until units and execution mode are confirmed.
The 1.0-second extension remains a calculation only, outside the current build.
See `shot_budget.md` for the proposed shot counts and the distinction between the
existing d=3 single-target circuit and a standalone one-qubit calibration probe.

The stored calibration records ambiguity in the quadratic convention. The JSON
also supplies the alternative radians convention and the k=1 calculation for
sensitivity; none is a measurement of the new sleep instruction.

Reproduce the estimates with:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 SG_final_round/src/review_duration_scales.py
```

Current official default-value table agrees with the stored gamma, f, and k:
https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html
Noise-channel description:
https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html
Neither establishes the sleep instruction's units. No new provider jobs were run.

## Local validation

Six structural tests passed. All seven programs assembled successfully with
clang, retaining the quantum/runtime call counts and QIR entrypoint attributes
in bitcode round-trip checks. This is not H2 syntax acceptance.
