# Single-qubit explicit-sleep sweep: 1,000 shots per setting

All five H2-1E jobs through Aqora (team q_sq) completed successfully. All five
free H2-1SC checks passed first. No no-sleep variant was submitted in this sweep.
The earlier 200-shot pilot is retained separately and is not pooled into these counts.

| Raw sleep argument | Errors / shots | Error rate | 95% Wilson interval |
|---|---:|---:|---:|
| 0 | 0 / 1000 | 0.00% | 0.00–0.38% |
| 0.1 | 1 / 1000 | 0.10% | 0.02–0.56% |
| 0.5 | 21 / 1000 | 2.10% | 1.38–3.19% |
| 0.75 | 55 / 1000 | 5.50% | 4.25–7.09% |
| 1 | 92 / 1000 | 9.20% | 7.56–11.15% |

The circuit uses virtual qubit 0, with the physical ion assigned by the backend:
implicit |0> preparation, Ry(pi/2), one explicit sleep, Ry(-pi/2), Z measurement.
The output m0=1 records an X-memory error. There are no injected Pauli faults,
ancillas, two-qubit gates or error correction. Every program retains both basis
rotations and its exact requested sleep argument after LLVM bitcode round-trip.

Requested backend options match the pilot: simulator=stabilizer,
noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true.

The error rate increases clearly with the sleep argument, providing evidence
for a duration-dependent noise effect in this one-qubit memory experiment.
This comparison does not independently verify seconds as the duration unit,
isolate the backend noise implementation, or determine a calibrated scaling law.
Zero observed errors at sleep(0) does not imply a zero background error rate.

Each formatted count was cross-checked against all 1,000 packed shot records.
Total emulator shots: 5,000. Gate-count HQC estimate: 5*(5+1000*12/5000)=37.
Actual charged HQCs were not returned in the saved result properties.

## Artifacts

- Config: `../configs/single_qubit_sweep_1000.json`.
- Circuits and build manifest: `../programs/single_qubit_sweep_73005efe45e835e4/`.
- Raw requests, job IDs and results: `../runs/single_qubit_sweep_73005efe45e835e4/`.
- Counts and intervals: `single_qubit_sweep_1000.json`.
- Builder, submission, fetch and analysis: `../src/single_qubit_sweep.py`.

Reproduce the analysis without submitting jobs:

    PYTHONDONTWRITEBYTECODE=1 python3 SG_final_round/src/single_qubit_sweep.py analyze

No additional jobs beyond the five syntax checks and five requested emulator runs were submitted.
