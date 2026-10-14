"""Generate the narrative notebooks (thin clients of the package). Run from the repo root:
    .venv-main/bin/python notebooks/_build.py notebooks
then execute them (Jupyter, or nbclient). Edit here, not in the .ipynb files."""
import sys
from pathlib import Path

import nbformat as nbf

OUT = Path(sys.argv[1])
md = lambda s: nbf.v4.new_markdown_cell(s.strip("\n"))
code = lambda s: nbf.v4.new_code_cell(s.strip("\n"))
SETUP = code('''
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
from qec_timing import plotting as P
P.style()
R = Path("..") / "results"
''')
NB = {}

# ---------------------------------------------------------------------------
NB["01_idle_in_applications"] = [
md('''
# 01 — Logical qubits idle most of the time in sequential applications

Resource estimates for fault-tolerant algorithms spend much of
their qubit budget on qubits that wait. Large estimates already treat idle storage as
its own problem, with denser codes for qubits at rest (Gidney 2025, arXiv 2505.15917;
yoked surface codes, arXiv 2312.04522). Here: how much do logical qubits idle in compiled
circuits, and in what stretches?

**Source:** `python -m qec_timing.studies.idle` → `results/idle/idle.json` (pytket compile
to Clifford+T, ASAP schedule; `qec_timing.apps`). Labels: *measured* = computed here;
*interp.* = reading.
'''),
SETUP,
code('''
idle = json.loads((R / "idle" / "idle.json").read_text())
print(f"{'app':<12}{'model':<9}{'qubits':>7}{'idle':>7}{'>=10 steps':>12}{'>=40 rounds (d=5)':>19}{'longest':>9}")
for r in idle["rows"]:
    print(f"{r['app']:<12}{r['time_model']:<9}{r['qubits']:>7}{r['idle_fraction']:>7.0%}"
          f"{r['share_in_stretches_ge_steps']['10']:>12.0%}{r['share_in_stretches_ge_rounds']:>19.0%}"
          f"{r['longest_stretch_steps']:>9.0f}")
'''),
code('''
apps = ["Ising-16x8", "QFT-16", "Adder-8"]
fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4), sharey=True)
for ax, tm, title in zip(axes, ("uniform", "magic"), ("every gate one step", "only non-Clifford gates take time")):
    rows = {r["app"]: r for r in idle["rows"] if r["time_model"] == tm}
    y = np.arange(len(apps))
    idle_frac = [rows[a]["idle_fraction"] for a in apps]
    long = [rows[a]["idle_fraction"] * rows[a]["share_in_stretches_ge_steps"]["10"] for a in apps]
    ax.barh(y, idle_frac, color=P.SEQUENTIAL[1], height=0.55, label="idle, any stretch")
    ax.barh(y, long, color=P.SEQUENTIAL[4], height=0.55, label="idle in stretches >= 10 steps")
    for yi, v in zip(y, idle_frac):
        ax.text(v + 0.015, yi, f"{v:.0%}", va="center", color=P.INK_2, fontsize=9)
    ax.set_yticks(y, apps); ax.set_xlim(0, 1.05); ax.set_xlabel("share of each qubit's active span")
    ax.set_title(title, loc="left"); ax.grid(axis="y", visible=False)
axes[0].legend(loc="lower right", fontsize=8)
fig.suptitle("Idle share of logical qubit time, and the part in long stretches", x=0.01, ha="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* sequential workloads leave most logical qubit time idle: the ripple-carry
  adder 84–87%, the QFT 41–51%. Most of it comes in long stretches: 93% of the adder's idle
  time is in stretches of at least 10 logical steps.
- *Measured:* a local, uniform workload (the Ising Trotter step) idles only in 1–3 step
  gaps: nothing for an interval choice to act on. That is the honest boundary of the claim.
- *Interp.:* with d rounds per logical step (d = 5), a stretch of L steps is a memory of
  5L syndrome rounds. Share of idle time in stretches of at least 50 / 100 / 250 rounds:
  QFT 54–68% / 34–64% / 0–18%, adder 93–95% / 76–92% / 29–77% (ranges over the two time
  models). In those stretches the qubit is a memory, and logical error per unit time — the
  quantity the interval optimises — is what counts. Whether a stretch is long enough
  depends on the optimal interval, which is device-dependent: an interval can only be
  applied in stretches several intervals long.
- *Limits:* 16–18 logical qubits; no routing, factories or rotation synthesis, all of which
  lengthen waiting, so these fractions are lower bounds.
'''),
]

# ---------------------------------------------------------------------------
NB["02_paper_model_guppy_vs_stim"] = [
md('''
# 02 — The paper's model, with noise injected in Guppy, agrees with Stim

Can the paper's phenomenological findings be reproduced with
artificial noise injected inside a Guppy program, as a device program would run? Within
the model's constraints (bit-flip data noise, readout that flips only the record), yes.

**Source:** `python -m qec_timing.validation.crosscheck` → `results/crosscheck/crosscheck.json`.
Rotated surface code, Z basis, p = 0.015, λ = 1, b_read = 1, T = 10, the original Stage 4a
grid at d = 5, 7, 9. Both backends' records are decoded by the same PyMatching decoder.
'''),
SETUP,
code('''
cc = json.loads((R / "crosscheck" / "crosscheck.json").read_text())
s = cc["summary"]
print(f"{s['points_overlapping']}/{s['points']} points: 99.9% intervals overlap")
for k, v in s.items():
    if isinstance(v, dict):
        print(f"{k:<40} chi2 = {v['chi2']:.1f} on {v['n_points']} (p = {v['chi2_p']:.2f}), "
              f"mean offset {v['mean_z_sigma']:+.1f} sigma")
'''),
code('''
fig, ax = plt.subplots(figsize=(7.5, 4))
for d in (5, 7, 9):
    rows = [r for r in cc["rows"] if r["d"] == d]
    dt = np.array([r["dt"] for r in rows])
    st = np.array([r["stim"]["p_L"] for r in rows])
    g = np.array([r["guppy"]["p_L"] for r in rows])
    glo = g - np.array([r["guppy"]["ci"][0] for r in rows]); ghi = np.array([r["guppy"]["ci"][1] for r in rows]) - g
    c = P.SERIES[(5, 7, 9).index(d)]                       # slots 1-3 for this study's distances
    ax.plot(dt, st, "-", color=c, lw=1.5)
    ax.errorbar(dt, g, yerr=[glo, ghi], fmt="o", color=c, ms=5, capsize=0, lw=1)
    P.label_end(ax, dt[-1], st[-1], P.dl(d))
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel(r"interval $\\Delta t$"); ax.set_ylabel(r"logical error $p_L$ at $T = 10$")
ax.set_title("Lines: Stim (200k shots). Points: Guppy, 99.9% intervals", loc="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* all 18 points agree within 99.9% intervals; jointly, χ² = 17.1 on 18 (p = 0.51),
  and the mean Guppy–Stim offset is −1.9σ, below any threshold for a real bias. The new Stim
  numbers also reproduce the original repo's reference (p = 0.92).
- *Measured:* each distance shows the U-shape: too-frequent extraction pays p_stab every
  round, too-rare extraction lets idle errors pile up.
- *Method note:* a first run gave Guppy points at the same distance overlapping per-shot seed
  ranges, which correlated them and faked a d = 7 bias; the package now refuses overlapping
  ranges (`spec.overlapping_seed_ranges`). See `results/crosscheck/README.md`.
- *Constraint:* this model has X-only data noise and ideal gates. It
  validates the injection mechanism and the analysis, not device physics.
'''),
]

