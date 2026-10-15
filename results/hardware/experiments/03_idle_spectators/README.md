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
| `idleA_*` | same, with targets **anchored** to the start of the wait | 0.6% floor, **2.4% at L = 16** |

Why anchoring: without it, nothing stops the scheduler from preparing the targets just before
readout, so they wait in |0⟩ and see no dephasing. The anchor (one extra qubit, a ZZ with each
target, undone at the end) forces the targets into |+⟩ before the wait.

**Runs.** H2-1E, 100 shots per point. Running now: anchored X at L = 0, 16, 32, 64 (1000 shots)
and Z at L = 64 (500 shots).

**Reading so far.** One point above the floor fits about 30 ms per layer on the emulator's idle
model. The long waits should turn this into a fitted curve.

**Files.** `results/hardware/calibration_programs/idle*`, `h2_1e_*idle*.fit.json`, `.png`.
