"""
PyTLWall - Python Transmission Line Wall Impedance Calculator

Main package initialization.
"""

from .beam import Beam, BeamValidationError, M_PROTON_MEV
from .frequencies import Frequencies
from .layer import Layer
from .chamber import Chamber
from .cfg_io import CfgIo
from .tlwall import TlWall
from .multiple_chamber import MultipleChamber

# I/O utilities
from . import io_util

# Logging utilities (optional, can be imported explicitly if needed)
from . import logging_util

__all__ = [
    'Beam',
    'BeamValidationError', 
    'M_PROTON_MEV',
    'Frequencies', 
    'Layer',
    'Chamber',
    'TlWall',
    'CfgIo',
    'io_util',
    'logging_util',
    'MultipleChamber'
]

__version__ = '1.0.0'
