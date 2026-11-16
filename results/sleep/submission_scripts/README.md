# Submission scripts (archived)

The one-off scripts that built programs and submitted, checked or fetched the sleep-experiment jobs,
moved here unchanged from `SG_final_round/src/` (stage 3 of `MIGRATION.md`). They are the
submission record for the runs in `../runs/`. They are not imported and do not run from here: they
import sibling modules that are now `qec_timing.sleep.*`.

Their build code lives in the package, which reproduces every committed program folder:

| Script(s) | Package |
| --- | --- |
| `single_qubit_pilot.py` | `qec_timing.sleep.builders.single_qubit` (`qir`, `pilot`) |
| `d3_h2_2_zero_sleep_control.py` | `builders.d3.zero_sleep_h2_2` |
| `d5_zero_sleep_control.py`, `d5_h2_2_zero_sleep_control.py`, `d5_h2_2_zero_sleep_n3_control.py` | `builders.d5.zero_sleep` (one parametrised builder) |
| `d5_h2_2_zero_sleep_control_repeat_250.py` | reruns the `d5_h2_2_zero_sleep_n2` program (no build code) |
| `d5_h2_2_zero_sleep_n3_skip5.py`, `submit_d5_h2_2_t1_skip5_*.py` | `qec_timing.sleep.mapping`, `builders.d5.zero_sleep_n3_skip5`, `builders.d5.skip5_t1` |
| `submit_d5_half_second_500.py` | `builders.d5.half_second` |
| `submit_d5_h2_2_t1_20261113.py`, `submit_d5_h2_2_t1_skip5_*.py` (`plan`) | `qec_timing.sleep.jobs.h2_2_d5_plan` |
| the other `submit_d5_*.py` (H2-1E / H2-2E d=5 retries and entity-name attempts) | submit only; reuse `d5_fixed_sleep_9fb82150bc37143a` |

`build_sleep_probe.py` is a byte-for-byte copy of the original probe builder
(sha256 `8f1775a21bcc2268b13911afc1bfe3666de7cb8e2b566ee2d99a9ed421fea419`). Probe folder names hash
the folder's config plus this file's bytes, so `qec_timing.sleep.builders.probe` reads it (and checks
its sha256) to reproduce `5944c048c1dfdc80` and `8cca8353b3f06d18`. Do not edit it.
