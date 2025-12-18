# chamber Module Examples

![PyTlWall Logo](logo005.png)

**Vacuum Chamber Geometries and Yokoya Factors**

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
| **chamber** | *You are here* |
| tlwall | [EXAMPLES_TLWALL.md](EXAMPLES_TLWALL.md) |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |

---

## Table of Contents

- [Overview](#overview)
- [Example 1: Circular Chamber](#example-1-circular-chamber)
- [Example 2: Elliptical Chamber](#example-2-elliptical-chamber)
- [Example 3: Rectangular Chamber](#example-3-rectangular-chamber)
- [Example 4: Geometry Comparison](#example-4-geometry-comparison)
- [Example 5: LHC Chamber Examples](#example-5-lhc-chamber-examples)
- [Example 6: Yokoya Factor Dependency](#example-6-yokoya-factor-dependency)
- [Example 7: Dynamic Modification](#example-7-dynamic-modification)
- [Example 8: Error Handling](#example-8-error-handling)
- [Shape Reference](#shape-reference)

---

## Overview

The `Chamber` class defines vacuum chamber geometries and automatically calculates Yokoya correction factors for non-circular cross-sections.

```python
import pytlwall

# Circular chamber
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022,        # Radius
    chamber_shape='CIRCULAR'
)

# Elliptical chamber
chamber = pytlwall.Chamber(
    pipe_hor_m=0.030,        # Horizontal half-aperture
    pipe_ver_m=0.020,        # Vertical half-aperture
    chamber_shape='ELLIPTICAL'
)
```

---

## Example 1: Circular Chamber

Most common geometry for beam pipes.

```python
import pytlwall

# Circular chamber (LHC-like)
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022,        # 22 mm radius
    pipe_len_m=1.0,          # 1 meter length
    chamber_shape='CIRCULAR',
    betax=100.0,             # Beta functions (m)
    betay=100.0,
    component_name='arc_dipole'
)

print(chamber.summary())

print(f"\nKey properties:")
print(f"  Radius:          {chamber.pipe_rad_m*1000:.1f} mm")
print(f"  Yokoya q:        {chamber.yokoya_q:.6f}")
print(f"  Long factor:     {chamber.long_yokoya_factor:.4f}")
print(f"  Driv_x factor:   {chamber.drivx_yokoya_factor:.4f}")
print(f"  Driv_y factor:   {chamber.drivy_yokoya_factor:.4f}")
```

**Notes:**
- Circular symmetry: horizontal = vertical = radius
- Yokoya q = 0 for circular chambers
- All Yokoya factors = 1.0 (no geometric correction)
- Simplest geometry for impedance calculations

---

## Example 2: Elliptical Chamber

Common in modern accelerators with flat chambers.

```python
import pytlwall

# Elliptical chamber with different apertures
chamber = pytlwall.Chamber(
    pipe_hor_m=0.030,        # 30 mm horizontal half-aperture
    pipe_ver_m=0.020,        # 20 mm vertical half-aperture
    pipe_len_m=1.0,
    chamber_shape='ELLIPTICAL',
    betax=50.0,
    betay=25.0,
    component_name='elliptical_section'
)

print(chamber.summary())

# Analyze aspect ratio
aspect_ratio = chamber.pipe_hor_m / chamber.pipe_ver_m
print(f"\nAspect ratio analysis:")
print(f"  Aspect ratio (h/v): {aspect_ratio:.2f}")
print(f"  Yokoya q:           {chamber.yokoya_q:.4f}")

print(f"\nYokoya corrections:")
print(f"  Longitudinal:       {chamber.long_yokoya_factor:.4f}")
print(f"  Horizontal driving: {chamber.drivx_yokoya_factor:.4f}")
print(f"  Vertical driving:   {chamber.drivy_yokoya_factor:.4f}")
```

**Use cases:**
- Flat chambers in modern colliders
- Accommodates beam separation
- Reduces vertical aperture where βy is small

---

## Example 3: Rectangular Chamber

For special applications like kickers and septa.

```python
import pytlwall

# Rectangular chamber
chamber = pytlwall.Chamber(
    pipe_hor_m=0.040,        # 40 mm horizontal half-width
    pipe_ver_m=0.015,        # 15 mm vertical half-height
    pipe_len_m=1.0,
    chamber_shape='RECTANGULAR',
    betax=30.0,
    betay=10.0,
    component_name='kicker_chamber'
)

print(chamber.summary())

print(f"\nGeometric properties:")
print(f"  Full width:   {chamber.pipe_hor_m*2*1000:.1f} mm")
print(f"  Full height:  {chamber.pipe_ver_m*2*1000:.1f} mm")
print(f"  Yokoya q:     {chamber.yokoya_q:.4f}")

# Get all Yokoya factors
factors = chamber.get_yokoya_factors()
print(f"\nAll Yokoya factors:")
for key, value in factors.items():
    print(f"  {key:15s}: {value:8.4f}")
```

**Use cases:**
- Kickers and septa
- Special insertion devices
- Strong geometric effects on impedance

---

## Example 4: Geometry Comparison

Comparing different chamber shapes with similar dimensions.

```python
import pytlwall

avg_dim = 0.025  # 25 mm average aperture

chambers = {
    'Circular': pytlwall.Chamber(
        pipe_rad_m=avg_dim,
        chamber_shape='CIRCULAR'
    ),
    'Elliptical (mild)': pytlwall.Chamber(
        pipe_hor_m=avg_dim * 1.2,
        pipe_ver_m=avg_dim * 0.8,
        chamber_shape='ELLIPTICAL'
    ),
    'Elliptical (flat)': pytlwall.Chamber(
        pipe_hor_m=avg_dim * 2.0,
        pipe_ver_m=avg_dim * 0.5,
        chamber_shape='ELLIPTICAL'
    ),
    'Rectangular': pytlwall.Chamber(
        pipe_hor_m=avg_dim * 1.5,
        pipe_ver_m=avg_dim * 0.67,
        chamber_shape='RECTANGULAR'
    )
}

print(f"Chamber comparison (avg aperture = {avg_dim*1000:.1f} mm):")
print(f"\n{'Geometry':<20} {'q param':>10} {'Long':>10} {'Driv_x':>10} {'Driv_y':>10}")
print("-" * 65)

for name, chamber in chambers.items():
    print(f"{name:<20} {chamber.yokoya_q:>10.4f} "
          f"{chamber.long_yokoya_factor:>10.4f} "
          f"{chamber.drivx_yokoya_factor:>10.4f} "
          f"{chamber.drivy_yokoya_factor:>10.4f}")
```

**Observations:**
- Yokoya q increases with aspect ratio (flatness)
- Circular chamber (q=0) has no geometric corrections
- Flat chambers have strongest corrections
- Rectangular differs from elliptical

---

## Example 5: LHC Chamber Examples

Realistic LHC chamber configurations.

```python
import pytlwall

# LHC Arc dipole
arc_dipole = pytlwall.Chamber(
    pipe_rad_m=0.022,        # 44 mm diameter beam screen
    pipe_len_m=14.3,         # Dipole length
    chamber_shape='CIRCULAR',
    betax=180.0,             # Typical arc optics
    betay=180.0,
    component_name='MB_dipole'
)

# LHC Interaction region
ir_triplet = pytlwall.Chamber(
    pipe_rad_m=0.021,        # 42 mm diameter
    pipe_len_m=4.0,
    chamber_shape='CIRCULAR',
    betax=0.55,              # IP beta* = 55 cm
    betay=0.55,
    component_name='IP1_triplet'
)

# LHC Injection kicker
injection = pytlwall.Chamber(
    pipe_rad_m=0.025,
    pipe_len_m=1.0,
    chamber_shape='CIRCULAR',
    betax=70.0,
    betay=70.0,
    component_name='MKI_kicker'
)

lhc_chambers = {
    'Arc Dipole':  arc_dipole,
    'IR Triplet':  ir_triplet,
    'Injection':   injection
}

print("LHC chamber configurations:\n")
for name, chamber in lhc_chambers.items():
    print(f"{name}:")
    print(f"  Shape:    {chamber.chamber_shape}")
    print(f"  Radius:   {chamber.pipe_rad_m*1000:.1f} mm")
    print(f"  Length:   {chamber.pipe_len_m:.1f} m")
    print(f"  βx/βy:    {chamber.betax:.1f}/{chamber.betay:.1f} m")
    print()
```

---

## Example 6: Yokoya Factor Dependency

Yokoya factors vs aspect ratio.

```python
import pytlwall
import numpy as np

# Test range of aspect ratios
aspect_ratios = [1.0, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0]
base_aperture = 0.020

print(f"Elliptical chamber - Yokoya factors vs aspect ratio:")
print(f"\n{'AR':>6} {'q':>10} {'Long':>10} {'Driv_x':>10} {'Driv_y':>10}")
print("-" * 50)

for ar in aspect_ratios:
    chamber = pytlwall.Chamber(
        pipe_hor_m=base_aperture * ar,
        pipe_ver_m=base_aperture,
        chamber_shape='ELLIPTICAL'
    )
    print(f"{ar:>6.1f} {chamber.yokoya_q:>10.4f} "
          f"{chamber.long_yokoya_factor:>10.4f} "
          f"{chamber.drivx_yokoya_factor:>10.4f} "
          f"{chamber.drivy_yokoya_factor:>10.4f}")

print(f"\nKey observations:")
print(f"  - q increases monotonically with aspect ratio")
print(f"  - Long factor decreases (impedance reduction)")
print(f"  - Driv_x increases, Driv_y decreases")
```

---

## Example 7: Dynamic Modification

Modifying chamber parameters during design optimization.

```python
import pytlwall

# Initial design
chamber = pytlwall.Chamber(
    pipe_rad_m=0.025,
    chamber_shape='CIRCULAR',
    component_name='initial_design'
)

print("Initial design:")
print(f"  Shape:   {chamber.chamber_shape}")
print(f"  Radius:  {chamber.pipe_rad_m*1000:.1f} mm")
print(f"  Yokoya q: {chamber.yokoya_q:.6f}")

# Modify to elliptical
print("\nModifying to elliptical chamber...")
chamber.chamber_shape = 'ELLIPTICAL'
chamber.pipe_hor_m = 0.035
chamber.pipe_ver_m = 0.020
chamber.component_name = 'optimized_design'

print("Updated design:")
print(f"  Shape:      {chamber.chamber_shape}")
print(f"  Horizontal: {chamber.pipe_hor_m*1000:.1f} mm")
print(f"  Vertical:   {chamber.pipe_ver_m*1000:.1f} mm")
print(f"  Yokoya q:   {chamber.yokoya_q:.4f}")
print(f"  Long factor: {chamber.long_yokoya_factor:.4f}")
```

**Use cases:**
- Design optimization studies
- Parameter scans
- Sensitivity analysis

---

## Example 8: Error Handling

Validation and error handling.

```python
import pytlwall

# Test 1: Invalid chamber shape
print("Test 1: Invalid chamber shape")
try:
    chamber = pytlwall.Chamber(chamber_shape='INVALID')
except pytlwall.chamber.ChamberShapeError as e:
    print(f"  ✓ Error caught: {e}")

# Test 2: Negative dimension
print("\nTest 2: Negative dimension")
try:
    chamber = pytlwall.Chamber(pipe_rad_m=-0.025)
except pytlwall.chamber.ChamberDimensionError as e:
    print(f"  ✓ Error caught: {e}")

# Test 3: Zero dimension
print("\nTest 3: Zero dimension")
try:
    chamber = pytlwall.Chamber(pipe_rad_m=0.0)
except pytlwall.chamber.ChamberDimensionError as e:
    print(f"  ✓ Error caught: {e}")

# Test 4: Invalid beta function
print("\nTest 4: Invalid beta function")
try:
    chamber = pytlwall.Chamber(betax=-10.0)
except pytlwall.chamber.ChamberDimensionError as e:
    print(f"  ✓ Error caught: {e}")

# Test 5: Valid chamber
print("\nTest 5: Valid chamber creation")
try:
    chamber = pytlwall.Chamber(
        pipe_rad_m=0.025,
        chamber_shape='CIRCULAR',
        betax=100.0,
        betay=50.0
    )
    print(f"  ✓ Chamber created: {chamber}")
except Exception as e:
    print(f"  ✗ Unexpected error: {e}")
```

---

## Shape Reference

### Supported Shapes

| Shape | Aliases | Description |
|-------|---------|-------------|
| `CIRCULAR` | `ROUND`, `CIRC` | Circular cross-section |
| `ELLIPTICAL` | `ELLIPTIC` | Elliptical cross-section |
| `RECTANGULAR` | `RECT`, `RECTANGLE` | Rectangular cross-section |

### Dimension Parameters

| Shape | Parameters |
|-------|------------|
| Circular | `pipe_rad_m` (radius) |
| Elliptical | `pipe_hor_m`, `pipe_ver_m` (half-apertures) |
| Rectangular | `pipe_hor_m`, `pipe_ver_m` (half-widths) |

### Yokoya Parameters

| Parameter | Description |
|-----------|-------------|
| `yokoya_q` | Asymmetry parameter (0 for circular) |
| `long_yokoya_factor` | Longitudinal impedance correction |
| `drivx_yokoya_factor` | Horizontal driving impedance correction |
| `drivy_yokoya_factor` | Vertical driving impedance correction |
| `detx_yokoya_factor` | Horizontal detuning correction |
| `dety_yokoya_factor` | Vertical detuning correction |

### Yokoya Factor Formulas

For elliptical chambers with aspect ratio q = (h-v)/(h+v):

$$F_{long} = 1 - 0.4 q^2$$

$$F_{driv,x} = 1 + 0.5 q$$

$$F_{driv,y} = 1 - 0.5 q$$

---

## See Also

- [API Reference - Chamber](API_REFERENCE_CHAMBER.md) - Complete API documentation
- [Chamber Shapes Reference](CHAMBER_SHAPES_REFERENCE.md) - Detailed shape information
- [Examples Main Page](EXAMPLES.md) - All module examples

---

**[◀ Back to Examples](EXAMPLES.md)** | **[◀ Previous: layer](EXAMPLES_LAYER.md)** | **[Next: tlwall ▶](EXAMPLES_TLWALL.md)**
