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

**Anchored, long waits (H2-1E, 1000 shots = 8000 samples per X point).**

| L | 0 | 16 | 32 | 64 | 128 | Z basis, L = 64 |
| --- | --- | --- | --- | --- | --- | --- |
| flip rate | 1.03% | 1.16% | 1.40% | 1.50% | 1.11% | 0.45% |

- No consistent growth: L = 128 is back at the floor (mean 1.22%; scatter a little above chance,
  p ≈ 0.04, but not a steady rise). Z stays low.
- Any idle dephasing is below ~0.5% even at L = 128: under ~0.2 s of effective idling on the
  emulator's own rates, i.e. ≲ 1–2 ms per layer, if the targets really wait in |+⟩. The ~60 ms
  published depth-one time is ruled out for these small layers.
- Withdrawn: the 100-shot 2.4% at L = 16, and the 4-point fit of ≈ 3.6 ms per layer.
- Open: whether the emulator applies idle dephasing to these programs at all. L = 256 (~1050
  two-qubit gates) was refused as over the per-job cost limit, even at 500 shots.

**Files.** `results/hardware/calibration_programs/idle*`, `h2_1e_*idle*.fit.json`,
`h2_1e_anchored_idle_long*.json`, `h2_1e_anchored_idle_long.png`.
