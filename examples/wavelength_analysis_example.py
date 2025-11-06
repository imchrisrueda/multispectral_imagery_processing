#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Wavelength Analysis
=============================

This example demonstrates wavelength analysis for multispectral images,
including CWL and FWHM extraction and visualization.

Usage:
    python examples/wavelength_analysis_example.py
"""

import os
from pathlib import Path
from multispectral_toolkit.core import WavelengthAnalyzer
import matplotlib.pyplot as plt


def analyze_single_image(image_path, save_plot=True):
    """
    Analyze a single image and display results.
    
    Args:
        image_path: Path to image file
        save_plot: Whether to save the plot
    """
    print(f"\nAnalyzing: {image_path}")
    print("-" * 60)
    
    analyzer = WavelengthAnalyzer()
    
    # Extract metadata
    metadata = analyzer.extract_metadata(image_path)
    print(f"Metadata fields found: {len(metadata)}")
    
    # Extract CWL and FWHM
    cwl, fwhm = analyzer.extract_cwl_fwhm(metadata)
    
    if cwl is not None:
        print(f"✓ Center Wavelength (CWL): {cwl:.2f} nm")
    else:
        print("✗ Center Wavelength not found")
    
    if fwhm is not None:
        print(f"✓ FWHM: {fwhm:.2f} nm")
    else:
        print("✗ FWHM not found")
    
    # Plot if CWL available
    if cwl is not None:
        output_path = None
        if save_plot:
            output_name = Path(image_path).stem + "_wavelength.png"
            output_path = output_name
        
        analyzer.plot_wavelength(
            image_path,
            save_path=output_path,
            show=False
        )
        
        if save_plot:
            print(f"✓ Plot saved: {output_path}")
    
    return cwl, fwhm


def analyze_multispectral_bands(directory, band_pattern="_*.tif"):
    """
    Analyze all bands in a multispectral image set.
    
    Args:
        directory: Directory containing band images
        band_pattern: Pattern for band files
    """
    print("\n" + "=" * 70)
    print("MULTISPECTRAL BAND ANALYSIS")
    print("=" * 70)
    
    analyzer = WavelengthAnalyzer()
    dir_path = Path(directory)
    
    # Find all band images
    band_files = sorted(dir_path.glob(f"*{band_pattern}"))
    
    if not band_files:
        print(f"No files matching pattern '{band_pattern}' found in {directory}")
        return
    
    print(f"\nFound {len(band_files)} band images")
    
    # Analyze each band
    results = []
    for band_file in band_files:
        band_name = band_file.stem
        cwl, fwhm = analyzer.analyze_image(str(band_file))
        
        results.append({
            'Band': band_name,
            'File': band_file.name,
            'CWL': cwl,
            'FWHM': fwhm
        })
        
        status = "✓" if cwl is not None else "✗"
        cwl_str = f"{cwl:.2f} nm" if cwl is not None else "Not found"
        fwhm_str = f"{fwhm:.2f} nm" if fwhm is not None else "Not found"
        
        print(f"\n{status} {band_name}:")
        print(f"   CWL: {cwl_str}")
        print(f"   FWHM: {fwhm_str}")
    
    # Create comparison plot
    valid_results = [r for r in results if r['CWL'] is not None]
    
    if len(valid_results) > 1:
        create_band_comparison_plot(valid_results, directory)


def create_band_comparison_plot(results, output_dir):
    """
    Create a comparison plot of multiple bands.
    
    Args:
        results: List of result dictionaries
        output_dir: Directory to save the plot
    """
    analyzer = WavelengthAnalyzer()
    
    plt.figure(figsize=(12, 6))
    
    colors = plt.cm.rainbow([i / len(results) for i in range(len(results))])
    
    for result, color in zip(results, colors):
        cwl = result['CWL']
        fwhm = result['FWHM']
        
        wl, resp = analyzer.gaussian_from_fwhm(cwl, fwhm)
        
        label = f"{result['Band']} ({cwl:.1f} nm)"
        plt.plot(wl, resp, label=label, color=color, linewidth=2)
    
    plt.xlabel("Wavelength (nm)", fontsize=12)
    plt.ylabel("Relative Response", fontsize=12)
    plt.title("Multispectral Band Comparison", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(loc="upper right")
    plt.xlim(350, 1000)
    plt.ylim(0, 1.05)
    plt.tight_layout()
    
    output_path = Path(output_dir) / "band_comparison.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"\n✓ Comparison plot saved: {output_path}")
    plt.close()


def main():
    """Main function."""
    print("=" * 70)
    print("WAVELENGTH ANALYSIS EXAMPLES")
    print("=" * 70)
    
    # Example 1: Single image analysis
    print("\n" + "=" * 70)
    print("Example 1: Single Image Analysis")
    print("=" * 70)
    
    example_image = "/path/to/image_1.tif"
    
    if os.path.exists(example_image):
        analyze_single_image(example_image)
    else:
        print(f"\nImage not found: {example_image}")
        print("Please update the example_image path with an actual image file.")
    
    # Example 2: Multispectral band analysis
    print("\n" + "=" * 70)
    print("Example 2: Multispectral Band Analysis")
    print("=" * 70)
    
    example_directory = "/path/to/multispectral/images"
    
    if os.path.isdir(example_directory):
        analyze_multispectral_bands(example_directory)
    else:
        print(f"\nDirectory not found: {example_directory}")
        print("Please update the example_directory path.")
    
    # Example 3: Manual wavelength plotting
    print("\n" + "=" * 70)
    print("Example 3: Manual Wavelength Specification")
    print("=" * 70)
    
    print("\nPlotting with manual parameters...")
    analyzer = WavelengthAnalyzer()
    
    # Create plots for common wavelengths
    wavelengths = [
        (475, 20, "Blue"),
        (560, 20, "Green"),
        (668, 10, "Red"),
        (840, 40, "NIR"),
    ]
    
    plt.figure(figsize=(12, 6))
    
    for cwl, fwhm, name in wavelengths:
        wl, resp = analyzer.gaussian_from_fwhm(cwl, fwhm)
        plt.plot(wl, resp, label=f"{name} ({cwl} nm, FWHM={fwhm} nm)", linewidth=2)
    
    plt.xlabel("Wavelength (nm)", fontsize=12)
    plt.ylabel("Relative Response", fontsize=12)
    plt.title("Example Spectral Bands", fontsize=14)
    plt.grid(True, linestyle="--", alpha=0.7)
    plt.legend(loc="upper right")
    plt.xlim(400, 900)
    plt.ylim(0, 1.05)
    plt.tight_layout()
    
    output_path = "example_bands.png"
    plt.savefig(output_path, dpi=150, bbox_inches='tight')
    print(f"✓ Example plot saved: {output_path}")
    plt.close()
    
    print("\n✅ All examples completed!")


if __name__ == "__main__":
    main()
