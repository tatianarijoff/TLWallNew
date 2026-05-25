# PyTlWall

![PyTlWall Logo](logo005.png)

**Python Transmission Line Wall Impedance Calculator**

---

## Overview

PyTlWall is a Python implementation of the **Transmission Line Impedance Model** for computing beam coupling impedances in particle accelerator vacuum chambers.

### Key Features

| Feature | Description |
|---------|-------------|
| **TL Model** | Longitudinal & transverse impedance calculation |
| **Multilayer** | Arbitrary number of material layers |
| **Chamber Types** | Circular, elliptical, rectangular cross-sections |
| **Yokoya Factors** | Automatic geometric correction factors |
| **Space Charge** | Direct and indirect space charge impedances |
| **Batch Mode** | Multi-chamber lattice processing |
| **GUI** | Qt-based configuration editor and visualizer |
| **Plotting** | Automatic impedance plots |
| **Export** | Excel/CSV data export |

---

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

### Reference

**Electromagnetic Simulation of CERN Accelerator Components and Experimental Applications**  
Author: **Carlo Zannini**

---

## Installation

### Requirements

| Component | Version | Notes |
|-----------|---------|-------|
| Python | ≥ 3.9 | Required |
| NumPy | latest | Required |
| SciPy | latest | Required |
| Matplotlib | latest | Required for plotting |
| openpyxl | latest | Required for Excel export |
| PyQt5 | latest | Optional, for GUI |

### Standard Installation

```bash
# Clone repository
git clone https://github.com/CERN/pytlwall.git
cd pytlwall

# Install package
pip install .
```

### Development Installation

```bash
# Install in editable mode
pip install -e .

# Install with all dependencies
pip install -e ".[dev,gui]"
```

### Conda Environment

```bash
conda create -n pytlwall python=3.12
conda activate pytlwall
pip install .
```

### GUI Dependencies

```bash
# For graphical interface
pip install pyqt5
```

---

## Quick Start

### Minimal Example

```python
from pytlwall import Beam, Frequencies, Layer, Chamber, TlWall

# 1. Define beam parameters (LHC 7 TeV protons)
beam = Beam(gammarel=7460.52)

# 2. Define frequency range (1 kHz to 1 GHz)
freqs = Frequencies(fmin=3, fmax=9, fstep=2)

# 3. Define chamber geometry
chamber = Chamber(
    pipe_rad_m=0.022,
    chamber_shape='CIRCULAR'
)

# 4. Define material layer
copper = Layer(
    thick_m=0.001,
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq
)
chamber.layers = [copper]

# 5. Calculate impedances
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()

print(f"Calculated at {len(freqs)} frequencies")
print(f"Max |ZLong|: {abs(ZLong).max():.3e} Ω")
print(f"Max |ZTrans|: {abs(ZTrans).max():.3e} Ω/m")
```

### Using Configuration Files

```python
from pytlwall import CfgIo

# Load configuration and create TlWall
cfg = CfgIo("chamber.cfg")
wall = cfg.read_pytlwall()

# Calculate impedances
ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()
```

### Multi-Chamber Lattice

```python
from pytlwall import MultipleChamber

mc = MultipleChamber(
    apertype_file="apertype2.txt",
    geom_file="b_L_betax_betay.txt",
    input_dir="./input/",
    out_dir="./output/"
)

# Load inputs
mc.load()

# Calculate all elements
mc.calculate_all()

# Plot total accumulated impedances
mc.plot_totals(show=False)
```

---

## Running PyTlWall

### Command Line Interface

```bash
# Run with configuration file
python -m pytlwall config.cfg

# Launch GUI
python -m pytlwall --gui
```

### Launch GUI Directly

```bash
# Using the GUI module
python -m pytlwall_gui

# Or with the run script
python run_gui.py

# Or via main module
python -m pytlwall --gui
```

### Python Script

```python
import pytlwall

# Access all modules
beam = pytlwall.Beam(gammarel=7460.52)
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
# ... etc
```

---

## Project Structure

### Core Modules

| Module | Description |
|--------|-------------|
| `beam.py` | Particle beam parameters with relativistic calculations |
| `frequencies.py` | Frequency array management |
| `layer.py` | Material layer definitions |
| `chamber.py` | Chamber geometry and Yokoya factors |
| `tlwall.py` | Main impedance calculation engine |
| `cfg_io.py` | Configuration file I/O |

### Utility Modules

| Module | Description |
|--------|-------------|
| `io_util.py` | Input/output helper functions |
| `plot_util.py` | Plotting utilities |
| `logging_util.py` | Logging system |
| `multiple_chamber.py` | Multi-element lattice processing |

### GUI Module

| Module | Description |
|--------|-------------|
| `pytlwall_gui/` | Qt-based graphical interface |

---

## Documentation

### API Reference

