"""Educational LMS equalizer simulator for digital communication systems."""

from .equalizer import LMSLinearEqualizer
from .simulation import run_simulation, run_snr_sweep

__all__ = ["LMSLinearEqualizer", "run_simulation", "run_snr_sweep"]
