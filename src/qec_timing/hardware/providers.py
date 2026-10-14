"""Quantinuum access through aqora or directly through Nexus. H2 env ONLY.

Every call keeps a record: a job directory under <store>/hardware/ with the
program, its metadata (including the experiment spec), what was asked, and every
raw response verbatim. Nothing is transformed before it is saved. Results are
then turned into a `RawRecord` (`hardware.records`) and stored as an ordinary run,
so they go through the same decoders and analyses as simulations.

Safety: execution that spends credits needs an explicit `confirm=True`. On aqora,
anything but a syntax checker (platform name ending in "SC") is refused unless
`allow_execution=True`, since that would run on an emulator or device.

Verified against the installed sources: aqora 0.36.0 (`QPU`, `QPUJob.from_id`,
results as QSYS JSON), qnexus 0.51.1 (`projects.get_or_create`, `qir.upload`,
`qir.cost`, `start_execute_job`, `jobs.get`, `jobs.wait_for`, `jobs.results`).
aqora's platform listing uses its private `_graphql` client: 0.36.0 has no
public one.
"""

from __future__ import annotations

import datetime as _dt
import json
from pathlib import Path
from typing import Any

from qec_timing.hardware.records import bits_from_shots, record_from_bits
from qec_timing.spec import MemorySpec, spec_from_json
from qec_timing.store import Store


def _register_builtins() -> None:
    import qec_timing.codes.surface  # noqa: F401
    import qec_timing.noise.circuit  # noqa: F401
    import qec_timing.noise.effective  # noqa: F401
    import qec_timing.noise.paper  # noqa: F401


class JobDir:
    """<store>/hardware/<utc stamp>_<provider>_<label>/: everything about one job."""

    def __init__(self, store: Store, provider: str, label: str):
        stamp = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        self.path = store.root / "hardware" / f"{stamp}_{provider}_{label}"
        self.path.mkdir(parents=True)
        self.record: dict[str, Any] = {"provider": provider, "label": label, "created": stamp}

    def save(self, **fields: Any) -> None:
        self.record.update(fields)
        (self.path / "job.json").write_text(json.dumps(self.record, indent=2, default=str))

    def raw(self, name: str, content: str | bytes) -> Path:
        p = self.path / name
        p.write_bytes(content) if isinstance(content, bytes) else p.write_text(content)
        return p


def load_program(path: Path) -> tuple[bytes, dict]:
    """A QIR program written by `hardware.cli build`: <name>.bc and <name>.json."""
    return path.read_bytes(), json.loads(path.with_suffix(".json").read_text())


# --- aqora ---------------------------------------------------------------------

def aqora_platforms() -> list[dict]:
    from aqora import QPU
    qpu = QPU()
    qpu._graphql.ensure_authenticated()
    return [dict(p) for p in qpu._graphql.get_provider_platforms()]


def _is_syntax_checker(name: str) -> bool:
    return name.upper().endswith("SC")


def aqora_run(store: Store, program: Path, platform: str, shots: int, as_entity: str | None = None,
              allow_execution: bool = False, confirm: bool = False, timeout: float = 1800.0) -> Path:
    """Submit a program on aqora and wait. A syntax checker validates and prices it."""
    from aqora import QPU
    from aqora._provider.jobs import platform_matches, qualified_platform_name

    bc, meta = load_program(program)
    qpu = QPU(platform=platform, as_entity=as_entity)
    match = [p for p in aqora_platforms() if platform_matches(platform, p)]
    if not match:
        raise SystemExit(f"platform {platform!r} not visible to this account; list them first")
    name = qualified_platform_name(match[0])
    if not _is_syntax_checker(match[0]["name"]) and not allow_execution:
        raise SystemExit(f"{name} executes programs (not a syntax checker); refusing without "
                         "allow_execution")
    if not _is_syntax_checker(match[0]["name"]) and not confirm:
        raise SystemExit("execution spends credits; pass confirm after reviewing the cost")
    job_dir = JobDir(store, "aqora", f"{program.stem}_{match[0]['name']}")
    job_dir.raw("program.bc", bc)
    job_dir.raw("program.json", json.dumps(meta, indent=2))
    job = qpu.run(bc, shots=shots)
    job_dir.save(platform=name, platform_meta=match[0].get("meta"), shots=shots,
                 as_entity=as_entity, job_id=job.job_id)
    try:
        job.wait(timeout=timeout, poll_interval=10.0)
    except (TimeoutError, RuntimeError) as err:
        job_dir.save(job=dict(job.refresh()), wait_error=str(err))
        return job_dir.path
    results = job.results(raise_on_item_error=False)
    for r in results:
        job_dir.raw(f"result_{r.index}.txt", r.raw or "")
    job_dir.save(job=dict(job.refresh()),
                 results=[{"index": r.index, "format": r.serialization_format,
                           "error": getattr(r, "error", None)} for r in results])
    return job_dir.path


# --- Nexus ---------------------------------------------------------------------

def nexus_cost(store: Store, program: Path, shots: int, project: str,
               system: str = "H2-1") -> Path:
    """Upload and price on the <system>SC syntax checker. Spends nothing."""
    import qnexus as qnx

    bc, meta = load_program(program)
    job_dir = JobDir(store, "nexus", f"{program.stem}_cost")
    job_dir.raw("program.bc", bc)
    job_dir.raw("program.json", json.dumps(meta, indent=2))
    proj = qnx.projects.get_or_create(name=project)
    ref = qnx.qir.upload(qir=bc, name=job_dir.path.name, project=proj)
    hqc = qnx.qir.cost(programs=ref, n_shots=shots, project=proj, system_name=system)
    job_dir.save(project=project, qir_id=str(ref.id), shots=shots, cost_system=f"{system}SC",
                 hqc=hqc)
    return job_dir.path


