#!/usr/bin/env bash
# Approach (A): the paper's phenomenological model, noise injected inside a Guppy program.
#   Guppy (validation path) vs Stim (production path) on the same model, then the paper's
#   scaling 1/dt* vs d (notebook 02), and what the program costs as QIR (notebook 10).
#   Main env. ~15 min from scratch; reruns reuse store/.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv-main/bin/python}
W=${WORKERS:-8}
$PY -m qec_timing.validation.crosscheck                  # results/crosscheck/
$PY -m qec_timing.studies.scaling --workers "$W"         # results/scaling/
# Size and build time of the Guppy program as QIR (notebook 10): needs the H2 env (hugr-qir),
# local and free. Without that env the committed results/hardware/qir_scaling.json is used.
if [[ -x .venv-h2/bin/python ]]; then
  .venv-h2/bin/python -m qec_timing.hardware.cli scaling      # results/hardware/qir_scaling.json
fi
if [[ "${NOTEBOOKS:-1}" == 1 ]]; then
  for nb in 02_paper_model_guppy_vs_stim 10_program_cost_estimates; do
    .venv-main/bin/jupyter execute --inplace "notebooks/$nb.ipynb"
  done
fi
echo "approach A done: results/crosscheck, results/scaling, results/hardware/qir_scaling.json, figures/02_*, 10_*"