| Document | Description |
|----------|-------------|
| [API_REFERENCE.md](doc/API_REFERENCE.md) | Main API overview |
| [API_REFERENCE_BEAM.md](doc/API_REFERENCE_BEAM.md) | Beam module |
| [API_REFERENCE_FREQUENCIES.md](doc/API_REFERENCE_FREQUENCIES.md) | Frequencies module |
| [API_REFERENCE_LAYER.md](doc/API_REFERENCE_LAYER.md) | Layer module |
| [API_REFERENCE_CHAMBER.md](doc/API_REFERENCE_CHAMBER.md) | Chamber module |
| [API_REFERENCE_TLWALL.md](doc/API_REFERENCE_TLWALL.md) | TlWall module |
| [API_REFERENCE_CFGIO.md](doc/API_REFERENCE_CFGIO.md) | CfgIo module |
| [API_REFERENCE_MULTIPLE.md](doc/API_REFERENCE_MULTIPLE.md) | MultipleChamber module |

### GUI Documentation

| Document | Description |
|----------|-------------|
| [GUI.md](doc/GUI.md) | GUI overview and getting started |
| [GUI_MENU_BAR.md](doc/GUI_MENU_BAR.md) | Menu bar reference |
| [GUI_SIDEBAR.md](doc/GUI_SIDEBAR.md) | Sidebar controls |
| [GUI_DATA_PANEL.md](doc/GUI_DATA_PANEL.md) | Data panel usage |
| [GUI_PLOT_PANEL.md](doc/GUI_PLOT_PANEL.md) | Plot panel features |
| [GUI_VIEW_IO.md](doc/GUI_VIEW_IO.md) | View and I/O operations |

### Examples

| Document | Description |
|----------|-------------|
| [EXAMPLES_README.md](doc/EXAMPLES_README.md) | Examples overview |
| [EXAMPLES_BEAM.md](doc/EXAMPLES_BEAM.md) | Beam examples |
| [EXAMPLES_FREQUENCIES.md](doc/EXAMPLES_FREQUENCIES.md) | Frequencies examples |
| [EXAMPLES_LAYER.md](doc/EXAMPLES_LAYER.md) | Layer examples |
| [EXAMPLES_CHAMBER.md](doc/EXAMPLES_CHAMBER.md) | Chamber examples |
| [EXAMPLES_TLWALL.md](doc/EXAMPLES_TLWALL.md) | TlWall examples |
| [EXAMPLES_MULTIPLE.md](doc/EXAMPLES_MULTIPLE.md) | MultipleChamber examples |
| [EXAMPLES_LOGGING.md](doc/EXAMPLES_LOGGING.md) | Logging examples |

### Time-Domain Wake

| Document | Description |
|----------|-------------|
| [WAKE.md](doc/WAKE.md) | Time-domain wake module (`TLWallWake`) overview and usage |
| [WAKE_THEORY.md](doc/WAKE_THEORY.md) | Physical model: transmission-line wake and thick/thin limits |
| [test_tlwall_wake.md](doc/testing/test_tlwall_wake.md) | Wake module test suite |

### Additional Documentation

| Document | Description |
|----------|-------------|
| [INSTALLATION.md](doc/INSTALLATION.md) | Detailed installation guide |
| [CHAMBER_SHAPES_REFERENCE.md](doc/CHAMBER_SHAPES_REFERENCE.md) | Chamber shape details |
| [PYTLWALL_THEORY.md](doc/PYTLWALL_THEORY.md) | Theoretical background |

---

## Configuration File Format

Example `.cfg` file:

```ini
[base_info]
component_name = arc_chamber
pipe_radius_m = 0.022
pipe_len_m = 1.0
chamber_shape = CIRCULAR
betax = 100.0
betay = 100.0

[layers_info]
nbr_layers = 1

[layer0]
type = CW
thick_m = 0.001
sigmaDC = 5.96e7
muinf_Hz = 0
k_Hz = inf
epsr = 1
tau = 0
RQ = 0

[boundary]
type = PEC

[frequency_info]
fmin = 1e3
fmax = 1e9
fstep = 10

[beam_info]
gammarel = 7460.52
test_beam_shift = 0.001
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Import error | Ensure pytlwall is installed: `pip install -e .` |
| GUI not launching | Install PyQt5: `pip install pyqt5` |
| Plot not showing | Install Matplotlib: `pip install matplotlib` |
| Excel export fails | Install openpyxl: `pip install openpyxl` |
| Config file error | Check INI format and section names |

### Getting Help

1. Check the [API Reference](doc/API_REFERENCE.md)
2. Review the [Examples](doc/EXAMPLES_README.md)
3. Contact the authors

---

## License

Copyright CERN. All rights reserved.

---

## Version History

- **v2.0** (December 2025)
  - Complete Python refactoring
  - Modern type hints and documentation
  - Qt-based GUI with multi-chamber support
  - MultipleChamber for lattice processing
  - Comprehensive test suite

- **v1.0** (Original)
  - Initial Fortran/Python implementation

---

*Last updated: December 2025*
