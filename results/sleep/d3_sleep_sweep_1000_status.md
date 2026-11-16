# d=3 all-data sleep with stabilizer extraction: emulator jobs submitted

Final update: all three jobs completed. See `d3_sleep_sweep_1000.md` for the
final analysis (decoded logical failures 3, 13, 115 / 1,000). The text below
is a historical preparation/submission record.

Update: the user explicitly authorized emulator submission despite unresolved
wait overlap. Three H2-1E jobs, 1,000 shots each, are now submitted:

- sleep(0): AFByb3ZpZGVySm9iAaGbWgzzd8KcJnrXT8rg7Q
- sleep(0.5): AFByb3ZpZGVySm9iAaGbWhNre5C4DxAeR0Iu0w
- sleep(1): AFByb3ZpZGVySm9iAaGbWhlCc4C5imMeU1O2dw

The original pre-submission record below is retained as history. Its timing
limitation remains. Execution does not establish simultaneous waits.

The three free H2-1SC checks through Aqora (team q_sq) completed without result
errors. No H2-1E execution jobs have been submitted, so no measured error rates
are available and no emulator HQCs have been spent on this sweep.

## Prepared circuits

Reuse the archived d=3 X-memory circuit: nine data qubits (0–8), one reused
ancilla (9), and two rounds of four X-stabilizer checks. This circuit extracts
only the X-check sector; it does not perform both X- and Z-check extraction or
prepare a fully encoded surface-code state.

After the first round's final ancilla reset, insert a ten-qubit barrier, nine
single-qubit sleep calls with the same raw argument, and another ten-qubit
barrier before the second extraction round. No sleep targets the ancilla.
Final X-basis readout and all 17 original syndrome/data output labels remain.
There are no artificial Pauli errors or offline flips.

Raw arguments: **0, 0.5, 1**. Planned execution: **1,000 shots per argument**,
with all nine data qubits measured on each shot. The zero variant contains all
nine explicit sleep calls. Units remain unverified. Backend options match the
single-qubit experiment: H2-1E stabilizer simulator, noisy simulation enabled,
optimization disabled, idle and transport dephasing enabled.

| Raw argument | H2-1SC job ID | Status | H2-1E |
|---|---|---|---|
| 0 | AFByb3ZpZGVySm9iAaGbVMGIceCfC_PXFOhkjg | COMPLETED, no item errors | Not submitted |
| 0.5 | AFByb3ZpZGVySm9iAaGbVMdGdVCWlXAoEaRajg | COMPLETED, no item errors | Not submitted |
| 1 | AFByb3ZpZGVySm9iAaGbVM1_dRKXixyNm-zCOw | COMPLETED, no item errors | Not submitted |

## Parallel scheduling remains unverified

The requirement is one common wait interval for all nine data qubits. The
barriers constrain operation ordering; neither those barriers nor syntax
acceptance establish identical start/end times for the nine sleeps.

Quantinuum's public QIR converter emits sleep on only one qubit per call:
https://docs.quantinuum.com/tket/extensions/pytket-qir/_modules/pytket/qir/conversion/qirgenerator.html
Its barrier signatures support the barriers used here, but the converter does
not specify backend overlap of separate sleeps. The PHIR converter represents
an Idle on a list of qubits with duration in seconds; this is a different
representation and does not establish semantics of these QIR calls:
https://github.com/Quantinuum/pytket-phir/blob/main/pytket/phir/phirgen.py

The saved Aqora syntax results have empty properties and do not provide a
schedule or an HQC quote. Verification requires a backend schedule showing a
common wait interval, or authoritative confirmation of this exact QIR pattern.
Matching error rates alone would not establish overlap. The execution action
fails before any provider access until this requirement can be established.

## HQC estimate

Published H2 formula: 5 + shots*(N1q + 10*N2q + 5*Nm)/5000.
Source: https://docs.quantinuum.com/systems/user_guide/hardware_user_guide/workflow.html

The archived circuit contains 90 phased-X gates, 82 virtual Rz gates, 24
two-qubit gates, 17 measurements, 16 resets, and 10 implicit preparations.
Thus Nm=43. Excluding/including virtual Rz in the billed one-qubit count gives
**114.0–130.4 HQC per 1,000-shot job**, or **342.0–391.2 HQC total**.
This assumes no additional sleep/barrier charge and no extra backend lowering
cost. It is an estimate, not an actual bill. Syntax checks are free.
The earlier 79.8 HQC estimate applied to independent nine-qubit probes without
extraction and does not apply to these circuits.

## Validation and artifacts

Seven local tests passed. All three bitcodes assembled at O0 and round-tripped
with quantum/runtime call counts and QIR entry attributes preserved. Tests
verify nine distinct data-qubit targets, exact arguments, no ancilla sleep, and
placement after four syndrome measurements and before the remaining thirteen
measurements. These are structural checks, not timing verification.

- Builder: `../src/d3_sleep_sweep.py`
- Config: `../configs/d3_sleep_sweep_1000.json`
- QIR, bitcodes, round-trips, manifest: `../programs/d3_sleep_sweep_f219bffeea86811d/`
- Requests and original check responses: `../runs/d3_sleep_sweep_f219bffeea86811d/check/`

An initial restricted-network attempt failed during platform discovery, before
job submission. Its request was archived as `request.failed_before_submission.json`;
the subsequent successful attempt submitted exactly the three jobs above.
