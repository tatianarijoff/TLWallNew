# test_chamber.py - Chamber Class Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `Chamber` class which handles beam pipe geometry, Yokoya factors, and beta functions.

**Module tested**: `pytlwall.chamber`

**Run this test**:
```bash
python tests/test_chamber.py -v
```

---

## Test Classes

### TestChamberInitialization

Tests chamber creation with various parameters.

| Test Method | Description |
|-------------|-------------|
| `test_default_initialization` | Verifies default values (length, radius, shape, beta) |
| `test_circular_chamber` | Tests CIRCULAR chamber: pipe_rad_m = pipe_hor_m = pipe_ver_m |
| `test_elliptical_chamber` | Tests ELLIPTICAL chamber with different hor/ver dimensions |
| `test_rectangular_chamber` | Tests RECTANGULAR chamber initialization |
| `test_with_beta_functions` | Tests custom βx and βy values |
| `test_with_component_name` | Tests custom component name |

### TestChamberDimensions

Tests dimension properties and validation.

| Test Method | Description |
|-------------|-------------|
| `test_set_pipe_length` | Tests pipe_len_m setter |
| `test_negative_pipe_length` | Verifies ChamberDimensionError for L < 0 |
| `test_zero_pipe_length` | Verifies ChamberDimensionError for L = 0 |
| `test_set_pipe_radius` | Tests that pipe_rad_m updates hor and ver |
| `test_negative_pipe_radius` | Verifies error for negative radius |
| `test_set_horizontal_dimension` | Tests pipe_hor_m setter |
| `test_negative_horizontal` | Verifies error for negative horizontal |
| `test_set_vertical_dimension` | Tests pipe_ver_m setter |
| `test_negative_vertical` | Verifies error for negative vertical |
| `test_invalid_dimension_type` | Tests type validation (string, None) |

### TestBetaFunctions

Tests beta function properties.

| Test Method | Description |
|-------------|-------------|
| `test_set_betax` | Tests βx setter |
| `test_set_betay` | Tests βy setter |
| `test_negative_betax` | Verifies error for βx < 0 |
| `test_zero_betax` | Verifies error for βx = 0 |
| `test_negative_betay` | Verifies error for βy < 0 |
| `test_invalid_beta_type` | Tests type validation |

### TestChamberShapes

Tests chamber shape specifications.

| Test Method | Description |
|-------------|-------------|
| `test_circular_shape` | Tests CIRCULAR: all Yokoya factors = 1 (driving), 0 (detuning) |
| `test_elliptical_shape` | Tests ELLIPTICAL shape recognition |
| `test_rectangular_shape` | Tests RECTANGULAR shape recognition |
| `test_shape_aliases` | Tests aliases: ROUND→CIRCULAR, ELLIPTIC→ELLIPTICAL, RECT→RECTANGULAR |
| `test_invalid_shape` | Verifies ChamberShapeError for invalid shapes |
| `test_shape_case_insensitive` | Tests case insensitivity |

### TestYokoyaFactors

Tests Yokoya factor calculations.

| Test Method | Description |
|-------------|-------------|
| `test_circular_yokoya_factors` | Verifies q=0, all driving factors=1 |
| `test_elliptical_yokoya_calculation` | Tests q = (a-b)/(a+b) for ellipse |
| `test_rectangular_yokoya_calculation` | Tests Yokoya factors for rectangle |
| `test_get_yokoya_factors_dict` | Tests get_yokoya_factors() returns dict |
| `test_yokoya_factors_positive` | Verifies driving factors ≥ 0 |

### TestChamberMethods

Tests utility methods.

| Test Method | Description |
|-------------|-------------|
| `test_get_dimensions` | Tests get_dimensions() dict output |
| `test_summary` | Tests summary() string output |
| `test_repr` | Tests `__repr__` method |
| `test_str` | Tests `__str__` method |

### TestChamberLayers

Tests layer handling.

| Test Method | Description |
|-------------|-------------|
| `test_empty_layers` | Tests chamber with no layers |
| `test_with_layers` | Tests chamber with layers list |

### TestChamberEdgeCases

Tests boundary conditions.

| Test Method | Description |
|-------------|-------------|
| `test_very_small_dimensions` | Tests 1 μm dimensions |
| `test_very_large_dimensions` | Tests 10 m dimensions |
| `test_equal_hor_ver_elliptical` | Tests elliptical with a=b (q≈0) |
| `test_extreme_aspect_ratio` | Tests flat chamber (q→1) |

### TestChamberIntegration

Integration tests with realistic configurations.

| Test Method | Description |
|-------------|-------------|
| `test_lhc_style_chamber` | Tests LHC arc dipole configuration |
| `test_flat_chamber` | Tests modern flat chamber design |

---

## Yokoya Factor Formulas

For a chamber with horizontal half-aperture `a` and vertical half-aperture `b`:

```
q = |a - b| / (a + b)

For CIRCULAR (q = 0):
  longitudinal = 1
  drivx = drivy = 1
  detx = dety = 0

For ELLIPTICAL/RECTANGULAR (q > 0):
  Factors depend on q through polynomial fits
```

---

## Example Usage

```python
from pytlwall.chamber import Chamber

# LHC-style circular chamber
chamber = Chamber(
    pipe_rad_m=0.022,      # 22 mm radius
    pipe_len_m=1.0,        # 1 m length
    chamber_shape='CIRCULAR',
    betax=100.0,           # 100 m horizontal beta
    betay=100.0,           # 100 m vertical beta
    component_name='LHC_dipole'
)

# Flat elliptical chamber
flat = Chamber(
    pipe_hor_m=0.040,      # 40 mm horizontal
    pipe_ver_m=0.012,      # 12 mm vertical  
    chamber_shape='ELLIPTICAL'
)

print(f"Yokoya q = {flat.yokoya_q:.4f}")
print(flat.get_yokoya_factors())
```

---

[← Back to Testing Documentation](../TESTING.md)
