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


# --------------------------------------------------------------------------- legacy H2-1E policy
# The sleep-dependent phenomenological policy of SG_final_round/src/redecode_d3_sleep_dependent.py
# (constants and functions verbatim). Used by the H2-1E emulator re-decodes (d=3 and d=5) and as
# the "old decoder" baseline in the physical H2-2 analyses. Same arithmetic as
# `round_probabilities` above with p_ext=.002, p_read=.001; kept separately so historical results
# reproduce byte for byte. It is not an approved physical H2-2 policy (/AGENTS.md).

LEGACY_P_EXT=.002
LEGACY_P_READ=.001
LINEAR_RATE=.0028
QUADRATIC_FREQUENCY_HZ=.043
INCOHERENT_FACTOR=2.0
LEGACY_SOURCES=[
 'https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/emulators/h2_emulators.html',
 'https://docs.quantinuum.com/systems/user_guide/emulator_user_guide/noise_model.html']


def xor_probability(a,b):
    return a+b-2*a*b


def idle_probability(u):
    """Independent stochastic Z channels, with frequency converted to rad/s.

    Frequency parameter is in units of 2*pi rad/s; incoherence multiplies
    frequency (not probability). Net Z is odd parity of the two channel faults.
    """
    if not 0<=LINEAR_RATE*u<=1:
        raise ValueError('Duration outside linear-channel probability domain')
    lin=LINEAR_RATE*u
    quad=math.sin(math.pi*QUADRATIC_FREQUENCY_HZ*INCOHERENT_FACTOR*u)**2
    return xor_probability(lin,quad)


def legacy_round_probabilities(n,u):
    # N extraction draws, but only N-1 waits; no wait before the first round.
    p=xor_probability(LEGACY_P_EXT,idle_probability(u))
    return [RoundNoise(LEGACY_P_EXT,LEGACY_P_READ)]+[RoundNoise(p,LEGACY_P_READ) for _ in range(n-1)]
