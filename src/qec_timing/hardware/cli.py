"""Hardware command line. H2 env ONLY (envs/h2.txt). Log in once first:
`.venv-h2/bin/aqora login` (aqora) or `.venv-h2/bin/qnx login` (Nexus).

    build         write a memory experiment as validated QIR (+ .json with its spec)
    local         run that program on local Selene: contract checks, no account needed
    aqora-list    platforms visible to the logged-in aqora account (read-only)
    aqora-check   submit to a syntax checker (validates and prices; executes nothing)
    nexus-cost    upload to Nexus and price on <system>SC (executes nothing)
    nexus-submit  run on a Nexus device/emulator: needs --confirm (spends credits)
    nexus-fetch   wait for a submitted job and save the result
    store         turn a job's saved result into a stored run

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
    noise = PaperNoise(a.p_inject, 0.0, b_read=0.0, pauli=pauli) if a.p_inject else CircuitNoise(0, 0, 0)
    spec = MemorySpec(RotatedSurfaceCode(a.d), a.basis, Schedule.rounds(1.0, a.rounds), noise,
                      a.shots, a.seed)
    q = build_qir(spec)
    a.out.mkdir(parents=True, exist_ok=True)
    name = f"d{a.d}_{a.basis}_r{a.rounds}_p{a.p_inject:g}"
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


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", type=Path, default=Path("store"))
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build")
    b.add_argument("--d", type=int, default=3)
    b.add_argument("--basis", choices=("X", "Z"), default="X")
    b.add_argument("--rounds", type=int, default=2)
    b.add_argument("--p-inject", type=float, default=0.0)
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

    a = ap.parse_args(argv)
    a.fn(a)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
