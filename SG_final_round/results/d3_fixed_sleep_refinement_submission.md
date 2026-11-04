# H2-1E fixed-sleep refinement: submitted

Same d=3 X-memory implementation and native QIR blocks as the completed coarse sweep. Nine data qubits, one reused ancilla, four X checks per round, with nine explicit sleep calls between each pair of rounds. Total requested sleep is one second; extraction duration is neglected. Sleep arguments are treated as seconds by agreement; parallel overlap remains unverified. No artificial faults or offline readout flips. Backend options are unchanged: noisy stabilizer simulation, optimization disabled, idle and transport dephasing enabled, other backend defaults retained.

| N | Delta t (s) | New shots | Intended combined shots | H2-1E job ID |
|---|---:|---:|---:|---|
| 4 | 0.333333333333 | 1000 | 1000 | AFByb3ZpZGVySm9iAaGfuYxbctGSIKmNl9b4sA |
| 5 | 0.25 | 500 | 1000 | AFByb3ZpZGVySm9iAaGfuZKwe6OQxL30PfT9XA |
| 6 | 0.2 | 1000 | 1000 | AFByb3ZpZGVySm9iAaGfuZkNdiOR9-vNTanrqA |
| 7 | 0.166666666667 | 1000 | 1000 | AFByb3ZpZGVySm9iAaGfuaBtenO1QFvYapJYBg |
| 8 | 0.142857142857 | 1000 | 1000 | AFByb3ZpZGVySm9iAaGfuacafiKPKzuAphfdlQ |

Only 4,500 new shots were submitted across five jobs. Pool N=5 only with the original 500-shot fixed-sleep dataset: AFByb3ZpZGVySm9iAaGfGN5PcLGFvG-7P5iz3Q. Original results are unchanged. Exact Delta t is generated as 1/(N-1), rather than rounded table values.

All five free H2-1SC checks passed. LLVM assembly/round-trip call counts and all refinement round/wait/output counts were verified; ten local tests passed. N=5 QIR is byte-identical to the original source.

Estimated execution cost: 1,314.7-1,506.9 HQCs total, excluding/including virtual Rz billing and assuming no extra wait/barrier charge. This is not an actual bill.

Programs and manifest: ../programs/d3_fixed_sleep_refinement_3bb6e107a0ff6de3/.
Raw requests, job IDs and results: ../runs/d3_fixed_sleep_refinement_3bb6e107a0ff6de3/.
Configuration: ../configs/d3_fixed_sleep_refinement.json.
Automatic collection: collect-fixed-sleep-d3-refinement-results, every 30 minutes, fetches only existing IDs and stops when all raw results are stored. Local scheduled collection requires the computer on and desktop app running. No automatic decoding or changes to decoder methodology are included in this collector.

Manual collection:
    PYTHONDONTWRITEBYTECODE=1 SG_final_round/env/.venv-h2/bin/python SG_final_round/src/fixed_sleep_d3.py fetch-execute --refinement
