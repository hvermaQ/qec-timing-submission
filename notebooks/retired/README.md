# Retired notebooks

Kept for the record; not part of the submission's argument and not rebuilt by `_build.py`
(their source is in git history before this move).

## artificial_idle_effective_parameters (was notebook 04)

Fitted the paper's λ and b_read for a native-gate extraction circuit under Selene's
depolarizing error model, against ρ = p2/p1 ∈ {0 … 100}. Retired because:

- the idle model is unphysical for ions: depolarizing, charged per identity op, data qubits
  only, no duration (ions dephase in time, on every qubit);
- it returns to a Z-basis memory, which cannot see trapped-ion (Z) idling;
- the headline trend is set by the parameterisation: idle error per unit is pinned to p1, so
  λ ≈ (2p1/3)/p_stab falls as p_stab grows with ρ;
- most of the ρ sweep is far from H2 (ρ ≈ 56), and the Δt* comparison used the paper's model
  with the ρ = 0 parameters, not the circuit.

The study code (`qec_timing.studies.effective`) and `results/effective/` are unchanged.