# ---------------------------------------------------------------------------
NB["11_program_cost_estimates"] = [
md('''
# 11 — Program size and cost before running anything

How large is the hardware program, and how does it grow? The memory
experiment is compiled to QIR for H2 (Guppy 0.21 → HUGR → QIR, validation on). The HQC
price comes from a syntax-checker job (aqora or Nexus), pending access; the program
statistics here are what can be measured offline.

**Source:** `python -m qec_timing.hardware.cli scaling` (H2 env) → `results/hardware/qir_scaling.json`.
'''),
SETUP,
code('''
sc = json.loads((R / "hardware" / "qir_scaling.json").read_text())
print("versions:", sc["versions"])
print(f"{'d':>3}{'rounds':>8}{'qubits':>8}{'bitcode kB':>12}{'QIR calls':>11}{'RZZ':>7}{'build s':>9}")
for r in sc["rows"]:
    print(f"{r['d']:>3}{r['rounds']:>8}{r['qubits']:>8}{r['bitcode_bytes']/1e3:>12.1f}{r['qir_calls']:>11}{r['rzz']:>7}{r['seconds']:>9.1f}")
'''),
code('''
fig, ax = plt.subplots(figsize=(6.5, 3.6))
for d in (3, 5, 7):
    rows = [r for r in sc["rows"] if r["d"] == d]
    x = [r["rounds"] * (d * d - 1) for r in rows]          # check measurements per shot
    y = [r["qir_calls"] for r in rows]
    ax.plot(x, y, "o-", color=P.D_COLOR[d]); P.label_end(ax, x[-1], y[-1], P.dl(d))
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel(r"syndrome measurements per shot (rounds $\\times$ checks)"); ax.set_ylabel("QIR calls")
ax.set_title(r"Program size grows linearly with rounds $\\times$ checks", loc="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* every program is straight-line (hugr-qir 0.1.2 cannot lower loops), so size
  grows linearly in rounds × checks: one QIR call per gate. d = 7 with 16 rounds is 12,474
  calls and 273 kB, built and validated in about 7 s.
- *Measured:* d = 7 needs 50 qubits, within H2's 56 for the stabilizer emulator; d = 9 (82) does not fit.
- *Interp.:* the RZZ count (one per CNOT) is the dominant cost term in Quantinuum's HQC
  formula, so price scales with rounds × checks too. Extracting less often at fixed total
  time (dt* > 1) cuts it proportionally — the cost side of notebook 10.
- *Pending access:* the HQC estimate itself (`hardware.cli aqora-check` / `nexus-cost`).
'''),
]

# ---------------------------------------------------------------------------
NB["12_hardware_validation_path"] = [
md('''
# 12 — The hardware program, checked end to end before submission

The validated stub (noise injected in-program) becomes a device
program without changing its physics: the same memory experiment, built as QIR from the
code interface, with optional seeded injection. Before spending credits, the exact program
runs on local Selene and must pass the same backend contract as every simulator.

**Source:** `qec_timing.hardware` (`qir`, `selene_local`, `records`, `providers`, `cli`);
programs in `results/hardware/programs/`. This notebook reads their metadata; the local
check runs in the H2 env (`hardware.cli local`), recorded below.
'''),
SETUP,
code('''
for p in sorted((R / "hardware" / "programs").glob("*.json")):
    m = json.loads(p.read_text())
    print(f"{p.stem:<16} {m['n_qubits']:>3} qubits  {m['qir_bitcode_bytes']/1e3:6.1f} kB  "
          f"{sum(m['qir_calls'].values()):>6} calls  p_inject {m['p_inject_effective']:.7f}  "
          f"basis {m['spec']['basis']}, rounds {m['spec']['schedule'].get('n_rounds')}")
'''),
md('''
**The path, and what each step guarantees** (all *measured* in the test suite, `tests/test_hardware.py`):

| step | command (H2 env) | checks |
| --- | --- | --- |
| build | `hardware.cli build --d 3 --basis X --rounds 2 --p-inject 0.05` | QIR validated; byte-identical to the original Stage 7a program |
| local | `hardware.cli local <program>.bc` | backend contract on local Selene: no detections without noise, seeds reach the noise, round-0 detector rate inside the 99.9% binomial interval |
| price | `hardware.cli aqora-check` / `nexus-cost` | syntax checker only: validates and prices, executes nothing |
| run | `hardware.cli nexus-submit --confirm` | emulator first; refuses without `--confirm` |
| fetch, store | `hardware.cli nexus-fetch`, `store` | raw results kept verbatim; converted to a stored run, decoded like any simulation |

**Design choices that matter on a device.**
- Injection uses an integer Bernoulli (`random_int_bounded(2^20) < round(p·2^20)`), because
  hugr-qir 0.1.2 cannot lower `RandomFloat`; the effective p is recorded.
- When the program injects its own dephasing, the emulator's idle dephasing is switched off
  by default, so the two are not double-counted (`providers.nexus_submit`).
- Extraction order is hook-safe for the surface code (`codes/surface.py`): it only matters
  with gate noise, which is exactly the device case.
'''),
]

# ---------------------------------------------------------------------------
NB["05_premise_realistic_noise"] = [
md('''
# 05 — Under realistic circuit noise, the paper's model still describes the circuit

Simulation is not the final question: does the trade-off survive
realistic noise — gate errors, the same idle noise on data and ancillas, native gates — and
does the paper's two-parameter model still describe the circuit?

**Source:** `python -m qec_timing.studies.premise --gates textbook|native` →
`results/premise/premise_{textbook,native}.json`. X-basis memory, H2-1E gate ratios scaled
so p2 = 5e-3, idle noise linear (γ = 0.3 p2), quadratic (c = 0.01 p2) or both, T = 192,
2 × 100k shots per point. Full-circuit numbers equal the original notebooks 08/09 exactly.
'''),
SETUP,
code('''
pr = {g: json.loads((R / "premise" / f"premise_{g}.json").read_text()) for g in ("textbook", "native")}
print(f"{'gates':<9}{'d':>2} {'idle':<10}{'dt* circuit':>12}{'predicted':>11}{'error':>8}{'b_read':>8}{'max P2 dev':>12}")
for g, data in pr.items():
    for r in data["rows"]:
        f, p = r["full"]["optimum"], r["predicted"]["optimum"]
        dev = max(max(abs(x["p_read / p_read(1)"] - 1), abs(x["p_data / [p_data(1) xor q_wait]"] - 1)) for x in r["p2_checks"])
        print(f"{g:<9}{r['d']:>2} {r['idle']:<10}{f['dt_star']:>12.2f}{p['dt_star']:>11.2f}"
              f"{p['dt_star']/f['dt_star']-1:>+8.0%}{r['calibration']['b_read']:>8.3f}{dev:>12.2%}")
'''),
code('''
fig, axes = plt.subplots(1, 3, figsize=(12, 3.6), sharey=False)
for ax, idle in zip(axes, ("lin 0.3", "quad 0.01", "mixed")):
    for r in pr["native"]["rows"]:
        if r["idle"] != idle:
            continue
        c = P.D_COLOR[r["d"]]
        full = r["full"]["points"]; pred = r["predicted"]["points"]
        ax.plot([q["dt"] for q in full], [q["r"] for q in full], "o", color=c, ms=4)
        ax.plot([q["dt"] for q in pred], [q["r"] for q in pred], "-", color=c, lw=1.5)
        o = r["full"]["optimum"]["dt_star"]; ax.axvline(o, color=c, lw=0.8, ls=":", ymax=0.80)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(P.idle_label(idle), loc="left")
    ax.set_xlabel(P.DT_TR)
    lo_, hi_ = ax.get_ylim(); ax.set_ylim(lo_, hi_ * 5)            # headroom for the values
    txt = "    ".join(rf"$d={r['d']}$: {r['full']['optimum']['dt_star']:.2f} / {r['predicted']['optimum']['dt_star']:.2f}"
                      for r in pr["native"]["rows"] if r["idle"] == idle)
    ax.text(0.03, 0.97, r"$\\Delta t^*$ circuit / model" + "\\n" + txt, transform=ax.transAxes, ha="left",
            va="top", fontsize=8, color=P.INK_2)
axes[0].set_ylabel(P.RATE)
from matplotlib.lines import Line2D
handles = [Line2D([], [], color=P.D_COLOR[d], marker="o", ls="-", label=P.dl(d)) for d in (3, 5, 7)]
handles += [Line2D([], [], color=P.MUTED, marker="o", ls="", label="full circuit"),
            Line2D([], [], color=P.MUTED, ls="-", label="model, one calibration"),
            Line2D([], [], color=P.MUTED, ls=":", lw=0.8, label=r"circuit $\\Delta t^*$")]
fig.legend(handles=handles, loc="lower center", ncol=6, bbox_to_anchor=(0.5, -0.04), fontsize=9)
fig.suptitle(r"Native gates: the full circuit against the paper's model calibrated once at $\\Delta t = 1$", x=0.01, ha="left")
fig.tight_layout(rect=(0, 0.06, 1, 1))
'''),
md('''
**Reading.**
- *Measured:* every one of the 18 curves (2 gate sets × 3 distances × 3 idle models) has an
  interior optimum. Realistic noise does not remove the trade-off.
- *Measured:* the paper's model, calibrated **once** at back-to-back rounds (p_data(1),
  p_read from detection events, plus the idle channel for the wait), predicts dt* to
  +15–20% at d = 3, +1–10% at d = 5 and −5…+3% at d = 7. The prediction improves with distance.
- *Measured (P2):* readout and data error rates stay within 0.8% of the one-calibration
  model at longer intervals: the two-number description holds, given the right numbers.
- *Measured, a limit:* the model places the optimum well but underestimates the error rate
  itself, more so with distance (the lines sit below the points at d = 7; the original
  notebook 08 measured prediction/circuit p_L = 0.51 there). Use it to choose dt*, not to
  quote p_L.
- *Where it differs from the paper's assumptions:* the effective rates are not the paper's.
  The data error per round is not uniform across data qubits, native decomposition adds
  gate faults, and two-qubit gates spread errors unevenly, so p_data and b_read must be
  measured from the circuit, not set to p and 1. A hand-built phenomenological decoder
  misses mid-round faults; decoding uses the circuit's full detector error model
  (`backends/stim_circuit`, `stim_native`).
- *Caveat:* in these Stim models ancillas reset every round and the wait is memoryless, so
  P2 is partly structural; whether a device keeps the parameters stable is what hardware
  test T9–T10 would show.
'''),
]

