# test_tlwall.py - TlWall Class Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `TlWall` class which performs the core impedance calculations using the Transmission Line Wall model.

**Module tested**: `pytlwall.tlwall`

**Run this test**:
```bash
python tests/test_tlwall.py -v
```

---

## Test Classes

### TestTlWallInitialization

Tests TlWall creation and configuration.

| Test Method | Description |
|-------------|-------------|
| `test_basic_initialization` | Tests creation with chamber, beam, frequencies |
| `test_custom_accuracy_factor` | Tests non-default accuracy factor |
| `test_chamber_without_layers` | Verifies TlWallConfigurationError for empty chamber |

### TestTlWallLongitudinalImpedance

Tests longitudinal impedance calculations (ZLong).

| Test Method | Description |
|-------------|-------------|
| `test_calc_ZLong_returns_array` | Verifies numpy complex array returned |
| `test_ZLong_property_caching` | Tests that property returns cached value |
| `test_ZLong_not_nan` | Verifies no NaN values |
| `test_ZLong_frequency_dependence` | Tests variation across frequencies |
| `test_ZLong_positive_real_part` | Verifies Re(Z) > 0 (resistive) |

### TestTlWallTransverseImpedance

Tests transverse impedance calculations (ZTrans).

| Test Method | Description |
|-------------|-------------|
| `test_calc_ZTrans_returns_array` | Verifies numpy complex array returned |
| `test_ZTrans_property_caching` | Tests caching behavior |
| `test_ZTrans_not_nan` | Verifies no NaN values |
| `test_ZDipX_ZDipY_calculated` | Verifies dipolar components calculated |
| `test_ZQuadX_ZQuadY_calculated` | Verifies quadrupolar components calculated |

### TestTlWallDipolarImpedance

Tests dipolar impedance components.

| Test Method | Description |
|-------------|-------------|
| `test_ZDipX_property` | Tests horizontal dipolar impedance |
| `test_ZDipY_property` | Tests vertical dipolar impedance |
| `test_circular_chamber_dipolar_equal` | Verifies ZDipX = ZDipY for circular |

### TestTlWallQuadrupolarImpedance

Tests quadrupolar impedance components.

| Test Method | Description |
|-------------|-------------|
| `test_ZQuadX_property` | Tests horizontal quadrupolar impedance |
| `test_ZQuadY_property` | Tests vertical quadrupolar impedance |
| `test_circular_chamber_quadrupolar_zero` | Verifies ZQuad ≈ 0 for circular |

### TestTlWallEllipticalChamber

Tests with elliptical chamber geometry.

| Test Method | Description |
|-------------|-------------|
| `test_elliptical_ZDipX_ZDipY_different` | Verifies ZDipX ≠ ZDipY |
| `test_elliptical_ZQuadX_ZQuadY_different` | Verifies ZQuadX ≠ ZQuadY |
| `test_elliptical_yokoya_applied` | Tests Yokoya factors affect results |

### TestTlWallRectangularChamber

Tests with rectangular chamber geometry.

| Test Method | Description |
|-------------|-------------|
| `test_rectangular_chamber_initialization` | Tests rectangular chamber support |
| `test_rectangular_impedance_calculation` | Tests impedance calculation works |

### TestTlWallMultipleLayers

Tests with multi-layer structures.

| Test Method | Description |
|-------------|-------------|
| `test_two_layer_structure` | Tests copper + steel configuration |
| `test_three_layer_structure` | Tests copper + ceramic + steel |
| `test_layer_order_matters` | Verifies different results for different order |

### TestTlWallCaching

Tests result caching behavior.

| Test Method | Description |
|-------------|-------------|
| `test_ZLong_cached_after_calculation` | Tests _ZLong populated |
| `test_ZTrans_cached_after_calculation` | Tests _ZTrans populated |
| `test_accuracy_factor_change_behavior` | Tests cache behavior on param change |
| `test_accuracy_factor_invalidates_cache` | Tests cache invalidation |

### TestTlWallEdgeCases

Tests boundary conditions.

| Test Method | Description |
|-------------|-------------|
| `test_very_thin_layer` | Tests 1 nm layer |
| `test_very_thick_layer` | Tests 1 m layer |

### TestTlWallSpaceCharge

Tests space charge impedance calculations.

| Test Method | Description |
|-------------|-------------|
| `test_calc_ZLongDSC_method_exists` | Verifies method exists |
| `test_calc_ZLongDSC_returns_array` | Tests return type |
| `test_calc_ZLongDSC_caching` | Tests caching |
| `test_calc_ZLongISC_method_exists` | Verifies method exists |
| `test_calc_ZLongISC_returns_array` | Tests return type |
| `test_calc_ZTransDSC_method_exists` | Verifies method exists |
| `test_calc_ZTransDSC_returns_array` | Tests return type |
| `test_calc_ZTransISC_method_exists` | Verifies method exists |
| `test_calc_ZTransISC_returns_array` | Tests return type |
| `test_space_charge_ultra_relativistic` | Verifies Z=0 for γ=∞ |
| `test_space_charge_non_relativistic` | Verifies Z≠0 for γ≈2 |
| `test_space_charge_frequency_dependence` | Tests f-dependence |

---

## Impedance Types

The TlWall class calculates:

| Property | Description | Unit |
|----------|-------------|------|
| `ZLong` | Longitudinal wall impedance | Ω |
| `ZTrans` | Transverse wall impedance (general) | Ω/m |
| `ZDipX` | Horizontal dipolar impedance | Ω/m |
| `ZDipY` | Vertical dipolar impedance | Ω/m |
| `ZQuadX` | Horizontal quadrupolar impedance | Ω/m |
| `ZQuadY` | Vertical quadrupolar impedance | Ω/m |
| `ZLongDSC` | Longitudinal direct space charge | Ω |
| `ZLongISC` | Longitudinal indirect space charge | Ω |
| `ZTransDSC` | Transverse direct space charge | Ω/m |
| `ZTransISC` | Transverse indirect space charge | Ω/m |

---

## API Detection

The test file includes automatic Beam API detection to handle different implementations:

```python
def create_beam_lhc():
    """Create LHC beam using correct API."""
    sig = inspect.signature(Beam.__init__)
    params = list(sig.parameters.keys())
    
    if 'gamma' in params:
        return Beam(gamma=7460.52)
    elif 'gammarel' in params:
        return Beam(gammarel=7460.52)
    # ... fallbacks
```

---

## Example Usage

```python
from pytlwall import TlWall, Chamber, Beam, Frequencies, Layer

# Setup
freq = Frequencies(fmin=3, fmax=9, fstep=2)
beam = Beam(gamma=7460.52)
chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freq.freq)
chamber.layers = [copper]

# Create TlWall and calculate
wall = TlWall(chamber=chamber, beam=beam, frequencies=freq)

# Get impedances
ZLong = wall.ZLong  # Cached property
ZDipX = wall.ZDipX
ZDipY = wall.ZDipY

# Space charge
ZLongDSC = wall.calc_ZLongDSC()
```

---

[← Back to Testing Documentation](../TESTING.md)
