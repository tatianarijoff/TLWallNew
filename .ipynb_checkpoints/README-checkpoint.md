# pytlwall

## Table of Contents
- [Introduction](#introduction)
- [Installation](#installation)
- [What's New in This Version](#whats-new-in-this-version)
- [Tasks Performed by pytlwall](#tasks-performed-by-pytlwall)
- [Structure of the Package](#structure-of-the-package)
- [Logging System](#logging-system)
- [Quick Start Examples](#quick-start-examples)
- [Documentation](#documentation)
- [Configuration File](ConfigModel.md)
- [References](#references)

## Introduction

**pytlwall** is a CERN Python code which uses transmission line theory to calculate the resistive wall impedance.

The first version of pytlwall was developed in 2011 in MATLAB by Carlo Zannini. Python development started in 2013. The current version has undergone a major restyling to follow current CERN guidelines and PEP8 recommendations, including a new integrated logging system for better diagnostics and testing.

### Capabilities

The aim of pytlwall is to calculate:
- Longitudinal impedance
- Transverse impedance
- Driving and detuning impedance taking care of form factors (Yokoya form factors)
- Space charge impedance (for speed < c)
- Surface impedance

The transmission line equations can be applied recursively to take into account any number of layers. The beam speed and the roughness are taken into account in the formulas. It is also possible to calculate the impedance of a list of chambers to "build" an entire accelerator.

## Installation

### Clean Installation (Recommended)

This version represents a complete package rebuild. If you have a previous version installed, we recommend a clean installation:

```bash
# Uninstall old version (if present)
pip uninstall pytlwall

# Install new version
pip install pytlwall
```

### Development Installation

For development or testing:

```bash
# Clone the repository
git clone <repository-url>
cd pytlwall

# Install in editable mode
pip install -e .
```

## What's New in This Version

### Integrated Logging System

This version introduces a **centralized logging system** integrated into the package, providing:

- ✅ **Unified logging** across all modules and test runners
- ✅ **Timestamped log files** to preserve execution history
- ✅ **Configurable verbosity levels** (WARNING, INFO, DEBUG)
- ✅ **Dual output** (file + console, configurable)
- ✅ **Section headers** for organized logs
- ✅ **Test runners** with detailed logging and comparison capabilities

The logging utilities follow the same pattern as other pytlwall utilities (`plot_util`, `output_util`) and are available as:

```python
from pytlwall import logging_util
```

### Enhanced Test Runners

Two comprehensive test runners are included:

- **`run_tests_base.py`** - Unit tests with configurable logging
- **`run_tests_complete.py`** - Integration tests with reference data comparison

Both test runners can be configured directly in the file or via command-line arguments.

## Tasks Performed by pytlwall

TlWall can:

### Calculate:
- Longitudinal impedance
- Transverse impedance 
- Dipolar and quadrupolar impedance (using chamber shape and Yokoya factors)
- Surface impedance (longitudinal and transverse)
- Indirect space charge impedance (longitudinal and transverse)
- Direct space charge impedance (longitudinal and transverse)

### Features:
- Read all information from a configuration file
- Interactive shell interface to create configuration files
- Basic plotting and output management
- **NEW**: Comprehensive logging for diagnostics and testing
- **NEW**: Automated test comparison with reference data

## Structure of the Package

```pytlwall``` follows the standard Python package structure:

```
pytlwall/                          # Top-level repository
├── pytlwall/                      # Source code package
│   ├── __init__.py               # Package initialization
│   ├── beam.py                   # Beam parameters
│   ├── frequencies.py            # Frequency management
│   ├── layer.py                  # Layer definitions
│   ├── chamber.py                # Chamber geometry
│   ├── cfg_io.py                 # Configuration I/O
│   ├── tlwall.py                 # Main TlWall class
│   ├── plot_util.py              # Plotting utilities
│   ├── output_util.py            # Output formatting
│   └── logging_util.py           # Logging utilities (NEW)
│
├── tests/                         # Unit and integration tests
│   ├── run_tests_base.py         # Base unit test runner (NEW)
│   ├── run_tests_complete.py     # Complete test runner (NEW)
│   └── test_*.py                 # Individual test modules
│
├── examples/                      # Usage examples
│   ├── example_*.py              # Example scripts
│   └── example_logging_usage.py  # Logging examples (NEW)
│
├── docs/                          # Documentation
│   ├── ConfigModel.md            # Configuration file format
│   ├── LOGGING_README.md         # Logging quick reference (NEW)
│   └── LOGGING_DOCUMENTATION.md  # Complete logging docs (NEW)
│
├── LICENSE.txt                    # License information
├── README.md                      # This file
├── pyproject.toml                # Build configuration
├── MANIFEST.in                    # Package manifest
└── setup.py                       # Installation script
```

### Key Components

- **Source code** (`pytlwall/`): Core package with all calculation modules and utilities
- **Unit tests** (`tests/`): Comprehensive test suite with logging and comparison capabilities
- **Examples** (`examples/`): Scripts demonstrating package usage
- **Documentation** (`docs/`, `README.md`): Package and API documentation

### Utilities

- **`plot_util`**: Basic plotting for testing and visualization (you can develop your own plotting interface)
- **`output_util`**: Output formatting and file writing
- **`logging_util`** *(NEW)*: Centralized logging system for diagnostics and testing

## Logging System

The new integrated logging system provides unified logging capabilities across the entire package.

### Basic Usage

```python
from pytlwall import logging_util

# Quick setup
log_path, logger = logging_util.quick_setup(
    log_dir="./logs/",
    log_basename="my_calculation",
    verbosity=2  # INFO level
)

# Use the logger
logger.info("Starting calculation...")
logger.info("Calculation completed!")
```

### In Your pytlwall Scripts

```python
import pytlwall
from pytlwall import logging_util

# Setup logging
log_path, logger = logging_util.quick_setup(
    log_dir="./logs/",
    log_basename="impedance_calc",
    verbosity=2
)

logging_util.log_section_header(logger, "IMPEDANCE CALCULATION")

# Read configuration
logger.info("Reading configuration file...")
cfg = pytlwall.CfgIo("config.cfg")
wall = cfg.read_pytlwall()

# Compute impedances
logger.info("Computing longitudinal impedance...")
wall.calc_ZLong()

logger.info("Computing transverse impedance...")
wall.calc_ZTrans()

logging_util.log_section_header(logger, "CALCULATION COMPLETED")
logger.info(f"Results logged to: {log_path}")
```

### Configuration Options

```python
from pytlwall.logging_util import LogConfig, setup_logging, get_logger

# Detailed configuration
config = LogConfig(
    log_dir="./logs/",
    log_basename="my_app",
    verbosity=2,           # 1=WARNING, 2=INFO, 3=DEBUG
    add_timestamp=True,    # Add timestamp to filename
    console_output=True    # Print to console too
)

log_path = setup_logging(config)
logger = get_logger(__name__)
```

### Verbosity Levels

| Level | Value | Python Level | Description |
|-------|-------|--------------|-------------|
| Quiet | 1 | `WARNING` | Only warnings and errors |
| Normal | 2 | `INFO` | Info, warnings, and errors |
| Verbose | 3 | `DEBUG` | All messages including debug |

### Test Runners with Logging

#### Base Unit Tests

Configure and run:

```python
# In run_tests_base.py - edit TestConfig class
class TestConfig:
    TEST_DIR: str = "./tests/"
    LOG_DIR: str = "./tests/logs/"
    LOG_BASENAME: str = "tlwall_test"
    VERBOSITY: int = 2
    SELECTED_MODULES: Optional[list[str]] = None

# Run from anywhere - automatic path setup included
python tests/run_tests_base.py
```

**Note**: Test runners include automatic path setup, so they can be run from any directory without setting PYTHONPATH or moving files. See [EXECUTION_GUIDE.md](docs/EXECUTION_GUIDE.md) for details.

#### Complete Integration Tests

With reference data comparison:

```python
# In run_tests_complete.py - edit TestConfig class
class TestConfig:
    LOG_DIR: Path = Path("tests/logs")
    LOG_BASENAME: str = "pytlwall_tests"
    VERBOSITY: int = 2
    RTOL: float = 1e-3  # Relative tolerance
    ATOL: float = 1e-10  # Absolute tolerance

# Run tests
python tests/run_tests_complete.py
```

## Quick Start Examples

### Example 1: Basic Calculation with Logging

```python
import pytlwall
from pytlwall import logging_util

# Setup logging
log_path, logger = logging_util.quick_setup()

# Read configuration and compute
cfg = pytlwall.CfgIo("my_config.cfg")
wall = cfg.read_pytlwall()

logger.info("Computing impedances...")
wall.calc_ZLong()
wall.calc_ZTrans()

logger.info(f"Max ZLong: {max(abs(wall.ZLong)):.3e} Ohm")
logger.info(f"Max ZTrans: {max(abs(wall.ZTrans)):.3e} Ohm/m")
```

### Example 2: Organized Workflow

```python
import pytlwall
from pytlwall import logging_util

log_path, logger = logging_util.quick_setup()

# Phase 1: Configuration
logging_util.log_section_header(logger, "PHASE 1: CONFIGURATION")
logger.info("Reading config file: config.cfg")
cfg = pytlwall.CfgIo("config.cfg")
wall = cfg.read_pytlwall()

# Phase 2: Computation
logging_util.log_section_header(logger, "PHASE 2: COMPUTATION")
logger.info("Computing longitudinal impedance...")
wall.calc_ZLong()
logger.info("Computing transverse impedance...")
wall.calc_ZTrans()

# Phase 3: Output
logging_util.log_section_header(logger, "PHASE 3: OUTPUT")
logger.info("Saving results...")
# Your output code here

logging_util.log_section_header(logger, "WORKFLOW COMPLETED")
```

### Example 3: Silent Processing (File Only)

```python
from pytlwall import logging_util
from pytlwall.logging_util import LogConfig

# Configure for file-only logging
config = LogConfig(
    log_dir="./logs/",
    log_basename="silent_calc",
    verbosity=2,
    console_output=False  # No console output
)

log_path = logging_util.setup_logging(config)
logger = logging_util.get_logger(__name__)

# All messages go only to file
logger.info("Processing data...")
logger.info("Done!")

print(f"Log saved to: {log_path}")
```

## Documentation

### Core Documentation

- **[README.md](README.md)** - This file, package overview
- **[ConfigModel.md](ConfigModel.md)** - Configuration file format

### Logging System Documentation

- **[LOGGING_README.md](docs/LOGGING_README.md)** - Quick reference for daily use
- **[LOGGING_DOCUMENTATION.md](docs/LOGGING_DOCUMENTATION.md)** - Complete logging API reference
- **[INTEGRATION_GUIDE.md](docs/INTEGRATION_GUIDE.md)** - Installation and integration guide

### Examples

Run the logging examples to see all features:

```bash
python examples/example_logging_usage.py
```

This will create several example log files demonstrating different usage patterns.

### API Reference

For detailed API documentation, see:

```python
# Get help on any module
import pytlwall
help(pytlwall.logging_util)

# Or specific functions
from pytlwall.logging_util import quick_setup
help(quick_setup)
```

## Installation Code

### pyproject.toml

The build configuration file defining package metadata and dependencies.

### MANIFEST.in

Specifies additional files to include in the distribution package.

### setup.py

Handles the installation process using setuptools.

## References

The following resources were used for preparing this package and documentation:

- Original MATLAB implementation by Carlo Zannini (2011)
- Python port and development (2013-present)
- CERN coding guidelines and PEP8 recommendations
- Python logging best practices

### Related Publications

*(Add relevant publications and references here)*

### Acknowledgments

This package is developed and maintained at CERN. Special thanks to all contributors and users providing feedback.

## License

This project is licensed under the terms specified in [LICENSE.txt](LICENSE.txt).

## Support and Contributing

For issues, questions, or contributions:

1. Check the documentation in `docs/`
2. Review example scripts in `examples/`
3. Run the example logging script: `python examples/example_logging_usage.py`
4. For logging issues, see `LOGGING_DOCUMENTATION.md` troubleshooting section

## Version History

### Current Version (2025)

- Complete package restructuring following CERN guidelines
- Integrated centralized logging system (`logging_util`)
- Enhanced test runners with detailed logging and comparison
- Improved documentation and examples
- Clean installation recommended from previous versions

### Previous Versions

- 2013-2024: Python development and iterations
- 2011: Original MATLAB implementation

---

**Quick Links:**

- [Installation](#installation)
- [Logging System](#logging-system)
- [Quick Start Examples](#quick-start-examples)
- [Documentation](#documentation)
- [Configuration File](ConfigModel.md)
