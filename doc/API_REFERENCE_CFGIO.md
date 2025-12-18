# 📚 CfgIo Module Documentation

## Overview

The `cfgio` module provides configuration file I/O for pytlwall. It handles reading and writing INI-style configuration files for chamber, beam, frequency, and output specifications.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [API Reference](#api-reference)
4. [Configuration File Format](#configuration-file-format)
5. [Examples](#examples)
6. [Best Practices](#best-practices)

---

## Installation

```python
from pytlwall.cfg_io import CfgIo
```

---

## Quick Start

### Reading Configuration

```python
from pytlwall.cfg_io import CfgIo

# Load configuration
cfg = CfgIo('config.ini')

# Read components
chamber = cfg.read_chamber()
beam = cfg.read_beam()
freq = cfg.read_freq()

# Create TlWall
wall = cfg.read_pytlwall()
```

### Writing Configuration

```python
from pytlwall.cfg_io import CfgIo
from pytlwall import Chamber, Beam, Frequencies, Layer

# Create configuration
cfg = CfgIo()

# Create components
chamber = Chamber(...)
beam = Beam(gamma=7460.52)
freq = Frequencies(fmin=1e3, fmax=1e9, fstep=10)

# Save to config
cfg.save_chamber(chamber)
cfg.save_beam(beam)
cfg.save_freq(freq)

# Write to file
cfg.write_cfg('my_config.ini')
```

---

## API Reference

### Class: CfgIo

Main configuration I/O handler.

#### Constructor

```python
CfgIo(cfg_file=None)
```

**Parameters:**
- `cfg_file` (str, optional): Path to configuration file

**Example:**
```python
cfg = CfgIo('config.ini')
```

#### Core I/O Methods

##### `read_cfg(cfg_file)`

Read configuration from INI file.

**Parameters:**
- `cfg_file` (str): Path to configuration file

**Raises:**
- `ConfigurationError`: If file doesn't exist

**Example:**
```python
cfg.read_cfg('config.ini')
```

##### `write_cfg(filename)`

Write configuration to file.

**Parameters:**
- `filename` (str): Output file path

**Example:**
```python
cfg.write_cfg('output.ini')
```

#### Chamber Methods

##### `read_chamber(cfg_file=None)`

Read chamber configuration.

**Parameters:**
- `cfg_file` (str, optional): Path to configuration file

**Returns:**
- `Chamber` or `None`: Chamber object or None if section missing

**Example:**
```python
chamber = cfg.read_chamber()
print(f"Shape: {chamber.chamber_shape}")
```

##### `save_chamber(chamber)`

Save chamber configuration.

**Parameters:**
- `chamber` (Chamber): Chamber object to save

**Example:**
```python
cfg.save_chamber(chamber)
```

##### `save_layer(layers)`

Save layer configurations.

**Parameters:**
- `layers` (List[Layer]): List of Layer objects

**Example:**
```python
cfg.save_layer([layer1, layer2, boundary])
```

#### Beam Methods

##### `read_beam(cfg_file=None)`

Read beam configuration.

**Parameters:**
- `cfg_file` (str, optional): Path to configuration file

**Returns:**
- `Beam` or `None`: Beam object or None if section missing

**Example:**
```python
beam = cfg.read_beam()
print(f"Gamma: {beam.gammarel:.2f}")
```

##### `save_beam(beam)`

Save beam configuration.

**Parameters:**
- `beam` (Beam): Beam object to save

**Example:**
```python
cfg.save_beam(beam)
```

#### Frequency Methods

##### `read_freq(cfg_file=None)`

Read frequency configuration.

**Parameters:**
- `cfg_file` (str, optional): Path to configuration file

**Returns:**
- `Frequencies`: Frequencies object

**Example:**
```python
freq = cfg.read_freq()
print(f"Points: {len(freq)}")
```

##### `save_freq(freq)`

Save frequency configuration.

**Parameters:**
- `freq` (Frequencies): Frequencies object to save

**Example:**
```python
cfg.save_freq(freq)
```

#### Output Methods

##### `read_output(cfg_file=None)`

Read output configuration.

**Parameters:**
- `cfg_file` (str, optional): Path to configuration file

**Side Effects:**
- Sets `self.list_output`, `self.file_output`, `self.img_output`

**Example:**
```python
cfg.read_output()
print(f"Impedances: {cfg.list_output}")
```

##### `save_calc(list_calc)`

Save calculation configuration.

**Parameters:**
- `list_calc` (Dict[str, bool]): Impedance name to boolean flag mapping

**Example:**
```python
cfg.save_calc({
    'ZLong': True,
    'ZTrans': True,
    'ZDipX': False
})
```

#### High-Level Methods

##### `read_pytlwall(cfg_file=None)`

Read complete configuration and create TlWall.

**Parameters:**
- `cfg_file` (str, optional): Path to configuration file

**Returns:**
- `TlWall` or `None`: TlWall object or None if incomplete

**Example:**
```python
wall = cfg.read_pytlwall()
ZLong = wall.calc_ZLong()
```

##### `calc_wall()`

Calculate impedances based on configuration.

**Side Effects:**
- Sets `self.mywall` and `self.myimped`

**Note:**
- Requires `read_output()` called first

**Example:**
```python
cfg.read_output()
cfg.calc_wall()
print(f"ZLong shape: {cfg.myimped['ZLong'].shape}")
```

##### `print_wall()`

Write calculated impedances to files.

**Note:**
- Requires `calc_wall()` called first
- Output format based on file extension (.xlsx or .csv)

**Example:**
```python
cfg.calc_wall()
cfg.print_wall()
```

##### `plot_wall()`

Generate plots of calculated impedances.

**Note:**
- Requires `calc_wall()` called first
- Uses `pytlwall.plot_util`

**Example:**
```python
cfg.calc_wall()
cfg.plot_wall()
```

---

## Configuration File Format

### Section: base_info

Chamber geometry and parameters.

```ini
[base_info]
component_name = chamber_name
pipe_len_m = 10.0
pipe_radius_m = 0.022  # For circular
# OR
pipe_hor_m = 0.030     # For elliptical/rectangular
pipe_ver_m = 0.020
chamber_shape = CIRCULAR  # See Chamber Shapes section below
betax = 100.0
betay = 50.0
```

#### Chamber Shape Values

**Official shapes:**
- `CIRCULAR` - Circular cross-section (cylindrical chamber)
- `ELLIPTICAL` - Elliptical cross-section
- `RECTANGULAR` - Rectangular cross-section

**Accepted aliases:**
- `ROUND` → automatically normalized to `CIRCULAR`
- `ELLIPTIC` → automatically normalized to `ELLIPTICAL`
- `RECT` → automatically normalized to `RECTANGULAR`
- `RECTANGLE` → automatically normalized to `RECTANGULAR`

**Example with aliases:**
```ini
chamber_shape = ROUND  # Valid alias for CIRCULAR
chamber_shape = ELLIPTIC  # Valid alias for ELLIPTICAL
chamber_shape = RECT  # Valid alias for RECTANGULAR
```

See [Chamber Shapes Reference](CHAMBER_SHAPES_REFERENCE.md) for complete documentation.

### Section: layers_info

Number of layers (excluding boundary).

```ini
[layers_info]
nbr_layers = 2
```

### Section: layer{N}

Individual layer configuration.

```ini
[layer0]
type = CW
thick_m = 0.001
muinf_Hz = 1.0
epsr = 1.0
sigmaDC = 5.96e7
k_Hz = 0.0
tau = 0.0
RQ = 1.0
```

For simple materials:
```ini
[layer1]
type = PEC
thick_m = 0.002
```

### Section: boundary

Boundary layer (outermost).

```ini
[boundary]
type = PEC
```

### Section: beam_info

Beam parameters.

```ini
[beam_info]
test_beam_shift = 0.001
# One of:
betarel = 0.999
# OR
gammarel = 7460.52
# OR
Ekin_MeV = 7000000
# OR
p_MeV_c = 7000000

# Optional:
mass_MeV_c2 = 938.272
```

**Priority:** betarel > gammarel > Ekin_MeV > p_MeV_c

### Section: frequency_info

Frequency range.

```ini
[frequency_info]
fmin = 1000
fmax = 1000000000
fstep = 10
```

### Section: frequency_file

Frequencies from file (alternative to frequency_info).

```ini
[frequency_file]
filename = frequencies.txt
separator = ,
freq_col = 0
skip_rows = 1
```

### Section: output

Impedances to calculate.

```ini
[output]
ZLong = True
ZTrans = True
ZDipX = False
ZDipY = False
ZQuadX = False
ZQuadY = False
ZLongSurf = True
ZTransSurf = False
ZLongDSC = False
ZLongISC = False
ZTransDSC = False
ZTransISC = False
```

### Section: output{N}

File output specification.

```ini
[output1]
output_name = results.xlsx
output_list = ZLong, ZTrans
use_name_flag = True
re_im_flag = both  # or 'real' or 'imag'
```

### Section: img_output{N}

Image output specification.

```ini
[img_output1]
img_name = impedance_plot.png
imped_list = ZLong, ZTrans
use_name_flag = False
re_im_flag = both
title = Impedance vs Frequency
xscale = log  # or 'lin'
yscale = log
```

---

## Examples

### Example 1: Basic Usage

```python
from pytlwall.cfg_io import CfgIo

# Read configuration
cfg = CfgIo('config.ini')
wall = cfg.read_pytlwall()

# Calculate
ZLong = wall.calc_ZLong()
print(f"Calculated at {len(wall.f)} frequencies")
```

### Example 2: Create Configuration

```python
from pytlwall.cfg_io import CfgIo
from pytlwall import Chamber, Beam, Frequencies, Layer

cfg = CfgIo()

# Setup components
chamber = Chamber(
    pipe_rad_m=0.022,
    chamber_shape='CIRCULAR',
    layers=[
        Layer(thick_m=0.001, sigmaDC=5.96e7, boundary=False),
        Layer(layer_type='PEC', boundary=True)
    ]
)
beam = Beam(gamma=7460.52)
freq = Frequencies(fmin=1e3, fmax=1e9, fstep=10)

# Save
cfg.save_chamber(chamber)
cfg.save_beam(beam)
cfg.save_freq(freq)
cfg.write_cfg('my_config.ini')
```

### Example 3: Calculate and Export

```python
cfg = CfgIo('config.ini')

# Setup outputs
cfg.config.add_section('output')
cfg.config.set('output', 'ZLong', 'True')
cfg.config.set('output', 'ZTrans', 'True')

cfg.config.add_section('output1')
cfg.config.set('output1', 'output_name', 'results.xlsx')
cfg.config.set('output1', 'output_list', 'ZLong, ZTrans')

# Calculate and save
cfg.read_output()
cfg.calc_wall()
cfg.print_wall()
```

### Example 4: Batch Processing

```python
chambers = ['chamber1.ini', 'chamber2.ini', 'chamber3.ini']

for cfg_file in chambers:
    cfg = CfgIo(cfg_file)
    wall = cfg.read_pytlwall()
    
    ZLong = wall.calc_ZLong()
    
    # Process results...
```

---

## Best Practices

### 1. Configuration Organization

```python
# Group related configurations
configs/
  ├── chambers/
  │   ├── lhc_arc.ini
  │   └── lhc_ir.ini
  ├── beams/
  │   ├── proton_7tev.ini
  │   └── lead_ion.ini
  └── frequencies/
      ├── low_freq.ini
      └── high_freq.ini
```

### 2. Error Handling

```python
from pytlwall.cfg_io import CfgIo, ConfigurationError

try:
    cfg = CfgIo('config.ini')
    wall = cfg.read_pytlwall()
    
    if wall is None:
        print("Incomplete configuration")
    
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### 3. Validation

```python
cfg = CfgIo('config.ini')

# Validate components
chamber = cfg.read_chamber()
if chamber is None:
    raise ValueError("Chamber configuration missing")

beam = cfg.read_beam()
if beam is None:
    raise ValueError("Beam configuration missing")

# Proceed with calculation
wall = cfg.read_pytlwall()
```

### 4. Modular Configuration

```python
# Base configuration
base_cfg = CfgIo('base.ini')
chamber = base_cfg.read_chamber()

# Override beam for different scenarios
for gamma in [1000, 5000, 10000]:
    cfg = CfgIo()
    cfg.save_chamber(chamber)
    cfg.save_beam(Beam(gamma=gamma))
    cfg.write_cfg(f'config_gamma{gamma}.ini')
```

### 5. Version Control

```ini
# Add metadata section
[metadata]
version = 1.0
date = 2025-12-04
author = Your Name
description = LHC beam pipe configuration
```

---

## Common Issues

### Issue 1: Missing Sections

**Problem:** `read_chamber()` returns `None`

**Solution:** Ensure all required sections exist:
- `[base_info]`
- `[layers_info]`
- `[boundary]`

### Issue 2: Invalid Layer Configuration

**Problem:** `ConfigurationError` when reading layers

**Solution:** Check layer numbering and boundary section

### Issue 3: File Not Found

**Problem:** `ConfigurationError: file does not exist`

**Solution:** Use absolute paths or verify working directory

```python
from pathlib import Path

config_path = Path(__file__).parent / 'config.ini'
cfg = CfgIo(str(config_path))
```

---

## Advanced Usage

### Custom Configuration Parser

```python
class ExtendedCfgIo(CfgIo):
    """Extended configuration with custom sections."""
    
    def read_custom_section(self):
        """Read custom configuration section."""
        if self.config.has_section('custom'):
            return self.config.get('custom', 'parameter')
        return None
```

### Programmatic Configuration

```python
cfg = CfgIo()

# Programmatically build configuration
cfg.config.add_section('base_info')
cfg.config.set('base_info', 'pipe_radius_m', '0.022')
cfg.config.set('base_info', 'chamber_shape', 'CIRCULAR')
# ...

# Save
cfg.write_cfg('generated.ini')
```

---

## See Also

- [Chamber Documentation](CHAMBER.md)
- [Beam Documentation](BEAM.md)
- [Frequencies Documentation](FREQUENCIES.md)
- [TlWall Documentation](TLWALL.md)

---

**Last Updated:** December 2025  
**Version:** 2.0  
**Copyright:** CERN
