# tlwall Module API Reference

## Overview

The `tlwall` module provides the `TlWall` class for calculating beam coupling impedances using the transmission line method with multi-layer vacuum chamber walls.

This is the main calculation engine of pytlwall, implementing the transmission line theory for computing longitudinal and transverse impedances including space charge effects.

## Table of Contents

- [Import](#import)
- [TlWall Class](#tlwall-class)
- [Impedance Properties](#impedance-properties)
- [Calculation Methods](#calculation-methods)
- [Utility Methods](#utility-methods)
- [Constants](#constants)
- [Exceptions](#exceptions)
- [Usage Examples](#usage-examples)
- [Physical Background](#physical-background)
- [See Also](#see-also)

---

## Import

```python
from pytlwall import TlWall
# or
from pytlwall.tlwall import TlWall, TlWallError, TlWallCalculationError, TlWallConfigurationError
```

---

## TlWall Class

### Class Definition

```python
class TlWall:
    """
    Transmission line wall impedance calculator.
    
    This class calculates longitudinal and transverse beam coupling
    impedances for multi-layer vacuum chamber walls using the
    transmission line method.
    """
```

### Constructor

```python
TlWall(
    chamber,
    beam,
    frequencies,
    accuracy_factor=0.3
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chamber` | `Chamber` | required | Chamber geometry with layers |
| `beam` | `Beam` | required | Beam parameters (gamma, beta, test_beam_shift) |
| `frequencies` | `Frequencies` | required | Frequency array for calculations |
| `accuracy_factor` | `float` | `0.3` | Accuracy factor for numerical corrections |

#### Raises

- `TlWallConfigurationError`: If chamber, beam, or frequencies are invalid
- `TlWallCalculationError`: If calculations fail

#### Example

```python
from pytlwall import TlWall, Chamber, Beam, Frequencies, Layer

# Setup components
freqs = Frequencies(fmin=3, fmax=9, fstep=2)
beam = Beam(gammarel=7460.52)
chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# Create TlWall
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
```

---

## Impedance Properties

All impedance properties return complex numpy arrays with length matching the frequency array.

### Primary Impedances

#### `ZLong`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Longitudinal impedance. Calculated on first access and cached.

**Formula:** ZLong = (L × KZeff) / (2π × r)

**Example:**

```python
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.ZLong
print(f"ZLong at 1 MHz: {abs(ZLong[0]):.3e} Ω")
```

---

#### `ZTrans`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm per meter (Ω/m)

**Description:** Transverse impedance. Calculated on first access and cached.

**Formula:** ZTrans = (2 × Zlongin × bypass) / (r² × β)

**Example:**

```python
ZTrans = wall.ZTrans
print(f"ZTrans at 1 GHz: {abs(ZTrans[-1]):.3e} Ω/m")
```

---

### Dipolar Impedances (with Yokoya Factors)

#### `ZDipX`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Horizontal dipolar impedance with Yokoya correction.

**Formula:** ZDipX = ZTrans × βx × drivx_yokoya_factor

---

#### `ZDipY`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Vertical dipolar impedance with Yokoya correction.

**Formula:** ZDipY = ZTrans × βy × drivy_yokoya_factor

---

### Quadrupolar Impedances

#### `ZQuadX`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Horizontal quadrupolar impedance with Yokoya correction.

**Formula:** ZQuadX = ZTrans × βx × detx_yokoya_factor

---

#### `ZQuadY`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Vertical quadrupolar impedance with Yokoya correction.

**Formula:** ZQuadY = ZTrans × βy × dety_yokoya_factor

---

### Surface Impedances

#### `ZLongSurf`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Longitudinal surface impedance (single-layer approximation).

---

#### `ZTransSurf`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm per meter (Ω/m)

**Description:** Transverse surface impedance (single-layer approximation).

---

### Space Charge Impedances

#### `ZLongDSC`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Longitudinal direct space charge impedance.

**Notes:** 
- Requires γ > 1.1 for meaningful calculation
- Pure imaginary for a smooth wall

---

#### `ZLongISC`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm (Ω)

**Description:** Longitudinal indirect space charge impedance.

---

#### `ZTransDSC`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm per meter (Ω/m)

**Description:** Transverse direct space charge impedance.

---

#### `ZTransISC`

**Type:** `np.ndarray` (complex)

**Unit:** Ohm per meter (Ω/m)

**Description:** Transverse indirect space charge impedance.

---

## Calculation Methods

### `calc_ZLong()`

```python
def calc_ZLong(self) -> np.ndarray
```

**Description:** Calculate longitudinal impedance.

**Returns:** Complex array of longitudinal impedance values in Ohms.

**Notes:**
- Result is cached in `_ZLong`
- Subsequent calls return cached value
- Uses transmission line method for multi-layer structures

**Example:**

```python
ZLong = wall.calc_ZLong()
print(f"Shape: {ZLong.shape}")
print(f"Max |ZLong|: {np.max(np.abs(ZLong)):.3e} Ω")
```

---

### `calc_ZTrans()`

```python
def calc_ZTrans(self) -> np.ndarray
```

**Description:** Calculate transverse impedance.

**Returns:** Complex array of transverse impedance values in Ω/m.

**Notes:**
- Result is cached in `_ZTrans`
- Depends on beam beta (relativistic factor)

---

### `calc_ZDipX()` / `calc_ZDipY()`

```python
def calc_ZDipX(self) -> np.ndarray
def calc_ZDipY(self) -> np.ndarray
```

**Description:** Calculate dipolar impedances with Yokoya factors.

**Returns:** Complex arrays in Ohms.

---

### `calc_ZQuadX()` / `calc_ZQuadY()`

```python
def calc_ZQuadX(self) -> np.ndarray
def calc_ZQuadY(self) -> np.ndarray
```

**Description:** Calculate quadrupolar impedances with Yokoya factors.

**Returns:** Complex arrays in Ohms.

---

### `calc_ZLongDSC()` / `calc_ZLongISC()`

```python
def calc_ZLongDSC(self) -> np.ndarray
def calc_ZLongISC(self) -> np.ndarray
```

**Description:** Calculate longitudinal space charge impedances.

**Returns:** Complex arrays in Ohms.

---

### `calc_ZTransDSC()` / `calc_ZTransISC()`

```python
def calc_ZTransDSC(self) -> np.ndarray
def calc_ZTransISC(self) -> np.ndarray
```

**Description:** Calculate transverse space charge impedances.

**Returns:** Complex arrays in Ω/m.

---

## Utility Methods

### `get_all_impedances()`

```python
def get_all_impedances(self) -> dict
```

**Description:** Calculate and return all impedances as a dictionary.

**Returns:** Dictionary with keys:
- `'ZLong'`, `'ZTrans'`
- `'ZDipX'`, `'ZDipY'`
- `'ZQuadX'`, `'ZQuadY'`
- `'ZLongSurf'`, `'ZTransSurf'`
- `'ZLongDSC'`, `'ZLongISC'`
- `'ZTransDSC'`, `'ZTransISC'`

**Example:**

```python
all_Z = wall.get_all_impedances()
for name, Z in all_Z.items():
    print(f"{name}: max = {np.max(np.abs(Z)):.3e}")
```

---

### `summary()`

```python
def summary(self) -> str
```

**Description:** Generate a configuration summary string.

**Returns:** Multi-line string with calculation parameters.

**Example:**

```python
print(wall.summary())
```

**Output:**
```
============================================================
TlWall Configuration Summary
============================================================
Chamber: CIRCULAR, radius=22.0 mm, length=1.000 m
Beam: γ=7460.52, β=0.9999999991
Frequencies: 1000 points, 1.00e+03 to 1.00e+09 Hz
Layers: 1 (Copper, 1.0 mm)
Accuracy factor: 0.3
============================================================
```

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `DEFAULT_ACCURACY_FACTOR` | 0.3 | Default accuracy factor |
| `MIN_GAMMA_FOR_SC` | 1.1 | Minimum γ for space charge calculations |
| `Z0` | 376.73... Ω | Impedance of free space |

---

## Exceptions

### `TlWallError`

```python
class TlWallError(Exception):
    """Base exception for TlWall errors."""
```

### `TlWallCalculationError`

```python
class TlWallCalculationError(TlWallError):
    """Raised when impedance calculation fails."""
```

### `TlWallConfigurationError`

```python
class TlWallConfigurationError(TlWallError):
    """Raised when TlWall configuration is invalid."""
```

---

## Usage Examples

### Example 1: Basic LHC-style Calculation

```python
from pytlwall import TlWall, Chamber, Beam, Frequencies, Layer
import numpy as np

# Setup
freqs = Frequencies(fmin=3, fmax=9, fstep=2)
beam = Beam(gammarel=7460.52)  # LHC 7 TeV
chamber = Chamber(
    pipe_rad_m=0.022,
    pipe_len_m=1.0,
    chamber_shape='CIRCULAR'
)

# Create copper layer
copper = Layer(
    thick_m=0.001,
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq
)
chamber.layers = [copper]

# Calculate impedances
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)

ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()

print(f"Calculated at {len(freqs)} frequencies")
print(f"ZLong range: {abs(ZLong[0]):.3e} to {abs(ZLong[-1]):.3e} Ω")
print(f"ZTrans range: {abs(ZTrans[0]):.3e} to {abs(ZTrans[-1]):.3e} Ω/m")
```

### Example 2: Elliptical Chamber with Yokoya Factors

```python
# Elliptical geometry
chamber = Chamber(
    pipe_hor_m=0.030,
    pipe_ver_m=0.020,
    pipe_len_m=2.0,
    chamber_shape='ELLIPTICAL',
    betax=100.0,
    betay=50.0
)

copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)

# Yokoya factors are automatically applied
print(f"Yokoya q: {chamber.yokoya_q:.4f}")
print(f"ZDipX max: {np.max(np.abs(wall.ZDipX)):.3e} Ω")
print(f"ZDipY max: {np.max(np.abs(wall.ZDipY)):.3e} Ω")
```

### Example 3: Multilayer Structure

```python
# Copper coating on stainless steel substrate
copper_coat = Layer(
    thick_m=50e-6,  # 50 μm coating
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq
)

steel_sub = Layer(
    thick_m=2e-3,  # 2 mm substrate
    sigmaDC=1.45e6,
    freq_Hz=freqs.freq
)

# PEC boundary (perfect conductor termination)
boundary = Layer(layer_type='PEC', boundary=True)

chamber.layers = [copper_coat, steel_sub, boundary]

wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()

print(f"Multilayer ZLong: {abs(ZLong[50]):.3e} Ω at f={freqs.freq[50]:.2e} Hz")
```

### Example 4: Space Charge Calculations

```python
# Lower energy beam where space charge is significant
low_energy_beam = Beam(gammarel=10.0)  # Low energy

wall = TlWall(
    chamber=chamber,
    beam=low_energy_beam,
    frequencies=freqs
)

# Space charge impedances
ZLongDSC = wall.ZLongDSC
ZTransDSC = wall.ZTransDSC

print(f"Direct space charge (longitudinal): {abs(ZLongDSC[0]):.3e} Ω")
print(f"Direct space charge (transverse): {abs(ZTransDSC[0]):.3e} Ω/m")
```

### Example 5: Export All Impedances

```python
import pandas as pd

wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
all_Z = wall.get_all_impedances()

# Create DataFrame for export
data = {'frequency': freqs.freq}
for name, Z in all_Z.items():
    data[f'{name}_real'] = Z.real
    data[f'{name}_imag'] = Z.imag
    data[f'{name}_abs'] = np.abs(Z)

df = pd.DataFrame(data)
df.to_csv('impedances.csv', index=False)
print(f"Exported {len(all_Z)} impedance types")
```

---

## Physical Background

### Transmission Line Method

The TlWall calculation uses the transmission line analogy where:
- Each material layer is treated as a transmission line segment
- The layers are cascaded using transfer matrices
- The effective surface impedance is computed from the cascade

### Impedance Types

| Type | Description | Unit |
|------|-------------|------|
| Longitudinal | Energy loss per turn | Ω |
| Transverse | Deflecting kick per offset | Ω/m |
| Dipolar | Coupled-bunch instabilities | Ω |
| Quadrupolar | Detuning with amplitude | Ω |
| Space Charge | Self-field effects | Ω, Ω/m |

### Yokoya Factors

For non-circular chambers, Yokoya factors correct the impedance:
- Derived from field solutions for elliptical/rectangular geometries
- Depend on chamber aspect ratio
- Different factors for longitudinal, dipolar, and quadrupolar impedances

### Space Charge

Space charge impedances represent:
- **Direct SC (DSC):** Self-field of the beam
- **Indirect SC (ISC):** Image charges in the chamber wall
- Significant at lower beam energies (low γ)
- Generally pure imaginary for smooth walls

---

## See Also

- [beam Module](API_REFERENCE_BEAM.md) - Beam parameters
- [frequencies Module](API_REFERENCE_FREQUENCIES.md) - Frequency arrays
- [layer Module](API_REFERENCE_LAYER.md) - Material layers
- [chamber Module](API_REFERENCE_CHAMBER.md) - Chamber geometry
- [cfg_io Module](API_REFERENCE_CFGIO.md) - Configuration file I/O
- [Main API Reference](API_REFERENCE.md) - Complete documentation

---

## References

1. L. Vos, "The Transverse Impedance of a Cylindrical Pipe with Arbitrary Surface Impedance", CERN-SL-95-36 (1995)
2. E. Métral et al., "Beam coupling impedance measurements and simulations", CERN Yellow Reports (2020)
3. K. Yokoya, "Resistive wall impedance of beam pipes of general cross section", Part. Accel. 41, 221 (1993)
4. B. Zotter and S. Kheifets, "Impedances and Wakes in High-Energy Particle Accelerators", World Scientific (1998)

---

*Last updated: December 2025*
