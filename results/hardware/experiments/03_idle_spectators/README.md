# 03 · Idle dephasing with spectator qubits

**Question.** How fast do idle qubits dephase on the emulator, and how long is one layer of work?

**Idea.** There is no delay instruction in Guppy. So 8 target qubits wait while other qubits
(spectators) do L layers of work. Targets in |+⟩ (X basis) feel dephasing; targets in |0⟩
(Z basis) should not. A feed-forward Z keeps the targets' readout after the wait.

**Three designs.**

| Design | Spectator layer | Result (X basis) |
| --- | --- | --- |
| `idle_*` | measure and reset | flat, 0–0.25% up to L = 64 |
| `idleT_*` | random-pairing ZZ (forces transport) | flat, 0–0.25% up to L = 16 |
| `idleA_*` | same, with targets **anchored** to the start of the wait | slow rise, see below |

Why anchoring: without it, nothing stops the scheduler from preparing the targets just before
readout, so they wait in |0⟩ and see no dephasing. The anchor (one extra qubit, a ZZ with each
target, undone at the end) forces the targets into |+⟩ before the wait.

**Anchored, long waits (H2-1E, 1000 shots = 8000 samples per point).**

| L | 0 | 16 | 32 | 64 | Z basis, L = 64 |
| --- | --- | --- | --- | --- | --- |
| flip rate | 1.03% | 1.16% | 1.40% | 1.50% | 0.45% |

- X rises slowly (+0.5 points by L = 64, ~3σ); Z stays low, as for Z-only idling.
- Fit with the emulator's own idle model: **one spectator layer ≈ 3.6 ± 0.8 ms** of idling
  (χ² 2.3 on 2 dof). Far shorter than the published ~60 ms depth-one time: these small
  17-qubit layers seem to need little transport on the emulator.
- An earlier 100-shot run showed 2.4% at L = 16; with 10× the shots it is 1.16%. That point was
  a fluctuation, and the "~30 ms per layer" read from it is withdrawn.

**Files.** `results/hardware/calibration_programs/idle*`, `h2_1e_*idle*.fit.json`,
`h2_1e_anchored_idle_long*.json`, `h2_1e_anchored_idle_long.png`.
