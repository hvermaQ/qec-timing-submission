# H2-2E d=3 sleep sweep: decoded results and noise interpretation

All five jobs completed, with 1,000 shots each. Nine data qubits and one reused ancilla perform two rounds of four X-stabilizer checks. All data qubits receive the same raw sleep argument between rounds, bounded by barriers. This tests the X-memory sector, not both stabilizer sectors or arbitrary encoded states. No artificial faults or offline flips were injected.

| Raw sleep argument | Decoded logical failures | Logical error rate | 95% Wilson interval | Mean data-qubit error | Raw logical parity flips |
|---|---:|---:|---:|---:|---:|
| 0 | 2 / 1000 | 0.20% | 0.05–0.73% | 0.133% | 3 / 1000 |
| 0.1 | 5 / 1000 | 0.50% | 0.21–1.17% | 0.400% | 11 / 1000 |
| 0.5 | 17 / 1000 | 1.70% | 1.06–2.71% | 3.044% | 94 / 1000 |
| 0.75 | 48 / 1000 | 4.80% | 3.64–6.31% | 5.967% | 139 / 1000 |
| 1 | 140 / 1000 | 14.00% | 11.99–16.29% | 10.133% | 261 / 1000 |

A logical failure is the final logical-X parity on data qubits 0,3,6 XOR the matching decoder’s predicted correction. Rates are per complete two-round experiment, not per round or second. A raw logical-parity flip is a different quantity from a decoded failure.

## Decoder and validation

Primary decoder: the same fixed phenomenological minimum-weight perfect matching graph used for the preceding H2-1E analysis, with p_data=0.002 per round, p_read=0.001, lam=0. These are decoder assumptions, not extra noise injected into the submitted circuits. Repeating decoding with p_data=0.02 and 0.1 gave exactly the same counts: 2, 5, 17, 48, 140. This sensitivity check does not make the decoder an exact model of backend correlations, hooks, or time-dependent dephasing.

All 5,000 packed shots match formatted joint counts; all 17 outputs are Boolean; raw-file hashes match collection records. Ideal decoding and each of the nine isolated between-round Z faults were checked and corrected. Seven structural tests passed. Confidence intervals assume independent shots; one job per setting does not measure run-to-run variability.

## Location of the added errors

| Raw argument | First-round mean detector rate | Inter-round mean detector rate | Final-boundary mean detector rate |
|---|---:|---:|---:|
| 0 | 0.300% | 0.450% | 0.250% |
| 0.1 | 0.250% | 1.250% | 0.575% |
| 0.5 | 0.500% | 8.525% | 0.425% |
| 0.75 | 0.325% | 16.025% | 0.475% |
| 1 | 0.375% | 23.975% | 0.425% |

Means average four checks; checks are not independent trials. The increase is concentrated in the inter-round block containing the wait. First-round and final-boundary rates remain comparatively low.

| Data qubit | sleep(0) | sleep(0.1) | sleep(0.5) | sleep(0.75) | sleep(1) |
|---|---:|---:|---:|---:|---:|
| 0 | 0.3% | 0.3% | 2.7% | 4.9% | 11.0% |
| 1 | 0.3% | 0.6% | 2.6% | 7.1% | 10.3% |
| 2 | 0.1% | 0.3% | 2.2% | 6.9% | 9.6% |
| 3 | 0.0% | 0.4% | 3.3% | 5.5% | 10.6% |
| 4 | 0.2% | 0.6% | 2.5% | 6.3% | 9.4% |
| 5 | 0.0% | 0.3% | 3.8% | 6.5% | 11.4% |
| 6 | 0.0% | 0.4% | 3.4% | 4.7% | 11.3% |
| 7 | 0.1% | 0.3% | 3.5% | 6.8% | 9.2% |
| 8 | 0.2% | 0.4% | 3.4% | 5.0% | 8.4% |

The 0.1 logical-error comparison with zero is inconclusive at this sample size (two-sided Fisher p=0.452). The 0.5 comparison gives p=0.000690; 0.75 and 1 show much stronger increases. These are exploratory comparisons, not corrections for repeated testing or job-level variability.

## Overall requested emulator error model

Execution requested stabilizer simulation, noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true. Other noise parameters were not overridden; unspecified channels retain backend defaults. They include gate, preparation, readout, crosstalk, and memory errors. Stabilizer memory noise uses stochastic Z faults with a linear term and a sinusoidal term that is quadratic at short times. No continuous coherent phase evolution was simulated in this mode.