# ---------------------------------------------------------------------------
NB["03_dephasing_needs_x_basis"] = [
md('''
# 03 — Trapped-ion idling is dephasing, and only an X-basis memory sees it

Quantinuum's emulator models idle noise as Z only: a linear term
(probability γt) and a quadratic term (sin²(ωt/2), twirled). A Z-basis memory decodes on
Z checks, which commute with Z errors: it cannot see idling at all, so it shows no
trade-off. The interval study therefore needs |+⟩ logical states and X checks.

This notebook runs a small demonstration through the package (d = 3, Stim, seconds).
`MemorySpec` refuses the blind combination unless it is marked as a deliberate control
(`allow_invisible_noise=True`).
'''),
SETUP,
code('''
from qec_timing.backends.stim_circuit import StimCircuitBackend
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.noise.circuit import CircuitNoise, IdleNoise
from qec_timing.schedule import Schedule
from qec_timing.spec import MemorySpec
from qec_timing.store import Store
from qec_timing.studies import runs

store, backend = Store(Path("..") / "store"), StimCircuitBackend()
gates = dict(p1=9e-5, p2=5e-3, p_meas=4.7e-3, p_init=1.9e-4)        # H2 ratios, scaled x4.76
out = {}
for basis in ("X", "Z"):
    for label, idle in (("dephasing on", IdleNoise(gamma=1.5e-3)), ("dephasing off", IdleNoise())):
        noise = CircuitNoise(**gates, idle=idle, placement="uniform")
        pts = []
        for dt in (1, 2, 4, 8, 16):
            R_ = int(round(48 / dt))
            spec = MemorySpec(RotatedSurfaceCode(3), basis, Schedule.rounds(float(dt), R_), noise,
                              50_000, 4000 + dt, allow_invisible_noise=(basis == "Z"))
            ids, f, n = runs.failures(store, backend, spec)
            pts.append((dt, f / n))
        out[(basis, label)] = pts
for k, v in out.items():
    print(k, [f"{p:.4f}" for _, p in v])
'''),
code('''
fig, axes = plt.subplots(1, 2, figsize=(9.5, 3.4), sharey=True)
for ax, basis in zip(axes, ("X", "Z")):
    for label, ls in (("dephasing on", "-"), ("dephasing off", "--")):
        dt, pl = zip(*out[(basis, label)])
        ax.plot(dt, pl, ls, marker="o", color=P.SERIES[0], label=label)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_xscale("log", base=2); ax.set_xlabel(r"$\\Delta t / t_R$, fixed $T = 48\\,t_R$")
    ax.set_title(f"{basis}-basis memory", loc="left")
axes[0].set_ylabel(P.PL)
fig.suptitle("Dephasing changes the X-basis memory; the Z-basis memory cannot see it", x=0.01, ha="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* turning dephasing on raises the X-basis logical error and grows with the
  interval; in the Z basis the two curves coincide within sampling noise. The original
  notebook 07 measured the same at larger scale: at most 2.1σ in Z against up to 304σ in X.
- *Consequence:* results from Z-basis memories (the paper's bit-flip model, notebook 02) say
  nothing about trapped-ion idling; every circuit-level and hardware study here uses X.
'''),
]

# ---------------------------------------------------------------------------
NB["13_hardware_calibration"] = [
md('''
# 13 — Measuring the device's idle noise, and feeding it back

The regime question (notebook 09) turns on numbers no data sheet
gives: the idle dephasing rates and the round duration. This notebook shows the experiments
that measure them, the fit that turns results into a `Calibration`, and the hand-off to the
regime study — demonstrated on synthetic data with known rates, pending device access.

**Source:** `qec_timing.hardware.calibration_experiments`; programs in
`results/hardware/calibration_programs/` (`hardware.cli calib-build`).
'''),
md('''
**The experiments** (hardware_tests T2–T4 of the original repo):

| test | program | measures |
| --- | --- | --- |
| T2 readout | half the qubits in \\|0⟩, half in \\|1⟩, measured | p_meas0, p_meas1 |
| T3 Z-only check | targets in \\|0⟩, L spectator layers, measured in Z | should not grow with L if idling is Z only |
| T4 idle law | targets in \\|+⟩, L spectator layers, measured in X | γ and c per layer, from the exact emulator form |

**No delay instruction exists** (Guppy 0.21/1.x, pytket), and this toolchain cannot lower
`barrier` to QIR. Idle time is therefore spectator layers of mid-circuit measurement, and the
targets' measurement is ordered after them by feed-forward: a Z on each target conditioned
on the spectators' parity. Z is virtual on H2 (error-free); the analysis undoes it.
'''),
SETUP,
code('''
from qec_timing.hardware import Calibration
from qec_timing.hardware.calibration_experiments import Rate, fit_idle, idle_pz, to_calibration_fields

truth = Calibration.load(Path("..") / "config" / "h2_1e_emulator.json")
tau = 0.01                                          # assumed: 10 ms per spectator layer
n = 8 * 4000                                        # 8 targets x 4000 shots per program
designs = {"0-64 layers": [0, 2, 4, 8, 16, 32, 64],
           "0-400 layers": [0, 25, 50, 100, 200, 300, 400]}   # omega * 400 * tau = 2.2 < pi
fits = {}
for name, layers in designs.items():
    rng = np.random.default_rng(11)
    rates = []
    for L in layers:
        pz = truth.idle_pz(L * tau)
        rates.append(Rate(int(rng.binomial(n, 0.5 * (1 - (1 - 2 * 0.003) * (1 - 2 * pz)))), n))
    fit = fit_idle(layers, rates)
    fits[name] = (layers, rates, fit)
    g, gs = fit["gamma_per_layer"] / tau, fit["gamma_per_layer_se"] / tau
    f = to_calibration_fields(fit, tau)
    print(f"{name:<13} gamma {g:.4f} +/- {gs:.4f} /s (true {truth.gamma})   "
          f"quad rate {f['quad_rate']:.4f} (true {truth.quad_rate})   chi2/dof {fit['chi2_per_dof']:.2f}")
'''),
code('''
fig, axes = plt.subplots(1, 2, figsize=(10, 3.5), sharey=False)
for ax, (name, (layers, rates, fit)) in zip(axes, fits.items()):
    L = np.array(layers); P_obs = np.array([r.p for r in rates]); se = np.array([r.se for r in rates])
    ax.errorbar(L, P_obs, yerr=se, fmt="o", color=P.SERIES[0], ms=5, lw=1)
    Lf = np.linspace(0, L[-1], 200)
    ax.plot(Lf, 0.5 * (1 - (1 - 2 * fit["spam_floor"]) * (1 - 2 * idle_pz(Lf, fit["gamma_per_layer"], fit["c_per_layer"]))),
            "-", color=P.SERIES[0], lw=1.5)
    ax.set_xlabel(r"spectator layers $L$"); ax.set_title(name, loc="left")
axes[0].set_ylabel(r"target flip probability ($X$ basis)")
fig.suptitle("Synthetic H2-1E idling, 10 ms per layer: data and fit", x=0.01, ha="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured (synthetic), a design finding:* the quadratic rate is recovered well (within 1%
  at 0–400 layers). The linear rate is weakly constrained: its contribution is ~0.2% flip
  probability over 0.64 s, under the quadratic term. With 0–64 layers it comes out
  0.0052 ± 0.0023 /s (true 0.0028: consistent, but ±45%); extending to 0–400 layers, still
  inside the model's validity (ω·t < π), halves the uncertainty. Pinning γ to ~10% needs
  roughly 20× the shots at the long-L end. On H2 the quadratic term dominates at the
  timescales that matter (notebook 09), so this is the less important parameter, but the
  grid should still reach seconds of idling (`hardware.cli calib-build --layers ...`).
- `tests/test_hardware.py` pins the fit's recovery and an end-to-end `calib-fit` that writes a
  `Calibration` file from job directories.
- *The hand-off (point 13):* `hardware.cli calib-fit --readout <job> --idle <jobs> --layer-seconds τ`
  writes `config/h2_measured.json`; then
  `python -m qec_timing.studies.regime --calibration config/h2_measured.json --t-round <t_R>`
  reruns notebook 09 at the device's own numbers. Nothing else changes.
- *Open on a device:* the duration of one spectator layer and of one round (from the job's
  duration report or Quantinuum), whether the compiler keeps the programs as written
  (check on the emulator first), and gate errors (taken from the base calibration).
'''),
]

