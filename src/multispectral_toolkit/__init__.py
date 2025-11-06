"""
Multispectral Imagery Processing Toolkit
=========================================

A comprehensive toolkit for processing and analyzing multispectral imagery,
particularly optimized for MicaSense camera systems.

Main modules:
    - core: Core processing functionality
    - gui: Graphical user interfaces
    - utils: Utility functions and helpers

Author: Christian Rueda
License: MIT
Version: 1.0.0
"""

__version__ = "1.0.0"
__author__ = "Christian Rueda"
__license__ = "MIT"

from .core import altitude_extractor, file_organizer, wavelength_analyzer

__all__ = [
    "altitude_extractor",
    "file_organizer",
    "wavelength_analyzer",
    "__version__",
]
