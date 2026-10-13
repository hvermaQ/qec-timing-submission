"""Application idle analysis: scheduling, the circuits, and the contract."""

import pytest

from qec_timing.apps.schedule import LogicalGate, profile

G = LogicalGate


def test_uniform_schedule_counts_interior_idle_only():
    # q0: gate in step 0, then waits while q1 runs its second gate (step 1), then
    # the shared gate in step 2 -> one idle stretch of 1. q1 is never idle.
    gates = [G((0,), False), G((1,), False), G((1,), False), G((0, 1), False)]
    p = profile(gates, 2, "uniform")
    assert p.steps == 3
    assert p.stretches == ((1.0,), ())
    assert p.active == (3.0, 3.0)


def test_magic_model_cliffords_take_no_time_and_do_not_end_idling():
    gates = [G((0,), True), G((0,), False), G((0,), False), G((0, 1), True), G((0,), True)]
    p = profile(gates, 2, "magic")
    # q0: T at 0-1, Cliffords at 1 (zero length), CCX-like at 1-2, T at 2-3: no idle.
    assert p.stretches[0] == ()
    gates = [G((0,), True), G((1,), True), G((1,), True), G((0,), False), G((0, 1), True)]
    p = profile(gates, 2, "magic")
    # q0 waits for q1's two T gates; its Clifford in between does not interrupt.
    assert p.stretches[0] == (1.0,)


def test_adder_is_correct_on_every_input():
    pytest.importorskip("pytket")
    from pytket import OpType

    from qec_timing.apps.library import adder_circuit

    nb = 4
    circ, a, b, z = adder_circuit(nb)
    for A in range(2 ** nb):
        for B in range(2 ** nb):
            bits = [0] * circ.n_qubits
            for i in range(nb):
                bits[a[i]], bits[b[i]] = (A >> i) & 1, (B >> i) & 1
            for cmd in circ.get_commands():
                q = [x.index[0] for x in cmd.qubits]
                if cmd.op.type == OpType.CX:
                    bits[q[1]] ^= bits[q[0]]
                else:
                    bits[q[2]] ^= bits[q[0]] & bits[q[1]]
            total = sum(bits[b[i]] << i for i in range(nb)) + (bits[z] << nb)
            assert total == A + B and all(bits[a[i]] == (A >> i) & 1 for i in range(nb))


def test_library_sources_pass_contract_and_reproduce_notebook_10():
    pytest.importorskip("pytket")
    from qec_timing.apps.library import QFT, CuccaroAdder, IsingTrotter
    from qec_timing.testing import contracts as C

    expected = {  # original notebook 10, idle fraction (uniform, magic)
        QFT(16): (0.410, 0.509), IsingTrotter(16, 8): (0.141, 0.351), CuccaroAdder(8): (0.843, 0.870)}
    for src, (u, m) in expected.items():
        C.check_idle_source(src)
        assert src.idle_profile("uniform").idle_fraction == pytest.approx(u, abs=1e-3)
        assert src.idle_profile("magic").idle_fraction == pytest.approx(m, abs=1e-3)
