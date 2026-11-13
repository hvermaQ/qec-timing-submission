"""Current user-approved decoder policy for physical H2-2 analyses."""
import json
import math
from pathlib import Path
from qec_timing.noise.base import RoundNoise

POLICY_PATH = Path(__file__).resolve().parents[1] / 'configs/h2_2_decoder.json'
POLICY = json.loads(POLICY_PATH.read_text())
P_EXT = POLICY['p_ext']
P_READ = POLICY['p_read']

def round_probabilities(n, u):
    if n < 1 or u < 0:
        raise ValueError('Require at least one round and nonnegative sleep')
    lin = POLICY['linear_rate_per_second'] * u
    if not 0 <= lin <= 1:
        raise ValueError('Duration outside linear-channel probability domain')
    quad = math.sin(math.pi * POLICY['frequency_hz'] * POLICY['frequency_multiplier'] * u) ** 2
    idle = lin + quad - 2 * lin * quad
    p = P_EXT + idle - 2 * P_EXT * idle
    return [RoundNoise(P_EXT, P_READ)] + [RoundNoise(p, P_READ) for _ in range(n-1)]
