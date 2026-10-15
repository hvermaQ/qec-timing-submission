#!/usr/bin/env bash
# Approach (B): circuit-level noise. Native gates, gate errors on every qubit, trapped-ion
#   idle dephasing (linear gamma, quadratic c, mixed). Does the optimum survive (Fig. 1), is it
#   predicted from one calibration, how does dt* move over the (gamma, c) plane (Fig. 2), and
#   where does H2 sit. Notebooks 03-08. Main env. ~2 h from scratch; reruns reuse store/.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv-main/bin/python}
W=${WORKERS:-8}
H2=config/h2_1e_emulator.json
$PY -m qec_timing.studies.premise --gates textbook --workers "$W"     # results/premise/
$PY -m qec_timing.studies.premise --gates native --workers "$W"       # Fig. 1
$PY -m qec_timing.studies.effective --workers "$W"                    # results/effective/
$PY -m qec_timing.studies.per_qubit                                   # results/per_qubit/
$PY -m qec_timing.studies.decoders --workers "$W"                     # results/decoders/ (after premise native)
$PY -m qec_timing.studies.idle_scaling --placement uniform --workers "$W"   # Fig. 2, the dt* map
$PY -m qec_timing.studies.regime --calibration "$H2" --t-round 0.002 0.01 0.03 0.1 0.3 \
    --distances 3 5 --workers "$W"                                    # results/regime/
if [[ "${NOTEBOOKS:-1}" == 1 ]]; then
  for nb in 03_dephasing_needs_x_basis 04_premise_realistic_noise 05_per_qubit_error \
            06_decoder_matters 07_dt_star_vs_idle_strength 08_regime_on_h2; do
    .venv-main/bin/jupyter nbconvert --to notebook --execute --inplace "notebooks/$nb.ipynb"
  done
fi
echo "approach B done: results/{premise,effective,per_qubit,decoders,idle_scaling,regime}, figures/03-08_*"
