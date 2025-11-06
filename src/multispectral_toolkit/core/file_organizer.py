#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multispectral File Organizer
=============================

Organizes multispectral image files from RED and BLUE camera folders
into a clean, structured directory layout.

Target structure:
    - photos/: Regular images (non-calibration)
    - calibration/: Calibration images (IMG_0000_1 through IMG_0000_11)
    - dat_files/: All .dat metadata files
    - discard_images/: Images to be discarded

Author: Christian Rueda
Date: August 2025
License: MIT
"""

import os
import shutil
import re
from pathlib import Path
from typing import List, Tuple, Optional
import logging

# Configure logging
logger = logging.getLogger(__name__)


class MultispectralOrganizer:
    """
    Organizes multispectral image files from MicaSense camera systems.
    
    Handles the organization of RED and BLUE channel folders into a
    structured directory layout with separate folders for photos,
    calibration images, and metadata files.
    """
    
    # Calibration pattern: IMG_0000_1.* through IMG_0000_11.*
    CALIBRATION_PATTERN = re.compile(r'IMG_0000_([1-9]|1[01])\..*')
    
    # Common image extensions
    IMAGE_EXTENSIONS = [
        '*.jpg', '*.jpeg', '*.png', '*.tiff', '*.tif', '*.bmp', '*.raw'
    ]
    
    def __init__(self, base_directory: str = "."):
        """
        Initialize the organizer.

        Args:
            base_directory: Base directory containing RED and BLUE folders
        """
        self.base_dir = Path(base_directory).resolve()
        self.red_dir = self.base_dir / "RED"
        self.blue_dir = self.base_dir / "BLUE"

        # Target directories
        self.photos_dir = self.base_dir / "photos"
        self.calibration_dir = self.base_dir / "calibration"
        self.dat_files_dir = self.base_dir / "dat_files"
        self.discard_images_dir = self.base_dir / "discard_images"

        self._setup_logging()
        logger.info(f"Initializing organizer in: {self.base_dir}")

    def _setup_logging(self) -> None:
        """Configure logging to file in base directory."""
        log_file = self.base_dir / "file_organizer.log"
        
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add new handlers
        file_handler = logging.FileHandler(log_file, mode='w', encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)
    
    def validate_structure(self) -> bool:
        """
        Validate that RED and BLUE folders exist.
        
        Returns:
            True if structure is valid, False otherwise
        """
        if not self.red_dir.exists():
            logger.error(f"RED folder not found: {self.red_dir}")
            return False
        
        if not self.blue_dir.exists():
            logger.error(f"BLUE folder not found: {self.blue_dir}")
            return False
        
        logger.info("✓ Folder structure validated successfully")
        return True
    
    def create_destination_folders(self) -> None:
        """Create target directories if they don't exist."""
        folders = [
            self.photos_dir,
            self.calibration_dir,
            self.dat_files_dir,
            self.discard_images_dir
        ]
        
        for folder in folders:
            if folder.exists():
                logger.warning(
                    f"Folder {folder.name} already exists. "
                    "Existing content will be preserved."
                )
            else:
                folder.mkdir(exist_ok=True)
                logger.info(f"✓ Created folder: {folder.name}")
    
    def get_all_images(self, source_dir: Path) -> List[Path]:
        """
        Get all image files from numbered subdirectories.
        
        Args:
            source_dir: Source directory (RED or BLUE)
            
        Returns:
            List of image file paths
        """
        images = []
        
        # Find numbered subdirectories (000, 001, 002, etc.)
        subdirs = [
            d for d in source_dir.iterdir()
            if d.is_dir() and d.name.isdigit()
        ]
        subdirs.sort()
        
        # Find all images in subdirectories
        for subdir in subdirs:
            for ext in self.IMAGE_EXTENSIONS:
                images.extend(subdir.glob(ext))
                images.extend(subdir.glob(ext.upper()))
        
        logger.info(f"Found {len(images)} images in {source_dir.name}")
        return images
    
    def is_calibration_image(self, image_path: Path) -> bool:
        """
        Check if an image is a calibration image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            True if it's a calibration image
        """
        return bool(self.CALIBRATION_PATTERN.match(image_path.name))
    
    def organize_images(self) -> Tuple[int, int]:
        """
        Organize images into appropriate folders.
        
        Returns:
            Tuple of (regular_count, calibration_count)
        """
        regular_count = 0
        calibration_count = 0
        
        for source_folder in [self.red_dir, self.blue_dir]:
            if not source_folder.exists():
                continue
            
            images = self.get_all_images(source_folder)
            
            for image_path in images:
                try:
                    if self.is_calibration_image(image_path):
                        # Calibration image
                        dest_path = self.calibration_dir / image_path.name
                        shutil.copy2(image_path, dest_path)
                        calibration_count += 1
                        logger.debug(
                            f"Calibration: {image_path.name} → calibration/"
                        )
                    else:
                        # Regular image
                        dest_path = self.photos_dir / image_path.name
                        shutil.copy2(image_path, dest_path)
                        regular_count += 1
                        logger.debug(
                            f"Regular: {image_path.name} → photos/"
                        )
                        
                except Exception as e:
                    logger.error(f"Error processing {image_path}: {e}")
        
        return regular_count, calibration_count
    
    def organize_dat_files(self) -> int:
        """
        Move all .dat files to dat_files directory.
        
        Returns:
            Number of .dat files processed
        """
        dat_files = list(self.base_dir.rglob("*.dat"))
        dat_count = 0
        
        for dat_file in dat_files:
            # Skip if already in target directory
            if dat_file.parent == self.dat_files_dir:
                continue
            
            try:
                dest_path = self.dat_files_dir / dat_file.name
                shutil.move(str(dat_file), str(dest_path))
                dat_count += 1
                logger.debug(f"DAT: {dat_file.name} → dat_files/")
            except Exception as e:
                logger.error(f"Error moving {dat_file}: {e}")
        
        return dat_count
    
    def cleanup_empty_folders(self) -> None:
        """Remove RED and BLUE folders if empty after organization."""
        folders_to_check = [self.red_dir, self.blue_dir]
        
        for folder in folders_to_check:
            if not folder.exists():
                continue
            
            try:
                # Check if folder is empty (including subdirectories)
                if not any(folder.rglob('*')):
                    shutil.rmtree(folder)
                    logger.info(f"✓ Removed empty folder: {folder.name}")
                else:
                    logger.info(
                        f"Folder {folder.name} is not empty, keeping it"
                    )
            except Exception as e:
                logger.warning(f"Could not remove {folder.name}: {e}")
    
    def generate_report(
        self,
        regular_images: int,
        calibration_images: int,
        dat_files: int
    ) -> str:
        """
        Generate organization report.
        
        Args:
            regular_images: Number of regular images processed
            calibration_images: Number of calibration images processed
            dat_files: Number of .dat files processed
            
        Returns:
            Report as string
        """
        report_lines = [
            "",
            "=" * 60,
            "ORGANIZATION REPORT",
            "=" * 60,
            f"📁 Regular images processed: {regular_images}",
            f"🔧 Calibration images processed: {calibration_images}",
            f"📄 DAT files processed: {dat_files}",
            f"📍 Base directory: {self.base_dir}",
            "",
            "Final structure:",
            f"├── photos/ ({regular_images} files)",
            f"├── calibration/ ({calibration_images} files)",
            f"├── dat_files/ ({dat_files} files)",
            f"└── discard_images/",
            "=" * 60,
        ]
        
        # Calibration check
        if calibration_images < 11:
            report_lines.append(
                f"⚠️  WARNING: Expected 11 calibration images, "
                f"found only {calibration_images}"
            )
        elif calibration_images == 11:
            report_lines.append(
                "✅ All expected calibration images found (11)"
            )
        
        return "\n".join(report_lines)
    
    def run(self, cleanup: bool = True) -> bool:
        """
        Execute the complete organization process.
        
        Args:
            cleanup: Whether to remove empty source folders
            
        Returns:
            True if successful, False otherwise
        """
        try:
            print("Starting multispectral file organization...")
            
            # Validate structure
            if not self.validate_structure():
                return False
            
            # Create target folders
            self.create_destination_folders()
            
            # Organize images
            print("Organizing images...")
            regular_count, calibration_count = self.organize_images()
            
            # Organize .dat files
            print("Organizing .dat files...")
            dat_count = self.organize_dat_files()
            
            # Cleanup (optional)
            if cleanup:
                print("Cleaning up empty folders...")
                self.cleanup_empty_folders()
            
            # Generate and print report
            report = self.generate_report(
                regular_count,
                calibration_count,
                dat_count
            )
            print(report)
            
            print("✅ Organization completed successfully!")
            print(f"\nDetails logged to: {self.base_dir / 'file_organizer.log'}")
            return True
            
        except Exception as e:
            logger.error(f"Error during organization: {e}", exc_info=True)
            print(f"❌ Error: {e}")
            return False


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Organize multispectral images from MicaSense cameras"
    )
    parser.add_argument(
        "directory",
        nargs='?',
        default=".",
        help="Base directory containing RED and BLUE folders (default: current directory)"
    )
    parser.add_argument(
        "--no-cleanup",
        action="store_true",
        help="Don't remove empty source folders after organization"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MICASENSE MULTISPECTRAL IMAGE ORGANIZER")
    print("=" * 60)
    
    # Create and run organizer
    organizer = MultispectralOrganizer(args.directory)
    success = organizer.run(cleanup=not args.no_cleanup)
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
