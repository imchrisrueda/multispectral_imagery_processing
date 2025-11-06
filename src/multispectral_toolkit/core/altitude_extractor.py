#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Altitude Extraction Module
===========================

Extracts GPS altitude information from image EXIF data using exiftool.

This module provides functionality to:
- Extract altitude from individual images
- Process entire directories of images
- Compare altitude changes between sequential images
- Generate reports of altitude variations

Requirements:
    - exiftool must be installed and available in PATH
    - On Ubuntu/Debian: sudo apt install libimage-exiftool-perl
    - On macOS: brew install exiftool
    - On Windows: download from https://exiftool.org/

Author: Christian Rueda
Date: 2025
License: MIT
"""

import os
import subprocess
import json
import re
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class AltitudeData:
    """Data class for storing altitude information."""
    filename: str
    altitude: Optional[float]
    status: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "Archivo": self.filename,
            "Altitud (m)": round(self.altitude, 2) if self.altitude is not None else "No disponible",
            "Estado": self.status
        }


class AltitudeExtractor:
    """
    Extracts altitude information from images using exiftool.
    
    Attributes:
        exiftool_cmd (str): Path to exiftool executable
        altitude_threshold (float): Threshold for detecting significant altitude changes (meters)
    """
    
    def __init__(self, exiftool_cmd: str = "exiftool", altitude_threshold: float = 10.0):
        """
        Initialize the altitude extractor.
        
        Args:
            exiftool_cmd: Path to exiftool executable (default: "exiftool")
            altitude_threshold: Threshold for altitude change detection in meters (default: 10.0)
        """
        self.exiftool_cmd = exiftool_cmd
        self.altitude_threshold = altitude_threshold
        self._verify_exiftool()
    
    def _verify_exiftool(self) -> None:
        """Verify that exiftool is available."""
        try:
            subprocess.run(
                [self.exiftool_cmd, "-ver"],
                capture_output=True,
                check=True
            )
            logger.info(f"Exiftool found: {self.exiftool_cmd}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.error(f"Exiftool not found at: {self.exiftool_cmd}")
            raise RuntimeError(
                f"Exiftool not found. Please install it or provide the correct path.\n"
                f"Ubuntu/Debian: sudo apt install libimage-exiftool-perl\n"
                f"macOS: brew install exiftool\n"
                f"Windows: download from https://exiftool.org/"
            )
    
    def extract_altitude(self, image_path: str) -> Optional[float]:
        """
        Extract altitude from a single image.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Altitude in meters, or None if not available
        """
        try:
            command = [
                self.exiftool_cmd,
                '-j',
                '-GPSAltitude',
                '-AbsoluteAltitude',
                image_path
            ]
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout.strip()
            if not output:
                logger.debug(f"No EXIF data for: {image_path}")
                return None
            
            metadata_list = json.loads(output)
            if not metadata_list:
                return None
            
            metadata = metadata_list[0]
            altitude = metadata.get('GPSAltitude') or metadata.get('AbsoluteAltitude')
            
            # Parse altitude value
            if isinstance(altitude, str):
                # Extract first number (including decimals)
                match = re.search(r"[-+]?\d*\.\d+|\d+", altitude)
                if match:
                    return float(match.group())
            elif isinstance(altitude, (int, float)):
                return float(altitude)
            
            return None
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Error processing {image_path}: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON from exiftool: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error with {image_path}: {e}")
            return None
    
    def process_directory(
        self,
        directory: str,
        file_extensions: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Process all images in a directory and extract altitude data.
        
        Args:
            directory: Path to directory containing images
            file_extensions: List of file extensions to process (default: ['.jpg', '.tif', '.tiff'])
            
        Returns:
            DataFrame with columns: Archivo, Altitud (m), Estado
        """
        if file_extensions is None:
            file_extensions = ['.jpg', '.jpeg', '.tif', '.tiff']
        
        # Normalize extensions to lowercase
        file_extensions = [ext.lower() for ext in file_extensions]
        
        # Get all image files
        files = sorted([
            f for f in os.listdir(directory)
            if os.path.splitext(f.lower())[1] in file_extensions
        ])
        
        if not files:
            logger.warning(f"No image files found in {directory}")
            return pd.DataFrame(columns=["Archivo", "Altitud (m)", "Estado"])
        
        logger.info(f"Processing {len(files)} images from {directory}")
        
        results = []
        previous_altitude = None
        
        for filename in files:
            filepath = os.path.join(directory, filename)
            altitude = self.extract_altitude(filepath)
            
            # Determine status
            if altitude is not None and previous_altitude is not None:
                altitude_change = abs(altitude - previous_altitude)
                status = (
                    f"Cambio >{int(self.altitude_threshold)}m"
                    if altitude_change > self.altitude_threshold
                    else "OK"
                )
            else:
                status = (
                    "Sin comparación"
                    if previous_altitude is None
                    else "Altitud no disponible"
                )
            
            # Store result
            altitude_data = AltitudeData(
                filename=filename,
                altitude=altitude,
                status=status
            )
            results.append(altitude_data.to_dict())
            
            # Update previous altitude
            if altitude is not None:
                previous_altitude = altitude
        
        return pd.DataFrame(results)
    
    def generate_report(
        self,
        df: pd.DataFrame,
        output_file: Optional[str] = None
    ) -> str:
        """
        Generate a text report from altitude data.
        
        Args:
            df: DataFrame with altitude data
            output_file: Optional path to save report (if None, returns as string)
            
        Returns:
            Report as string
        """
        report_lines = [
            "=" * 70,
            "ALTITUDE ANALYSIS REPORT",
            "=" * 70,
            f"\nTotal images processed: {len(df)}",
        ]
        
        # Count by status
        status_counts = df['Estado'].value_counts()
        report_lines.append("\nStatus summary:")
        for status, count in status_counts.items():
            report_lines.append(f"  {status}: {count}")
        
        # Altitude statistics
        valid_altitudes = df[df['Altitud (m)'] != "No disponible"]['Altitud (m)']
        if len(valid_altitudes) > 0:
            report_lines.extend([
                "\nAltitude statistics:",
                f"  Minimum: {valid_altitudes.min():.2f} m",
                f"  Maximum: {valid_altitudes.max():.2f} m",
                f"  Average: {valid_altitudes.mean():.2f} m",
                f"  Std Dev: {valid_altitudes.std():.2f} m",
            ])
        
        report_lines.extend([
            "\n" + "=" * 70,
            "\nDetailed results:\n",
            df.to_string(index=False),
            "\n" + "=" * 70,
        ])
        
        report = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to: {output_file}")
        
        return report


