# Migrating `SG_final_round/` into the repository layout

The sleep experiments (explicit QIR `sleep` between X-memory extraction rounds, on H2-1E / H2-2E and on
physical H2-1 / H2-2) live in `SG_final_round/` as a self-contained folder of loose scripts. This file is
the plan for moving them into the structure of the rest of the repo, in eight stages. Stage 0 (this file)
changed nothing else.

Written from a full read of: `README.md`, `REPRODUCE.md`, `pyproject.toml`, `.gitignore`,
`hardware/README.md`, `hardware/*.sh`, `run_*.sh`, `notebooks/_build.py` (skimmed), the layout of
`src/qec_timing/` and `tests/`; and in `SG_final_round/`: `README.md`, `AGENTS.md`, `env/README.md`,
`configs/`, all 72 files in `src/` and all 4 in `tests/`.

## 1. Ground rules

- Measured data never changes. Everything under SG_final_round/programs, runs, results, outputs is moved with `git mv`, never edited, except fixing relative links in .md files. Absolute /Users/harshank_s/... paths inside historical JSON stay as they are.
- Never submit, check or fetch jobs: no aqora/qnexus calls, no build-script actions check/execute/fetch-*, no --confirm.
- Do not change the contents of any CONFIG dict or any QIR-generating code: build folder names are a hash of CONFIG + QIR text.
- Keep the physical H2-2 decoder policies in SG_final_round/AGENTS.md exactly. Never pool the two d=5 mappings (original, skip-index-5).
- This machine is Windows: no clang and no H2 env. Verify programs by regenerating the .ll text and comparing it with the committed .ll. Skip anything needing guppylang 0.21, hugr-qir or aqora and say so.
- Run Python with .venv\Scripts\python.exe.
- Stop at the end of each stage, summarise what changed, and do not commit.

## 2. Target layout

```
src/qec_timing/sleep/          Harshank's code as a subpackage (module plan below)
config/sleep/                  SG_final_round/configs/*.json (experiment configs, byte-identical)
config/sleep/decoders/         h2_2_decoder.json, h2_2_d5_decoder.json, h2_2_d5_skip5_decoder.json
results/sleep/
  programs/                    SG_final_round/programs/   (committed, git mv, untouched)
  runs/                        SG_final_round/runs/       (committed, git mv, untouched; holds 15 run-local .py scripts)
  *.json *.md *.npz *.png *.pdf *.csv, decoders/, circuit_audit/
                               all of SG_final_round/results/* (git mv, untouched)
  figures/                     SG_final_round/results/figures/* + SG_final_round/outputs/*.pdf (no name collisions)
  README.md                    SG_final_round/README.md (only its 79 relative links fixed)
  DECODER_POLICY.md            SG_final_round/AGENTS.md
  submission_scripts/          the dated one-off submit scripts, git mv unchanged; archived, not imported, not runnable from there
hardware/sleep.sh              job script in the style of hardware/config.sh + 3_submit.sh
notebooks/_build.py            + NB["19_sleep_emulator"], NB["20_sleep_h2_2_d3"], NB["21_sleep_h2_2_d5"]
figures/19_*, 20_*, 21_*       written by those notebooks (P.save)
tests/test_sleep.py            SG_final_round/tests ported to pytest, plus regression tests
```

Proposed modules in `src/qec_timing/sleep/` (the brief's list, plus `qir.py`, `unpack.py`, `jobs.py`,
`plots.py` and `stats.py` to hold code that is duplicated today; names can change in stage 3):

| Module | Holds |
| --- | --- |
| `paths.py` | every path in one place: `REPO`, `CONFIG = config/sleep`, `DECODERS = config/sleep/decoders`, `RESULTS = results/sleep`, `PROGRAMS`, `RUNS`, `FIGURES`, the pinned baselines `results/hardware/programs/d3_X_r2_p0.*` and `d5_X_r5_p0.*`; `recorded(path)`, which maps a path stored in a historical record (`/Users/harshank_s/qec-timing-submission/SG_final_round/<x>/...` or `SG_final_round/<x>/...`) to its new location; an output-root override so re-running an analysis can write to a scratch folder instead of `results/sleep/` |
| `qir.py` | shared QIR text helpers: `SLEEP`, `BOUNDARY`, `call_counts`, `operand`, `result_operand`, `remap_results`, `rename_locals`, optional clang `assemble`/roundtrip |
| `builders/probe.py`, `builders/single_qubit.py`, `builders/d3.py`, `builders/d5.py` | the QIR builders, CONFIG dicts copied verbatim, folder names computed with the same expressions |
| `mapping.py` | skip-index-5 mapping (forward, inverse, and the `.ll`-level remap), one implementation |
| `decoder.py` | `h2_2_decoder` (policy loader, `round_probabilities`) and the legacy H2-1E sleep-dependent constants (p_ext 0.002) from `redecode_d3_sleep_dependent.py` |
| `unpack.py` | the four `unpack` / `unpack_hardware` variants as one parametrised function that keeps each call site's strictness |
| `stats.py` | `wilson` |
| `analysis/` | `emulator_d3.py`, `emulator_d5.py`, `h2_2_d3.py`, `h2_2_d5.py`, `controls.py`, `audit.py` |
| `fits.py` | every `fit_*` plus the fit parts of `analyze_fixed_sleep_all.py`, `report_d3_all_shots.py`, `plot_g1_stacked.py` |
| `plots.py`, `reports.py` | figures; markdown and PDF writers |
| `jobs.py` | `OPTIONS`, `accepted`, and the aqora check/submit/fetch/status code: imports aqora lazily, refuses to submit without `--confirm`; never called during the migration |
| `cli.py` | `python -m qec_timing.sleep.cli ...`: `build`, `verify-programs`, `plan`, `analyze`, `fit`, `plot`, `report`, and the gated `check`/`submit`/`fetch` |

