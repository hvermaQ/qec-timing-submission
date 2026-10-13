"""Circuit-level backend on Selene's NATIVE gates (original notebooks 07b and 09).

Selene compiles each CX into one Rzz plus single-qubit Rxy / Rz gates. On a device
that is what runs, so a round carries more, and differently placed, gate faults
than the textbook circuit. This backend:

  1. writes the extraction circuit as a Guppy program (CX order and logical from
     Stim's generated rotated memory circuit, both sectors measured each round,
     a fresh ancilla array per round), compiles it with Selene, and reads the
     native operations of one noiseless shot (`CircuitExtractor`); cached per
     (d, basis, rounds);
  2. rebuilds them gate for gate in Stim. Each gate goes through its unitary
     (`stim.Tableau.from_unitary_matrix`), and the round trip is checked: Stim
     silently returns a wrong Clifford for a non-Clifford input;
  3. places `CircuitNoise`: DEPOLARIZE1(p1) before each Rxy (and Rz if
     spec.extra["rz_noise"]; H2's Rz is virtual, so off by default), DEPOLARIZE2(p2)
     before each Rzz (placement by analogy with Selene's 1q noise, not read off
     its log), record flip p_meas, X_ERROR(p_init) after each reset; idle noise
       "uniform":       ops scheduled ASAP into L layers per round, each lasting
                        1/L; every qubit gets idle(1/L) after each layer and
                        idle(dt - 1) before the round;
       "data_interval": idle(dt) on the data at the start of each round;
  4. writes detectors in the standard layout (checks ordered as in
     `RotatedSurfaceCode`, via the same alignment as `stim_circuit`).
"""

from __future__ import annotations

import importlib.metadata as md
import importlib.util
import json
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import stim

from qec_timing.backends.stim_circuit import _generated, alignment
from qec_timing.codes.base import checks_of
from qec_timing.noise.circuit import CircuitNoise
from qec_timing.records import DetectorLayout, RawRecord
from qec_timing.registry import register
from qec_timing.spec import MemorySpec

PREAMBLE = """from guppylang import guppy
from guppylang.std.angles import angle
from guppylang.std.builtins import array, output, py
from guppylang.std.quantum import collect_measurements, cx, h, measure, measure_array, qubit


"""

# --- the extraction circuit, from Stim's layout ---------------------------------

@lru_cache(maxsize=None)
def stim_layout(d: int, basis: str) -> dict:
    """Data qubits, ancillas by sector, CX pairs in order, observable (Stim qubit ids)."""
    c = _generated(basis, d, 1)
    anc, data_order, cx_pairs, obs = set(), [], [], []
    for inst in c.flattened():
        t = [g.value for g in inst.targets_copy() if g.is_qubit_target]
        if inst.name == "CX":
            cx_pairs += [(t[i], t[i + 1]) for i in range(0, len(t), 2)]
        elif inst.name == "MR":
            anc.update(t)
        elif inst.name in ("M", "MX"):
            data_order = t
        elif inst.name == "OBSERVABLE_INCLUDE":
            recs = [g.value for g in inst.targets_copy() if g.is_measurement_record_target]
            obs = [data_order[len(data_order) + r] for r in recs]
    zsup, xsup = {}, {}
    for ctrl, tgt in cx_pairs:
        if tgt in anc:
            zsup.setdefault(tgt, []).append(ctrl)
        if ctrl in anc:
            xsup.setdefault(ctrl, []).append(tgt)
    data = [q for q in data_order if q not in anc]
    return dict(data=data, zanc=sorted(zsup), xanc=sorted(xsup), zsup=zsup, xsup=xsup,
                obs=obs, cx=cx_pairs, coords=c.get_final_qubit_coordinates())


def program_source(d: int, basis: str, rounds: int) -> str:
    L = stim_layout(d, basis)
    didx = {q: i for i, q in enumerate(L["data"])}
    aidx = {q: i for i, q in enumerate(L["zanc"] + L["xanc"])}
    n_data, n_anc = len(didx), len(aidx)
    o = ["@guppy", "def prog() -> None:", f"    qs = array(qubit() for _ in range(py({n_data})))"]
    if basis == "X":
        o += [f"    for i in range(py({n_data})):", "        h(qs[i])"]
    o += [f"    for _ in range(py({rounds})):",
          f"        anc = array(qubit() for _ in range(py({n_anc})))"]
    o += [f"        h(anc[{aidx[a]}])" for a in L["xanc"]]
    for ctrl, tgt in L["cx"]:
        cs = f"anc[{aidx[ctrl]}]" if ctrl in aidx else f"qs[{didx[ctrl]}]"
        ts = f"anc[{aidx[tgt]}]" if tgt in aidx else f"qs[{didx[tgt]}]"
        o.append(f"        cx({cs}, {ts})")
    o += [f"        h(anc[{aidx[a]}])" for a in L["xanc"]]
    o.append('        output("s", collect_measurements(measure_array(anc)))')
    if basis == "X":
        o += [f"    for i in range(py({n_data})):", "        h(qs[i])"]
    o.append('    output("data", collect_measurements(measure_array(qs)))')
    return PREAMBLE + "\n".join(o) + "\n"


