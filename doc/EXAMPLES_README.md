# PyTlWall Examples Documentation

![PyTlWall Logo](logo005.png)

**Usage Examples for PyTlWall Modules**

This document provides comprehensive examples for using the main PyTlWall modules.

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

---

## Table of Contents

- [Beam Module Examples](#beam-module-examples)
- [Frequencies Module Examples](#frequencies-module-examples)
- [Layer Module Examples](#layer-module-examples)
- [Chamber Module Examples](#chamber-module-examples)
- [TlWall Module Examples](#tlwall-module-examples)
- [Logging Module Examples](#logging-module-examples)

---

## Beam Module Examples

The `Beam` class handles particle beam parameters with automatic relativistic calculations.

### Example 1: LHC Proton Beam

```python
import pytlwall

# LHC protons at 7 TeV kinetic energy
lhc_beam = pytlwall.Beam(Ekin_MeV=7e6)

print(f"Beta (v/c):    {lhc_beam.betarel:.12f}")
print(f"Gamma:         {lhc_beam.gammarel:.2f}")
print(f"Momentum:      {lhc_beam.p_MeV_c:.2e} MeV/c")
print(f"Velocity:      {lhc_beam.velocity_m_s:.6e} m/s")
```

### Example 2: Electron Beam

```python
# Electron at 1 GeV (specify mass)
electron_mass = 0.511  # MeV/c²
electron_beam = pytlwall.Beam(Ekin_MeV=1000, mass_MeV_c2=electron_mass)

print(f"Gamma: {electron_beam.gammarel:.1f}")
print(f"Beta:  {electron_beam.betarel:.10f}")
```

### Example 3: Initialize from Different Parameters

```python
# From gamma
beam1 = pytlwall.Beam(gammarel=7460.52)

# From beta
beam2 = pytlwall.Beam(betarel=0.999999)

# From momentum
beam3 = pytlwall.Beam(p_MeV_c=1000)

# All parameters are automatically consistent
print(f"Beam1 energy: {beam1.Ekin_MeV:.2e} MeV")
print(f"Beam2 gamma:  {beam2.gammarel:.2f}")
print(f"Beam3 beta:   {beam3.betarel:.6f}")
```

### Example 4: Error Handling

```python
try:
    # Beta > 1 is physically impossible
    beam = pytlwall.Beam(betarel=1.5)
except pytlwall.BeamValidationError as e:
    print(f"Error: {e}")

try:
    # Gamma < 1 is impossible for massive particles
    beam = pytlwall.Beam(gammarel=0.5)
except pytlwall.BeamValidationError as e:
    print(f"Error: {e}")
```

### Key Parameters

| Parameter | Description | Unit |
|-----------|-------------|------|
| `gammarel` | Lorentz gamma factor | - |
| `betarel` | Relativistic beta (v/c) | - |
| `Ekin_MeV` | Kinetic energy | MeV |
| `p_MeV_c` | Momentum | MeV/c |
| `mass_MeV_c2` | Rest mass (default: proton) | MeV/c² |
| `E_tot_MeV` | Total energy | MeV |
| `velocity_m_s` | Velocity | m/s |

---

## Frequencies Module Examples

The `Frequencies` class manages frequency arrays for impedance calculations.

### Example 1: Logarithmic Frequency Array

```python
import pytlwall

# Create array from 1 kHz to 1 GHz
# fmin, fmax are exponents (10^fmin to 10^fmax)
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)

print(f"Number of points: {len(freqs)}")
print(f"Range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
```

### Example 2: Explicit Frequency List

```python
# Specific frequencies (e.g., resonant modes)
resonances = [455e3, 1.2e6, 2.8e6, 5.5e6, 12.0e6, 25.0e6]
freqs = pytlwall.Frequencies(freq_list=resonances)

print(f"Points: {len(freqs)}")
# Frequencies are automatically sorted
```

### Example 3: Resolution Comparison

```python
# IMPORTANT: Larger fstep = MORE points (higher resolution)

freqs_low = pytlwall.Frequencies(fmin=3, fmax=6, fstep=1)   # Low resolution
freqs_med = pytlwall.Frequencies(fmin=3, fmax=6, fstep=2)   # Medium
freqs_high = pytlwall.Frequencies(fmin=3, fmax=6, fstep=3)  # High resolution

print(f"fstep=1: {len(freqs_low)} points (low res)")
print(f"fstep=2: {len(freqs_med)} points (medium)")
print(f"fstep=3: {len(freqs_high)} points (high res)")
```

### Example 4: Dynamic Update

```python
# Start with broad scan
freqs = pytlwall.Frequencies(fmin=0, fmax=10, fstep=1)
print(f"Broad scan: {len(freqs)} points")

# Zoom in on interesting region with higher resolution
freqs.update_from_exponents(fmin=6, fmax=8, fstep=3)
print(f"Detailed scan: {len(freqs)} points")
```

### Resolution Guide

| fstep | Resolution | Use Case |
|-------|------------|----------|
| 1 | Low (fewer points) | Quick scans, initial analysis |
| 2 | Medium | Standard calculations |
| 3 | High (more points) | Detailed analysis, convergence |

**Note:** Larger `fstep` = MORE points per decade

---

## Layer Module Examples

The `Layer` class defines material layers with electromagnetic properties.

### Example 1: Copper Layer

```python
import pytlwall
import numpy as np

# Define frequency range
freq = np.logspace(3, 9, 100)  # 1 kHz to 1 GHz

# Create copper layer
copper = pytlwall.Layer(
    layer_type='CW',
    thick_m=0.001,       # 1 mm thickness
    sigmaDC=5.96e7,      # Copper conductivity (S/m)
    freq_Hz=freq
)

# Properties at 1 MHz
idx = np.argmin(np.abs(freq - 1e6))
print(f"Skin depth at 1 MHz: {abs(copper.delta[idx])*1e6:.2f} μm")
print(f"Surface resistance:  {copper.RS[idx].real:.3e} Ω")
```

### Example 2: Stainless Steel with Roughness

```python
freq = np.logspace(3, 9, 100)

steel = pytlwall.Layer(
    layer_type='CW',
    thick_m=0.002,       # 2 mm
    sigmaDC=1.45e6,      # Stainless steel conductivity
    RQ=1e-6,             # 1 μm surface roughness
    freq_Hz=freq
)

# Roughness increases surface resistance at high frequencies
```

### Example 3: Vacuum Boundary

```python
# Vacuum boundary (outer boundary in multi-layer)
vacuum = pytlwall.Layer(boundary=True)

print(f"Type: {vacuum.layer_type}")  # 'V' for vacuum
```

### Example 4: Perfect Conductor (PEC)

```python
# Perfect electrical conductor (theoretical limit)
pec = pytlwall.Layer(layer_type='PEC')

# Zero surface resistance, zero skin depth
```

### Example 5: Multi-layer Structure

```python
freq = np.logspace(3, 9, 100)

# Layer 1: Thin copper coating
copper_coating = pytlwall.Layer(
    thick_m=50e-6,       # 50 μm
    sigmaDC=5.96e7,
    freq_Hz=freq
)

# Layer 2: Steel substrate
steel_substrate = pytlwall.Layer(
    thick_m=2e-3,        # 2 mm
    sigmaDC=1.45e6,
    freq_Hz=freq
)

# Layer 3: Vacuum boundary
boundary = pytlwall.Layer(boundary=True)

# Assign to chamber
chamber.layers = [copper_coating, steel_substrate, boundary]
```

### Common Material Conductivities

| Material | σ (S/m) | Notes |
|----------|---------|-------|
| Copper | 5.96×10⁷ | Excellent conductor |
| Aluminum | 3.77×10⁷ | Good conductor |
| Stainless Steel | 1.45×10⁶ | Poor conductor, common in UHV |
| Titanium | 2.38×10⁶ | |

---

## Chamber Module Examples

The `Chamber` class defines vacuum chamber geometries and Yokoya factors.

### Example 1: Circular Chamber

```python
import pytlwall

chamber = pytlwall.Chamber(
    pipe_rad_m=0.022,        # 22 mm radius
    pipe_len_m=1.0,          # 1 m length
    chamber_shape='CIRCULAR',
    betax=100.0,             # Beta functions
    betay=100.0,
    component_name='arc_dipole'
)

print(f"Yokoya q: {chamber.yokoya_q}")  # 0 for circular
print(f"Long factor: {chamber.long_yokoya_factor}")  # 1.0
```

### Example 2: Elliptical Chamber

```python
chamber = pytlwall.Chamber(
    pipe_hor_m=0.030,        # 30 mm horizontal
    pipe_ver_m=0.020,        # 20 mm vertical
    chamber_shape='ELLIPTICAL',
    betax=50.0,
    betay=25.0
)

print(f"Aspect ratio: {chamber.pipe_hor_m / chamber.pipe_ver_m:.2f}")
print(f"Yokoya q: {chamber.yokoya_q:.4f}")
print(f"Long factor: {chamber.long_yokoya_factor:.4f}")
```

### Example 3: Rectangular Chamber

```python
chamber = pytlwall.Chamber(
    pipe_hor_m=0.040,        # 40 mm half-width
    pipe_ver_m=0.015,        # 15 mm half-height
    chamber_shape='RECTANGULAR'
)

# Get all Yokoya factors
factors = chamber.get_yokoya_factors()
for name, value in factors.items():
    print(f"{name}: {value:.4f}")
```

### Example 4: Shape Comparison

```python
avg_dim = 0.025  # 25 mm

circular = pytlwall.Chamber(
    pipe_rad_m=avg_dim,
    chamber_shape='CIRCULAR'
)

elliptical = pytlwall.Chamber(
    pipe_hor_m=avg_dim * 1.5,
    pipe_ver_m=avg_dim * 0.67,
    chamber_shape='ELLIPTICAL'
)

print(f"Circular q:    {circular.yokoya_q:.4f}")
print(f"Elliptical q:  {elliptical.yokoya_q:.4f}")
```

### Supported Shapes

| Shape | Aliases | Yokoya q |
|-------|---------|----------|
| CIRCULAR | ROUND, CIRC | 0 |
| ELLIPTICAL | ELLIPTIC | > 0 |
| RECTANGULAR | RECT, RECTANGLE | > 0 |

---

## TlWall Module Examples

The `TlWall` class is the main impedance calculation engine.

### Example 1: Basic Copper Chamber

```python
import pytlwall

# Setup
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)  # LHC 7 TeV
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# Calculate impedances
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()

print(f"ZLong at 1 kHz:  {abs(ZLong[0]):.3e} Ω")
print(f"ZTrans at 1 GHz: {abs(ZTrans[-1]):.3e} Ω/m")
```

### Example 2: Elliptical Chamber with Yokoya Factors

```python
freqs = pytlwall.Frequencies(fmin=6, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(
    pipe_hor_m=0.030,
    pipe_ver_m=0.020,
    chamber_shape='ELLIPTICAL',
    betax=100.0,
    betay=50.0
)
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)

# Access dipolar and quadrupolar impedances
print(f"ZDipX:  {abs(wall.ZDipX[0]):.3e} Ω")
print(f"ZDipY:  {abs(wall.ZDipY[0]):.3e} Ω")
print(f"ZQuadX: {abs(wall.ZQuadX[0]):.3e} Ω")
print(f"ZQuadY: {abs(wall.ZQuadY[0]):.3e} Ω")
```

### Example 3: Multi-layer Structure

```python
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')

# Copper coating on stainless steel
copper = pytlwall.Layer(thick_m=50e-6, sigmaDC=5.96e7, freq_Hz=freqs.freq)
steel = pytlwall.Layer(thick_m=2e-3, sigmaDC=1.45e6, freq_Hz=freqs.freq)
chamber.layers = [copper, steel]

wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()
```

### Example 4: Space Charge Effects

```python
# Low energy beam for significant space charge
freqs = pytlwall.Frequencies(fmin=3, fmax=7, fstep=2)
beam = pytlwall.Beam(gammarel=10.0)  # Low energy
chamber = pytlwall.Chamber(pipe_rad_m=0.050, chamber_shape='CIRCULAR')
aluminum = pytlwall.Layer(thick_m=0.001, sigmaDC=3.77e7, freq_Hz=freqs.freq)
chamber.layers = [aluminum]

wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)

# Space charge impedances
print(f"ZLongDSC:  {abs(wall.ZLongDSC[0]):.3e} Ω")
print(f"ZLongISC:  {abs(wall.ZLongISC[0]):.3e} Ω")
print(f"ZTransDSC: {abs(wall.ZTransDSC[0]):.3e} Ω/m")
print(f"ZTransISC: {abs(wall.ZTransISC[0]):.3e} Ω/m")
```

### Example 5: Get All Impedances

```python
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
all_Z = wall.get_all_impedances()

for name, Z in all_Z.items():
    print(f"{name}: {abs(Z[0]):.3e}")
```

### Available Impedances

| Property | Method | Unit | Description |
|----------|--------|------|-------------|
| `ZLong` | `calc_ZLong()` | Ω | Longitudinal |
| `ZTrans` | `calc_ZTrans()` | Ω/m | Transverse |
| `ZDipX`, `ZDipY` | - | Ω | Dipolar |
| `ZQuadX`, `ZQuadY` | - | Ω | Quadrupolar |
| `ZLongDSC` | `calc_ZLongDSC()` | Ω | Long. direct space charge |
| `ZLongISC` | `calc_ZLongISC()` | Ω | Long. indirect space charge |
| `ZTransDSC` | `calc_ZTransDSC()` | Ω/m | Trans. direct space charge |
| `ZTransISC` | `calc_ZTransISC()` | Ω/m | Trans. indirect space charge |

---

## Logging Module Examples

The `logging_util` module provides centralized logging for PyTlWall.

### Example 1: Quick Setup

```python
from pytlwall import logging_util

# Quick setup - returns log path and logger
log_path, logger = logging_util.quick_setup(
    log_dir="./my_logs/",
    log_basename="my_calculation",
    verbosity=2,
)

logger.info("Starting calculation...")
logger.warning("This is a warning")
logger.info("Calculation completed")

print(f"Log saved to: {log_path}")
```

### Example 2: Detailed Configuration

```python
from pytlwall import logging_util

config = logging_util.LogConfig(
    log_dir="./my_logs/",
    log_basename="detailed_calculation",
    verbosity=3,  # DEBUG level
    add_timestamp=True,
    console_output=True,
)

log_path = logging_util.setup_logging(config)
logger = logging_util.get_logger(__name__)

logger.debug("Debug message (verbosity >= 3)")
logger.info("Info message (verbosity >= 2)")
logger.warning("Warning message (verbosity >= 1)")
logger.error("Error message (always visible)")
```

### Example 3: Section Headers

```python
from pytlwall import logging_util

log_path, logger = logging_util.quick_setup(
    log_dir="./my_logs/",
    log_basename="organized",
    verbosity=2,
)

logging_util.log_section_header(logger, "STARTING CALCULATION")

logging_util.log_section_header(logger, "Configuration", char="-", width=60)
logger.info("Chamber radius: 50 mm")
logger.info("Frequency range: 1e3 - 1e9 Hz")

logging_util.log_section_header(logger, "Results", char="-", width=60)
logger.info("Maximum ZLong: 1.23e-3 Ohm")

logging_util.log_section_header(logger, "COMPLETED")
```

### Example 4: File-Only Logging

```python
from pytlwall import logging_util

config = logging_util.LogConfig(
    log_dir="./my_logs/",
    log_basename="silent",
    verbosity=2,
    console_output=False,  # No console output
)

log_path = logging_util.setup_logging(config)
logger = logging_util.get_logger(__name__)

# Messages only go to file
logger.info("This appears only in the log file")
```

### Verbosity Levels

| Level | Messages Shown |
|-------|----------------|
| 0 | ERROR only |
| 1 | ERROR, WARNING |
| 2 | ERROR, WARNING, INFO |
| 3 | ERROR, WARNING, INFO, DEBUG |

---

## Running the Examples

Each example module can be run directly:

```bash
# Run beam examples
python examples/example_beam_usage.py

# Run frequencies examples
python examples/example_frequencies_usage.py

# Run layer examples
python examples/example_layer_usage.py

# Run chamber examples
python examples/example_chamber_usage.py

# Run tlwall examples
python examples/example_tlwall_usage.py

# Run logging examples
python examples/example_logging_usage.py
```

---

## Quick Reference

### Minimal Impedance Calculation

```python
import pytlwall

# 1. Frequencies
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)

# 2. Beam
beam = pytlwall.Beam(gammarel=7460.52)

# 3. Chamber with layer
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# 4. Calculate
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.ZLong
ZTrans = wall.ZTrans
```

---

*Last updated: December 2025*
