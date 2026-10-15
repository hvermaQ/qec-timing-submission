#!/usr/bin/env bash
# Approach (A): the paper's phenomenological model, noise injected inside a Guppy program.
#   Guppy (validation path) vs Stim (production path) on the same model, then the paper's
#   scaling 1/dt* vs d. Notebook 02. Main env. ~15 min from scratch; reruns reuse store/.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv-main/bin/python}
W=${WORKERS:-8}
$PY -m qec_timing.validation.crosscheck                  # results/crosscheck/
$PY -m qec_timing.studies.scaling --workers "$W"         # results/scaling/
[[ "${NOTEBOOKS:-1}" == 1 ]] && .venv-main/bin/jupyter nbconvert --to notebook --execute --inplace \
    notebooks/02_paper_model_guppy_vs_stim.ipynb
echo "approach A done: results/crosscheck, results/scaling, figures/02_*"
