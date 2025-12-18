# test_plot.py - Plotting Utilities Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `plot_util` module which provides plotting functions for impedance visualization.

**Module tested**: `pytlwall.plot_util`

**Run this test**:
```bash
python tests/test_plot.py -v
```

---

## Test Classes

### TestPlot

Tests plotting functionality.

| Test Method | Description |
|-------------|-------------|
| `test_longitudinal_output` | Tests longitudinal impedance plot (log-log scale) |
| `test_transverse_output` | Tests transverse impedance plots (log-symlog scale) |

---

## Test Details

### test_longitudinal_output

Creates a simple longitudinal impedance plot:

- **Configuration**: `tests/input/one_layer.cfg`
- **Output**: `tests/output/one_layer/img/ZLong.png`
- **Scale**: log-log
- **Impedance type**: "L" (Longitudinal)

### test_transverse_output

Creates transverse impedance plots (real and imaginary parts):

- **Configuration**: `tests/input/one_layer.cfg`
- **Output**: 
  - `tests/output/one_layer/img/ZTransReal.png`
  - `tests/output/one_layer/img/ZTransImag.png`
- **Scale**: x=log, y=symlog
- **Components plotted**:
  - Dipolar X
  - Dipolar Y
  - Quadrupolar X
  - Quadrupolar Y

---

## Plotting Functions Tested

### plot_Z_vs_f_simple

Single impedance vs frequency plot:

```python
plot_util.plot_Z_vs_f_simple(
    f,              # Frequency array
    Z,              # Complex impedance array
    imped_type,     # "L" or "T"
    title,          # Plot title
    savedir,        # Output directory
    savename,       # Output filename
    xscale='log',   # X-axis scale
    yscale='log'    # Y-axis scale
)
```

### plot_list_Z_vs_f

Multiple impedances on same plot:

```python
plot_util.plot_list_Z_vs_f(
    f,              # Frequency array
    list_Z,         # List of impedance arrays
    list_label,     # List of labels
    imped_type,     # "L" or "T"
    title,          # Plot title
    savedir,        # Output directory
    savename,       # Output filename
    xscale,         # X-axis scale
    yscale          # Y-axis scale ('symlog' for negative values)
)
```

---

## Scale Options

| Scale | Description | Use Case |
|-------|-------------|----------|
| `'log'` | Logarithmic | Positive values spanning decades |
| `'linear'` | Linear | Small range, comparison |
| `'symlog'` | Symmetric log | Values crossing zero |

---

## Output Directory Structure

```
tests/output/
└── one_layer/
    └── img/
        ├── ZLong.png
        ├── ZTransReal.png
        └── ZTransImag.png
```

---

## Example Usage

```python
import pytlwall
import pytlwall.plot_util as plot

# Load configuration and calculate
cfg = pytlwall.CfgIo('tests/input/one_layer.cfg')
wall = cfg.read_pytlwall()
wall.calc_ZLong()
wall.calc_ZTrans()

# Simple longitudinal plot
plot.plot_Z_vs_f_simple(
    wall.f, 
    wall.ZLong, 
    "L",
    "Longitudinal Impedance",
    'output/img/',
    'ZLong.png',
    xscale='log',
    yscale='log'
)

# Multiple transverse components
list_Z = [wall.ZDipX.real, wall.ZDipY.real, 
          wall.ZQuadX.real, wall.ZQuadY.real]
list_label = ['Dipolar X', 'Dipolar Y', 
              'Quadrupolar X', 'Quadrupolar Y']

plot.plot_list_Z_vs_f(
    wall.f,
    list_Z,
    list_label,
    'T',
    'Transverse Impedance (Real)',
    'output/img/',
    'ZTrans_real.png',
    'log',
    'symlog'
)
```

---

## Dependencies

- `matplotlib` - Required for plotting
- Output directories are created automatically if they don't exist

---

[← Back to Testing Documentation](../TESTING.md)
