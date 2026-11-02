"""Reproduce conditional wait-noise estimates from the saved H2 calibration.

These are estimates for an isolated idle channel, not measured sleep durations,
predictions of logical failure, or a verified configuration of an aqora job.
"""
import dataclasses
import hashlib
import json
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.path.insert(0, str(REPO / "src"))
from qec_timing.hardware.calibration import Calibration


def main():
    path = REPO / "config/h2_1e_emulator.json"
    cal = Calibration.load(path)
    config = json.loads((ROOT / "configs/sleep_probe.json").read_text())
    durations = config["finite_durations_raw"]
    rows = []
    for duration in durations + [t for t in [0.5, 1.0] if t not in durations]:
        p = cal.idle_pz(duration)
        rows.append({
            "raw_argument_if_seconds": duration,
            "milliseconds_if_seconds": duration * 1000,
            "included_in_current_sweep": duration in durations,
            "p_z_saved_cycles_convention": p,
            "expected_target_z_faults_per_1000_shots": p * 1000,
            "p_z_alternative_radians_convention": dataclasses.replace(cal, quad_convention="radians").idle_pz(duration),
            "p_z_without_stabilizer_multiplier": dataclasses.replace(cal, quad_factor=1.0).idle_pz(duration),
        })
    previous = REPO / "results/hardware/h2_1e_anchored_idle_long.json"
    data = {
        "calibration_source": str(path.relative_to(REPO)),
        "calibration_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "gamma_per_second_assumed": cal.gamma,
        "quadratic_rate_cycles_per_second_assumed": cal.quad_rate,
        "coherent_to_incoherent_factor_assumed": cal.quad_factor,
        "omega_radians_per_second": cal.omega,
        "linear_quadratic_small_time_crossover_seconds": cal.gamma / (cal.omega / 2) ** 2,
        "assumptions": [
            "raw sleep argument interpreted as seconds for this calculation ONLY",
            "saved cycles convention and factor 2; job simulator mode is unverified",
            "one uninterrupted idle channel on q4; no DD; no extra channel splitting",
            "expected faults exclude gate/readout/preparation errors and correction",
        ],
        "rows": rows,
        "previous_anchored_run_source": str(previous.relative_to(REPO)),
        "previous_anchored_run_sha256": hashlib.sha256(previous.read_bytes()).hexdigest(),
        "previous_anchored_counts": json.loads(previous.read_text()),
        "previous_fit_status": "3.6 ms/layer estimate withdrawn after L=128; no confirmed layer-to-seconds conversion",
        "sleep_unit_status": "unverified",
        "new_emulator_jobs_submitted": 0,
    }
    out = ROOT / "results/duration_scales.json"
    out.write_text(json.dumps(data, indent=2) + "\n")
    for row in rows:
        print(f"{row['milliseconds_if_seconds']:6g} ms: "
              f"pZ={100 * row['p_z_saved_cycles_convention']:.6f}%, "
              f"{row['expected_target_z_faults_per_1000_shots']:.4f} faults/1000")
    print(f"Linear/quadratic crossover: {data['linear_quadratic_small_time_crossover_seconds'] * 1000:.2f} ms")
    print(out)


if __name__ == "__main__":
    main()
