# test_beam.py - Beam Class Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `Beam` class which handles relativistic beam kinematics calculations and parameter handling.

**Module tested**: `pytlwall.beam`

**Run this test**:
```bash
python tests/test_beam.py -v
```

---

## Test Classes

### TestBeamInitialization

Tests various beam initialization methods.

| Test Method | Description |
|-------------|-------------|
| `test_default_initialization` | Verifies default ultra-relativistic beam (β=1, γ=∞) |
| `test_init_with_gammarel` | Tests initialization with `gammarel` parameter |
| `test_init_with_gamma` | Tests initialization with `gamma` alias parameter |
| `test_gamma_gammarel_equivalence` | Verifies `gamma` and `gammarel` produce identical results |
| `test_both_gamma_and_gammarel` | Tests priority when both parameters provided |
| `test_init_with_Ekin` | Tests initialization with kinetic energy (MeV) |
| `test_init_with_betarel` | Tests initialization with relativistic β |
| `test_init_with_momentum` | Tests initialization with momentum (MeV/c) |
| `test_custom_test_beam_shift` | Tests custom test beam shift value |
| `test_custom_mass` | Tests custom particle mass (e.g., electron) |
| `test_invalid_mass` | Verifies error raised for invalid mass |

### TestBeamParameterPriority

Tests the priority order of initialization parameters.

| Test Method | Description |
|-------------|-------------|
| `test_Ekin_priority_over_gamma` | Verifies Ekin_MeV takes priority over gamma |
| `test_Ekin_priority_over_gammarel` | Verifies Ekin_MeV takes priority over gammarel |
| `test_p_priority_over_beta` | Verifies momentum takes priority over betarel |
| `test_beta_priority_over_gamma` | Verifies betarel takes priority over gamma |

### TestBeamSetters

Tests property setters and validation.

| Test Method | Description |
|-------------|-------------|
| `test_set_gammarel` | Tests gammarel setter updates β correctly |
| `test_set_betarel` | Tests betarel setter updates γ correctly |
| `test_set_Ekin_MeV` | Tests kinetic energy setter |
| `test_set_p_MeV_c` | Tests momentum setter |
| `test_invalid_gammarel` | Tests rejection of γ < 1 |
| `test_invalid_betarel` | Tests rejection of β > 1 |
| `test_invalid_Ekin` | Tests rejection of negative energy |
| `test_invalid_momentum` | Tests rejection of negative momentum |

### TestBeamPhysics

Tests relativistic physics calculations.

| Test Method | Description |
|-------------|-------------|
| `test_ultra_relativistic_limit` | Tests β → 1 limit |
| `test_non_relativistic` | Tests β << 1 case |
| `test_relativistic_relations` | Verifies E = γmc², E_kin = (γ-1)mc², p = γmβc |
| `test_velocity_calculation` | Tests velocity = βc calculation |

### TestBeamConstants

Tests exported physical constants.

| Test Method | Description |
|-------------|-------------|
| `test_proton_mass_export` | Verifies m_p_MeV and M_PROTON_MEV values |

### TestBeamStringRepresentation

Tests string output methods.

| Test Method | Description |
|-------------|-------------|
| `test_repr` | Tests `__repr__` contains key info |
| `test_str` | Tests `__str__` is human-readable |

### TestBeamEdgeCases

Tests boundary conditions and extreme values.

| Test Method | Description |
|-------------|-------------|
| `test_gamma_exactly_one` | Tests γ = 1 (particle at rest) |
| `test_very_large_gamma` | Tests γ = 10¹² (extreme relativistic) |
| `test_beta_exactly_one` | Tests β = 1 (speed of light) |

---

## Key Equations Tested

The beam class implements these relativistic relations:

```
β = v/c
γ = 1/√(1 - β²)
E_tot = γ m c²
E_kin = (γ - 1) m c²
p = γ m β c
```

---

## Example Usage

```python
from pytlwall.beam import Beam

# LHC proton beam (7 TeV)
beam = Beam(gamma=7460.52)
print(f"β = {beam.betarel:.10f}")  # ~0.9999999991
print(f"E_kin = {beam.Ekin_MeV/1e6:.2f} TeV")  # ~7 TeV

# Low energy beam
beam_low = Beam(Ekin_MeV=100)
print(f"γ = {beam_low.gammarel:.2f}")  # ~1.107
```

---

[← Back to Testing Documentation](../TESTING.md)
