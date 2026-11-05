"""Idle tests T0-T5 on H2-1E (the emulator only; T6, real hardware, is excluded).

Each test's question, runs and decision rule are fixed in PLAN before any shots; `plan`
writes them to config/idle_tests.json. Every program is built with pytket + pytket-qir
(Quantinuum's own QIR route, so no hand-edited QIR), and every job sends explicit
emulator options (the earlier hardware arc sent none).

    python -m qec_timing.hardware.idle_tests plan      # write the config, no network
    python -m qec_timing.hardware.idle_tests build     # programs + manifest, no network
    python -m qec_timing.hardware.idle_tests check     # H2-1SC syntax checks (free)
    python -m qec_timing.hardware.idle_tests execute   # H2-1E runs (needs every check accepted)
    python -m qec_timing.hardware.idle_tests fetch     # wait for / collect submitted jobs
    python -m qec_timing.hardware.idle_tests analyze   # results/hardware/h2_1e_idle_tests.json

Env: SG_final_round/env/.venv-idle (pytket 2.18.5, pytket-qir 2.0.2, aqora 0.36.0, and the
repo's qec_timing installed --no-deps for the surface-code checks).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import random
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PLATFORM, CHECK_PLATFORM, ENTITY = "nexus:H2-1E", "nexus:H2-1SC", "q_sq"
OPTIONS = {
    "on": {"simulator": "stabilizer", "noisy_simulation": True, "no_opt": True,
           "error_params": {"idle_dephasing": True, "transport_dephasing": True}},
    "off": {"simulator": "stabilizer", "noisy_simulation": True, "no_opt": True,
            "error_params": {"idle_dephasing": False, "transport_dephasing": False}},
}
T3_SHOTS = {0.0: 20000, 0.04: 90000, 0.07: 36000, 0.1: 20000, 0.2: 6000, 0.35: 2000,
            0.5: 1000, 1.0: 1000}
ROUNDS = 5


def tag(x: float) -> str:
    return f"{x:g}".replace(".", "p")


PLAN = {
    "T0": dict(
        question="Do emulator options sent through aqora take effect?",
        decision="X-basis sleep(1.0) with dephasing off consistent with 0, far below the ~9% "
                 "seen with it on -> options reach the emulator.",
        runs=[dict(name="T0_X_sleep1_off", kind="probe", basis="X", sleep=1.0, options="off",
                   shots=1000)]),
    "T1": dict(
        question="Is the hand-inserted sleep the instruction Quantinuum's own converter emits?",
        decision="Same __quantum__qis__sleep__body(qubit, double) call from pytket-qir -> the "
                 "hand edit is the official instruction. Every program here uses pytket-qir. "
                 "The unit (seconds) is not documented and stays inferred.",
        runs=[]),
    "T2": dict(
        question="Does sleep cause dephasing only, or also bit flips?",
        decision="Z-basis errors consistent with 0 at every sleep -> dephasing only.",
        runs=[dict(name=f"T2_Z_sleep{tag(t)}", kind="probe", basis="Z", sleep=t, options="on",
                   shots=1000) for t in (0.0, 0.1, 0.5, 0.75, 1.0)]),
    "T3": dict(
        question="What are the linear (gamma) and quadratic (f*k) idle terms?",
        decision="Fit P = floor (+) [a + b - 2ab], a = gamma t, b = sin^2(pi fk t), with "
                 "uncertainties; compare with the configured gamma = 0.0028/s, fk = 0.086. "
                 "Shots give >= ~20 expected errors per point under the configured model.",
        runs=[dict(name=f"T3_X_sleep{tag(t)}", kind="probe", basis="X", sleep=t, options="on",
                   shots=n) for t, n in T3_SHOTS.items()]),
    "T4": dict(
        question="Is idling inside a circuit (transport layers) the same noise as sleep?",
        decision="4 qubits in |+>, L layers of [barrier; RZZ(0) on a random pairing], as in "
                 "Quantinuum's memory benchmark. Idle part = rate(on) - rate(off) at L = 64; "
                 "with the T3 curve it converts to seconds per layer. Also: does the rate grow "
                 "with L at all (L = 0, 16, 64)?",
        runs=[dict(name=f"T4_transport_L{L}_{o}", kind="transport", n=4, layers=L, options=o,
                   shots=1000) for L, o in ((0, "on"), (16, "on"), (64, "on"), (64, "off"))]),
    "T5a": dict(
        question="Do sleeps on different qubits run at the same time or one after another?",
        decision="4 qubits in |+>, sleep(0.25) on each in turn. Error ~ P(0.25 s) (~0.5%) -> "
                 "concurrent; ~ P(1 s) (~7-9%) -> serial.",
        runs=[dict(name="T5a_sleep_each_0p25", kind="concurrency", n=4, sleep=0.25,
                   options="on", shots=1000)]),
    "T5": dict(
        question="How long does a d = 3 syndrome round take?",
        decision=f"8 targets in |+> wait (barriers) while the d = 3 X-memory circuit runs "
                 f"{ROUNDS} rounds (one reused ancilla). Idle part = rate(on) - rate(off); "
                 "inverting the T3 curve gives the block's idle time, / rounds = round time. "
                 "A difference consistent with 0 gives an upper bound.",
        runs=[dict(name=f"T5_rounds{ROUNDS}_{o}", kind="rounds", targets=8, rounds=ROUNDS,
                   options=o, shots=1000) for o in ("on", "off")]),
}
RUNS_BY_NAME = {r["name"]: dict(r, test=t) for t, p in PLAN.items() for r in p["runs"]}


# --- programs (pytket -> QIR) ---------------------------------------------------

def prep_x(c, q):
    c.PhasedX(0.5, 0.5, q)        # |0> -> |+>  (Ry(pi/2))


def unprep_x(c, q):
    c.PhasedX(0.5, -0.5, q)       # |+> -> |0>  (Ry(-pi/2)); a Z error then reads 1


def circuit(run: dict):
    from pytket import Circuit

    k = run["kind"]
    if k == "probe":
        c = Circuit(1, 1)
        if run["basis"] == "X":
            prep_x(c, 0)
        if run["sleep"] > 0:
            c.add_barrier([0], data=f"sleep({run['sleep']!r})")
        if run["basis"] == "X":
            unprep_x(c, 0)
        c.Measure(0, 0)
        return c
    if k == "concurrency":
        n = run["n"]
        c = Circuit(n, n)
        for q in range(n):
            prep_x(c, q)
        for q in range(n):
            c.add_barrier([q], data=f"sleep({run['sleep']!r})")
        for q in range(n):
            unprep_x(c, q)
            c.Measure(q, q)
        return c
    if k == "transport":
        n = run["n"]
        c = Circuit(n, n)
        for q in range(n):
            prep_x(c, q)
        rng = random.Random(1000 + run["layers"])
        for _ in range(run["layers"]):
            c.add_barrier(list(range(n)))
            perm = list(range(n))
            rng.shuffle(perm)
            for a, b in zip(perm[::2], perm[1::2]):
                c.ZZPhase(0.0, a, b)
        c.add_barrier(list(range(n)))
        for q in range(n):
            unprep_x(c, q)
            c.Measure(q, q)
        return c
    if k == "rounds":
        from qec_timing.codes.base import checks_of
        from qec_timing.codes.surface import RotatedSurfaceCode

        checks = [ch.extraction_order for ch in checks_of(RotatedSurfaceCode(3), "X")]
        nt, R = run["targets"], run["rounds"]
        # pytket-qir takes the default qubit register only: targets q[0..nt), data, ancilla.
        c = Circuit(nt + 10)
        tq, dq, anc = list(range(nt)), list(range(nt, nt + 9)), nt + 9
        tb = list(c.add_c_register("m", nt))
        sb = list(c.add_c_register("s", R * len(checks)))
        for q in tq + dq:
            prep_x(c, q)
        allq = tq + dq + [anc]
        c.add_barrier(allq)
        for r in range(R):
            for ci, order in enumerate(checks):
                c.H(anc)
                for i in order:
                    c.CX(anc, dq[i])
                c.H(anc)
                c.Measure(anc, sb[r * len(checks) + ci])
                c.Reset(anc)
        c.add_barrier(allq)
        for q, b in zip(tq, tb):
            unprep_x(c, q)
            c.Measure(q, b)
        return c
    raise ValueError(k)


def target_bits(run: dict) -> list:
    """The classical bits that record a memory error (1 = error), as (register, index)."""
    k = run["kind"]
    if k == "probe":
        return [("c", 0)]
    if k in ("concurrency", "transport"):
        return [("c", i) for i in range(run["n"])]
    return [("m", i) for i in range(run["targets"])]


def hqc_estimate(ll: str, shots: int) -> float:
    """Published formula on the program's QIR calls (sleep and barriers not charged)."""
    calls = lambda g: len(re.findall(rf"call [^@]*@__quantum__qis__{g}__body\(", ll))  # noqa: E731
    n1 = calls("phasedx") + calls("h") + calls("rz")
    n2 = calls("rzz") + calls("cnot") + calls("cx")
    nm = calls("mz") + calls("reset") + int(ll.split('"required_num_qubits"="')[1].split('"')[0])
    return 5 + shots * (n1 + 10 * n2 + 5 * nm) / 5000


