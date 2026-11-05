# Shared settings for the hardware steps (sourced by the numbered scripts, not run).
# Override any of these from the environment, e.g. ENTITY=my_org hardware/2_check.sh
cd "$(dirname "${BASH_SOURCE[0]}")/.."
PY_H2=${PY_H2:-.venv-h2/bin/python}          # build, check, submit: Guppy 0.21, hugr-qir, aqora
PY_MAIN=${PY_MAIN:-.venv-main/bin/python}    # collect, analyse: Stim, PyMatching, Jupyter
CLI_H2="$PY_H2 -m qec_timing.hardware.cli"
ENTITY=${ENTITY:-q_sq}                       # aqora organisation the jobs run as
# Emulator options (JSON or @file), e.g. OPTIONS='{"no_opt": true}'. Empty = none sent, as for
# every committed result (platform defaults); set it for new experiments.
OPTIONS=${OPTIONS:-}
P=results/hardware/programs
C=results/hardware/calibration_programs

# The emulator runs behind results/hardware/: experiment | program | platform | shots.
# Left out, over aqora's per-job cost cap: d = 5 at R = 70, and anchored idle at L = 256.
plan() {
  local b L p r f
  for p in 0 0.05; do echo "memory_d3 $P/d3_X_r2_p$p.bc H2-1E 100"; done
  for r in 20 10 4 2; do                     # d = 5 at fixed T = 10: dt = 0.5 ... 5
    f=("$P"/d5_X_r${r}_p0.015_lam1_dt*.bc); echo "dt_sweep_d5 ${f[0]} H2-2E 1000"
  done
  echo "readout $C/readout.bc H2-1E 100"
  for b in X Z; do for L in 0 2 4 8 16 32 64; do echo "idle_measure_reset $C/idle_${b}_L$L.bc H2-1E 100"; done; done
  for b in X Z; do for L in 0 2 4 8 16; do echo "idle_transport $C/idleT_${b}_L$L.bc H2-1E 100"; done; done
  for b in X Z; do for L in 0 2 4 8 16; do echo "idle_anchored $C/idleA_${b}_L$L.bc H2-1E 100"; done; done
  for L in 0 16 32 64 128; do echo "idle_anchored_long $C/idleA_X_L$L.bc H2-1E 1000"; done
  echo "idle_anchored_long $C/idleA_Z_L64.bc H2-1E 500"
}

# The plan, restricted to the experiments named as arguments (all if none).
plan_for() {
  if (($#)); then plan | grep -E "^($(IFS='|'; echo "$*")) " || { echo "no such experiment: $*" >&2; return 1; }
  else plan; fi
}
