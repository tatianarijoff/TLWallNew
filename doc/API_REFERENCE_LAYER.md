# layer Module API Reference

## Overview

The `layer` module provides the `Layer` class for defining material layers with electromagnetic properties in vacuum chambers.

The `Layer` class represents a material layer with frequency-dependent electrical and magnetic properties. It calculates skin depth, surface impedance, and other parameters essential for impedance calculations in particle accelerators.

Layers can represent:
- Conductive materials (copper, stainless steel, aluminum)
- Vacuum boundaries
- Perfect electrical conductors (PEC)
- Dielectric materials

## Table of Contents

- [Import](#import)
- [Layer Class](#layer-class)
- [Basic Properties](#basic-properties)
- [Calculated Properties](#calculated-properties)
- [Methods](#methods)
- [Material Constants](#material-constants)
- [Usage Examples](#usage-examples)
- [Notes and Conventions](#notes-and-conventions)
- [See Also](#see-also)

---

## Import

```python
from pytlwall import Layer
# or
from pytlwall.layer import Layer, LayerValidationError
```

---

## Layer Class

### Class Definition

```python
class Layer:
    """
    Represents a material layer in a vacuum chamber with
    frequency-dependent electromagnetic properties.
    """
```

### Constructor

```python
Layer(
    layer_type='CW',
    thick_m=0.01,
    muinf_Hz=0.0,
    epsr=1.0,
    sigmaDC=1e6,
    k_Hz=inf,
    tau=0.0,
    RQ=0.0,
    freq_Hz=None,
    boundary=False
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `layer_type` | `str` | `'CW'` | Layer type: 'CW' (conductor), 'V' (vacuum), 'PEC' (perfect conductor) |
| `thick_m` | `float` | `0.01` | Layer thickness in meters (must be positive) |
| `muinf_Hz` | `float` | `0.0` | Magnetic permeability parameter |
| `epsr` | `float` | `1.0` | Relative permittivity (dielectric constant, must be positive) |
| `sigmaDC` | `float` | `1e6` | DC electrical conductivity in S/m (must be non-negative) |
| `k_Hz` | `float` | `inf` | Relaxation frequency for permeability in Hz |
| `tau` | `float` | `0.0` | Relaxation time for permittivity in seconds |
| `RQ` | `float` | `0.0` | Surface roughness parameter in meters |
| `freq_Hz` | `array-like` | `None` | Frequency array in Hz for calculations |
| `boundary` | `bool` | `False` | If True, creates vacuum boundary layer |

#### Examples

```python
from pytlwall import Layer
import numpy as np

# Copper layer
copper = Layer(
    layer_type='CW',
    thick_m=0.001,  # 1 mm
    sigmaDC=5.96e7,  # Copper conductivity
    freq_Hz=np.logspace(3, 9, 100)
)

# Stainless steel with roughness
steel = Layer(
    thick_m=0.002,  # 2 mm
    sigmaDC=1.45e6,  # SS conductivity
    RQ=1e-6,  # 1 micron roughness
    freq_Hz=np.logspace(3, 9, 100)
)

# Vacuum boundary
vacuum = Layer(boundary=True)

# Perfect conductor
pec = Layer(layer_type='PEC')
```

---

## Basic Properties

### `layer_type`

**Type:** `str`

**Description:** Layer type identifier.

**Valid values:**
- `'CW'`: Conductor (default)
- `'V'`: Vacuum
- `'PEC'`: Perfect electrical conductor

**Example:**

```python
layer = Layer(layer_type='CW')
print(layer.layer_type)  # Output: 'CW'
```

---

### `thick_m`

**Type:** `float`

**Description:** Layer thickness in meters.

**Validation:** Must be positive (> 0).

**Example:**

```python
layer = Layer(thick_m=0.001)  # 1 mm
print(f"Thickness: {layer.thick_m*1000} mm")
```

---

### `sigmaDC`

**Type:** `float`

**Description:** DC electrical conductivity in S/m (Siemens per meter).

**Validation:** Must be non-negative (≥ 0).

**Typical values:**
- Copper: 5.96×10⁷ S/m
- Aluminum: 3.77×10⁷ S/m
- Stainless Steel: 1.45×10⁶ S/m
- Insulator: 0 S/m

**Example:**

```python
copper = Layer(sigmaDC=5.96e7)
print(f"Copper conductivity: {copper.sigmaDC:.2e} S/m")
```

---

### `epsr`

**Type:** `float`

**Description:** Relative permittivity (dielectric constant).

**Validation:** Must be positive (> 0).

**Typical values:**
- Vacuum/Air: 1.0
- Teflon: ~2.1
- Alumina: ~9.0

**Example:**

```python
layer = Layer(epsr=1.0)  # Vacuum
print(f"Relative permittivity: {layer.epsr}")
```

---

### `RQ`

**Type:** `float`

**Description:** Surface roughness parameter in meters.

**Validation:** Must be non-negative (≥ 0).

**Notes:**
- RQ = 0: Perfectly smooth surface
- RQ > 0: Rough surface (increases resistance at high frequencies)
- Typical values: 0.1 μm to 10 μm

**Example:**

```python
rough = Layer(RQ=1e-6)  # 1 micron roughness
smooth = Layer(RQ=0.0)  # Smooth surface
```

---

### `freq_Hz`

**Type:** `np.ndarray`

**Description:** Frequency array in Hz for property calculations.

**Validation:** All frequencies must be positive.

**Example:**

```python
import numpy as np
freq = np.logspace(6, 9, 100)  # 1 MHz to 1 GHz
layer = Layer(freq_Hz=freq)
print(f"Number of frequencies: {len(layer.freq_Hz)}")
```

---

## Calculated Properties

All calculated properties are computed on-demand and returned as numpy arrays with length matching `freq_Hz`.

### `sigmaAC`

**Type:** `np.ndarray` (complex)

**Description:** Frequency-dependent AC conductivity.

**Formula:** σ_AC = σ_DC_R / (1 + j·2π·τ·f)

**Example:**

```python
layer = Layer(sigmaDC=5.96e7, freq_Hz=np.logspace(6, 9, 10))
sigmaAC = layer.sigmaAC
print(f"AC conductivity at first freq: {abs(sigmaAC[0]):.2e} S/m")
```

---

### `delta`

**Type:** `np.ndarray` (complex)

**Description:** Skin depth in meters.

**Formula:** δ = √[2 / (2πfμσ_AC + j·με(2πf)²)]

**Notes:**
- Penetration depth of electromagnetic fields
- Decreases with frequency: δ ∝ 1/√f
- Real part gives effective penetration depth

**Example:**

```python
copper = Layer(sigmaDC=5.96e7, freq_Hz=np.array([1e6]))
delta = abs(copper.delta[0])
print(f"Skin depth at 1 MHz: {delta*1e6:.1f} μm")
# Expected: ~66 μm for copper
```

---

### `RS`

**Type:** `np.ndarray` (real)

**Description:** Surface resistance in Ohms, including roughness effects.

**Formula:** Rs = √(μπf/σ_DC) · [1 + (2/π)·arctan(0.7·μ·2πf·σ_DC·RQ²)]

**Notes:**
- Increases with frequency: Rs ∝ √f
- Roughness term (Hammerstad model) increases resistance
- Important for cavity Q-factor and beam-induced heating

**Example:**

```python
layer = Layer(sigmaDC=5.96e7, RQ=0, freq_Hz=np.array([1e9]))
RS = layer.RS[0].real
print(f"Surface resistance at 1 GHz: {RS:.3e} Ω")
```

---

### `KZ`

**Type:** `np.ndarray` (complex)

**Description:** Surface impedance.

**Formula (default):** KZ = (1 + j) / (σ_PM · δ_M)

**Notes:**
- Complex quantity: resistance + reactance
- Can be set directly or calculated
- Use `set_surf_imped()` to interpolate measured data

**Example:**

```python
layer = Layer(sigmaDC=5.96e7, freq_Hz=np.logspace(6, 9, 10))
KZ = layer.KZ
print(f"Surface impedance: {KZ[0]:.3e}")
```

---

### `eps`

**Type:** `float`

**Description:** Absolute permittivity in F/m.

**Formula:** ε = ε₀ · εᵣ

**Example:**

```python
layer = Layer(epsr=2.0)
print(f"Absolute permittivity: {layer.eps:.3e} F/m")
```

---

### `mu`

**Type:** `np.ndarray` (complex)

**Description:** Absolute permeability in H/m (frequency-dependent).

**Formula:** μ = μ₀ · μᵣ

**Example:**

```python
layer = Layer(freq_Hz=np.logspace(6, 9, 10))
mu = layer.mu
print(f"Permeability at first freq: {abs(mu[0]):.3e} H/m")
```

---

### `mur`

**Type:** `np.ndarray` (complex)

**Description:** Relative permeability (frequency-dependent).

**Formula:** μᵣ = 1 + μ_inf / (1 + j·f/k)

---

### `sigmaPM`

**Type:** `np.ndarray` (real)

**Description:** Effective conductivity magnitude in S/m.

**Formula:** σ_PM = √[(2πfε)² + |σ_AC|²]

---

### `deltaM`

**Type:** `np.ndarray` (complex)

**Description:** Modified skin depth in meters.

**Formula:** δ_M = √[2 / (2πfμσ_AC - j·με(2πf)²)]

---

### `kprop`

**Type:** `np.ndarray` (complex)

**Description:** Propagation constant in 1/m.

**Formula:** k = (1 - j) / δ

---

## Methods

### `set_surf_imped(newfreq_Hz, newKZ)`

Set surface impedance with interpolation to layer frequencies.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `newfreq_Hz` | `array-like` | Frequency array for impedance data (Hz) |
| `newKZ` | `array-like` | Complex surface impedance at those frequencies |

**Returns:** None (modifies object in place)

**Raises:** `LayerValidationError` if data is invalid

**Example:**

```python
layer = Layer(freq_Hz=np.logspace(6, 9, 100))

# Set impedance from measurements at specific frequencies
measured_freq = np.array([1e6, 1e8, 1e9])
measured_KZ = np.array([1e-3+1e-3j, 5e-3+5e-3j, 1e-2+1e-2j])

layer.set_surf_imped(measured_freq, measured_KZ)
# Now layer.KZ is interpolated to all 100 frequencies
```

---

## Material Constants

### Typical Conductivity Values

| Material | Conductivity (S/m) | Notes |
|----------|-------------------|-------|
| Silver | 6.30×10⁷ | Best conductor |
| Copper | 5.96×10⁷ | Standard for RF |
| Gold | 4.52×10⁷ | Corrosion resistant |
| Aluminum | 3.77×10⁷ | Lightweight |
| Brass | 1.57×10⁷ | Cu-Zn alloy |
| Stainless Steel 304 | 1.45×10⁶ | Common vacuum chamber |
| Stainless Steel 316L | 1.35×10⁶ | Low carbon variant |

### Skin Depth at 1 MHz

| Material | Skin Depth |
|----------|------------|
| Copper | ~66 μm |
| Aluminum | ~84 μm |
| Stainless Steel | ~830 μm |

**Formula:** δ = √(2/(ωμσ)) = √(1/(πfμσ))

---

## Usage Examples

### Example 1: Copper Vacuum Chamber

```python
import numpy as np
from pytlwall import Layer

# Define frequency range
freq = np.logspace(3, 9, 100)  # 1 kHz to 1 GHz

# Create copper layer
copper = Layer(
    thick_m=0.001,  # 1 mm wall thickness
    sigmaDC=5.96e7,
    freq_Hz=freq
)

# Calculate skin depth at different frequencies
for f in [1e6, 1e7, 1e8, 1e9]:
    idx = np.argmin(np.abs(freq - f))
    delta = abs(copper.delta[idx])
    print(f"Skin depth at {f/1e6} MHz: {delta*1e6:.1f} μm")
```

### Example 2: Roughness Effect

```python
freq = np.logspace(6, 9, 50)

# Smooth surface
smooth = Layer(sigmaDC=5.96e7, RQ=0.0, freq_Hz=freq)

# Rough surface (1 micron RMS roughness)
rough = Layer(sigmaDC=5.96e7, RQ=1e-6, freq_Hz=freq)

# Compare surface resistance at 1 GHz
idx = -1  # Last frequency point
print(f"Smooth: {smooth.RS[idx].real:.3e} Ω")
print(f"Rough:  {rough.RS[idx].real:.3e} Ω")
print(f"Increase: {(rough.RS[idx]/smooth.RS[idx] - 1)*100:.1f}%")
```

### Example 3: Multilayer Preparation

```python
# Prepare layers for multilayer impedance calculation
freq = np.logspace(3, 9, 100)

# All layers must share the same frequency array
layers = [
    Layer(thick_m=50e-6, sigmaDC=5.96e7, freq_Hz=freq),  # Cu coating
    Layer(thick_m=2e-3, sigmaDC=1.45e6, freq_Hz=freq),   # SS substrate
    Layer(boundary=True)  # Vacuum boundary
]

print(f"Created {len(layers)}-layer structure")
```

### Example 4: Custom Surface Impedance

```python
# Create layer
freq = np.logspace(6, 9, 100)
layer = Layer(sigmaDC=5.96e7, freq_Hz=freq)

# Option 1: Use calculated impedance (default)
KZ_calc = layer.KZ

# Option 2: Set from measurements
measured_freq = np.array([1e6, 1e7, 1e8, 1e9])
measured_KZ = np.array([1e-3+1e-3j, 3e-3+3e-3j, 8e-3+8e-3j, 1.5e-2+1.5e-2j])
layer.set_surf_imped(measured_freq, measured_KZ)

# Now layer.KZ uses interpolated measured data
```

---

## Notes and Conventions

### Frequency Dependence

Most properties vary with frequency:
- **Skin depth:** δ ∝ 1/√f (decreases)
- **Surface resistance:** Rs ∝ √f (increases)  
- **AC conductivity:** Complex, frequency-dependent
- **Permeability:** Can be frequency-dependent (if μ_inf ≠ 0)

### Roughness Model

Uses Hammerstad roughness correction:
- Increases surface resistance
- Effect more pronounced at high frequencies
- RQ typically 0.1-10 μm for machined surfaces

### Coordinate System

- Thickness measured perpendicular to surface
- Surface normal assumed in z-direction
- Layering from inner (beam) to outer (vacuum)

### Physical Constants

| Constant | Symbol | Value |
|----------|--------|-------|
| Permeability of vacuum | μ₀ | 4π×10⁻⁷ H/m |
| Permittivity of vacuum | ε₀ | 8.854×10⁻¹² F/m |

---

## See Also

- [beam Module](API_REFERENCE_BEAM.md) - Beam parameters affecting impedance
- [frequencies Module](API_REFERENCE_FREQUENCIES.md) - Frequency array management
- [chamber Module](API_REFERENCE_CHAMBER.md) - Chamber geometry
- [Main API Reference](API_REFERENCE.md) - Complete API documentation

---

*Last updated: December 2025*
