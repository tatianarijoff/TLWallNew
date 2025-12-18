# frequencies Module Examples

![PyTlWall Logo](logo005.png)

**Frequency Array Management for Impedance Calculations**

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
| **frequencies** | *You are here* |
| layer | [EXAMPLES_LAYER.md](EXAMPLES_LAYER.md) |
| chamber | [EXAMPLES_CHAMBER.md](EXAMPLES_CHAMBER.md) |
| tlwall | [EXAMPLES_TLWALL.md](EXAMPLES_TLWALL.md) |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |

---

## Table of Contents

- [Overview](#overview)
- [Example 1: Basic Logarithmic Array](#example-1-basic-logarithmic-array)
- [Example 2: Explicit Frequency List](#example-2-explicit-frequency-list)
- [Example 3: LHC Calculation Range](#example-3-lhc-calculation-range)
- [Example 4: Resolution Comparison](#example-4-resolution-comparison)
- [Example 5: Dynamic Update](#example-5-dynamic-update)
- [Example 6: Integration with TlWall](#example-6-integration-with-tlwall)
- [Example 7: Practical Workflow](#example-7-practical-workflow)
- [Parameter Reference](#parameter-reference)

---

## Overview

The `Frequencies` class creates and manages frequency arrays for impedance calculations. It supports logarithmic spacing (most common) or explicit frequency lists.

```python
import pytlwall

# Logarithmic array: 10^fmin to 10^fmax Hz
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)

# Explicit list
freqs = pytlwall.Frequencies(freq_list=[1e6, 10e6, 100e6])
```

**Important:** `fmin` and `fmax` are exponents! `fmin=3` means 10³ = 1 kHz.

---

## Example 1: Basic Logarithmic Array

Create a frequency array from 1 Hz to 1 MHz.

```python
import pytlwall

# Logarithmic array from 10^0 = 1 Hz to 10^6 = 1 MHz
freqs = pytlwall.Frequencies(fmin=0, fmax=6, fstep=2)

print(f"Frequency array parameters:")
print(f"  Minimum exponent:  {freqs.fmin}")
print(f"  Maximum exponent:  {freqs.fmax}")
print(f"  Step parameter:    {freqs.fstep}")
print(f"  Number of points:  {len(freqs)}")
print(f"  Minimum frequency: {freqs.freq[0]:.2e} Hz")
print(f"  Maximum frequency: {freqs.freq[-1]:.2e} Hz")

print(f"\nFirst 5 frequencies:")
for i, f in enumerate(freqs.freq[:5]):
    print(f"  [{i+1}] {f:.2e} Hz")

print(f"\nLast 5 frequencies:")
for i, f in enumerate(freqs.freq[-5:]):
    print(f"  [{len(freqs)-4+i}] {f:.2e} Hz")
```

---

## Example 2: Explicit Frequency List

Use specific frequencies (e.g., resonant modes).

```python
import pytlwall

# Define specific frequencies of interest
resonances = [
    455e3,    # 455 kHz
    1.2e6,    # 1.2 MHz
    2.8e6,    # 2.8 MHz
    5.5e6,    # 5.5 MHz
    12.0e6,   # 12 MHz
    25.0e6,   # 25 MHz
]

freqs = pytlwall.Frequencies(freq_list=resonances)

print(f"Custom frequency list:")
print(f"  Number of points:  {len(freqs)}")

print(f"\nAll frequencies:")
for i, f in enumerate(freqs.freq):
    print(f"  Mode {i+1}: {f/1e6:.2f} MHz")
```

**Notes:**
- Frequencies are automatically sorted
- Useful for analyzing specific resonant modes
- `fstep` is set to 0 for explicit lists

---

## Example 3: LHC Calculation Range

Wide frequency range typical for LHC impedance calculations.

```python
import pytlwall
import numpy as np

# LHC: wide range from 1 Hz to 10 GHz
freqs = pytlwall.Frequencies(fmin=0, fmax=10, fstep=2)

print(f"LHC frequency range:")
print(f"  Range:           10^{freqs.fmin} to 10^{freqs.fmax} Hz")
print(f"  Actual range:    {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
print(f"  Number of points: {len(freqs)}")

# Analyze distribution per decade
print(f"\nPoints per decade:")
for decade in range(int(freqs.fmin), int(freqs.fmax)):
    low = 10**decade
    high = 10**(decade + 1)
    count = np.sum((freqs.freq >= low) & (freqs.freq < high))
    print(f"  10^{decade:2d} - 10^{decade+1:2d} Hz: {count:4d} points")
```

**Notes:**
- Wide range covers all relevant impedance contributions
- From resistive wall (low f) to broadband (high f)
- Typical calculation time: minutes to hours depending on complexity

---

## Example 4: Resolution Comparison

Understanding the `fstep` parameter.

```python
import pytlwall

# Same range, different resolutions
# IMPORTANT: Larger fstep = MORE points per decade!

freqs_low = pytlwall.Frequencies(fmin=3, fmax=6, fstep=1)   # Low resolution
freqs_med = pytlwall.Frequencies(fmin=3, fmax=6, fstep=2)   # Medium
freqs_high = pytlwall.Frequencies(fmin=3, fmax=6, fstep=3)  # High resolution

print(f"Same range (1 kHz to 1 MHz), different resolutions:")
print(f"  fstep=1 (low):    {len(freqs_low):5d} points")
print(f"  fstep=2 (medium): {len(freqs_med):5d} points")
print(f"  fstep=3 (high):   {len(freqs_high):5d} points")

print(f"\nRatio high/low: {len(freqs_high)/len(freqs_low):.1f}x more points")

print(f"\nFirst 5 points comparison:")
print(f"{'Index':>6} {'Low (fstep=1)':>15} {'Med (fstep=2)':>15} {'High (fstep=3)':>15}")
print("-" * 55)
for i in range(5):
    print(f"{i+1:6d} {freqs_low.freq[i]:>15.2e} {freqs_med.freq[i]:>15.2e} {freqs_high.freq[i]:>15.2e}")
```

### Resolution Guide

| fstep | Resolution | Points/decade | Use Case |
|-------|------------|---------------|----------|
| 1 | Low | ~10 | Quick scans, initial analysis |
| 2 | Medium | ~20 | Standard calculations |
| 3 | High | ~30 | Detailed analysis, convergence |

**⚠️ Key Point:** Larger `fstep` = MORE points = Higher resolution

---

## Example 5: Dynamic Update

Update frequency range during analysis.

```python
import pytlwall

# Step 1: Start with broad scan (low resolution)
print("Step 1: Initial broad scan")
freqs = pytlwall.Frequencies(fmin=0, fmax=10, fstep=1)
print(f"  Range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
print(f"  Points: {len(freqs)}")

# Step 2: Identify interesting region (e.g., 1 MHz - 100 MHz)
print("\nStep 2: Identify interesting region")
print(f"  Found peaks between 10^6 and 10^8 Hz")

# Step 3: Zoom in with higher resolution
print("\nStep 3: Zoom in with higher resolution")
freqs.update_from_exponents(fmin=6, fmax=8, fstep=3)
print(f"  New range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
print(f"  New points: {len(freqs)}")
```

**Workflow:**
1. Quick scan (fstep=1) → identify impedance peaks
2. Detailed scan (fstep=3) → accurate characterization
3. Saves computation time vs. always using high resolution

---

## Example 6: Integration with TlWall

Using Frequencies with impedance calculations.

```python
import pytlwall

# Create frequency array
freqs = pytlwall.Frequencies(fmin=3, fmax=9, fstep=2)

# Setup beam and chamber
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')

# Layer needs the frequency array
copper = pytlwall.Layer(
    thick_m=0.001,
    sigmaDC=5.96e7,
    freq_Hz=freqs.freq  # Pass frequency array here!
)
chamber.layers = [copper]

# Calculate impedances
wall = pytlwall.TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.ZLong

print(f"Impedance calculated at {len(freqs)} frequency points")
print(f"ZLong[0] at {freqs.freq[0]:.2e} Hz: {abs(ZLong[0]):.3e} Ω")
print(f"ZLong[-1] at {freqs.freq[-1]:.2e} Hz: {abs(ZLong[-1]):.3e} Ω")
```

**Important:** The `Layer` object requires `freq_Hz=freqs.freq` to compute frequency-dependent properties!

---

## Example 7: Practical Workflow

Complete workflow for impedance studies.

```python
import pytlwall

print("SCENARIO: Analyzing impedance of a new chamber design")

# Step 1: Preliminary broad scan
print("\n1. Preliminary broad scan")
freqs_broad = pytlwall.Frequencies(fmin=0, fmax=10, fstep=1)
print(f"   {len(freqs_broad)} points from 1 Hz to 10 GHz")
print(f"   Purpose: Identify general behavior and peaks")

# Step 2: Identify critical regions
print("\n2. Critical frequency regions identified:")
print("   - Low frequency: < 1 kHz (resistive wall)")
print("   - Mid frequency: 10-100 MHz (trapped modes)")
print("   - High frequency: > 1 GHz (broadband)")

# Step 3: Detailed scan of trapped mode region
print("\n3. Detailed scan of trapped mode region")
freqs_detailed = pytlwall.Frequencies(fmin=7, fmax=8, fstep=3)
print(f"   {len(freqs_detailed)} points from 10 MHz to 100 MHz")
print(f"   Purpose: Accurate resonance characterization")

# Step 4: Beam harmonic frequencies
print("\n4. Beam harmonic frequencies")
f_rev = 11.245e3  # LHC revolution frequency (Hz)
harmonics = [f_rev * n for n in [1, 10, 100, 1000, 10000]]
freqs_beam = pytlwall.Frequencies(freq_list=harmonics)
print(f"   {len(freqs_beam)} beam revolution harmonics")
print(f"   Purpose: Check impedance at critical frequencies")

# Summary
print("\n5. Frequency ranges used:")
print(f"   Broad scan:     {freqs_broad}")
print(f"   Detailed scan:  {freqs_detailed}")
print(f"   Beam harmonics: {freqs_beam}")
```

---

## Parameter Reference

### Constructor Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `fmin` | int/float | Minimum frequency exponent (10^fmin Hz) |
| `fmax` | int/float | Maximum frequency exponent (10^fmax Hz) |
| `fstep` | int | Resolution parameter (larger = more points) |
| `freq_list` | list | Explicit frequency list (overrides fmin/fmax/fstep) |

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `freq` | ndarray | Array of frequencies in Hz |
| `fmin` | float | Minimum exponent (or min freq for explicit list) |
| `fmax` | float | Maximum exponent (or max freq for explicit list) |
| `fstep` | int | Resolution parameter (0 for explicit list) |

### Methods

| Method | Description |
|--------|-------------|
| `update_from_exponents(fmin, fmax, fstep)` | Update to new range |
| `__len__()` | Number of frequency points |

---

## See Also

- [API Reference - Frequencies](API_REFERENCE_FREQUENCIES.md) - Complete API documentation
- [Examples Main Page](EXAMPLES.md) - All module examples

---

**[◀ Back to Examples](EXAMPLES.md)** | **[◀ Previous: beam](EXAMPLES_BEAM.md)** | **[Next: layer ▶](EXAMPLES_LAYER.md)**
