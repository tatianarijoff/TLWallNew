# Chamber Module API Reference

## Overview

The `Chamber` module provides the `Chamber` class for defining vacuum chamber geometries with different cross-sectional shapes and calculating Yokoya correction factors for impedance calculations.

## Table of Contents

- [Chamber Class](#chamber-class)
- [Properties](#properties)
- [Methods](#methods)
- [Exceptions](#exceptions)
- [Constants](#constants)
- [Examples](#examples)

---

## Chamber Class

```python
class Chamber:
    """
    Represents a vacuum chamber with specified geometry and optical parameters.
    """
```

### Constructor

```python
Chamber(
    pipe_len_m: float = 1.0,
    pipe_rad_m: float = 0.01,
    pipe_hor_m: Optional[float] = None,
    pipe_ver_m: Optional[float] = None,
    chamber_shape: str = 'CIRCULAR',
    betax: float = 1.0,
    betay: float = 1.0,
    layers: Optional[List] = None,
    component_name: str = 'el'
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `pipe_len_m` | float | 1.0 | Pipe length in meters |
| `pipe_rad_m` | float | 0.01 | Pipe radius in meters (for circular chambers) |
| `pipe_hor_m` | float or None | None | Horizontal half-aperture in meters. If None, uses `pipe_rad_m` |
| `pipe_ver_m` | float or None | None | Vertical half-aperture in meters. If None, uses `pipe_rad_m` |
| `chamber_shape` | str | 'CIRCULAR' | Chamber cross-section shape: 'CIRCULAR', 'ELLIPTICAL', or 'RECTANGULAR' |
| `betax` | float | 1.0 | Horizontal beta function at chamber location (m) |
| `betay` | float | 1.0 | Vertical beta function at chamber location (m) |
| `layers` | List or None | None | List of Layer objects for multi-layer structure |
| `component_name` | str | 'el' | Name identifier for the chamber component |

#### Raises

- `ChamberDimensionError`: If dimensions are invalid (negative or zero)
- `ChamberShapeError`: If chamber_shape is not recognized

#### Examples

```python
# Circular chamber
chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')

# Elliptical chamber
chamber = Chamber(
    pipe_hor_m=0.030,
    pipe_ver_m=0.020,
    chamber_shape='ELLIPTICAL',
    betax=100.0,
    betay=50.0
)

# Rectangular chamber
chamber = Chamber(
    pipe_hor_m=0.040,
    pipe_ver_m=0.025,
    chamber_shape='RECTANGULAR'
)
```

---

## Properties

### Dimension Properties

#### `pipe_len_m`

```python
@property
def pipe_len_m(self) -> float
```

**Description**: Get or set pipe length in meters.

**Type**: float (read/write)

**Raises**: `ChamberDimensionError` if value is not positive

**Example**:
```python
chamber = Chamber()
chamber.pipe_len_m = 2.5
print(f"Length: {chamber.pipe_len_m} m")
```

---

#### `pipe_rad_m`

```python
@property
def pipe_rad_m(self) -> float
```

**Description**: Get or set pipe radius in meters. For circular chambers, this also sets horizontal and vertical dimensions.

**Type**: float (read/write)

**Raises**: `ChamberDimensionError` if value is not positive

**Example**:
```python
chamber = Chamber()
chamber.pipe_rad_m = 0.025  # 25 mm radius
# This also sets pipe_hor_m and pipe_ver_m to 0.025
```

---

#### `pipe_hor_m`

```python
@property
def pipe_hor_m(self) -> float
```

**Description**: Get or set horizontal half-aperture in meters.

**Type**: float (read/write)

**Raises**: `ChamberDimensionError` if value is not positive

**Example**:
```python
chamber = Chamber()
chamber.pipe_hor_m = 0.030  # 30 mm horizontal aperture
```

---

#### `pipe_ver_m`

```python
@property
def pipe_ver_m(self) -> float
```

**Description**: Get or set vertical half-aperture in meters.

**Type**: float (read/write)

**Raises**: `ChamberDimensionError` if value is not positive

**Example**:
```python
chamber = Chamber()
chamber.pipe_ver_m = 0.020  # 20 mm vertical aperture
```

---

### Optical Properties

#### `betax`

```python
@property
def betax(self) -> float
```

**Description**: Get or set horizontal beta function in meters.

**Type**: float (read/write)

**Raises**: `ChamberDimensionError` if value is not positive

**Example**:
```python
chamber = Chamber()
chamber.betax = 100.0  # 100 m horizontal beta function
```

---

#### `betay`

```python
@property
def betay(self) -> float
```

**Description**: Get or set vertical beta function in meters.

**Type**: float (read/write)

**Raises**: `ChamberDimensionError` if value is not positive

**Example**:
```python
chamber = Chamber()
chamber.betay = 50.0  # 50 m vertical beta function
```

---

### Shape Properties

#### `chamber_shape`

```python
@property
def chamber_shape(self) -> str
```

**Description**: Get or set chamber cross-section shape. Valid values: 'CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR'. Setting this property initializes the appropriate Yokoya factor tables.

**Type**: str (read/write)

**Raises**: `ChamberShapeError` if shape is not recognized

**Example**:
```python
chamber = Chamber()
chamber.chamber_shape = 'ELLIPTICAL'
print(f"Shape: {chamber.chamber_shape}")
```

---

#### `component_name`

```python
@property
def component_name(self) -> str
```

**Description**: Get or set component name identifier.

**Type**: str (read/write)

**Example**:
```python
chamber = Chamber()
chamber.component_name = 'arc_dipole_01'
```

---

### Yokoya Factor Properties

#### `yokoya_q`

```python
@property
def yokoya_q(self) -> float
```

**Description**: Calculate Yokoya asymmetry parameter q = |h - v| / (h + v), where h is horizontal and v is vertical half-aperture.

**Type**: float (read-only)

**Returns**: Yokoya asymmetry parameter (0 for circular, >0 for non-circular)

**Example**:
```python
chamber = Chamber(pipe_hor_m=0.030, pipe_ver_m=0.020)
print(f"Asymmetry: {chamber.yokoya_q:.4f}")  # Output: 0.2000
```

---

#### `yokoya_q_idx`

```python
@property
def yokoya_q_idx(self) -> int
```

**Description**: Get index in Yokoya factor tables for current asymmetry.

**Type**: int (read-only)

**Returns**: Index in yoko_q array closest to current yokoya_q value

---

#### `long_yokoya_factor`

```python
@property
def long_yokoya_factor(self) -> float
```

**Description**: Get longitudinal Yokoya correction factor.

**Type**: float (read-only)

**Returns**: Yokoya factor for longitudinal impedance

**Example**:
```python
chamber = Chamber(
    pipe_hor_m=0.030,
    pipe_ver_m=0.020,
    chamber_shape='ELLIPTICAL'
)
print(f"Longitudinal factor: {chamber.long_yokoya_factor:.4f}")
```

---

#### `drivx_yokoya_factor`

```python
@property
def drivx_yokoya_factor(self) -> float
```

**Description**: Get horizontal driving Yokoya correction factor.

**Type**: float (read-only)

**Returns**: Yokoya factor for horizontal driving impedance

---

#### `drivy_yokoya_factor`

```python
@property
def drivy_yokoya_factor(self) -> float
```

**Description**: Get vertical driving Yokoya correction factor.

**Type**: float (read-only)

**Returns**: Yokoya factor for vertical driving impedance

---

#### `detx_yokoya_factor`

```python
@property
def detx_yokoya_factor(self) -> float
```

**Description**: Get horizontal detuning Yokoya correction factor.

**Type**: float (read-only)

**Returns**: Yokoya factor for horizontal detuning impedance

---

#### `dety_yokoya_factor`

```python
@property
def dety_yokoya_factor(self) -> float
```

**Description**: Get vertical detuning Yokoya correction factor.

**Type**: float (read-only)

**Returns**: Yokoya factor for vertical detuning impedance

---

## Methods

### `get_yokoya_factors()`

```python
def get_yokoya_factors(self) -> dict
```

**Description**: Get all Yokoya factors as a dictionary.

**Returns**: Dictionary containing:
- `'q'`: asymmetry parameter
- `'longitudinal'`: longitudinal factor
- `'drivx'`: horizontal driving factor
- `'drivy'`: vertical driving factor
- `'detx'`: horizontal detuning factor
- `'dety'`: vertical detuning factor

**Example**:
```python
chamber = Chamber(pipe_hor_m=0.030, pipe_ver_m=0.020, 
                  chamber_shape='ELLIPTICAL')
factors = chamber.get_yokoya_factors()
print(f"Longitudinal factor: {factors['longitudinal']:.3f}")
```

---

### `get_dimensions()`

```python
def get_dimensions(self) -> dict
```

**Description**: Get chamber dimensions as a dictionary.

**Returns**: Dictionary containing:
- `'length'`: pipe length in meters
- `'radius'`: pipe radius in meters (for circular)
- `'horizontal'`: horizontal half-aperture in meters
- `'vertical'`: vertical half-aperture in meters

**Example**:
```python
chamber = Chamber(pipe_rad_m=0.025)
dims = chamber.get_dimensions()
print(f"Chamber radius: {dims['radius']*1000:.1f} mm")
```

---

### `summary()`

```python
def summary(self) -> str
```

**Description**: Generate a detailed summary of the chamber configuration.

**Returns**: Multi-line formatted string with chamber properties

**Example**:
```python
chamber = Chamber(pipe_hor_m=0.030, pipe_ver_m=0.020, 
                  chamber_shape='ELLIPTICAL')
print(chamber.summary())
```

**Output**:
```
============================================================
Chamber: el
============================================================
Shape:              ELLIPTICAL
Length:             1.000 m
Horizontal aperture: 30.00 mm
Vertical aperture:   20.00 mm
Beta_x:             1.00 m
Beta_y:             1.00 m
Number of layers:   0

Yokoya Factors:
  Asymmetry (q):    0.2000
  Longitudinal:     1.2345
  Driv_x:           0.9876
  Driv_y:           1.0543
  Det_x:            0.0123
  Det_y:            -0.0098
============================================================
```

---

### `__repr__()`

```python
def __repr__(self) -> str
```

**Description**: Return detailed string representation of Chamber.

**Returns**: String with chamber parameters

**Example**:
```python
chamber = Chamber(pipe_rad_m=0.025, chamber_shape='CIRCULAR')
print(repr(chamber))
# Output: Chamber(shape='CIRCULAR', length=1.000m, hor=25.0mm, ver=25.0mm, βx=1.0m, βy=1.0m, name='el')
```

---

### `__str__()`

```python
def __str__(self) -> str
```

**Description**: Return user-friendly string representation of Chamber.

**Returns**: Human-readable description

**Example**:
```python
chamber = Chamber(pipe_rad_m=0.025, chamber_shape='CIRCULAR')
print(str(chamber))
# Output: CIRCULAR chamber (radius=25.0 mm)
```

---

## Exceptions

### `ChamberShapeError`

```python
class ChamberShapeError(ValueError):
    """Exception raised for invalid chamber shape specifications."""
```

**Raised when**: An invalid chamber shape is specified (not 'CIRCULAR', 'ELLIPTICAL', or 'RECTANGULAR')

**Example**:
```python
try:
    chamber = Chamber(chamber_shape='INVALID')
except ChamberShapeError as e:
    print(f"Error: {e}")
```

---

### `ChamberDimensionError`

```python
class ChamberDimensionError(ValueError):
    """Exception raised for invalid chamber dimensions."""
```

**Raised when**: A chamber dimension is invalid (negative, zero, or non-numeric)

**Example**:
```python
try:
    chamber = Chamber(pipe_rad_m=-0.025)
except ChamberDimensionError as e:
    print(f"Error: {e}")
```

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `DEFAULT_PIPE_LENGTH_M` | 1.0 | Default pipe length in meters |
| `DEFAULT_PIPE_RADIUS_M` | 0.01 | Default pipe radius in meters (10 mm) |
| `DEFAULT_PIPE_HORIZONTAL_M` | 0.01 | Default horizontal half-aperture in meters |
| `DEFAULT_PIPE_VERTICAL_M` | 0.01 | Default vertical half-aperture in meters |
| `DEFAULT_CHAMBER_SHAPE` | 'CIRCULAR' | Default chamber shape |
| `DEFAULT_BETA_X` | 1.0 | Default horizontal beta function in meters |
| `DEFAULT_BETA_Y` | 1.0 | Default vertical beta function in meters |
| `DEFAULT_COMPONENT_NAME` | 'el' | Default component name |

---

## Examples

### Basic Usage

#### Creating a Circular Chamber

```python
import pytlwall

# Simple circular chamber
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022,        # 22 mm radius
    chamber_shape='CIRCULAR'
)

print(chamber.summary())
```

#### Creating an Elliptical Chamber

```python
# Elliptical chamber with different apertures
chamber = pytlwall.Chamber(
    pipe_hor_m=0.030,        # 30 mm horizontal
    pipe_ver_m=0.020,        # 20 mm vertical
    chamber_shape='ELLIPTICAL',
    betax=100.0,
    betay=50.0,
    component_name='flat_chamber'
)

# Get Yokoya factors
factors = chamber.get_yokoya_factors()
print(f"Yokoya q: {factors['q']:.4f}")
print(f"Longitudinal factor: {factors['longitudinal']:.4f}")
```

#### Creating a Rectangular Chamber

```python
# Rectangular chamber
chamber = pytlwall.Chamber(
    pipe_hor_m=0.040,
    pipe_ver_m=0.015,
    chamber_shape='RECTANGULAR',
    component_name='kicker'
)

print(f"Aspect ratio: {chamber.pipe_hor_m / chamber.pipe_ver_m:.2f}")
print(f"Yokoya q: {chamber.yokoya_q:.4f}")
```

### Advanced Usage

#### LHC-Style Chamber Configuration

```python
# LHC arc dipole chamber
lhc_dipole = pytlwall.Chamber(
    pipe_rad_m=0.022,         # 44 mm diameter beam screen
    pipe_len_m=14.3,          # Dipole length
    chamber_shape='CIRCULAR',
    betax=180.0,              # Arc optics
    betay=180.0,
    component_name='MB_dipole'
)

print(f"Chamber: {lhc_dipole.component_name}")
print(f"Aperture: {lhc_dipole.pipe_rad_m * 1000:.1f} mm")
print(f"Beta functions: βx={lhc_dipole.betax:.0f} m, βy={lhc_dipole.betay:.0f} m")
```

#### Dynamic Modification

```python
# Create and modify chamber
chamber = pytlwall.Chamber(pipe_rad_m=0.025)

# Change to elliptical
chamber.chamber_shape = 'ELLIPTICAL'
chamber.pipe_hor_m = 0.035
chamber.pipe_ver_m = 0.020

# Update beta functions
chamber.betax = 120.0
chamber.betay = 60.0

print(chamber.summary())
```

#### Error Handling

```python
import pytlwall
from pytlwall.chamber import ChamberShapeError, ChamberDimensionError

# Validate input
try:
    chamber = pytlwall.Chamber(
        pipe_rad_m=0.025,
        chamber_shape='CIRCULAR'
    )
except ChamberDimensionError as e:
    print(f"Dimension error: {e}")
except ChamberShapeError as e:
    print(f"Shape error: {e}")
```

#### Comparing Chamber Geometries

```python
# Compare different shapes
chambers = {
    'Circular': pytlwall.Chamber(
        pipe_rad_m=0.025,
        chamber_shape='CIRCULAR'
    ),
    'Elliptical': pytlwall.Chamber(
        pipe_hor_m=0.030,
        pipe_ver_m=0.020,
        chamber_shape='ELLIPTICAL'
    ),
    'Rectangular': pytlwall.Chamber(
        pipe_hor_m=0.035,
        pipe_ver_m=0.018,
        chamber_shape='RECTANGULAR'
    )
}

for name, chamber in chambers.items():
    print(f"{name:12s}: q={chamber.yokoya_q:.4f}, "
          f"long={chamber.long_yokoya_factor:.4f}")
```

---

## Notes

### Yokoya Factors

Yokoya factors are geometric correction factors that account for non-circular cross-sections in impedance calculations. They were derived by K. Yokoya and are widely used in accelerator impedance calculations.

- **Circular chambers** (q=0): All Yokoya factors = 1.0 (no correction needed)
- **Elliptical chambers** (q>0): Smooth wall approximation, factors vary with aspect ratio
- **Rectangular chambers** (q>0): Different correction than elliptical

### Beta Functions

Beta functions (βx, βy) are optical parameters from beam dynamics that describe the beam envelope. They are used in transverse impedance calculations:

- Higher β → larger beam size → different wake field effects
- Typically βx ≠ βy in non-circular chambers
- Important for accurate transverse impedance predictions

### Multi-Layer Structures

The `layers` attribute supports multi-layer chamber structures (e.g., coating on substrate). Each layer should be a `Layer` object from the `pytlwall.Layer` module.

---

## See Also

- [Layer Module](LAYER_API.md): Material layer definitions
- [TlWall Module](TLWALL_API.md): Main impedance calculation class
- [Frequencies Module](FREQUENCIES_API.md): Frequency array management
- [Examples](../examples/): Complete usage examples

---

## References

1. K. Yokoya, "Resistive wall impedance of beam pipes of general cross section", Part. Accel. 41, 221 (1993)
2. A. Chao, "Physics of Collective Beam Instabilities in High Energy Accelerators", Wiley (1993)
3. B. Zotter and S. Kheifets, "Impedances and Wakes in High-Energy Particle Accelerators", World Scientific (1998)

---

**Last Updated**: 2025
**Version**: 1.0
