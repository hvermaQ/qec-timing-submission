"""Simulators and hardware adapters. Each lives in its own module and registers itself."""

from qec_timing.backends.base import Backend, run_checked

__all__ = ["Backend", "run_checked"]
