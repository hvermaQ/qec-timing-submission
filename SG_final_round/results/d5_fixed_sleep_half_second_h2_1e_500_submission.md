# d=5 H2-1E: half-second fixed-sleep sweep

Authorized N=3,4,5,6, 500 shots each (2,000 shots). Uses the pinned native extraction circuit with fixed requested sleep of 0.5 seconds per data qubit, Delta t=0.5/(N-1), X-memory sector and no artificial injected faults. Noise options: stabilizer, noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true. Existing H2-1E jobs are preserved.

Gate-count cost estimate: 1,394.8 HQC if all four are accepted, including four execution-job overheads. H2-1SC validation is required before execution.

| N | Shots | Status | HQC reported | Job ID |
|---:|---:|---|---:|---|
| 3 | 500 | WAITING | 244.3 | AFByb3ZpZGVySm9iAaGiJxjQcFGyRWIw7DeXng |
| 4 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiJyCKefGbdVOiWWhP5g |
| 5 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiJymRdgCZZZjwNN-wdA |
| 6 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiJzNJfFOtCJb0tPfnCA |

No further retries or additional shots submitted. Provider costs for waiting jobs are not final completed-execution billing.
Raw records: `/Users/harshank_s/qec-timing-submission/SG_final_round/runs/d5_fixed_sleep_half_second_h2_1e_500_n3_4_5_6`.
