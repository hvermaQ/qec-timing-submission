# Proposed shots and cost — no submissions

Use H2-1E initially: published dephasing parameters match H2-2E, while its
gate/readout fault probabilities are lower. It also matches the saved calibration.
Source: https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html

The current build (5944c048c1dfdc80) is a ten-qubit d=3 circuit, with one sleep
target. A standalone one-qubit probe is a proposed next circuit, not built here.
For measuring idle noise, prefer prepare |+>, sleep, measure X (equivalently
prepare |0>, H, sleep, H, measure Z). A Z-basis memory probe misses pure dephasing.
Preserve the delay against gate cancellation and verify the resulting QIR.

After verifying instruction support and units, recommend 10,000 shots each for
no sleep, sleep(0), 0.01, 0.05, 0.1, 0.2, 0.5: 70,000 shots total. This is a first
scaling measurement, not a precision calibration at all durations. Conditional
on seconds and the saved factor-2 model, expected wait faults per finite point
are 0.35, 3.22, 10.09, 34.74, 194.87. The two shortest waits are weak-signal
controls; background subtraction further reduces sensitivity. Simulator mode,
DD and scheduling must be recorded before comparing to this prediction.

As a separate initial pilot, 200 shots each at no sleep, sleep(0), and 0.5 can
test execution and look for a large effect. A flat pilot is inconclusive; it
must not gate further investigation solely on statistical significance.

Published formula: HQC = 5 per job + shots*(N1q + 10*N2q + 5*Nm)/5000.
Nm includes implicit preparation, all measurements and resets; H2 charges all
conditional branches. Syntax checks are free. The historical aqora wrapper
did not expose a reliable price quote, so these are estimates, not reservations.
Source: https://docs.quantinuum.com/systems/user_guide/hardware_user_guide/workflow.html

| Circuit | Counts (physical 1q, virtual Rz, 2q, Nm) | Jobs | Full sweep HQC |
|---|---|---|---|
| Proposed standalone 1q | 2, up to 2, 0, 2 | 7 x 10,000 shots | 203–231 |
| Existing d=3, sleep only on q4 | 90, 82, 24, 43 | 14 x 5,000 shots | 7,700–8,848 |

Ranges exclude/include virtual Rz in billing because H2-specific billing for
these instructions has not been verified. One-qubit counts assume a minimal
native implementation; d=3 counts come from the actual generated QIR metadata.
There is no duration term in the published formula; these estimates assume no
extra sleep charge. Actual acceptance, backend lowering and quotes take priority.
The d=3 job split keeps each job at 550–632 HQC, below the historically observed
aqora 1,000-HQC/job ceiling; confirm the current account limit.

The optional three-job pilot adds 16.44–16.68 HQC for standalone 1q, or
80.40–90.24 HQC for d=3. Thus pilot plus full standalone sweep is 219.44–247.68
HQC. Reserve approximately 250 HQC for that plan before retries. A 1,000-shot
per-setting d=3 screening sweep instead costs 798–912.8 HQC, but cannot resolve
the shortest waits. Do not use d=3 logical failure rate alone: q4 errors may be
corrected, so examine detector outcomes.

Numerical budget inputs and totals: `hqc_estimate.json`. Conditional noise
predictions: `duration_scales.json`. No paid jobs have been submitted.
