#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the file_organizer module.

Run with: pytest tests/test_file_organizer.py
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from multispectral_toolkit.core import MultispectralOrganizer


class TestMultispectralOrganizer:
    """Test suite for MultispectralOrganizer class."""
    
    def test_initialization(self):
        """Test initialization with default directory."""
        organizer = MultispectralOrganizer(".")
        
        assert organizer.base_dir == Path(".").resolve()
        assert organizer.red_dir == organizer.base_dir / "RED"
        assert organizer.blue_dir == organizer.base_dir / "BLUE"
        assert organizer.photos_dir == organizer.base_dir / "photos"
    
    def test_calibration_pattern(self):
        """Test calibration image pattern matching."""
        organizer = MultispectralOrganizer(".")
        
        # Test valid calibration images
        assert organizer.is_calibration_image(Path("IMG_0000_1.tif"))
        assert organizer.is_calibration_image(Path("IMG_0000_5.tif"))
        assert organizer.is_calibration_image(Path("IMG_0000_11.tif"))
        
        # Test invalid calibration images
        assert not organizer.is_calibration_image(Path("IMG_0000_0.tif"))
        assert not organizer.is_calibration_image(Path("IMG_0000_12.tif"))
        assert not organizer.is_calibration_image(Path("IMG_0001_1.tif"))
        assert not organizer.is_calibration_image(Path("IMG_0000_1_band.tif"))
    
    @patch.object(Path, 'exists')
    def test_validate_structure_success(self, mock_exists):
        """Test structure validation with valid structure."""
        mock_exists.return_value = True
        
        organizer = MultispectralOrganizer(".")
        result = organizer.validate_structure()
        
        assert result is True
    
    @patch.object(Path, 'exists')
    def test_validate_structure_missing_red(self, mock_exists):
        """Test structure validation with missing RED folder."""
        def side_effect(path):
            return "BLUE" in str(path)
        
        mock_exists.side_effect = side_effect
        organizer = MultispectralOrganizer(".")
        result = organizer.validate_structure()
        
        assert result is False
    
    def test_get_all_images(self):
        """Test image file discovery."""
        # Create temporary directory structure
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create subdirectories
            subdir = tmppath / "000"
            subdir.mkdir()
            
            # Create test files
            (subdir / "test1.tif").touch()
            (subdir / "test2.jpg").touch()
            (subdir / "test3.txt").touch()  # Should be ignored
            
            organizer = MultispectralOrganizer(tmpdir)
            images = organizer.get_all_images(tmppath)
            
            # Should find 2 images, not the .txt file
            assert len(images) == 2
            assert all(img.suffix.lower() in ['.tif', '.jpg'] for img in images)
    
    def test_organize_images_logic(self):
        """Test image organization logic without actual file operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create structure
            red_dir = tmppath / "RED" / "000"
            red_dir.mkdir(parents=True)
            
            # Create test images
            (red_dir / "IMG_0000_1.tif").touch()  # Calibration
            (red_dir / "IMG_0001_1.tif").touch()  # Regular
            
            organizer = MultispectralOrganizer(tmpdir)
            organizer.create_destination_folders()
            
            # Test calibration detection
            assert organizer.is_calibration_image(Path("IMG_0000_1.tif"))
            assert not organizer.is_calibration_image(Path("IMG_0001_1.tif"))
    
    def test_generate_report(self):
        """Test report generation."""
        organizer = MultispectralOrganizer(".")
        report = organizer.generate_report(
            regular_images=100,
            calibration_images=11,
            dat_files=5
        )
        
        assert "ORGANIZATION REPORT" in report
        assert "100" in report  # Regular images
        assert "11" in report   # Calibration images
        assert "5" in report    # DAT files
        assert "All expected calibration images found" in report


class TestFileOperations:
    """Test file operations with temporary directories."""
    
    def test_full_organization_flow(self):
        """Test complete organization flow with temporary files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create structure
            red_000 = tmppath / "RED" / "000"
            blue_000 = tmppath / "BLUE" / "000"
            red_000.mkdir(parents=True)
            blue_000.mkdir(parents=True)
            
            # Create test files
            (red_000 / "IMG_0000_1.tif").touch()   # Calibration
            (red_000 / "IMG_0001_1.tif").touch()   # Regular
            (blue_000 / "IMG_0000_2.tif").touch()  # Calibration
            (tmppath / "test.dat").touch()          # DAT file
            
            # Run organizer
            organizer = MultispectralOrganizer(tmpdir)
            organizer.create_destination_folders()
            regular, calib = organizer.organize_images()
            dat_count = organizer.organize_dat_files()
            
            # Verify results
            assert regular == 1
            assert calib == 2
            assert dat_count == 1
            
            # Verify files were copied
            assert (tmppath / "photos" / "IMG_0001_1.tif").exists()
            assert (tmppath / "calibration" / "IMG_0000_1.tif").exists()
            assert (tmppath / "calibration" / "IMG_0000_2.tif").exists()
            assert (tmppath / "dat_files" / "test.dat").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
