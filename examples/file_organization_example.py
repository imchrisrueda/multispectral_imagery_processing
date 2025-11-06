#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: File Organization
===========================

This example demonstrates how to organize multispectral image files
from MicaSense camera RED and BLUE folders.

Usage:
    python examples/file_organization_example.py /path/to/base/directory
"""

import sys
import os
from multispectral_toolkit.core import MultispectralOrganizer


def organize_with_custom_logging(base_directory):
    """
    Organize files with detailed logging.
    
    Args:
        base_directory: Base directory containing RED and BLUE folders
    """
    print("=" * 70)
    print("MULTISPECTRAL IMAGE ORGANIZATION EXAMPLE")
    print("=" * 70)
    print(f"\nBase directory: {base_directory}")
    
    # Create organizer
    organizer = MultispectralOrganizer(base_directory)
    
    # Validate structure before proceeding
    print("\n1. Validating directory structure...")
    if not organizer.validate_structure():
        print("❌ Invalid directory structure!")
        print("\nExpected structure:")
        print("  base_directory/")
        print("  ├── RED/")
        print("  │   ├── 000/")
        print("  │   ├── 001/")
        print("  │   └── ...")
        print("  └── BLUE/")
        print("      ├── 000/")
        print("      ├── 001/")
        print("      └── ...")
        return False
    
    # Create destination folders
    print("\n2. Creating destination folders...")
    organizer.create_destination_folders()
    
    # Get image counts
    print("\n3. Scanning for images...")
    red_images = organizer.get_all_images(organizer.red_dir) if organizer.red_dir.exists() else []
    blue_images = organizer.get_all_images(organizer.blue_dir) if organizer.blue_dir.exists() else []
    
    total_images = len(red_images) + len(blue_images)
    print(f"   Found {len(red_images)} images in RED folder")
    print(f"   Found {len(blue_images)} images in BLUE folder")
    print(f"   Total: {total_images} images")
    
    if total_images == 0:
        print("\n⚠️  No images found to organize!")
        return False
    
    # Ask for confirmation
    response = input("\nProceed with organization? (y/n): ")
    if response.lower() != 'y':
        print("Operation cancelled.")
        return False
    
    # Organize files
    print("\n4. Organizing images...")
    regular_count, calibration_count = organizer.organize_images()
    
    print("\n5. Organizing .dat files...")
    dat_count = organizer.organize_dat_files()
    
    # Optional cleanup
    response = input("\n6. Remove empty source folders? (y/n): ")
    if response.lower() == 'y':
        organizer.cleanup_empty_folders()
    
    # Generate and display report
    print("\n")
    report = organizer.generate_report(regular_count, calibration_count, dat_count)
    print(report)
    
    print(f"\n📝 Detailed log available at: {organizer.base_dir / 'file_organizer.log'}")
    
    return True


def quick_organize(base_directory, cleanup=True):
    """
    Quick organization without prompts.
    
    Args:
        base_directory: Base directory containing RED and BLUE folders
        cleanup: Whether to remove empty source folders
    """
    organizer = MultispectralOrganizer(base_directory)
    success = organizer.run(cleanup=cleanup)
    return success


def main():
    """Main function."""
    # Get base directory from command line or use current directory
    if len(sys.argv) > 1:
        base_directory = sys.argv[1]
    else:
        base_directory = "."
    
    # Validate directory
    if not os.path.isdir(base_directory):
        print(f"Error: Directory not found: {base_directory}")
        print("\nUsage:")
        print("  python file_organization_example.py [base_directory]")
        print("\nExample:")
        print("  python file_organization_example.py /data/2025-11-06/flight_001")
        return 1
    
    # Choose organization mode
    print("\nOrganization modes:")
    print("  1. Interactive mode (with prompts)")
    print("  2. Quick mode (automatic)")
    
    mode = input("\nSelect mode (1/2) [1]: ").strip() or "1"
    
    if mode == "1":
        success = organize_with_custom_logging(base_directory)
    else:
        success = quick_organize(base_directory)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
