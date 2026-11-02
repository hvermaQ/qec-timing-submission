"""Returned emulator jobs -> the summaries in results/hardware/ that notebooks 13-15 read.
Main env (Stim, PyMatching, pytket). Spends nothing: reads only <store>/hardware/.

    python -m qec_timing.hardware.cli collect

Two kinds of number are written, and the files keep them apart by name:
- from the returned shots (detector rates, logical flips, decoded failures, idle flip
  counts and fits, syntax-check outputs): exact, the same on every rerun;
- model predictions (keys starting `stim_`, the model curves): Stim samples of the
  paper's model or of the hardware program (`program_model`), with the shots and seeds in
  MODEL below, so reruns are identical.

The analysis choices below are the ones the committed results were made with
(emulator_runs.md). Their seeds were not recorded at the time; the ones here were recovered
by reproducing the committed numbers, all of them exactly except the H2-2E-gate model curve
(seed not found; a fixed one is used, within shot noise of the original).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path

import numpy as np

from qec_timing.codes.base import checks_of
from qec_timing.hardware.calibration_experiments import Rate, fit_idle, fit_readout, flips
from qec_timing.hardware.providers import _register_builtins, load_shots
from qec_timing.hardware.records import add_record_flips, bits_from_shots, record_from_bits
from qec_timing.spec import MemorySpec, spec_from_json

# d = 3 memory (H2-1E): decoded on the paper's graph, p_data = injected p (2e-3 without).
D3_P_READ, D3_P_FLOOR = 1e-3, 2e-3
# d = 5 sweep (H2-2E): the paper's model; record flips added offline, seeded 700 + R.
SWEEP_P, SWEEP_LAM, SWEEP_P_READ, SWEEP_T = 0.015, 1.0, 0.015, 10.0
MODEL_R = (40, 30, 20, 14, 10, 8, 6, 5, 4, 3, 2)
# Program model at H2-2E rates: p1, p2 from Quantinuum's H2-2E emulator page; p_meas and
# p_init are H2-1E's (an assumption: H2-2E's are not listed separately).
H22E = {"p1": 7.3e-5, "p2": 1.29e-3, "p_meas": 1e-3, "p_init": 4e-5}
LONG_IDLE = {"X": (0, 16, 32, 64, 128), "Z": (64,)}
# (shots, seed) of each model prediction.
MODEL = {"d3_paper": (200_000, 7),                 # stim_* in h2_1e_memory_d3.json
         "sweep_paper": (50_000, 0),               # stim_pL in h2_2e_dt_sweep_d5.json
         "program_injected": (200_000, 1),         # stim_program_injected_only
         "program_H22E": (200_000, 2),             # stim_program_with_H22E_gates
         "curve_injected": (60_000, 3),            # model curves
         "curve_H22E": (60_000, 4)}


def record_flip_seed(n_rounds: int) -> int:
    return 700 + n_rounds


@dataclass(frozen=True)
class Job:
    """One job directory: <utc stamp>_<provider>_<program>_<platform>/."""
    path: Path
    program: str
    platform: str            # H2-1E, H2-2SC, ...
    record: dict | None      # job.json; None if the request was never accepted

    @property
    def status(self) -> str | None:
        return (self.record.get("job") or {}).get("status") if self.record else None

    @property
    def shots(self) -> int | None:
        return self.record.get("shots") if self.record else None

    @property
    def has_result(self) -> bool:
        return any(self.path.glob("result_*.txt")) or (self.path / "result_qsys.json").exists()

    def meta(self) -> dict:
        m = json.loads((self.path / "program.json").read_text())
        return m.get("meta", m)


_DIR = re.compile(r"^\d{8}T\d{6}Z_[a-z]+_(?P<program>.+)_(?P<platform>H2-\d[A-Z]+)$")


def jobs(store_hw: Path) -> list[Job]:
    out = []
    for d in sorted(p for p in store_hw.iterdir() if p.is_dir()):
        if (m := _DIR.match(d.name)):
            rec = json.loads((d / "job.json").read_text()) if (d / "job.json").exists() else None
            out.append(Job(d, m["program"], m["platform"], rec))
    return out


def pick(js: list[Job], program: str, platform: str, shots: int | None = None) -> Job | None:
    """The latest job of `program` on `platform` that returned a result."""
    hits = [j for j in js if j.program == program and j.platform == platform and j.has_result
            and (shots is None or j.shots == shots)]
    return hits[-1] if hits else None


def bits(job: Job) -> tuple[MemorySpec, np.ndarray, np.ndarray]:
    spec = spec_from_json(job.meta()["spec"])
    syn, dat = bits_from_shots(load_shots(job.path), spec.schedule.n_rounds,
                               len(checks_of(spec.code, spec.basis)), spec.code.n_data)
    return spec, syn, dat


def failures(dem: str, det: np.ndarray, obs: np.ndarray) -> int:
    from qec_timing.decoders.pymatching_decoder import PyMatchingDecoder
    return int((PyMatchingDecoder(dem).decode_batch(det) != obs).any(axis=1).sum())


def sample(circuit, shots: int, seed: int, dem: str | None = None) -> tuple[float, np.ndarray]:
    """(p_L decoded with `dem` or the circuit's own DEM, detector rates)."""
    det, obs = circuit.compile_detector_sampler(seed=seed).sample(shots, separate_observables=True)
    dem = dem or str(circuit.detector_error_model(decompose_errors=True))
    return failures(dem, det, obs) / shots, det.mean(axis=0)


# --- memory and the d = 5 sweep -------------------------------------------------

def paper_graph(spec: MemorySpec, p: float, lam: float, p_read: float) -> MemorySpec:
    from qec_timing.noise.paper import PaperNoise
    return replace(spec, noise=PaperNoise(p, lam, b_read=p_read / p, pauli="Z"))


def memory_d3(js: list[Job]) -> dict:
    from qec_timing.backends.stim_phenom import build_circuit, dem_for

    runs = {}
    for program in ("d3_X_r2_p0", "d3_X_r2_p0.05"):
        job = pick(js, program, "H2-1E")
        if job is None:
            continue
        spec, syn, dat = bits(job)
        rec = record_from_bits(spec, syn, dat)
        p = float(spec.noise.params().get("p", 0.0))
        graph = paper_graph(spec, p or D3_P_FLOOR, 0.0, D3_P_READ)
        row = {"injected_p": p, "shots": rec.shots,
               "detector_rates": rec.detectors.mean(axis=0).tolist(),
               "raw_logical_flips": int(rec.observables.sum()),
               "decoded_failures": failures(dem_for(graph), rec.detectors, rec.observables)}
        if p:
            pL, rates = sample(build_circuit(graph), *MODEL["d3_paper"], dem_for(graph))
            row |= {"stim_detector_rates": rates.tolist(), "stim_pL": pL}
        runs[program] = row
    return {"setup": "d=3 rotated surface code, X basis, 2 rounds, one reused ancilla; H2-1E via "
                     "aqora (q_sq), 100 shots; decoded with the paper-model graph (p_data = "
                     f"injected p or {D3_P_FLOOR:g}, p_read = {D3_P_READ:g}); stim_* = that "
                     f"graph's model in Stim, {MODEL['d3_paper'][0]} shots",
            "runs": runs}


def sweep_spec(R: int, shots: int = 1000, seed: int = 0) -> MemorySpec:
    """The d = 5 sweep program's spec (as `hardware.cli build --total-time 10`)."""
    from qec_timing.codes.surface import RotatedSurfaceCode
    from qec_timing.noise.paper import PaperNoise
    from qec_timing.schedule import Schedule
    return MemorySpec(RotatedSurfaceCode(5), "X", Schedule.rounds(SWEEP_T / R, R),
                      PaperNoise(SWEEP_P, SWEEP_LAM, b_read=0.0, pauli="Z"), shots, seed)


def dt_sweep_d5(js: list[Job]) -> tuple[dict, dict]:
    """(h2_2e_dt_sweep_d5.json, h2_2e_dt_sweep_d5_circuit_decoder.json)."""
    from qec_timing.backends.stim_phenom import build_circuit, dem_for
    from qec_timing.hardware.program_model import program_circuit

    done = {}
    for j in js:      # every sweep point that ran to completion, result returned or not
        if j.program.startswith("d5_X_r") and j.platform == "H2-2E" and j.status == "COMPLETED":
            done[j.program] = pick(js, j.program, "H2-2E") or j
    rows, model_rows = [], []
    for job in sorted(done.values(), key=lambda j: -spec_from_json(j.meta()["spec"]).schedule.n_rounds):
        spec = spec_from_json(job.meta()["spec"])
        R, dt = spec.schedule.n_rounds, float(spec.schedule.dts[0])
        graph = paper_graph(spec, SWEEP_P, SWEEP_LAM, SWEEP_P_READ)
        inj = program_circuit(spec, p_read=SWEEP_P_READ)
        gates = program_circuit(spec, **H22E, p_read=SWEEP_P_READ)
        gates_dem = str(gates.detector_error_model(decompose_errors=True))
        m = {"R": R, "dt": dt,
             "stim_program_injected_only": sample(inj, *MODEL["program_injected"])[0],
             "stim_program_with_H22E_gates": sample(gates, *MODEL["program_H22E"], gates_dem)[0]}
        if job.has_result:
            _, syn, dat = bits(job)
            rec = record_from_bits(spec, *add_record_flips(syn, dat, SWEEP_P_READ, record_flip_seed(R)))
            f = failures(dem_for(graph), rec.detectors, rec.observables)
            rows.append({"R": R, "dt": dt, "shots": rec.shots, "failures": f, "pL": f / rec.shots,
                         "stim_pL": round(sample(build_circuit(graph), *MODEL["sweep_paper"],
                                                 dem_for(graph))[0], 3),
                         "det_rate": float(rec.detectors.mean())})
            m |= {"h22e_paper_graph": f / rec.shots,
                  "h22e_program_dem_H22E": failures(gates_dem, rec.detectors, rec.observables) / rec.shots}
        model_rows.append(m)
    sweep = {"setup": f"d=5 X, p={SWEEP_P:g}, lam={SWEEP_LAM:g}, T={SWEEP_T:g}; record flips "
                      f"p_read={SWEEP_P_READ:g} added offline (seed 700 + R); H2-2E via aqora q_sq, "
                      f"1000 shots; stim_pL = the paper's model, {MODEL['sweep_paper'][0]} shots",
             "rows": rows}
    decoder = {"model": "hardware program in Stim (one reused ancilla, serial checks), H2-2E p1,p2; "
                        "p_meas,p_init from H2-1E; no idle/leakage; h22e_* = H2-2E shots decoded on "
                        f"the paper graph / on this model's DEM; stim_* = {MODEL['program_H22E'][0]} shots; "
                        "the local-Selene decoding check is recorded in emulator_runs.md",
               "rates": H22E, "rows": model_rows}
    return sweep, decoder


def model_curves() -> dict:
    from qec_timing.hardware.program_model import program_circuit

    curves = {"injected only": [], "injected + H2-2E gate/readout noise": []}
    for R in MODEL_R:
        spec = sweep_spec(R)
        curves["injected only"].append(round(
            sample(program_circuit(spec, p_read=SWEEP_P_READ), *MODEL["curve_injected"])[0], 3))
        curves["injected + H2-2E gate/readout noise"].append(round(
            sample(program_circuit(spec, **H22E, p_read=SWEEP_P_READ), *MODEL["curve_H22E"])[0], 3))
    return {"R": list(MODEL_R), "curves": curves, "shots_per_point": MODEL["curve_injected"][0]}


# --- idle calibration -----------------------------------------------------------

def fit_calibration(readout: Path | None, idle: list[Path]) -> dict:
    """Readout and per-basis idle fits from job directories (`hardware.cli calib-fit`)."""
    out = {"readout": fit_readout(load_shots(readout)) if readout else None, "idle": {}}
    by_basis: dict[str, list] = {}
    for jd in idle:
        meta = json.loads((jd / "program.json").read_text())
        by_basis.setdefault(meta["basis"], []).append(
            (meta["layers"], flips(load_shots(jd), meta["basis"])))
    for basis, pts in by_basis.items():
        pts.sort()
        out["idle"][basis] = fit_idle([L for L, _ in pts], [r for _, r in pts])
    return out


def idle_jobs(js: list[Job], design: str, shots: int | None = None) -> list[Path]:
    """The latest returned H2-1E job per layer count of one spectator design."""
    progs = sorted({j.program for j in js if re.fullmatch(rf"{design}_[XZ]_L\d+", j.program)})
    return [j.path for p in progs if (j := pick(js, p, "H2-1E", shots))]


def anchored_long(js: list[Job]) -> tuple[dict, dict]:
    """Pooled target flips of the 1000-shot (X) / 500-shot (Z) anchored runs, and a constant
    fit across the X waits."""
    pts = {}
    for basis, layers in LONG_IDLE.items():
        for L in layers:
            j = next((j for j in reversed(js) if j.program == f"idleA_{basis}_L{L}"
                      and j.platform == "H2-1E" and j.has_result and (j.shots or 0) >= 500), None)
            if j:
                r = flips(load_shots(j.path), basis)
                pts[f"{basis}_L{L}"] = {"k": r.k, "n": r.n, "p": r.p, "job_dir": j.path.name}
    x = [Rate(v["k"], v["n"]) for k, v in pts.items() if k.startswith("X_")]
    w = np.array([1 / r.se ** 2 for r in x])
    p = np.array([r.p for r in x])
    c = float(w @ p / w.sum())
    fit = {"note": "No consistent growth over L = 0-128; the earlier layer-duration fit is withdrawn.",
           "constant_rate": round(c, 4), "chi2_constant": round(float(w @ (p - c) ** 2), 1),
           "dof": len(x) - 1}
    return pts, fit


def idle_patterns(js: list[Job]) -> dict:
    """Per-shot flip patterns of every returned spectator-idle job (latest per program and
    shot count): {pattern: shots}, pattern = one character per target, '1' = flipped (the
    feed-forward parity undone in basis X). Shows flips that come together within a shot."""
    val = lambda v: int(v[0] if isinstance(v, (list, tuple)) else v)      # noqa: E731
    keys = sorted({(j.program, j.shots) for j in js
                   if re.fullmatch(r"idle[TA]?_[XZ]_L\d+", j.program) and j.platform == "H2-1E"})
    runs = {}
    for program, shots in keys:
        j = pick(js, program, "H2-1E", shots)
        if j is None:
            continue
        design, basis, L = program.split("_")
        counts: dict[str, int] = {}
        for s in load_shots(j.path):
            par = val(s.get("par", 0)) if basis == "X" else 0
            n_t = sum(t.startswith("t") for t in s)
            pat = "".join(str(val(s[f"t{i}"]) ^ par) for i in range(n_t))
            counts[pat] = counts.get(pat, 0) + 1
        runs[f"{program}@{shots}"] = {
            "design": {"idle": "measure-and-reset", "idleT": "transport", "idleA": "anchored"}[design],
            "basis": basis, "layers": int(L[1:]), "shots": shots, "job_dir": j.path.name,
            "patterns": dict(sorted(counts.items()))}
    return {"note": "per-shot target flip patterns, H2-1E; character i = target i, 1 = flipped",
            "runs": runs}


# --- syntax checks --------------------------------------------------------------

def syntax_checks(js: list[Job]) -> dict:
    rows = []
    for j in js:
        if not j.platform.endswith("SC"):
            continue
        rec = j.record or {}
        output = []
        if j.has_result:
            raw = json.loads(sorted(j.path.glob("result_*.txt"))[0].read_text())
            output = [{"registers": len({b[0] for b in raw["bits"]}), "bits": len(raw["bits"]),
                       "shots": len((raw.get("shots") or {}).get("array", []))}]
        job = rec.get("job") or {}
        rows.append({"dir": j.path.name, "program": j.program, "platform": j.platform,
                     "as_entity": rec.get("as_entity"), "job_id": rec.get("job_id"),
                     "status": job.get("status") or ("NOT SUBMITTED" if not j.record else None),
                     "error": job.get("error"), "output": output})
    return {"rows": rows}


# --- all ------------------------------------------------------------------------

def collect(store_hw: Path, out: Path) -> list[Path]:
    _register_builtins()
    js = jobs(store_hw)
    sweep, decoder = dt_sweep_d5(js)
    long_pts, long_fit = anchored_long(js)
    readout = pick(js, "readout", "H2-1E")
    files = {
        "h2_1e_memory_d3.json": memory_d3(js),
        "h2_2e_dt_sweep_d5.json": sweep,
        "h2_2e_dt_sweep_d5_circuit_decoder.json": decoder,
        "h2_2e_dt_sweep_d5_model_curves.json": model_curves(),
        "h2_1e_calibration_runs.fit.json": fit_calibration(readout and readout.path,
                                                           idle_jobs(js, "idle")),
        "h2_1e_transport_idle.fit.json": fit_calibration(None, idle_jobs(js, "idleT")),
        "h2_1e_anchored_idle.fit.json": fit_calibration(None, idle_jobs(js, "idleA", shots=100)),
        "h2_1e_anchored_idle_long.json": long_pts,
        "h2_1e_anchored_idle_long_fit.json": long_fit,
        "h2_1e_idle_flip_patterns.json": idle_patterns(js),
        "syntax_checks.json": syntax_checks(js),
    }
    out.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        (out / name).write_text(json.dumps(data, indent=2 if name.endswith(".fit.json") else 1) + "\n")
    return [out / n for n in files]
