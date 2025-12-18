# logging Module Examples

![PyTlWall Logo](logo005.png)

**Centralized Logging System**

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

---

## Navigation

**[◀ Back to Examples](EXAMPLES.md)**

| Module | Link |
|--------|------|
| beam | [EXAMPLES_BEAM.md](EXAMPLES_BEAM.md) |
| frequencies | [EXAMPLES_FREQUENCIES.md](EXAMPLES_FREQUENCIES.md) |
| layer | [EXAMPLES_LAYER.md](EXAMPLES_LAYER.md) |
| chamber | [EXAMPLES_CHAMBER.md](EXAMPLES_CHAMBER.md) |
| tlwall | [EXAMPLES_TLWALL.md](EXAMPLES_TLWALL.md) |
| **logging** | *You are here* |

---

## Table of Contents

- [Overview](#overview)
- [Example 1: Quick Setup](#example-1-quick-setup)
- [Example 2: Detailed Configuration](#example-2-detailed-configuration)
- [Example 3: Section Headers](#example-3-section-headers)
- [Example 4: File-Only Logging](#example-4-file-only-logging)
- [Example 5: Multiple Loggers](#example-5-multiple-loggers)
- [Example 6: Complete Workflow](#example-6-complete-workflow)
- [Configuration Reference](#configuration-reference)

---

## Overview

The `logging_util` module provides centralized logging for PyTlWall calculations. It supports:

- Console and file logging
- Configurable verbosity levels
- Section headers for organized output
- Timestamped log files

```python
from pytlwall import logging_util

# Quick setup
log_path, logger = logging_util.quick_setup(
    log_dir="./logs/",
    log_basename="calculation",
    verbosity=2
)

logger.info("Starting calculation...")
logger.warning("This is a warning")
logger.error("This is an error")
```

---

## Example 1: Quick Setup

Simplest way to start logging.

```python
from pytlwall import logging_util

# Quick setup - returns log path and logger
log_path, logger = logging_util.quick_setup(
    log_dir="./my_logs/",
    log_basename="my_calculation",
    verbosity=2,
)

logger.info("Starting calculation...")
logger.info("Processing data...")
logger.warning("This is a warning message")
logger.info("Calculation completed successfully")

print(f"\nLog saved to: {log_path}")
```

**Output (console):**
```
INFO     Starting calculation...
INFO     Processing data...
WARNING  This is a warning message
INFO     Calculation completed successfully

Log saved to: ./my_logs/my_calculation_20251207_143022.log
```

---

## Example 2: Detailed Configuration

Full control over logging configuration.

```python
from pytlwall import logging_util

# Create custom configuration
config = logging_util.LogConfig(
    log_dir="./my_logs/",
    log_basename="detailed_calculation",
    verbosity=3,          # DEBUG level
    add_timestamp=True,
    console_output=True,
)

# Setup logging
log_path = logging_util.setup_logging(config)
logger = logging_util.get_logger(__name__)

# Different log levels
logger.debug("Debug message - only visible at verbosity >= 3")
logger.info("Info message - visible at verbosity >= 2")
logger.warning("Warning message - visible at verbosity >= 1")
logger.error("Error message - always visible")

print(f"\nLog saved to: {log_path}")
```

**Verbosity levels:**
- `0`: ERROR only
- `1`: ERROR + WARNING
- `2`: ERROR + WARNING + INFO
- `3`: ERROR + WARNING + INFO + DEBUG

---

## Example 3: Section Headers

Organize logs with visual section headers.

```python
from pytlwall import logging_util

log_path, logger = logging_util.quick_setup(
    log_dir="./my_logs/",
    log_basename="organized_calculation",
    verbosity=2,
)

# Main header (wide, = characters)
logging_util.log_section_header(logger, "STARTING IMPEDANCE CALCULATION")

# Sub-section (narrower, - characters)
logging_util.log_section_header(logger, "Configuration", char="-", width=60)
logger.info("Chamber radius: 50 mm")
logger.info("Number of layers: 3")
logger.info("Frequency range: 1e3 - 1e9 Hz")

logging_util.log_section_header(logger, "Computation", char="-", width=60)
logger.info("Computing longitudinal impedance...")
logger.info("Computing transverse impedance...")

logging_util.log_section_header(logger, "Results", char="-", width=60)
logger.info("Maximum ZLong: 1.23e-3 Ohm")
logger.info("Maximum ZTrans: 4.56e-2 Ohm/m")

logging_util.log_section_header(logger, "CALCULATION COMPLETED SUCCESSFULLY")

print(f"\nLog saved to: {log_path}")
```

**Output:**
```
================================================================================
                    STARTING IMPEDANCE CALCULATION
================================================================================
------------------------------------------------------------
                       Configuration
------------------------------------------------------------
INFO     Chamber radius: 50 mm
INFO     Number of layers: 3
INFO     Frequency range: 1e3 - 1e9 Hz
------------------------------------------------------------
                        Computation
------------------------------------------------------------
INFO     Computing longitudinal impedance...
INFO     Computing transverse impedance...
------------------------------------------------------------
                          Results
------------------------------------------------------------
INFO     Maximum ZLong: 1.23e-3 Ohm
INFO     Maximum ZTrans: 4.56e-2 Ohm/m
================================================================================
               CALCULATION COMPLETED SUCCESSFULLY
================================================================================
```

---

## Example 4: File-Only Logging

Log to file without console output.

```python
from pytlwall import logging_util

config = logging_util.LogConfig(
    log_dir="./my_logs/",
    log_basename="silent_calculation",
    verbosity=2,
    console_output=False,  # No console output
)

log_path = logging_util.setup_logging(config)
logger = logging_util.get_logger(__name__)

# These messages only go to the file
logger.info("This message appears only in the log file")
logger.info("No console clutter!")
logger.info("Perfect for batch processing")

print(f"Log saved to: {log_path} (no console output was produced)")
```

**Use cases:**
- Batch processing
- Background jobs
- When console output would be too verbose

---

## Example 5: Multiple Loggers

Using different loggers for different modules.

```python
from pytlwall import logging_util

log_path, _ = logging_util.quick_setup(
    log_dir="./my_logs/",
    log_basename="multi_logger",
    verbosity=2,
)

# Get different loggers for different modules
logger_main = logging_util.get_logger("main")
logger_calc = logging_util.get_logger("calculation")
logger_io = logging_util.get_logger("io")

logger_main.info("Main program started")
logger_calc.info("Starting calculation module")
logger_io.info("Reading input file")
logger_calc.info("Calculation completed")
logger_io.info("Writing output file")
logger_main.info("Main program completed")

print(f"\nLog saved to: {log_path}")
```

**Output (in log file):**
```
2025-12-07 14:30:22 - main - INFO - Main program started
2025-12-07 14:30:22 - calculation - INFO - Starting calculation module
2025-12-07 14:30:22 - io - INFO - Reading input file
2025-12-07 14:30:22 - calculation - INFO - Calculation completed
2025-12-07 14:30:22 - io - INFO - Writing output file
2025-12-07 14:30:22 - main - INFO - Main program completed
```

---

## Example 6: Complete Workflow

Complete PyTlWall workflow with logging.

```python
from pytlwall import logging_util
from datetime import datetime

# Setup logging for the entire workflow
config = logging_util.LogConfig(
    log_dir="./my_logs/",
    log_basename="pytlwall_workflow",
    verbosity=2,
    add_timestamp=True,
)

log_path = logging_util.setup_logging(config)
logger = logging_util.get_logger("pytlwall_workflow")

# Start workflow
logging_util.log_section_header(logger, "PYTLWALL IMPEDANCE CALCULATION")
logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info(f"Log file: {log_path}")
logger.info("")

# Phase 1: Configuration
logging_util.log_section_header(logger, "Phase 1: Configuration", char="-", width=60)
logger.info("Reading configuration file: config.cfg")
logger.info("Validating parameters...")
logger.info("Configuration loaded successfully")
logger.info("")

# Phase 2: Geometry setup
logging_util.log_section_header(logger, "Phase 2: Geometry Setup", char="-", width=60)
logger.info("Building wall structure...")
logger.info("  - Number of layers: 3")
logger.info("  - Chamber type: circular")
logger.info("  - Radius: 50.0 mm")
logger.info("Geometry setup completed")
logger.info("")

# Phase 3: Frequency setup
logging_util.log_section_header(logger, "Phase 3: Frequency Setup", char="-", width=60)
logger.info("Frequency range: 1.0e+03 to 1.0e+09 Hz")
logger.info("Number of points: 1000")
logger.info("Scale: logarithmic")
logger.info("")

# Phase 4: Computation
logging_util.log_section_header(logger, "Phase 4: Impedance Computation", char="-", width=60)
logger.info("Computing longitudinal impedance...")
logger.info("  - Progress: 100%")
logger.info("Computing transverse impedance...")
logger.info("  - Progress: 100%")
logger.info("Computation completed successfully")
logger.info("")

# Phase 5: Output
logging_util.log_section_header(logger, "Phase 5: Output Generation", char="-", width=60)
logger.info("Saving Excel output: results.xlsx")
logger.info("Generating plots:")
logger.info("  - Longitudinal impedance: ZLong.png")
logger.info("  - Transverse impedance: ZTrans.png")
logger.info("Output generation completed")
logger.info("")

# Summary
logging_util.log_section_header(logger, "WORKFLOW COMPLETED SUCCESSFULLY")
logger.info(f"Total execution time: 12.34 seconds")
logger.info(f"Full log saved to: {log_path}")

print(f"\nWorkflow completed. See log file: {log_path}")
```

---

## Configuration Reference

### LogConfig Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `log_dir` | str | `"./logs/"` | Directory for log files |
| `log_basename` | str | `"pytlwall"` | Base name for log file |
| `verbosity` | int | `2` | Verbosity level (0-3) |
| `add_timestamp` | bool | `True` | Add timestamp to filename |
| `console_output` | bool | `True` | Enable console output |

### Verbosity Levels

| Level | Logging Level | Messages Shown |
|-------|---------------|----------------|
| 0 | ERROR | Errors only |
| 1 | WARNING | Errors + Warnings |
| 2 | INFO | Errors + Warnings + Info |
| 3 | DEBUG | All messages |

### Functions

| Function | Description |
|----------|-------------|
| `quick_setup(...)` | Quick setup, returns (log_path, logger) |
| `setup_logging(config)` | Full setup with LogConfig |
| `get_logger(name)` | Get a named logger |
| `log_section_header(logger, title, char, width)` | Print section header |

### Log File Format

Default format:
```
2025-12-07 14:30:22 - module_name - INFO - Message text
```

Components:
- Timestamp (ISO format)
- Logger name
- Log level
- Message

---

## Integration with PyTlWall

```python
from pytlwall import logging_util
import pytlwall

# Setup logging
log_path, logger = logging_util.quick_setup(
    log_dir="./logs/",
    log_basename="impedance_calc",
    verbosity=2
)

logging_util.log_section_header(logger, "IMPEDANCE CALCULATION")

# Setup components
logger.info("Setting up beam parameters...")
beam = pytlwall.Beam(gammarel=7460.52)
logger.info(f"  Beam gamma: {beam.gammarel}")

logger.info("Setting up chamber...")
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
logger.info(f"  Chamber radius: {chamber.pipe_rad_m*1000} mm")

logger.info("Setting up frequencies...")
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
logger.info(f"  Frequency points: {len(freqs)}")

logger.info("Setting up layers...")
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

logger.info("Calculating impedances...")
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.ZLong
ZTrans = wall.ZTrans

logger.info(f"  Max |ZLong|: {abs(ZLong).max():.3e} Ω")
logger.info(f"  Max |ZTrans|: {abs(ZTrans).max():.3e} Ω/m")

logging_util.log_section_header(logger, "CALCULATION COMPLETED")
```

---

## See Also

- [API Reference - Logging](LOGGING_README.md) - Complete API documentation
- [Examples Main Page](EXAMPLES.md) - All module examples

---

**[◀ Back to Examples](EXAMPLES.md)** | **[◀ Previous: tlwall](EXAMPLES_TLWALL.md)**
