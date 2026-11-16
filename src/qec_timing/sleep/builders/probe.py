"""Create a controlled QIR sleep sweep from the committed d=3 Guppy artifact.

No Guppy recompile or remote submission. Python 3.9+ and clang suffice locally.
LLVM assembly success is NOT validation by Quantinuum's QIR checker or H2.

Ported from SG_final_round/src/build_sleep_probe.py. The original file is kept byte for byte
at results/sleep/submission_scripts/build_sleep_probe.py: probe folder names hash the
folder's config plus that file's bytes, so this module hashes the archived copy (asserting
its sha256) rather than its own source. `5944c048c1dfdc80` and `8cca8353b3f06d18` reproduce
by name; `98ff453353750ae5` came from an older builder (`ecaf8610...`) and an older
single-duration config format, so only its `.ll` text is reproducible (`from_folder`).
"""
from __future__ import annotations

import copy
import difflib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path

from qec_timing.codes.base import checks_of
from qec_timing.codes.surface import RotatedSurfaceCode

from .. import paths
from ..qir import BASELINE_D3_SHA256 as SOURCE_SHA256, BOUNDARY, SLEEP, assemble, call_counts, digest
from . import Build

SOURCE = paths.BASELINE_D3
BUILDER = paths.PROBE_BUILDER
BUILDER_SHA256 = '8f1775a21bcc2268b13911afc1bfe3666de7cb8e2b566ee2d99a9ed421fea419'
FOLDERS = ['98ff453353750ae5', '5944c048c1dfdc80', '8cca8353b3f06d18']
LEGACY = {'98ff453353750ae5': 'older builder ecaf8610... and single-duration config; .ll text only'}


def builder_bytes() -> bytes:
    data = BUILDER.read_bytes()
    if digest(data) != BUILDER_SHA256:
        raise RuntimeError(f'{BUILDER} changed (sha256 {digest(data)}); probe folder names hash its bytes')
    return data


def transform(source: str, duration: float | None, qubit: int = 4) -> str:
    if digest(source.encode()) != SOURCE_SHA256:
        raise ValueError("Baseline changed: re-inspect its round boundary before patching")
    if not isinstance(qubit, int) or not 0 <= qubit < 9:
        raise ValueError("sleep target must be a data qubit 0..8")
    if source.count(BOUNDARY) != 1:
        raise ValueError("Expected exactly one verified round boundary")
    if duration is None:
        return source
    if not math.isfinite(duration) or duration < 0:
        raise ValueError("sleep duration must be finite and nonnegative")
    operand = "null" if qubit == 0 else f"inttoptr (i64 {qubit} to %Qubit*)"
    call = f"  call void @{SLEEP}(%Qubit* {operand}, double {duration:.17e})\n"
    result = source.replace(BOUNDARY, BOUNDARY + call, 1)
    declaration = f"declare void @{SLEEP}(%Qubit*, double)\n\n"
    return result.replace("declare i64 @___get_current_shot()", declaration +
                          "declare i64 @___get_current_shot()", 1)


def variants_from_config(config: dict) -> dict:
    values = config["finite_durations_raw"]
    if not isinstance(values, list) or not values:
        raise ValueError("finite_durations_raw must be a nonempty list")
    durations = [float(value) for value in values]
    if any(not math.isfinite(value) or value <= 0 for value in durations):
        raise ValueError("finite_durations_raw must contain positive finite values")
    if len(set(durations)) != len(durations):
        raise ValueError("duplicate sleep durations")
    variants = {"no_sleep": None, "sleep_zero": 0.0}
    for duration in durations:
        label = str(duration).replace(".", "p").replace("-", "m").replace("+", "p")
        variants["sleep_" + label] = duration
    return variants


def name_for(config: dict) -> str:
    """Folder name: sha256(json.dumps(config, sort_keys=True) + original builder bytes)[:16]."""
    return digest(json.dumps(config, sort_keys=True).encode() + builder_bytes())[:16]


def probe(config: dict) -> Build:
    if (config["distance"], config["basis"], config["rounds"]) != (3, "X", 2):
        raise ValueError("This first probe supports only the pinned d3 X two-round program")
    variants = variants_from_config(config)
    source = paths.read_text(SOURCE.with_suffix(".ll"))
    texts = {name: transform(source, value, config["data_qubit"]) for name, value in variants.items()}
    return Build(name_for(config), texts, config=config, extra={'variants': variants})


