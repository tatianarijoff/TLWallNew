# test_layer.py - Layer Class Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `Layer` class which handles material properties, frequency-dependent calculations, and surface impedance.

**Module tested**: `pytlwall.layer`

**Run this test**:
```bash
python tests/test_layer.py -v
```

---

## Test Classes

### TestLayerInitialization

Tests layer creation scenarios.

| Test Method | Description |
|-------------|-------------|
| `test_default_initialization` | Verifies default values (CW type, 1cm thick, σ=10⁶ S/m) |
| `test_boundary_initialization` | Tests boundary=True sets type to 'V' (vacuum) |
| `test_custom_initialization` | Tests all custom parameters |
| `test_initialization_with_frequencies` | Tests frequency array initialization |

### TestLayerType

Tests layer type property.

| Test Method | Description |
|-------------|-------------|
| `test_valid_layer_types` | Tests 'CW', 'V', 'PEC' types |
| `test_case_insensitive` | Tests 'cw', 'Cw', 'CW' all work |
| `test_invalid_layer_type` | Verifies LayerValidationError |
| `test_layer_type_setter` | Tests setter validation |

### TestLayerThickness

Tests thickness property.

| Test Method | Description |
|-------------|-------------|
| `test_positive_thickness` | Tests valid thickness |
| `test_zero_thickness` | Verifies error for t=0 |
| `test_negative_thickness` | Verifies error for t<0 |
| `test_thickness_setter` | Tests setter validation |

### TestLayerConductivity

Tests electrical conductivity.

| Test Method | Description |
|-------------|-------------|
| `test_positive_conductivity` | Tests copper σ=5.96×10⁷ S/m |
| `test_zero_conductivity` | Tests insulator σ=0 |
| `test_negative_conductivity` | Verifies error for σ<0 |
| `test_conductivity_range` | Tests copper and stainless steel values |

### TestLayerPermittivity

Tests permittivity properties.

| Test Method | Description |
|-------------|-------------|
| `test_relative_permittivity` | Tests εr setting |
| `test_absolute_permittivity` | Tests ε = ε₀ × εr calculation |
| `test_zero_permittivity` | Verifies error for εr=0 |
| `test_negative_permittivity` | Verifies error for εr<0 |

### TestLayerRoughness

Tests surface roughness (RQ parameter).

| Test Method | Description |
|-------------|-------------|
| `test_zero_roughness` | Tests smooth surface RQ=0 |
| `test_positive_roughness` | Tests RQ=1μm |
| `test_negative_roughness` | Verifies error for RQ<0 |

### TestFrequencyArray

Tests frequency array handling.

| Test Method | Description |
|-------------|-------------|
| `test_set_frequency_array` | Tests freq_Hz setter |
| `test_empty_frequency_array` | Tests default empty array |
| `test_negative_frequencies` | Verifies error for f<0 |
| `test_zero_frequency` | Verifies error for f=0 |
| `test_frequency_setter` | Tests array replacement |

### TestCalculatedProperties

Tests frequency-dependent calculations.

| Test Method | Description |
|-------------|-------------|
| `test_skin_depth_calculation` | Tests δ = √(2/(ωμσ)) |
| `test_skin_depth_frequency_dependence` | Verifies δ decreases with f |
| `test_surface_resistance` | Tests Rs calculation |
| `test_surface_reactance` | Tests Xs calculation |
| `test_skin_depth_decreases_with_frequency` | Verifies physical behavior |

### TestSurfaceImpedance

Tests surface impedance handling.

| Test Method | Description |
|-------------|-------------|
| `test_default_surface_impedance` | Tests default KZ calculation |
| `test_set_surface_impedance_directly` | Tests direct KZ assignment |
| `test_surface_impedance_must_be_complex` | Verifies complex requirement |
| `test_set_surf_imped_with_interpolation` | Tests interpolation from sparse data |

### TestRoughnessEffects

Tests surface roughness impact.

| Test Method | Description |
|-------------|-------------|
| `test_roughness_increases_resistance` | Verifies Rs(rough) ≥ Rs(smooth) |
| `test_roughness_effect_frequency_dependent` | Tests f-dependence of roughness |

### TestMaterialExamples

Tests realistic material parameters.

| Test Method | Description |
|-------------|-------------|
| `test_copper_layer` | Tests copper: σ=5.96×10⁷ S/m |
| `test_stainless_steel_layer` | Tests steel: σ=1.45×10⁶ S/m, RQ=1μm |
| `test_vacuum_layer` | Tests vacuum boundary |
| `test_perfect_conductor` | Tests PEC type |

### TestLayerValidation

Tests comprehensive validation.

| Test Method | Description |
|-------------|-------------|
| `test_invalid_type_value` | Tests string thickness rejection |
| `test_invalid_conductivity_value` | Tests string conductivity rejection |
| `test_invalid_frequency_array` | Tests string array rejection |

### TestLayerRepresentation

Tests string output.

| Test Method | Description |
|-------------|-------------|
| `test_repr` | Tests `__repr__` contains type, thickness |
| `test_str` | Tests `__str__` is readable |

### TestLayerConsistency

Tests property update consistency.

| Test Method | Description |
|-------------|-------------|
| `test_property_update_consistency` | Tests that changing σ updates δ |
| `test_frequency_change_updates_calculations` | Tests recalculation on f change |

### TestEdgeCases

Tests extreme values.

| Test Method | Description |
|-------------|-------------|
| `test_very_high_conductivity` | Tests σ=10¹⁰ S/m (superconductor-like) |
| `test_very_low_conductivity` | Tests σ=10⁻¹⁰ S/m (insulator-like) |
| `test_single_frequency` | Tests single frequency point |
| `test_many_frequencies` | Tests 10,000 frequency points |

---

## Key Formulas Tested

```
Skin depth:       δ = √(2 / (ω μ σ))
Surface resistance: Rs = 1 / (σ δ)
Surface impedance:  Zs = Rs (1 + j)

With roughness (RQ):
  Rs_rough = Rs × (1 + f(RQ, δ))
```

---

## Example Usage

```python
from pytlwall.layer import Layer
import numpy as np

# Copper layer with frequencies
freq = np.logspace(3, 9, 100)  # 1 kHz to 1 GHz
copper = Layer(
    layer_type='CW',
    thick_m=0.001,           # 1 mm
    sigmaDC=5.96e7,          # Copper conductivity
    epsr=1.0,
    RQ=0.5e-6,               # 0.5 μm roughness
    freq_Hz=freq
)

# Get calculated properties
print(f"Skin depth at 1 GHz: {copper.delta[-1]*1e6:.2f} μm")
print(f"Surface resistance: {copper.RS[-1]:.4f} Ω")
```

---

[← Back to Testing Documentation](../TESTING.md)