### Facts that constrain the migration

1. **Build folder names.** Reproducible from CONFIG + QIR text: `d3_sleep_sweep_f219bffeea86811d`,
   `d3_sleep_five_point_a2588f7078f6e696`, `d3_sleep_five_point_h2_2e_67d11d0348065703`,
   `d3_fixed_sleep_690baca08b24dfd2`, `d3_fixed_sleep_refinement_3bb6e107a0ff6de3`,
   `d3_fixed_sleep_resolution_c2380924e8c69578`, `d5_fixed_sleep_9fb82150bc37143a`; from QIR text only:
   `single_qubit_2c64d96fea4bbbac`, `single_qubit_sweep_73005efe45e835e4`. `OPTIONS` (from
   `single_qubit_sweep.py`) is part of the d3 CONFIGs, so it must stay the same dict. Fixed names (no hash):
   the zero-sleep, half-second and skip5 folders. **Not reproducible at all:** the three probe folders
   `98ff453353750ae5`, `5944c048c1dfdc80`, `8cca8353b3f06d18`. `build_sleep_probe.py` hashes the config plus
   the *builder file's own bytes*; the committed folders came from two older builder versions
   (`builder_sha256` `ecaf8610...` and `8f1775a2...`, current file `f65cf22b...`). For these, verify the `.ll`
   text only.
2. **CRLF.** `core.autocrlf=true` and there is no `.gitattributes`: the 331 `.ll`/`.dem`/`.stim`/`.md` files
   in `SG_final_round/` are LF in git and CRLF in this working tree. `read_text()` normalises, so baseline
   hashes and folder names still come out right. But hashing file bytes fails: the README's own DEM check
   (`runs/d5_h2_2_t1_skip5_n10_20261115/shots160/n10/decoder_p_ext_0_005.dem`) gives `56499613...` here
   against the recorded `412d8dbd...`. Raw `result_0.txt` files have no newlines and verify fine. Compare
   regenerated `.ll` with `read_text()` or with the git blob, and write with `newline="\n"`.
3. **Scripts write into measured-data folders and outside the folder.** `analyze_d3_sleep_sweep`,
   `analyze_fixed_sleep_d3` and `analyze_fixed_sleep_refinement` write `.dem` files and `manifest.json` into
   `programs/<build>/`. `analyze_d5_h2_2_zero_sleep_*` and `analyze_d5_h2_2_t1_skip5` write analysis
   files into `runs/`. Builders rewrite `configs/*.json` on every fresh build. `plot_g1_stacked`,
   `plot_h2_2_g1_pdf` and `create_h2_2e_summary_pdf` write to the repo-level `output/pdf/`. The package
   must not do any of this by default.
4. **Recorded paths are re-opened.** 609 files hold `/Users/harshank_s/...` (440 under `runs/`, 116
   `programs/`, 51 `results/`, 2 `configs/`). Analyses open `job['program']`, `item['path']` (in
   `d5_h2_1e_all_job_status.json`), `source['run']` (in `d3_fixed_sleep_all_shots.json`), `row['raw_path']`
   and `row['dem_path']`. Some `job.json` `program` fields are relative (`SG_final_round/programs/...`) and
   one is absolute. All of these go through `paths.recorded()`; the files themselves stay as they are.
5. **Policy dicts are compared for equality.** `analyze_d5_h2_2_t1_20261113` asserts
   `job['decoder_policy'] == config JSON`, and `fit_h2_2_g1` asserts `data['decoder_policy'] == POLICY`.
   So the three decoder JSONs must stay byte-for-byte as they are, including the absolute
   `calibration_result` path in `h2_2_d5_skip5_decoder.json`.
6. **`exec()` across files.** `combine_h2_2_updated_decoder.py` and `test_h2_2_decoder_sensitivity.py`
   `exec` the function `unpack_hardware` out of `runs/h2_2_hardware_d3_x_t1_20261111/analyze.py`.
   `create_combined_sleep_pdf.py` `exec`s the top half of `create_h2_2e_summary_pdf.py`. The package
   replaces all three with imports.
7. **Inputs with no generating script** (only committed outputs, so they act as fixed inputs):
   `d3_d5_all_explicit_sleep_logical_comparison.json` and `zero_sleep_pooled_d3_d5.json` (inputs to four
   fits), `d5_h2_1e_all_job_status.json`, `d5_h2_2_skip5_t1_p_ext_0_005_2000_shots.json`,
   `d5_h2_2_zero_sleep_pooled_750.json`, `d5_fixed_baseline_before_sleep_redecode_d5d743d35114.json`,
   `circuit_audit/all_stabilizer_syndrome_comparison.json`. Also `h2_2_hardware_p_ext_0_00117_all_shots.*`,
   `d3_d5_calibrated_g_one_third_fit.json`, `d3_n2_logical_quadratic_fit.json`, `d3_d5_u1_per_qubit_readout_errors.json`,
   `d3_sleep_five_point_emulator_comparison.json`, `d3/d5_zero_sleep_repeat_comparison.json`,
   `zero_sleep_extraction_controls.json`, `zero_sleep_d3_d5_physical_extraction_comparison.json`,
   `hqc_since_renewal_20261105.json`, `physical_hqc_audit_20261115.*`, `single_qubit_local_validation.json`,
   `sleep_sweep_H2-1e-2e_d_3_results.pdf`, most `*_submission.md` and status files, and figures
   `d3_fixed_sleep_preliminary.*` and `d5_h2_1e_completed_sleep_probabilities.png`. The runs
   `d3_zero_sleep_n2_1000_repeat_20261106`, `d5_zero_sleep_n2_1000_repeat_20261106` and
   `d5_fixed_sleep_additional_20261106_500_n4_5_6_7` have no committed submit script.
