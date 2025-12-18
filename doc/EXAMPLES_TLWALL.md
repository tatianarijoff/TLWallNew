# tlwall Module Examples

![PyTlWall Logo](logo005.png)

**Main Impedance Calculation Engine**

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

---

## Navigation

**[◀ Back to Examples](EXAMPLES.md)**

| Module | Link |
|--------|------|
| beam | [EXAMPLES_BEAM.md](EXAMPLES_BEAM.md) |
| frequencies | [EXAMPLES_FREQUENCIES.md](EXAMPLES_FREQUENCIES.md) |
| layer | [EXAMPLES_LAYER.md](EXAMPLES_LAYER.md) |
| chamber | [EXAMPLES_CHAMBER.md](EXAMPLES_CHAMBER.md) |
| **tlwall** | *You are here* |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |

---

## Table of Contents

- [Overview](#overview)
- [Example 1: Basic Copper Chamber](#example-1-basic-copper-chamber)
- [Example 2: Elliptical Chamber with Yokoya](#example-2-elliptical-chamber-with-yokoya)
- [Example 3: Multi-layer Coating](#example-3-multi-layer-coating)
- [Example 4: Space Charge Effects](#example-4-space-charge-effects)
- [Example 5: All Impedances](#example-5-all-impedances)
- [Example 6: Summary and Info](#example-6-summary-and-info)
- [Impedance Reference](#impedance-reference)

---

## Overview

The `TlWall` class is the main impedance calculation engine. It combines:
- Beam parameters
- Chamber geometry
- Material layers
- Frequency array

To compute longitudinal and transverse impedances using the transmission line method.

```python
import pytlwall

# Setup components
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# Create calculator and get impedances
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.ZLong    # Longitudinal impedance
ZTrans = wall.ZTrans  # Transverse impedance
```

---

## Example 1: Basic Copper Chamber

LHC-style circular copper chamber.

```python
import pytlwall

# Setup
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)  # LHC 7 TeV protons
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# Calculate impedances
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()

print(f"Configuration:")
print(f"  Beam: LHC protons, γ = {beam.gammarel:.2f}")
print(f"  Chamber: circular, r = {chamber.pipe_rad_m*1000:.1f} mm")
print(f"  Layer: copper, t = {copper.thick_m*1000:.1f} mm")
print(f"  Frequencies: {len(freqs)} points")

print(f"\nResults:")
print(f"  ZLong at 1 kHz:  {abs(ZLong[0]):.3e} Ω")
print(f"  ZLong at 1 GHz:  {abs(ZLong[-1]):.3e} Ω")
print(f"  ZTrans at 1 kHz: {abs(ZTrans[0]):.3e} Ω/m")
print(f"  ZTrans at 1 GHz: {abs(ZTrans[-1]):.3e} Ω/m")
```

---

## Example 2: Elliptical Chamber with Yokoya

Non-circular chamber with Yokoya correction factors.

```python
import pytlwall
import numpy as np

# Setup
freqs = pytlwall.Frequencies(fmin=6, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(
    pipe_hor_m=0.030,     # 30 mm horizontal
    pipe_ver_m=0.020,     # 20 mm vertical
    chamber_shape='ELLIPTICAL',
    betax=100.0,
    betay=50.0
)
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# Calculate
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)

print(f"Configuration:")
print(f"  Chamber: elliptical, {chamber.pipe_hor_m*1000:.1f} × {chamber.pipe_ver_m*1000:.1f} mm")
print(f"  Yokoya q: {chamber.yokoya_q:.4f}")
print(f"  Beta functions: βx = {chamber.betax:.1f} m, βy = {chamber.betay:.1f} m")

# Dipolar and quadrupolar impedances
idx = np.argmin(np.abs(freqs.freq - 1e6))
print(f"\nImpedances at 1 MHz:")
print(f"  ZDipX:  {abs(wall.ZDipX[idx]):.3e} Ω")
print(f"  ZDipY:  {abs(wall.ZDipY[idx]):.3e} Ω")
print(f"  ZQuadX: {abs(wall.ZQuadX[idx]):.3e} Ω")
print(f"  ZQuadY: {abs(wall.ZQuadY[idx]):.3e} Ω")

print(f"\nNote: Dipolar/quadrupolar differ due to Yokoya factors")
```

---

## Example 3: Multi-layer Coating

Copper coating on stainless steel substrate.

```python
import pytlwall

# Setup
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')

# Multi-layer: thin copper coating + thick steel substrate
copper_coating = pytlwall.Layer(
    thick_m=50e-6,       # 50 μm copper coating
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq
)
steel_substrate = pytlwall.Layer(
    thick_m=2e-3,        # 2 mm stainless steel
    sigmaDC=1.45e6,
    freq_Hz=freqs.freq
)
chamber.layers = [copper_coating, steel_substrate]

# Calculate
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()

print(f"Multi-layer configuration:")
print(f"  Layer 1: copper coating, t = {copper_coating.thick_m*1e6:.1f} μm")
print(f"  Layer 2: steel substrate, t = {steel_substrate.thick_m*1000:.1f} mm")

print(f"\nLongitudinal Impedance:")
for i in [0, len(freqs)//2, -1]:
    print(f"  f = {freqs.freq[i]:.2e} Hz: |ZLong| = {abs(ZLong[i]):.3e} Ω")
```

**Notes:**
- At high frequencies: skin depth << coating thickness → copper dominates
- At low frequencies: current penetrates into steel → higher impedance

---

## Example 4: Space Charge Effects

Space charge impedances at low beam energy.

```python
import pytlwall
import numpy as np

# Setup - low energy beam for significant space charge
freqs = pytlwall.Frequencies(fmin=3, fmax=7, fstep=2)

beam_low = pytlwall.Beam(gammarel=10.0)     # Low energy
beam_high = pytlwall.Beam(gammarel=7460.52) # High energy (LHC)

chamber = pytlwall.Chamber(pipe_rad_m=0.050, chamber_shape='CIRCULAR')
aluminum = pytlwall.Layer(thick_m=0.001, sigmaDC=3.77e7, freq_Hz=freqs.freq)
chamber.layers = [aluminum]

# Calculate for both beams
wall_low = pytlwall.TlWall(chamber=chamber, beam=beam_low, frequencies=freqs)
wall_high = pytlwall.TlWall(chamber=chamber, beam=beam_high, frequencies=freqs)

idx = np.argmin(np.abs(freqs.freq - 1e7))
print(f"Space charge at 10 MHz:")

print(f"\nLow energy (γ = {beam_low.gammarel:.1f}):")
print(f"  ZLongDSC:  {abs(wall_low.ZLongDSC[idx]):.3e} Ω")
print(f"  ZLongISC:  {abs(wall_low.ZLongISC[idx]):.3e} Ω")
print(f"  ZTransDSC: {abs(wall_low.ZTransDSC[idx]):.3e} Ω/m")
print(f"  ZTransISC: {abs(wall_low.ZTransISC[idx]):.3e} Ω/m")

print(f"\nHigh energy (γ = {beam_high.gammarel:.1f}):")
print(f"  ZLongDSC:  {abs(wall_high.ZLongDSC[idx]):.3e} Ω (negligible)")
print(f"  ZLongISC:  {abs(wall_high.ZLongISC[idx]):.3e} Ω (negligible)")
```

**Notes:**
- Space charge scales as 1/γ²
- Significant only at low energy (γ ~ 1-100)
- Negligible at ultra-relativistic energies (LHC)

---

## Example 5: All Impedances

Get all available impedances at once.

```python
import pytlwall

# Setup
freqs = pytlwall.Frequencies(fmin=6, fmax=8, fstep=1)
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022,
    chamber_shape='CIRCULAR',
    betax=100.0,
    betay=100.0
)
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# Calculate all impedances
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
all_Z = wall.get_all_impedances()

print(f"All impedances at f = {freqs.freq[0]:.2e} Hz:")
print(f"\n  {'Impedance':<15} {'Magnitude':<15} {'Unit'}")
print(f"  {'-'*15} {'-'*15} {'-'*10}")

units = {
    'ZLong': 'Ω', 'ZTrans': 'Ω/m',
    'ZDipX': 'Ω', 'ZDipY': 'Ω',
    'ZQuadX': 'Ω', 'ZQuadY': 'Ω',
    'ZLongSurf': 'Ω', 'ZTransSurf': 'Ω',
    'ZLongDSC': 'Ω', 'ZLongISC': 'Ω',
    'ZTransDSC': 'Ω/m', 'ZTransISC': 'Ω/m',
    'ZDipDSC': 'Ω/m', 'ZDipISC': 'Ω/m'
}

for name, Z in all_Z.items():
    unit = units.get(name, '')
    print(f"  {name:<15} {abs(Z[0]):<15.3e} {unit}")
```

---

## Example 6: Summary and Info

Using summary and utility methods.

```python
import pytlwall

# Setup
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = pytlwall.Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)

# Trigger calculations
_ = wall.ZLong
_ = wall.ZTrans

# Display summary
print(wall.summary())

# Object representation
print(f"\nObject representation:")
print(f"  {repr(wall)}")
```

---

## Impedance Reference

### Wall Impedances

| Property | Method | Unit | Description |
|----------|--------|------|-------------|
| `ZLong` | `calc_ZLong()` | Ω | Longitudinal wall impedance |
| `ZTrans` | `calc_ZTrans()` | Ω/m | Transverse wall impedance |
| `ZLongSurf` | - | Ω | Surface longitudinal |
| `ZTransSurf` | - | Ω | Surface transverse |

### Dipolar and Quadrupolar

| Property | Unit | Description |
|----------|------|-------------|
| `ZDipX` | Ω | Horizontal dipolar (driving) |
| `ZDipY` | Ω | Vertical dipolar (driving) |
| `ZQuadX` | Ω | Horizontal quadrupolar (detuning) |
| `ZQuadY` | Ω | Vertical quadrupolar (detuning) |

### Space Charge Impedances

| Property | Method | Unit | Description |
|----------|--------|------|-------------|
| `ZLongDSC` | `calc_ZLongDSC()` | Ω | Long. direct space charge |
| `ZLongISC` | `calc_ZLongISC()` | Ω | Long. indirect space charge |
| `ZTransDSC` | `calc_ZTransDSC()` | Ω/m | Trans. direct space charge |
| `ZTransISC` | `calc_ZTransISC()` | Ω/m | Trans. indirect space charge |
| `ZDipDSC` | - | Ω/m | Dipolar direct space charge |
| `ZDipISC` | - | Ω/m | Dipolar indirect space charge |

### Accessing Impedances

Two equivalent ways:

```python
# Via property (lazy calculation)
ZLong = wall.ZLong

# Via method
ZLong = wall.calc_ZLong()
```

Properties cache results - calling them multiple times doesn't recalculate.

### Impedance Relationships

For circular chamber:
- `ZDipX = ZDipY = ZTrans × β`
- `ZQuadX = ZQuadY = 0` (in ultra-relativistic limit)

For non-circular chamber:
- Yokoya factors modify the relationships
- `ZDipX ≠ ZDipY` in general

---

## Complete Workflow Example

```python
import pytlwall
import numpy as np

# 1. Setup frequencies
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)

# 2. Setup beam
beam = pytlwall.Beam(gammarel=7460.52)

# 3. Setup chamber
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022,
    chamber_shape='CIRCULAR',
    betax=100.0,
    betay=100.0,
    pipe_len_m=1.0
)

# 4. Setup layers
copper = pytlwall.Layer(
    thick_m=0.001,
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq
)
chamber.layers = [copper]

# 5. Create calculator
wall = pytlwall.TlWall(
    chamber=chamber,
    beam=beam,
    frequencies=freqs
)

# 6. Get impedances
ZLong = wall.ZLong
ZTrans = wall.ZTrans

# 7. Analyze results
idx_max = np.argmax(np.abs(ZLong))
print(f"Peak ZLong: {abs(ZLong[idx_max]):.3e} Ω at {freqs.freq[idx_max]:.2e} Hz")

# 8. Export or plot...
```

---

## See Also

- [API Reference - TlWall](API_REFERENCE_TLWALL.md) - Complete API documentation
- [Examples Main Page](EXAMPLES.md) - All module examples

---

**[◀ Back to Examples](EXAMPLES.md)** | **[◀ Previous: chamber](EXAMPLES_CHAMBER.md)** | **[Next: logging ▶](EXAMPLES_LOGGING.md)**
