# H2-1E d=3 five-point sleep sweep: logical error probabilities

This analysis uses the fresh five-point H2-1E sweep only. The earlier three-point experiment is retained separately and is not pooled into these results.

## Exact protocol

Distance d=3 rotated surface-code geometry: nine data qubits, one reused ancilla, four X-stabilizer checks per extraction round. Prepare all data qubits in |+>, extract X stabilizers once, apply the all-data sleep block, extract X stabilizers again, then measure all data qubits in X. Nine explicit single-qubit sleep calls use the same raw argument u, with ten-qubit barriers before and after the block; the ancilla has no sleep call. The zero control includes explicit sleep calls. This tests X-sector memory, not both stabilizer sectors or arbitrary encoded states.

Arguments 0, 0.1, 0.5, 0.75, 1 each use 1,000 shots. Execution was on H2-1E through Aqora (q_sq), with noisy stabilizer simulation, optimization disabled, and idle/transport dephasing enabled. No artificial faults or offline readout flips were added.

## Decoded logical error probabilities

| Raw argument u | Logical failures / shots | P_L(u) | 95% Wilson interval | Mean data error | Raw logical parity flips |
|---|---:|---:|---:|---:|---:|
| 0 | 3 / 1000 | 0.003 (0.30%) | 0.10% - 0.88% | 0.278% | 8 / 1000 |
| 0.1 | 4 / 1000 | 0.004 (0.40%) | 0.16% - 1.02% | 0.411% | 11 / 1000 |
| 0.5 | 16 / 1000 | 0.016 (1.60%) | 0.99% - 2.58% | 3.056% | 86 / 1000 |
| 0.75 | 46 / 1000 | 0.046 (4.60%) | 3.47% - 6.08% | 5.989% | 161 / 1000 |
| 1 | 115 / 1000 | 0.115 (11.50%) | 9.67% - 13.63% | 10.144% | 230 / 1000 |

P_L is a probability per complete two-round experiment, not an error rate per round or time. A logical failure is the final logical-X parity on qubits 0,3,6 XOR the matching decoder’s predicted logical correction. The future effective time-normalized metric P_L(R, Delta t)/T requires an R-round experiment and a verified definition of total physical duration T, including extraction time as appropriate. These two-round probabilities cannot simply be extrapolated to many rounds.

Primary decoder: fixed historical phenomenological minimum-weight perfect matching graph, p_data=0.002 per round, p_read=0.001, lam=0. These are decoder-weight assumptions, not injected faults. Sensitivity checks with p_data=0.02 and 0.1 produced exactly the same failures: 3, 4, 16, 46, 115. This is not an exact calibrated decoder for all backend correlations or circuit faults.

All 5,000 packed shots agree with provider-formatted joint counts. All expected 17 outputs are Boolean. Raw-file hashes match the stored collection metadata, and seven structural tests passed. One job per setting does not quantify run-to-run variability; uncertainty assumes independent shots.

## Where the errors increase

| u | First-round mean detector probability | Inter-round mean detector probability | Final-boundary mean detector probability |
|---|---:|---:|---:|
| 0 | 0.325% | 0.500% | 0.625% |
| 0.1 | 0.275% | 1.000% | 0.550% |
| 0.5 | 0.425% | 8.325% | 0.675% |
| 0.75 | 0.350% | 16.250% | 0.975% |
| 1 | 0.350% | 23.950% | 0.700% |

These values average four checks at each boundary; checks are not independent trials. The dominant increase is concentrated across the inserted wait.

| Data qubit | u=0 | u=0.1 | u=0.5 | u=0.75 | u=1 |
|---|---:|---:|---:|---:|---:|
| 0 | 0.1% | 0.3% | 3.3% | 5.6% | 9.9% |
| 1 | 0.3% | 0.5% | 2.2% | 6.1% | 9.8% |
| 2 | 0.4% | 0.6% | 4.1% | 4.8% | 10.9% |
| 3 | 0.3% | 0.5% | 3.1% | 6.4% | 9.2% |
| 4 | 0.7% | 0.5% | 2.8% | 6.6% | 10.7% |
| 5 | 0.0% | 0.3% | 2.4% | 6.5% | 10.1% |
| 6 | 0.4% | 0.3% | 3.4% | 4.9% | 9.7% |
| 7 | 0.3% | 0.4% | 3.0% | 6.9% | 9.4% |
| 8 | 0.0% | 0.3% | 3.2% | 6.1% | 11.6% |

The logical increase at u=0.1 is inconclusive (exploratory two-sided Fisher p=1.0 versus zero). At u=0.5, p=0.00425; at 0.75 and 1 the increases are much clearer. Tests assume independent samples and do not account for job-level drift or multiple comparisons.