# ---------------------------------------------------------------------------
GRID_LOAD = code('''
grid = json.loads(next((R / "regime" / "grid").glob("regime_*.json")).read_text())
rows = grid["rows"]
T_R = sorted({r["t_round"] for r in rows}); DS = sorted({r["d"] for r in rows})
cell = {(r["t_round"], r["d"]): r for r in rows}
def best(r):                            # lowest used rate and its interval
    return min((p["r"], p["dt"]) for p in r["points"] if p.get("used"))
print("calibration:", grid["calibration"]["source"][:90], "...")
print(f"{len(rows)} (t_R, d) cells; rounds per run {grid['setup']['rounds']}, "
      f"target {grid['setup']['target']} failures per point, max {grid['setup']['max_shots']:,} shots")
''')

NB["09_regime_on_h2"] = [
md('''
# 09 — On H2-1E's rates, when does waiting between rounds pay, and how much?

The full circuit (textbook gates, the same idle noise on every
qubit), at H2-1E's own gate, readout and dephasing rates, unscaled. The one number the data
sheet does not give is the duration of a syndrome round, t_R, so it is the axis: each cell is
a full interval sweep at that t_R and distance.

**Source:** `python -m qec_timing.studies.regime --calibration config/h2_1e_emulator.json
--t-round 0.001 ... 0.3 --distances 3 5 7` → `results/regime/grid/`. Points past the
quadratic model's validity (ω·Δt·t_R ≥ π, where the twirled rotation would "rephase") and
after saturation are excluded; `points_used` counts the rest.
'''),
SETUP, GRID_LOAD,
code('''
print(f"{'t_R ms':>7}" + "".join(f"{'d='+str(d)+' gain':>12}{'dt* ms':>8}" for d in DS) + f"{'idle/round':>12}")
for t in T_R:
    line = f"{t*1e3:>7.1f}"
    for d in DS:
        r = cell.get((t, d))
        line += (f"{r['gain']:>11.2f}{'*' if r['regime'] == 'wait' else ' '}{r['dt_star_seconds']*1e3:>8.0f}"
                 if r else " " * 20)
    print(line + f"{cell[(t, DS[0])]['idle_per_round']:>12.1e}")
print("* = waiting beats back to back by more than 3 sigma")
'''),
code('''
fig, ax = plt.subplots(figsize=(8.5, 3.0))
G = np.array([[cell[(t, d)]["gain"] if (t, d) in cell else np.nan for t in T_R] for d in DS])
top = np.nanmax(np.log10(G))
im = ax.imshow(np.log10(G), aspect="auto", cmap=P.sequential_cmap(), vmin=0, vmax=top)
for i, d in enumerate(DS):
    for j, t in enumerate(T_R):
        r = cell.get((t, d))
        if r:
            txt = f"{r['gain']:.1f}x" if r["regime"] == "wait" else "1x"
            ax.text(j, i, txt, ha="center", va="center", fontsize=8,
                    color="white" if np.log10(r["gain"]) > 0.6 * top else P.INK)
ax.set_xticks(range(len(T_R)), [f"{t*1e3:g}" for t in T_R])
ax.set_yticks(range(len(DS)), [f"d = {d}" for d in DS])
ax.set_xlabel("syndrome round duration $t_R$ (ms)"); ax.grid(False)
ax.set_title("Gain of the optimal interval over back-to-back extraction (rate per unit time)", loc="left")
fig.colorbar(im, ax=ax, label=r"$\\log_{10}$ gain", fraction=0.025, pad=0.01)
fig.tight_layout()
'''),
code('''
fig, axes = plt.subplots(1, 2, figsize=(10, 3.6))
for d in DS:
    ts = [t for t in T_R if (t, d) in cell]
    axes[0].plot([t * 1e3 for t in ts], [cell[(t, d)]["dt_star_seconds"] * 1e3 for t in ts], "o-",
                 color=P.D_COLOR[d], label=P.dl(d))
axes[0].plot([T_R[0] * 1e3, T_R[-1] * 1e3], [T_R[0] * 1e3, T_R[-1] * 1e3], "--", color=P.MUTED, lw=1,
             label="back to back")
axes[0].set_xscale("log"); axes[0].set_yscale("log"); axes[0].legend(fontsize=8)
axes[0].set_xlabel(r"$t_R$ (ms)"); axes[0].set_ylabel(r"optimal period $\\Delta t^*$ (ms)")
axes[0].set_title("Optimal period in physical time", loc="left")
d = 5
for t, c in zip((0.002, 0.03, 0.1), (P.SEQUENTIAL[6], P.SEQUENTIAL[4], P.SEQUENTIAL[2])):
    r = cell.get((t, d))
    if not r:
        continue
    pts = [p for p in r["points"] if p.get("used")]
    axes[1].plot([p["dt"] for p in pts], [p["r"] / pts[0]["r"] for p in pts], "o-", color=c,
                 label=rf"$t_R = {t*1e3:g}$ ms: $\\times${r['gain']:.1f} at $\\Delta t^* = {r['dt_star_rounds']:.1f}$")
axes[1].set_xscale("log"); axes[1].set_yscale("log"); axes[1].legend(fontsize=8)
axes[1].set_xlabel(r"period $\\Delta t$ (rounds)"); axes[1].set_ylabel(r"rate / rate at $\\Delta t$ = 1")
axes[1].set_title(rf"U-curves at $d = {d}$", loc="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* the answer is set by the idle error accumulated per round relative to the
  two-qubit gate error. With rounds of a few ms, idling per round is ~10⁻⁵, far below
  p2 = 10⁻³, and waiting tens of rounds lowers the logical error rate per unit time by an
  order of magnitude or more. As t_R grows the gain shrinks, and once idle error per round
  approaches p2 (t_R ≈ 0.1 s) back to back is best at d ≥ 5.
- *Measured:* while waiting pays, the optimal period in **seconds** stays in a narrow band
  and shortens with distance (the paper's 1/Δt* ∝ d, here in physical time).
- *Interp.:* the decisive unknown for H2 is t_R. Quantinuum's early 7-qubit colour-code
  experiment reported ~200 ms per QEC round (via arXiv 2208.08064; not an H2 figure), which
  would sit in the back-to-back region; faster rounds move a device left on this map. It
  has to be measured on the device.
- *Modelling limits:* the 2π reading of the quadratic rate ("cycles", the conservative
  choice) and equal layer durations are assumptions; the "radians" reading moves dt* by ~4×.
  At d = 7 and short t_R, failures are rare and some points hit the shot cap.
'''),
]

