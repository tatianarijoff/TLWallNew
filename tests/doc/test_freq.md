# test_freq.py - Frequencies Class Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `Frequencies` class which generates logarithmically-spaced frequency arrays for impedance calculations.

**Module tested**: `pytlwall.frequencies`

**Run this test**:
```bash
python tests/test_freq.py -v
```

---

## Test Classes

### TestFrequenciesGeneration

Tests frequency array generation from exponents.

| Test Method | Description |
|-------------|-------------|
| `test_default_generation` | Verifies defaults: fmin=0, fmax=8, fstep=2 |
| `test_custom_exponents` | Tests custom fmin, fmax, fstep |
| `test_frequency_coverage` | Verifies range from 10^fmin to 10^fmax |
| `test_step_resolution` | Tests that larger fstep produces more points |
| `test_logarithmic_spacing` | Verifies roughly constant ratio between points |

### TestFrequenciesExplicitList

Tests frequency creation from explicit list.

| Test Method | Description |
|-------------|-------------|
| `test_explicit_list` | Tests freq_list parameter |
| `test_unsorted_list_gets_sorted` | Verifies automatic sorting |
| `test_single_frequency` | Tests single frequency point |
| `test_empty_list_uses_defaults` | Tests fallback to exponent generation |
| `test_explicit_list_ignores_exponents` | Verifies freq_list takes priority |

### TestFrequenciesValidation

Tests error handling.

| Test Method | Description |
|-------------|-------------|
| `test_negative_frequencies_rejected` | Verifies ValueError for f<0 |
| `test_zero_frequency_rejected` | Verifies ValueError for f=0 |
| `test_invalid_fmin_raises_error` | Tests type validation |
| `test_invalid_fmax_raises_error` | Tests type validation |
| `test_invalid_fstep_raises_error` | Tests type validation |
| `test_fmin_greater_than_fmax_warning` | Tests UserWarning for inverted range |
| `test_negative_fstep_warning` | Tests UserWarning for negative step |

### TestFrequenciesProperties

Tests property getters and setters.

| Test Method | Description |
|-------------|-------------|
| `test_freq_is_readonly` | Verifies freq cannot be set directly |
| `test_fmin_setter` | Tests fmin setter |
| `test_fmax_setter` | Tests fmax setter |
| `test_fstep_setter` | Tests fstep setter |
| `test_update_from_exponents` | Tests update_from_exponents() method |

### TestFrequenciesEdgeCases

Tests special values.

| Test Method | Description |
|-------------|-------------|
| `test_very_small_range` | Tests fmin≈fmax (single decade) |
| `test_very_large_range` | Tests 0 to 15 decades |
| `test_fractional_exponents` | Tests non-integer exponents |
| `test_large_step` | Tests dense array generation |

### TestFrequenciesMethods

Tests utility methods.

| Test Method | Description |
|-------------|-------------|
| `test_len` | Tests `__len__` returns array length |
| `test_repr` | Tests `__repr__` contains key info |
| `test_repr_explicit_list` | Tests repr for explicit list mode |
| `test_str` | Tests `__str__` is readable |

### TestFrequenciesArrayProperties

Tests array characteristics.

| Test Method | Description |
|-------------|-------------|
| `test_all_positive` | Verifies all frequencies > 0 |
| `test_strictly_increasing` | Verifies sorted ascending order |
| `test_no_duplicates` | Verifies unique values |
| `test_finite_values` | Verifies no inf or NaN |
| `test_reasonable_values` | Tests 0.1 Hz to 100 GHz range |

### TestFrequenciesNumericalStability

Tests numerical precision.

| Test Method | Description |
|-------------|-------------|
| `test_round_trip_exponents` | Tests same params give same result |
| `test_precision_maintained` | Tests significant figures maintained |

### TestFrequenciesComparison

Tests different configurations.

| Test Method | Description |
|-------------|-------------|
| `test_different_steps_same_range` | Tests coverage with different steps |
| `test_points_per_decade_consistent` | Tests reasonable point density |

### TestFrequenciesIntegration

Tests realistic use cases.

| Test Method | Description |
|-------------|-------------|
| `test_lhc_range` | Tests 1 Hz to 10 GHz (LHC typical) |
| `test_resonance_frequencies` | Tests specific cavity resonances |

---

## Frequency Generation Algorithm

The `Frequencies` class generates points using:

```
fmin, fmax: exponents (powers of 10)
fstep: points per decade

Frequencies span from 10^fmin to 10^fmax Hz
with approximately fstep points per decade.

Note: Larger fstep → MORE points (counterintuitive naming)
```

---

## Example Usage

```python
from pytlwall import Frequencies

# Default: 1 Hz to 100 MHz with medium density
freq = Frequencies()
print(f"Generated {len(freq)} frequencies")
print(f"Range: {freq.freq[0]:.1e} to {freq.freq[-1]:.1e} Hz")

# High resolution for narrow band
freq_hr = Frequencies(fmin=6, fmax=9, fstep=10)
print(f"High-res: {len(freq_hr)} points, 1 MHz to 1 GHz")

# Explicit resonance frequencies
resonances = Frequencies(freq_list=[400.79e6, 800e6, 1200e6])
print(f"Resonances: {resonances.freq}")
```

---

[← Back to Testing Documentation](../TESTING.md)
