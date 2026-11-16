# d=5 H2-2E: five 500-shot execution requests

Authorized N=5,6,7,8,10, 500 shots each (2,500 shots). Uses the exact previously validated native QIR with fixed requested sleep of one second per data qubit, Delta t=1/(N-1), X-memory sector and no artificial injected faults. Noise options: stabilizer, noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true. Existing H2-1E jobs are preserved.

Gate-count cost estimate: 2,683.1 HQC if all five are accepted, including five execution-job overheads. H2-2SC validation is required before execution.

| N | Shots | Status | HQC reported | Job ID |
|---:|---:|---|---:|---|
| 5 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiEPjfe2KTBq0KJMpIow |
| 6 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiEQJSeoCwwyrKt1W_3g |
| 7 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiEQmjdLK8y4LgWD0mrw |
| 8 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiERCscBKpTu8T8N3-sA |
| 10 | 500 | Job cost exceeds allowed cost (code: 1002) | 0.0 | AFByb3ZpZGVySm9iAaGiERh-cvKELIPruFKKLw |

No further retries or additional shots submitted. Provider costs for waiting jobs are not final completed-execution billing.
Raw records: `/Users/harshank_s/qec-timing-submission/SG_final_round/runs/d5_fixed_sleep_h2_2e_500_n5_6_7_8_10`.