8. **Environment.** There is no `.venv` in this checkout. Python 3.11, 3.12 (uv) and 3.14 are installed;
   clang is not. Analyses need numpy, scipy, stim, pymatching and matplotlib. Reports also need reportlab,
   pypdf, pypdfium2 and PyMuPDF, and `create_*_pdf` need macOS system fonts (`/System/Library/Fonts`).

## 3. File table

`sleep/` = `src/qec_timing/sleep/`; `archive/` = `results/sleep/submission_scripts/` (git mv, unchanged).
"→ archive too" means the build code is ported into the package and the original file is archived
for its submission record.

| Current path (`SG_final_round/`) | New path | What it does | Notes |
| --- | --- | --- | --- |
| `src/analyze_d3_sleep_sweep.py` | `sleep/analysis/emulator_d3.py`; `unpack` → `sleep/unpack.py` | Decodes the two-round d=3 sweeps (3-point H2-1E; 5-point H2-1E/H2-2E) with fixed paper-graph MWPM, p_data .002/.02/.1 → `d3_sleep_sweep_1000.json`, `d3_sleep_five_point_<plat>_1000.json` | Writes `decoder_p*.dem` + `manifest.json` into `programs/` and `collection_status.json` into `runs/`. Emulator `unpack` (rejects `JOB_*` tags) |
| `src/analyze_d5_h2_2_t1_20261113.py` | `sleep/analysis/h2_2_d5.py` | H2-2 d=5 **original mapping**, 5 jobs / 3,500 shots, policy p_ext .004 → `d5_h2_2_t1_p_ext_0_004_3500_shots.{json,npz,md}`, DEMs in `decoders/h2_2_d5_p_ext_0_004_20261113/` | Asserts the job's stored policy equals the config (fact 5). Stores absolute raw/DEM paths |
| `src/analyze_d5_h2_2_t1_skip5.py` | `sleep/analysis/h2_2_d5.py` | H2-2 d=5 **skip-index-5**, one setting per call (`--rounds 2/3/4/6/10`), p_ext .005 → `runs/<batch>/.../analysis_p_ext_0_005.{json,npz}` + `decoder_p_ext_0_005.dem` | Writes into `runs/`. Overrides policy fields in code (`policy.update`); keep exactly. N=10 reads `shots160/n10` |
| `src/analyze_d5_h2_2_zero_sleep_control.py` | `sleep/analysis/controls.py`; `unpack_hardware` → `sleep/unpack.py` | d=5 N=2 zero-sleep H2-2 control (500 shots): raw error, p_ext estimate, decode → `runs/d5_h2_2_zero_sleep_n2_500_20261113/execute/{analysis.json,decoder.dem}`; `--verify` mode | Decodes d=5 with the **d=3** policy (p_ext .00117), which was historically correct: the d=5 policy didn't exist yet. Writes into `runs/` |
| `src/analyze_d5_h2_2_zero_sleep_n3.py` | `sleep/analysis/controls.py` | N=3 zero-sleep, original mapping, raw-error diagnostic → `runs/.../raw_analysis.json` | Top-level script. Loads `circuit_audit/all_stabilizer_syndrome_comparison.json` but never uses it |
| `src/analyze_d5_h2_2_zero_sleep_n3_skip5.py` | `sleep/analysis/controls.py` | Same for the skip-5 mapping | Near-duplicate of the previous row → one function with a mapping argument |
| `src/analyze_d5_sleep_results.py` | `sleep/analysis/emulator_d5.py`; `unpack` → `sleep/unpack.py` | Pools completed d=5 H2-1E jobs listed in `d5_h2_1e_all_job_status.json`; fixed + sleep-dependent decode → `d5_h2_1e_sleep_logical_probabilities.{json,md}`, `decoders/d5_h2_1e_sleep/` | Opens absolute mac paths from the inventory (fact 4). Third `unpack` copy (d=5 emulator) |
| `src/analyze_fixed_sleep_all.py` | `sleep/analysis/emulator_d3.py` + `sleep/fits.py` + `sleep/plots.py` | d=3 H2-1E, all 18 jobs / 13,000 shots, fixed decoder; paper-linear and quadratic fits, 1,000-sample bootstrap → `d3_fixed_sleep_all_shots.{json,md}`, figure, `decoders/d3_fixed_sleep_all_shots/` | Records absolute `run` paths that `redecode_d3` re-opens |
| `src/analyze_fixed_sleep_d3.py` | `sleep/analysis/emulator_d3.py` | Coarse 500-shot batch → `d3_fixed_sleep_500[_partial].{json,md}` | Writes `decoder_n*_p*.dem` into `programs/` |
| `src/analyze_fixed_sleep_refinement.py` | `sleep/analysis/emulator_d3.py` | Coarse + refinement combined → `d3_fixed_sleep_combined.{json,md}` + figure; defines `load_batch` | Writes DEMs into `programs/`. Calls `configure_refinement()`, which mutates `fixed_sleep_d3` globals. `load_batch` is used by 3 scripts |
| `src/analyze_h2_2_hardware_pooled.py` | `sleep/analysis/h2_2_d3.py` | Pools the first two H2-2 d=3 batches' run-local `analysis.json` (6,750 shots, legacy p_ext .002) → `h2_2_hardware_d3_all_shots.{json,png}` | Top-level script. Historical (superseded by the 10,750-shot redecode) but it is the input to the decoder-sensitivity study |
| `src/analyze_single_qubit_pilot.py` | `sleep/analysis/controls.py`; `wilson` → `sleep/stats.py` | 200-shot single-qubit pilot counts → `single_qubit_pilot_counts.json` | `wilson` is imported by about 20 files |
| `src/audit_native_memory.py` | `sleep/analysis/audit.py` | Disassembles submitted `.bc` (clang), translates to Stim, ideal run + single-Z-fault checks → `circuit_audit/*.ll`, `*.stim`, `ideal_audit.json` | **Needs clang: cannot run here.** Writes into `results/circuit_audit/` |
| `src/build_sleep_probe.py` | `sleep/builders/probe.py`; helpers → `sleep/qir.py` | One `sleep` call inserted into the pinned d=3 baseline → `programs/<hash16>/`, `syntax_plan.json` | Folder hash includes the builder's own bytes (fact 1). `ROOT`/`SOURCE`/`BOUNDARY`/`SLEEP`/`call_counts`/`assemble` are imported by most scripts |
| `src/characterize_h2_2e_sleep.py` | `sleep/analysis/emulator_d3.py` | Shot-bootstrap of mean data error for the 5-point sweeps → `d3_sleep_five_point_<plat>_noise_characterization.json` | |
| `src/combine_h2_2_updated_decoder.py` | `sleep/analysis/h2_2_d3.py` | Re-decodes all 16 H2-2 d=3 jobs (10,750 shots) with policy p_ext .00117 and compares with legacy → `h2_2_hardware_p_ext_0_00117_10750_shots.{json,npz,md,png}`, `decoders/h2_2_p_ext_0_00117_20261112/` | `exec`s from `runs/` (fact 6); joins `REPO / job['program']` (fact 4). Top-level script |
| `src/create_combined_sleep_pdf.py` | `sleep/reports.py` | Two-emulator d=3 PDF → `results/h2_1e_h2_2e_d3_sleep_summary.pdf` | That PDF is not committed. `exec`s the next file. macOS fonts. Numbers hard-coded in prose |
| `src/create_h2_2e_summary_pdf.py` | `sleep/reports.py` | Two-page H2-2E PDF → repo-level `output/pdf/h2_2e_d3_sleep_summary.pdf` | Committed copy is `outputs/h2_2e_d3_sleep_summary.pdf`. macOS-only font paths; won't run on Windows |
| `src/create_sleep_explanation_pdf.py` | `sleep/reports.py` | Explainer PDF → `sleep_parameter_explanation.pdf` + `results/pdf_preview/*.png` | reportlab, pypdf, pypdfium2; `pdf_preview/` not committed |
| `src/d3_h2_2_zero_sleep_control.py` | `build` → `sleep/builders/d3.py`; → archive too | Builds `programs/d3_h2_2_zero_sleep_n2` (9 × sleep(0)); H2-2 1,000-shot check/execute/status | Fixed folder name; committed manifest stores an absolute source path |
| `src/d3_sleep_sweep.py` | `sleep/builders/d3.py`; check/execute/fetch → `sleep/jobs.py` | Two-round d=3 with an all-data sleep block between barriers; 3-point and 5-point (H2-1E/H2-2E) | Folder = prefix + hash(CONFIG + QIR). `configure_five_point()` mutates globals; `build()` rewrites `configs/` (fact 3). `operand` is imported by others |
| `src/d5_h2_2_p_read_sensitivity.py` | `sleep/analysis/h2_2_d5.py` | p_read over 7 values on the 3,500 original-mapping shots → `d5_h2_2_p_read_sensitivity.{json,npz,md}`, `decoders/d5_h2_2_p_read_sensitivity/` | Re-opens absolute `raw_path`/`dem_path` |
| `src/d5_h2_2_zero_sleep_control.py` | `build` → `sleep/builders/d5.py`; → archive too | `programs/d5_h2_2_zero_sleep_n2`; H2-2 500 shots | Duplicate of the next three builders, differing only in N, shots, platform and `estimated_hqc` → one parametrised builder |
| `src/d5_h2_2_zero_sleep_control_repeat_250.py` | archive | 250-shot H2-2 repeat that reuses the program above | No build code of its own |
| `src/d5_h2_2_zero_sleep_n3_control.py` | `build` → `sleep/builders/d5.py`; → archive too | `programs/d5_h2_2_zero_sleep_n3` (50 × sleep(0)); H2-2 250 shots | Records the d=5 original policy in the request |
| `src/d5_h2_2_zero_sleep_n3_skip5.py` | remap → `sleep/mapping.py`; → archive too | Remaps `d5_h2_2_zero_sleep_n3/n3.ll` to skip-5 indices → `programs/d5_h2_2_zero_sleep_n3_skip5` | Second skip-5 implementation (works on `.ll` text). Must agree with `mapped_qir`; test it |
| `src/d5_zero_sleep_control.py` | `build` → `sleep/builders/d5.py`; → archive too | `programs/d5_zero_sleep_n2`; H2-1E 1,000 shots | Uses emulator `OPTIONS`; the H2-2 ones use `{"no_opt": true}` |
| `src/fit_d3_calibrated_g.py` | `sleep/fits.py` | d=3 g fit with idle a=.006522, b=.092896 → `d3_calibrated_g_fit.json` | Top-level script; inputs have no generating script (fact 7) |
| `src/fit_d3_free_idle.py` | `sleep/fits.py` | Free a, b, C, g at d=3 → `d3_free_idle_g_fit.json` | Chain: needs `d3_calibrated_g_fit.json` |
| `src/fit_d5_free_idle.py` | `sleep/fits.py` | Same at d=5 → `d5_free_idle_g_fit.json` | Needs `d5_transferred_idle_g_fit.json` |
| `src/fit_d5_sleep_dependent.py` | `sleep/fits.py` + `sleep/plots.py` | d=5 H2-1E linear+quadratic fit, α=2.4 → `d5_sleep_dependent_linear_quadratic_fit[_n3_plus].{json,md,npz}` + figures | Both `--min-rounds 2` and `3` outputs are committed |
| `src/fit_d5_transferred_idle.py` | `sleep/fits.py` | d=5 with a, b taken from the d=3 free fit → `d5_transferred_idle_g_fit.json` | Needs `d3_free_idle_g_fit.json` |
| `src/fit_h2_2_d5_skip5_g1.py` | `sleep/fits.py` | Skip-5 d=5 g=1 fit, N=10 rounded to 1.3% plus exact-count fit → `h2_2_d5_skip5_g1_rounded_n10_fit.json` | Skip-5 only (asserts p_ext .005 and unused index 5); reads `runs/.../analysis_p_ext_0_005.json` |
| `src/fit_h2_2_free_g.py` | `sleep/fits.py` + `sleep/plots.py` | H2-2 d=3 free-g vs g=1, 500-sample bootstrap → `h2_2_d3_free_g_linear_quadratic_fit.{json,png}` | Needs the g=1 fit |
| `src/fit_h2_2_g1.py` | `sleep/fits.py` + `sleep/plots.py` | H2-2 d=3 g=1 fit on 9,750 shots, 1,000-sample bootstrap → `h2_2_d3_g1_linear_quadratic_fit.{json,npz,png}` | Asserts the policy equals `h2_2_decoder.json` |
| `src/fit_shared_g_calibrated.py` | `sleep/fits.py` | Shared-g d=3+d=5 fit with boundary terms → `d3_d5_calibrated_shared_g_fit.json` | Top-level script |
| `src/fit_shared_g_no_boundary.py` | `sleep/fits.py` | Same without boundary terms → `d3_d5_calibrated_shared_g_no_boundary_fit.json` | Top-level script |
| `src/fixed_sleep_d3.py` | `sleep/builders/d3.py` + `sleep/qir.py`; jobs → `sleep/jobs.py` | d=3, N rounds, fixed 1 s total sleep (coarse / refinement / resolution) → `programs/d3_fixed_sleep*_<hash>` | Folder hash; `configure_*()` mutate globals; `build()` rewrites `configs/` |
| `src/fixed_sleep_d5.py` | `sleep/builders/d5.py`; jobs → `sleep/jobs.py` | d=5 fixed 1 s sleep → `programs/d5_fixed_sleep_9fb82150bc37143a`; `PLAN` splits jobs under the cost cap | Folder hash; `build()` rewrites `configs/d5_fixed_sleep_13000.json` (which holds an absolute path). Re-exports `accepted` |
| `src/h2_2_decoder.py` | `sleep/decoder.py` | Loads the H2-2 policy, `round_probabilities(n, u, policy=)` | Loads `configs/h2_2_decoder.json` at import → `config/sleep/decoders/`. d=3 stays the default (DECODER_POLICY.md) |
| `src/plot_d5_h2_2_raw_qubit_errors.py` | `sleep/plots.py` | Per-qubit raw errors, original mapping → `figures/d5_h2_2_raw_error_by_qubit.{png,pdf,json}` | Hand-placed annotations (Q5, Q2) |
| `src/plot_d5_sleep_dependent.py` | `sleep/plots.py` | Fixed vs sleep-dependent d=5 H2-1E → `figures/d5_sleep_dependent_comparison.*` | |
| `src/plot_d5_sleep_results.py` | `sleep/plots.py` | d=5 H2-1E T=1 s → `figures/d5_h2_1e_t1_n2_to_n10.*` **and** `d5_h2_1e_t1_n2_to_n10.json` | A plot script that also writes a data file |
| `src/plot_free_idle_fits.py` | `sleep/plots.py` | d=3 and d=5 free-idle fits → `figures/d3_d5_free_idle_fit_comparison.{png,pdf}` | |
| `src/plot_g1_stacked.py` | fit → `sleep/fits.py`; plot → `sleep/plots.py` | Re-fits g=1 for d=3/5 and plots them stacked → `d3_d5_g1_stacked_fits.json`; PDF/PNG to repo-level `output/pdf/` | Writes outside the folder. Committed PDF copies: `results/` and `outputs/` (identical) |
| `src/plot_h2_2_d3_d5_skip5_g1.py` | `sleep/plots.py` | H2-2 d=3 + skip-5 d=5 g=1 curves → `outputs/h2_2_d3_d5_skip5_g1_fitted_curves.pdf` | Puts both on one page as separate panels, with no pooling. Uses the skip-5 exact-count fit |
| `src/plot_h2_2_g1_pdf.py` | `sleep/plots.py` | H2-2 d=3 g=1 figure → repo-level `output/pdf/h2_2_d3_g1_fixed_fit.{pdf,png}` | Writes outside the folder; committed PDF is in `outputs/` |
| `src/redecode_d3_sleep_dependent.py` | `sleep/analysis/emulator_d3.py`; constants → `sleep/decoder.py` | Re-decodes the 13,000 d=3 H2-1E shots with the sleep-dependent DEM (p_ext .002) → `d3_sleep_dependent_redecode.{json,md,npz}`, `decoders/d3_sleep_dependent/`, figure | Its `round_probabilities` is the H2-2 one with p_ext .002 (same arithmetic; check DEM bytes). Re-opens absolute `run` paths |
| `src/redecode_d5_sleep_dependent.py` | `sleep/analysis/emulator_d5.py` | Same for d=5 H2-1E → `d5_sleep_dependent_redecode.*`, `d5_h2_1e_pooled_raw_measurements.npz`, `decoders/d5_sleep_dependent/` | Records the path and sha256 of `redecode_d3_sleep_dependent.py`, so a rerun after the move changes those two fields (expected) |
| `src/report_d3_all_shots.py` | `fit` → `sleep/fits.py`; `pdf` → `sleep/reports.py` | d=3 linear+quadratic fit → `d3_fixed_sleep_linear_quadratic_fit.json` + figures; methodology PDF `d3_h2_1e_full_methodology_all_shots.pdf` | PDF prose hard-codes numbers |
| `src/review_duration_scales.py` | `sleep/analysis/audit.py` | Expected idle pZ per raw sleep argument from `config/h2_1e_emulator.json` → `duration_scales.json` | Reads `results/hardware/h2_1e_anchored_idle_long.json` (main repo) |
| `src/single_qubit_pilot.py` | `qir`/build → `sleep/builders/single_qubit.py`; run/fetch → archive too | Single-qubit X memory with optional sleep → `programs/single_qubit_2c64d96fea4bbbac`; 200-shot pilot | Folder = hash of QIR text only |
| `src/single_qubit_sweep.py` | `sleep/builders/single_qubit.py`; `analyze` → `sleep/analysis/controls.py`; `OPTIONS`, `accepted` → `sleep/jobs.py` | 5-point 1,000-shot sweep → `programs/single_qubit_sweep_73005efe45e835e4`, `single_qubit_sweep_1000.json` | `OPTIONS` is part of the d=3 CONFIGs (fact 1) |
| `src/submit_d5_additional_n2_3_4_5_20261105.py` | archive | H2-1E d=5 N=2–5, 500 shots, reusing `d5_fixed_sleep` programs | Dated one-off submit. Same template as `submit_d5_retry_500.py` (only `ROUNDS`/`DEST`/text differ) |
| `src/submit_d5_additional_n6_7_20261105.py` | archive | Same, N=6,7 | Dated one-off submit (retry template) |
| `src/submit_d5_capital_Q_squared_20261105.py` | archive | Same template, N=7–10, `as_entity='Q_squared'` | Attempt to find the right aqora entity; its submission md is not committed |
| `src/submit_d5_display_name_20261105.py` | archive | Same, `as_entity='Q squared'` | Entity-name attempt; md not committed |
| `src/submit_d5_h2_2_t1_20261113.py` | archive | Physical H2-2 d=5 **original mapping** N=2,3,4,6,10 (3,500 shots); `plan` validates the circuits | No build code. Records the policy p_ext .004 in each request |
| `src/submit_d5_h2_2_t1_skip5_20261114.py` | `mapped_qir`/build → `sleep/mapping.py`; → archive too | H2-2 skip-5 N=3,4 → `programs/d5_h2_2_t1_skip5_n3_n4` | Request records the **original-mapping** policy (p_ext .004). That is how it was submitted; analysis later used .005 |
| `src/submit_d5_h2_2_t1_skip5_n10_20261115.py` | same | H2-2 skip-5 N=10 (250 requested, 160 completed) → `programs/d5_h2_2_t1_skip5_n10` | Third copy of `mapped_qir`; records the skip-5 policy |
| `src/submit_d5_h2_2_t1_skip5_n2_n6_20261114.py` | same | H2-2 skip-5 N=2,6 → `programs/d5_h2_2_t1_skip5_n2_n6` | Second copy of `mapped_qir`; records the skip-5 policy |
| `src/submit_d5_h2_2e_500.py` | archive | H2-2E d=5 N=5,6,7,8,10 (all rejected for cost) | Dated one-off submit |
| `src/submit_d5_h2_2e_renewed_20261105.py` | archive | H2-2E d=5 N=7–10 (rejected) | Uses private aqora API (`_graphql.create_provider_job`, `_run_sync`) |
| `src/submit_d5_half_second_500.py` | `half_second_qir`/build → `sleep/builders/d5.py`; → archive too | H2-1E d=5, T=0.5 s, N=3–6 → `programs/d5_fixed_sleep_half_second_n3_4_5_6` | Only builder for that folder; also rewrites `configs/d5_fixed_sleep_half_second_2000.json` |
| `src/submit_d5_n8_9_10_accepted_credit.py` | archive | H2-1E d=5 N=8,9,10, 500 shots | Dated one-off submit (retry template) |
| `src/submit_d5_q_squared_20261105.py` | archive | Retry template, `as_entity='q_squared'` | Entity-name attempt |
| `src/submit_d5_renewed_20261105.py` | archive | H2-1E d=5 N=7–10 after credit renewal | Dated one-off submit (retry template) |
| `src/submit_d5_retry_500.py` | archive | H2-1E d=5 N=7,8,9,10,15 retry, 500 shots | The template for the 10 near-identical scripts |
| `src/submit_d5_single_n7_q_sq_100_20261105.py` | archive | H2-1E d=5 N=7, 100 shots | Dated one-off submit (retry template, 100 shots) |
| `src/submit_d5_single_n7_q_sq_20261105.py` | archive | H2-1E d=5 N=7, 500 shots | Dated one-off submit (retry template) |
| `src/submit_d5_single_n7_q_sq_500_attempt2.py` | archive | H2-1E d=5 N=7, 500 shots, second attempt | Dated one-off submit (retry template) |
| `src/test_h2_2_decoder_sensitivity.py` | `sleep/analysis/h2_2_d3.py` (`decoder_sensitivity`) | 630-configuration decoder-weight grid on the 6,750 H2-2 d=3 shots → `h2_2_decoder_sensitivity.{json,npz,png}` | **Not a test**, despite the name (pytest would collect it). `exec`s from `runs/` |
| `tests/test_d3_sleep_sweep.py` | `tests/test_sleep.py` | Sleep block placed between rounds, 9 sleeps, 2 barriers, ancilla untouched | unittest → pytest |
| `tests/test_fixed_sleep_d3.py` | `tests/test_sleep.py` | Baseline gate sequence, per-N counts and output tags, shot parts | unittest → pytest |
| `tests/test_fixed_sleep_d5.py` | `tests/test_sleep.py` | Pinned 5-round sequence, gate counts, result ids, cost cap per part | unittest → pytest |
| `tests/test_sleep_probe.py` | `tests/test_sleep.py` | Probe transform: baseline unchanged, single insertion, invalid inputs refused | unittest → pytest |

