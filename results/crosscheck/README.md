# Guppy vs Stim cross-check

`crosscheck.json` / `run.log`: the result. Produced by
`python -m qec_timing.validation.crosscheck`; every run is in the store under the
`run_id`s listed in the JSON.

`*_overlapping_seeds.*`: the first attempt, kept for the record. Guppy points at
the same distance had overlapping per-shot seed ranges, so they shared random
numbers and their errors were correlated. That made d = 7 look biased (-1.9 sigma
within the run, -3.5 sigma pooled with the original Stage 4a numbers). With
separate seed blocks the d = 7 offset is -0.7 sigma. The cross-check now refuses
overlapping ranges.
