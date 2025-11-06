# Contributing to Multispectral Imagery Processing Toolkit

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

## Code of Conduct

This project adheres to a code of conduct based on respect, inclusivity, and professionalism. By participating, you are expected to uphold this code.

### Our Standards

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on what is best for the community
- Show empathy towards other community members
- Be patient and constructive in discussions

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- exiftool installed on your system
- Basic understanding of multispectral imaging (helpful but not required)

### Finding Issues to Work On

- Check the [Issues](https://github.com/imchrisrueda/multispectral_imagery_processing/issues) page
- Look for issues labeled `good first issue` or `help wanted`
- Feel free to ask questions on any issue

## Development Setup

1. **Fork the repository**
   ```bash
   # On GitHub, click the "Fork" button
   ```

2. **Clone your fork**
   ```bash
   git clone https://github.com/YOUR_USERNAME/multispectral_imagery_processing.git
   cd multispectral_imagery_processing
   ```

3. **Add upstream remote**
   ```bash
   git remote add upstream https://github.com/imchrisrueda/multispectral_imagery_processing.git
   ```

4. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

5. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

6. **Verify installation**
   ```bash
   pytest
   ```

## How to Contribute

### Reporting Bugs

When reporting bugs, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected behavior
- Actual behavior
- Any error messages or screenshots
- Sample data (if applicable and not sensitive)

### Suggesting Features

Feature requests are welcome! Please:

- Check if the feature already exists or has been requested
- Clearly describe the use case
- Explain how it would benefit users
- Provide examples if possible

### Code Contributions

1. **Create a branch**
   ```bash
   git checkout -b feature/your-feature-name
   # or
   git checkout -b fix/your-bug-fix
   ```

2. **Make your changes**
   - Write clear, readable code
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Test your changes**
   ```bash
   # Run all tests
   pytest
   
   # Run with coverage
   pytest --cov=src/multispectral_toolkit
   
   # Run specific tests
   pytest tests/test_altitude_extractor.py
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "Brief description of changes"
   ```
   
   Use clear commit messages:
   - `feat: Add new wavelength analysis feature`
   - `fix: Correct altitude extraction bug`
   - `docs: Update README with examples`
   - `test: Add tests for file organizer`

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Go to your fork on GitHub
   - Click "New Pull Request"
   - Fill out the PR template
   - Reference any related issues

## Coding Standards

### Python Style Guide

We follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) with some modifications:

- Line length: 100 characters (not 79)
- Use type hints where appropriate
- Use descriptive variable names
- Add docstrings to all public functions and classes

### Code Formatting

We use **Black** for code formatting:

```bash
# Format all files
black src/ tests/ examples/

# Check without modifying
black --check src/
```

### Import Sorting

We use **isort** for import organization:

```bash
# Sort imports
isort src/ tests/ examples/

# Check without modifying
isort --check-only src/
```

### Linting

We use **flake8** for linting:

```bash
flake8 src/ tests/ examples/
```

### Type Checking

We use **mypy** for type checking (optional but encouraged):

```bash
mypy src/
```

### Docstring Format

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of the function.
    
    More detailed description if needed. Can span multiple lines
    and include examples.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When and why this is raised
        
    Example:
        >>> example_function("test", 42)
        True
    """
    pass
```

## Testing

### Writing Tests

- Place tests in the `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (like exiftool)

Example test:

```python
def test_altitude_extraction_success():
    """Test successful altitude extraction from image."""
    extractor = AltitudeExtractor()
    
    with patch('subprocess.run') as mock_run:
        mock_run.return_value = Mock(
            stdout='[{"GPSAltitude": "100.5 m"}]',
            returncode=0
        )
        
        altitude = extractor.extract_altitude("test.jpg")
        assert altitude == 100.5
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src/multispectral_toolkit --cov-report=html

# Run specific test file
pytest tests/test_altitude_extractor.py

# Run specific test
pytest tests/test_altitude_extractor.py::TestAltitudeExtractor::test_initialization

# Run with verbose output
pytest -v

# Run and stop at first failure
pytest -x
```

## Documentation

### Code Documentation

- All public classes, functions, and methods must have docstrings
- Include type hints
- Provide usage examples in docstrings when helpful
- Keep documentation up to date with code changes

### README and Guides

- Update README.md if you add features
- Add examples to the examples/ directory
- Update CHANGELOG.md for significant changes
- Create detailed guides in docs/ for complex features

### API Documentation

When adding or modifying public APIs, update:
- Docstrings in the code
- Examples in README.md
- API reference in docs/API.md (if applicable)

## Pull Request Process

### Before Submitting

- [ ] Code follows the style guidelines
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Documentation updated
- [ ] CHANGELOG.md updated (for significant changes)
- [ ] Commit messages are clear and descriptive

### PR Template

When creating a PR, include:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
- [ ] All tests pass
- [ ] New tests added
- [ ] Manually tested

## Related Issues
Closes #123

## Additional Notes
Any additional context
```

### Review Process

1. Automated tests will run on your PR
2. A maintainer will review your code
3. Address any feedback or requested changes
4. Once approved, your PR will be merged

### After Merge

- Delete your feature branch
- Update your fork:
  ```bash
  git checkout main
  git pull upstream main
  git push origin main
  ```

## Questions?

If you have questions:

1. Check existing documentation
2. Search closed issues
3. Open a new issue with the `question` label
4. Reach out to maintainers

## Recognition

Contributors will be recognized in:
- README.md (major contributions)
- Release notes
- GitHub contributors page

Thank you for contributing! 🎉