Other files in `SG_final_round/`: `configs/*.json` → `config/sleep/` (decoders in `decoders/`);
`env/README.md`, `env/pilot_environment.json` → see question Q2; `.gitignore` → question Q3;
`results/.gitkeep` dropped (folder is non-empty), `runs/.gitkeep` kept.

## 4. References to `SG_final_round` outside the folder

| File | Line(s) | Reference |
| --- | --- | --- |
| `output/hardware_budget/analyze_budget.py` | 4, 5 | `R=Path('/Users/harshank_s/qec-timing-submission')`; reads `SG_final_round/results/d3_d5_g1_stacked_fits.json` |
| `output/hardware_budget/read_costs.py` | 4, 8 | same absolute root; reads `SG_final_round/results/d{d}_free_idle_g_fit.json` |
| `output/hardware_budget/h2_2_additional_shots_recommendation.json` | 2 | `"source": "SG_final_round/runs/h2_2_hardware_d3_x_t1_20261111/analysis.json"` |
| `output/hardware_budget/hardware_hqc_current.json` | 46–286 (16 entries) | `"source": "SG_final_round/runs/.../job.json"` |
| `output/hardware_budget/physical_hardware_total_20261113.json` | 13–222 (21 entries) | `"path": "SG_final_round/runs/.../job.json"` |
| `scratchpad.md` | 42, 71 | prose: "the one-qubit sleep sweep on H2-1E (SG_final_round, ...)", "SG_final_round build" |
| `src/qec_timing/hardware/idle_tests.py` | 15 | docstring: `Env: SG_final_round/env/.venv-idle (...)` |

