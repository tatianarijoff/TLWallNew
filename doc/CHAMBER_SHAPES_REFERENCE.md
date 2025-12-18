# Chamber Shapes Reference

## Overview

This document describes the supported chamber shapes in pytlwall and their aliases for configuration files.

## Table of Contents

1. [Valid Chamber Shapes](#valid-chamber-shapes)
2. [Shape Aliases](#shape-aliases)
3. [Configuration Examples](#configuration-examples)
4. [Shape-Specific Parameters](#shape-specific-parameters)
5. [Yokoya Factors by Shape](#yokoya-factors-by-shape)
6. [Validation and Error Handling](#validation-and-error-handling)
7. [Migration Guide](#migration-guide)
8. [FAQ](#faq)

---

## Valid Chamber Shapes

pytlwall supports three fundamental chamber geometries:

### 1. CIRCULAR

Cylindrical vacuum chamber with circular cross-section.

**Properties:**
- Single radius defines the geometry
- Simplest geometry for calculations
- Most common in accelerators
- Azimuthally symmetric
- Yokoya factors = 1.0 (no correction needed)

**Required Parameters:**
- `pipe_radius_m` or `pipe_rad_m`

**Use Cases:**
- Most beam pipes in straight sections
- Simple cylindrical chambers
- Circular collimators

---

### 2. ELLIPTICAL

Elliptical cross-section chamber.

**Properties:**
- Two semi-axes (horizontal and vertical)
- Common in flat beam scenarios
- Different Yokoya factors than circular
- Asymmetric impedance (different horizontal/vertical)

**Required Parameters:**
- `pipe_hor_m` (horizontal semi-axis)
- `pipe_ver_m` (vertical semi-axis)

**Use Cases:**
- Flat beam chambers
- Insertion regions
- Elliptical vacuum chambers

---

### 3. RECTANGULAR

Rectangular cross-section chamber.

**Properties:**
- Four flat walls
- Highest impedance per unit size
- Complex field patterns
- Distinct Yokoya factors

**Required Parameters:**
- `pipe_hor_m` (half-width)
- `pipe_ver_m` (half-height)

**Use Cases:**
- Kicker magnets
- Some septum chambers
- Rectangular collimators
- Special insertion devices

---

## Shape Aliases

For convenience and backward compatibility, the following aliases are supported:

### Alias Mapping Table

| Official Name | Aliases | Status |
|--------------|---------|--------|
| CIRCULAR | ROUND | ✅ Supported |
| ELLIPTICAL | ELLIPTIC | ✅ Supported |
| RECTANGULAR | RECT, RECTANGLE | ✅ Supported |

### Normalization Rules

1. All shape names are **case-sensitive** in config files (use UPPERCASE)
2. Aliases are automatically normalized to official names
3. Unknown shapes raise `ChamberShapeError`

**Normalization Examples:**
```python
# Input: 'ROUND' → Normalized: 'CIRCULAR'
# Input: 'ELLIPTIC' → Normalized: 'ELLIPTICAL'
# Input: 'RECT' → Normalized: 'RECTANGULAR'
# Input: 'RECTANGLE' → Normalized: 'RECTANGULAR'
```

---

## Configuration Examples

### CIRCULAR Chamber

```ini
[base_info]
chamber_shape = CIRCULAR
pipe_radius_m = 0.022
```

**Equivalent configurations:**
```ini
# Using alias
chamber_shape = ROUND
pipe_radius_m = 0.022

# Alternative parameter name
chamber_shape = CIRCULAR
pipe_rad_m = 0.022
```

---

### ELLIPTICAL Chamber

```ini
[base_info]
chamber_shape = ELLIPTICAL
pipe_hor_m = 0.030
pipe_ver_m = 0.020
```

**Using alias:**
```ini
chamber_shape = ELLIPTIC
pipe_hor_m = 0.030
pipe_ver_m = 0.020
```

---

### RECTANGULAR Chamber

```ini
[base_info]
chamber_shape = RECTANGULAR
pipe_hor_m = 0.040
pipe_ver_m = 0.025
```

**Using aliases:**
```ini
# Short alias
chamber_shape = RECT
pipe_hor_m = 0.040
pipe_ver_m = 0.025

# Full word alias
chamber_shape = RECTANGLE
pipe_hor_m = 0.040
pipe_ver_m = 0.025
```

---

## Shape-Specific Parameters

### Parameter Requirements by Shape

| Shape | Required Parameters | Optional Parameters |
|-------|-------------------|-------------------|
| CIRCULAR | `pipe_radius_m` or `pipe_rad_m` | `pipe_hor_m`, `pipe_ver_m` (ignored) |
| ELLIPTICAL | `pipe_hor_m`, `pipe_ver_m` | None |
| RECTANGULAR | `pipe_hor_m`, `pipe_ver_m` | None |

### Parameter Precedence

For CIRCULAR chambers:
1. `pipe_radius_m` (if specified)
2. `pipe_rad_m` (if specified)
3. `pipe_ver_m` (fallback)

### Common Parameters (All Shapes)

| Parameter | Description | Default |
|-----------|-------------|---------|
| `pipe_len_m` | Chamber length in meters | 1.0 |
| `betax` | Horizontal beta function (m) | 1.0 |
| `betay` | Vertical beta function (m) | 1.0 |
| `component_name` | Chamber identifier | 'el' |

---

## Yokoya Factors by Shape

Yokoya factors correct impedance calculations for non-circular geometries.

### Asymmetry Parameter

The Yokoya asymmetry parameter q is defined as:

```
q = |h - v| / (h + v)
```

where h = horizontal half-aperture, v = vertical half-aperture.

| Shape | q Value |
|-------|---------|
| CIRCULAR | 0 (symmetric) |
| ELLIPTICAL | 0 < q < 1 |
| RECTANGULAR | 0 < q < 1 |

### Longitudinal Factors

| Shape | Factor | Notes |
|-------|--------|-------|
| CIRCULAR | 1.0 | No correction |
| ELLIPTICAL | Interpolated | Based on q, from table |
| RECTANGULAR | Interpolated | Based on q, from table |

### Transverse Factors

#### Dipolar (Driving) Factors

| Shape | Horizontal (drivx) | Vertical (drivy) |
|-------|-----------|----------|
| CIRCULAR | 1.0 | 1.0 |
| ELLIPTICAL | π²b/(2a) ≈ 1.0 | π²a/(2b) ≈ 1.0 |
| RECTANGULAR | From table | From table |

#### Quadrupolar (Detuning) Factors

| Shape | Horizontal (detx) | Vertical (dety) |
|-------|-----------|----------|
| CIRCULAR | 0.0 | 0.0 |
| ELLIPTICAL | From table | From table |
| RECTANGULAR | From table | From table |

**Note:** Exact Yokoya factors are calculated automatically by the `Chamber` class based on geometry parameters using interpolation from stored tables.

---

## Validation and Error Handling

### Valid Shape Check

```python
from pytlwall import Chamber
from pytlwall.chamber import ChamberShapeError

# Valid shapes
chamber1 = Chamber(chamber_shape='CIRCULAR', pipe_rad_m=0.02)  # ✅
chamber2 = Chamber(chamber_shape='ROUND', pipe_rad_m=0.02)     # ✅ (alias)
chamber3 = Chamber(chamber_shape='ELLIPTICAL', 
                   pipe_hor_m=0.03, pipe_ver_m=0.02)           # ✅

# Invalid shape
try:
    chamber = Chamber(chamber_shape='HEXAGONAL', pipe_rad_m=0.02)  # ❌
except ChamberShapeError as e:
    print(f"Error: {e}")
    # Output: Error: Unknown chamber shape 'HEXAGONAL'. 
    #         Must be one of: 'CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR'
```

### Error Messages

**Unknown shape:**
```
ChamberShapeError: Unknown chamber shape 'HEXAGONAL'. 
Must be one of: 'CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR'
```

**Note:** Error messages show official names, not aliases.

---

## Migration Guide

### Updating Old Configuration Files

If you have old configuration files using aliases:

**ROUND → CIRCULAR:**
```diff
[base_info]
- chamber_shape = ROUND
+ chamber_shape = CIRCULAR
  pipe_radius_m = 0.022
```

**ELLIPTIC → ELLIPTICAL:**
```diff
[base_info]
- chamber_shape = ELLIPTIC
+ chamber_shape = ELLIPTICAL
  pipe_hor_m = 0.030
  pipe_ver_m = 0.020
```

**RECT → RECTANGULAR:**
```diff
[base_info]
- chamber_shape = RECT
+ chamber_shape = RECTANGULAR
  pipe_hor_m = 0.040
  pipe_ver_m = 0.025
```

**Note:** No changes are required if using aliases — they work automatically!

---

## FAQ

### Q: Are shape names case-sensitive?

**A:** Yes. Use uppercase: `CIRCULAR`, not `circular` or `Circular`.

### Q: Can I mix official names and aliases?

**A:** Yes. Aliases are normalized automatically before any calculations.

### Q: What happens if I misspell a shape name?

**A:** You'll get a `ChamberShapeError` listing valid shapes.

### Q: Do aliases affect calculations?

**A:** No. Aliases are normalized before any calculations.

### Q: Can I add custom shapes?

**A:** Not through config files. Custom shapes require code modifications.

### Q: How do I check which shape is being used?

**A:**
```python
chamber = Chamber(chamber_shape='ROUND', pipe_rad_m=0.02)
print(chamber.chamber_shape)  # Output: CIRCULAR
```

### Q: What if I don't know the correct parameters?

**A:**
```python
# Check required parameters
from pytlwall import Chamber

# For circular - only radius needed
c1 = Chamber(pipe_rad_m=0.02, chamber_shape='CIRCULAR')

# For elliptical/rectangular - both hor and ver needed
c2 = Chamber(pipe_hor_m=0.03, pipe_ver_m=0.02, chamber_shape='ELLIPTICAL')
```

---

## Quick Reference

### Supported Shapes Summary

| Official Name | Aliases | Parameters | Symmetry |
|--------------|---------|------------|----------|
| CIRCULAR | ROUND | radius | Full |
| ELLIPTICAL | ELLIPTIC | hor, ver | 2-fold |
| RECTANGULAR | RECT, RECTANGLE | hor, ver | 4-fold |

### Python API Quick Reference

```python
from pytlwall import Chamber

# Circular
chamber = Chamber(
    pipe_rad_m=0.022,
    chamber_shape='CIRCULAR'
)

# Elliptical
chamber = Chamber(
    pipe_hor_m=0.030,
    pipe_ver_m=0.020,
    chamber_shape='ELLIPTICAL'
)

# Rectangular
chamber = Chamber(
    pipe_hor_m=0.040,
    pipe_ver_m=0.025,
    chamber_shape='RECTANGULAR'
)

# Get Yokoya factors
factors = chamber.get_yokoya_factors()
print(f"q = {factors['q']:.4f}")
print(f"longitudinal = {factors['longitudinal']:.4f}")
```

---

## See Also

- [Chamber API Reference](API_REFERENCE_CHAMBER.md)
- [CfgIo API Reference](API_REFERENCE_CFGIO.md)
- [Main API Reference](API_REFERENCE.md)

---

*Last Updated: December 2025*
*Version: 2.0*
*Copyright: CERN*
