# Scratchpad

## Backend access (recorded 2026-11-02)

Participants will have access to the following Quantinuum backends throughout the challenge:
- H2-1
- H2-2
- Helios-1
- Helios-1E

Each team has been allocated **8000 HQCs** for use on H2-1 and H2-2.

Helios-1 and Helios-1E are available at low priority: expect longer queue times. Results
submitted to either Helios machine during the final few days of the challenge are not
guaranteed to complete, so submit jobs early.

Continued access to existing systems, as normal:
- H2-1
- H2-2
- H2-Emulator
- Selene

## HQC estimates of our programs (formula, not Quantinuum's price)

HQC = 5 + shots · (N1q + 10·N2q + 5·Nm) / 5000. Range: N1q = phasedx only .. phasedx + rz.

| program | shots | HQC |
| --- | --- | --- |
| d3, R = 2 (p 0 or 0.05) | 100 | 15–17 |
| d5, Δt = 5 (R = 2) | 1000 | 318–380 |
| d5, Δt = 2.5 (R = 4) | 1000 | 597–710 |
| d5, Δt = 1 (R = 10) | 1000 | 1432–1700 |
| d5, Δt = 0.5 (R = 20) | 1000 | 2824–3350 |
| d5, Δt = 0.14 (R = 70) | 1000 | 9784–11600 |

aqora's earlier "cost exceeds allowed cost (1002)" did not match this formula (R = 20 was accepted).
Exact price: `hardware.cli nexus-cost <program>.bc --shots N`.

## Open questions, as tests (one at a time, in order)

Each test fixes its question, method and decision rule before any shots are taken.
Status of what we have: the one-qubit sleep sweep on H2-1E (SG_final_round, 1000 shots at
sleep 0, 0.1, 0.5, 0.75, 1.0: 0, 0.1, 2.1, 5.5, 9.2%) is exploratory input, not one of these tests.

**T1. Is the sleep argument in seconds?** (emulator)
- Method: build the one-qubit probe through pytket + pytket-qir (official route) and check it emits
  the same `__quantum__qis__sleep__body` call as the hand edit; confirm the unit in Quantinuum docs.
- Decision: same call and a documented unit → use it; otherwise the unit stays "inferred".
- Cost: free (local build, syntax check).

**T2. Does sleep cause dephasing only, or also bit flips?** (emulator)
- Method: the same sweep in the Z basis (|0⟩ → sleep → measure Z) next to the X basis.
- Decision: Z-basis errors consistent with 0 at every t → pure dephasing.
- Cost: ~40 HQC (5 × 1000 shots).

**T3. What are the linear and quadratic idle terms?** (emulator)
- Method: X-basis sweep across the crossover (t ≈ 10 ms – 1 s, log-spaced), shots scaled so each
  point has ≥ 20 expected errors; fit P = a + b − 2ab, a = γt, b = sin²(πfk·t); check on P/t vs t.
- Decision: γ and fk with uncertainties; compare with the configured γ = 0.0028/s, fk = 0.086.
- Cost: dominated by short t (~1e5 shots near 40 ms): roughly 250–500 HQC.

**T4. Is sleep the same noise as idling inside a circuit?** (emulator)
- Method: a target that waits through L transport layers (barrier-ordered, RZZ(0) pairings as in
  Quantinuum's memory benchmark, no anchor) vs the same target slept; find the sleep that gives
  the same error as L layers.
- Decision: if errors match for some sleep t(L) ∝ L, one layer = t(L)/L in seconds; if waiting in
  a circuit costs more than any matching sleep, sleep misses transport dephasing.
- Cost: to be estimated after T3.

**T5. How long is one syndrome round?** (emulator)
- Method: d = 3 memory circuit with sleep s between rounds (SG_final_round build, no injection);
  measure the idle-type detector rate vs s; the round's own idle contribution equals the sleep s0
  that doubles it (or extrapolate to the zero-idle intercept).
- Decision: round time in seconds (via T1), or in layer units (via T4).
- Cost: d = 3 jobs, ~80–90 HQC per 1000 shots.

**T6. Does the hardware apply dynamical decoupling during sleep?** (H2-1, real device)
- Method: repeat T3's sweep (fewer points) on H2-1.
- Decision: errors well below the emulator curve and no quadratic growth → DD (or a quieter
  device); a match → no DD.
- Cost: ~7 HQC per 1000 shots per point (from the 8000 HQC budget).

**T7. Where is the optimum Δt in physical time?** (analysis, after T3–T6)
- Method: idle error per gap (T3/T6) vs extraction error per round (gate model; T5's round time)
  → λ and Δt = 1 in seconds; compare with the simulation notebooks' Δt*.
- Prediction to test (from the exploratory sweep): idling costs ~1e-4 per qubit for tens of ms
  against ~1e-2 per round of extraction, so the optimum gap is long (~0.1–1 s).
