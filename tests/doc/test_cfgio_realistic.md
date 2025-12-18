# test_cfgio_realistic.py - CfgIo Realistic Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `CfgIo` class using actual .cfg configuration files from the `tests/input/` directory.

**Module tested**: `pytlwall.cfg_io`

**Run this test**:
```bash
python tests/test_cfgio_realistic.py -v
```

---

## Test Configuration Files

The tests use these files from `tests/input/`:

| File | Description |
|------|-------------|
| `one_layer.cfg` | Single layer elliptical chamber |
| `test001.cfg` | Basic test configuration |
| `two_layers.cfg` | Multi-layer structure |
| `rectangular_chamber.cfg` | RECTANGULAR chamber |
| `test_round.cfg` | CIRCULAR with `:` delimiters |
| `test_rect.cfg` | RECTANGULAR with CW boundary |
| `freq_input.txt` | Plain frequency data (not .cfg) |
| `freq_input2.txt` | Plain frequency data (not .cfg) |
| `freq_input3.dat` | Plain frequency data (not .cfg) |

---

## Test Classes

### TestCfgIoRealistic

Tests CfgIo with realistic .cfg files.

#### one_layer.cfg Tests

| Test Method | Description |
|-------------|-------------|
| `test_onelayer_chamber_base_info` | Tests [base_info]: name, dimensions, beta, shape |
| `test_onelayer_layers_and_boundary` | Tests layer properties: type, thick_m, σ, ε, RQ |
| `test_frequency_info_onelayer` | Tests [frequency_info]: fmin, fmax, fstep |
| `test_beam_info_onelayer` | Tests [beam_info]: test_beam_shift, gammarel |
| `test_pytlwall_one_layer_global` | Tests full TlWall creation |
| `test_pytlwall_one_layer_calculate` | Tests impedance calculation (new pattern) |

#### test001.cfg Tests

| Test Method | Description |
|-------------|-------------|
| `test_pytlwall_test001_cfg` | Tests TlWall creation, frequency sorting, beam/chamber validation |

#### two_layers.cfg Tests

| Test Method | Description |
|-------------|-------------|
| `test_two_layers_chamber` | Tests multi-layer parsing (≥2 layers + boundary) |

#### rectangular_chamber.cfg Tests

| Test Method | Description |
|-------------|-------------|
| `test_rectangular_chamber_shape` | Tests RECTANGULAR shape and pipe_hor_m/pipe_ver_m |

#### test_round.cfg Tests (`:` delimiter)

| Test Method | Description |
|-------------|-------------|
| `test_round_chamber_with_colon_delimiter` | Tests INI parsing with `:` delimiter |
| `test_round_beam_with_colon_delimiter` | Tests beam parsing with `:` delimiter |

#### test_rect.cfg Tests (CW boundary)

| Test Method | Description |
|-------------|-------------|
| `test_rect_chamber_with_cw_boundary` | Tests CW (conductive wall) as boundary type |

#### Frequency File Error Tests

| Test Method | Description |
|-------------|-------------|
| `test_frequency_from_freq_input_txt_raises` | Verifies error for plain .txt file |
| `test_frequency_from_freq_input2_txt_raises` | Verifies error for plain .txt file |
| `test_frequency_from_freq_input3_dat_raises` | Verifies error for plain .dat file |

#### Frequency File Section Tests

| Test Method | Description |
|-------------|-------------|
| `test_frequency_file_section` | Tests [frequency_file] section with external file |

#### Edge Case Tests

| Test Method | Description |
|-------------|-------------|
| `test_missing_config_file` | Verifies ConfigurationError |
| `test_missing_section` | Tests None return for missing sections |
| `test_thick_M_uppercase_support` | Tests thick_M (uppercase M) compatibility |

---

## Configuration Variations Tested

### INI Delimiters

Both `=` and `:` delimiters are supported:

```ini
# Using '=' (standard)
pipe_radius_m = 0.022

# Using ':' (also valid)
pipe_radius_m : 0.022
```

### Chamber Shape Aliases

```ini
# All equivalent:
chamber_shape = CIRCULAR
chamber_shape = ROUND

chamber_shape = ELLIPTICAL
chamber_shape = ELLIPTIC

chamber_shape = RECTANGULAR
chamber_shape = RECT
```

### Boundary Layer Types

```ini
# Perfect conductor
[boundary]
type = PEC

# Conductive wall (used as outermost layer)
[boundary]
type = CW
sigmaDC = 1e6
```

### Frequency Sources

```ini
# Method 1: Exponent range
[frequency_info]
fmin = 3
fmax = 9
fstep = 2

# Method 2: External file
[frequency_file]
filename = path/to/frequencies.txt
separator = whitespace
freq_col = 0
skip_rows = 1
```

---

## Example Usage

```python
from pytlwall.cfg_io import CfgIo

# Load realistic config
cfg = CfgIo('tests/input/one_layer.cfg')

# Create TlWall
wall = cfg.read_pytlwall()

# Verify components
print(f"Chamber: {wall.chamber.component_name}")
print(f"Shape: {wall.chamber.chamber_shape}")
print(f"Layers: {len(wall.chamber.layers)}")
print(f"Beam γ: {wall.beam.gammarel:.2f}")

# Calculate impedance
ZLong = wall.ZLong
print(f"ZLong calculated: {len(ZLong)} points")
```

---

[← Back to Testing Documentation](../TESTING.md)
