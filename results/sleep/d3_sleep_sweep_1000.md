# d=3 X-memory sleep sweep: completed H2-1E results

All three Aqora jobs (team q_sq) completed on 2 November 2026, with 1,000
shots per setting. Each circuit contains nine data qubits and one reused
ancilla, two rounds of four X-stabilizer checks, and a nine-call sleep block
between rounds bounded by ten-qubit barriers. There are no artificial faults
or offline readout flips. This is X-sector surface-code memory, not a test of
both stabilizer sectors or arbitrary encoded states.

| Raw sleep argument | Decoded logical failures / shots | Logical error rate | 95% Wilson interval | Raw logical parity flips |
|---|---:|---:|---:|---:|
| 0 | 3 / 1000 | 0.30% | 0.10–0.88% | 4 / 1000 |
| 0.5 | 13 / 1000 | 1.30% | 0.76–2.21% | 67 / 1000 |
| 1 | 115 / 1000 | 11.50% | 9.67–13.63% | 228 / 1000 |

Rates are per complete two-round experiment, not per extraction round or unit
time. A logical failure is the final X-logical parity on data qubits 0,3,6 XOR
the decoder's predicted logical correction. Raw parity flips are reported
separately and are not the decoded logical error rate.

## Decoder and validation

The primary decoder is the repository's historical d=3 minimum-weight perfect
matching decoder using the phenomenological graph with p_data=0.002 per round,
p_read=0.001, lam=0. Identical decoder weights were fixed across all settings;
no decoder was fitted to these returned shots. These are decoder-model
assumptions, not injected errors. Repeating decoding at p_data=0.02 and 0.1
with the same p_read produced the same failure counts (3, 13, 115).
The decoder is not a calibrated maximum-likelihood model of this backend's
sleep scheduling or correlated errors.

All 3,000 packed shot records match the provider's formatted joint counts.
All 17 expected syndrome/data registers were verified as Boolean. Local
validation also checked the ideal case and all nine possible single-data Z
faults between rounds: all were corrected by the primary decoder. Seven
structural tests passed, and the submitted bitcodes retain the original
extraction gates, outputs, and exact sleep calls after assembly round-trip.

## Where the changes occur

| Raw argument | Mean first-round detector rate | Mean inter-round detector rate | Mean final-boundary detector rate |
|---|---:|---:|---:|
| 0 | 0.45% | 0.75% | 0.375% |
| 0.5 | 0.35% | 7.575% | 0.525% |
| 1 | 0.30% | 23.85% | 0.725% |

Each mean averages the four checks at that boundary, not independent trials.
The large increase is concentrated between the extraction rounds, where the
sleep block was inserted. The first-round rates remain low. All nine final
X-basis data-qubit error rates rise with the raw sleep argument:

| Data qubit | sleep(0) | sleep(0.5) | sleep(1) |
|---|---:|---:|---:|
| 0 | 0.1% | 2.4% | 9.0% |
| 1 | 0.1% | 2.4% | 11.2% |
| 2 | 0.3% | 2.7% | 10.4% |
| 3 | 0.3% | 1.7% | 10.4% |
| 4 | 0.3% | 2.7% | 10.3% |
| 5 | 0.1% | 2.2% | 9.1% |
| 6 | 0.0% | 3.0% | 10.4% |
| 7 | 0.3% | 3.2% | 10.3% |
| 8 | 0.1% | 3.4% | 9.8% |

Compared with sleep(0), decoded logical failure increases by 1.0 percentage
point at 0.5 and 11.2 points at 1. Exploratory two-sided Fisher tests give
p=0.0208 and p=6.05e-32 respectively, assuming independent shots and jobs.
These comparisons do not measure run-to-run variability; there is one job
per setting, submitted in increasing argument order, with no supplied emulator
random seed or independent repeated jobs.

## Interpretation: sleep-dependent, not established as purely idle noise

The three QIR programs differ only in the raw sleep argument; gates,
barriers, shots, and requested backend noise options match. The monotonic
data-error increase and its concentration across the wait provide strong
evidence for an added sleep-dependent memory-error effect. Error correction
reduces the observed logical-parity flip rate but does not remove the increase.

It would be too strong to attribute the full logical error rate, or uniquely
its increment, to pure idle dephasing. The baseline includes gate,
preparation, readout, and extraction noise. Idle and transport dephasing are
both enabled, and their combination with other faults and the decoder is
nonlinear. Changing a sleep can also change backend scheduling. The emulator
keeps unspecified noise channels enabled; its documented memory noise depends
on both idling and transport duration. See the official noise model:
https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html

No noise-off or dephasing-disabled execution was submitted. Such controls,
with other parameters fixed, would help isolate the responsible noise channel.
Raw argument units and simultaneous overlap of the nine sleeps remain
unverified. Barriers and successful syntax checks establish neither.
The observed data-qubit scaling is consistent with a common wait, but is not
a backend timing trace and cannot prove parallel execution.

## HQCs and provenance

Three syntax checks were free. Gate-count execution estimate: 114.0–130.4 HQCs
per job, or **342.0–391.2 HQCs total**, excluding/including virtual Rz billing
and assuming no additional sleep/barrier charge. Actual billed HQCs were not
returned: all three result properties are empty. Cost formula:
https://docs.quantinuum.com/systems/user_guide/hardware_user_guide/workflow.html

| Raw argument | H2-1E job ID |
|---|---|
| 0 | AFByb3ZpZGVySm9iAaGbWgzzd8KcJnrXT8rg7Q |
| 0.5 | AFByb3ZpZGVySm9iAaGbWhNre5C4DxAeR0Iu0w |
| 1 | AFByb3ZpZGVySm9iAaGbWhlCc4C5imMeU1O2dw |

- Full counts, intervals, comparisons, hashes and versions: `d3_sleep_sweep_1000.json`.
- Original requests, job responses and results: `../runs/d3_sleep_sweep_f219bffeea86811d/execute/`.
- QIR, bitcode, validation and decoder DEMs: `../programs/d3_sleep_sweep_f219bffeea86811d/`.
- Submission and fetch: `../src/d3_sleep_sweep.py`.
- Reproducible analysis: `../src/analyze_d3_sleep_sweep.py` (NumPy, Stim, PyMatching, SciPy).

Only the three authorized 1,000-shot emulator jobs were submitted; no
additional execution controls or retries were submitted.