def nexus_submit(store: Store, program: Path, shots: int, project: str, device: str = "H2-1E",
                 transport_dephasing: bool = True, idle_dephasing: bool | None = None,
                 confirm: bool = False) -> Path:
    """Run on a Nexus device or emulator. Needs confirm=True (spends credits)."""
    import qnexus as qnx
    from qnexus.models import QuantinuumConfig, UserErrorParams

    if not confirm:
        raise SystemExit("execution spends credits; run nexus-cost first, then pass confirm")
    bc, meta = load_program(program)
    job_dir = JobDir(store, "nexus", f"{program.stem}_{device}")
    job_dir.raw("program.bc", bc)
    job_dir.raw("program.json", json.dumps(meta, indent=2))
    proj = qnx.projects.get_or_create(name=project)
    ref = qnx.qir.upload(qir=bc, name=job_dir.path.name, project=proj)
    # A program that injects its own dephasing replaces the emulator's idle
    # dephasing (off by default then); otherwise the emulator's model is the experiment.
    if idle_dephasing is None:
        idle_dephasing = meta["p_inject"] == 0
    params = UserErrorParams(idle_dephasing=idle_dephasing, transport_dephasing=transport_dephasing)
    config = QuantinuumConfig(device_name=device, simulator="stabilizer", noisy_simulation=True,
                              error_params=params)
    job = qnx.start_execute_job(programs=[ref], n_shots=[shots], backend_config=config,
                                name=job_dir.path.name, project=proj)
    job_dir.save(project=project, qir_id=str(ref.id), device=device, shots=shots,
                 job_id=str(job.id), error_params=params.model_dump(exclude_none=True))
    return job_dir.path


def nexus_fetch(job_dir: Path, timeout: float | None = None) -> Path:
    """Wait for a submitted Nexus job and save its result verbatim."""
    import qnexus as qnx

    rec = json.loads((job_dir / "job.json").read_text())
    job = qnx.jobs.get(id=rec["job_id"])
    qnx.jobs.wait_for(job, timeout=timeout) if timeout else qnx.jobs.wait_for(job)
    result = qnx.jobs.results(job)[0].download_result()
    shots = [shot.collate_tags() for shot in result.results]
    (job_dir / "result_qsys.json").write_text(json.dumps(shots))
    rec["fetched"] = _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")
    (job_dir / "job.json").write_text(json.dumps(rec, indent=2, default=str))
    return job_dir / "result_qsys.json"


# --- results -> store ----------------------------------------------------------

def load_shots(job_dir: Path) -> list[dict]:
    """Per-shot tag maps of a finished job: result_qsys.json (Nexus) or the first
    result_*.txt in QSYS format (aqora)."""
    if (job_dir / "result_qsys.json").exists():
        return json.loads((job_dir / "result_qsys.json").read_text())
    from aqora._provider import wire
    from aqora._provider.results import ProviderResult
    raw = sorted(job_dir.glob("result_*.txt"))[0].read_text()
    job = json.loads((job_dir / "job.json").read_text())
    fmt = (job.get("results") or [{}])[0].get("format", wire.RESULT_QSYS_RESULT_JSON_V1)
    if fmt == wire.RESULT_PYTKET_BACKEND_RESULT_JSON_V1:
        return _pytket_tag_maps(ProviderResult(0, fmt, raw).to_backend_result())
    return [s.collate_tags() for s in ProviderResult(
        0, wire.RESULT_QSYS_RESULT_JSON_V1, raw).to_qsys_result().results]


def _pytket_tag_maps(br) -> list[dict]:
    """Per-shot {tag: integer} from a pytket BackendResult: each result() tag is a
    classical register (64 bits for a recorded bool), bit i weighing 2**i."""
    bits = br.get_bitlist()
    shots = br.get_shots(cbits=bits)
    regs: dict[str, list[tuple[int, int]]] = {}
    for col, b in enumerate(bits):
        regs.setdefault(b.reg_name, []).append((col, b.index[0]))
    return [{tag: sum(int(row[c]) << i for c, i in cols) for tag, cols in regs.items()}
            for row in shots]


def store_results(store: Store, job_dir: Path, backend_name: str) -> str:
    """Turn a job's saved shots into a stored run (run id from its spec and backend).

    Reads result_qsys.json (Nexus) or the first result_*.txt in QSYS format (aqora).
    Every raw file of the job is attached to the run untouched."""
    _register_builtins()
    meta = json.loads((job_dir / "program.json").read_text())
    spec: MemorySpec = spec_from_json(meta["meta"]["spec"] if "meta" in meta else meta["spec"])
    shots = load_shots(job_dir)
    from qec_timing.codes.base import checks_of
    syn, dat = bits_from_shots(shots, spec.schedule.n_rounds,
                               len(checks_of(spec.code, spec.basis)), spec.code.n_data)
    attachments = {p.name: p.read_bytes() for p in job_dir.iterdir() if p.is_file()}
    record = record_from_bits(spec, syn, dat,
                              payload=json.loads((job_dir / "job.json").read_text()),
                              attachments=attachments)
    from dataclasses import replace
    spec = replace(spec, shots=record.shots)          # what actually ran
    return store.save_run(spec, backend_name, {"job_dir": job_dir.name}, record)
