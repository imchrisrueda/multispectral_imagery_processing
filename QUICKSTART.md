# Quick Start Guide

## Installation (5 minutes)

### 1. Install System Dependencies

```bash
# Ubuntu/Debian
sudo apt install libimage-exiftool-perl

# macOS
brew install exiftool

# Windows - Download from https://exiftool.org/
```

### 2. Install Python Package

```bash
cd /home/christianrueda/workfiles/Github/multispectral_imagery_processing

# Install in development mode (recommended)
pip install -e .

# Or with all optional dependencies
pip install -e ".[all]"
```

### 3. Verify Installation

```bash
# Check if command-line tools work
multispectral-altitude --help
multispectral-organize --help
multispectral-wavelength --help

# Run tests (optional)
pytest
```

## Common Tasks

### Task 1: Extract Altitude from Images (2 minutes)

```bash
# Quick CLI usage
multispectral-altitude /path/to/images

# With options
multispectral-altitude /path/to/images \
    --threshold 15 \
    --export-csv altitude_results.csv
```

**Python API:**
```python
from multispectral_toolkit.core import AltitudeExtractor

extractor = AltitudeExtractor(altitude_threshold=10.0)
df = extractor.process_directory("/path/to/images")
print(df)
```

### Task 2: Organize MicaSense Files (3 minutes)

```bash
# Navigate to your data directory
cd /path/to/your/flight/data

# Run organizer
multispectral-organize .
```

**Python API:**
```python
from multispectral_toolkit.core import MultispectralOrganizer

organizer = MultispectralOrganizer("/path/to/data")
organizer.run()
```

### Task 3: Analyze Wavelengths (2 minutes)

```bash
# Analyze single image
multispectral-wavelength --image IMG_0001_1.tif --save wavelength.png
```

**Python API:**
```python
from multispectral_toolkit.core import WavelengthAnalyzer

analyzer = WavelengthAnalyzer()
cwl, fwhm = analyzer.analyze_image("IMG_0001_1.tif")
print(f"Center Wavelength: {cwl} nm, FWHM: {fwhm} nm")
```

## Example Workflows

### Workflow 1: Process New Flight Data

```bash
# 1. Organize files
cd /data/flight_2025-11-06
multispectral-organize .

# 2. Extract altitude
multispectral-altitude photos/ --export-csv altitude.csv

# 3. Analyze wavelengths
multispectral-wavelength --image photos/IMG_0001_1.tif
```

### Workflow 2: Batch Process Multiple Flights

```python
from pathlib import Path
from multispectral_toolkit.core import AltitudeExtractor, MultispectralOrganizer

base_dir = Path("/data/flights")
flight_dirs = [d for d in base_dir.iterdir() if d.is_dir()]

for flight_dir in flight_dirs:
    print(f"Processing {flight_dir.name}...")
    
    # Organize
    organizer = MultispectralOrganizer(flight_dir)
    organizer.run()
    
    # Extract altitude
    extractor = AltitudeExtractor()
    df = extractor.process_directory(flight_dir / "photos")
    df.to_csv(flight_dir / "altitude.csv", index=False)
```

## GUI Application

```bash
# Launch the altitude analyzer GUI
python altitude_check_app.py
```

## Getting Help

```bash
# Command help
multispectral-altitude --help
multispectral-organize --help
multispectral-wavelength --help

# Python help
python
>>> from multispectral_toolkit.core import AltitudeExtractor
>>> help(AltitudeExtractor)
```

## Troubleshooting

### Problem: "exiftool not found"

**Solution:**
```bash
# Check if installed
which exiftool

# If not, install:
# Ubuntu: sudo apt install libimage-exiftool-perl
# macOS: brew install exiftool
```

### Problem: "Module not found"

**Solution:**
```bash
# Make sure you're in the project directory
cd /home/christianrueda/workfiles/Github/multispectral_imagery_processing

# Reinstall
pip install -e .
```

### Problem: Tests failing

**Solution:**
```bash
# Install test dependencies
pip install -e ".[dev]"

# Run tests with verbose output
pytest -v
```

## Next Steps

1. **Read the full README**: `README.md`
2. **Try examples**: Check `examples/` directory
3. **Review documentation**: See `docs/` directory
4. **Customize configuration**: Edit `config/default_config.yaml`

## Support

- **Issues**: https://github.com/imchrisrueda/multispectral_imagery_processing/issues
- **Documentation**: See `README.md` and `docs/`
- **Examples**: Check `examples/` directory

---

**Ready to go! 🚀**
