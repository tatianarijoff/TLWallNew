# layer Module Examples

![PyTlWall Logo](logo005.png)

**Material Layer Definitions with Electromagnetic Properties**

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
| **layer** | *You are here* |
| chamber | [EXAMPLES_CHAMBER.md](EXAMPLES_CHAMBER.md) |
| tlwall | [EXAMPLES_TLWALL.md](EXAMPLES_TLWALL.md) |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |

---

## Table of Contents

- [Overview](#overview)
- [Example 1: Copper Layer](#example-1-copper-layer)
- [Example 2: Stainless Steel with Roughness](#example-2-stainless-steel-with-roughness)
- [Example 3: Vacuum Boundary](#example-3-vacuum-boundary)
- [Example 4: Material Comparison](#example-4-material-comparison)
- [Example 5: Skin Depth vs Frequency](#example-5-skin-depth-vs-frequency)
- [Example 6: Surface Impedance](#example-6-surface-impedance)
- [Example 7: Multi-layer Structure](#example-7-multi-layer-structure)
- [Example 8: Perfect Conductor (PEC)](#example-8-perfect-conductor-pec)
- [Material Reference](#material-reference)

---

## Overview

The `Layer` class defines material layers with electromagnetic properties for vacuum chamber walls. Each layer has:

- Thickness
- DC conductivity
- Relative permittivity
- Optional surface roughness
- Frequency-dependent skin depth and surface resistance

```python
import pytlwall
import numpy as np

freq = np.logspace(3, 9, 100)  # 1 kHz to 1 GHz

layer = pytlwall.Layer(
    layer_type='CW',     # Conducting wall
    thick_m=0.001,       # 1 mm thickness
    sigmaDC=5.96e7,      # Copper conductivity (S/m)
    epsr=1.0,            # Relative permittivity
    freq_Hz=freq         # Frequency array
)
```

---

## Example 1: Copper Layer

High conductivity metal, common in RF applications.

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
    epsr=1.0,
    freq_Hz=freq
)

print(f"Copper layer parameters:")
print(f"  Type:              {copper.layer_type}")
print(f"  Thickness:         {copper.thick_m*1000:.2f} mm")
print(f"  DC Conductivity:   {copper.sigmaDC:.2e} S/m")
print(f"  Relative εᵣ:       {copper.epsr}")

# Properties at 1 MHz
idx_1MHz = np.argmin(np.abs(freq - 1e6))
print(f"\nProperties at 1 MHz:")
print(f"  Skin depth δ:      {abs(copper.delta[idx_1MHz])*1e6:.2f} μm")
print(f"  Surface resistance: {copper.RS[idx_1MHz].real:.3e} Ω")

# Properties at 1 GHz
idx_1GHz = np.argmin(np.abs(freq - 1e9))
print(f"\nProperties at 1 GHz:")
print(f"  Skin depth δ:      {abs(copper.delta[idx_1GHz])*1e6:.2f} μm")
print(f"  Surface resistance: {copper.RS[idx_1GHz].real:.3e} Ω")
```

**Notes:**
- Copper has excellent conductivity (5.96×10⁷ S/m)
- Skin depth decreases with frequency
- Common in RF cavities and beam pipes

---

## Example 2: Stainless Steel with Roughness

Lower conductivity material with surface roughness effects.

```python
import pytlwall
import numpy as np

freq = np.logspace(3, 9, 100)

# Stainless steel with roughness
steel = pytlwall.Layer(
    layer_type='CW',
    thick_m=0.002,       # 2 mm thickness
    sigmaDC=1.45e6,      # Stainless steel conductivity
    RQ=1e-6,             # 1 μm surface roughness
    freq_Hz=freq
)

# Compare with smooth surface
steel_smooth = pytlwall.Layer(
    thick_m=0.002,
    sigmaDC=1.45e6,
    RQ=0.0,              # Smooth surface
    freq_Hz=freq
)

print(f"Stainless steel layer:")
print(f"  Thickness:         {steel.thick_m*1000:.2f} mm")
print(f"  DC Conductivity:   {steel.sigmaDC:.2e} S/m")
print(f"  Surface roughness: {steel.RQ*1e6:.2f} μm")

idx_1GHz = np.argmin(np.abs(freq - 1e9))
print(f"\nSurface resistance at 1 GHz:")
print(f"  Smooth surface:    {steel_smooth.RS[idx_1GHz].real:.3e} Ω")
print(f"  Rough surface:     {steel.RS[idx_1GHz].real:.3e} Ω")

increase = (steel.RS[idx_1GHz].real / steel_smooth.RS[idx_1GHz].real - 1) * 100
print(f"  Roughness increase: {increase:.1f}%")
```

**Notes:**
- Stainless steel has ~40x lower conductivity than copper
- Surface roughness increases resistance at high frequencies
- Effect more pronounced when δ ~ RQ

---

## Example 3: Vacuum Boundary

Outer boundary for multi-layer calculations.

```python
import pytlwall

# Create vacuum boundary
vacuum = pytlwall.Layer(boundary=True)

print(f"Vacuum boundary parameters:")
print(f"  Type:              {vacuum.layer_type}")  # 'V'
print(f"  DC Conductivity:   {vacuum.sigmaDC:.2e} S/m")
print(f"  Relative εᵣ:       {vacuum.epsr}")
```

**Notes:**
- Automatically sets type to 'V' (vacuum)
- Used as outer boundary in multi-layer structures
- Represents free space outside the chamber

---

## Example 4: Material Comparison

Comparing different materials at the same frequency.

```python
import pytlwall
import numpy as np

freq = np.logspace(6, 9, 50)  # 1 MHz to 1 GHz

# Define materials
materials = {
    'Copper':           {'sigmaDC': 5.96e7},
    'Aluminum':         {'sigmaDC': 3.77e7},
    'Stainless Steel':  {'sigmaDC': 1.45e6},
}

layers = {}
for name, props in materials.items():
    layers[name] = pytlwall.Layer(
        thick_m=0.001,
        sigmaDC=props['sigmaDC'],
        freq_Hz=freq
    )

print(f"Material comparison:")
print(f"\nConductivity:")
for name, layer in layers.items():
    print(f"  {name:20s}: {layer.sigmaDC:.2e} S/m")

idx_10MHz = np.argmin(np.abs(freq - 1e7))
print(f"\nSkin depth at 10 MHz:")
for name, layer in layers.items():
    delta = abs(layer.delta[idx_10MHz]) * 1e6  # μm
    print(f"  {name:20s}: {delta:.1f} μm")

idx_1GHz = np.argmin(np.abs(freq - 1e9))
print(f"\nSurface resistance at 1 GHz:")
for name, layer in layers.items():
    RS = layer.RS[idx_1GHz].real
    print(f"  {name:20s}: {RS:.3e} Ω")
```

**Key observations:**
- Better conductors have smaller skin depth
- Better conductors have lower surface resistance
- Stainless steel has significantly higher losses

---

## Example 5: Skin Depth vs Frequency

Skin depth dependence on frequency.

```python
import pytlwall
import numpy as np

freq = np.logspace(3, 9, 100)  # 1 kHz to 1 GHz
copper = pytlwall.Layer(sigmaDC=5.96e7, freq_Hz=freq)

delta = abs(copper.delta)

print(f"Copper skin depth variation with frequency:")
print(f"\n{'Frequency':>12} {'Skin Depth':>15}")
print("-" * 30)

test_frequencies = [1e3, 1e4, 1e5, 1e6, 1e7, 1e8, 1e9]
for f in test_frequencies:
    idx = np.argmin(np.abs(freq - f))
    d = delta[idx]
    
    if d > 1e-3:
        d_str = f"{d*1000:.2f} mm"
    elif d > 1e-6:
        d_str = f"{d*1e6:.2f} μm"
    else:
        d_str = f"{d*1e9:.2f} nm"
    
    print(f"{f:>12.0e} {d_str:>15}")

print(f"\nTheoretical relationship:")
print(f"  δ ∝ 1/√f")
print(f"  Doubling frequency reduces skin depth by √2 ≈ 1.41")
```

---

## Example 6: Surface Impedance

Surface impedance calculation and custom setting.

```python
import pytlwall
import numpy as np

freq = np.logspace(6, 9, 50)
copper = pytlwall.Layer(sigmaDC=5.96e7, freq_Hz=freq)

# Get automatically calculated surface impedance
KZ = copper.KZ

idx_10MHz = np.argmin(np.abs(freq - 1e7))
idx_1GHz = np.argmin(np.abs(freq - 1e9))

print(f"Surface impedance (calculated):")
print(f"\n  At 10 MHz:")
print(f"    Real part:      {KZ[idx_10MHz].real:.3e} Ω")
print(f"    Imaginary part: {KZ[idx_10MHz].imag:.3e} Ω")

print(f"\n  At 1 GHz:")
print(f"    Real part:      {KZ[idx_1GHz].real:.3e} Ω")
print(f"    Imaginary part: {KZ[idx_1GHz].imag:.3e} Ω")

# Set custom surface impedance (e.g., from measurements)
print(f"\nSetting custom surface impedance from measurements:")
measured_freq = np.array([1e6, 1e8, 1e9])
measured_KZ = np.array([1e-3+1e-3j, 5e-3+5e-3j, 1e-2+1e-2j])

copper.set_surf_imped(measured_freq, measured_KZ)
print(f"  ✓ Interpolated to {len(freq)} frequency points")
```

**Notes:**
- Surface impedance is complex (resistance + reactance)
- Can be calculated from material properties or set from measurements
- `set_surf_imped()` interpolates measured data to the frequency array

---

## Example 7: Multi-layer Structure

Building a coated chamber wall.

```python
import pytlwall
import numpy as np

freq = np.logspace(3, 9, 100)

print(f"Creating vacuum chamber with coating:")

# Layer 1: Inner copper coating (thin)
layer1 = pytlwall.Layer(
    layer_type='CW',
    thick_m=50e-6,       # 50 μm copper coating
    sigmaDC=5.96e7,
    freq_Hz=freq
)
print(f"\n  Layer 1 - Copper coating:")
print(f"    Thickness:     {layer1.thick_m*1e6:.1f} μm")
print(f"    Conductivity:  {layer1.sigmaDC:.2e} S/m")

# Layer 2: Stainless steel substrate (thick)
layer2 = pytlwall.Layer(
    layer_type='CW',
    thick_m=2e-3,        # 2 mm stainless steel
    sigmaDC=1.45e6,
    freq_Hz=freq
)
print(f"\n  Layer 2 - Stainless steel substrate:")
print(f"    Thickness:     {layer2.thick_m*1000:.1f} mm")
print(f"    Conductivity:  {layer2.sigmaDC:.2e} S/m")

# Layer 3: Vacuum boundary
layer3 = pytlwall.Layer(boundary=True)
print(f"\n  Layer 3 - Vacuum boundary:")
print(f"    Type:          {layer3.layer_type}")

# Assign to chamber
print(f"\nAssign to chamber:")
print(f"  chamber.layers = [layer1, layer2, layer3]")
```

**Notes:**
- Multiple layers model complex structures
- Inner layer affects high-frequency impedance
- Outer layers important at low frequencies
- All layers must share the same frequency array

---

## Example 8: Perfect Conductor (PEC)

Ideal conductor for theoretical calculations.

```python
import pytlwall

# Create PEC layer
pec = pytlwall.Layer(layer_type='PEC')

print(f"Perfect conductor parameters:")
print(f"  Type:              {pec.layer_type}")
print(f"  Conductivity:      Infinite (σ → ∞)")
print(f"  Skin depth:        Zero (δ → 0)")
print(f"  Surface resistance: Zero (Rs → 0)")

print(f"\nUse cases:")
print(f"  - Theoretical calculations")
print(f"  - Comparison benchmark")
print(f"  - Ideal cavity analysis")
print(f"  - Validation of code limits")
```

---

## Material Reference

### Common Materials

| Material | σ (S/m) | Notes |
|----------|---------|-------|
| Copper | 5.96×10⁷ | Excellent conductor, RF cavities |
| Aluminum | 3.77×10⁷ | Good conductor, lightweight |
| Gold | 4.10×10⁷ | Corrosion resistant |
| Silver | 6.30×10⁷ | Best conductor |
| Stainless Steel | 1.45×10⁶ | UHV compatible, poor conductor |
| Titanium | 2.38×10⁶ | Light, strong |

### Layer Types

| Type | Description |
|------|-------------|
| `CW` | Conducting wall (default) |
| `PEC` | Perfect electric conductor |
| `V` | Vacuum (boundary) |

### Key Formulas

**Skin depth:**
$$\delta = \sqrt{\frac{2}{\omega \mu \sigma}}$$

**Surface resistance:**
$$R_s = \frac{1}{\sigma \delta}$$

**Relationship:**
- δ ∝ 1/√f (skin depth decreases with frequency)
- Rs ∝ √f (surface resistance increases with frequency)

---

## See Also

- [API Reference - Layer](API_REFERENCE_LAYER.md) - Complete API documentation
- [Examples Main Page](EXAMPLES.md) - All module examples

---

**[◀ Back to Examples](EXAMPLES.md)** | **[◀ Previous: frequencies](EXAMPLES_FREQUENCIES.md)** | **[Next: chamber ▶](EXAMPLES_CHAMBER.md)**