def extract_native_ops(d: int, basis: str, rounds: int) -> list[dict]:
    """Compile with Selene and read one noiseless shot's native operations."""
    from selene_sim import CircuitExtractor, IdealErrorModel, Stim, build

    name = f"native_{basis}_d{d}_r{rounds}"
    path = Path(tempfile.mkdtemp(prefix="qec_native_")) / f"{name}.py"
    # Guppy reads the decorated function's source from disk; exec() of a string fails.
    path.write_text(program_source(d, basis, rounds))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    instance = build(mod.prog.compile())
    L = stim_layout(d, basis)
    hook = CircuitExtractor()
    for shot in instance.run_shots(simulator=Stim(), n_qubits=len(L["data"]) + len(L["zanc"]) + len(L["xanc"]),
                                   n_shots=1, error_model=IdealErrorModel(), random_seed=1,
                                   event_hook=hook):
        list(shot)                    # consume as it arrives, or the child process dies
    return hook.shots[0].get_error_model_output()


_KINDS = ("Reset", "Rxy", "Rz", "Rzz", "MeasureRequest", "QAlloc", "QFree", "BatchStart")


def _pack(ops: list[dict]) -> dict:
    nan = float("nan")
    for o in ops:
        if o["op"] not in _KINDS:
            raise ValueError(f"cannot store native op: {o}")
    return dict(kind=np.array([_KINDS.index(o["op"]) for o in ops], np.int8),
                q0=np.array([o.get("qubit", o.get("qubit0", -1)) for o in ops], np.int32),
                q1=np.array([o.get("qubit1", -1) for o in ops], np.int32),
                theta=np.array([o.get("theta", nan) for o in ops], float),
                phi=np.array([o.get("phi", nan) for o in ops], float))


def _unpack(a) -> list[dict]:
    ops = []
    for k, q0, q1, th, ph in zip(a["kind"], a["q0"], a["q1"], a["theta"], a["phi"]):
        kind = _KINDS[k]
        if kind == "Rzz":
            ops.append({"op": kind, "qubit0": int(q0), "qubit1": int(q1), "theta": float(th)})
            continue
        o = {"op": kind}
        if q0 >= 0:
            o["qubit"] = int(q0)
        if not np.isnan(th):
            o["theta"] = float(th)
        if not np.isnan(ph):
            o["phi"] = float(ph)
        ops.append(o)
    return ops


# --- scheduling ----------------------------------------------------------------

def segments(ops, n_data, n_anc):
    """(prep, rounds, final): a round starts at the first non-data reset and ends when
    n_anc non-data qubits have been measured."""
    ops = [o for o in ops if o["op"] not in ("QAlloc", "QFree", "BatchStart")]
    data, i = set(), 0
    while len(data) < n_data:
        if ops[i]["op"] == "Reset":
            data.add(ops[i]["qubit"])
        i += 1
    prep, rounds, final, cur, n_meas = ops[:i], [], [], None, 0
    for o in ops[i:]:
        q = o.get("qubit")
        if cur is None:
            if o["op"] == "Reset" and q not in data:
                cur, n_meas, final = [], 0, []
            else:
                (final if rounds else prep).append(o)
                continue
        cur.append(o)
        if o["op"] == "MeasureRequest" and q not in data:
            n_meas += 1
            if n_meas == n_anc:
                rounds.append(cur)
                cur = None
    assert cur is None, "op list ends inside a round"
    return prep, rounds, final


def _qubits(o):
    return [o["qubit0"], o["qubit1"]] if o["op"] == "Rzz" else [o["qubit"]]


def layers(round_ops):
    """ASAP: each op in the first layer after every earlier op on its qubits. Order on
    each qubit is kept, so the circuit is unchanged."""
    free, out = {}, []
    for o in round_ops:
        qs = _qubits(o)
        k = max(free.get(q, 0) for q in qs)
        for q in qs:
            free[q] = k + 1
        while len(out) <= k:
            out.append([])
        out[k].append(o)
    return out