def from_folder(folder: str) -> Build:
    """The Build for a committed probe folder, from its own config.json.

    For the legacy folder (oldest config format: one finite duration, variant `sleep_finite`)
    the name is the committed one and `hashed` is False: it cannot be recomputed.
    """
    config = json.loads(paths.read_text(paths.PROGRAMS / folder / 'config.json'))
    if 'finite_durations_raw' in config:
        return probe(config)
    variants = {'no_sleep': None, 'sleep_zero': 0.0, 'sleep_finite': float(config['finite_duration_raw'])}
    source = paths.read_text(SOURCE.with_suffix('.ll'))
    texts = {name: transform(source, value, config['data_qubit']) for name, value in variants.items()}
    return Build(folder, texts, config=config, hashed=False, extra={'variants': variants, 'legacy': LEGACY[folder]})


def materialize(config_path: Path = paths.CONFIG / 'sleep_probe.json', clang: str | None = None) -> Path:
    """Write a new probe folder (the original `build`). Refuses if the folder exists."""
    config_bytes = Path(config_path).read_bytes()
    config = json.loads(config_bytes)
    build = probe(config)
    variants, texts = build.extra['variants'], build.texts
    code = RotatedSurfaceCode(3)
    source = paths.read_text(SOURCE.with_suffix(".ll"))
    meta = json.loads(paths.read_text(SOURCE.with_suffix(".json")))
    if meta["p_inject"] != 0 or meta["n_qubits"] != code.n_data + 1:
        raise ValueError("Unexpected baseline metadata")
    out = build.folder
    out.mkdir(parents=True, exist_ok=False)
    originals = out / "original"
    for suffix in (".ll", ".bc", ".json"):
        paths.write_bytes(originals / ("guppy_baseline" + suffix), SOURCE.with_suffix(suffix).read_bytes())
    paths.write_bytes(out / "config.json", config_bytes)
    tool = {"python": sys.version, "platform": platform.platform(), "clang": None}
    if clang:
        tool["clang"] = subprocess.check_output([clang, "--version"], text=True).strip()
    paths.write_text(out / "toolchain.json", json.dumps(tool, indent=2) + "\n")
    jobs = []
    for name, value in variants.items():
        ll = out / (name + ".ll")
        paths.write_text(ll, texts[name])
        paths.write_text(ll.with_suffix(".diff"), "".join(difflib.unified_diff(
            source.splitlines(True), texts[name].splitlines(True),
            fromfile="original/guppy_baseline.ll", tofile=ll.name)))
        status = assemble(clang, ll) if clang else {"llvm_assembly": "not_run"}
        sleep = {"enabled": value is not None, "duration_raw": value,
                 "duration_unit": config["duration_unit"], "physical_duration_seconds": None,
                 "target_data_qubit": config["data_qubit"], "after_round_index": 0,
                 "scheduling_semantics": "unverified"}
        spec = copy.deepcopy(meta["spec"])
        spec["extra"]["explicit_sleep_probe"] = sleep
        metadata = {"spec": spec, "n_qubits": code.n_data + 1,
                    "n_checks": len(checks_of(code, "X")), "p_inject": 0.0,
                    "p_inject_effective": 0.0, "offline_readout_flips": False,
                    "sleep": sleep, "validation": status, "qir_calls": call_counts(texts[name]),
                    "baseline_source": SOURCE.relative_to(paths.REPO).as_posix(),
                    "baseline_ll_sha256": SOURCE_SHA256,
                    "baseline_compiler_versions": meta["versions"],
                    "builder_sha256": digest(builder_bytes()),
                    "ll_sha256": digest(ll.read_bytes()),
                    "bc_sha256": digest(ll.with_suffix('.bc').read_bytes()) if clang else None,
                    "schedule_note": "Inherited schedule is a placeholder, not measured time; sleep units unknown."}
        paths.write_text(ll.with_suffix(".json"), json.dumps(metadata, indent=2) + "\n")
        jobs.append({"variant": name, "program": ll.with_suffix('.bc').relative_to(paths.REPO).as_posix(),
                     "platform": config["syntax_platform"], "shots": 1,
                     "status": "not_submitted"})
    paths.write_text(out / "syntax_plan.json", json.dumps(jobs, indent=2) + "\n")
    return out
