#!/usr/bin/env bash
# Step 1: every hardware program as QIR, and a contract check of the memory program on local
#   Selene. H2 env; no account; free. Rewrites results/hardware/programs/ and
#   calibration_programs/: the bitcode byte for byte, the .json metadata with new build times.
set -euo pipefail
source "$(dirname "$0")/config.sh"
# Memory programs: d = 3 (run), the d = 5 sweep at T = 10 (run but R = 70), and two built only.
for p in 0 0.05; do $CLI_H2 build --d 3 --basis X --rounds 2 --p-inject $p; done
for r in 70 20 10 4 2; do $CLI_H2 build --d 5 --basis X --rounds $r --p-inject 0.015 --lam 1 --total-time 10; done
for r in 30 10 5 2 1; do $CLI_H2 build --d 3 --basis X --rounds $r --p-inject 0.015 --lam 1 --total-time 10; done
$CLI_H2 build --d 5 --basis X --rounds 5
# Calibration programs: readout and measure-and-reset spectators; transport; anchored transport.
$CLI_H2 calib-build --layers 0 2 4 8 16 32 64
$CLI_H2 calib-build --transport --layers 0 2 4 8 16 --spectators 8
$CLI_H2 calib-build --anchored --layers 0 2 4 8 16 32 64 128 256 --spectators 8
$CLI_H2 local $P/d3_X_r2_p0.05.bc
echo "built: $P, $C"
