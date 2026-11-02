# Final-round experiments: explicit sleep on H2-1E

First experiment: d=3, X-basis memory, nine data qubits and one reused ancilla,
two extraction rounds. Compare no sleep, sleep(0), and sleep arguments
0.01, 0.05, 0.1, 0.2, 0.5 on data qubit 4 (the centre of the patch), between
rounds. These are **raw instruction arguments for syntax testing**, not
established durations in seconds. See `results/duration_review.md` for the
previous H2 results and the conditional physical timescale calculation.
There are no artificial Pauli errors or offline readout flips.

## Implementation

The memory circuit originates in the existing Guppy builder
`src/qec_timing/hardware/qir.py`. For this initial probe we reuse its committed,
compiled `results/hardware/programs/d3_X_r2_p0.{ll,bc,json}` artifact. The new
Python builder imports the existing surface-code definition and adds one call
to the textual QIR, followed by LLVM assembly to bitcode:

```llvm
declare void @__quantum__qis__sleep__body(%Qubit*, double)
; After round 0's final ancilla reset, before round 1 begins:
call void @__quantum__qis__sleep__body(%Qubit* inttoptr (i64 4 to %Qubit*), double 1.00000000000000002e-02)
```

The signature follows Quantinuum's
[pytket-qir converter](https://docs.quantinuum.com/tket/extensions/pytket-qir/_modules/pytket/qir/conversion/qirgenerator.html).
Endpoint support, units, scheduling, and idle-noise effects remain unverified.
This does not add Guppy sleep support. It isolates the backend instruction test
from Guppy/hugr-qir lowering. The original artifact is hash-pinned and copied into
each build. Changed input fails closed and requires re-inspection of the boundary.

All seven variants are assembled with the same clang, at O0. The original
bitcode is retained separately: clang may change the LLVM representation, so
the reassembled no-sleep control is essential. Assembly and round-trip checks
are not Quantinuum QIR-profile validation or proof of execution semantics.
The stored Schedule is inherited bookkeeping; it does not describe physical wait
time. Sleep information enters `spec.extra` so variants have distinct run identities.

## Layout

- `env/`: environment requirements and records.
- `src/`: new experiment code; imports existing definitions read-only.
- `configs/`: inputs, including raw duration and selected data qubit.
- `programs/<build-id>/`: original and modified QIR, bitcode, diffs, hashes,
  assembly diagnostics, toolchain versions, and syntax-check plan.
- `runs/`: provider job records and raw results; never put credentials here.
- `results/`: analysis, figures, local test records.
- `tests/`: local structural checks.

## Local build

From the repository root, Python 3.9+ and clang suffice; no H2 dependencies are
needed to transform the archived artifact.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s SG_final_round/tests -v
PYTHONDONTWRITEBYTECODE=1 python3 SG_final_round/src/build_sleep_probe.py --clang clang
```

Omit `--clang` to generate textual QIR only. Each build has its own identity;
an existing build directory is not overwritten. To change duration edit the
config (or pass another config under this folder). Do not label raw values as
milliseconds or seconds until the endpoint contract is verified.

## Provider checks: next stage

Use the `syntax_plan.json` in the successful build. In an environment with the
existing hardware dependencies and aqora authentication, each check can reuse:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m qec_timing.hardware.cli \
  --store SG_final_round/runs aqora-check \
  SG_final_round/programs/<build-id>/no_sleep.bc \
  --platform nexus:H2-1SC --as-entity q_sq --shots 1
```

Repeat for the other six files in `syntax_plan.json`, retaining all responses.
Finite variants are named `sleep_0p01.bc`, `sleep_0p05.bc`, `sleep_0p1.bc`,
`sleep_0p2.bc`, and `sleep_0p5.bc`. The earlier three-variant build is retained
as a historical artifact; use the plan from the new seven-variant build.
Do not interpret baseline compilation failure as rejection of sleep. If the
reassembled baseline fails, check the preserved original bitcode to isolate
LLVM/toolchain compatibility. Local tools that do not implement sleep cannot
establish whether H2 supports it by treating it as an identity.

No emulator submission is included in this builder. After syntax acceptance,
resolve units and scheduling, record noise/DD options exposed by aqora, estimate
cost, and define the small execution pilot. Fixed two-round comparisons isolate
the added wait; they are not yet fixed-total-time timing optimization.

Single-target sleep is an instruction-support probe. It does not establish that
all nine data qubits wait together or that a synchronous round boundary survives
backend scheduling. That requires a later scheduling test. Flat logical error
rates alone do not establish absent idle noise; inspect detector rates and use
uncorrected memory calibration probes for sensitivity.

Current build: `programs/5944c048c1dfdc80/`. Proposed shot counts and HQC estimates
are in `results/shot_budget.md`; these do not submit jobs or change shot metadata.

## Completed standalone pilot

The one-qubit pilot on H2-1E through Aqora completed with 200 shots per setting:
no sleep 0 errors, sleep(0) 0 errors, sleep(0.5) 2 errors. Details, intervals and
interpretation are in `results/single_qubit_pilot.md`. Circuits are under
`programs/single_qubit_2c64d96fea4bbbac/` and original job responses under
`runs/single_qubit_2c64d96fea4bbbac/`. Duration units remain unverified.

## Completed 1,000-shot explicit-sleep sweep

H2-1E through Aqora: raw sleep arguments 0, 0.1, 0.5, 0.75, 1, with 1,000
shots each and no no-sleep variant. Error counts: 0, 1, 21, 55, 92. See
`results/single_qubit_sweep_1000.md` for intervals, settings and raw-record paths.
The 200-shot pilot and d=3 artifacts are preserved separately.
