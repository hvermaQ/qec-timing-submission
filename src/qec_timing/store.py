"""On-disk store for runs, fitted models and derived results.

    <root>/runs/<run_id>/manifest.json         spec, backend, versions, commit, time
    <root>/runs/<run_id>/raw/detectors.npy     packed uint64 detection events
    <root>/runs/<run_id>/raw/observables.npy   raw logical readout (shots, 1)
    <root>/runs/<run_id>/raw/rounds.npz        dt, t, p_data, p_read per round
    <root>/runs/<run_id>/raw/payload.json      backend output, verbatim
    <root>/runs/<run_id>/raw/attachments/      backend files, untouched
    <root>/runs/<run_id>/model/<name>.json     fitted EffectiveModel (+ <name>.dem)
    <root>/derived/<derived_id>/derived.json   a Derived result and its parents

Raw data is written once and never rewritten: saving a run id that exists raises.
Every manifest records the code commit, so `check_lineage` can flag results built
on runs made by different code.
"""

from __future__ import annotations

import datetime as _dt
import hashlib
import json
import os
import platform
import shutil
import subprocess
from dataclasses import asdict
from pathlib import Path
from typing import Any

import numpy as np

from qec_timing.records import (DetectorLayout, Derived, EffectiveModel, Estimate, RawRecord,
                                pack_bits, unpack_bits)
from qec_timing.spec import MemorySpec

STORE_VERSION = 1


def code_commit() -> dict[str, Any]:
    """The git commit of this package's source, and whether the tree was dirty."""
    src = Path(__file__).resolve().parent
    try:
        rev = subprocess.run(["git", "rev-parse", "HEAD"], cwd=src, capture_output=True,
                             text=True, check=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "--", "."], cwd=src,
                                    capture_output=True, text=True, check=True).stdout.strip())
    except (OSError, subprocess.CalledProcessError):
        return {"commit": None, "dirty": None}
    return {"commit": rev, "dirty": dirty}