Not textual references, but they couple the two:
- Writes from SG code into the repo-level `output/pdf/`: `plot_g1_stacked.py`, `plot_h2_2_g1_pdf.py`,
  `create_h2_2e_summary_pdf.py`. `output/pdf/d3_d5_g1_stacked_fits.png` and `h2_2_d3_g1_fixed_fit.png` are
  their outputs.
- SG code reads from the main repo. These must not move: `results/hardware/programs/d3_X_r2_p0.{ll,json,bc}`
  and `d5_X_r5_p0.{ll,json}` (pinned baselines, hash-checked), `config/h2_1e_emulator.json`,
  `results/hardware/h2_1e_anchored_idle_long.json`. Also `qec_timing.codes.surface`, `codes.base`,
  `noise.base.RoundNoise`, `hardware.collect.paper_graph`, `hardware.providers._register_builtins`,
  `hardware.records`, `backends.stim_phenom.dem_for`, `decoders.pymatching_decoder`, `spec.spec_from_json`,
  `schedule.Schedule`, `hardware.calibration`.
- There are no references in `README.md`, `REPRODUCE.md`, `hardware/`, `run_*.sh`, `notebooks/_build.py`,
  `tests/`, `pyproject.toml` or `.gitignore`.

## 5. Stages

- [ ] **1 Baseline.** Create `.venv` (Q1). Save the blob inventory `git ls-tree -r HEAD -- SG_final_round output`
      to the scratchpad, as the reference for "measured data never changes". Run the existing pytest suite
      and the four SG unittests (from a scratch `git worktree` so nothing writes into this tree). Regenerate
      the `.ll` text of every program folder with the *current* SG code and compare with the committed `.ll`
      (via `read_text()`); compute the 9 folder hashes. Record the decoded counts the regression tests will
      pin. Report what was skipped: clang, H2 env, aqora.