def build_dir() -> Path:
    from pytket.qir import QIRFormat, QIRProfile, pytket_to_qir

    texts = {n: pytket_to_qir(circuit(r), name=n, qir_format=QIRFormat.STRING,
                              profile=QIRProfile.ADAPTIVE) for n, r in RUNS_BY_NAME.items()}
    ident = hashlib.sha256(json.dumps([PLAN, OPTIONS, texts], sort_keys=True,
                                      default=str).encode()).hexdigest()[:16]
    out = ROOT / "results" / "hardware" / "programs" / f"idle_tests_{ident}"
    if (out / "manifest.json").exists():
        man = json.loads((out / "manifest.json").read_text())
        for n, h in man["bitcode_sha256"].items():
            assert hashlib.sha256((out / f"{n}.bc").read_bytes()).hexdigest() == h, n
        return out
    out.mkdir(parents=True)
    hashes, hqc = {}, {}
    for n, r in RUNS_BY_NAME.items():
        bc = pytket_to_qir(circuit(r), name=n, qir_format=QIRFormat.BINARY,
                           profile=QIRProfile.ADAPTIVE)
        (out / f"{n}.ll").write_text(texts[n])
        (out / f"{n}.bc").write_bytes(bc)
        hashes[n] = hashlib.sha256(bc).hexdigest()
        hqc[n] = round(hqc_estimate(texts[n], r["shots"]), 1)
        if r["kind"] in ("probe", "concurrency") and r.get("sleep", 0) > 0:
            assert "@__quantum__qis__sleep__body(" in texts[n], n
        if r["kind"] == "transport" and r["layers"]:
            assert texts[n].count("@__quantum__qis__rzz__body(double 0.000000e+00") == 2 * r["layers"], n
    (out / "manifest.json").write_text(json.dumps(
        dict(platform=PLATFORM, options=OPTIONS, runs=RUNS_BY_NAME, bitcode_sha256=hashes,
             hqc_estimate=hqc, hqc_estimate_total=round(sum(hqc.values()), 1)), indent=2) + "\n")
    return out


