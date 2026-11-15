# Physical H2-2 decoder policy

For new analyses of physical H2-2 shots, use `src/h2_2_decoder.py`, which loads `configs/h2_2_decoder.json`. The user selected p_ext=0.00117 going forward on 2026-11-12. Keep the other sleep-dependent decoder constants unchanged. This applies to H2-2, not H2-1 or emulators. Record the policy version and exact DEM hash in new analysis results. Preserve historical analyses and submission-time decoder metadata; label any reanalysis with its new policy. Do not silently pool results decoded under different policies.

## Distance-5 physical H2-2 policy (2026-11-13)

For d=5 physical H2-2 analyses going forward, the user selected p_ext=0.004 from the combined 750-shot zero-sleep controls. Use `configs/h2_2_d5_decoder.json` for this distance, keeping its other sleep-dependent constants unchanged. The d=3 policy in `configs/h2_2_decoder.json` remains p_ext=0.00117. Record the distance-specific policy version and exact DEM hash; preserve historical analyses.

## Skip-index-5 physical H2-2 policy (2026-11-14)

For the new d=5 mapping with data indices 0–4 and 6–25 and ancilla 26, use `configs/h2_2_d5_skip5_decoder.json`: user-requested p_ext=0.005, p_read=0.001, with the existing sleep-dependent constants. Preserve original code-position output labels and keep this configuration separate from historical mappings and calibration results.
