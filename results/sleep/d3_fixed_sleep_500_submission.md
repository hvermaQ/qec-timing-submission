# d=3 fixed requested sleep: H2-1E submission

Protocol: nine data qubits, one reused ancilla, four X stabilizers per round. Native QIR round blocks are cloned from the hash-pinned prior circuit, including the original conditional ancilla restoration/reset sequence and compiler-fused final basis rotations. Every pair of successive rounds is separated by nine equal sleep calls bounded by ten-qubit barriers. No artificial faults or offline flips. Sleep arguments are treated as seconds by agreement; overlap remains unverified. Extraction duration is neglected, so this is fixed requested sleep rather than verified fixed physical total duration.

| N | Delta t (s) | Exact fraction | Wait blocks | Total shots |
|---|---:|---|---:|---:|
| 2 | 1 | 1/1 | 1 | 500 |
| 5 | 0.25 | 1/4 | 4 | 500 |
| 10 | 0.111111111111 | 1/9 | 9 | 500 |
| 20 | 0.0526315789474 | 1/19 | 19 | 500 |
| 40 | 0.025641025641 | 1/39 | 39 | 500 |

Total requested sleep per data qubit is (N-1)*Delta t=1 second to double precision. Five free H2-1SC checks completed without item errors. Six H2-1E execution jobs were submitted; N=40 is split into two 250-shot jobs to avoid the historical 1,000-HQC/job ceiling. Requested noisy stabilizer simulation, no_opt=true, idle_dephasing=true, transport_dephasing=true; other backend defaults retained.

| Job | Shots | Aqora job ID |
|---|---:|---|
| n2_part1 | 500 | AFByb3ZpZGVySm9iAaGfGNfVdiCKOmWPC5nZyA |
| n5_part1 | 500 | AFByb3ZpZGVySm9iAaGfGN5PcLGFvG-7P5iz3Q |
| n10_part1 | 500 | AFByb3ZpZGVySm9iAaGfGOUZcYOgGWZ3gES-Xg |
| n20_part1 | 500 | AFByb3ZpZGVySm9iAaGfGOvVfbGVQVM5-z0pSw |
| n40_part1 | 250 | AFByb3ZpZGVySm9iAaGfGPOzfwOSJxV2rN2C2w |
| n40_part2 | 250 | AFByb3ZpZGVySm9iAaGfGPuweuCUuqzCetMs0A |

Gate-count HQC estimate (excludes/includes virtual Rz): total 1,749.7-2,005.1 HQCs, including the extra split-job overhead. Actual billing not returned. No additional jobs or control executions are authorized by the collector.

Validation: ten local tests passed, all five LLVM round-trips preserve call counts, all variable-round output schemas match syntax responses, and N=2 preserves the prior circuit quantum-call sequence exactly. Offline decoder contract checks corrected ideal shots and every isolated between-round data Z fault for all five N values.

Raw records: ../runs/d3_fixed_sleep_690baca08b24dfd2/; QIR, bitcode and manifest: ../programs/d3_fixed_sleep_690baca08b24dfd2/.
Collector: collect-and-decode-fixed-sleep-d3-sweep checks every 30 minutes, fetches only existing jobs, then decodes after all results are stored. It saves logical probabilities and Wilson intervals to d3_fixed_sleep_500.json/.md and reports whether a minimum is supported. Local scheduled collection requires the computer on and desktop app running. Provider jobs run independently.

Analysis command (requires NumPy, Stim, PyMatching, SciPy):
    PYTHONDONTWRITEBYTECODE=1 MPLCONFIGDIR=/private/tmp/qec-d3-mpl PYTHONPATH=src:/private/tmp/qec-d3-decoder-deps:SG_final_round/src python3 SG_final_round/src/analyze_fixed_sleep_d3.py
