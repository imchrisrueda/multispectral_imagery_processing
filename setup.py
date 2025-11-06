#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Setup script for Multispectral Imagery Processing Toolkit

For development installation:
    pip install -e .
    
For production installation:
    pip install .
    
For installation with GUI support:
    pip install .[gui]
    
For installation with development tools:
    pip install .[dev]
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
if readme_file.exists():
    with open(readme_file, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A comprehensive toolkit for processing and analyzing multispectral imagery"

# Read requirements
requirements_file = Path(__file__).parent / "requirements.txt"
if requirements_file.exists():
    with open(requirements_file, "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
else:
    requirements = [
        "numpy>=1.20.0",
        "pandas>=1.3.0",
        "matplotlib>=3.4.0",
        "python-dateutil>=2.8.0",
    ]

setup(
    name="multispectral-toolkit",
    version="1.0.0",
    author="Christian Rueda",
    author_email="your.email@example.com",
    description="A comprehensive toolkit for processing and analyzing multispectral imagery",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imchrisrueda/multispectral_imagery_processing",
    project_urls={
        "Bug Tracker": "https://github.com/imchrisrueda/multispectral_imagery_processing/issues",
        "Documentation": "https://github.com/imchrisrueda/multispectral_imagery_processing/blob/main/README.md",
        "Source Code": "https://github.com/imchrisrueda/multispectral_imagery_processing",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Image Processing",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    keywords="multispectral imaging remote-sensing micasense exif gps",
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "gui": ["PyQt6>=6.0.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "isort>=5.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "multispectral-altitude=multispectral_toolkit.core.altitude_extractor:main",
            "multispectral-organize=multispectral_toolkit.core.file_organizer:main",
            "multispectral-wavelength=multispectral_toolkit.core.wavelength_analyzer:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
