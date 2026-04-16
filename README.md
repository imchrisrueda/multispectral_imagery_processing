# Multispectral Imagery Processing Toolkit

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive toolkit for processing and analyzing multispectral imagery, particularly optimized for MicaSense camera systems.

## 🌟 Features

- **Project Initialization**: Instantly create standardized directory structures for new missions
- **Altitude Extraction**: Extract and analyze GPS altitude data from image EXIF metadata
- **File Organization**: Automatically organize multispectral image files (RED/BLUE channels) into structured directories
- **Wavelength Analysis**: Extract and visualize spectral wavelength characteristics (CWL, FWHM)
- **GUI Applications**: User-friendly desktop applications for altitude analysis
- **Batch Processing**: Process entire directories of images efficiently
- **Export Capabilities**: Export results to CSV, generate reports, and save visualizations

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Modules Overview](#modules-overview)
- [Usage Examples](#usage-examples)
- [Command-Line Tools](#command-line-tools)
- [API Documentation](#api-documentation)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Installation

### Prerequisites

1. **Python 3.8 or higher**
2. **exiftool** - Required for metadata extraction
   - **Ubuntu/Debian**: `sudo apt install libimage-exiftool-perl`
   - **macOS**: `brew install exiftool`
   - **Windows**: Download from [exiftool.org](https://exiftool.org/)

### Install from source

```bash
# Clone the repository
git clone https://github.com/imchrisrueda/multispectral_imagery_processing.git
cd multispectral_imagery_processing

# Install in development mode
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```

### Dependencies

- **Core**: `pandas`, `numpy`, `matplotlib`
- **GUI**: `PyQt6` (optional, for GUI applications)
- **Testing**: `pytest`, `pytest-cov` (optional, for development)

## ⚡ Quick Start

### Altitude Extraction

```python
from multispectral_toolkit.core import AltitudeExtractor

# Initialize extractor
extractor = AltitudeExtractor(altitude_threshold=10.0)

# Process a directory
df = extractor.process_directory("/path/to/images")

# Generate report
report = extractor.generate_report(df)
print(report)

# Export to CSV
df.to_csv("altitude_report.csv", index=False)
```

### File Organization

```python
from multispectral_toolkit.core import MultispectralOrganizer

# Initialize organizer
organizer = MultispectralOrganizer("/path/to/base/directory")

# Run organization
success = organizer.run()
```

### Wavelength Analysis

```python
from multispectral_toolkit.core import WavelengthAnalyzer

# Initialize analyzer
analyzer = WavelengthAnalyzer()

# Analyze an image
cwl, fwhm = analyzer.analyze_image("/path/to/image.tif")
print(f"Center Wavelength: {cwl} nm, FWHM: {fwhm} nm")

# Plot wavelength characteristics
analyzer.plot_wavelength(
    "/path/to/image.tif",
    save_path="wavelength_plot.png"
)
```

## 📦 Modules Overview

### Core Modules (`src/multispectral_toolkit/core/`)

#### 1. **altitude_extractor.py**
- Extract GPS altitude from image EXIF data
- Detect altitude changes between sequential images
- Generate comprehensive reports
- Export data to CSV

#### 2. **file_organizer.py**
- Generate standard flight mission directory structures (`--init-project`)
- Organize RED and BLUE channel folders
- Separate calibration images (IMG_0000_1 through IMG_0000_11)
- Move .dat metadata files
- Clean up empty directories

#### 3. **wavelength_analyzer.py**
- Extract Center Wavelength (CWL) and FWHM from metadata
- Generate Gaussian response curves
- Visualize spectral characteristics
- Plot wavelength distributions

### GUI Modules (`src/multispectral_toolkit/gui/`)

#### 1. **altitude_gui.py**
- Desktop application for altitude analysis
- Real-time progress tracking
- CSV export functionality
- Support for RGB, Thermal, and Multispectral images

## 📚 Usage Examples

### Example 1: Batch Altitude Analysis

```python
from multispectral_toolkit.core import AltitudeExtractor
import os

# Process multiple directories
directories = [
    "/data/flight_001",
    "/data/flight_002",
    "/data/flight_003"
]

extractor = AltitudeExtractor(altitude_threshold=15.0)

for directory in directories:
    print(f"Processing: {directory}")
    df = extractor.process_directory(directory)
    
    # Save results
    output_file = os.path.join(directory, "altitude_report.csv")
    df.to_csv(output_file, index=False)
    print(f"Results saved to: {output_file}")
```

### Example 2: Custom Calibration Detection

```python
from multispectral_toolkit.core import MultispectralOrganizer
import re

class CustomOrganizer(MultispectralOrganizer):
    # Override calibration pattern
    CALIBRATION_PATTERN = re.compile(r'CALIB_\d+\..*')

# Use custom organizer
organizer = CustomOrganizer("/path/to/data")
organizer.run()
```

### Example 3: Wavelength Batch Analysis

```python
from multispectral_toolkit.core import WavelengthAnalyzer
import os

analyzer = WavelengthAnalyzer()
image_dir = "/path/to/multispectral/images"

# Analyze all band 1 images
for filename in os.listdir(image_dir):
    if filename.endswith("_1.tif"):
        image_path = os.path.join(image_dir, filename)
        cwl, fwhm = analyzer.analyze_image(image_path)
        print(f"{filename}: CWL={cwl}nm, FWHM={fwhm}nm")
```

## 🖥️ Command-Line Tools

### Altitude Extraction CLI

```bash
# Basic usage
python -m multispectral_toolkit.core.altitude_extractor /path/to/images

# With custom threshold
python -m multispectral_toolkit.core.altitude_extractor /path/to/images --threshold 15

# Export results
python -m multispectral_toolkit.core.altitude_extractor /path/to/images \
    --export-csv results.csv \
    --output report.txt
```

### File Organizer CLI

```bash
# Create standard project directory structure
python -m multispectral_toolkit.core.file_organizer --init-project /path/to/new_project

# Organize current directory
python -m multispectral_toolkit.core.file_organizer .

# Organize specific directory
python -m multispectral_toolkit.core.file_organizer /path/to/data

# Keep source folders
python -m multispectral_toolkit.core.file_organizer /path/to/data --no-cleanup
```

### Wavelength Analyzer CLI

```bash
# Analyze and display plot
python -m multispectral_toolkit.core.wavelength_analyzer --image image_1.tif

# Save plot without displaying
python -m multispectral_toolkit.core.wavelength_analyzer \
    --image image_1.tif \
    --save wavelength.png \
    --no-show

# Override metadata
python -m multispectral_toolkit.core.wavelength_analyzer \
    --image image_1.tif \
    --wl 475 \
    --fwhm 20
```

### GUI Application

```bash
# Launch altitude analyzer GUI
python altitude_check_app.py
```

## 📖 API Documentation

Full API documentation is available in the `docs/` directory.

### Key Classes

#### AltitudeExtractor
```python
class AltitudeExtractor:
    def __init__(self, exiftool_cmd="exiftool", altitude_threshold=10.0)
    def extract_altitude(self, image_path: str) -> Optional[float]
    def process_directory(self, directory: str) -> pd.DataFrame
    def generate_report(self, df: pd.DataFrame) -> str
```

#### MultispectralOrganizer
```python
class MultispectralOrganizer:
    def __init__(self, base_directory: str = ".")
    def validate_structure(self) -> bool
    def organize_images(self) -> Tuple[int, int]
    def run(self, cleanup: bool = True) -> bool
```

#### WavelengthAnalyzer
```python
class WavelengthAnalyzer:
    def __init__(self, exiftool_cmd: str = "exiftool")
    def analyze_image(self, image_path: str) -> Tuple[Optional[float], Optional[float]]
    def plot_wavelength(self, image_path: str, **kwargs) -> None
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/multispectral_toolkit

# Run specific test file
pytest tests/test_altitude_extractor.py
```

## 📁 Project Structure

```
multispectral_imagery_processing/
├── src/
│   └── multispectral_toolkit/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── altitude_extractor.py
│       │   ├── file_organizer.py
│       │   └── wavelength_analyzer.py
│       ├── gui/
│       │   ├── __init__.py
│       │   └── altitude_gui.py
│       └── utils/
│           └── __init__.py
├── tests/
│   ├── __init__.py
│   ├── test_altitude_extractor.py
│   ├── test_file_organizer.py
│   └── test_wavelength_analyzer.py
├── examples/
│   ├── altitude_batch_processing.py
│   ├── file_organization_example.py
│   └── wavelength_analysis_example.py
├── docs/
│   ├── API.md
│   ├── USAGE.md
│   └── CONTRIBUTING.md
├── config/
│   └── default_config.yaml
├── altitude_check_app.py  (legacy GUI)
├── setup.py
├── pyproject.toml
├── requirements.txt
├── README.md
├── LICENSE
└── CHANGELOG.md
```

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](docs/CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

### Development Setup

```bash
# Clone repository
git clone https://github.com/imchrisrueda/multispectral_imagery_processing.git
cd multispectral_imagery_processing

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Christian Rueda**
- GitHub: [@imchrisrueda](https://github.com/imchrisrueda)

## 🙏 Acknowledgments

- MicaSense for multispectral camera technology
- ExifTool by Phil Harvey for metadata extraction
- The Python scientific computing community

## 📮 Support

For questions, issues, or feature requests, please open an issue on GitHub:
https://github.com/imchrisrueda/multispectral_imagery_processing/issues

## 🗺️ Roadmap

- [ ] Add support for additional camera systems
- [ ] Implement GPU acceleration for batch processing
- [ ] Add machine learning-based image classification
- [ ] Web-based interface
- [ ] Docker containerization
- [ ] Cloud storage integration

---

**Note**: This toolkit is optimized for MicaSense multispectral camera systems but can be adapted for other multispectral imaging platforms.
