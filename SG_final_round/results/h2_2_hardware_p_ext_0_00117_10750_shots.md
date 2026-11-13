# Physical H2-2: all shots with updated sleep-dependent decoder

16 unique jobs, 10,750 shots: 9,750 at total requested sleep T=1 s; 1,000 zero-sleep control shots. p_ext=0.00117, p_read=0.001. All other decoder constants unchanged. Historical results preserved.

| N | u (s) | Shots | Logical failures | Logical error | 95% Wilson | Raw bits / total | Raw error |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 2 | 1 | 500 | 21 | 4.2% | 2.76–6.34% | 205 / 4500 | 4.56% |
| 3 | 0.5 | 1500 | 16 | 1.07% | 0.658–1.73% | 352 / 13500 | 2.61% |
| 4 | 0.333333 | 2000 | 21 | 1.05% | 0.688–1.6% | 332 / 18000 | 1.84% |
| 5 | 0.25 | 2000 | 27 | 1.35% | 0.929–1.96% | 397 / 18000 | 2.21% |
| 6 | 0.2 | 2000 | 25 | 1.25% | 0.848–1.84% | 339 / 18000 | 1.88% |
| 10 | 0.111111 | 1000 | 13 | 1.3% | 0.761–2.21% | 153 / 9000 | 1.7% |
| 20 | 0.0526316 | 500 | 9 | 1.8% | 0.95–3.39% | 87 / 4500 | 1.93% |
| 40 | 0.025641 | 250 | 12 | 4.8% | 2.77–8.2% | 68 / 2250 | 3.02% |

Zero-sleep control: [{'rounds': 2, 'total_requested_sleep_seconds': 0.0, 'interval_seconds': 0.0, 'shots': 1000, 'jobs': 1, 'logical_failures': 4, 'logical_error_probability': 0.004, 'logical_wilson_95': [0.0015565881404084308, 0.010239556277262253], 'raw_data_bit_errors': 21, 'data_bits': 9000, 'raw_data_error_probability': 0.0023333333333333335, 'raw_data_shot_bootstrap_95': [0.0014444444444444444, 0.0033333333333333335], 'per_qubit_error_counts': [5, 0, 1, 3, 4, 1, 4, 3, 0], 'old_decoder_failures': 4, 'changed_predictions': 0, 'corrected': 0, 'harmed': 0, 'job_ids': ['AFByb3ZpZGVySm9iAaHPP4sff7OAv5OZhac2rA']}]

Ranges reflect shot sampling only. The sample minimum does not establish a unique optimum. Control shots are excluded from the fixed-T curve. The control informed p_ext and is not independent validation. JSON records job/raw/program/DEM provenance; NPZ stores per-shot failures and predictions.