NB["10_time_for_space"] = [
md('''
# 10 — Saving resources with time instead of space

Idle qubits are usually protected by more space: a larger distance,
or a denser storage code. The optimal interval protects them with time: the same code,
extracted less often. Two ways to price that, from the H2-1E regime grid (notebook 09):

- **qubits:** does the optimal interval at distance d beat back-to-back extraction at d + 2?
  If so, waiting replaces a distance step: (d+2)² − d² data qubits per logical qubit
  (rotated surface code; about twice that with ancillas);
- **operations:** per unit time the memory extracts Δt* times less often, so it runs Δt*
  times fewer two-qubit gates and measurements, which dominate a trapped-ion machine's cost
  (Quantinuum's HQC formula weights them; *interp.*).

**Setup (the regime grid of notebook 09; nothing new is simulated here).**
- Circuit: Stim's rotated surface-code memory circuit (H, 4 CX layers, H, measure-reset;
  7 layers per round), X basis, d = 3, 5, 7, decoded by PyMatching on the circuit's DEM.
- Noise: H2-1E emulator defaults, unscaled (p2 = 1.05×10⁻³); idle Z dephasing (linear +
  twirled quadratic) on every qubit, during each layer and during the wait (notebook 03).
- t_R is not published for H2: it is the x-axis, each value a hypothetical device.
- N = 60 rounds per run, so T = 60·Δt·t_R grows with Δt; R = −ln(1−2p_L)/(2T) assumes a
  constant rate per unit time. Per second = per round time / t_R.
- "Optimal interval" is the lowest sampled point of a 14-point Δt grid (1–256 rounds), not
  the fitted Δt*. About 400 failures per point.
'''),
SETUP, GRID_LOAD,
code('''
# Study rates are per unit of round time (T counted in rounds); per second = / t_R.
print(f"{'t_R ms':>7}{'d':>3}{'b2b(d) /s':>11}{'opt(d) /s':>11}{'b2b(d+2) /s':>12}   {'optimal(d) beats b2b(d+2)?':<30}{'extractions':>12}")
for t in T_R:
    for d in DS[:-1]:
        a, b = cell.get((t, d)), cell.get((t, d + 2))
        if not (a and b):
            continue
        r_b2b, r_opt, r_next = (x / t for x in (a["points"][0]["r"], best(a)[0], b["points"][0]["r"]))
        verdict = f"yes: saves {(d + 2)**2 - d**2} data qubits" if r_opt < r_next else "no"
        print(f"{t*1e3:>7.1f}{d:>3}{r_b2b:>11.2e}{r_opt:>11.2e}{r_next:>12.2e}   {verdict:<30}"
              f"{a['dt_star_rounds']:>9.1f}x fewer")
'''),
code('''
from matplotlib.lines import Line2D
fig, ax = plt.subplots(figsize=(7.5, 3.8))
for d in DS:
    ts = [t for t in T_R if (t, d) in cell]
    ax.plot([t * 1e3 for t in ts], [cell[(t, d)]["points"][0]["r"] / t for t in ts], "--", color=P.D_COLOR[d], lw=1.5)
    ax.plot([t * 1e3 for t in ts], [best(cell[(t, d)])[0] / t for t in ts], "o-", color=P.D_COLOR[d])
ax.set_xscale("log"); ax.set_yscale("log")
ax.set_xlabel(r"$t_R$ (ms)"); ax.set_ylabel(r"logical error rate $R$ (s$^{-1}$)")
h = [Line2D([], [], color=P.D_COLOR[d], marker="o", label=P.dl(d)) for d in DS]
h += [Line2D([], [], color=P.MUTED, ls="--", label="back to back"),
      Line2D([], [], color=P.MUTED, marker="o", label="optimal interval")]
ax.legend(handles=h, fontsize=8, ncol=2)
ax.set_title(r"Optimal interval at $d$ against back-to-back extraction at $d + 2$", loc="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* for short rounds the optimal interval at distance d gives a lower logical
  error rate per second than back-to-back extraction at d + 2: up to t_R = 4 ms for
  d = 3 → 5, and up to 2 ms for d = 5 → 7. There, time replaces a distance step, saving
  (d+2)² − d² data qubits per idle logical qubit (16 and 24), with no change to the code.
  For longer rounds the gain is real but smaller than a distance step (notebook 09: ×2–12
  between 4 and 30 ms).
- *Measured:* in the same regime the memory extracts Δt* times less often, tens of times at
  t_R of a few ms, so its gate and measurement count per unit time falls by that factor.
- *Interp., the pitch:* combined with notebook 01 (most logical qubit time in sequential
  workloads is idle, in long stretches), the interval is a free knob acting on most of an
  application's space-time volume. Mis-setting it costs more as d grows (the paper's Γ_opt
  grows exponentially in α ∝ d), so it should be calibrated per device, which takes one
  calibration (notebook 05).
- *Boundary:* a full distance step is saved only for rounds of a few ms; any gain needs idle
  error per round well below p2. On H2 both depend on t_R, unknown until measured
  (notebook 09).
'''),
]

# ---------------------------------------------------------------------------
# Scaling (study A) appended to notebook 02.
NB["02_paper_model_guppy_vs_stim"] += [
md('''
## The paper's scaling: 1/Δt* grows linearly with d

**Source:** `python -m qec_timing.studies.scaling` → `results/scaling/scaling.json`. Same
model, Stim, 15 intervals per distance from 0.2× to 4× Eq. 6's prediction, 200k shots each;
Δt* from the parabola-in-log fit with a bootstrap interval; 1/Δt* = η d + z by weighted
least squares. The paper's slope 0.402 was fitted on d = 11–27 with T = 200.
'''),
code('''
sc = json.loads((R / "scaling" / "scaling.json").read_text())
f = sc["fit"]
print(f"1/dt* = ({f['eta']:.3f} +/- {f['eta_se']:.3f}) d + ({f['z']:.3f} +/- {f['z_se']:.3f});  "
      f"paper slope {f['paper_eta']}: {f['sigma_from_paper']:+.1f} sigma")
for r in sc["rows"]:
    o = r["optimum"]
    print(f"d={r['d']:>2}: dt* = {o['dt_star']:.4f} [{o['lo']:.4f}, {o['hi']:.4f}]   Eq. 6 (g = 0.8): {r['eq6']:.4f}")
'''),
code('''
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
cols = dict(zip([r["d"] for r in sc["rows"]], P.SERIES + ["#e87ba4"]))
for r in sc["rows"]:
    pts = r["points"]; c = cols[r["d"]]
    rr = np.array([p["r"] for p in pts]); dt = np.array([p["dt"] for p in pts])
    axes[0].plot(dt, rr / rr.min(), "o-", color=c, ms=3, lw=1.5,
                 label=rf"$d = {r['d']}$: $\\Delta t^* = {r['optimum']['dt_star']:.3f}$")
    axes[0].axvline(r["optimum"]["dt_star"], color=c, lw=0.8, ls=":")
axes[0].set_xscale("log"); axes[0].set_yscale("log"); axes[0].legend(fontsize=8)
axes[0].set_xlabel(P.DT); axes[0].set_ylabel(r"$R / R_{\\min}$")
axes[0].set_title(r"U-curves (dotted: fitted $\\Delta t^*$)", loc="left")
d = np.array([r["d"] for r in sc["rows"]], float)
y = np.array([1 / r["optimum"]["dt_star"] for r in sc["rows"]])
s = np.array([(1 / r["optimum"]["lo"] - 1 / r["optimum"]["hi"]) / 2 for r in sc["rows"]])
xs = np.linspace(d.min() - 1, d.max() + 1, 50)
axes[1].errorbar(d, y, yerr=s, fmt="o", color=P.SERIES[0], ms=6, label="this work (Stim)")
axes[1].plot(xs, f["eta"] * xs + f["z"], "-", color=P.SERIES[0], lw=1.5, label=rf"fit: $1/\\Delta t^* = {f['eta']:.3f}\\,d {f['z']:+.2f}$")
axes[1].plot(xs, 0.8 * (xs + 1) / 2 - 1, "--", color=P.MUTED, lw=1.2,      # Eq. 6: 1/dt* = lam (alpha - 1)
             label=r"Eq. 6, $g = 0.8$ (slope 0.4)")
gx = [5, 7, 9]; gy = [1 / 0.9343, 1 / 0.5546, 1 / 0.3888]
axes[1].plot(gx, gy, "s", color=P.SERIES[1], ms=5, label="original Stage 4a (Guppy + reference)")
axes[1].set_xlabel(r"distance $d$"); axes[1].set_ylabel(r"$1/\\Delta t^*$"); axes[1].legend(fontsize=8)
axes[1].set_title(rf"Slope ${f['eta']:.3f} \\pm {f['eta_se']:.3f}$ against the paper's $0.402$", loc="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* 1/Δt* is linear in d with slope 0.385 ± 0.013, within 1.3σ of the paper's 0.402,
  and twice as precise as the original Stage 4a fit (0.376 ± 0.026).
- *Measured:* the fitted Δt* sits above Eq. 6 by +38% at d = 5, falling to +11% at d = 11. Eq. 6
  uses the paper's g = 0.8, fitted at d = 11–27; at small d the effective g is lower (original
  Stage 4a: g ≈ 0.70), and the gap closes as d grows, as it should.
'''),
]