# Convenience functions for backward compatibility
def extract_altitude_from_image(image_path: str, exiftool_cmd: str = "exiftool") -> Optional[float]:
    """
    Extract altitude from a single image (convenience function).
    
    Args:
        image_path: Path to image file
        exiftool_cmd: Path to exiftool executable
        
    Returns:
        Altitude in meters, or None if not available
    """
    extractor = AltitudeExtractor(exiftool_cmd=exiftool_cmd)
    return extractor.extract_altitude(image_path)


def process_directory(
    directory: str,
    exiftool_cmd: str = "exiftool",
    altitude_threshold: float = 10.0
) -> pd.DataFrame:
    """
    Process all images in a directory (convenience function).
    
    Args:
        directory: Path to directory containing images
        exiftool_cmd: Path to exiftool executable
        altitude_threshold: Threshold for altitude change detection in meters
        
    Returns:
        DataFrame with altitude data
    """
    extractor = AltitudeExtractor(
        exiftool_cmd=exiftool_cmd,
        altitude_threshold=altitude_threshold
    )
    return extractor.process_directory(directory)


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Extract and analyze GPS altitude from images"
    )
    parser.add_argument(
        "directory",
        help="Path to directory containing images"
    )
    parser.add_argument(
        "--exiftool",
        default="exiftool",
        help="Path to exiftool executable (default: exiftool)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=10.0,
        help="Altitude change threshold in meters (default: 10.0)"
    )
    parser.add_argument(
        "--output",
        help="Save report to file (optional)"
    )
    parser.add_argument(
        "--export-csv",
        help="Export results to CSV file (optional)"
    )
    
    args = parser.parse_args()
    
    # Validate directory
    directory = os.path.abspath(args.directory)
    if not os.path.isdir(directory):
        logger.error(f"Invalid directory: {directory}")
        return 1
    
    # Process images
    extractor = AltitudeExtractor(
        exiftool_cmd=args.exiftool,
        altitude_threshold=args.threshold
    )
    
    df = extractor.process_directory(directory)
    
    # Generate report
    report = extractor.generate_report(df, output_file=args.output)
    print(report)
    
    # Export to CSV if requested
    if args.export_csv:
        df.to_csv(args.export_csv, index=False)
        logger.info(f"Data exported to: {args.export_csv}")
    
    return 0


if __name__ == "__main__":
    exit(main())
