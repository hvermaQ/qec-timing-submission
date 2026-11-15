# Physical H2-2 d=5 circuit audit — 2026-11-14

The five submitted d=5 programs pass an independent ideal-Clifford audit. Six physical d=3 reference programs also pass, consistent with the successful d=3 finite-sleep experiments. No production circuit, decoder policy, or hardware submission was changed.

## Checks and results

- Verified the saved submitted bitcode hashes for d=5 N=2,3,4,6,10 and d=3 N=2,3,5,6,10,20.
- Disassembled those exact bitcode files with clang and translated native phased-X, Rz, Rzz, measurement, and reset operations into Stim via their unitary matrices.
- Conditional measurement-restoration branches act solely on the ancilla and immediately rejoin at an ancilla reset. Their execution cannot affect subsequent ideal behavior; the translator checks this before flattening them.
- Checked unique result registers and complete unique output-tag mappings.
- All ideal measurements have exact +1 Z expectation immediately before measurement (zero output); independently sampled 4,096 ideal shots per circuit. No nonzero syndrome or final-data outputs occurred.
- The original compiled d=5 five-round source also passes the ideal check.
- Injected a single Z fault on each data qubit at every wait boundary. All subsequent X-check outputs and final-data bits match the code's expected support parity: 500 d=5 cases and 360 d=3 cases passed.
- Sleep gates are treated as identity in this ideal audit. It does not model finite-duration dephasing, transport, calibration drift, leakage, or provider-side lowering/scheduling. It is not proof of correctness under every possible physical fault.

## Hardware localization

The check with support {5,6,10,11} shows a large jump at the third extraction in each N>=3 job. Third-extraction detection events (successive syndrome XOR) occur in 360/750, 458/1000, 324/750, and 217/500 shots for N=3,4,6,10.

For N=3,4,6 respectively, Q5 final errors occur in 70.6%, 72.3%, 75.0% of shots with this event, compared with 16.9%, 17.0%, 17.6% without it. The association weakens at N=10 (55.3% versus 43.1%). The shared check does not uniquely identify Q5 as the origin; it includes Q6, Q10 and Q11. Correlation is not a causal diagnosis.

Q5 remains elevated across all five consecutive record-order blocks of each N>=3 job. These blocks are descriptive and are not identified physical execution chunks.

## Interpretation and next step

No submitted-program error was found in the audited behavior. The d=3 evidence is consistent with this result. The remaining explanations include finite-wait effects, transport/scheduling, correlated physical faults, and backend behavior not visible in the submitted program. The data do not establish a defective physical ion.

The next discriminating paid experiment, if authorized, is d=5 N=3 with explicit zero sleep, 250 shots (estimated 124.65 HQC). This tests the third extraction absent intentional finite waiting. It has not been submitted. Preserve the finite-sleep results and frozen decoder; avoid treating N=6's sample minimum as a calibrated timing optimum until this anomaly is understood.

Artifacts: `ideal_audit.json` records the circuit checks, `third_extraction_diagnostics.json` records the hardware associations, and the .ll/.stim files permit inspection of the disassembled and translated programs. Reproduce with `python3 SG_final_round/src/audit_native_memory.py` in an environment with NumPy and Stim.