NB["04_artificial_idle_effective_parameters"] = [
md('''
# 04 — An artificial idle model, and the circuit's effective λ and b_read

Before realistic idle noise, the arc used Selene's own
error model: a depolarizing Pauli before every native gate, with idling written as explicit
identity operations charged the same rate. It is artificial (ions do not depolarize when
idle, and an Rx(0) has no duration), but it answers a precise question: what λ and b_read
does a real extraction circuit have, compared with the paper's assumed λ = 0.31 and b_read = 1?

**Source:** `python -m qec_timing.studies.effective` → `results/effective/effective.json`.
Selene's native gates mirrored exactly in Stim (`stim_native`), p1 = 5×10⁻⁴ on every
single-qubit gate including Rz, Rzz charged p2 = ρ·p1, readout 2×10⁻³, one idle op per unit
of interval on each data qubit; Z basis. p_data(Δt) and p_read are measured from detection
events at Δt = 1, 2, 4, 8; Eqs. 1–2 make ln(1 − p_data) linear in Δt, giving p_stab and λ.
'''),
SETUP,
code('''
ef = json.loads((R / "effective" / "effective.json").read_text())
print(f"{'d':>2}{'rho':>6}{'p_stab':>10}{'lambda':>9}{'b_read':>8}{'floor':>8}")
for e in ef["params"]:
    print(f"{e['d']:>2}{e['rho']:>6g}{e['p_stab']:>10.2e}{e['lam']:>9.3f}{e['b_read']:>8.3f}{e['b_read_floor']:>8.3f}")
'''),
code('''
fig, axes = plt.subplots(1, 2, figsize=(10.5, 3.6))
for d in sorted({e["d"] for e in ef["params"]}):
    rows = [e for e in ef["params"] if e["d"] == d]
    rho = [max(e["rho"], 0.3) for e in rows]
    axes[0].plot(rho, [e["lam"] for e in rows], "o-", color=P.D_COLOR[d], label=P.dl(d))
    axes[1].plot(rho, [e["b_read"] for e in rows], "o-", color=P.D_COLOR[d], label=P.dl(d))
    axes[1].plot(rho, [e["b_read_floor"] for e in rows], "o--", color=P.D_COLOR[d], ms=3, lw=1.2)
for ax, ref, name in ((axes[0], ef["setup"]["paper_lam"], r"paper $\\lambda = 0.31$ (Willow fit)"),
                      (axes[1], ef["setup"]["paper_b_read"], r"paper $b_{\\rm read} = 1$")):
    ax.axhline(ref, color=P.MUTED, ls="--", lw=1)
    ax.annotate(name, (0.35, ref), xytext=(0, -4), textcoords="offset points", va="top", color=P.INK_2, fontsize=8)
    ax.set_xscale("log"); ax.set_xlabel(r"$\\rho = p_2 / p_1$ ($\\rho = 0$ drawn at 0.3)"); ax.legend(fontsize=8)
axes[0].set_yscale("log"); axes[0].set_ylabel(r"effective $\\lambda$"); axes[1].set_ylabel(r"effective $b_{\\rm read}$")
axes[0].set_title(r"$\\lambda$ falls as two-qubit gates get noisier", loc="left")
axes[1].set_title(r"$b_{\\rm read}$: solid with readout error, dashed its floor ($p_{\\rm meas} = 0$)", loc="left")
fig.tight_layout()
'''),
code('''
fig, axes = plt.subplots(1, len(ef["curves"]), figsize=(4 * len(ef["curves"]), 3.4), sharey=False)
for ax, c in zip(np.atleast_1d(axes), ef["curves"]):
    col = P.D_COLOR[c["d"]]
    for key, ls, lab in (("paper", ":", r"paper $\\lambda$, $b_{\\rm read}$"),
                         ("effective", "-", r"circuit's own $\\lambda$, $b_{\\rm read}$")):
        pts = c[key]["points"]
        ax.plot([p["dt"] for p in pts], [p["pL"] for p in pts], ls, marker="o", ms=3, color=col, label=lab)
        ax.axvline(c[key]["optimum"]["dt_star"], color=col, ls=ls, lw=0.8)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(P.dl(c["d"]), loc="left")
    ax.set_xlabel(r"$\\Delta t$ ($T = 96$)"); ax.legend(fontsize=8)
np.atleast_1d(axes)[0].set_ylabel(P.PL)
fig.suptitle(r"Same $p_{\\rm stab}$: the paper's $\\lambda$, $b_{\\rm read}$ (dotted) against the circuit's own (solid)", x=0.01, ha="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* with only single-qubit noise (ρ = 0), the circuit's effective λ is well below the
  paper's 0.31: an extraction round already charges each data qubit several gate-errors' worth,
  so one idle op is small in comparison. λ falls further as ρ grows.
- *Measured:* b_read (solid) includes the 2×10⁻³ readout error and so sits well above 1 at these
  small gate rates; its floor (dashed, readout error off: what the ancilla's gate noise alone
  adds, the original repo's definition) is the circuit-structure part. Both fall as two-qubit
  noise grows, because the data error grows faster than the record error.
- *Measured:* those parameters move Δt*: with the circuit's own λ and b_read the optimum is
  2.2× (d = 5) and 2.5× (d = 7) longer than with the paper's, exactly the λ ratio Eq. 6 predicts
  (Δt* ∝ 1/λ: 0.31/0.131, 0.31/0.125); 4.1× at d = 3, where the readout term adds to it. Shots
  are sized per point to ~300 failures; with a fixed 100k shots the d = 7 curves (20–90
  failures per point) could not locate the minimum. The paper's two numbers are circuit
  properties to be measured, not constants.
- *Limit:* this idle model (depolarizing, an op count with no duration) is not trapped-ion
  physics, which is time-based Z dephasing on every qubit (notebook 03).
'''),
]