- [ ] **2 Move data.** `git mv` `programs/`, `runs/`, `results/*`, `outputs/*` → `results/sleep/...`; `configs/`
      → `config/sleep/` (+ `decoders/`); README → `results/sleep/README.md` (fix its 79 links: `results/X` →
      `X`, `runs/` unchanged, `configs/` → `../../config/sleep/decoders/`, `src/` → package, `env/` per Q2);
      AGENTS.md → `results/sleep/DECODER_POLICY.md`; dated submit scripts → `submission_scripts/` (+ a short
      README there). Check that `git status` shows only renames (R100) apart from README links, and that every
      blob id matches the stage-1 inventory under its new path.
- [ ] **3 Code into package.** `git mv` builders/decoder/analyses into `src/qec_timing/sleep/` (history kept),
      then edit: `paths.py`, `paths.recorded()`, imports instead of `exec`, one copy of each duplicate
      (unpack, skip-5 mapping, round_probabilities, zero-sleep builder, wilson). CONFIG literals and QIR
      text functions stay verbatim. No default writes into `programs/`, `runs/`, `config/` or `output/`.
      Re-check `.ll` text and folder hashes against stage 1.
- [ ] **4 CLI + `hardware/sleep.sh`.** `qec_timing.sleep.cli`; `sleep.sh` sources `config.sh`. Without
      arguments it prints the plan, like `3_submit.sh`; `--confirm` is required for anything that contacts
      aqora. Verified only by dry runs and `verify-programs`. Never run `check`/`submit`/`fetch`.
