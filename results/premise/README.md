# Premise study (original notebooks 08 and 09)

`premise_textbook.json` (Stim generated circuit) and `premise_native.json` (Selene's native
gates). Produced by `python -m qec_timing.studies.premise --gates textbook|native`; every
run is in the store under the listed run ids. `run_*.log`: console output.

Full-circuit dt* equals the original notebooks' values to every printed digit at all
9 (d, idle) points for both gate sets, since the circuits and seeds are identical. The
one-calibration predictions agree within sampling noise; they cannot match exactly
because the phenomenological circuit here is built with MPP, not Stim's generated
circuit.

`b_read` here is p_read / p_data(1), both measured at dt = 1 (0.93-1.02). The original
notebook-arc summary quotes 1.08-1.15 "with linear dephasing" for a different ratio;
its definition should be checked before that number is quoted.
