# Run Tests Deep - Documentation

**Deep Test Runner for PyTlWall**

Comprehensive testing tool that compares PyTlWall impedance calculations against reference data from Wake2D/IW2D and OldTLWall.

## Authors

- **Tatiana Rijoff** — tatiana.rijoff@gmail.com
- **Carlo Zannini** — carlo.zannini@cern.ch

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
3. **Compares** results with reference data (Wake2D/IW2D or OldTLWall)
4. **Generates** comparison reports (Excel files and plots)

This tool is essential for validating PyTlWall against established impedance calculation codes.

> **Note:** Deep tests do NOT perform automatic pass/fail validation. Percentage differences can be misleading for very small values. Results require expert analysis.

---

## Installation

The script is located in the `tests/` directory of PyTlWall:

```
pytlwall/
├── pytlwall/                # Main package
├── tests/
│   ├── run_tests_deep.py    # ← This script
│   └── deep_test/           # Test data directories
│       ├── NewCV/
│       ├── RoundChamber/
│       ├── RoundChamberLowBeta/
│       └── Ti_Cer_Cu_Vac/
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

# Run all deep tests
python tests/run_tests_deep.py

# Run tests comparing with Wake2D/IW2D
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
| `--base-dir` | | Base directory for deep tests (default: `tests/deep_test`) |
| `--subdirs` | | Specific subdirectories to test (space-separated) |
| `--cfg-pattern` | | Glob pattern for config files (e.g., `*Wake2D.cfg`) |
| `--no-space-charge` | | Skip space charge impedance calculations |
| `--verbosity` | `-v` | Verbosity level (1=WARNING, 2=INFO, 3=DEBUG) |
| `--help` | `-h` | Show help message |

### Pattern Matching

The `--cfg-pattern` option uses glob patterns:

| Pattern | Matches |
|---------|---------|
| `*Wake2D.cfg` | Any file ending with `Wake2D.cfg` |
| `*OldTLWall.cfg` | Any file ending with `OldTLWall.cfg` |
| `*.cfg` | All `.cfg` files |
| `LHC*.cfg` | Files starting with `LHC` |

---

## Directory Structure

### Test Directories

The following test cases are available:

| Directory | Description |
|-----------|-------------|
| `NewCV/` | New CV (Constant Voltage) test case |
| `RoundChamber/` | Circular chamber test |
| `RoundChamberLowBeta/` | Circular chamber with low beta |
| `Ti_Cer_Cu_Vac/` | Titanium-Ceramic-Copper-Vacuum multilayer |

### Test Directory Layout

```
tests/deep_test/
├── NewCV/                        # Test case directory
│   ├── *_Wake2D.cfg              # Config for Wake2D/IW2D comparison
│   ├── *_OldTLWall.cfg           # Config for OldTLWall comparison
│   ├── Wake2D/                   # Wake2D/IW2D reference data
│   │   ├── ZlongW*.dat
│   │   ├── ZtransW*.dat
│   │   ├── ZxdipW*.dat
│   │   └── ZxquadW*.dat
│   ├── OldTLWall/                # OldTLWall reference data
│   │   ├── ZLong.txt
│   │   ├── ZTrans.txt
│   │   ├── ZDip.txt
│   │   └── ZQuad.txt
│   ├── output/                   # Generated output (created by script)
│   │   ├── ZLong.txt
│   │   ├── ZTrans.txt
│   │   ├── NewTLWallvsWake2D_ZLong.xlsx
│   │   └── ...
│   └── img/                      # Generated plots (created by script)
│       ├── ZLong.png
│       ├── WakeVsNew_ZLong.png
│       └── OldVsNew_ZLong.png
├── RoundChamber/
│   └── ...
├── RoundChamberLowBeta/
│   └── ...
└── Ti_Cer_Cu_Vac/
    └── ...
```

### Reference Data Directories

| Directory | Description |
|-----------|-------------|
| `Wake2D/` | Reference data from Wake2D/IW2D code |
| `OldTLWall/` | Reference data from original TLWall |

---

## Configuration Files

Configuration files (`.cfg`) define the test parameters. Two types are typically used:

### Wake2D Configuration (`*Wake2D.cfg`)

Used when comparing against Wake2D/IW2D reference data. The configuration should match the Wake2D simulation parameters.

### OldTLWall Configuration (`*OldTLWall.cfg`)

Used when comparing against the original TLWall code output.

### Example Configuration

```ini
[path_info]
main_path = tests/deep_test/NewCV