NB["06_per_qubit_error"] = [
md('''
# 06 — Data qubits are not equal: per-qubit error and where it comes from

The paper gives every data qubit the same flip probability per round.
In the circuit each qubit's error depends on how many CNOTs it sits in, at which end, and on
faults that spread to it from ancillas through later CNOTs (hook errors).

**Source:** `python -m qec_timing.studies.per_qubit` → `results/per_qubit/per_qubit.json`.
One round of the actual noisy circuit (premise settings: H2 ratios scaled to p2 = 5×10⁻³,
linear idle γ = 0.3 p2 on every qubit, X basis) in Stim's Pauli-frame simulator, 200k frames;
the Z component on each data qubit after the round. Split by keeping one noise class at a time.
'''),
SETUP,
code('''
pq = json.loads((R / "per_qubit" / "per_qubit.json").read_text())
for r in pq["rows"]:
    z = {k: np.array(v) for k, v in r["z"].items()}
    print(f"d={r['d']} {r['gates']:<8} mean {z['total'].mean():.2e}  range {z['total'].min():.2e}-{z['total'].max():.2e}  "
          f"(x{z['total'].max() / z['total'].min():.1f})   shares: data {z['data'].sum() / z['total'].sum():.0%}, "
          f"propagated {z['ancilla'].sum() / z['total'].sum():.0%}, idle {z['idle'].sum() / z['total'].sum():.0%}")
'''),
code('''
rows = [r for r in pq["rows"] if r["d"] == max(x["d"] for x in pq["rows"])]
fig, axes = plt.subplots(1, len(rows), figsize=(4.6 * len(rows), 4))
vmax = max(max(r["z"]["total"]) for r in rows)
for ax, r in zip(np.atleast_1d(axes), rows):
    d = r["d"]; M = np.full((d, d), np.nan)
    for (row, col), v in zip(r["grid"], r["z"]["total"]):
        M[int(row), int(col)] = v
    im = ax.imshow(M, cmap=P.sequential_cmap(), vmin=0, vmax=vmax)
    for i in range(d):
        for j in range(d):
            ax.text(j, i, f"{M[i, j] * 100:.2f}", ha="center", va="center", fontsize=7,
                    color="white" if M[i, j] > 0.6 * vmax else P.INK)
    ax.set_xticks([]); ax.set_yticks([]); ax.grid(False)
    ax.set_title(rf"$d = {d}$, {r['gates']} gates (% per round)", loc="left")
fig.colorbar(im, ax=axes, label="Z-error probability per round", fraction=0.03)
'''),
code('''
r = next(x for x in pq["rows"] if x["d"] == min(y["d"] for y in pq["rows"]) and x["gates"] == "native")
z = {k: np.array(v) for k, v in r["z"].items()}
order = np.argsort(-z["total"]); x = np.arange(len(order))
fig, ax = plt.subplots(figsize=(8, 3.4))
bottom = np.zeros(len(order))
for key, col, lab in (("data", P.SEQUENTIAL[5], "own (gates on the data qubit)"),
                      ("ancilla", P.SERIES[1], "propagated from ancillas"),
                      ("idle", P.SEQUENTIAL[2], "idling")):
    ax.bar(x, z[key][order], bottom=bottom, color=col, width=0.7, label=lab, edgecolor=P.SURFACE, linewidth=1)
    bottom += z[key][order]
ax.plot(x, z["total"][order], "_", color=P.INK, ms=14, mew=1.5, label="total (all noise at once)")
ax.set_xticks(x, [f"q{i}" for i in order]); ax.set_ylabel("Z-error probability per round")
ax.legend(fontsize=8); ax.set_title(rf"$d = {r['d']}$, native gates: sources per data qubit", loc="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* per-round error varies about 3× across data qubits: corner and edge qubits sit in
  fewer CNOTs than bulk qubits. The paper's model replaces this with one number.
- *Measured:* with native gates 16–17% of the data error arrives by propagation from ancillas
  (7–9% with textbook gates): the native CNOT decomposition puts noisy single-qubit gates on the
  ancillas, and their faults spread through later CNOTs.
- *Consequence:* a decoder or a model that assumes uniform, independent data errors misses
  structure that the circuit's own detector error model contains.
- *Note:* these are physical error frames; the effective p_data measured from detection events
  (notebook 05) is lower, because correlated pairs from one fault (hooks) count once there.
'''),
]

NB["07_decoder_matters"] = [
md('''
# 07 — The decoder decides the answer, not only the error rate

Decoding with the paper's phenomenological graph (the natural choice when
only p_data and p_read are known) against decoding with the circuit's full detector error model,
on the same detection events.

**Source:** `python -m qec_timing.studies.decoders` → `results/decoders/decoders.json`. The
premise study's native-gate runs (linear idle γ = 0.3 p2), each decoded twice: PyMatching on the
circuit's exact DEM, and PyMatching on the paper's model with the same circuit's measured
p_data(Δt) and p_read.
'''),
SETUP,
code('''
dec = json.loads((R / "decoders" / "decoders.json").read_text())
for r in dec["rows"]:
    ratio = np.array([p["pL_paper"] / p["pL_full"] for p in r["points"]])
    print(f"d={r['d']} {r['idle']}: p_L ratio (paper graph / full DEM) {ratio.min():.2f}-{ratio.max():.2f};  "
          f"dt* full {r['optimum_full']['dt_star']:.2f}, with the paper graph {r['optimum_paper']['dt_star']:.2f}")
'''),
code('''
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
for r in dec["rows"]:
    c = P.D_COLOR[r["d"]]; pts = r["points"]
    dt = [p["dt"] for p in pts]
    axes[0].plot(dt, [p["r_full"] for p in pts], "-o", color=c, ms=3,
                 label=rf"$d = {r['d']}$, full DEM: $\\Delta t^* = {r['optimum_full']['dt_star']:.1f}$")
    axes[0].plot(dt, [p["r_paper"] for p in pts], ":", marker="o", ms=3, color=c,
                 label=rf"$d = {r['d']}$, paper graph: $\\Delta t^* = {r['optimum_paper']['dt_star']:.1f}$")
    axes[1].plot(dt, [p["pL_paper"] / p["pL_full"] for p in pts], "o-", color=c, ms=3, label=P.dl(r["d"]))
axes[0].set_xscale("log"); axes[0].set_yscale("log"); axes[0].legend(fontsize=7, ncol=2)
axes[0].set_xlabel(P.DT_TR); axes[0].set_ylabel(P.RATE)
axes[0].set_title("Same shots, two decoders", loc="left")
axes[1].axhline(1, color=P.MUTED, lw=1, ls="--"); axes[1].set_xscale("log"); axes[1].legend(fontsize=8)
axes[1].set_xlabel(P.DT_TR); axes[1].set_ylabel(r"$p_L^{\\rm paper\\ graph} / p_L^{\\rm full\\ DEM}$")
axes[1].set_title("What the simple decoder loses", loc="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* the phenomenological graph loses most at short intervals, where mid-round and
  hook faults (which it cannot represent) are a larger share of all faults, and the loss grows
  with distance.
- *Measured, the important part:* because the loss depends on Δt, the simple decoder also moves
  the optimum, here to a much longer interval. A study that used it would recommend the wrong
  interval. Every circuit-level result in this repo decodes with the full DEM.
'''),
]

NB["08_dt_star_vs_idle_strength"] = [
md('''
# 08 — How the optimum moves with idle-noise strength, and why

Across idle strengths, with gates held fixed: does Δt* follow the
scaling the paper's ansatz implies, and where does waiting stop paying?

**Source:** `python -m qec_timing.studies.idle_scaling` → `results/idle_scaling/idle_scaling.json`.
Original notebook 07's setup (reproduced exactly): textbook gates, idle once per interval on
the data, X basis, H2 ratios scaled to p2 = 5×10⁻³, T = 192. Linear γ/p2 ∈ {0.15, 0.3, 0.6},
quadratic c/p2 ∈ {0.0025, 0.01, 0.04}. The ansatz R = (A/Δt)(1 + q(Δt)/p_e)^α is fitted per
distance to all six curves and then predicts Δt* for any idle error per round.
'''),
SETUP,
code('''
isc = json.loads((R / "idle_scaling" / "idle_scaling.json").read_text())
for r in isc["rows"]:
    s, f = r["slopes"], r["ansatz"]
    print(f"d={r['d']}: slope linear {s['lin']['slope']:.3f} ± {s['lin']['se']:.3f} (predicted -1), "
          f"quadratic {s['quad']['slope']:.3f} ± {s['quad']['se']:.3f} (predicted -0.5);  "
          f"alpha {f['alpha']:.2f} ± {f['alpha_se']:.2f} -> g = {f['implied_g']:.2f} (paper 0.8)")
'''),
code('''
fig, axes = plt.subplots(1, 2, figsize=(11, 3.8))
for ax, fam, xlab, pred in ((axes[0], "lin", r"$\\gamma / p_2$", -1.0), (axes[1], "quad", r"$c / p_2$", -0.5)):
    for r in isc["rows"]:
        cs = [c for c in r["curves"] if c["family"] == fam]
        x = np.array([c["value"] for c in cs]); y = np.array([c["optimum"]["dt_star"] for c in cs])
        lo = y - np.array([c["optimum"]["lo"] for c in cs]); hi = np.array([c["optimum"]["hi"] for c in cs]) - y
        ax.errorbar(x, y, yerr=[lo, hi], fmt="o", color=P.D_COLOR[r["d"]], ms=5,
                    label=rf"$d = {r['d']}$: slope ${r['slopes'][fam]['slope']:.2f} \\pm {r['slopes'][fam]['se']:.2f}$")
        m = r["slopes"][fam]["slope"]; xs = np.geomspace(x.min() * 0.8, x.max() * 1.25, 20)
        ax.plot(xs, y[1] * (xs / x[1]) ** m, "-", color=P.D_COLOR[r["d"]], lw=1.2)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.legend(fontsize=8)
    ax.set_xlabel(xlab); ax.set_ylabel(r"$\\Delta t^* / t_R$")
    ax.set_title(f"{'linear' if fam == 'lin' else 'quadratic'} idle: predicted slope {pred}", loc="left")
fig.tight_layout()
'''),
code('''
fig, axes = plt.subplots(1, len(isc["rows"]), figsize=(4 * len(isc["rows"]), 3.6), sharey=True)
for ax, r in zip(np.atleast_1d(axes), isc["rows"]):
    for fam, col in (("lin", P.SERIES[0]), ("quad", P.SERIES[1])):
        F = r["formula"][fam]
        ax.plot([q["q_over_p2"] for q in F], [q["dt_star"] for q in F], "-", color=col, lw=1.5,
                label=f"ansatz, all {'linear' if fam == 'lin' else 'quadratic'}")
        cs = [c for c in r["curves"] if c["family"] == fam]
        q1 = [(c["value"] if fam == "lin" else np.sin(np.sqrt(c["value"] * 5e-3)) ** 2 / 5e-3) for c in cs]
        ax.plot(q1, [c["optimum"]["dt_star"] for c in cs], "o", color=col, ms=5)
    ax.axhline(1, color=P.MUTED, lw=1); ax.text(1.2e-3, 0.75, "below: back to back is best", color=P.INK_2, fontsize=8)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.set_title(P.dl(r["d"]), loc="left")
    ax.set_xlabel(r"idle error per round $q(1) / p_2$")
np.atleast_1d(axes)[0].set_ylabel(r"$\\Delta t^* / t_R$"); np.atleast_1d(axes)[0].legend(fontsize=8)
fig.suptitle("Points: simulated. Lines: the ansatz fitted per distance", x=0.01, ha="left")
fig.tight_layout()
'''),
md('''
**Reading.**
- *Measured:* Δt* follows the power laws the ansatz implies, γ⁻¹ for linear idle and c^(−1/2) for
  quadratic, at every distance (original notebook 07: −1.06…−1.07 and −0.51…−0.52).
- *Measured:* the fitted α corresponds to g below the paper's 0.8 at these small distances
  (as in the scaling study, notebook 02).
- *Interp.:* the crossing of the lines with Δt* = 1 is the boundary of the useful regime, in
  units of idle error per round over p2: waiting pays only when idling per round is well below
  the two-qubit gate error. A device's position on this axis is set by its round duration t_R.
'''),
]

