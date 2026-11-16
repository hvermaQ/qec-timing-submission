# d=5 H2-2E: four 500-shot execution requests

Authorized N=7,8,9,10, 500 shots each (2,000 shots). Uses the exact previously validated native QIR with fixed requested sleep of one second per data qubit, Delta t=1/(N-1), X-memory sector and no artificial injected faults. Noise options: stabilizer, noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true. Existing H2-1E jobs are preserved.

Gate-count cost estimate: 2,508.4 HQC if all four are accepted, including four execution-job overheads. H2-2SC validation is required before execution.

| N | Shots | Status | HQC reported | Job ID |
|---:|---:|---|---:|---|
| 7 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGq5tyrcVC0l6uy96ecmA |
| 8 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGq5uT2fqCoWXdsylUhzQ |
| 9 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGq5ug-cWGTuwELlgGKMg |
| 10 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGq5utieVCvWXhm0Zxr6w |

No further retries or additional shots submitted. Provider costs for waiting jobs are not final completed-execution billing.
Raw records: `/Users/harshank_s/qec-timing-submission/SG_final_round/runs/d5_fixed_sleep_h2_2e_renewed_20261105_500_n7_8_9_10`.
