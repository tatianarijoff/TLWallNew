# Run Tests Deep - Documentation

**Deep Test Runner for PyTlWall**

Comprehensive testing tool that compares PyTlWall impedance calculations against reference data from Wake2D and OldTLWall.

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

---

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Command Line Usage](#command-line-usage)
- [Directory Structure](#directory-structure)
- [Configuration Files](#configuration-files)
- [Output Files](#output-files)
- [Impedance Types](#impedance-types)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Overview

`run_tests_deep.py` is a validation tool that:

1. **Reads** configuration files (`.cfg`) for test cases
2. **Computes** impedances using PyTlWall
3. **Compares** results with reference data (Wake2D or OldTLWall)
4. **Generates** comparison reports (Excel files and plots)

This tool is essential for validating PyTlWall against established impedance calculation codes.

---

## Installation

The script is located in the `tests/` directory of PyTlWall:

```
pytlwall/
├── pytlwall/           # Main package
├── tests/
│   ├── run_tests_deep.py    # ← This script
│   └── deep_test/           # Test data directories
└── doc/
```

### Requirements

```bash
pip install numpy matplotlib pandas openpyxl
```

---

## Quick Start

```bash
# Navigate to pytlwall directory
cd pytlwall

# Run tests comparing with Wake2D
python tests/run_tests_deep.py --cfg-pattern "*Wake2D.cfg"

# Run tests comparing with OldTLWall
python tests/run_tests_deep.py --cfg-pattern "*OldTLWall.cfg"
```

---

## Command Line Usage

```
python run_tests_deep.py [OPTIONS]
```

### Options

| Option | Short | Description |
|--------|-------|-------------|
| `--subdirs` | | Specific subdirectories to test (space-separated) |
| `--cfg-pattern` | | Glob pattern for config files (e.g., `*Wake2D.cfg`) |
| `--no-space-charge` | | Skip space charge impedance calculations |
| `--verbose` | `-v` | Verbose output with detailed logging |
| `--help` | `-h` | Show help message |

### Pattern Matching

The `--cfg-pattern` option uses glob patterns:

| Pattern | Matches |
|---------|---------|
| `*Wake2D.cfg` | Any file ending with `Wake2D.cfg` |
| `*OldTLWall.cfg` | Any file ending with `OldTLWall.cfg` |
| `*.cfg` | All `.cfg` files |
| `PSB*.cfg` | Files starting with `PSB` |

---

## Directory Structure

### Test Directory Layout

```
tests/deep_test/
├── newCV/                      # Test case directory
│   ├── PSB2layers_Wake2D.cfg   # Config for Wake2D comparison
│   ├── PSB2layers_OldTLWall.cfg # Config for OldTLWall comparison
│   ├── Wake2D/                 # Wake2D reference data
│   │   ├── ZlongW*.dat
│   │   ├── ZtransW*.dat
│   │   ├── ZxdipW*.dat
│   │   └── ZxquadW*.dat
│   ├── OldTLWall/              # OldTLWall reference data
│   │   ├── ZLong.txt
│   │   ├── ZTrans.txt
│   │   ├── ZDip.txt
│   │   └── ZQuad.txt
│   ├── output/                 # Generated output (created by script)
│   │   ├── ZLong.txt
│   │   ├── ZTrans.txt
│   │   ├── NewTLWallvsWake2D_ZLong.xlsx
│   │   └── ...
│   └── img/                    # Generated plots (created by script)
│       ├── ZLong.png
│       ├── WakeVsNew_ZLong.png
│       └── OldVsNew_ZLong.png
├── newlowbeta/                 # Another test case
│   └── ...
└── another_test/
    └── ...
```

### Reference Data Directories

| Directory | Description |
|-----------|-------------|
| `Wake2D/` | Reference data from Wake2D code |
| `OldTLWall/` | Reference data from original TLWall |

---

## Configuration Files

Configuration files (`.cfg`) define the test parameters. Two types are typically used:

### Wake2D Configuration (`*Wake2D.cfg`)

Used when comparing against Wake2D reference data. The configuration should match the Wake2D simulation parameters.

### OldTLWall Configuration (`*OldTLWall.cfg`)

Used when comparing against the original TLWall code output.

### Example Configuration

```ini
[path_info]
main_path = tests/deep_test/newCV

[frequency_file]
filename = ZLong.txt

[beam]
gammarel = 2.5

[chamber]
chamber_shape = CIRCULAR
pipe_rad_m = 0.025
betax = 1.0
betay = 1.0

[boundary]
type = PEC

[layer1]
thick_m = 0.002
sigmaDC = 1.4e6
type = CW
```

---

## Output Files

### Generated Impedance Files

Located in `output/` subdirectory:

| File | Description | Unit |
|------|-------------|------|
| `ZLong.txt` | Longitudinal impedance | Ω |
| `ZTrans.txt` | Transverse impedance | Ω/m |
| `ZDip.txt` | Dipolar impedance | Ω |
| `ZQuad.txt` | Quadrupolar impedance | Ω |
| `ZLongDSC.txt` | Longitudinal direct space charge | Ω |
| `ZLongISC.txt` | Longitudinal indirect space charge | Ω |
| `ZTransDSC.txt` | Transverse direct space charge | Ω/m |
| `ZTransISC.txt` | Transverse indirect space charge | Ω/m |
| `ZDipDSC.txt` | Dipolar direct space charge | Ω/m |
| `ZDipISC.txt` | Dipolar indirect space charge | Ω/m |

### Comparison Excel Files

| File Pattern | Description |
|--------------|-------------|
| `NewTLWallvsWake2D_*.xlsx` | Comparison with Wake2D |
| `NewTLWallvsOld_*.xlsx` | Comparison with OldTLWall |

Each Excel file contains:
- Frequency column
- PyTlWall real/imaginary values
- Reference real/imaginary values
- Absolute differences
- Percentage differences
- README sheet with analysis notes

### Plot Files

Located in `img/` subdirectory:

| File Pattern | Description |
|--------------|-------------|
| `ZLong.png`, `ZTrans.png`, ... | Single impedance plots |
| `WakeVsNew_ZLong.png`, ... | Comparison with Wake2D |
| `OldVsNew_ZLong.png`, ... | Comparison with OldTLWall |

---

## Impedance Types

### Standard Impedances

| Name | Property | Method | Description |
|------|----------|--------|-------------|
| ZLong | `ZLong` | `calc_ZLong()` | Longitudinal wall impedance |
| ZTrans | `ZTrans` | `calc_ZTrans()` | Transverse wall impedance |
| ZDip | `ZDipX` | `calc_ZTrans()` | Dipolar (driving) impedance |
| ZQuad | `ZQuadX` | `calc_ZTrans()` | Quadrupolar (detuning) impedance |

### Space Charge Impedances

| Name | Property | Method | Description |
|------|----------|--------|-------------|
| ZLongDSC | `ZLongDSC` | `calc_ZLongDSC()` | Longitudinal direct space charge |
| ZLongISC | `ZLongISC` | `calc_ZLongISC()` | Longitudinal indirect space charge |
| ZTransDSC | `ZTransDSC` | `calc_ZTransDSC()` | Transverse direct space charge |
| ZTransISC | `ZTransISC` | `calc_ZTransISC()` | Transverse indirect space charge |
| ZDipDSC | `ZDipDSC` | `calc_ZTransDSC()` | Dipolar direct space charge |
| ZDipISC | `ZDipISC` | `calc_ZTransISC()` | Dipolar indirect space charge |

---

## Examples

### Example 1: Full Wake2D Comparison

```bash
# Run all tests with Wake2D reference
python tests/run_tests_deep.py --cfg-pattern "*Wake2D.cfg"
```

**Output:**
```
============================================================
 PyTlWall Deep Test Runner
============================================================

Found 3 test directories.

Processing: newCV
  Config: PSB2layers_Wake2D.cfg
  
  Processing ZLong (Longitudinal Impedance)...
    Saved output: ZLong.txt
    Saved plot: ZLong.png
    Wake2D reference: ZlongW_PSB.dat
    Saved plot: WakeVsNew_ZLong.png
    
  Processing ZTrans (Transverse Impedance)...
    ...

✓ Test newCV completed successfully

============================================================
 SUMMARY
============================================================
  ✓ Passed: 3
  ✗ Failed: 0
```

### Example 2: Single Directory Test

```bash
# Test only newCV directory with OldTLWall
python tests/run_tests_deep.py --subdirs newCV --cfg-pattern "*OldTLWall.cfg"
```

### Example 3: Multiple Directories

```bash
# Test specific directories
python tests/run_tests_deep.py --subdirs newCV newlowbeta --cfg-pattern "*Wake2D.cfg"
```

### Example 4: Fast Test (No Space Charge)

```bash
# Skip space charge calculations for faster testing
python tests/run_tests_deep.py --subdirs newCV --cfg-pattern "*Wake2D.cfg" --no-space-charge
```

### Example 5: Verbose Mode

```bash
# Detailed output for debugging
python tests/run_tests_deep.py --subdirs newCV --cfg-pattern "*Wake2D.cfg" -v
```

---

## Troubleshooting

### Common Errors

#### 1. Configuration File Not Found

```
ERROR: No configuration files found matching pattern '*Wake2D.cfg'
```

**Solution:** Check that the config file exists in the test directory with the correct naming pattern.

#### 2. Frequency File Not Found

```
ConfigurationError: Frequency file not found: ZLong.txt
```

**Solution:** The frequency file path in the config is relative to `main_path`. Ensure the file exists or the path is correct.

#### 3. Reference Data Missing

```
WARNING: No Wake2D reference file found: ZlongW*.dat
```

**Solution:** This is a warning, not an error. The test will continue but won't generate comparison files for this impedance type.

#### 4. Layer Configuration Issue

```
WARNING: Config has 'layer1' section!
         This might be incorrect - check if it should be 'boundary'
```

**Solution:** For PEC (Perfect Electric Conductor) boundaries, use `[boundary]` section instead of `[layer1]`.

### Debugging Tips

1. **Use verbose mode** (`-v`) to see detailed output
2. **Check the config file** paths are correct
3. **Verify reference data** exists in Wake2D/ or OldTLWall/ directories
4. **Compare frequency counts** - mismatches may indicate wrong reference files

---

## API Usage

You can also use the test runner programmatically:

```python
from run_tests_deep import run_deep_tests

# Run all tests
success = run_deep_tests(
    subdirs=['newCV', 'newlowbeta'],
    cfg_pattern='*Wake2D.cfg',
    compute_space_charge=True,
    verbosity=2
)

if success:
    print("All tests passed!")
else:
    print("Some tests failed!")
```

---

## Version History

- **v1.0** - Initial release
- **v1.1** - Added space charge impedances
- **v2.0** - Added ZDipDSC, ZDipISC; improved output organization

---

*Last updated: December 2025*
