# test_cfgio_special_cases.py - CfgIo Special Cases Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for edge cases and special configuration scenarios in `CfgIo`, including infinite thickness layers, frequency file sections, and test configuration sections.

**Module tested**: `pytlwall.cfg_io`

**Run this test**:
```bash
python tests/test_cfgio_special_cases.py -v
```

---

## Test Classes

### TestSpecialCases

Tests special configuration scenarios.

| Test Method | Description |
|-------------|-------------|
| `test_infinite_thickness_layer` | Tests layer with thick_m = inf |
| `test_frequency_file_section` | Tests [frequency_file] section loading |
| `test_test_config_section` | Tests [test_config] section for reference files |
| `test_complete_lhc_config` | Tests full LHC-style configuration |

---

## Tested Features

### Infinite Thickness Layers

Some configurations use `thick_m = inf` for semi-infinite backing layers:

```ini
[layer1]
type = CW
thick_m = inf
muinf_Hz = 500
k_Hz = 10000
sigmaDC = 1.0e6
```

The test verifies:
- Layer 0 has finite thickness (1e-3 m)
- Layer 1 has `thick_m == float('inf')`
- Both layers + boundary are correctly parsed

### Frequency File Section

External frequency files can be loaded via [frequency_file] section:

```ini
[frequency_file]
filename = path/to/frequencies.dat
separator = whitespace
freq_col = 0
skip_rows = 1
```

The test verifies:
- External .dat file is loaded
- Header rows are skipped
- Correct column is parsed
- Frequencies match expected values

### Test Configuration Section

The [test_config] section stores reference file paths for validation:

```ini
[test_config]
ref_long_file = tests/ZlongW.dat
ref_long_skip_rows = 1
ref_trans_dip_file = tests/ZtransdipW.dat
ref_trans_dip_skip_rows = 1
ref_trans_quad_file = tests/ZtransquadW.dat
ref_trans_quad_skip_rows = 1
```

The test verifies:
- Section is parsed correctly
- File paths are returned as strings
- Skip row counts are returned as integers

### Complete LHC Configuration

Tests a full LHC-style configuration with:

```ini
[base_info]
component_name = LHC_2layers_24p25mm_some_element
chamber_shape = CIRCULAR
pipe_radius_m = 0.02425
pipe_len_m = 1.0
betax = 100.0
betay = 100.0

[frequency_file]
filename = {external_file}
separator = whitespace
freq_col = 0
skip_rows = 1

[test_config]
ref_long_file = tests/complete/newCV/ZlongWLHC2layers24p25mm_some_element.dat
ref_long_skip_rows = 1
...

[layers_info]
nbr_layers = 2

[layer0]
type = CW
thick_m = 1e-3
muinf_Hz = 0
k_Hz = inf
sigmaDC = 1.670000e+06
...

[layer1]
type = CW
thick_m = inf
muinf_Hz = 500
k_Hz = 10000
sigmaDC = 1.000000e+06
...

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.01
gammarel = 10000
```

Verifies:
- All sections parsed correctly
- Chamber with 2 layers + boundary
- Finite and infinite thickness layers
- Beam parameters
- External frequency file loading
- Test config reference paths

---

## Example Usage

```python
from pytlwall.cfg_io import CfgIo

# Load config with special features
cfg = CfgIo('config_with_infinite_layer.cfg')

# Read chamber with infinite thickness layer
chamber = cfg.read_chamber()
for i, layer in enumerate(chamber.layers):
    if layer.thick_m == float('inf'):
        print(f"Layer {i} is semi-infinite")
    else:
        print(f"Layer {i}: {layer.thick_m*1000:.3f} mm")

# Read test configuration
test_cfg = cfg.read_test_config()
if test_cfg:
    print(f"Reference long file: {test_cfg['ref_long_file']}")
```

---

[← Back to Testing Documentation](../TESTING.md)
