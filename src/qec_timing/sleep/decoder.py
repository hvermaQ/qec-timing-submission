"""Current user-approved decoder policy for physical H2-2 analyses.

Moved from SG_final_round/src/h2_2_decoder.py. The policies are config/sleep/decoders/*.json,
byte-identical to the originals (analyses compare stored policy dicts for equality):

    h2_2_decoder.json             d=3 physical H2-2, p_ext 0.00117 (the default, as before)
    h2_2_d5_decoder.json          d=5 physical H2-2, original mapping, p_ext 0.004
    h2_2_d5_skip5_decoder.json    d=5 physical H2-2, skip-index-5 mapping, p_ext 0.005

The policy rules are in /AGENTS.md. They apply to physical H2-2 only, not to H2-1 or the
emulators. Never pool results decoded under different policies or mappings.
"""
import json
import math

from qec_timing.noise.base import RoundNoise

from . import paths

POLICY_FILES = {'d3': 'h2_2_decoder.json', 'd5': 'h2_2_d5_decoder.json', 'd5_skip5': 'h2_2_d5_skip5_decoder.json'}


def load_policy(name='d3'):
    """A policy dict by key ('d3', 'd5', 'd5_skip5') or file name in config/sleep/decoders/."""
    return json.loads(paths.read_text(paths.DECODERS / POLICY_FILES.get(name, name)))


POLICY_PATH = paths.DECODERS / POLICY_FILES['d3']
POLICY = load_policy('d3')
P_EXT = POLICY['p_ext']
P_READ = POLICY['p_read']

def round_probabilities(n, u, *, policy=None):
    policy = POLICY if policy is None else policy
    p_ext, p_read = policy['p_ext'], policy['p_read']
    if n < 1 or u < 0:
        raise ValueError('Require at least one round and nonnegative sleep')
    lin = policy['linear_rate_per_second'] * u
    if not 0 <= lin <= 1:
        raise ValueError('Duration outside linear-channel probability domain')
    quad = math.sin(math.pi * policy['frequency_hz'] * policy['frequency_multiplier'] * u) ** 2
    idle = lin + quad - 2 * lin * quad
    p = p_ext + idle - 2 * p_ext * idle
    return [RoundNoise(p_ext, p_read)] + [RoundNoise(p, p_read) for _ in range(n-1)]