[frequency_file]
filename = frequencies.dat
separator = whitespace
freq_col = 0
skip_rows = 1

[base_info]
component_name = TestChamber
chamber_shape = CIRCULAR
pipe_radius_m = 0.025
pipe_len_m = 1.0
betax = 100.0
betay = 100.0

[beam_info]
gammarel = 2.5
test_beam_shift = 0.001

[layers_info]
nbr_layers = 2

[layer0]
type = CW
thick_m = 0.002
sigmaDC = 1.4e6
epsr = 1.0

[layer1]
type = CW
thick_m = inf
sigmaDC = 1.0e6

[boundary]
type = PEC

[test_config]
ref_long_file = Wake2D/ZlongW.dat
ref_long_skip_rows = 1
```

---

## Output Files

### Generated Impedance Files

Located in `output/` subdirectory:

#### Base Impedances (Wall Contribution)

| File | Description | Unit |
|------|-------------|------|
| `ZLong.txt` | Longitudinal impedance | Ω |
| `ZTrans.txt` | Transverse impedance | Ω/m |
| `ZDipX.txt` | Horizontal dipolar impedance | Ω/m |
| `ZDipY.txt` | Vertical dipolar impedance | Ω/m |
| `ZQuadX.txt` | Horizontal quadrupolar impedance | Ω/m |
| `ZQuadY.txt` | Vertical quadrupolar impedance | Ω/m |

#### Total Impedances (Wall + Space Charge)

| File | Description | Unit |
|------|-------------|------|
| `ZLongTotal.txt` | Total longitudinal impedance | Ω |
| `ZTransTotal.txt` | Total transverse impedance | Ω/m |
| `ZDipXTotal.txt` | Total horizontal dipolar | Ω/m |
| `ZDipYTotal.txt` | Total vertical dipolar | Ω/m |
| `ZQuadXTotal.txt` | Total horizontal quadrupolar | Ω/m |
| `ZQuadYTotal.txt` | Total vertical quadrupolar | Ω/m |

#### Surface Impedances

| File | Description | Unit |
|------|-------------|------|
| `ZLongSurf.txt` | Longitudinal surface impedance | Ω |
| `ZTransSurf.txt` | Transverse surface impedance | Ω/m |

#### Space Charge Impedances

| File | Description | Unit |
|------|-------------|------|
| `ZLongDSC.txt` | Longitudinal direct space charge | Ω |
| `ZLongISC.txt` | Longitudinal indirect space charge | Ω |
| `ZTransDSC.txt` | Transverse direct space charge | Ω/m |
| `ZTransISC.txt` | Transverse indirect space charge | Ω/m |

### Comparison Excel Files

| File Pattern | Description |
|--------------|-------------|
| `NewTLWallvsWake2D_*.xlsx` | Comparison with Wake2D/IW2D |
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
| `WakeVsNew_ZLong.png`, ... | Comparison with Wake2D/IW2D |
| `OldVsNew_ZLong.png`, ... | Comparison with OldTLWall |

---

## Impedance Types

### Base Impedances (Wall Contribution)

| Name | Property | Description |
|------|----------|-------------|
| ZLong | `ZLong` | Longitudinal wall impedance |
| ZTrans | `ZTrans` | Transverse wall impedance |
| ZDipX | `ZDipX` | Horizontal dipolar impedance |
| ZDipY | `ZDipY` | Vertical dipolar impedance |
| ZQuadX | `ZQuadX` | Horizontal quadrupolar impedance |
| ZQuadY | `ZQuadY` | Vertical quadrupolar impedance |

### Total Impedances (Wall + Space Charge)

| Name | Property | Description |
|------|----------|-------------|
| ZLongTotal | `ZLongTotal` | Total longitudinal (wall + SC) |
| ZTransTotal | `ZTransTotal` | Total transverse (wall + SC) |
| ZDipXTotal | `ZDipXTotal` | Total horizontal dipolar |
| ZDipYTotal | `ZDipYTotal` | Total vertical dipolar |
| ZQuadXTotal | `ZQuadXTotal` | Total horizontal quadrupolar |
| ZQuadYTotal | `ZQuadYTotal` | Total vertical quadrupolar |

### Surface Impedances

| Name | Property | Description |
|------|----------|-------------|
| ZLongSurf | `ZLongSurf` | Longitudinal surface impedance |
| ZTransSurf | `ZTransSurf` | Transverse surface impedance |

### Space Charge Impedances

| Name | Property | Description |
|------|----------|-------------|
| ZLongDSC | `ZLongDSC` | Longitudinal direct space charge |
| ZLongISC | `ZLongISC` | Longitudinal indirect space charge |
| ZTransDSC | `ZTransDSC` | Transverse direct space charge |
| ZTransISC | `ZTransISC` | Transverse indirect space charge |

### IW2D Validation Notes

Based on comparisons with IW2D:

| Status | Impedances |
|--------|------------|
| ✓ Consistent | ZLong, ZTrans, ZLongTotal, ZDipX, ZDipY, ZQuadX, ZQuadY |
| ⚠ May vary | ZTransTotal, ZDipXTotal, ZDipYTotal, ZQuadXTotal, ZQuadYTotal |

---

## Examples

### Example 1: Run All Tests

```bash
# Run all deep tests with default settings
python tests/run_tests_deep.py
```

### Example 2: Wake2D/IW2D Comparison

```bash
# Run all tests with Wake2D/IW2D reference
python tests/run_tests_deep.py --cfg-pattern "*Wake2D.cfg"
```

**Output:**
```
============================================================
 PyTlWall Deep Test Runner
