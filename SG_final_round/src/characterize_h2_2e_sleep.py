"""Shot-level uncertainty and descriptive growth in H2-2E data errors."""
import argparse
import json
import numpy as np
from analyze_d3_sleep_sweep import unpack
import d3_sleep_sweep as sweep


def main(platform='nexus:H2-2E'):
    sweep.configure_five_point(platform)
    rng = np.random.default_rng(20261102)
    rows, bootstraps = [], []
    for name, u in sweep.VARIANTS.items():
        raw = json.loads((sweep.RUNS/'execute'/name/'result_0.txt').read_text())
        shots = unpack(raw)
        data = np.array([[s[f'm{i}'] for i in range(9)] for s in shots], dtype=float)
        weight = data.sum(axis=1).astype(int)
        hist = np.bincount(weight, minlength=10)
        # Resample complete shots: retain dependence among the nine qubits.
        draws = rng.multinomial(len(shots), hist/len(shots), size=10000)
        boot = draws @ np.arange(10) / (len(shots)*9)
        bootstraps.append(boot)
        rows.append(dict(duration_raw=u, mean_data_error=float(data.mean()),
            shot_bootstrap_95=np.quantile(boot, [.025, .975]).tolist(),
            shot_mean_standard_error=float((weight/9).std(ddof=1)/np.sqrt(len(shots))),
            per_qubit_error=data.mean(axis=0).tolist(), fault_weight_histogram=hist.tolist()))
    p0 = rows[0]['mean_data_error']
    for row, boot in zip(rows, bootstraps):
        # Under an independent XOR composition of background and added flip channels.
        row['effective_extra_flip_probability'] = (row['mean_data_error']-p0)/(1-2*p0)
        extra_boot = (boot-bootstraps[0])/(1-2*bootstraps[0])
        row['effective_extra_flip_bootstrap_95'] = np.quantile(extra_boot, [.025, .975]).tolist()
    # Descriptive fit in RAW argument units; no inference of physical seconds.
    u = np.array(list(sweep.VARIANTS.values()))
    p = np.array([r['mean_data_error'] for r in rows])
    # Fix the measured background; coefficients may be negative in this unconstrained diagnostic.
    a,b = np.linalg.lstsq(np.column_stack([u, u*u]), p-p0, rcond=None)[0]
    result = dict(rows=rows, bootstrap_repetitions=10000, bootstrap_seed=20261102,
        extra_channel_assumption='p(u)=p0+(1-2*p0)*q(u); background unchanged, added XOR flip channel',
        descriptive_fit=dict(form='mean_data_error(u) = measured_p0 + a*u + b*u^2',
            p0=p0, a_per_raw_argument=float(a), b_per_raw_argument_squared=float(b),
            fitted_values=(p0+a*u+b*u*u).tolist(),
            status='descriptive only; no physical rate calibration or model identification'),
        uncertainty_note='Shot bootstrap retains within-shot qubit correlation; assumes independent shots, no run-to-run variability measured')
    target = platform.split(':')[1].lower().replace('-', '_')
    (sweep.ROOT/'results'/f'd3_sleep_five_point_{target}_noise_characterization.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--platform', choices=['nexus:H2-1E', 'nexus:H2-2E'], default='nexus:H2-2E')
    main(parser.parse_args().platform)
