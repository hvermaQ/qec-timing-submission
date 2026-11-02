# H2-2E five-point d=3 sleep sweep: submitted, analysis deferred

Five fresh jobs were submitted through Aqora (q_sq) to the H2-2E emulator,
1,000 shots each, for raw sleep arguments 0, 0.1, 0.5, 0.75, 1. All five free
H2-2SC syntax checks passed. No jobs were submitted to quantum hardware.

QIR and explicit options match the H2-1E five-point sweep exactly; only the
target emulator differs. Backend default noise parameters may differ between
emulators. There are nine data qubits, one reused ancilla, and two rounds of
four X-stabilizer checks with data-qubit sleep calls between barriers between
rounds. No artificial faults are injected. Raw sleep units and wait overlap
remain unverified.

The queued H2-1E jobs are preserved and continue independently.
Estimated additional execution cost: 570–652 HQCs; this is not a billed quote.

| Variant | H2-2E job ID |
|---|---|
| sleep_0p0 | AFByb3ZpZGVySm9iAaGb-E_weuOiSP2Hj2Jdfg |
| sleep_0p1 | AFByb3ZpZGVySm9iAaGb-FYJeyKLv_ofmAmwTA |
| sleep_0p5 | AFByb3ZpZGVySm9iAaGb-FxAduOd4MTqj3l2dg |
| sleep_0p75 | AFByb3ZpZGVySm9iAaGb-GOAehCbxwBeNWvUtg |
| sleep_1p0 | AFByb3ZpZGVySm9iAaGb-GmmcFCF0koVMVevlQ |

Raw requests, job records and result payloads:
`../runs/d3_sleep_five_point_h2_2e_67d11d0348065703/execute/`.
Collection status and file hashes are saved to that run's `collection_status.json`.
Programs: `../programs/d3_sleep_five_point_h2_2e_67d11d0348065703/`.
Config: `../configs/d3_sleep_five_point_h2_2e_1000.json`.

The existing heartbeat collect-aqora-five-point-d3-results now collects both
emulator sweeps every 30 minutes and stops once both sets of raw results are
saved. The computer must be on and the desktop app running for local collection.
Analysis remains deferred until the user explicitly requests it.

Manual raw collection (never submits jobs):

    PYTHONDONTWRITEBYTECODE=1 SG_final_round/env/.venv-h2/bin/python SG_final_round/src/d3_sleep_sweep.py fetch-execute --five-point --platform nexus:H2-2E
