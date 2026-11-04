# d=5 fixed-requested-sleep H2-1E submission

Authorized 3 November 2026. All 25 execution requests sent via Aqora as q_sq, totaling 13,000 requested shots. **Partial acceptance: five jobs (2,667 shots) are WAITING; 20 jobs (10,333 shots) returned “Job cost exceeds allowed cost (code: 1002)”. The full sweep is not queued.** All 11 H2-1SC checks completed without item errors before execution submission. All 13 local structural tests passed.

X-memory sector: 25 data qubits and one reused ancilla, 12 X checks per round. Prepare all data in |+>, N extraction rounds, N-1 all-data sleep blocks, final X readout. Delta t = 1/(N-1) seconds; total requested sleep is one second per data qubit. Extraction duration is neglected and physical parallel sleep overlap remains unverified.

Options: stabilizer simulator, noisy_simulation=true, no_opt=true, idle_dephasing=true, transport_dephasing=true; other defaults retained. No artificial Pauli faults or offline readout flips. Pinned native QIR blocks from results/hardware/programs/d5_X_r5_p0.ll, retaining the final-round compiler-moved basis rotations.

Initial estimated execution cost: **15,464.4–17,768.0 HQC**, excluding/including virtual Rz billing, assuming no additional sleep/barrier charge. Includes 5 HQC overhead for each of 25 jobs. This is a gate-count estimate, not actual billing. Planning budget: 17,800 HQC, excluding retries.

Per-shot counts: physical 1q=116N+50, virtual Rz=104N+50, 2q=40N, preparation/measurement/reset=36N+51. HQC=5 per job + shots*(N1q+10*N2q+5*Nm)/5000. Conservative splits keep each estimated job below the historical 1,000-HQC ceiling, even including Rz.

| N | Delta t (s) | Shots | Shot splits | Estimated HQC |
|---:|---:|---:|---|---:|
| 2 | 1 | 500 | 500 | 174.7–200.5 |
| 3 | 0.5 | 500 | 500 | 244.3–280.5 |
| 4 | 0.3333333 | 500 | 500 | 313.9–360.5 |
| 5 | 0.25 | 500 | 500 | 383.5–440.5 |
| 6 | 0.2 | 2000 | 667 + 667 + 666 | 1807.4–2077.0 |
| 7 | 0.1666667 | 2000 | 667 + 667 + 666 | 2085.8–2397.0 |
| 8 | 0.1428571 | 2000 | 667 + 667 + 666 | 2364.2–2717.0 |
| 9 | 0.125 | 2000 | 500 + 500 + 500 + 500 | 2647.6–3042.0 |
| 10 | 0.1111111 | 2000 | 500 + 500 + 500 + 500 | 2926.0–3362.0 |
| 15 | 0.07142857 | 500 | 250 + 250 | 1084.5–1245.5 |
| 20 | 0.05263158 | 500 | 250 + 250 | 1432.5–1645.5 |

## Execution job IDs

| Setting / part | Shots | Aqora job ID |
|---|---:|---|
| n2_part1 | 500 | AFByb3ZpZGVySm9iAaGh9ZhIdJKUHjfzj6faKQ |
| n3_part1 | 500 | AFByb3ZpZGVySm9iAaGh9aIpeOCwZYpJAaxv0A |
| n4_part1 | 500 | AFByb3ZpZGVySm9iAaGh9azpeLGTJGRxMyDT9g |
| n5_part1 | 500 | AFByb3ZpZGVySm9iAaGh9bNPfRKRYbLP8CHB1A |
| n6_part1 | 667 | AFByb3ZpZGVySm9iAaGh9boXefKot0ydZs8b_g |
| n6_part2 | 667 | AFByb3ZpZGVySm9iAaGh9cCpc-KAS2IUCMhHpw |
| n6_part3 | 666 | AFByb3ZpZGVySm9iAaGh9ceocMOdDJp_8suX8Q |
| n7_part1 | 667 | AFByb3ZpZGVySm9iAaGh9c9hfSOTqmh-A025aA |
| n7_part2 | 667 | AFByb3ZpZGVySm9iAaGh9dxOenOJWfSwJ581PA |
| n7_part3 | 666 | AFByb3ZpZGVySm9iAaGh9ePMfyG474vJxxk8rw |
| n8_part1 | 667 | AFByb3ZpZGVySm9iAaGh9exbdyKKSB_WN4nDJw |
| n8_part2 | 667 | AFByb3ZpZGVySm9iAaGh9fOPdIGcuM-BstWgbg |
| n8_part3 | 666 | AFByb3ZpZGVySm9iAaGh9fq8cHGX6AAV1dZxiQ |
| n9_part1 | 500 | AFByb3ZpZGVySm9iAaGh9gIcfIKvPnIZM-L69w |
| n9_part2 | 500 | AFByb3ZpZGVySm9iAaGh9gl7ekKA1Vfv7HVUqA |
| n9_part3 | 500 | AFByb3ZpZGVySm9iAaGh9hEafOCZNWgGwBLx-g |
| n9_part4 | 500 | AFByb3ZpZGVySm9iAaGh9hjDfjCjVdpTCjVZ4g |
| n10_part1 | 500 | AFByb3ZpZGVySm9iAaGh9iK3cuK59BWB1zUo0A |
| n10_part2 | 500 | AFByb3ZpZGVySm9iAaGh9irrc5Oy6Rirz_lVnQ |
| n10_part3 | 500 | AFByb3ZpZGVySm9iAaGh9jN4cGGXUP8knXS_kg |
| n10_part4 | 500 | AFByb3ZpZGVySm9iAaGh9jwLcnCWLjhUkCT3Nw |
| n15_part1 | 250 | AFByb3ZpZGVySm9iAaGh9kYJf7ObRfJdgEOS_A |
| n15_part2 | 250 | AFByb3ZpZGVySm9iAaGh9k8yfOG_cSlARv8gOg |
| n20_part1 | 250 | AFByb3ZpZGVySm9iAaGh9lfucLKDjtIjg0HJHQ |
| n20_part2 | 250 | AFByb3ZpZGVySm9iAaGh9mEwfZCiyHyVfkucJQ |

