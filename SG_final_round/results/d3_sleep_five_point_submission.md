# Five-point d=3 sleep sweep: submitted, analysis deferred

Five fresh H2-1E jobs were submitted through Aqora (q_sq), 1,000 shots each,
for raw sleep arguments 0, 0.1, 0.5, 0.75, 1. All five H2-1SC checks passed.
The circuit and noise settings match the preceding three-point experiment:
nine data qubits, one reused ancilla, two rounds of four X-stabilizer checks,
sleep on each data qubit between rounds, barriers before and after the wait;
no artificial faults. Raw sleep units and wait overlap remain unverified.

The earlier three-point runs and results are preserved separately. This is
5,000 new emulator shots, with estimated cost 570–652 HQCs, not a billed quote.

| Variant | Emulator job ID |
|---|---|
| sleep_0p0 | AFByb3ZpZGVySm9iAaGbgdnsdkCMOqKxGIBYwA |
| sleep_0p1 | AFByb3ZpZGVySm9iAaGbgd_0eTOZK28S-fax0w |
| sleep_0p5 | AFByb3ZpZGVySm9iAaGbgeXrchGQdJCI-RlGJA |
| sleep_0p75 | AFByb3ZpZGVySm9iAaGbgezjc6KqvizAFNcATw |
| sleep_1p0 | AFByb3ZpZGVySm9iAaGbgfLwcCGWbrwVjtHZ2A |

Raw requests, job records and downloaded payloads are stored under
`../runs/d3_sleep_five_point_a2588f7078f6e696/execute/`.
The raw-file hashes and collection status are recorded in
`../runs/d3_sleep_five_point_a2588f7078f6e696/collection_status.json`.
Programs and hashes: `../programs/d3_sleep_five_point_a2588f7078f6e696/`.
Config: `../configs/d3_sleep_five_point_1000.json`.

The heartbeat `collect-aqora-five-point-d3-results` checks every 10 minutes,
fetches only existing job results, and pauses after all five payloads are saved.
It does not submit jobs, cancel jobs, or perform analysis. The computer must be
on and the desktop app running for scheduled local collection. Provider-side
jobs continue independently of the local collector. No raw outcomes have been
analyzed; analysis is deferred until the user's next explicit request.

Manual collection (never resubmits):

    PYTHONDONTWRITEBYTECODE=1 SG_final_round/env/.venv-h2/bin/python SG_final_round/src/d3_sleep_sweep.py fetch-execute --five-point
