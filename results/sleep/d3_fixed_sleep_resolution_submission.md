# H2-1E fixed-sleep additional minimum-resolution sweep

Same d=3 X-memory QIR protocol and noise options as the coarse and first-refinement sweeps. Four X checks per round, nine data qubits, one reused ancilla. Delta t=1/(N-1) seconds; accumulated requested sleep per data qubit is one second. Extraction duration is neglected and wait overlap remains unverified. No artificial faults, offline flips, or changes to decoder methodology.

| N | Delta t (s) | Additional shots | Total available after pooling | H2-1E job ID |
|---|---:|---:|---:|---|
| 3 | 0.5 | 500 | 500 | AFByb3ZpZGVySm9iAaGgw6Mmc_KLmuGYsQZmtg |
| 4 | 0.333333333333 | 1000 | 2000 | AFByb3ZpZGVySm9iAaGgw6jxelOwJP1HqPSezg |
| 5 | 0.25 | 1000 | 2000 | AFByb3ZpZGVySm9iAaGgw7DneCOXDPSvrFo_hA |
| 6 | 0.2 | 1000 | 2000 | AFByb3ZpZGVySm9iAaGgw7dFeqOrXSckDYeb3Q |
| 7 | 0.166666666667 | 1000 | 2000 | AFByb3ZpZGVySm9iAaGgw71pc-GZUFGpKnw4iQ |
| 8 | 0.142857142857 | 1000 | 2000 | AFByb3ZpZGVySm9iAaGgw8UXd8G3fk6Jonaf1Q |
| 10 | 0.111111111111 | 500 | 1000 | AFByb3ZpZGVySm9iAaGgw8wrfbOFa8qM8gBJnA |

Seven new execution jobs, 6,000 new shots. All seven free H2-1SC checks completed successfully. LLVM round-trip call counts, round/wait/output structure and ten local tests passed. QIR for all previously measured settings is identical to prior source. Prior configurations and datasets are unchanged.

Estimated total execution cost: 1,747.4-2,002.6 HQCs, excluding/including virtual Rz billing, assuming no additional sleep/barrier cost. Actual billing is not returned here.

Prior pooling sources: coarse d3_fixed_sleep_690baca08b24dfd2 and first refinement d3_fixed_sleep_refinement_3bb6e107a0ff6de3. For N=5 include the original 500 and first refinement 500 plus these new 1,000 shots exactly once. N=4,6,7,8 use prior 1,000 plus new 1,000; N=10 prior 500 plus new 500. N=3 is new.

Programs: ../programs/d3_fixed_sleep_resolution_c2380924e8c69578/.
Raw records: ../runs/d3_fixed_sleep_resolution_c2380924e8c69578/.
Configuration: ../configs/d3_fixed_sleep_resolution.json.
Heartbeat collect-d3-minimum-resolution-results collects raw results every 30 minutes and stops after all seven are saved and verified; it performs no outcome analysis. The computer must be on and desktop app running for local collection. Provider jobs continue independently.

Manual raw fetch:
    PYTHONDONTWRITEBYTECODE=1 SG_final_round/env/.venv-h2/bin/python SG_final_round/src/fixed_sleep_d3.py fetch-execute --resolution
