"""Shared statistics helpers (from SG_final_round/src/analyze_single_qubit_pilot.py)."""
import math


def wilson(k,n):
    z=1.959963984540054
    den=1+z*z/n
    center=(k/n+z*z/(2*n))/den
    half=z*math.sqrt((k/n)*(1-k/n)/n+z*z/(4*n*n))/den
    return [max(0,center-half),min(1,center+half)]