Nominal documented H2-2E defaults: p1=7.3e-5, p2=0.00129, readout probabilities 0.0009/0.0018 for 0/1, p_init=4e-5, measurement/initialization crosstalk 8.8e-6/9.6e-6. Memory defaults: linear parameter 0.0028 per second, quadratic parameter 0.043 in the documentation’s frequency convention, incoherent multiplier 2. These values are documentation defaults, not a returned snapshot of these jobs.

Sources accessed 2 November 2026:
- https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html
- https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html

## What the data identify

With raw argument u, the observed mean physical X-readout error is p(u). If an unchanged background flip channel p0 composes independently by XOR with an added channel q(u), then p(u)=p0+(1−2p0)q(u). This gives an effective added flip probability, not a directly measured idle rate:

| Raw argument | Effective added flip probability q | 95% shot-bootstrap interval |
|---|---:|---:|
| 0.1 | 0.267% | 0.112–0.423% |
| 0.5 | 2.919% | 2.574–3.270% |
| 0.75 | 5.849% | 5.371–6.336% |
| 1 | 10.027% | 9.400–10.655% |

Bootstrap intervals use 10,000 resamples of complete shots (seed 20261102), retaining within-shot correlation among qubits and uncertainty in p0. They exclude job-to-job drift. The independent background-channel assumption is not established by this experiment.

An unweighted descriptive fit, with measured p0 fixed, is:

    p(u) ≈ 0.001333 + 0.015245 u + 0.084495 u²

These are probabilities in raw argument units. The fit is a compact interpolation over 0≤u≤1, not an estimate of the backend’s linear/quadratic parameters, a unique identification of its noise model, or a reliable extrapolation. Its curvature is consistent with a substantial quadratic contribution. Logical-error growth alone cannot identify that contribution because decoding and multiple-fault probabilities are nonlinear even for a simpler physical noise model.

If the quadratic channel already experiences an unknown baseline duration d0, adding a wait gives (d0+u)²−d0²=2d0u+u². Thus even the fitted linear coefficient can contain a quadratic cross-term; it cannot simply be equated with the emulator’s linear dephasing parameter.

For one uninterrupted interval, a useful conditional model is p_lin=r d and p_quad=sin²(ω_eff d/2). If these are independent Z channels, their net probability is p_lin+p_quad−2 p_lin p_quad. At small d this is approximately r d+(ω_eff²/4)d². Applying this to our jobs requires knowing duration units, how the backend partitions waits/transport intervals, and actual noise parameters; those are not confirmed here.

## Inference and limits

The sweep establishes a pronounced sleep-dependent increase in physical and decoded logical error, localized across the inserted wait. The raw physical growth is compatible with the documented linear-plus-quadratic dephasing family. The absolute failure probability includes all enabled channels and decoder effects; the excess cannot uniquely be assigned to idle dephasing without matched controls.

It does not establish: physical seconds per sleep argument; nine simultaneous waits; a T2 value; separate idle versus transport rates; exact linear/quadratic parameters; independent faults; absence of correlated noise; or performance for both stabilizer sectors. Similar error rates on all nine qubits do not prove parallel timing.

For calibrated idle rates, first confirm units and scheduling. Then use matched controls with idle dephasing off, transport dephasing controlled separately, and gate/readout/preparation/crosstalk contributions removed or independently calibrated. Add more short waits, repeated jobs, and finer shot counts to separate small linear noise from quadratic growth. No additional provider jobs were submitted for this analysis.

## Reproducibility

- Decoded counts, intervals, models, versions and job IDs: `d3_sleep_five_point_h2_2e_1000.json`.
- Effective flip estimates, bootstrap and descriptive fit: `d3_sleep_five_point_h2_2e_noise_characterization.json`.
- Original payloads: `../runs/d3_sleep_five_point_h2_2e_67d11d0348065703/execute/`.
- Decoder: `../src/analyze_d3_sleep_sweep.py --five-point --platform nexus:H2-2E`.
- Physical characterization: `../src/characterize_h2_2e_sleep.py`.

Execution HQC estimate remains 570–652 total. Actual billed HQCs were not returned. H2-1E five-point results were not analyzed here.
