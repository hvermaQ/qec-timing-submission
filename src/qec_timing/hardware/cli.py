"""Hardware command line. H2 env ONLY (envs/h2.txt). Log in once first:
`.venv-h2/bin/aqora login` (aqora) or `.venv-h2/bin/qnx login` (Nexus).

    build         write a memory experiment as validated QIR (+ .json with its spec)
    local         run that program on local Selene: contract checks, no account needed
    aqora-list    platforms visible to the logged-in aqora account (read-only)
    aqora-check   submit to a syntax checker (validates and prices; executes nothing)
    aqora-submit  run on an aqora-hosted emulator/device: needs --confirm (spends team credits)
    nexus-cost    upload to Nexus and price on <system>SC (executes nothing)
    nexus-submit  run on a Nexus device/emulator: needs --confirm (spends credits)
    nexus-fetch   wait for a submitted job and save the result
    store         turn a job's saved result into a stored run
    scaling       QIR size, call count and build time against distance and rounds
    calib-build   readout and spectator-idle calibration programs (QIR), one per layer count
    calib-fit     fit returned calibration jobs and write a Calibration file

Examples (repo root):
    .venv-h2/bin/python -m qec_timing.hardware.cli build --d 3 --basis X --rounds 2 --p-inject 0.05
    .venv-h2/bin/python -m qec_timing.hardware.cli local results/hardware/programs/d3_X_r2_p0.05.bc
    .venv-h2/bin/python -m qec_timing.hardware.cli aqora-list
    .venv-h2/bin/python -m qec_timing.hardware.cli aqora-check results/hardware/programs/d3_X_r2_p0.05.bc --platform nexus:H2-1SC
    .venv-h2/bin/python -m qec_timing.hardware.cli nexus-cost results/hardware/programs/d3_X_r2_p0.05.bc --shots 100
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from qec_timing.store import Store

PROGRAMS = Path("results/hardware/programs")


def cmd_build(a) -> None:
    from qec_timing.codes.surface import RotatedSurfaceCode
    from qec_timing.hardware.qir import build_qir
    from qec_timing.noise.circuit import CircuitNoise
    from qec_timing.noise.paper import PaperNoise
    from qec_timing.schedule import Schedule
    from qec_timing.spec import MemorySpec

    pauli = "Z" if a.basis == "X" else "X"
    # Injected flips only (readout and gates are the device's); no injection = device noise.
    # Data flips only: record flips (b_read) are classical and are added to the shots offline.
    noise = (PaperNoise(a.p_inject, a.lam, b_read=0.0, pauli=pauli) if a.p_inject
             else CircuitNoise(0, 0, 0))
    dt = 1.0 if a.total_time is None else a.total_time / a.rounds
    spec = MemorySpec(RotatedSurfaceCode(a.d), a.basis, Schedule.rounds(dt, a.rounds), noise,
                      a.shots, a.seed)
    q = build_qir(spec)
    a.out.mkdir(parents=True, exist_ok=True)
    name = f"d{a.d}_{a.basis}_r{a.rounds}_p{a.p_inject:g}"
    if a.lam or a.total_time is not None:
        name += f"_lam{a.lam:g}_dt{dt:.4g}"
    (a.out / f"{name}.bc").write_bytes(q["bitcode"])
    (a.out / f"{name}.ll").write_text(q["ll"])
    (a.out / f"{name}.json").write_text(json.dumps(q["meta"], indent=2))
    m = q["meta"]
    print(f"{a.out / name}.bc: {m['n_qubits']} qubits, {m['qir_bitcode_bytes']} B, "
          f"{sum(m['qir_calls'].values())} QIR calls, p_inject {m['p_inject_effective']:.7f}")


def cmd_local(a) -> None:
    import dataclasses

    from qec_timing.hardware.providers import _register_builtins, load_program
    from qec_timing.hardware.selene_local import SeleneQirProgramBackend
    from qec_timing.spec import spec_from_json
    from qec_timing.testing import contracts as C

    _register_builtins()
    spec = spec_from_json(load_program(a.program)[1]["spec"])
    quiet = dataclasses.replace(spec, noise=dataclasses.replace(spec.noise, p=0.0)
                                if hasattr(spec.noise, "p") else spec.noise, shots=30)
    noisy = dataclasses.replace(spec, shots=a.shots)
    C.check_backend(SeleneQirProgramBackend(), quiet, noisy)
    print(f"{a.program.name}: backend contract passed on local Selene ({a.shots} shots)")


def cmd_aqora_list(a) -> None:
    from qec_timing.hardware.providers import aqora_platforms

    rows = aqora_platforms()
    print(f"{len(rows)} platforms")
    for p in rows:
        m = p.get("meta") or {}
        sc = "  [syntax checker]" if p["name"].upper().endswith("SC") else ""
        print(f"{p['provider']}:{p['name']}  maxQubits={m.get('maxQubits')} maxShots={m.get('maxShots')} "
              f"inputFormats={m.get('inputFormats')}{sc}")


def cmd_aqora_check(a) -> None:
    from qec_timing.hardware.providers import aqora_run

    d = aqora_run(Store(a.store), a.program, a.platform, a.shots, a.as_entity)
    print(f"saved {d}")


def cmd_aqora_submit(a) -> None:
    from qec_timing.hardware.providers import aqora_run

    d = aqora_run(Store(a.store), a.program, a.platform, a.shots, a.as_entity,
                  allow_execution=True, confirm=a.confirm, timeout=a.timeout)
    print(f"saved {d}")


def cmd_nexus_cost(a) -> None:
    from qec_timing.hardware.providers import nexus_cost

    d = nexus_cost(Store(a.store), a.program, a.shots, a.project, a.system)
    print(f"HQC: {json.loads((d / 'job.json').read_text())['hqc']}   saved {d}")


def cmd_nexus_submit(a) -> None:
    from qec_timing.hardware.providers import nexus_submit

    if a.shots > a.max_shots:
        raise SystemExit(f"--shots {a.shots} > --max-shots {a.max_shots}")
    d = nexus_submit(Store(a.store), a.program, a.shots, a.project, a.device,
                     transport_dephasing=not a.transport_dephasing_off, confirm=a.confirm)
    print(f"submitted; saved {d}")


def cmd_nexus_fetch(a) -> None:
    from qec_timing.hardware.providers import nexus_fetch

    print(f"saved {nexus_fetch(a.job_dir)}")


def cmd_store(a) -> None:
    from qec_timing.hardware.providers import store_results

    print(f"stored run {store_results(Store(a.store), a.job_dir, a.backend)}")


def cmd_scaling(a) -> None:
    from qec_timing.codes.surface import RotatedSurfaceCode
    from qec_timing.hardware.qir import build_qir
    from qec_timing.noise.paper import PaperNoise
    from qec_timing.schedule import Schedule
    from qec_timing.spec import MemorySpec

    rows = []
    for d, rounds in [(3, 2), (3, 8), (3, 32), (5, 2), (5, 8), (5, 32), (7, 2), (7, 8), (7, 16)]:
        spec = MemorySpec(RotatedSurfaceCode(d), "X", Schedule.rounds(1.0, rounds),
                          PaperNoise(0.05, 0.0, b_read=0.0, pauli="Z"), 100, 7_000_000)
        m = build_qir(spec)["meta"]
        row = {"d": d, "rounds": rounds, "qubits": m["n_qubits"], "bitcode_bytes": m["qir_bitcode_bytes"],
               "qir_calls": sum(m["qir_calls"].values()), "rzz": m["qir_calls"].get("__quantum__qis__rzz__body", 0),
               "seconds": m["seconds_hugr"] + m["seconds_qir"]}
        rows.append(row)
        print(row, flush=True)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps({"versions": m["versions"], "rows": rows}, indent=1))
    print(f"wrote {a.out}")


def cmd_calib_build(a) -> None:
    import importlib.metadata as md

    from hugr_qir.output import OutputFormat

    from qec_timing.hardware.calibration_experiments import (idle_program, readout_program,
                                                             transport_idle_program)
    from qec_timing.hardware.qir import _convert

    a.out.mkdir(parents=True, exist_ok=True)
    jobs = [] if a.transport else [("readout", readout_program(a.readout_qubits),
                                    {"experiment": "readout", "n": a.readout_qubits})]
    for basis in a.bases:
        for L in a.layers:
            if a.transport:
                jobs.append((f"idleT_{basis}_L{L}",
                             transport_idle_program(a.targets, a.spectators, L, basis),
                             {"experiment": "idle", "spectator_layer": "random-pairing zz_max",
                              "basis": basis, "layers": L, "n_targets": a.targets,
                              "n_spectators": a.spectators}))
            else:
                jobs.append((f"idle_{basis}_L{L}", idle_program(a.targets, a.spectators, L, basis),
                             {"experiment": "idle", "spectator_layer": "measure-reset",
                              "basis": basis, "layers": L, "n_targets": a.targets,
                              "n_spectators": a.spectators}))
    versions = {k: md.version(k) for k in ("guppylang", "hugr-qir")}
    for name, prog, meta in jobs:
        bc = _convert(prog.compile(), OutputFormat.BITCODE)
        (a.out / f"{name}.bc").write_bytes(bc)
        # p_inject 0: no injected noise, the device's own idling is the experiment.
        (a.out / f"{name}.json").write_text(json.dumps({**meta, "p_inject": 0.0,
                                                         "versions": versions}, indent=2))
        print(f"{a.out / name}.bc  {len(bc)} B")


def cmd_calib_fit(a) -> None:
    import dataclasses

    from qec_timing.hardware import Calibration
    from qec_timing.hardware.calibration_experiments import (fit_idle, fit_readout, flips,
                                                             to_calibration_fields)
    from qec_timing.hardware.providers import load_shots

    out = {"readout": None, "idle": {}}
    if a.readout:
        out["readout"] = fit_readout(load_shots(a.readout))
    by_basis: dict[str, list] = {}
    for jd in a.idle:
        meta = json.loads((jd / "program.json").read_text())
        by_basis.setdefault(meta["basis"], []).append(
            (meta["layers"], flips(load_shots(jd), meta["basis"])))
    for basis, pts in by_basis.items():
        pts.sort()
        out["idle"][basis] = fit_idle([L for L, _ in pts], [r for _, r in pts])
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.with_suffix(".fit.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2))
    if "X" not in out["idle"] or a.layer_seconds is None:
        print("no Calibration written: needs an X-basis idle fit and --layer-seconds")
        return
    base = Calibration.load(a.base)
    fields = to_calibration_fields(out["idle"]["X"], a.layer_seconds)
    if out["readout"]:
        fields.update(p_meas0=out["readout"]["p_meas0"], p_meas1=out["readout"]["p_meas1"])
    sources = ", ".join(p.name for p in ([a.readout] if a.readout else []) + list(a.idle))
    cal = dataclasses.replace(base, **fields, source=(
        f"measured: readout and idle ({sources}; layer {a.layer_seconds} s); "
        f"gates and p_init from: {base.source}"))
    cal.save(a.out)
    print(f"wrote {a.out}")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", type=Path, default=Path("store"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("--d", type=int, default=3)
    b.add_argument("--basis", choices=("X", "Z"), default="X")
    b.add_argument("--rounds", type=int, default=2)
    b.add_argument("--p-inject", type=float, default=0.0, help="the paper's p (p_stab)")
    b.add_argument("--lam", type=float, default=0.0, help="the paper's lambda: idle flips grow with dt")
    b.add_argument("--total-time", type=float, default=None,
                   help="fixed T: dt = T / rounds (default dt = 1)")
    b.add_argument("--shots", type=int, default=100)
    b.add_argument("--seed", type=int, default=7_000_000)
    b.add_argument("--out", type=Path, default=PROGRAMS)
    b.set_defaults(fn=cmd_build)

    lo = sub.add_parser("local")
    lo.add_argument("program", type=Path)
    lo.add_argument("--shots", type=int, default=3000)
    lo.set_defaults(fn=cmd_local)

    sub.add_parser("aqora-list").set_defaults(fn=cmd_aqora_list)

    c = sub.add_parser("aqora-check")
    c.add_argument("program", type=Path)
    c.add_argument("--platform", required=True, help="as listed, e.g. nexus:H2-1SC")
    c.add_argument("--shots", type=int, default=100)
    c.add_argument("--as-entity", default=None)
    c.set_defaults(fn=cmd_aqora_check)

    asub = sub.add_parser("aqora-submit")
    asub.add_argument("program", type=Path)
    asub.add_argument("--platform", required=True, help="as listed, e.g. nexus:H2-1E")
    asub.add_argument("--shots", type=int, default=100)
    asub.add_argument("--as-entity", default=None)
    asub.add_argument("--timeout", type=float, default=3600.0, help="seconds to wait for the job")
    asub.add_argument("--confirm", action="store_true", help="required: execution spends credits")
    asub.set_defaults(fn=cmd_aqora_submit)

    nc = sub.add_parser("nexus-cost")
    nc.add_argument("program", type=Path)
    nc.add_argument("--shots", type=int, default=100)
    nc.add_argument("--project", default="qec-timing")
    nc.add_argument("--system", default="H2-1")
    nc.set_defaults(fn=cmd_nexus_cost)

    ns = sub.add_parser("nexus-submit")
    ns.add_argument("program", type=Path)
    ns.add_argument("--shots", type=int, default=100)
    ns.add_argument("--max-shots", type=int, default=1000)
    ns.add_argument("--project", default="qec-timing")
    ns.add_argument("--device", default="H2-1E")
    ns.add_argument("--transport-dephasing-off", action="store_true")
    ns.add_argument("--confirm", action="store_true", help="I have seen the cost; spend credits")
    ns.set_defaults(fn=cmd_nexus_submit)

    nf = sub.add_parser("nexus-fetch")
    nf.add_argument("job_dir", type=Path)
    nf.set_defaults(fn=cmd_nexus_fetch)

    st = sub.add_parser("store")
    st.add_argument("job_dir", type=Path)
    st.add_argument("--backend", required=True, help="name for the run, e.g. nexus:H2-1E")
    st.set_defaults(fn=cmd_store)

    sc = sub.add_parser("scaling")
    sc.add_argument("--out", type=Path, default=Path("results/hardware/qir_scaling.json"))
    sc.set_defaults(fn=cmd_scaling)

    cb = sub.add_parser("calib-build")
    cb.add_argument("--layers", type=int, nargs="+", default=[0, 2, 4, 8, 16, 32, 64])
    cb.add_argument("--bases", nargs="+", default=["X", "Z"], choices=["X", "Z"])
    cb.add_argument("--targets", type=int, default=8)
    cb.add_argument("--spectators", type=int, default=2)
    cb.add_argument("--readout-qubits", type=int, default=8)
    cb.add_argument("--out", type=Path, default=Path("results/hardware/calibration_programs"))
    cb.add_argument("--transport", action="store_true",
                    help="spectators do random-pairing zz_max layers (forces transport)")
    cb.set_defaults(fn=cmd_calib_build)

    cf = sub.add_parser("calib-fit")
    cf.add_argument("--readout", type=Path, default=None, help="job dir of the readout program")
    cf.add_argument("--idle", type=Path, nargs="*", default=[], help="job dirs of idle programs")
    cf.add_argument("--layer-seconds", type=float, default=None,
                    help="duration of one spectator layer; without it only per-layer fits are written")
    cf.add_argument("--base", type=Path, default=Path("config/h2_1e_emulator.json"),
                    help="gate and init errors are taken from here (not measured by these programs)")
    cf.add_argument("--out", type=Path, default=Path("config/h2_measured.json"))
    cf.set_defaults(fn=cmd_calib_fit)

    a = ap.parse_args(argv)
    a.fn(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
