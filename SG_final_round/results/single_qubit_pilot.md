# Standalone one-qubit pilot

Requested execution: H2-1E through Aqora, team q_sq, 200 shots each of no sleep,
sleep(0), and sleep(0.5). No artificial errors are injected.

Programs: `../programs/single_qubit_2c64d96fea4bbbac/`.
Builder/runner: `../src/single_qubit_pilot.py`.
Job records and raw results: `../runs/single_qubit_2c64d96fea4bbbac/`.

One backend-assigned qubit (virtual q0) is implicitly prepared in |0>, rotated
by Ry(pi/2) into |+>, optionally slept, rotated by Ry(-pi/2), and measured in Z.
The output m0=1 means an X-memory error. No entangling gates, ancillas, explicit
reset, virtual Rz or error correction are used. Both native phased-X rotations
remain in each assembled bitcode. Local state-vector calculation verifies ideal
output 0 and output 1 following a single Z error. It does not verify sleep noise.

The raw value 0.5 is not yet a verified physical duration. Requested emulator
options: noisy stabilizer simulation, idle and transport dephasing enabled,
no_opt=true. All three syntax checks and all three H2-1E execution jobs completed successfully. At the earlier
conditional factor-2 model estimate, 200 shots give only ~3.9 added faults at
0.5 seconds: a small pilot cannot establish the full scaling law.

Gate-count cost estimate: 2 physical 1q gates, no 2q gates, 1 implicit preparation
and 1 measurement. HQC = 5 + 200*(2 + 5*2)/5000 = 5.48 per job, 16.44 total.
This assumes accepted instruction semantics and no extra sleep charge; it is not
a provider quote. Syntax-check results are placeholders, never experimental data.

Initial upload failed with Missing Authorization before creating a job. Aqora
browser login then succeeded, and the free syntax checks were started.

## Completed H2-1E results

| Setting | Shots | X-memory errors (m0=1) | Error rate | 95% Wilson interval |
|---|---:|---:|---:|---:|
| No sleep | 200 | 0 | 0% | 0–1.88% |
| sleep(0) | 200 | 0 | 0% | 0–1.88% |
| sleep(0.5) | 200 | 2 | 1.00% | 0.27–3.57% |

These are emulator results, not syntax-check placeholders. Formatted counts were
cross-checked against all 200 packed shot records for each job. Both control jobs
returned all-zero m0; the finite-sleep job returned 198 zeros and two ones.

The tested sleep signature is accepted in this Aqora → H2-1E QIR pathway and the
programs return results. The observed finite-sleep errors are consistent with a
wait effect, but this small pilot cannot demonstrate that sleep caused them,
verify seconds as the argument unit, or determine linear/quadratic scaling.
Zero errors in a control does not establish a zero background error rate.
Provider-reported job duration is not a calibration of the sleep argument.

No further paid runs were submitted. Total requested emulator shots: 600.
The returned result properties contain no HQC charge, so 16.44 HQCs remains an
estimate, not a verified billed amount. The native circuit contains no Rz, so
there is no virtual-Rz ambiguity in this updated gate-count estimate.

Machine-readable results and job IDs: `single_qubit_pilot_counts.json`.
Reproduce the summary with:

    PYTHONDONTWRITEBYTECODE=1 python3 SG_final_round/src/analyze_single_qubit_pilot.py

Re-fetch existing jobs if needed (never resubmits):

    PYTHONDONTWRITEBYTECODE=1 SG_final_round/env/.venv-h2/bin/python SG_final_round/src/single_qubit_pilot.py fetch
