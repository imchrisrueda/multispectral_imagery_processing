#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wavelength Analysis Module
===========================

Extracts and visualizes spectral wavelength information from multispectral images.

This module provides functionality to:
- Extract Center Wavelength (CWL) and FWHM from image metadata
- Generate Gaussian response curves
- Visualize spectral characteristics
- Plot wavelength distribution with FWHM bands

Requirements:
    - exiftool must be installed
    - numpy, matplotlib

Author: Christian Rueda
Date: 2025
License: MIT
"""

import json
import re
import subprocess
from typing import Any, Dict, Optional, Tuple
import logging

import numpy as np
import matplotlib.pyplot as plt

# Configure logging
logger = logging.getLogger(__name__)


class WavelengthAnalyzer:
    """
    Analyzes wavelength characteristics of multispectral images.
    
    Extracts Center Wavelength (CWL) and Full Width at Half Maximum (FWHM)
    from image metadata and generates spectral response curves.
    """
    
    # Possible metadata keys for CWL
    CWL_KEYS = [
        "CenterWavelength", "Wavelength", "CWL", "CentralWavelength",
        "SpectralBandCentralWavelength", "XMP:CenterWavelength",
        "XMP:Wavelength"
    ]
    
    # Possible metadata keys for FWHM
    FWHM_KEYS = [
        "FWHM", "Bandwidth", "BandWidth", "FullWidthHalfMax",
        "SpectralBandWidth", "XMP:FWHM", "XMP:Bandwidth"
    ]
    
    def __init__(self, exiftool_cmd: str = "exiftool"):
        """
        Initialize the wavelength analyzer.
        
        Args:
            exiftool_cmd: Path to exiftool executable
        """
        self.exiftool_cmd = exiftool_cmd
        self._verify_exiftool()
    
    def _verify_exiftool(self) -> None:
        """Verify that exiftool is available."""
        try:
            subprocess.run(
                [self.exiftool_cmd, "-ver"],
                capture_output=True,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                f"Exiftool not found at: {self.exiftool_cmd}\n"
                f"Please install it or provide the correct path."
            )
    
    def extract_metadata(self, image_path: str) -> Dict[str, Any]:
        """
        Extract all metadata from an image using exiftool.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with metadata
        """
        cmd = [self.exiftool_cmd, "-j", "-a", "-G", "-s", image_path]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            data = json.loads(result.stdout)
            return data[0] if isinstance(data, list) and data else {}
            
        except FileNotFoundError:
            raise RuntimeError(
                "Exiftool not found. Please install it and add to PATH."
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(
                f"Error running exiftool: {e.stderr or e.stdout}"
            )
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Error parsing exiftool JSON output: {e}")
    
    @staticmethod
    def _to_float_nm(value: Any) -> Optional[float]:
        """
        Convert a value to float in nanometers.
        
        Args:
            value: Value to convert (can be string with units, number, etc.)
            
        Returns:
            Float value in nm, or None if conversion fails
        """
        if value is None:
            return None
        
        if isinstance(value, (int, float)):
            return float(value)
        
        # Try to extract number from string
        s = str(value)
        pattern = r'([-+]?\d+(?:\.\d+)?)\s*(?:nm|nanometer|nanometers)?'
        match = re.search(pattern, s, re.IGNORECASE)
        
        if match:
            return float(match.group(1))
        
        return None
    
    def extract_cwl_fwhm(
        self,
        metadata: Dict[str, Any]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Extract Center Wavelength and FWHM from metadata.
        
        Args:
            metadata: Metadata dictionary from exiftool
            
        Returns:
            Tuple of (cwl, fwhm) in nanometers
        """
        cwl = None
        fwhm = None
        
        # Search in metadata keys
        for key, value in metadata.items():
            base_key = key.split(":")[-1]
            
            # Check for CWL
            if base_key in self.CWL_KEYS or key in self.CWL_KEYS:
                cwl = cwl or self._to_float_nm(value)
            
            # Check for FWHM
            if base_key in self.FWHM_KEYS or key in self.FWHM_KEYS:
                fwhm = fwhm or self._to_float_nm(value)
        
        # If not found, do fuzzy search in string values
        if cwl is None or fwhm is None:
            blob = "\n".join([
                str(v) for v in metadata.values()
                if isinstance(v, str) and v
            ])
            
            # Search for CWL
            if cwl is None:
                pattern = r'(center\s*wave(length)?|cwl)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)\s*nm'
                match = re.search(pattern, blob, re.IGNORECASE)
                if match:
                    cwl = float(match.group(3))
            
            # Search for FWHM
            if fwhm is None:
                pattern = r'(fwhm|band\s*width|bandwidth)\s*[:=]?\s*([-+]?\d+(?:\.\d+)?)\s*nm'
                match = re.search(pattern, blob, re.IGNORECASE)
                if match:
                    fwhm = float(match.group(2))
        
        return cwl, fwhm
    
    def analyze_image(self, image_path: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Analyze wavelength characteristics of an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (cwl, fwhm) in nanometers
        """
        metadata = self.extract_metadata(image_path)
        return self.extract_cwl_fwhm(metadata)
    
    @staticmethod
    def gaussian_from_fwhm(
        center_nm: float,
        fwhm_nm: Optional[float],
        wl_min: float = 350,
        wl_max: float = 1000,
        step: float = 0.5
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Generate Gaussian response curve from CWL and FWHM.
        
        Args:
            center_nm: Center wavelength in nm
            fwhm_nm: Full width at half maximum in nm (None for delta function)
            wl_min: Minimum wavelength for range
            wl_max: Maximum wavelength for range
            step: Step size for wavelength array
            
        Returns:
            Tuple of (wavelengths, response) arrays
        """
        wl = np.arange(wl_min, wl_max + step, step)
        
        # Delta function if no FWHM
        if not fwhm_nm or fwhm_nm <= 0:
            resp = np.zeros_like(wl, dtype=float)
            resp[(np.abs(wl - center_nm)).argmin()] = 1.0
            return wl, resp
        
        # Gaussian from FWHM
        # FWHM = 2 * sqrt(2 * ln(2)) * sigma
        sigma = fwhm_nm / (2.0 * np.sqrt(2.0 * np.log(2.0)))
        resp = np.exp(-0.5 * ((wl - center_nm) / sigma) ** 2)
        
        # Normalize
        if resp.max() > 0:
            resp /= resp.max()
        
        return wl, resp
    
    def plot_wavelength(
        self,
        image_path: str,
        cwl_override: Optional[float] = None,
        fwhm_override: Optional[float] = None,
        wl_min: float = 350,
        wl_max: float = 1000,
        save_path: Optional[str] = None,
        show: bool = True
    ) -> None:
        """
        Plot wavelength characteristics with response curve.
        
        Args:
            image_path: Path to image file
            cwl_override: Override CWL value (if metadata missing)
            fwhm_override: Override FWHM value (if metadata missing)
            wl_min: Minimum wavelength for plot
            wl_max: Maximum wavelength for plot
            save_path: Path to save figure (optional)
            show: Whether to show the plot
        """
        # Get wavelength info
        if cwl_override is not None:
            cwl = cwl_override
            fwhm = fwhm_override
        else:
            cwl, fwhm = self.analyze_image(image_path)
        
        if cwl is None:
            raise ValueError(
                "Could not extract CWL from metadata and no override provided"
            )
        
        # Generate response curve
        wl, resp = self.gaussian_from_fwhm(cwl, fwhm, wl_min, wl_max)
        
        # Create plot
        plt.figure(figsize=(10, 6))
        
        # Plot response curve
        plt.plot(wl, resp, linewidth=2, label="Response curve (idealized)")
        
        # Plot center wavelength
        plt.axvline(
            cwl,
            linestyle="--",
            linewidth=1.5,
            color='red',
            label=f"CWL = {cwl:.1f} nm"
        )
        
        # Plot half-height line
        plt.axhline(
            0.5,
            linestyle=":",
            linewidth=1.0,
            color='gray',
            label="Half height (50%)"
        )
        
        # Shade FWHM region if available
        if fwhm and fwhm > 0:
            # Find crossings with 50% line
            above = resp >= 0.5
            idx = np.where(np.diff(above.astype(int)) != 0)[0]
            crossings = []
            
            for i in idx:
                x0, x1 = wl[i], wl[i + 1]
                y0, y1 = resp[i], resp[i + 1]
                if y1 != y0:
                    xc = x0 + (0.5 - y0) * (x1 - x0) / (y1 - y0)
                    crossings.append(xc)
            
            if len(crossings) >= 2:
                left, right = crossings[0], crossings[-1]
                plt.fill_betweenx(
                    [0, 1],
                    left,
                    right,
                    alpha=0.2,
                    color='blue',
                    label=f"FWHM ≈ {right - left:.1f} nm"
                )
        
        # Formatting
        plt.xlim(wl_min, wl_max)
        plt.ylim(0, 1.05)
        plt.xlabel("Wavelength (nm)", fontsize=12)
        plt.ylabel("Relative Response", fontsize=12)
        plt.title(
            f"Spectral Response\n{image_path.split('/')[-1]}",
            fontsize=14
        )
        plt.grid(True, linestyle="--", linewidth=0.5, alpha=0.7)
        plt.legend(loc="upper right", fontsize=10)
        plt.tight_layout()
        
        # Save if requested
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            logger.info(f"Plot saved to: {save_path}")
        
        # Show if requested
        if show:
            plt.show()


# Convenience functions
def extract_cwl_fwhm(metadata: Dict[str, Any]) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract CWL and FWHM from metadata (convenience function).
    
    Args:
        metadata: Metadata dictionary from exiftool
        
    Returns:
        Tuple of (cwl, fwhm) in nanometers
    """
    analyzer = WavelengthAnalyzer()
    return analyzer.extract_cwl_fwhm(metadata)


def gaussian_from_fwhm(
    center_nm: float,
    fwhm_nm: Optional[float],
    wl_min: float = 350,
    wl_max: float = 1000,
    step: float = 0.5
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Generate Gaussian response curve (convenience function).
    
    Args:
        center_nm: Center wavelength in nm
        fwhm_nm: Full width at half maximum in nm
        wl_min: Minimum wavelength
        wl_max: Maximum wavelength
        step: Step size
        
    Returns:
        Tuple of (wavelengths, response) arrays
    """
    return WavelengthAnalyzer.gaussian_from_fwhm(
        center_nm, fwhm_nm, wl_min, wl_max, step
    )


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Analyze and plot spectral wavelength characteristics"
    )
    parser.add_argument(
        "--image",
        required=True,
        help="Path to image file"
    )
    parser.add_argument(
        "--wl",
        type=float,
        default=None,
        help="Override CWL in nm (if metadata missing)"
    )
    parser.add_argument(
        "--fwhm",
        type=float,
        default=None,
        help="Override FWHM in nm (if metadata missing)"
    )
    parser.add_argument(
        "--wlmin",
        type=float,
        default=350,
        help="Minimum wavelength for plot (default: 350 nm)"
    )
    parser.add_argument(
        "--wlmax",
        type=float,
        default=1000,
        help="Maximum wavelength for plot (default: 1000 nm)"
    )
    parser.add_argument(
        "--save",
        type=str,
        default=None,
        help="Save figure to file (PNG format)"
    )
    parser.add_argument(
        "--no-show",
        action="store_true",
        help="Don't display the plot"
    )
    
    args = parser.parse_args()
    
    # Create analyzer and plot
    analyzer = WavelengthAnalyzer()
    
    try:
        analyzer.plot_wavelength(
            image_path=args.image,
            cwl_override=args.wl,
            fwhm_override=args.fwhm,
            wl_min=args.wlmin,
            wl_max=args.wlmax,
            save_path=args.save,
            show=not args.no_show
        )
        
        logger.info("Analysis completed successfully")
        return 0
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
