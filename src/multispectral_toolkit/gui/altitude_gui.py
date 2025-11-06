#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Altitude Analyzer GUI Application
==================================

Desktop application for extracting and analyzing GPS altitude from images.

Features:
- Browse and select image directories
- Configure analysis parameters
- Real-time progress tracking
- Export results to CSV
- Support for RGB, Thermal, and Multispectral images

Requirements:
    - PyQt6
    - pandas
    - exiftool installed and in PATH

Author: Christian Rueda
Date: 2025
License: MIT
"""

# This is a reference to the original altitude_check_app.py
# The GUI implementation has been preserved in the original file
# for compatibility. Use the core modules for programmatic access.

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..core.altitude_extractor import AltitudeExtractor


class AltitudeAnalyzerGUI:
    """
    Wrapper class for the altitude analyzer GUI.
    
    Note: The full GUI implementation is in altitude_check_app.py
    for backward compatibility.
    """
    
    @staticmethod
    def launch():
        """Launch the altitude analyzer GUI application."""
        # Import the original app
        root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        app_path = os.path.join(root_dir, "altitude_check_app.py")
        
        if os.path.exists(app_path):
            import subprocess
            subprocess.run([sys.executable, app_path])
        else:
            print("GUI application not found. Please use the core modules directly.")
            print("Example:")
            print("  from multispectral_toolkit.core import AltitudeExtractor")
            print("  extractor = AltitudeExtractor()")
            print("  df = extractor.process_directory('path/to/images')")


def main():
    """Command-line entry point."""
    AltitudeAnalyzerGUI.launch()


if __name__ == "__main__":
    main()