# --- provider -------------------------------------------------------------------

def record_path(stage: str, out: Path, name: str) -> Path:
    return ROOT / "store" / "hardware" / out.name / stage / name


MAX_SHOTS = 10000      # aqora: "Count must be between 1 and 10,000" per job


def parts(stage: str, out: Path, name: str) -> list[tuple[Path, int]]:
    """(record dir, shots) of each job of a run. Runs above MAX_SHOTS are split into
    part<i> jobs of the same program; the analysis pools them."""
    dest, shots = record_path(stage, out, name), RUNS_BY_NAME[name]["shots"]
    if stage == "check":
        return [(dest, 1)]
    if shots <= MAX_SHOTS:
        return [(dest, shots)]
    k = math.ceil(shots / MAX_SHOTS)
    sizes = [shots // k + (i < shots % k) for i in range(k)]
    return [(dest / f"part{i}", n) for i, n in enumerate(sizes)]


def accepted(data: dict) -> bool:
    return (data.get("job") or {}).get("status") == "COMPLETED" and bool(data.get("results")) \
        and not any(r.get("error") for r in data["results"])


def submit(stage: str) -> None:
    from aqora import QPU

    out = build_dir()
    platform = CHECK_PLATFORM if stage == "check" else PLATFORM
    if stage == "execute":
        bad = [n for n in RUNS_BY_NAME if not accepted(json.loads(
            (record_path("check", out, n) / "job.json").read_text()))]
        if bad:
            raise SystemExit(f"syntax check not accepted: {bad}")
    qpu = QPU(platform=platform, as_entity=ENTITY)
    for n, r in RUNS_BY_NAME.items():
        for dest, shots in parts(stage, out, n):
            if (dest / "job.json").exists():
                print(dest.relative_to(ROOT), "already submitted", flush=True)
                continue
            dest.mkdir(parents=True, exist_ok=True)
            req = dict(platform=platform, as_entity=ENTITY, options=OPTIONS[r["options"]],
                       shots=shots, program=str(out / f"{n}.bc"))
            (dest / "request.json").write_text(json.dumps(req, indent=2) + "\n")
            job = qpu.run((out / f"{n}.bc").read_bytes(), shots=shots, options=req["options"])
            (dest / "job.json").write_text(json.dumps(dict(req, job_id=job.job_id), indent=2) + "\n")
            print(dest.relative_to(ROOT), job.job_id, flush=True)
    fetch(stage)


def fetch(stage: str, timeout: float = 3600.0) -> None:
    from aqora import QPUJob

    out = build_dir()
    t0 = time.time()
    while True:
        pending = []
        for rec in (d / "job.json" for n in RUNS_BY_NAME for d, _ in parts(stage, out, n)):
            if not rec.exists():
                continue
            data = json.loads(rec.read_text())
            if accepted(data) or (data.get("job") or {}).get("status") in ("FAILED", "CANCELLED"):
                continue
            job = QPUJob.from_id(data["job_id"])
            state = dict(job.refresh())
            data["job"] = state
            if state.get("status") == "COMPLETED":
                results = job.results(raise_on_item_error=False)
                for res in results:
                    (rec.parent / f"result_{res.index}.txt").write_text(res.raw or "")
                data["results"] = [dict(index=res.index, format=res.serialization_format,
                                        error=getattr(res, "error", None)) for res in results]
            elif state.get("status") not in ("FAILED", "CANCELLED"):
                pending.append(str(rec.parent.relative_to(ROOT)))
            rec.write_text(json.dumps(data, indent=2, default=str) + "\n")
            print(rec.parent.relative_to(ROOT), state.get("status"), state.get("error") or "", flush=True)
        if not pending or time.time() - t0 > timeout:
            print("pending:", pending, flush=True)
            return
        time.sleep(30)


# --- analysis -------------------------------------------------------------------

def errors(out: Path, name: str) -> tuple[int, int]:
    """(memory errors, samples) of an executed run."""
    from pytket.backends.backendresult import BackendResult
    from pytket.circuit import Bit

    keep = ("qubits", "bits", "counts", "shots", "state", "unitary", "density_matrix", "ppcirc")
    bits = [Bit(reg, i) for reg, i in target_bits(RUNS_BY_NAME[name])]
    k = m = 0
    for dest, _ in parts("execute", out, name):
        raw = json.loads((dest / "result_0.txt").read_text())
        br = BackendResult.from_dict({key: v for key, v in raw.items() if key in keep and v not in ([], None)})
        shots = br.get_shots(cbits=bits)
        k, m = k + int(shots.sum()), m + int(shots.size)
    return k, m


def cp(k: int, n: int) -> tuple[float, float]:
    """95% Clopper-Pearson interval (bisection on the binomial tail; no scipy)."""
    def tail(p, lo):
        if p <= 0.0 or p >= 1.0:
            return float(lo) if p >= 1.0 else float(not lo)
        lp, lq = math.log(p), math.log1p(-p)
        terms = [math.lgamma(n + 1) - math.lgamma(j + 1) - math.lgamma(n - j + 1) + j * lp + (n - j) * lq
                 for j in (range(k, n + 1) if lo else range(0, k + 1))]
        top = max(terms)
        return math.exp(top) * sum(math.exp(t - top) for t in terms)
    def solve(f, target):
        a, b = 0.0, 1.0
        for _ in range(60):
            m = (a + b) / 2
            a, b = (m, b) if f(m) < target else (a, m)
        return (a + b) / 2
    lo = 0.0 if k == 0 else solve(lambda p: tail(p, True), 0.025)
    hi = 1.0 if k == n else solve(lambda p: -tail(p, False), -0.025)
    return lo, hi


def model(t, gamma, fk):
    a = gamma * t
    b = math.sin(math.pi * fk * t) ** 2
    return a + b - 2 * a * b


def oplus(x, y):
    return x + y - 2 * x * y


def analyze() -> None:
    out = build_dir()
    rows = {}
    for n, r in RUNS_BY_NAME.items():
        k, m = errors(out, n)
        rows[n] = dict(test=r["test"], k=k, n=m, p=k / m, ci95=cp(k, m) if m <= 20000 else
                       (k / m - 1.96 * math.sqrt(k / m * (1 - k / m) / m),
                        k / m + 1.96 * math.sqrt(k / m * (1 - k / m) / m)))
    # T3 fit: floor (+) model(t), weighted least squares on a grid.
    t3 = [(RUNS_BY_NAME[n]["sleep"], rows[n]) for n in rows if rows[n]["test"] == "T3"]
    floor = next(r["p"] for t, r in t3 if t == 0)
    pts = [(t, r["p"], max(r["p"] * (1 - r["p"]), 1 / r["n"]) / r["n"]) for t, r in t3 if t > 0]
    best = None
    grid = []
    for gi in range(0, 401):
        g = gi * 0.00005                       # 0 .. 0.02 /s
        for fi in range(0, 401):
            fk = 0.05 + fi * 0.0002            # 0.05 .. 0.13
            chi = sum((oplus(floor, model(t, g, fk)) - p) ** 2 / v for t, p, v in pts)
            grid.append((chi, g, fk))
            if best is None or chi < best[0]:
                best = (chi, g, fk)
    within = [(g, fk) for chi, g, fk in grid if chi <= best[0] + 2.30]       # 68% joint
    fit = dict(floor=floor, gamma=best[1], fk=best[2], chi2=best[0], dof=len(pts) - 2,
               gamma_68=(min(g for g, _ in within), max(g for g, _ in within)),
               fk_68=(min(f for _, f in within), max(f for _, f in within)),
               configured=dict(gamma=0.0028, fk=0.086))

    def invert(p_idle):
        """Seconds of sleep that give idle error p_idle on the fitted curve."""
        if p_idle <= 0:
            return 0.0
        a, b = 0.0, 5.0
        for _ in range(80):
            m = (a + b) / 2
            a, b = (m, b) if model(m, fit["gamma"], fit["fk"]) < p_idle else (a, m)
        return (a + b) / 2

    derived = {}
    on, off = rows["T4_transport_L64_on"], rows["T4_transport_L64_off"]
    d = on["p"] - off["p"]
    se = math.sqrt(on["p"] * (1 - on["p"]) / on["n"] + off["p"] * (1 - off["p"]) / off["n"])
    derived["T4"] = dict(idle_part_L64=d, se=se, seconds_per_layer=invert(d) / 64,
                         seconds_per_layer_upper_2se=invert(d + 2 * se) / 64)
    on, off = rows[f"T5_rounds{ROUNDS}_on"], rows[f"T5_rounds{ROUNDS}_off"]
    d = on["p"] - off["p"]
    se = math.sqrt(on["p"] * (1 - on["p"]) / on["n"] + off["p"] * (1 - off["p"]) / off["n"])
    derived["T5"] = dict(idle_part=d, se=se, rounds=ROUNDS, seconds_per_round=invert(d) / ROUNDS,
                         seconds_per_round_upper_2se=invert(d + 2 * se) / ROUNDS)
    c = rows["T5a_sleep_each_0p25"]
    derived["T5a"] = dict(observed=c["p"], fitted_concurrent=oplus(floor, model(0.25, fit["gamma"], fit["fk"])),
                          fitted_serial=oplus(floor, model(1.0, fit["gamma"], fit["fk"])))
    man = json.loads((out / "manifest.json").read_text())
    res = dict(build=out.name, platform=PLATFORM, options=OPTIONS, plan=PLAN, rows=rows,
               t3_fit=fit, derived=derived, hqc_estimate_total=man["hqc_estimate_total"],
               job_ids={n: [json.loads((d / "job.json").read_text())["job_id"] for d, _ in parts("execute", out, n)]
                        for n in RUNS_BY_NAME})
    (ROOT / "results" / "hardware" / "h2_1e_idle_tests.json").write_text(json.dumps(res, indent=2) + "\n")
    for n, r in rows.items():
        print(f"{n:24s} {r['k']:6d}/{r['n']:<7d} {100 * r['p']:7.3f}%  "
              f"[{100 * r['ci95'][0]:.3f}, {100 * r['ci95'][1]:.3f}]")
    print(json.dumps(dict(t3_fit=fit, derived=derived), indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["plan", "build", "check", "execute", "fetch", "analyze"])
    ap.add_argument("--stage", default="execute", choices=["check", "execute"])
    ap.add_argument("--timeout", type=float, default=3600.0, help="fetch: seconds to keep polling")
    a = ap.parse_args()
    if a.action == "plan":
        (ROOT / "config" / "idle_tests.json").write_text(json.dumps(
            dict(platform=PLATFORM, check_platform=CHECK_PLATFORM, as_entity=ENTITY,
                 options=OPTIONS, tests=PLAN), indent=2) + "\n")
    elif a.action == "build":
        o = build_dir()
        print(o, json.loads((o / "manifest.json").read_text())["hqc_estimate_total"], "HQC (estimate)")
    elif a.action == "fetch":
        fetch(a.stage, a.timeout)
    elif a.action == "analyze":
        analyze()
    else:
        submit(a.action)
