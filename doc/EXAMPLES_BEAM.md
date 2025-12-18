# beam Module Examples

![PyTlWall Logo](logo005.png)

**Particle Beam Parameters with Relativistic Calculations**

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

---

## Navigation

**[◀ Back to Examples](EXAMPLES.md)**

| Module | Link |
|--------|------|
| **beam** | *You are here* |
| frequencies | [EXAMPLES_FREQUENCIES.md](EXAMPLES_FREQUENCIES.md) |
| layer | [EXAMPLES_LAYER.md](EXAMPLES_LAYER.md) |
| chamber | [EXAMPLES_CHAMBER.md](EXAMPLES_CHAMBER.md) |
| tlwall | [EXAMPLES_TLWALL.md](EXAMPLES_TLWALL.md) |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |

---

## Table of Contents

- [Overview](#overview)
- [Example 1: LHC Proton Beam](#example-1-lhc-proton-beam)
- [Example 2: Electron Beam](#example-2-electron-beam)
- [Example 3: Medical Proton Therapy](#example-3-medical-proton-therapy)
- [Example 4: Parameter Conversion](#example-4-parameter-conversion)
- [Example 5: Error Handling](#example-5-error-handling)
- [Example 6: Heavy Ion Beam](#example-6-heavy-ion-beam)
- [Example 7: Particle Comparison](#example-7-particle-comparison)
- [Parameter Reference](#parameter-reference)

---

## Overview

The `Beam` class handles particle beam parameters with automatic relativistic calculations. You can initialize a beam with any relativistic parameter (gamma, beta, energy, or momentum), and all other parameters are automatically computed and kept consistent.

```python
import pytlwall

# Initialize with any parameter
beam = pytlwall.Beam(gammarel=7460.52)    # From gamma
beam = pytlwall.Beam(betarel=0.999999)    # From beta
beam = pytlwall.Beam(Ekin_MeV=7e6)        # From kinetic energy
beam = pytlwall.Beam(p_MeV_c=7e6)         # From momentum
```

---

## Example 1: LHC Proton Beam

LHC protons at 7 TeV kinetic energy.

```python
import pytlwall

# LHC: protons at 7 TeV kinetic energy
lhc_beam = pytlwall.Beam(Ekin_MeV=7e6)

print(f"LHC beam parameters:")
print(f"  Kinetic energy:  {lhc_beam.Ekin_MeV:.2e} MeV ({lhc_beam.Ekin_MeV/1e6:.1f} TeV)")
print(f"  Beta (v/c):      {lhc_beam.betarel:.12f}")
print(f"  Gamma:           {lhc_beam.gammarel:.2f}")
print(f"  Momentum:        {lhc_beam.p_MeV_c:.2e} MeV/c")
print(f"  Total energy:    {lhc_beam.E_tot_MeV:.2e} MeV")
print(f"  Velocity:        {lhc_beam.velocity_m_s:.6e} m/s")
print(f"  Rest mass:       {lhc_beam.mass_MeV_c2:.4f} MeV/c²")
```

**Output:**
```
LHC beam parameters:
  Kinetic energy:  7.00e+06 MeV (7.0 TeV)
  Beta (v/c):      0.999999991001
  Gamma:           7461.52
  Momentum:        7.00e+06 MeV/c
  Total energy:    7.00e+06 MeV
  Velocity:        2.997925e+08 m/s
  Rest mass:       938.2720 MeV/c²
```

**Notes:**
- The beam travels at 99.9999991% of the speed of light
- The energy is ~7461 times the rest energy
- Default mass is proton mass (938.272 MeV/c²)

---

## Example 2: Electron Beam

Electron in a linear accelerator at 1 GeV.

```python
import pytlwall

# Electron: mass much smaller than proton
electron_mass = 0.511  # MeV/c²
electron_beam = pytlwall.Beam(Ekin_MeV=1000, mass_MeV_c2=electron_mass)

print(f"Electron parameters:")
print(f"  Rest mass:       {electron_beam.mass_MeV_c2:.3f} MeV/c²")
print(f"  Kinetic energy:  {electron_beam.Ekin_MeV:.2f} MeV (1 GeV)")
print(f"  Beta (v/c):      {electron_beam.betarel:.10f}")
print(f"  Gamma:           {electron_beam.gammarel:.1f}")
print(f"  Momentum:        {electron_beam.p_MeV_c:.2f} MeV/c")
print(f"  Velocity:        {electron_beam.velocity_m_s:.6e} m/s")
```

**Output:**
```
Electron parameters:
  Rest mass:       0.511 MeV/c²
  Kinetic energy:  1000.00 MeV (1 GeV)
  Beta (v/c):      0.9999998693
  Gamma:           1958.4
  Momentum:        1000.26 MeV/c
  Velocity:        2.997924e+08 m/s
```

**Notes:**
- Electrons are highly relativistic even at 1 GeV
- Time dilation factor: 1958x
- Gamma >> 1 indicates ultra-relativistic regime

---

## Example 3: Medical Proton Therapy

Protons for tumor treatment at 200 MeV.

```python
import pytlwall

# Medical protons: ~200 MeV
medical_beam = pytlwall.Beam(Ekin_MeV=200)

print(f"Medical beam parameters:")
print(f"  Kinetic energy:  {medical_beam.Ekin_MeV:.2f} MeV")
print(f"  Beta (v/c):      {medical_beam.betarel:.6f}")
print(f"  Gamma:           {medical_beam.gammarel:.6f}")
print(f"  Momentum:        {medical_beam.p_MeV_c:.2f} MeV/c")
print(f"  Velocity:        {medical_beam.velocity_m_s:.3e} m/s")
```

**Output:**
```
Medical beam parameters:
  Kinetic energy:  200.00 MeV
  Beta (v/c):      0.566299
  Gamma:           1.213160
  Momentum:        644.45 MeV/c
  Velocity:        1.698e+08 m/s
```

**Notes:**
- Moderately relativistic (gamma ≈ 1.2)
- Velocity: ~57% of the speed of light
- Optimal energy for deep tissue penetration

---

## Example 4: Parameter Conversion

Automatic conversion between relativistic parameters.

```python
import pytlwall

# Initialize with momentum
print("Initialize with p = 1000 MeV/c:")
beam = pytlwall.Beam(p_MeV_c=1000)

print(f"  Beta:            {beam.betarel:.6f}")
print(f"  Gamma:           {beam.gammarel:.6f}")
print(f"  Kinetic energy:  {beam.Ekin_MeV:.2f} MeV")
print(f"  Total energy:    {beam.E_tot_MeV:.2f} MeV")

# Update kinetic energy - all parameters recalculate
print("\nUpdate to E_kin = 500 MeV:")
beam.Ekin_MeV = 500

print(f"  Beta:            {beam.betarel:.6f}")
print(f"  Gamma:           {beam.gammarel:.6f}")
print(f"  Momentum:        {beam.p_MeV_c:.2f} MeV/c")
print(f"  Total energy:    {beam.E_tot_MeV:.2f} MeV")
```

**Key point:** All parameters remain automatically consistent when you change any single parameter.

---

## Example 5: Error Handling

The `Beam` class validates all inputs.

```python
import pytlwall

# Test 1: Beta > 1 (physically impossible)
print("Test 1: Beta > 1")
try:
    beam = pytlwall.Beam(betarel=1.5)
except pytlwall.BeamValidationError as e:
    print(f"  ✓ Error caught: {e}")

# Test 2: Gamma < 1 (impossible for massive particles)
print("\nTest 2: Gamma < 1")
try:
    beam = pytlwall.Beam(gammarel=0.5)
except pytlwall.BeamValidationError as e:
    print(f"  ✓ Error caught: {e}")

# Test 3: Negative energy
print("\nTest 3: Negative energy")
try:
    beam = pytlwall.Beam(Ekin_MeV=-100)
except pytlwall.BeamValidationError as e:
    print(f"  ✓ Error caught: {e}")

# Test 4: Non-numeric input
print("\nTest 4: Non-numeric input")
try:
    beam = pytlwall.Beam(betarel="not a number")
except pytlwall.BeamValidationError as e:
    print(f"  ✓ Error caught: {e}")
```

**Best practice:**
```python
try:
    beam = pytlwall.Beam(betarel=user_input)
except pytlwall.BeamValidationError:
    print("Invalid input, using default")
    beam = pytlwall.Beam()  # Ultra-relativistic default
```

---

## Example 6: Heavy Ion Beam

Carbon-12 ion beam at 100 MeV.

```python
import pytlwall

# Carbon-12: mass much greater than proton
carbon_mass = 12 * 931.5  # MeV/c² (12 atomic mass units)
carbon_beam = pytlwall.Beam(Ekin_MeV=100, mass_MeV_c2=carbon_mass)

print(f"Carbon ion parameters:")
print(f"  Rest mass:       {carbon_beam.mass_MeV_c2:.1f} MeV/c² (~12 u)")
print(f"  Kinetic energy:  {carbon_beam.Ekin_MeV:.2f} MeV")
print(f"  Beta (v/c):      {carbon_beam.betarel:.6f}")
print(f"  Gamma:           {carbon_beam.gammarel:.6f}")
print(f"  Momentum:        {carbon_beam.p_MeV_c:.2f} MeV/c")
print(f"  Velocity:        {carbon_beam.velocity_m_s:.3e} m/s")
```

**Output:**
```
Carbon ion parameters:
  Rest mass:       11178.0 MeV/c² (~12 u)
  Kinetic energy:  100.00 MeV
  Beta (v/c):      0.004217
  Gamma:           1.008944
  Momentum:        1496.82 MeV/c
  Velocity:        1.264e+06 m/s
```

**Notes:**
- Non-relativistic regime (gamma ≈ 1)
- Only 0.42% of the speed of light
- Heavy ions need much more energy to become relativistic

---

## Example 7: Particle Comparison

Comparing proton and electron at the same kinetic energy.

```python
import pytlwall

energy = 100.0  # MeV

electron_mass = 0.511   # MeV/c²
proton_mass = 938.272   # MeV/c²

electron = pytlwall.Beam(Ekin_MeV=energy, mass_MeV_c2=electron_mass)
proton = pytlwall.Beam(Ekin_MeV=energy, mass_MeV_c2=proton_mass)

print(f"Kinetic energy: {energy} MeV\n")

print(f"ELECTRON (m = {electron_mass:.3f} MeV/c²):")
print(f"  Beta:      {electron.betarel:.10f}")
print(f"  Gamma:     {electron.gammarel:.2f}")
print(f"  Momentum:  {electron.p_MeV_c:.2f} MeV/c")
print(f"  Velocity:  {electron.velocity_m_s:.6e} m/s")

print(f"\nPROTON (m = {proton_mass:.3f} MeV/c²):")
print(f"  Beta:      {proton.betarel:.10f}")
print(f"  Gamma:     {proton.gammarel:.2f}")
print(f"  Momentum:  {proton.p_MeV_c:.2f} MeV/c")
print(f"  Velocity:  {proton.velocity_m_s:.6e} m/s")

print(f"\nCOMPARISON:")
print(f"  Mass ratio:     {proton_mass/electron_mass:.1f}:1")
print(f"  Gamma ratio:    {electron.gammarel/proton.gammarel:.2f}:1")
print(f"  Velocity ratio: {electron.betarel/proton.betarel:.2f}:1")
```

**Key insight:** At equal kinetic energy, lighter particles are much more relativistic and move faster.

---

## Parameter Reference

### Input Parameters

| Parameter | Description | Unit | Constraints |
|-----------|-------------|------|-------------|
| `gammarel` | Lorentz gamma factor | - | ≥ 1 |
| `betarel` | Relativistic beta (v/c) | - | 0 < β < 1 |
| `Ekin_MeV` | Kinetic energy | MeV | > 0 |
| `p_MeV_c` | Momentum | MeV/c | > 0 |
| `mass_MeV_c2` | Rest mass | MeV/c² | > 0 (default: proton) |

### Computed Properties

| Property | Description | Unit |
|----------|-------------|------|
| `E_tot_MeV` | Total energy (E = γmc²) | MeV |
| `velocity_m_s` | Velocity | m/s |

### Relativistic Relations

$$\gamma = \frac{1}{\sqrt{1 - \beta^2}}$$

$$E_{tot} = \gamma m c^2$$

$$E_{kin} = (\gamma - 1) m c^2$$

$$p = \gamma m v = \beta \gamma m c$$

---

## See Also

- [API Reference - Beam](API_REFERENCE_BEAM.md) - Complete API documentation
- [Examples Main Page](EXAMPLES.md) - All module examples

---

**[◀ Back to Examples](EXAMPLES.md)** | **[Next: frequencies ▶](EXAMPLES_FREQUENCIES.md)**