# --- native gate -> Stim -------------------------------------------------------

_X = np.array([[0, 1], [1, 0]], dtype=complex)
_Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
_GATES: dict[tuple, stim.Circuit] = {}


def _unitary(op):
    if op["op"] == "Rxy":
        th, ph = op["theta"], op["phi"]
        return np.cos(th / 2) * np.eye(2) - 1j * np.sin(th / 2) * (np.cos(ph) * _X + np.sin(ph) * _Y)
    if op["op"] == "Rz":
        return np.diag([np.exp(-1j * op["theta"] / 2), np.exp(1j * op["theta"] / 2)])
    return np.diag(np.exp(-1j * op["theta"] / 2 * np.array([1, -1, -1, 1])))


def _clifford(op):
    key = (op["op"], round(op["theta"], 9), round(op.get("phi", 0.0), 9))
    if key not in _GATES:
        U = _unitary(op)
        tab = stim.Tableau.from_unitary_matrix(U, endian="little")
        V = tab.to_unitary_matrix(endian="little")
        if abs(abs(np.trace(V.conj().T @ U)) - U.shape[0]) > 1e-6:
            raise ValueError(f"not a Clifford gate, cannot be mirrored: {op}")
        _GATES[key] = tab.to_circuit(method="elimination")
    return _GATES[key], _qubits(op)


def to_stim(ops, d: int, basis: str, rounds: int, noise: CircuitNoise, rz_noise: bool,
            data_idle=None) -> stim.Circuit:
    L = stim_layout(d, basis)
    n_data, n_anc = len(L["data"]), len(L["zanc"]) + len(L["xanc"])
    anc_order = L["zanc"] + L["xanc"]                       # per-round ancilla array order
    position = alignment(d, basis)
    decoded = [(position[tuple(L["coords"][a][:2])], i, a) for i, a in enumerate(anc_order)
               if tuple(L["coords"][a][:2]) in position]
    decoded.sort()                                          # our check order
    sup = {a: (L["zsup"] if basis == "Z" else L["xsup"])[a] for _, _, a in decoded}
    data_pos = {q: i for i, q in enumerate(L["data"])}

    c = stim.Circuit()
    data_ids, anc_ids, resets = None, [], []
    rec, n_meas, rnd = {}, 0, -1
    for op in ops:
        kind = op["op"]
        if kind == "Reset":
            if data_ids is not None and (len(anc_ids) == n_anc or rnd < 0):
                anc_ids, rnd = [], rnd + 1
                if data_idle is not None:
                    c.append("PAULI_CHANNEL_1", data_ids, list(data_idle))
            c.append("R", [op["qubit"]])
            if noise.p_init:
                c.append("X_ERROR", [op["qubit"]], noise.p_init)
            resets.append(op["qubit"])
            if data_ids is None:
                if len(resets) == n_data:
                    data_ids = list(resets)
            else:
                anc_ids.append(op["qubit"])
        elif kind in ("Rxy", "Rz"):
            if noise.p1 and (rz_noise or kind == "Rxy"):
                c.append("DEPOLARIZE1", [op["qubit"]], noise.p1)
            local, qs = _clifford(op)
            for inst in local:
                c.append(inst.name, [qs[t.value] for t in inst.targets_copy()], inst.gate_args_copy())
        elif kind == "Rzz":
            if noise.p2:
                c.append("DEPOLARIZE2", [op["qubit0"], op["qubit1"]], noise.p2)
            local, qs = _clifford(op)
            for inst in local:
                c.append(inst.name, [qs[t.value] for t in inst.targets_copy()], inst.gate_args_copy())
        elif kind == "MeasureRequest":
            q = op["qubit"]
            c.append("M", [q], noise.p_meas) if noise.p_meas else c.append("M", [q])
            if q in anc_ids and (rnd, anc_ids.index(q)) not in rec:
                rec[(rnd, anc_ids.index(q))] = n_meas
            elif data_ids is not None and q in data_ids:
                rec[("data", data_ids.index(q))] = n_meas
            else:
                raise ValueError(f"measurement of unexpected qubit {q}")
            n_meas += 1
        elif kind == "Idle":
            c.append("PAULI_CHANNEL_1", op["qubits"], list(op["channel"]))
        elif kind in ("QAlloc", "QFree", "BatchStart"):
            continue
        else:
            raise ValueError(f"operation not mirrored: {op}")
    assert data_ids is not None and rnd + 1 == rounds, (rnd + 1, rounds)
    assert len(rec) == rounds * n_anc + n_data

    r = lambda key: stim.target_rec(rec[key] - n_meas)          # noqa: E731
    for j in range(rounds + 1):
        for _, col, a in decoded:
            t = [r((j, col))] if j < rounds else [r(("data", data_pos[q])) for q in sup[a]]
            if j > 0:
                t.append(r((j - 1, col)))
            c.append("DETECTOR", t)
    c.append("OBSERVABLE_INCLUDE", [r(("data", data_pos[q])) for q in L["obs"]], 0)
    return c


