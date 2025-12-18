# PyTlWall API Reference

**Transmission Line Wall Impedance Calculator**

Complete API documentation for all pytlwall modules.

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

---

## Table of Contents

- [Quick Start](#quick-start)
- [Module Reference](#module-reference)
  - [beam Module](API_REFERENCE_BEAM.md) - Particle beam parameters with relativistic calculations
  - [frequencies Module](API_REFERENCE_FREQUENCIES.md) - Frequency array management for impedance calculations
  - [layer Module](API_REFERENCE_LAYER.md) - Material layer definitions with electromagnetic properties
  - [chamber Module](API_REFERENCE_CHAMBER.md) - Vacuum chamber geometries and Yokoya factors
  - [tlwall Module](API_REFERENCE_TLWALL.md) - Main impedance calculation engine
  - [cfg_io Module](API_REFERENCE_CFGIO.md) - Configuration file I/O for pytlwall
- [Utility Modules](#utility-modules)
- [Installation](#installation)
- [Basic Workflow](#basic-workflow)
- [Additional Resources](#additional-resources)

---

## Quick Start

```python
from pytlwall import Beam, Frequencies, Layer, Chamber, TlWall

# 1. Define beam (LHC 7 TeV protons)
beam = Beam(gammarel=7460.52)

# 2. Define frequency range (1 kHz to 1 GHz)
freqs = Frequencies(fmin=3, fmax=9, fstep=2)

# 3. Define chamber geometry
chamber = Chamber(
    pipe_rad_m=0.022,
    chamber_shape='CIRCULAR'
)

# 4. Define material layers
copper = Layer(
    thick_m=0.001,
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq
)
chamber.layers = [copper]

# 5. Calculate impedances
wall = TlWall(
    beam=beam,
    chamber=chamber,
    frequencies=freqs
)

ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()

print(f"Calculated at {len(freqs)} frequencies")
```

---

## Module Reference

### Core Modules

| Module | Purpose | Key Classes |
|--------|---------|-------------|
| [beam](API_REFERENCE_BEAM.md) | Beam parameters | `Beam`, `BeamValidationError` |
| [frequencies](API_REFERENCE_FREQUENCIES.md) | Frequency arrays | `Frequencies` |
| [layer](API_REFERENCE_LAYER.md) | Material properties | `Layer`, `LayerValidationError` |
| [chamber](API_REFERENCE_CHAMBER.md) | Chamber geometry | `Chamber`, `ChamberShapeError`, `ChamberDimensionError` |
| [tlwall](API_REFERENCE_TLWALL.md) | Impedance calculation | `TlWall`, `TlWallError` |
| [cfg_io](API_REFERENCE_CFGIO.md) | Configuration I/O | `CfgIo`, `ConfigurationError` |
| [multiple_chamber](API_REFERENCE_MULTIPLE.md) | Lattice processing | `MultipleChamber` |

---

## Module Overview

### [beam Module](API_REFERENCE_BEAM.md)

Handles particle beam parameters with relativistic calculations.

**Key Features:**
- Lorentz factor (γ) and relativistic beta (β) conversions
- Kinetic energy and momentum calculations
- Automatic parameter consistency
- Support for different particle types (proton, electron, etc.)

**Key Parameters:**
- `gammarel` - Lorentz gamma factor
- `betarel` - Relativistic beta (v/c)
- `Ekin_MeV` - Kinetic energy in MeV
- `p_MeV_c` - Momentum in MeV/c
- `mass_MeV_c2` - Rest mass in MeV/c²

**Quick Example:**
```python
from pytlwall import Beam

# LHC proton beam at 7 TeV
beam = Beam(gammarel=7460.52)
print(f"Beta: {beam.betarel:.10f}")
print(f"Energy: {beam.Ekin_MeV/1e6:.2f} TeV")
```

[→ Full beam Module Documentation](API_REFERENCE_BEAM.md)

---

### [frequencies Module](API_REFERENCE_FREQUENCIES.md)

Manages frequency arrays for impedance calculations.

**Key Features:**
- Logarithmic frequency spacing
- Explicit frequency lists
- Dynamic range adjustment
- Resolution control via fstep parameter

**Key Parameters:**
- `fmin` - Minimum frequency exponent (base 10)
- `fmax` - Maximum frequency exponent (base 10)
- `fstep` - Step exponent (larger = more points)
- `freq_list` - Explicit list of frequencies

**Quick Example:**
```python
from pytlwall import Frequencies

# Generate logarithmic frequency array (1 kHz to 1 GHz)
freqs = Frequencies(fmin=3, fmax=9, fstep=2)
print(f"Calculating at {len(freqs)} frequencies")
print(f"Range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
```

**Note:** Larger fstep values produce MORE frequency points (higher resolution).

[→ Full frequencies Module Documentation](API_REFERENCE_FREQUENCIES.md)

---

### [layer Module](API_REFERENCE_LAYER.md)

Defines material layers with electromagnetic properties.

**Key Features:**
- Frequency-dependent skin depth
- Surface impedance calculations
- Roughness effects (Hammerstad model)
- Multiple material types (conductors, vacuum, PEC)

**Key Parameters:**
- `layer_type` - 'CW' (conductor), 'V' (vacuum), 'PEC' (perfect conductor)
- `thick_m` - Layer thickness in meters
- `sigmaDC` - DC conductivity in S/m
- `RQ` - Surface roughness parameter
- `freq_Hz` - Frequency array for calculations

**Quick Example:**
```python
from pytlwall import Layer
import numpy as np

# Copper layer
freq = np.logspace(6, 9, 100)
copper = Layer(
    thick_m=0.001,
    sigmaDC=5.96e7,  # Copper conductivity
    freq_Hz=freq
)

# Get skin depth at 1 MHz
idx = np.argmin(np.abs(freq - 1e6))
print(f"Skin depth: {abs(copper.delta[idx])*1e6:.1f} μm")
```

[→ Full layer Module Documentation](API_REFERENCE_LAYER.md)

---

### [chamber Module](API_REFERENCE_CHAMBER.md)

Defines vacuum chamber geometries and calculates Yokoya correction factors.

**Key Features:**
- Circular, elliptical, and rectangular geometries
- Automatic Yokoya factor calculations
- Beta function integration
- Multi-layer support

**Key Parameters:**
- `pipe_rad_m` - Pipe radius (circular chambers)
- `pipe_hor_m`, `pipe_ver_m` - Half-apertures (elliptical/rectangular)
- `chamber_shape` - 'CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR'
- `betax`, `betay` - Optical beta functions
- `layers` - List of Layer objects

**Quick Example:**
```python
from pytlwall import Chamber

# Elliptical chamber
chamber = Chamber(
    pipe_hor_m=0.030,  # 30 mm horizontal
    pipe_ver_m=0.020,  # 20 mm vertical
    chamber_shape='ELLIPTICAL',
    betax=100.0,
    betay=50.0
)

print(f"Yokoya q: {chamber.yokoya_q:.4f}")
print(f"Long. factor: {chamber.long_yokoya_factor:.4f}")
```

[→ Full chamber Module Documentation](API_REFERENCE_CHAMBER.md)

---

### [tlwall Module](API_REFERENCE_TLWALL.md)

Main impedance calculation engine using transmission line method.

**Key Features:**
- Longitudinal and transverse impedance
- Dipolar and quadrupolar impedances with Yokoya factors
- Space charge impedances (direct and indirect)
- Multi-layer wall support
- Caching for efficient repeated access

**Key Impedances:**
| Property | Unit | Description |
|----------|------|-------------|
| `ZLong` | Ω | Longitudinal impedance |
| `ZTrans` | Ω/m | Transverse impedance |
| `ZDipX`, `ZDipY` | Ω | Dipolar impedances |
| `ZQuadX`, `ZQuadY` | Ω | Quadrupolar impedances |
| `ZLongSurf` | Ω | Longitudinal surface impedance |
| `ZTransSurf` | Ω | Transverse surface impedance |
| `ZLongDSC`, `ZTransDSC` | Ω, Ω/m | Direct space charge |
| `ZLongISC`, `ZTransISC` | Ω, Ω/m | Indirect space charge |
| `ZDipDSC`, `ZDipISC` | Ω/m | Dipolar space charge |

**Quick Example:**
```python
from pytlwall import TlWall, Chamber, Beam, Frequencies, Layer

freqs = Frequencies(fmin=3, fmax=9, fstep=2)
beam = Beam(gammarel=7460.52)
chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()

print(f"ZLong at 1 kHz: {abs(ZLong[0]):.3e} Ω")
```

[→ Full tlwall Module Documentation](API_REFERENCE_TLWALL.md)

---

### [cfg_io Module](API_REFERENCE_CFGIO.md)

Configuration file input/output for pytlwall calculations.

**Key Features:**
- Read/write INI-style configuration files
- Complete TlWall object creation from config
- Automatic shape alias normalization
- Support for frequency files and ranges

**Shape Aliases:**
- `ROUND` → `CIRCULAR`
- `ELLIPTIC` → `ELLIPTICAL`
- `RECT` / `RECTANGLE` → `RECTANGULAR`

**Quick Example:**
```python
from pytlwall.cfg_io import CfgIo

# Read configuration and create TlWall
cfg = CfgIo('config.ini')
wall = cfg.read_pytlwall()

# Calculate impedances
ZLong = wall.calc_ZLong()
```

[→ Full cfg_io Module Documentation](API_REFERENCE_CFGIO.md)

---

## Utility Modules

| Module | Purpose | Status |
|--------|---------|--------|
| logging_util | Logging system | ✅ Available |
| plot_util | Visualization tools | ✅ Available |
| output_util | Output formatting | ✅ Available |
| txt_util | Text I/O utilities | ✅ Available |

---

## Installation

```bash
pip install pytlwall
```

Or for development:

```bash
git clone https://github.com/CERN/pytlwall.git
cd pytlwall
pip install -e .
```

---

## Basic Workflow

### Step-by-Step Impedance Calculation

```python
from pytlwall import Beam, Frequencies, Layer, Chamber, TlWall
import numpy as np
import matplotlib.pyplot as plt

# ============================================
# STEP 1: Define Beam Parameters
# ============================================
beam = Beam(gammarel=7460.52)  # LHC 7 TeV protons
print(f"Beam: γ={beam.gammarel:.2f}, β={beam.betarel:.10f}")

# ============================================
# STEP 2: Define Frequency Range
# ============================================
freqs = Frequencies(fmin=3, fmax=9, fstep=2)
print(f"Frequencies: {len(freqs)} points, {freqs.freq[0]:.1e} to {freqs.freq[-1]:.1e} Hz")

# ============================================
# STEP 3: Define Chamber Geometry
# ============================================
chamber = Chamber(
    pipe_rad_m=0.022,
    pipe_len_m=1.0,
    chamber_shape='CIRCULAR',
    betax=100.0,
    betay=100.0,
    component_name='arc_chamber'
)
print(f"Chamber: {chamber.chamber_shape}, r={chamber.pipe_rad_m*1000:.1f} mm")

# ============================================
# STEP 4: Define Material Layers
# ============================================
# Copper coating on stainless steel
copper = Layer(
    thick_m=50e-6,  # 50 μm coating
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq
)
steel = Layer(
    thick_m=2e-3,  # 2 mm substrate
    sigmaDC=1.45e6,
    freq_Hz=freqs.freq
)
boundary = Layer(layer_type='PEC', boundary=True)

chamber.layers = [copper, steel, boundary]
print(f"Layers: {len(chamber.layers)} (Cu coating + SS + PEC)")

# ============================================
# STEP 5: Calculate Impedances
# ============================================
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)

ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()

print(f"\nResults:")
print(f"  ZLong range: {np.abs(ZLong).min():.2e} to {np.abs(ZLong).max():.2e} Ω")
print(f"  ZTrans range: {np.abs(ZTrans).min():.2e} to {np.abs(ZTrans).max():.2e} Ω/m")

# ============================================
# STEP 6: Visualize Results
# ============================================
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Longitudinal impedance
axes[0, 0].loglog(freqs.freq, np.real(ZLong), 'b-', label='Real')
axes[0, 0].loglog(freqs.freq, np.imag(ZLong), 'r--', label='Imag')
axes[0, 0].set_xlabel('Frequency [Hz]')
axes[0, 0].set_ylabel('ZLong [Ω]')
axes[0, 0].legend()
axes[0, 0].set_title('Longitudinal Impedance')
axes[0, 0].grid(True, alpha=0.3)

# Transverse impedance
axes[0, 1].loglog(freqs.freq, np.real(ZTrans), 'b-', label='Real')
axes[0, 1].loglog(freqs.freq, np.imag(ZTrans), 'r--', label='Imag')
axes[0, 1].set_xlabel('Frequency [Hz]')
axes[0, 1].set_ylabel('ZTrans [Ω/m]')
axes[0, 1].legend()
axes[0, 1].set_title('Transverse Impedance')
axes[0, 1].grid(True, alpha=0.3)

# Absolute values
axes[1, 0].loglog(freqs.freq, np.abs(ZLong), 'b-')
axes[1, 0].set_xlabel('Frequency [Hz]')
axes[1, 0].set_ylabel('|ZLong| [Ω]')
axes[1, 0].set_title('Longitudinal Impedance (Magnitude)')
axes[1, 0].grid(True, alpha=0.3)

axes[1, 1].loglog(freqs.freq, np.abs(ZTrans), 'r-')
axes[1, 1].set_xlabel('Frequency [Hz]')
axes[1, 1].set_ylabel('|ZTrans| [Ω/m]')
axes[1, 1].set_title('Transverse Impedance (Magnitude)')
axes[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('impedance_results.png', dpi=150)
plt.show()
```

---

## Additional Resources

### Package Documentation

- [Configuration Guide](ConfigModel.md) - Configuration file format
- [Logging Guide](LOGGING_README.md) - Logging system documentation
- [Examples](../examples/) - Complete usage examples

### Interactive Help

```python
# Module help
from pytlwall import tlwall
help(tlwall)

# Class help
help(tlwall.TlWall)

# Method help
help(tlwall.TlWall.calc_ZTrans)
```

---

## Version History

- **v2.0** (December 2025)
  - Complete refactoring to modern Python standards
  - Comprehensive documentation for all modules
  - Type hints and improved error handling
  - Extensive test coverage

- **v1.0** (Original)
  - Initial release

---

*Last updated: December 2025*
*For questions or issues, please refer to the project repository.*
*Copyright: CERN*