class Store:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    # --- raw runs ------------------------------------------------------------

    def run_dir(self, run_id: str) -> Path:
        return self.root / "runs" / run_id

    def has_run(self, run_id: str) -> bool:
        return (self.run_dir(run_id) / "manifest.json").exists()

    def save_run(self, spec: MemorySpec, backend: str, versions: dict[str, str],
                 record: RawRecord) -> str:
        """Write a run once. It is assembled in a temporary directory and renamed into
        place in one step, so an interrupted write (a killed process) never looks
        like a run; its leftovers are removed on the next attempt."""
        run_id = spec.run_id(backend)
        d = self.run_dir(run_id)
        if self.has_run(run_id):
            raise FileExistsError(f"run {run_id} already stored; raw data is never rewritten")
        if d.exists():                                  # no manifest: an interrupted write
            shutil.rmtree(d)
        tmp = d.parent / f".tmp-{run_id}-{os.getpid()}"
        if tmp.exists():
            shutil.rmtree(tmp)
        raw = tmp / "raw"
        (raw / "attachments").mkdir(parents=True)
        np.save(raw / "detectors.npy", pack_bits(record.detectors))
        np.save(raw / "observables.npy", record.observables)
        np.savez(raw / "rounds.npz", **record.rounds)
        _write_json(raw / "payload.json", record.payload)
        for name, blob in record.attachments.items():
            (raw / "attachments" / name).write_bytes(blob)
        manifest = {
            "store_version": STORE_VERSION,
            "run_id": run_id,
            "created": _now(),
            "backend": backend,
            "spec": spec.to_json(),
            "layout": asdict(record.layout),
            "shots": record.shots,
            "versions": {"python": platform.python_version(), "numpy": np.__version__,
                         **versions},
            "code": code_commit(),
            "checksums": {p.name: _sha256(p) for p in sorted(raw.glob("*")) if p.is_file()},
        }
        _write_json(tmp / "manifest.json", manifest)
        try:
            os.rename(tmp, d)                           # atomic on one filesystem
        except OSError:
            shutil.rmtree(tmp)                          # another process stored it first
            if not self.has_run(run_id):
                raise
        return run_id

    def manifest(self, run_id: str) -> dict[str, Any]:
        return json.loads((self.run_dir(run_id) / "manifest.json").read_text())

    def load_run(self, run_id: str) -> tuple[dict[str, Any], RawRecord]:
        """Manifest and record. The spec stays as JSON: rebuilding code and noise
        objects needs their registries, which the caller has."""
        m = self.manifest(run_id)
        raw = self.run_dir(run_id) / "raw"
        for name, digest in m["checksums"].items():
            if _sha256(raw / name) != digest:
                raise IOError(f"run {run_id}: {name} does not match its checksum")
        layout = DetectorLayout(**m["layout"])
        record = RawRecord(
            layout=layout,
            detectors=unpack_bits(np.load(raw / "detectors.npy"), layout.n_detectors),
            observables=np.load(raw / "observables.npy"),
            rounds=dict(np.load(raw / "rounds.npz")),
            payload=json.loads((raw / "payload.json").read_text()),
            attachments={p.name: p.read_bytes() for p in (raw / "attachments").iterdir()},
        )
        return m, record

    def runs(self) -> list[str]:
        base = self.root / "runs"
        return sorted(p.name for p in base.iterdir()
                      if not p.name.startswith(".") and (p / "manifest.json").exists()) \
            if base.exists() else []

    # --- fitted models -------------------------------------------------------

    def save_model(self, run_id: str, model: EffectiveModel) -> Path:
        if not self.has_run(run_id):
            raise KeyError(f"no run {run_id}")
        d = self.run_dir(run_id) / "model"
        d.mkdir(exist_ok=True)
        out = {"name": model.name, "parents": list(model.parents), "created": _now(),
               "code": code_commit(), "info": model.info,
               "params": {k: asdict(v) for k, v in model.params.items()}}
        _write_json(d / f"{model.name}.json", out)
        if model.dem is not None:
            (d / f"{model.name}.dem").write_text(model.dem)
        return d / f"{model.name}.json"

    def load_model(self, run_id: str, name: str) -> EffectiveModel:
        d = self.run_dir(run_id) / "model"
        j = json.loads((d / f"{name}.json").read_text())
        dem = d / f"{name}.dem"
        return EffectiveModel(name=j["name"], parents=tuple(j["parents"]), info=j["info"],
                              params={k: Estimate(**v) for k, v in j["params"].items()},
                              dem=dem.read_text() if dem.exists() else None)

    # --- derived results -----------------------------------------------------

    def save_derived(self, derived: Derived) -> str:
        missing = [p for p in derived.parents if not self.has_run(p)
                   and not (self.root / "derived" / p).exists()]
        if missing:
            raise KeyError(f"parents not in store: {missing}")
        blob = json.dumps({"name": derived.name, "data": derived.data,
                           "parents": sorted(derived.parents)}, sort_keys=True)
        derived_id = hashlib.sha256(blob.encode()).hexdigest()[:16]
        d = self.root / "derived" / derived_id
        d.mkdir(parents=True, exist_ok=True)
        _write_json(d / "derived.json", {"derived_id": derived_id, "name": derived.name,
                                         "parents": list(derived.parents), "created": _now(),
                                         "code": code_commit(), "data": derived.data})
        return derived_id

    def load_derived(self, derived_id: str) -> Derived:
        j = json.loads((self.root / "derived" / derived_id / "derived.json").read_text())
        return Derived(name=j["name"], data=j["data"], parents=tuple(j["parents"]))

    # --- checks --------------------------------------------------------------

    def check_lineage(self, derived_id: str) -> list[str]:
        """Problems with a derived result's inputs: missing parents, parents made
        by a different code commit than the result, or by a dirty tree."""
        j = json.loads((self.root / "derived" / derived_id / "derived.json").read_text())
        issues, own = [], j["code"]["commit"]
        for p in j["parents"]:
            if self.has_run(p):
                code = self.manifest(p)["code"]
            elif (self.root / "derived" / p / "derived.json").exists():
                code = json.loads((self.root / "derived" / p / "derived.json").read_text())["code"]
            else:
                issues.append(f"{p}: missing")
                continue
            if code["commit"] != own:
                issues.append(f"{p}: made by commit {code['commit']}, result by {own}")
            if code["dirty"]:
                issues.append(f"{p}: made from a dirty working tree")
        return issues


def _now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_json(path: Path, obj: Any) -> None:
    path.write_text(json.dumps(obj, indent=2, sort_keys=True, default=_json_default))


def _json_default(o: Any) -> Any:
    if isinstance(o, np.generic):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON-serialisable: {type(o).__name__}")
