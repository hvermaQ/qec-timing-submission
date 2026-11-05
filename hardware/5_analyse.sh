#!/usr/bin/env bash
# Step 5: notebooks 11-17 (the hardware arc) on the summaries in results/hardware/. Main env;
#   free. Figures go to figures/.
set -euo pipefail
source "$(dirname "$0")/config.sh"
for nb in 11_hardware_validation_path 12_hardware_calibration 13_hardware_experiments \
          14_emulator_noise_injection 15_emulator_idle_parameters 16_reinterpreting_anchoring_results \
          17_idle_from_single_flips; do
  "$(dirname "$PY_MAIN")/jupyter" execute --inplace "notebooks/$nb.ipynb"
done
echo "hardware analysis done: figures/11-17_*"
