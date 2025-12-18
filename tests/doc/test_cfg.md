# test_cfg.py - CfgIo Class Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `CfgIo` class which handles reading and writing configuration files in INI format.

**Module tested**: `pytlwall.cfg_io`

**Run this test**:
```bash
python tests/test_cfg.py -v
```

---

## Test Classes

### TestCfgIoInitialization

Tests CfgIo creation.

| Test Method | Description |
|-------------|-------------|
| `test_default_initialization` | Tests creation without file |
| `test_initialization_with_file` | Tests loading from .ini file |
| `test_initialization_with_nonexistent_file` | Verifies ConfigurationError |

### TestCfgIoReadCfg

Tests read_cfg method.

| Test Method | Description |
|-------------|-------------|
| `test_read_existing_file` | Tests loading config from file |
| `test_read_nonexistent_file` | Verifies ConfigurationError |

### TestCfgIoChamberIO

Tests chamber configuration reading/writing.

| Test Method | Description |
|-------------|-------------|
| `test_read_circular_chamber` | Tests [base_info] parsing for CIRCULAR |
| `test_read_elliptical_chamber` | Tests [base_info] parsing for ELLIPTICAL |
| `test_read_chamber_no_section` | Tests None return for missing section |
| `test_save_and_read_chamber` | Tests round-trip save/load |

### TestCfgIoBeamIO

Tests beam configuration reading/writing.

| Test Method | Description |
|-------------|-------------|
| `test_read_beam_with_gamma` | Tests gammarel parsing |
| `test_read_beam_with_beta` | Tests betarel parsing |
| `test_read_beam_with_mass` | Tests custom mass parsing |
| `test_read_beam_no_section` | Tests None return for missing section |
| `test_save_beam` | Tests beam serialization |

### TestCfgIoFrequencyIO

Tests frequency configuration reading/writing.

| Test Method | Description |
|-------------|-------------|
| `test_read_frequency_range` | Tests fmin/fmax/fstep parsing |
| `test_read_frequency_default` | Tests default Frequencies object |
| `test_save_frequency` | Tests frequency serialization |

### TestCfgIoOutputConfiguration

Tests output configuration parsing.

| Test Method | Description |
|-------------|-------------|
| `test_read_output_list` | Tests [output] section boolean flags |
| `test_save_calc` | Tests saving calculation flags |

### TestCfgIoHighLevel

Tests high-level operations.

| Test Method | Description |
|-------------|-------------|
| `test_read_pytlwall_complete` | Tests full TlWall creation from config |
| `test_write_cfg` | Tests config file writing |
| `test_read_pytlwall_and_calculate` | Tests new pattern (replaces calc_wall) |

### TestCfgIoStringRepresentation

Tests string output.

| Test Method | Description |
|-------------|-------------|
| `test_repr` | Tests `__repr__` method |
| `test_str` | Tests `__str__` method |

---

## Configuration File Format

Example configuration file structure:

```ini
[base_info]
component_name = test_chamber
chamber_shape = CIRCULAR
pipe_radius_m = 0.022
pipe_len_m = 10.0
betax = 100.0
betay = 50.0

[layers_info]
nbr_layers = 1

[layer0]
type = CW
thick_m = 0.001
sigmaDC = 5.96e7
epsr = 1.0
muinf_Hz = 1.0
k_Hz = inf
tau = 0.0
RQ = 1.0

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.001
gammarel = 7460.52

[frequency_info]
fmin = 3
fmax = 9
fstep = 3

[output]
ZLong = True
ZTrans = True
ZDipX = True
```

---

## New Pattern (Replaces calc_wall)

The old `calc_wall()` method has been removed. Use this pattern instead:

```python
# Old pattern (deprecated):
# cfg = CfgIo('config.cfg')
# cfg.read_output()
# cfg.calc_wall()
# Z = cfg.myimped['ZLong']

# New pattern:
cfg = CfgIo('config.cfg')
cfg.read_output()
wall = cfg.read_pytlwall()  # Returns TlWall object
Z = wall.ZLong  # Calculate directly on TlWall
```

---

## Example Usage

```python
from pytlwall.cfg_io import CfgIo

# Load configuration
cfg = CfgIo('tests/input/one_layer.cfg')

# Read components individually
chamber = cfg.read_chamber()
beam = cfg.read_beam()
freq = cfg.read_freq()

# Or create TlWall directly
wall = cfg.read_pytlwall()

# Calculate impedance
ZLong = wall.ZLong
ZDipX = wall.ZDipX
```

---

[← Back to Testing Documentation](../TESTING.md)