- [ ] **5 Notebooks.** Add `19_sleep_emulator` (single qubit, d=3 two-round sweeps, d=3 13,000-shot fixed
      sleep, d=5 H2-1E), `20_sleep_h2_2_d3` (H2-1 pilot, 10,750 shots under p_ext .00117, g=1/free-g fits,
      decoder sensitivity) and `21_sleep_h2_2_d5` (controls, original mapping and skip-5 **in separate
      panels/tables**, per-qubit raw errors, p_read sensitivity) to `_build.py`. They read
      `results/sleep/` only. Generate, execute, and check `figures/19-21_*` appear.
- [ ] **6 Tests.** `tests/test_sleep.py`: the 13 ported tests; folder-name hashes; regenerated `.ll` ==
      committed `.ll` for every reproducible folder; manifest `bitcode_sha256` == committed `.bc`;
      `raw_sha256` of every `result_*.txt`; the two skip-5 implementations agree and invert; the legacy and
      policy `round_probabilities` give identical DEMs; committed DEMs reproduce (LF-compared); decoded
      counts reproduce, marked slow: d=3 H2-1E 13,000, H2-2 d=3 10,750, d=5 original 11/30/40/12/19,
      skip-5 12/5/6/6/2; the decoder JSONs are pinned to the DECODER_POLICY values; pooling across
      `policy_version`s / mappings is refused; `paths.recorded()` resolves every stored path. Missing
      stim/scipy → `importorskip`.
