"""Create a controlled QIR sleep sweep from the committed d=3 Guppy artifact.

No Guppy recompile or remote submission. Python 3.9+ and clang suffice locally.
LLVM assembly success is NOT validation by Quantinuum's QIR checker or H2.
"""
from __future__ import annotations

import argparse
import copy
import difflib
import hashlib
import json
import math
import platform
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parent
sys.dont_write_bytecode = True
sys.path.insert(0, str(REPO / "src"))
from qec_timing.codes.surface import RotatedSurfaceCode
from qec_timing.codes.base import checks_of

SOURCE = REPO / "results/hardware/programs/d3_X_r2_p0"
SOURCE_SHA256 = "1d76441345a391205fcb9c9898deed404462c26098f58d57a0f0c19385ccd531"
SLEEP = "__quantum__qis__sleep__body"
# Pinned artifact: this is the join after the fourth syndrome measurement's
# conditional path, followed by the final ancilla reset of round zero.
# Insertion here executes once regardless of that syndrome outcome.
BOUNDARY = (
    "cond_exit_1230:                                   ; preds = %cond_exit_1145, %cond_1230_case_1\n"
    "  tail call void @__quantum__qis__reset__body(%Qubit* nonnull inttoptr (i64 9 to %Qubit*))\n"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


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


def call_counts(ir: str) -> dict:
    return dict(sorted((name, len(re.findall(r"\bcall\b[^\n@]*@" + re.escape(name) + r"\(", ir)))
                       for name in set(re.findall(r"\bcall\b[^\n@]*@([\w.]+)\(", ir))))


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


def assemble(clang: str, ll: Path) -> dict:
    bc = ll.with_suffix(".bc")
    # Assemble every variant through the same tool, including no_sleep.
    # No optimization: in particular, retain sleep(0).
    cmd = [clang, "-target", "aarch64-unknown-linux-gnu", "-x", "ir", "-c",
           "-emit-llvm", "-O0", str(ll), "-o", str(bc)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    report = {"command": cmd, "returncode": result.returncode,
              "stdout": result.stdout, "stderr": result.stderr}
    ll.with_suffix(".assembly.json").write_text(json.dumps(report, indent=2) + "\n")
    if result.returncode:
        raise RuntimeError(f"LLVM assembly failed; see {ll.with_suffix('.assembly.json')}")
    # Read the actual submitted bitcode back and check that calls and entrypoint
    # attributes survived assembly. Keep this representation for inspection.
    out = ll.with_suffix(".roundtrip.ll")
    subprocess.run([clang, "-target", "aarch64-unknown-linux-gnu", "-S", "-emit-llvm",
                    "-O0", str(bc), "-o", str(out)], check=True, capture_output=True)
    roundtrip = out.read_text()
    if call_counts(roundtrip) != call_counts(ll.read_text()):
        raise RuntimeError("Assembly changed the quantum/runtime call counts")
    for attr in ('"entry_point"', '"required_num_qubits"="10"',
                 '"required_num_results"="17"', '"qir_profiles"="adaptive_profile"'):
        if attr not in roundtrip:
            raise RuntimeError(f"Assembly lost QIR attribute {attr}")
    return {"llvm_assembly": "passed", "call_counts_preserved": True,
            "quantinuum_qircheck": "not_run", "h2_syntax_check": "not_run",
            "emulator_execution": "not_run"}


def build(config_path: Path, clang: str | None = None) -> Path:
    config = json.loads(config_path.read_text())
    if (config["distance"], config["basis"], config["rounds"]) != (3, "X", 2):
        raise ValueError("This first probe supports only the pinned d3 X two-round program")
    variants = variants_from_config(config)
    code = RotatedSurfaceCode(3)
    source = SOURCE.with_suffix(".ll").read_text()
    meta = json.loads(SOURCE.with_suffix(".json").read_text())
    if meta["p_inject"] != 0 or meta["n_qubits"] != code.n_data + 1:
        raise ValueError("Unexpected baseline metadata")
    texts = {name: transform(source, value, config["data_qubit"])
             for name, value in variants.items()}
    identity = json.dumps(config, sort_keys=True).encode() + Path(__file__).read_bytes()
    out = ROOT / "programs" / digest(identity)[:16]
    out.mkdir(parents=True, exist_ok=False)
    originals = out / "original"
    originals.mkdir()
    for suffix in (".ll", ".bc", ".json"):
        shutil.copyfile(SOURCE.with_suffix(suffix), originals / ("guppy_baseline" + suffix))
    shutil.copyfile(config_path, out / "config.json")
    tool = {"python": sys.version, "platform": platform.platform(), "clang": None}
    if clang:
        tool["clang"] = subprocess.check_output([clang, "--version"], text=True).strip()
    (out / "toolchain.json").write_text(json.dumps(tool, indent=2) + "\n")
    jobs = []
    for name, value in variants.items():
        ll = out / (name + ".ll")
        ll.write_text(texts[name])
        ll.with_suffix(".diff").write_text("".join(difflib.unified_diff(
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
                    "baseline_source": str(SOURCE.relative_to(REPO)),
                    "baseline_ll_sha256": SOURCE_SHA256,
                    "baseline_compiler_versions": meta["versions"],
                    "builder_sha256": digest(Path(__file__).read_bytes()),
                    "ll_sha256": digest(ll.read_bytes()),
                    "bc_sha256": digest(ll.with_suffix('.bc').read_bytes()) if clang else None,
                    "schedule_note": "Inherited schedule is a placeholder, not measured time; sleep units unknown."}
        ll.with_suffix(".json").write_text(json.dumps(metadata, indent=2) + "\n")
        jobs.append({"variant": name, "program": str(ll.with_suffix('.bc').relative_to(REPO)),
                     "platform": config["syntax_platform"], "shots": 1,
                     "status": "not_submitted"})
    (out / "syntax_plan.json").write_text(json.dumps(jobs, indent=2) + "\n")
    return out


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "configs/sleep_probe.json")
    parser.add_argument("--clang", help="LLVM assembler; omit to write textual QIR only")
    args = parser.parse_args()
    print(build(args.config, args.clang))
