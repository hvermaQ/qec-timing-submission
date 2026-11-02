#!/usr/bin/env bash
# Step 4: the returned jobs in store/hardware/ -> the summaries in results/hardware/ that
#   notebooks 13-15 read (decoding, idle fits, model predictions, syntax checks). Main env;
#   free; ~20 s. See src/qec_timing/hardware/collect.py.
set -euo pipefail
source "$(dirname "$0")/config.sh"
$PY_MAIN -m qec_timing.hardware.cli collect