- [ ] **7 Docs.** README (layout, Running, a claims row, Where results live), REPRODUCE.md (sleep commands +
      test counts), `hardware/README.md` (`sleep.sh`), `results/sleep/README.md` header ("moved from
      `SG_final_round/`; shell snippets run from `results/sleep/`"), `idle_tests.py` docstring, and
      `output/hardware_budget` paths (Q4).
- [ ] **8 Final verification.** `SG_final_round/` is gone; the blob inventory matches; `git grep SG_final_round`
      finds only historical JSON/records; full pytest in `.venv`; notebooks execute; `sleep.sh` dry run;
      list everything skipped (clang, H2 env, aqora, macOS-font PDFs).

## 6. Open questions

- **Q1 `.venv`.** It does not exist. Which pins? `envs/core.txt` (numpy, pytest) is enough for the
  structural tests; decoding, fits and notebooks need stim/pymatching/scipy/matplotlib/nbformat from
  `envs/main.txt`, whose guppylang/selene pins may not install on Windows. Proposal: `.venv` from
  `envs/main.txt` on Python 3.12, accepting that Selene-dependent tests skip.
- **Q2 `env/`** (`README.md`, `pilot_environment.json`) has no destination in the target layout. Proposal:
  `results/sleep/env/` (it is a record of the submission environment).
- **Q3 `SG_final_round/.gitignore`** (`env/uv-cache/`, `env/python/`, `env/.venv*/`). The root `.venv*/`
  already covers venvs. Proposal: drop it.
- **Q4 `output/hardware_budget/`** is Harshank's sleep-experiment budgeting (two scripts with absolute mac
  roots, three JSONs pointing into `runs/`). Move to `results/sleep/hardware_budget/`, or leave it and
  only fix the two scripts' paths in stage 7?
- **Q5 `outputs/` vs repo `output/pdf/`.** Three scripts write to `output/pdf/`, while the committed PDFs are
  in `SG_final_round/outputs/`. Proposal: the package writes to `results/sleep/figures/` and
  `output/pdf/*.png` stays as is. `results/d3_d5_g1_stacked_fits.pdf` and
  `outputs/d3_d5_g1_stacked_fits.pdf` are byte-identical; keep both?
- **Q6 CRLF.** Add a `.gitattributes` (`results/sleep/** -text`, or `*.ll *.dem *.stim eol=lf`) so the
  working tree matches the recorded hashes on Windows? The committed bytes stay the same either way.
- **Q7 `DECODER_POLICY.md`.** Keep the AGENTS.md text verbatim and append a "paths after migration" table
  (`src/h2_2_decoder.py` → `sleep/decoder.py`, `configs/` → `config/sleep/decoders/`)? Moving it also stops it
  acting as an agent-instruction file for that folder.
- **Q8 Probe folders.** The three probe build names cannot be reproduced (fact 1). Is verifying their `.ll`
  text enough? `98ff453353750ae5` came from an older config format (`sleep_finite`) and may not match even
  in text.
- **Q9 Legacy analyses.** Port superseded ones too (`analyze_h2_2_hardware_pooled`,
  `analyze_d5_h2_2_zero_sleep_control` with the d=3 policy, the 3-point d=3 sweep), or archive them? Proposal:
  port, because their outputs are inputs to later analyses.
- **Q10 `jobs.py`.** Port the aqora submit/fetch code into the package at all, or leave submission only in
  the archive and give `sleep.sh` just build/verify/analyse? Porting is needed for the plan-printing
  `sleep.sh` the brief asks for, but it cannot be exercised here.
