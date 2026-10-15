#!/usr/bin/env bash
# Why idling matters: how much of an application's logical-qubit time is idle (adder, QFT,
#   Ising), and what a longer syndrome interval buys there: waiting at distance d against
#   back-to-back rounds at d + 2 (time for space) on H2-1E rates over round durations t_R.
#   Notebooks 01 and 09. Main env. Idle fractions take seconds; the regime grid ~1 h from scratch.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv-main/bin/python}
W=${WORKERS:-8}
$PY -m qec_timing.studies.idle                                        # results/idle/
$PY -m qec_timing.studies.regime --calibration config/h2_1e_emulator.json \
    --t-round 0.001 0.002 0.004 0.007 0.01 0.02 0.03 0.05 0.07 0.1 0.15 0.2 0.3 \
    --distances 3 5 7 --workers "$W" --out results/regime/grid        # results/regime/grid/
if [[ "${NOTEBOOKS:-1}" == 1 ]]; then
  for nb in 01_idle_in_applications 09_time_for_space; do
    .venv-main/bin/jupyter nbconvert --to notebook --execute --inplace "notebooks/$nb.ipynb"
  done
fi
echo "idle importance done: results/idle, results/regime/grid, figures/01_*, figures/09_*"
