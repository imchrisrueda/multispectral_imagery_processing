#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Batch Altitude Processing
===================================

This example demonstrates how to process multiple directories
of images and generate consolidated reports.

Usage:
    python examples/altitude_batch_processing.py
"""

import os
from pathlib import Path
from multispectral_toolkit.core import AltitudeExtractor


def process_multiple_flights(flight_directories, output_dir="results"):
    """
    Process multiple flight directories and generate reports.
    
    Args:
        flight_directories: List of directories containing flight images
        output_dir: Directory to save results
    """
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Initialize extractor
    extractor = AltitudeExtractor(altitude_threshold=15.0)
    
    # Process each directory
    results_summary = []
    
    for flight_dir in flight_directories:
        flight_name = Path(flight_dir).name
        print(f"\n{'=' * 60}")
        print(f"Processing: {flight_name}")
        print(f"{'=' * 60}")
        
        # Process directory
        df = extractor.process_directory(flight_dir)
        
        if len(df) == 0:
            print(f"No images found in {flight_dir}")
            continue
        
        # Generate report
        report = extractor.generate_report(df)
        
        # Save CSV
        csv_path = output_path / f"{flight_name}_altitude.csv"
        df.to_csv(csv_path, index=False)
        print(f"✓ CSV saved: {csv_path}")
        
        # Save report
        report_path = output_path / f"{flight_name}_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Report saved: {report_path}")
        
        # Add to summary
        valid_altitudes = df[df['Altitud (m)'] != "No disponible"]['Altitud (m)']
        results_summary.append({
            'Flight': flight_name,
            'Total Images': len(df),
            'Valid Altitudes': len(valid_altitudes),
            'Min Altitude': valid_altitudes.min() if len(valid_altitudes) > 0 else None,
            'Max Altitude': valid_altitudes.max() if len(valid_altitudes) > 0 else None,
            'Avg Altitude': valid_altitudes.mean() if len(valid_altitudes) > 0 else None,
        })
    
    # Print summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING SUMMARY")
    print("=" * 60)
    
    for summary in results_summary:
        print(f"\n{summary['Flight']}:")
        print(f"  Total images: {summary['Total Images']}")
        print(f"  Valid altitudes: {summary['Valid Altitudes']}")
        if summary['Min Altitude'] is not None:
            print(f"  Altitude range: {summary['Min Altitude']:.2f} - {summary['Max Altitude']:.2f} m")
            print(f"  Average altitude: {summary['Avg Altitude']:.2f} m")
    
    print("\n✅ All flights processed successfully!")


def main():
    """Main function."""
    # Example flight directories
    # Replace with your actual directories
    flight_directories = [
        "/path/to/flight_001",
        "/path/to/flight_002",
        "/path/to/flight_003",
    ]
    
    # Check if directories exist
    valid_dirs = [d for d in flight_directories if os.path.isdir(d)]
    
    if not valid_dirs:
        print("No valid directories found!")
        print("\nPlease update the flight_directories list with actual paths.")
        print("\nExample usage:")
        print("  flight_directories = [")
        print('      "/data/2025-11-06/flight_001",')
        print('      "/data/2025-11-06/flight_002",')
        print("  ]")
        return
    
    # Process flights
    process_multiple_flights(valid_dirs)


if __name__ == "__main__":
    main()
