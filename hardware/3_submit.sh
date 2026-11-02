#!/usr/bin/env bash
# Step 3: run the plan on the H2 emulators (H2-1E / H2-2E) through aqora. SPENDS CREDITS.
#   hardware/3_submit.sh [experiment ...]             print what would run, and stop
#   hardware/3_submit.sh --confirm [experiment ...]   run it
# Raw jobs land in store/hardware/ (program sent, job record, result verbatim).
set -euo pipefail
source "$(dirname "$0")/config.sh"
if [[ "${1:-}" != --confirm ]]; then
  echo "Would run (experiment, program, platform, shots):"; plan_for "$@" | column -t
  echo "Re-run with --confirm to submit (spends aqora credits)."; exit 0
fi
shift
plan_for "$@" | while read -r _ prog plat shots; do
  $CLI_H2 aqora-submit "$prog" --platform "nexus:$plat" --shots "$shots" --as-entity "$ENTITY" --confirm
done