## Saved records

- Build and bitcode hashes: `SG_final_round/programs/d5_fixed_sleep_9fb82150bc37143a/manifest.json`.
- Exact allocation and cost estimate: `SG_final_round/configs/d5_fixed_sleep_13000.json`.
- Raw job requests, IDs, statuses and available results: `SG_final_round/runs/d5_fixed_sleep_9fb82150bc37143a/`.
- Builder/collector: `SG_final_round/src/fixed_sleep_d5.py`; action `fetch-execute` retrieves only the existing jobs. It never submits further jobs.
- Tests: `SG_final_round/tests/test_fixed_sleep_d5.py`.

No recurring collector was added. Results are not yet decoded; this record confirms attempted submission and partial acceptance, not successful completion or final billing. No rejected jobs have been retried.

## Initial provider response

| Setting / part | Shots | Status / error |
|---|---:|---|
| n2_part1 | 500 | WAITING |
| n3_part1 | 500 | WAITING |
| n4_part1 | 500 | WAITING |
| n5_part1 | 500 | WAITING |
| n6_part1 | 667 | WAITING |
| n6_part2 | 667 | Job cost exceeds allowed cost (code: 1002) |
| n6_part3 | 666 | Job cost exceeds allowed cost (code: 1002) |
| n7_part1 | 667 | Job cost exceeds allowed cost (code: 1002) |
| n7_part2 | 667 | Job cost exceeds allowed cost (code: 1002) |
| n7_part3 | 666 | Job cost exceeds allowed cost (code: 1002) |
| n8_part1 | 667 | Job cost exceeds allowed cost (code: 1002) |
| n8_part2 | 667 | Job cost exceeds allowed cost (code: 1002) |
| n8_part3 | 666 | Job cost exceeds allowed cost (code: 1002) |
| n9_part1 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n9_part2 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n9_part3 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n9_part4 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n10_part1 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n10_part2 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n10_part3 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n10_part4 | 500 | Job cost exceeds allowed cost (code: 1002) |
| n15_part1 | 250 | Job cost exceeds allowed cost (code: 1002) |
| n15_part2 | 250 | Job cost exceeds allowed cost (code: 1002) |
| n20_part1 | 250 | Job cost exceeds allowed cost (code: 1002) |
| n20_part2 | 250 | Job cost exceeds allowed cost (code: 1002) |

Identical 667-shot N=6 jobs received different responses (first waiting, second cost-rejected), suggesting a cumulative available-credit or budget constraint rather than a deterministic per-job gate-cost ceiling. This remains unconfirmed. Quantinuum describes code 1002 as insufficient funds or a maximum-cost restriction. The Aqora schema exposes job hqcCost but no team balance/quota field in the inspected Entity/Organization/ProviderPlatform types.

## Provider-reported costing

Read-only GraphQL retrieval of ProviderJob.hqcCost confirms that H2-1E and H2-1SC prices match the physical-single-qubit-only estimate (virtual Rz excluded). All 11 one-shot syntax-check quotes match 5+(696N+305)/5000. Thus the full requested allocation with the existing 25-job split is **15,464.4 HQC**.

The five WAITING execution jobs have provider-reported costs totaling **1,719.1654 HQC**. The remaining intended shots would cost approximately **13,745.2346 HQC** with unchanged splits. Rejected jobs each report hqcCost=0.0. These pending-job costs are not a final completed-execution bill. Raw cost/status evidence: `SG_final_round/runs/d5_fixed_sleep_9fb82150bc37143a/provider_cost_status.json`.

Provider error-code reference: https://docs.quantinuum.com/systems/support/troubleshooting.html . Code 1002 indicates insufficient funds or a restricted maximum cost; the exact account constraint has not been exposed. No account settings were changed and no rejected jobs were resubmitted.
