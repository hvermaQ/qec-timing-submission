#!/usr/bin/env bash
# Hardware experiments on Quantinuum H2 emulators through aqora. H2 env (envs/h2.txt).
#   ./run_hardware.sh build              programs as QIR + local Selene check (no account, free)
#   ./run_hardware.sh check              syntax-check every program on H2-1SC / H2-2SC (login; free)
#   ./run_hardware.sh submit             print what would run and stop
#   ./run_hardware.sh submit --confirm   run them on H2-1E / H2-2E (SPENDS CREDITS)
#   ./run_hardware.sh analyse            notebooks 10-15 from the results in results/hardware/
# Log in once first: .venv-h2/bin/aqora login. Organisation: ENTITY (default q_sq).
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-.venv-h2/bin/python}
CLI="$PY -m qec_timing.hardware.cli"
ENTITY=${ENTITY:-q_sq}
P=results/hardware/programs
C=results/hardware/calibration_programs
SWEEP="70 20 10 4 2"                     # d = 5 rounds at fixed T = 10: dt = 0.14 ... 5
LAYERS="0 16 32 64 128"                  # anchored spectator waits (L = 256 exceeds the cost cap)

# experiment | program | platform | shots
plan() {
  for p in 0 0.05; do echo "memory_d3 $P/d3_X_r2_p$p.bc nexus:H2-1E 100"; done
  for r in $SWEEP; do
    f=$(ls $P/d5_X_r${r}_p0.015_lam1_dt*.bc); echo "dt_sweep_d5 $f nexus:H2-2E 1000"
  done
  for L in $LAYERS; do echo "idle_anchored $C/idleA_X_L$L.bc nexus:H2-1E 1000"; done
  echo "idle_anchored $C/idleA_Z_L64.bc nexus:H2-1E 1000"
}

case "${1:-}" in
  build)
    for p in 0 0.05; do $CLI build --d 3 --basis X --rounds 2 --p-inject $p; done
    for r in $SWEEP; do $CLI build --d 5 --basis X --rounds $r --p-inject 0.015 --lam 1 --total-time 10; done
    $CLI calib-build --anchored --layers 0 2 4 8 16 32 64 128 256 --bases X Z --spectators 8
    $CLI local $P/d3_X_r2_p0.05.bc          # contract checks on local Selene
    $CLI scaling ;;
  check)
    plan | while read -r _ prog plat _; do
      $CLI aqora-check "$prog" --platform "${plat/E/SC}" --as-entity "$ENTITY"
    done ;;
  submit)
    if [[ "${2:-}" != --confirm ]]; then
      echo "Would run (experiment, program, platform, shots):"; plan | column -t
      echo "Re-run with: ./run_hardware.sh submit --confirm  (spends aqora credits)"; exit 0
    fi
    plan | while read -r _ prog plat shots; do
      $CLI aqora-submit "$prog" --platform "$plat" --shots "$shots" --as-entity "$ENTITY" --confirm
    done ;;
  analyse)
    for nb in 10_program_cost_estimates 11_hardware_validation_path 12_hardware_calibration \
              13_hardware_experiments 14_emulator_noise_injection 15_emulator_idle_parameters; do
      .venv-main/bin/jupyter nbconvert --to notebook --execute --inplace "notebooks/$nb.ipynb"
    done ;;
  *) sed -n '2,8p' "$0"; exit 1 ;;
esac
