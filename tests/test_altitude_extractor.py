#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for the altitude_extractor module.

Run with: pytest tests/test_altitude_extractor.py
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

from multispectral_toolkit.core import (
    AltitudeExtractor,
    extract_altitude_from_image,
    process_directory
)


class TestAltitudeExtractor:
    """Test suite for AltitudeExtractor class."""
    
    def test_initialization_default(self):
        """Test default initialization."""
        extractor = AltitudeExtractor()
        assert extractor.exiftool_cmd == "exiftool"
        assert extractor.altitude_threshold == 10.0
    
    def test_initialization_custom(self):
        """Test custom initialization."""
        extractor = AltitudeExtractor(
            exiftool_cmd="/usr/bin/exiftool",
            altitude_threshold=15.0
        )
        assert extractor.exiftool_cmd == "/usr/bin/exiftool"
        assert extractor.altitude_threshold == 15.0
    
    @patch('subprocess.run')
    def test_extract_altitude_success(self, mock_run):
        """Test successful altitude extraction."""
        # Mock exiftool output
        mock_run.return_value = Mock(
            stdout=json.dumps([{"GPSAltitude": "549.7 m"}]),
            returncode=0
        )
        
        extractor = AltitudeExtractor()
        altitude = extractor.extract_altitude("test_image.jpg")
        
        assert altitude == 549.7
    
    @patch('subprocess.run')
    def test_extract_altitude_numeric(self, mock_run):
        """Test altitude extraction with numeric value."""
        mock_run.return_value = Mock(
            stdout=json.dumps([{"GPSAltitude": 549.7}]),
            returncode=0
        )
        
        extractor = AltitudeExtractor()
        altitude = extractor.extract_altitude("test_image.jpg")
        
        assert altitude == 549.7
    
    @patch('subprocess.run')
    def test_extract_altitude_no_data(self, mock_run):
        """Test altitude extraction with no data."""
        mock_run.return_value = Mock(stdout="", returncode=0)
        
        extractor = AltitudeExtractor()
        altitude = extractor.extract_altitude("test_image.jpg")
        
        assert altitude is None
    
    @patch('subprocess.run')
    def test_extract_altitude_error(self, mock_run):
        """Test altitude extraction with subprocess error."""
        mock_run.side_effect = FileNotFoundError()
        
        extractor = AltitudeExtractor()
        altitude = extractor.extract_altitude("test_image.jpg")
        
        assert altitude is None
    
    @patch('os.listdir')
    @patch.object(AltitudeExtractor, 'extract_altitude')
    def test_process_directory(self, mock_extract, mock_listdir):
        """Test directory processing."""
        # Mock file list
        mock_listdir.return_value = ["img1.jpg", "img2.jpg", "img3.tif"]
        
        # Mock altitude extraction
        mock_extract.side_effect = [100.0, 105.0, 120.0]
        
        extractor = AltitudeExtractor(altitude_threshold=10.0)
        df = extractor.process_directory("/fake/path")
        
        assert len(df) == 3
        assert "Archivo" in df.columns
        assert "Altitud (m)" in df.columns
        assert "Estado" in df.columns
    
    def test_altitude_data_class(self):
        """Test AltitudeData dataclass."""
        from multispectral_toolkit.core.altitude_extractor import AltitudeData
        
        data = AltitudeData(
            filename="test.jpg",
            altitude=100.5,
            status="OK"
        )
        
        result = data.to_dict()
        assert result["Archivo"] == "test.jpg"
        assert result["Altitud (m)"] == 100.5
        assert result["Estado"] == "OK"
    
    def test_generate_report(self):
        """Test report generation."""
        # Create sample dataframe
        df = pd.DataFrame({
            "Archivo": ["img1.jpg", "img2.jpg"],
            "Altitud (m)": [100.5, 105.2],
            "Estado": ["Sin comparación", "OK"]
        })
        
        extractor = AltitudeExtractor()
        report = extractor.generate_report(df)
        
        assert "ALTITUDE ANALYSIS REPORT" in report
        assert "Total images processed: 2" in report
        assert "img1.jpg" in report


class TestConvenienceFunctions:
    """Test convenience functions."""
    
    @patch.object(AltitudeExtractor, 'extract_altitude')
    def test_extract_altitude_from_image(self, mock_extract):
        """Test extract_altitude_from_image convenience function."""
        mock_extract.return_value = 100.0
        
        altitude = extract_altitude_from_image("test.jpg")
        assert altitude == 100.0
    
    @patch.object(AltitudeExtractor, 'process_directory')
    def test_process_directory_convenience(self, mock_process):
        """Test process_directory convenience function."""
        mock_df = pd.DataFrame({"Archivo": ["test.jpg"]})
        mock_process.return_value = mock_df
        
        df = process_directory("/fake/path")
        assert len(df) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
