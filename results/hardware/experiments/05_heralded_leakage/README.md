# 05 · Leakage-heralded decoding (design only)

**Question.** Can we flag leaked qubits and tell the decoder, to lower p_L?

**Status.** Not run.

- Guppy's `measure_leaked` (returns 0, 1 or 2 = leaked) works in Guppy, but the QIR converter
  (hugr-qir 0.1.2 and 0.3.0) cannot compile it. The H2 emulators only take QIR or pytket.
- Plan: use Quantinuum's leakage-detection gadget instead (one flag qubit: reset, X, H, ZZ, ZZ,
  H, measure; plus Z on the checked qubit). Ordinary gates only, so it compiles. It reads 1 only
  if the checked qubit leaked.
- Cost: +2 two-qubit gates per measured qubit, so bigger jobs (watch the cost cap).

**Next.** Build it into the memory program, test on local Selene with its leakage model, then a
small d = 3 run on H2-1E.
