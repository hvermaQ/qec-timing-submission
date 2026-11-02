#!/usr/bin/env bash
# Step 2: the planned programs through the H2 syntax checkers (H2-1SC / H2-2SC). Validates,
#   executes nothing; free. Needs one `.venv-h2/bin/aqora login` first.
#   hardware/2_check.sh [experiment ...]       (experiments as listed by 3_submit.sh)
set -euo pipefail
source "$(dirname "$0")/config.sh"
plan_for "$@" | while read -r _ prog plat shots; do
  $CLI_H2 aqora-check "$prog" --platform "nexus:${plat/E/SC}" --shots "$shots" --as-entity "$ENTITY"
done
