# beam Module API Reference

## Overview

The `beam` module provides the `Beam` class for handling relativistic particle beam parameters in accelerator physics calculations.

The `Beam` class represents a particle beam, managing relativistic parameters such as the Lorentz factor (γ), relativistic beta (β), kinetic energy, and momentum. It provides automatic conversions between different representations of beam energy and velocity while maintaining internal consistency.

## Table of Contents

- [Import](#import)
- [Beam Class](#beam-class)
- [Attributes](#attributes)
- [Methods](#methods)
- [Constants](#constants)
- [Exceptions](#exceptions)
- [Usage Examples](#usage-examples)
- [Notes and Conventions](#notes-and-conventions)
- [See Also](#see-also)

---

## Import

```python
from pytlwall import Beam
# or
from pytlwall.beam import Beam, BeamValidationError, M_PROTON_MEV
```

---

## Beam Class

### Class Definition

```python
class Beam:
    """
    Relativistic particle beam representation.
    
    This class encapsulates the kinematic properties of a relativistic
    particle beam, automatically maintaining consistency between different
    representations (beta, gamma, kinetic energy, momentum).
    """
```

### Constructor

```python
Beam(
    Ekin_MeV=None,
    p_MeV_c=None,
    betarel=None,
    gammarel=None,
    test_beam_shift=0.001,
    mass_MeV_c2=938.272
)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `Ekin_MeV` | `float` | `inf` | Kinetic energy in MeV |
| `p_MeV_c` | `float` | `inf` | Momentum in MeV/c |
| `betarel` | `float` | `1.0` | Relativistic beta (β = v/c) |
| `gammarel` | `float` | `inf` | Lorentz gamma factor (γ) |
| `test_beam_shift` | `float` | `0.001` | Test beam distance offset in meters |
| `mass_MeV_c2` | `float` | `M_PROTON_MEV` | Particle rest mass energy in MeV/c² |

#### Priority Order

When multiple parameters are provided, the priority is:

1. `Ekin_MeV` (highest priority)
2. `p_MeV_c`
3. `betarel`
4. `gammarel` (lowest priority)

If no parameters are provided, defaults to ultra-relativistic limit (β = 1).

#### Raises

- `BeamValidationError`: If mass is invalid (≤ 0) or kinematic parameters are out of valid range

#### Examples

```python
from pytlwall.beam import Beam

# Create beam from gamma (LHC 7 TeV protons)
beam1 = Beam(gammarel=7460.52)

# Create beam from kinetic energy
beam2 = Beam(Ekin_MeV=7e6)  # 7 TeV

# Create beam from beta
beam3 = Beam(betarel=0.999999991)

# Create beam from momentum
beam4 = Beam(p_MeV_c=7000000)

# Ultra-relativistic (default)
beam5 = Beam()  # β = 1, γ = inf
```

---

## Attributes

### `betarel`

**Type:** `float` (read/write)

**Description:** Relativistic beta factor (β = v/c).

**Range:** 0 < β ≤ 1

**Notes:** Setting this property automatically updates `gammarel`, `Ekin_MeV`, and `p_MeV_c`.

**Example:**

```python
beam = Beam(gammarel=2.0)
print(f"Beta: {beam.betarel:.6f}")  # Output: Beta: 0.866025

# Modify beta
beam.betarel = 0.9
print(f"New gamma: {beam.gammarel:.4f}")  # Automatically updated
```

---

### `gammarel`

**Type:** `float` (read/write)

**Description:** Lorentz gamma factor (γ).

**Range:** γ ≥ 1 (1 for rest, inf for ultra-relativistic)

**Definition:** γ = 1/√(1-β²)

**Notes:** Setting this property automatically updates `betarel`, `Ekin_MeV`, and `p_MeV_c`.

**Example:**

```python
beam = Beam(gammarel=7460.52)
print(f"Gamma: {beam.gammarel:.2f}")  # Output: Gamma: 7460.52
```

---

### `Ekin_MeV`

**Type:** `float` (read/write)

**Description:** Kinetic energy in MeV.

**Formula:** E_kin = (γ - 1) × m × c²

**Notes:** Setting this property automatically updates `betarel`, `gammarel`, and `p_MeV_c`.

**Example:**

```python
beam = Beam(gammarel=2.0)
print(f"Kinetic energy: {beam.Ekin_MeV:.2f} MeV")
```

---

### `p_MeV_c`

**Type:** `float` (read/write)

**Description:** Momentum in MeV/c.

**Formula:** p = γ × m × β × c

**Notes:** Setting this property automatically updates `betarel`, `gammarel`, and `Ekin_MeV`.

**Example:**

```python
beam = Beam(p_MeV_c=7000000)  # 7 TeV/c momentum
print(f"Momentum: {beam.p_MeV_c:.0f} MeV/c")
```

---

### `E_tot_MeV`

**Type:** `float` (read-only)

**Description:** Total energy in MeV.

**Formula:** E_tot = γ × m × c² = E_kin + m × c²

**Example:**

```python
beam = Beam(gammarel=2.0)
print(f"Total energy: {beam.E_tot_MeV:.2f} MeV")
print(f"Verification: {beam.Ekin_MeV + beam.mass_MeV_c2:.2f} MeV")
```

---

### `test_beam_shift`

**Type:** `float` (read/write)

**Description:** Test beam distance offset in meters for impedance calculations.

**Default:** 0.001 m (1 mm)

**Example:**

```python
beam = Beam(gammarel=7460.52)
beam.test_beam_shift = 0.002  # 2 mm offset
```

---

### `mass_MeV_c2`

**Type:** `float` (read-only)

**Description:** Particle rest mass energy in MeV/c².

**Default:** Proton mass (938.272 MeV/c²)

**Example:**

```python
beam = Beam(gammarel=2.0)
print(f"Proton mass: {beam.mass_MeV_c2:.3f} MeV/c²")

# Electron beam
electron_beam = Beam(gammarel=1000, mass_MeV_c2=0.511)
```

---

## Methods

### Property Setters

Each kinematic property (`betarel`, `gammarel`, `Ekin_MeV`, `p_MeV_c`) has a setter that:
1. Validates the input value
2. Updates the internal state
3. Automatically recalculates all dependent quantities

**Validation Behavior:**
- Invalid values raise `BeamValidationError`
- All kinematic parameters remain consistent after any change

**Example:**

```python
beam = Beam(betarel=0.5)
print(f"Initial: β={beam.betarel:.4f}, γ={beam.gammarel:.4f}")

beam.gammarel = 5.0  # Change gamma
print(f"After:   β={beam.betarel:.6f}, γ={beam.gammarel:.4f}")
# β is automatically recalculated
```

---

### `__repr__()` / `__str__()`

String representations of the Beam object.

**Example:**

```python
beam = Beam(gammarel=7460.52)
print(repr(beam))
# Output: Beam(β=0.999999991, γ=7460.52, E_kin=7.00e+06 MeV)
```

---

## Constants

### `M_PROTON_MEV`

**Type:** `float`

**Value:** 938.27208816 MeV/c² (CODATA 2018)

**Description:** Proton rest mass energy equivalent.

**Usage:**

```python
from pytlwall.beam import M_PROTON_MEV

print(f"Proton mass: {M_PROTON_MEV:.6f} MeV/c²")
```

---

## Exceptions

### `BeamValidationError`

```python
class BeamValidationError(ValueError):
    """Exception raised for invalid beam parameter values."""
```

**Raised when:**
- `betarel` ≤ 0 or > 1
- `gammarel` < 1
- `Ekin_MeV` < 0
- `p_MeV_c` < 0
- `mass_MeV_c2` ≤ 0

**Example:**

```python
from pytlwall.beam import Beam, BeamValidationError

try:
    beam = Beam(betarel=1.5)  # Invalid: β > 1
except BeamValidationError as e:
    print(f"Error: {e}")
```

---

## Usage Examples

### Example 1: LHC Proton Beam at 7 TeV

```python
from pytlwall.beam import Beam

# Create beam from kinetic energy
lhc_beam = Beam(Ekin_MeV=7e6)  # 7 TeV

print(f"LHC 7 TeV Proton Beam:")
print(f"  Gamma: {lhc_beam.gammarel:.2f}")
print(f"  Beta:  {lhc_beam.betarel:.10f}")
print(f"  Kinetic Energy: {lhc_beam.Ekin_MeV/1e6:.2f} TeV")
print(f"  Momentum: {lhc_beam.p_MeV_c/1e6:.2f} TeV/c")
```

### Example 2: Converting Between Representations

```python
from pytlwall.beam import Beam

# Start with beta
beam = Beam(betarel=0.9)
print(f"From β=0.9:")
print(f"  γ = {beam.gammarel:.4f}")
print(f"  E_kin = {beam.Ekin_MeV:.2f} MeV")
print(f"  p = {beam.p_MeV_c:.2f} MeV/c")

# Change to different gamma
beam.gammarel = 10.0
print(f"\nAfter setting γ=10:")
print(f"  β = {beam.betarel:.6f}")
print(f"  E_kin = {beam.Ekin_MeV:.2f} MeV")
```

### Example 3: Electron Beam

```python
from pytlwall.beam import Beam

# Electron at 100 GeV
electron = Beam(
    Ekin_MeV=100000,  # 100 GeV
    mass_MeV_c2=0.511  # Electron mass
)

print(f"100 GeV Electron:")
print(f"  Gamma: {electron.gammarel:.0f}")
print(f"  Beta:  {electron.betarel:.12f}")
```

### Example 4: Low Energy vs High Energy

```python
from pytlwall.beam import Beam

# Low energy (non-relativistic)
low_energy = Beam(gammarel=1.1)
print(f"Low energy (γ=1.1):")
print(f"  β = {low_energy.betarel:.4f}")
print(f"  v/c = {low_energy.betarel*100:.2f}%")

# High energy (ultra-relativistic)
high_energy = Beam(gammarel=7460)
print(f"\nHigh energy (γ=7460):")
print(f"  β = {high_energy.betarel:.10f}")
print(f"  1 - β = {1-high_energy.betarel:.2e}")
```

### Example 5: Integration with TlWall

```python
from pytlwall import Beam, Frequencies, Layer, Chamber, TlWall

# Define LHC beam
beam = Beam(gammarel=7460.52)

# Create chamber with layers
freqs = Frequencies(fmin=3, fmax=9, fstep=2)
chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# Calculate impedance
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.calc_ZLong()

print(f"Calculated for beam with β={beam.betarel:.6f}")
```

---

## Notes and Conventions

### Relativistic Relations

The `Beam` class uses these fundamental relations:

| Relation | Formula |
|----------|---------|
| Lorentz factor | γ = 1/√(1-β²) |
| Beta factor | β = √(1-1/γ²) |
| Kinetic energy | E_kin = (γ-1)·m·c² |
| Total energy | E_tot = γ·m·c² |
| Momentum | p = γ·m·β·c |
| Energy-momentum | E_tot² = (pc)² + (mc²)² |

### Typical Beam Parameters

| Accelerator | Particle | Energy | γ | β |
|-------------|----------|--------|---|---|
| LHC | Proton | 7 TeV | 7460.52 | 0.999999991 |
| SPS | Proton | 450 GeV | 479.6 | 0.999998 |
| Tevatron | Proton | 980 GeV | 1044.6 | 0.999999543 |
| LEP | Electron | 100 GeV | 195695 | 0.999999999987 |
| RHIC | Au ion | 100 GeV/u | 107.4 | 0.99996 |

### Ultra-Relativistic Limit

When no parameters are specified, the beam defaults to the ultra-relativistic limit:
- β = 1.0
- γ = ∞
- E_kin = ∞
- p = ∞

This is useful for quick calculations where the exact beam energy is not critical.

### Parameter Priority

The constructor priority ensures that if you specify multiple parameters, the most physically meaningful one takes precedence:

```python
# Ekin_MeV takes priority - other parameters ignored
beam = Beam(Ekin_MeV=1000, gammarel=100)
# Result: gammarel will be calculated from Ekin_MeV, not 100
```

---

## See Also

- [frequencies Module](API_REFERENCE_FREQUENCIES.md) - Frequency range definition
- [layer Module](API_REFERENCE_LAYER.md) - Material layer properties
- [chamber Module](API_REFERENCE_CHAMBER.md) - Chamber geometry definitions
- [tlwall Module](API_REFERENCE_TLWALL.md) - Main impedance calculator
- [Main API Reference](API_REFERENCE.md) - Complete API documentation

---

*Last updated: December 2025*