@register("backend", "stim_native")
class StimNativeBackend:
    name = "stim_native"

    def __init__(self, cache_dir: str | Path = "store/cache/native_ops") -> None:
        self.cache = Path(cache_dir)
        self._ops: dict[tuple, list[dict]] = {}

    def versions(self) -> dict[str, str]:
        return {p: md.version(p) for p in ("stim", "selene-sim", "guppylang")}

    def supports(self, spec: MemorySpec) -> str | None:
        if spec.code.name != "rotated_surface":
            return "native program is written for the rotated surface code"
        if not isinstance(spec.noise, CircuitNoise):
            return "needs CircuitNoise"
        if not spec.schedule.is_constant:
            return "one interval per run"
        if spec.noise.placement == "uniform" and spec.schedule.dts[0] < 1.0 - 1e-12:
            return "uniform placement: dt is the full round period, so dt >= 1"
        return None

    def native_ops(self, d: int, basis: str, rounds: int) -> list[dict]:
        key = (d, basis, rounds)
        if key not in self._ops:
            path = self.cache / f"{basis}_d{d}_r{rounds}.npz"
            if path.exists():
                self._ops[key] = _unpack(np.load(path))
            else:
                ops = extract_native_ops(d, basis, rounds)
                self.cache.mkdir(parents=True, exist_ok=True)
                np.savez(path, **_pack(ops))
                path.with_suffix(".json").write_text(json.dumps(
                    {"versions": self.versions(), "n_ops": len(ops)}, indent=1))
                self._ops[key] = ops
        return self._ops[key]

    def prepare(self, spec: MemorySpec) -> None:
        """Compile and cache the native gates for this spec (Selene; not fork-safe)."""
        self.native_ops(spec.code.d, spec.basis, spec.schedule.n_rounds)

    def circuit(self, spec: MemorySpec) -> stim.Circuit:
        noise: CircuitNoise = spec.noise
        d, basis, R = spec.code.d, spec.basis, spec.schedule.n_rounds
        dt = spec.schedule.dts[0]
        rz_noise = bool(spec.extra.get("rz_noise", False))
        ops = self.native_ops(d, basis, R)
        if noise.placement == "data_interval":
            return to_stim(ops, d, basis, R, noise, rz_noise, data_idle=noise.idle.channel(dt))
        L = stim_layout(d, basis)
        prep, rnds, final = segments(ops, len(L["data"]), len(L["zanc"]) + len(L["xanc"]))
        assert len(rnds) == R
        allq = sorted({q for o in ops if "qubit" in o or "qubit0" in o for q in _qubits(o)})
        wait = noise.idle.channel(dt - 1.0)
        nonzero = lambda ch: any(v > 0 for v in ch)          # noqa: E731
        out = list(prep)
        for rnd in rnds:
            lay = layers(rnd)
            if nonzero(wait):
                out.append({"op": "Idle", "qubits": allq, "channel": wait})
            step = noise.idle.channel(1.0 / len(lay))
            for layer_ops in lay:
                out += layer_ops
                if nonzero(step):
                    out.append({"op": "Idle", "qubits": allq, "channel": step})
        out += final
        return to_stim(out, d, basis, R, noise, rz_noise)

    def dem(self, spec: MemorySpec) -> str:
        return str(self.circuit(spec).detector_error_model(decompose_errors=True))

    def run(self, spec: MemorySpec) -> RawRecord:
        c = self.circuit(spec)
        det, obs = c.compile_detector_sampler(seed=spec.seed).sample(
            spec.shots, separate_observables=True)
        s = spec.schedule
        nan = np.full(s.n_rounds, np.nan)
        rounds = {"dt": np.array(s.dts), "t": np.array(s.starts), "p_data": nan, "p_read": nan.copy()}
        layout = DetectorLayout(s.n_rounds, len(checks_of(spec.code, spec.basis)))
        return RawRecord(layout, det, obs, rounds,
                         payload={"seed": spec.seed, "rz_noise": bool(spec.extra.get("rz_noise", False))})
