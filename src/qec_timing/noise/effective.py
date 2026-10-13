"""The paper's model with measured parameters: what the circuit looks like to the
phenomenological description.

    p_data(dt) = p_data(1) XOR q_wait(dt - 1)        p_read constant

p_data(1) and p_read come from one calibration run at dt = 1 (back-to-back
rounds, `EdgeExtractor`); q_wait is the Z probability of the idle channel over
the wait, which is what an idle benchmark on the device measures. With `wait`
None, p_data is the same at every dt (a model measured at each dt separately).
This is the "measured once" arm of the original notebooks 08/09.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

from qec_timing.codes.base import Pauli
from qec_timing.extract.edges import xor
from qec_timing.noise.base import RoundNoise
from qec_timing.noise.circuit import IdleNoise
from qec_timing.registry import register


@register("noise", "effective")
@dataclass(frozen=True)
class EffectiveNoise:
    p_data: float
    p_read: float
    wait: IdleNoise | None = None
    pauli: Pauli = "Z"

    name = "effective"

    def params(self) -> dict[str, Any]:
        return {"p_data": self.p_data, "p_read": self.p_read,
                "wait": None if self.wait is None else asdict(self.wait)}

    @property
    def data_pauli(self) -> Pauli:
        return self.pauli

    def round_noise(self, t: float, dt: float) -> RoundNoise:
        if self.wait is None:
            return RoundNoise(self.p_data, self.p_read)
        return RoundNoise(float(xor(self.p_data, self.wait.pz(dt - 1.0))), self.p_read)

    def final_read(self) -> float:
        return self.p_read