## Physical data-error probability p_data(u)

p_data(u) is the mean final X-readout error probability per data qubit, averaged across nine qubits. It includes background circuit errors; it is not a measured pure idle-channel probability.

An unweighted descriptive fit, fixing the intercept to the measured zero-control background, gives:

    p_data(u) ≈ 0.002778 + 0.010631 u + 0.087958 u²

u is the raw sleep argument, with no verified physical-time unit. Values are probabilities, not percentages. The expression interpolates the measured interval 0 <= u <= 1; its coefficients are not physical rates or backend parameter estimates.

Under the conditional assumption that an unchanged background channel p0 combines by independent XOR with an added flip channel q(u), q(u)=[p_data(u)-p0]/(1-2p0):

| u | Effective added flip probability | 95% shot-bootstrap interval |
|---|---:|---:|
| 0.1 | 0.134% | -0.034% - 0.301% |
| 0.5 | 2.793% | 2.425% - 3.172% |
| 0.75 | 5.743% | 5.242% - 6.250% |
| 1 | 9.922% | 9.278% - 10.575% |

Bootstrap uses 10,000 resamples of complete shots, seed 20261102, retaining within-shot qubit correlations and baseline uncertainty. The independent-background assumption and absence of run-to-run changes remain unverified.

## Overall error model and idle-noise inference

The jobs used the full noisy emulator, retaining default gate, readout, preparation and crosstalk faults alongside explicitly enabled idle and transport dephasing. Stabilizer memory noise is represented by stochastic Z faults with linear-duration and short-time-quadratic contributions. The observed physical curvature is compatible with this family; it does not uniquely identify a noise mechanism.

Nominal H2-1E defaults in the current documentation are p1=1.89e-5, p2=0.00105, readout probabilities 0.0006/0.00139, preparation probability 4e-5, and measurement/initialization crosstalk 3.3e-6 each. Documented dephasing parameters are linear 0.0028 per second, quadratic 0.043 in the documented frequency convention, and incoherent multiplier 2. These are published defaults, not values inferred here or returned snapshots of these jobs.

For an uninterrupted interval, an illustrative independent-channel model is p_lin=r*d, p_quad=sin²(omega_eff*d/2), and combined p_Z=p_lin+p_quad-2*p_lin*p_quad. At short duration this is approximately r*d+(omega_eff²/4)*d². Applying it quantitatively requires verified duration and scheduling. Pre-existing duration d0 causes the quadratic increment (d0+u)²-d0²=2*d0*u+u², so the descriptive linear coefficient cannot simply be called the linear idle rate.

Sources checked 2 November 2026:
- https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html
- https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html

## Comparison with H2-2E

| u | H2-1E P_L | H2-2E P_L | Two-sided Fisher p |
|---|---:|---:|---:|
| 0 | 0.30% | 0.20% | 1.000 |
| 0.1 | 0.40% | 0.50% | 1.000 |
| 0.5 | 1.60% | 1.70% | 1.000 |
| 0.75 | 4.60% | 4.80% | 0.916 |
| 1 | 11.50% | 14.00% | 0.107 |

Physical probabilities at u=0.5, 0.75, 1 are 3.056%, 5.989%, 10.144% on H2-1E, versus 3.044%, 5.967%, 10.133% on H2-2E. The physical growth is very similar. The documentation lists the same dephasing parameters for both emulators, making this similarity plausible, but it does not prove identical internal scheduling or effective noise.

No corresponding logical comparison establishes an emulator difference with these samples. At u=1, 11.5% versus 14.0% gives p=0.107. This is absence of resolved difference, not proof of equivalence or superior performance. The zero-control physical error being higher in this H2-1E sample should not be read as evidence against the nominal gate-error ordering.

## Conclusion

The fresh H2-1E sweep confirms a pronounced sleep-dependent increase in physical and decoded logical error probabilities, with the syndrome growth localized across the inserted wait. Its physical scaling closely matches H2-2E and is compatible with substantial quadratic memory noise. Neither dataset alone establishes a pure idle-noise rate, calibrated T2, physical seconds per raw argument, independent faults, or parallel waits. Matched idle-off/transport controls and verified timing are required for calibrated rates. Many-round logical probabilities and total physical duration must be measured before forming time-normalized logical-error metrics.

Artifacts: d3_sleep_five_point_h2_1e_1000.json; d3_sleep_five_point_h2_1e_noise_characterization.json; d3_sleep_five_point_emulator_comparison.json. Raw run: ../runs/d3_sleep_five_point_a2588f7078f6e696/. No new provider jobs were submitted.