============================================================

Found 4 test directories.

Processing: NewCV
  Config: PSB2layers_Wake2D.cfg
  
  Processing ZLong (Longitudinal Impedance)...
    Saved output: ZLong.txt
    Saved plot: ZLong.png
    Wake2D reference: ZlongW_PSB.dat
    Saved comparison: NewTLWallvsWake2D_ZLong.xlsx
    Saved plot: WakeVsNew_ZLong.png
    
  Processing ZTrans (Transverse Impedance)...
    ...

✓ Test NewCV completed successfully

Processing: RoundChamber
  ...

============================================================
 SUMMARY
============================================================
  ✓ Passed: 4
  ✗ Failed: 0
```

### Example 3: Single Directory Test

```bash
# Test only NewCV directory
python tests/run_tests_deep.py --subdirs NewCV --cfg-pattern "*Wake2D.cfg"
```

### Example 4: Multiple Directories

```bash
# Test specific directories
python tests/run_tests_deep.py --subdirs NewCV RoundChamber --cfg-pattern "*Wake2D.cfg"
```

### Example 5: Fast Test (No Space Charge)

```bash
# Skip space charge calculations for faster testing
python tests/run_tests_deep.py --subdirs NewCV --no-space-charge
```

### Example 6: Verbose Mode

```bash
# Detailed output for debugging
python tests/run_tests_deep.py --subdirs NewCV --verbosity 3
```

### Example 7: OldTLWall Comparison

```bash
# Compare with original TLWall
python tests/run_tests_deep.py --cfg-pattern "*OldTLWall.cfg"
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
ConfigurationError: Frequency file not found: frequencies.dat
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

**Solution:** For PEC (Perfect Electric Conductor) boundaries, use `[boundary]` section instead of an extra layer.

### Debugging Tips

1. **Use verbose mode** (`--verbosity 3`) to see detailed output
2. **Check the config file** paths are correct
3. **Verify reference data** exists in Wake2D/ or OldTLWall/ directories
4. **Compare frequency counts** — mismatches may indicate wrong reference files
5. **Check log files** in `tests/logs/` for detailed error messages

---

## Programmatic Usage

You can also use the test runner from Python code:

```python
from tests.run_tests_deep import run_deep_tests

# Run specific tests
success = run_deep_tests(
    base_dir="tests/deep_test",
    subdirs=["NewCV", "RoundChamber"],
    cfg_pattern="*Wake2D.cfg",
    compute_space_charge=True,
    verbosity=2
)

if success:
    print("All tests passed!")
else:
    print("Some tests failed - check outputs for details")
```

---

## See Also

- [TESTING.md](TESTING.md) — Full testing documentation
- [RUN_TESTS_BASE.md](RUN_TESTS_BASE.md) — Base test runner documentation
- [tests/README.md](../tests/README.md) — Tests overview

---

*Last updated: December 2025*
