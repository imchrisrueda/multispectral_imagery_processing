"""
Core Processing Modules
=======================

Contains the main processing logic for:
- Altitude extraction from EXIF data
- Multispectral file organization
- Wavelength analysis
"""

from .altitude_extractor import AltitudeExtractor, extract_altitude_from_image, process_directory
from .file_organizer import MultispectralOrganizer
from .wavelength_analyzer import WavelengthAnalyzer, extract_cwl_fwhm, gaussian_from_fwhm

__all__ = [
    "AltitudeExtractor",
    "extract_altitude_from_image",
    "process_directory",
    "MultispectralOrganizer",
    "WavelengthAnalyzer",
    "extract_cwl_fwhm",
    "gaussian_from_fwhm",
]
