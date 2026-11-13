"""Pool disjoint H2-2 hardware batches by N using their frozen DEM results."""
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.stats import fisher_exact
from analyze_single_qubit_pilot import wilson

ROOT = Path(__file__).resolve().parents[1]
BATCHES = ['h2_2_hardware_d3_x_t1_20261111', 'h2_2_hardware_d3_x_t1_additional_20261112']
grouped = defaultdict(list)
seen = set()
for batch in BATCHES:
    source = ROOT / 'runs' / batch / 'analysis.json'
    analysis = json.loads(source.read_text())
    assert analysis['platform'] == 'nexus:H2-2'
    for row in analysis['rows']:
        assert row['job_id'] not in seen
        seen.add(row['job_id'])
        grouped[row['rounds']].append(dict(batch=batch, **row))
rows = []
for n, batches in sorted(grouped.items()):
    assert len({r['dem_sha256'] for r in batches}) == 1
    shots = sum(r['shots'] for r in batches)
    failures = sum(r['logical_failures'] for r in batches)
    raw_errors = sum(r['data_bit_errors'] for r in batches)
    row = dict(rounds=n, interval_seconds=1/(n-1), shots=shots,
               logical_failures=failures, logical_error_probability=failures/shots,
               logical_wilson_95=wilson(failures, shots),
               raw_data_bit_errors=raw_errors, data_bits=shots*9,
               raw_data_error_probability=raw_errors/(shots*9),
               per_qubit_error_counts=np.sum([r['per_qubit_error_counts'] for r in batches], axis=0).tolist(),
               batches=batches)
    if len(batches) == 2:
        table = [[r['logical_failures'], r['shots']-r['logical_failures']] for r in batches]
        row['batch_difference_fisher_two_sided_p'] = float(fisher_exact(table)[1])
    rows.append(row)
assert len(seen) == 10 and sum(r['shots'] for r in rows) == 6750
summary = dict(platform='nexus:H2-2', distance=3, basis='X', total_requested_sleep_seconds=1,
               total_shots=6750, total_jobs=len(seen),
               decoder='Frozen sleep-dependent phenomenological MWPM', no_postselection=True,
               mixed_schedule_total_failures=sum(r['logical_failures'] for r in rows), rows=rows)
output = ROOT / 'results/h2_2_hardware_d3_all_shots.json'
output.write_text(json.dumps(summary, indent=2)+'\n')
for r in rows:
    print(json.dumps({k:v for k,v in r.items() if k != 'batches'}), flush=True)
print('Mixed-schedule failures:', summary['mixed_schedule_total_failures'])

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
ordered = sorted(rows, key=lambda r:r['interval_seconds'])
x = np.array([r['interval_seconds'] for r in ordered])
y = np.array([r['logical_error_probability'] for r in ordered])
bounds = np.array([r['logical_wilson_95'] for r in ordered])
fig, ax = plt.subplots(figsize=(7.2, 4.4), layout='constrained')
ax.errorbar(x, y, yerr=[y-bounds[:,0], bounds[:,1]-y], fmt='o',
            mfc='none', color='#176baf', capsize=4, markersize=6)
ax.set_xscale('log')
ax.set_xticks(x, [f'{u:.4g}' for u in x], rotation=30)
ax.set_xlabel('Requested sleep interval Δt (s)')
ax.set_ylabel('Logical error probability')
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.set_ylim(0, max(bounds[:,1])*1.23)
for r in ordered:
    ax.annotate(f"N={r['rounds']}\n{r['logical_failures']}/{r['shots']}",
                (r['interval_seconds'], r['logical_wilson_95'][1]),
                xytext=((-8, 8) if r['rounds'] == 6 else (8, 8) if r['rounds'] == 5 else (0, 6)),
                textcoords='offset points',
                ha=('right' if r['rounds'] == 6 else 'left' if r['rounds'] == 5 else 'center'), fontsize=9)
ax.spines[['top','right']].set_visible(False)
ax.grid(axis='y', alpha=.2)
ax.set_title('Physical H2-2 · d=3 X-memory · all 6,750 shots\nTotal requested sleep 1 s · frozen sleep-dependent MWPM · 95% Wilson intervals', fontsize=11)
fig.savefig(output.with_suffix('.png'), dpi=170)
