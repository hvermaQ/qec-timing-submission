"""Analyses of the saved sleep-experiment shots (decode, pool, control diagnostics, audits).

    emulator_d3   d=3 H2-1E / H2-2E: two-round sweeps*, fixed-sleep 500*/combined*/all shots,
                  noise characterization, sleep-dependent re-decode
    emulator_d5   d=5 H2-1E: completed-job decode*, sleep-dependent re-decode
    h2_2_d3       physical H2-2 d=3: pooled first batches*, all shots under the approved policy,
                  decoder-weight sensitivity
    h2_2_d5       physical H2-2 d=5: original mapping, skip-index-5 mapping (never pooled), p_read sensitivity
    controls      single-qubit pilot and sweep counts; d=5 H2-2 zero-sleep controls (N=2*, N=3)
    audit         native-QIR ideal audit (needs clang); duration scales

* historical: superseded analyses, kept so their committed results stay reproducible. Each
  one's docstring says so and names the decoder it used.

Importing these modules writes nothing and needs only numpy; stim, pymatching and scipy are
imported when an analysis runs.
"""
