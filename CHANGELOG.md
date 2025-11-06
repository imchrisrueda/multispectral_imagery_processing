# Changelog

All notable changes to the Multispectral Imagery Processing Toolkit will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-06

### Added
- Initial release of Multispectral Imagery Processing Toolkit
- Core altitude extraction module with EXIF metadata parsing
- File organization system for MicaSense RED/BLUE folders
- Wavelength analysis module with CWL and FWHM extraction
- GUI application for altitude analysis (PyQt6)
- Comprehensive API documentation
- Command-line interfaces for all core modules
- Unit test framework with pytest
- Example scripts for common use cases
- Structured project layout following best practices

### Core Features
- **Altitude Extractor**
  - Extract GPS altitude from image EXIF data
  - Detect altitude changes between sequential images
  - Generate comprehensive reports
  - Export results to CSV
  - Support for multiple image formats (.jpg, .tif, .tiff)

- **File Organizer**
  - Automatic organization of RED/BLUE channel folders
  - Calibration image detection and separation
  - DAT file management
  - Empty folder cleanup
  - Detailed logging system

- **Wavelength Analyzer**
  - Center Wavelength (CWL) extraction
  - FWHM (Full Width at Half Maximum) analysis
  - Gaussian response curve generation
  - Spectral characteristic visualization
  - Plot export capabilities

- **GUI Applications**
  - Altitude Analyzer desktop application
  - Real-time progress tracking
  - Support for RGB, Thermal, and Multispectral modes
  - CSV export functionality

### Infrastructure
- Python 3.8+ support
- Modular architecture with clean separation of concerns
- Comprehensive documentation (README, API docs, usage guides)
- Testing framework with pytest
- Continuous integration ready
- MIT License

### Documentation
- Complete README with installation and usage instructions
- API documentation for all modules
- Usage examples for common scenarios
- Contributing guidelines
- Changelog tracking

## [Unreleased]

### Planned Features
- Support for additional camera systems beyond MicaSense
- GPU acceleration for batch processing
- Machine learning-based image classification
- Web-based interface
- Docker containerization
- Cloud storage integration (AWS S3, Google Cloud Storage)
- Advanced filtering and preprocessing tools
- Automated georeferencing
- Integration with GIS platforms

### Known Issues
- None reported yet

---

## Version History

- **1.0.0** (2025-11-06) - Initial public release

## Migration Notes

### From Legacy Scripts
If you're migrating from the original standalone scripts (`multi_check.py`, `altitude_check_app.py`, etc.):

1. **Import Changes**:
   ```python
   # Old
   from multi_check import extraer_altitud_exiftool
   
   # New
   from multispectral_toolkit.core import AltitudeExtractor
   extractor = AltitudeExtractor()
   ```

2. **Command-Line Changes**:
   ```bash
   # Old
   python multi_check.py /path/to/images
   
   # New
   multispectral-altitude /path/to/images
   # or
   python -m multispectral_toolkit.core.altitude_extractor /path/to/images
   ```

3. **File Organization**:
   ```python
   # Old
   from multi_pic_organizer import MultispectralOrganizer
   
   # New (same API)
   from multispectral_toolkit.core import MultispectralOrganizer
   ```

The API remains largely compatible, with improved error handling and documentation.

## Contributing

See [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines on contributing to this project.

## Support

For issues, questions, or feature requests, please open an issue on GitHub:
https://github.com/imchrisrueda/multispectral_imagery_processing/issues