MAP_CELLS = [
md('''
## Where waiting pays, over the whole idle plane (figure 07c, revised)

The calibrated ansatz's Δt* over the plane of linear and quadratic idle strength, per distance.
Inside the dashed box simulations exist (the six fitted curves sit on its edges); outside it
the formula is extrapolated (pale). The white line is Δt* = 1: beyond it, back to back is best.
The star is a simulation with **both** idle terms that was held out of the fit, the test of
the formula. The dark line is H2-1E's emulator idle rates for round durations t_R from 1 to
300 ms: the device's position in this plane is set by t_R (γ/p2 ∝ t_R, c/p2 ∝ t_R²).

*Assumption:* the axes are idle strength relative to p2, so the map built at scaled gates
(p2 = 5×10⁻³) is read at H2's own p2; notebook 07 of the original repo checked that halving
all rates leaves Δt* unchanged.
'''),
code('''
import math
from matplotlib.colors import BoundaryNorm
cal = json.loads((Path("..") / "config" / "h2_1e_emulator.json").read_text())
omega = 2 * math.pi * cal["quad_rate"] * cal["quad_factor"]          # "cycles" reading
tR = np.geomspace(1e-3, 0.3, 60)
h2_g = cal["gamma"] * tR / cal["p2"]; h2_c = (omega * tR / 2) ** 2 / cal["p2"]
fig, axes = plt.subplots(1, len(isc["rows"]), figsize=(4.6 * len(isc["rows"]), 4.3), sharey=True)
levels = np.arange(-0.5, 2.51, 0.25)
cmap = P.sequential_cmap(); norm = BoundaryNorm(levels, cmap.N)
lin, quad = isc["setup"]["lin"], isc["setup"]["quad"]
for ax, r in zip(np.atleast_1d(axes), isc["rows"]):
    ax_ = np.array(r["map"]["axis"]); Z = np.log10(np.array(r["map"]["dt_star"]))
    cs = ax.contourf(ax_, ax_, Z, levels=levels, cmap=cmap, norm=norm, extend="both")
    ax.contour(ax_, ax_, Z, levels=[0.0], colors="white", linewidths=2)
    # extrapolated region: everything outside the simulated box
    box = (min(lin), max(lin), min(quad), max(quad))
    from matplotlib.patches import Rectangle
    for x0, y0, x1, y1 in ((box[1], ax_[0], ax_[-1], ax_[-1]), (ax_[0], box[3], box[1], ax_[-1])):
        ax.add_patch(Rectangle((x0, y0), x1 - x0, y1 - y0, color=P.SURFACE, alpha=0.55, lw=0, zorder=2))
    ax.plot([ax_[0], box[1], box[1]], [box[3], box[3], ax_[0]], "--", color=P.INK, lw=1)
    ax.plot(lin, [ax_[1]] * 3, ">", color="white", mec=P.INK, ms=7)
    ax.plot([ax_[1]] * 3, quad, "^", color="white", mec=P.INK, ms=7)
    h = r["held_out"]
    ax.plot(h["gamma_over_p2"], h["c_over_p2"], "*", color=P.SERIES[1], mec=P.INK, ms=15)

    ax.plot(h2_g, h2_c, "-", color=P.INK, lw=1.8)
    for t in (2e-3, 1e-2, 3e-2, 0.1, 0.3):
        g_, c_ = cal["gamma"] * t / cal["p2"], (omega * t / 2) ** 2 / cal["p2"]
        if g_ > ax_[0] and c_ > ax_[0]:
            ax.plot(g_, c_, "o", color=P.INK, ms=4)
            ax.annotate(f"{t*1e3:g} ms", (g_, c_), xytext=(4, -3), textcoords="offset points", fontsize=8, color=P.INK)
    ax.set_xscale("log"); ax.set_yscale("log"); ax.grid(False)
    ax.set_xlim(ax_[0], ax_[-1]); ax.set_ylim(ax_[0], ax_[-1])
    ax.set_xlabel(r"linear idle $\\gamma / p_2$")
    ax.set_title(rf"$d = {r['d']}$.  Held out (star): {h['optimum']['dt_star']:.2f} simulated, {h['formula_dt_star']:.2f} formula",
                 loc="left", fontsize=9)
np.atleast_1d(axes)[0].set_ylabel(r"quadratic idle $c / p_2$")
fig.colorbar(cs, ax=axes, label=r"$\\log_{10}(\\Delta t^* / t_R)$", fraction=0.025, pad=0.02)
fig.suptitle(r"Optimal interval over the idle plane. White line: $\\Delta t^* = 1$. Dark line: H2-1E idle rates by round duration $t_R$", x=0.01, ha="left")
'''),
md('''
**Reading.**
- *Measured:* the held-out simulation (both idle terms at once) is predicted to within 4–6%
  (Δt* 5.10, 3.55, 2.63 simulated against 5.39, 3.73, 2.73 at d = 3, 5, 7), with the formula
  slightly long; inside the box the map is a calibrated prediction, not just a fit.
- *Interp.:* the white line is the regime boundary in idle-noise space. H2-1E's trajectory
  crosses it at a round duration of tens of ms (a fitted formula at scaled gates, not a
  simulation at H2's own rates).
- *Limits:* outside the box (pale) the formula is extrapolated; the quadratic search stops at
  the term's first maximum, where the twirled model stops describing decoherence.
'''),
]
NB["08_dt_star_vs_idle_strength"] += MAP_CELLS

for name, cells in NB.items():
    # Every figure cell also writes its PNG to notebooks/figures/<notebook>_<n>.png.
    k = 0
    for c in cells:
        if c.cell_type == "code" and "plt.subplots" in c.source:
            k += 1
            c.source += f'\nP.save(fig, "{name}_{k}")'
    nb = nbf.v4.new_notebook()
    nb["cells"] = cells
    nb["metadata"] = {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
                      "language_info": {"name": "python"}}
    nbf.write(nb, OUT / f"{name}.ipynb")
    print("wrote", name)
