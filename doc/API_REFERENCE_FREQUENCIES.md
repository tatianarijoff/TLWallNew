# frequencies Module API Reference

## Overview

The `frequencies` module provides the `Frequencies` class for managing frequency arrays used in impedance calculations.

The `Frequencies` class handles frequency arrays in Hertz at which impedances are calculated. Frequencies can be specified explicitly as a list or generated logarithmically from exponents (base 10), providing good coverage across multiple orders of magnitude.

This is essential for impedance calculations as different frequency ranges reveal different physical phenomena in accelerator components.

## Table of Contents

- [Import](#import)
- [Frequencies Class](#frequencies-class)
- [Attributes](#attributes)
- [Methods](#methods)
- [Constants](#constants)
- [Usage Examples](#usage-examples)
- [Notes and Conventions](#notes-and-conventions)
- [See Also](#see-also)

---

## Import

```python
from pytlwall import frequencies
# or
from pytlwall.frequencies import Frequencies
```

---

## Frequencies Class

### Class Definition

```python
class Frequencies:
    """
    Manages frequency arrays for impedance calculations.
    
    Frequencies can be provided as an explicit list or generated 
    logarithmically from minimum and maximum exponents.
    """
```

### Constructor

```python
Frequencies(freq_list=None, fmin=0, fmax=8, fstep=2)
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `freq_list` | `array-like` | `None` | Explicit list of frequencies in Hz. If provided, fmin/fmax/fstep are ignored |
| `fmin` | `float` | `0` | Minimum frequency exponent (base 10). Default: 0 → 1 Hz |
| `fmax` | `float` | `8` | Maximum frequency exponent (base 10). Default: 8 → 100 MHz |
| `fstep` | `float` | `2` | Step exponent for logarithmic spacing. **Note**: LARGER values = MORE points (higher resolution) |

#### Notes
- If `freq_list` is provided, it takes precedence over exponent-based generation
- Frequencies from list are automatically sorted
- All frequencies must be positive (> 0 Hz)
- When using exponents, the array is generated logarithmically for better coverage
- **Important:** Larger fstep = MORE points per decade (higher resolution)

#### Examples

```python
from pytlwall.frequencies import Frequencies

# Method 1: Generate from exponents (logarithmic spacing)
freqs = Frequencies(fmin=0, fmax=6, fstep=2)
print(f"Generated {len(freqs)} frequency points")
print(f"Range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")

# Method 2: Provide explicit list
freq_list = [1e3, 1e4, 1e5, 1e6, 1e7]
freqs = Frequencies(freq_list=freq_list)
print(f"Using {len(freqs)} explicit frequencies")
```

---

## Attributes

### `freq`

**Type:** `np.ndarray` (read-only)

**Description:** Array of frequencies in Hertz.

**Notes:**
- This is a read-only property
- Contains all frequency points at which impedance will be calculated
- Always sorted in ascending order

**Example:**

```python
freqs = Frequencies(fmin=3, fmax=5, fstep=1)
print(f"Frequency array: {freqs.freq}")
print(f"First frequency: {freqs.freq[0]:.2e} Hz")
print(f"Last frequency: {freqs.freq[-1]:.2e} Hz")
print(f"Number of points: {len(freqs.freq)}")
```

---

### `fmin`

**Type:** `float`

**Description:** Minimum frequency or its exponent (base 10).

**Notes:**
- When using exponent generation: represents the exponent (e.g., 0 → 10^0 = 1 Hz)
- When using explicit list: represents the actual minimum frequency value
- Setting fmin > fmax will trigger a warning

**Example:**

```python
freqs = Frequencies(fmin=2, fmax=6, fstep=1)
print(f"Minimum exponent: {freqs.fmin}")
print(f"Minimum frequency: {10**freqs.fmin} Hz")

# Update minimum
freqs.fmin = 3
freqs.update_from_exponents(freqs.fmin, freqs.fmax, freqs.fstep)
```

---

### `fmax`

**Type:** `float`

**Description:** Maximum frequency or its exponent (base 10).

**Notes:**
- When using exponent generation: represents the exponent (e.g., 8 → 10^8 = 100 MHz)
- When using explicit list: represents the actual maximum frequency value
- Setting fmax < fmin will trigger a warning

**Example:**

```python
freqs = Frequencies(fmin=0, fmax=9, fstep=2)
print(f"Maximum exponent: {freqs.fmax}")
print(f"Maximum frequency: {10**freqs.fmax:.2e} Hz")
```

---

### `fstep`

**Type:** `float`

**Description:** Step exponent for logarithmic spacing.

**Notes:**
- Controls the density of frequency points per decade
- **Important behavior**: LARGER fstep → MORE points per decade (higher resolution)
- Example: fstep=3 produces ~10x more points than fstep=1
- Set to 0.0 when using explicit frequency list
- This behavior matches the original pytlwall algorithm

**Example:**

```python
# Low resolution (FEWER points) - smaller fstep
freqs_low = Frequencies(fmin=0, fmax=6, fstep=1)
print(f"Low resolution: {len(freqs_low)} points")

# High resolution (MORE points) - larger fstep  
freqs_high = Frequencies(fmin=0, fmax=6, fstep=3)
print(f"High resolution: {len(freqs_high)} points")

# Note: fstep=3 gives MORE points than fstep=1
```

---

## Methods

### `update_from_exponents(fmin, fmax, fstep)`

Update frequency array from new exponents.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `fmin` | `float` | New minimum frequency exponent |
| `fmax` | `float` | New maximum frequency exponent |
| `fstep` | `float` | New step exponent |

**Returns:** None (modifies object in place)

**Example:**

```python
freqs = Frequencies(fmin=0, fmax=6, fstep=2)
print(f"Initial: {len(freqs)} points from {freqs.freq[0]:.1e} to {freqs.freq[-1]:.1e} Hz")

# Update to new range
freqs.update_from_exponents(fmin=3, fmax=9, fstep=1)
print(f"Updated: {len(freqs)} points from {freqs.freq[0]:.1e} to {freqs.freq[-1]:.1e} Hz")
```

---

### `__len__()`

Get number of frequency points.

**Returns:**

| Type | Description |
|------|-------------|
| `int` | Number of frequency points in the array |

**Example:**

```python
freqs = Frequencies(fmin=0, fmax=6, fstep=2)
n_points = len(freqs)
print(f"Calculating impedance at {n_points} frequency points")
```

---

### `__repr__()`

String representation of the Frequencies object.

**Returns:**

| Type | Description |
|------|-------------|
| `str` | Formatted string showing key parameters |

**Example:**

```python
freqs1 = Frequencies(fmin=0, fmax=6, fstep=2)
print(freqs1)
# Output: Frequencies(n=500, fmin=0, fmax=6, fstep=2)

freqs2 = Frequencies(freq_list=[1e3, 1e6, 1e9])
print(freqs2)
# Output: Frequencies(n=3, range=[1.00e+03, 1.00e+09] Hz, explicit list)
```

---

## Constants

| Constant | Value | Description |
|----------|-------|-------------|
| `DEFAULT_FMIN` | 0 | Default minimum frequency exponent (1 Hz) |
| `DEFAULT_FMAX` | 8 | Default maximum frequency exponent (100 MHz) |
| `DEFAULT_FSTEP` | 2 | Default step exponent |
| `DEFAULT_FREQ_UNIT` | "Hz" | Default frequency unit |

---

## Usage Examples

### Example 1: Typical Impedance Calculation Range

```python
from pytlwall.frequencies import Frequencies

# Standard range for LHC impedance calculations
# 1 Hz to 10 GHz (10^0 to 10^10)
freqs = Frequencies(fmin=0, fmax=10, fstep=2)

print(f"Frequency range for LHC impedance:")
print(f"  Points: {len(freqs)}")
print(f"  Min: {freqs.freq[0]:.2e} Hz")
print(f"  Max: {freqs.freq[-1]:.2e} Hz")
print(f"  Sample: {freqs.freq[:5]}")
```

### Example 2: Custom Frequency List for Specific Modes

```python
from pytlwall.frequencies import Frequencies

# Focus on specific resonant frequencies
resonances = [
    455e3,   # 455 kHz - Mode 1
    1.2e6,   # 1.2 MHz - Mode 2
    2.8e6,   # 2.8 MHz - Mode 3
    5.5e6,   # 5.5 MHz - Mode 4
]

freqs = Frequencies(freq_list=resonances)

print(f"Analyzing {len(freqs)} resonant frequencies:")
for i, f in enumerate(freqs.freq):
    print(f"  Mode {i+1}: {f/1e6:.2f} MHz")
```

### Example 3: Comparing Different Resolutions

```python
from pytlwall.frequencies import Frequencies
import matplotlib.pyplot as plt

# Create three frequency arrays with different resolutions
freqs_low = Frequencies(fmin=3, fmax=9, fstep=1)   # Low resolution
freqs_med = Frequencies(fmin=3, fmax=9, fstep=2)   # Medium resolution
freqs_high = Frequencies(fmin=3, fmax=9, fstep=3)  # High resolution

print(f"Resolution comparison:")
print(f"  Low (fstep=1):  {len(freqs_low)} points")
print(f"  Medium (fstep=2): {len(freqs_med)} points")
print(f"  High (fstep=3): {len(freqs_high)} points")

# Visualize distribution
plt.figure(figsize=(10, 4))
plt.plot(freqs_low.freq, [1]*len(freqs_low), 'ro', label='Low', alpha=0.5)
plt.plot(freqs_med.freq, [2]*len(freqs_med), 'go', label='Medium', alpha=0.5)
plt.plot(freqs_high.freq, [3]*len(freqs_high), 'bo', label='High', alpha=0.5)
plt.xscale('log')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Resolution Level')
plt.legend()
plt.title('Frequency Point Distribution vs Resolution')
plt.grid(True, alpha=0.3)
plt.show()
```

### Example 4: Integration with pytlwall

```python
from pytlwall.frequencies import Frequencies
from pytlwall import TlWall, Beam, Layer, Chamber

# Define frequency range
freqs = Frequencies(fmin=3, fmax=9, fstep=2)

# Create beam and chamber
beam = Beam(gamma=7460.52)
layer = Layer(material='copper', thickness=0.001)
chamber = Chamber(radius=0.02, shape='circular')

# Create TlWall object with frequencies
wall = TlWall(
    beam=beam,
    chamber=chamber,
    layers=[layer],
    frequencies=freqs  # Pass frequencies object
)

# Calculate impedances at all frequency points
wall.calc_ZLong()
wall.calc_ZTrans()

print(f"Calculated impedance at {len(freqs)} frequencies")
print(f"Frequency range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
```

### Example 5: Dynamic Frequency Adjustment

```python
from pytlwall.frequencies import Frequencies

# Start with broad range
freqs = Frequencies(fmin=0, fmax=10, fstep=1)
print(f"Initial scan: {len(freqs)} points")

# Identify interesting region (e.g., 1 MHz to 100 MHz)
# Then zoom in with higher resolution
freqs.update_from_exponents(fmin=6, fmax=8, fstep=3)
print(f"Detailed scan: {len(freqs)} points")
print(f"New range: {freqs.freq[0]:.2e} to {freqs.freq[-1]:.2e} Hz")
```

### Example 6: Validation and Error Handling

```python
from pytlwall.frequencies import Frequencies
import warnings

# Example 1: Invalid frequency list
try:
    freqs = Frequencies(freq_list=[-100, 0, 1e6])  # Negative/zero frequencies
except ValueError as e:
    print(f"Error: {e}")

# Example 2: Inconsistent exponents (triggers warning)
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter("always")
    freqs = Frequencies(fmin=6, fmax=3, fstep=2)  # fmin > fmax
    if w:
        print(f"Warning: {w[0].message}")

# Example 3: Proper usage with validation
freq_list = [1e3, 5e3, 1e4, 5e4, 1e5]
freqs = Frequencies(freq_list=freq_list)
print(f"Valid frequencies: {len(freqs)} points from {freqs.fmin:.2e} to {freqs.fmax:.2e} Hz")
```

### Example 7: LHC Revolution Harmonics

```python
from pytlwall.frequencies import Frequencies

# LHC revolution frequency
f_rev = 11.245e3  # Hz

# Calculate harmonics up to 10,000th harmonic
harmonics = [f_rev * n for n in range(1, 10001)]

freqs = Frequencies(freq_list=harmonics)

print(f"LHC revolution harmonics:")
print(f"  Fundamental: {freqs.freq[0]/1e3:.3f} kHz")
print(f"  10th harmonic: {freqs.freq[9]/1e3:.1f} kHz")
print(f"  100th harmonic: {freqs.freq[99]/1e6:.3f} MHz")
print(f"  1000th harmonic: {freqs.freq[999]/1e6:.2f} MHz")
print(f"  10000th harmonic: {freqs.freq[9999]/1e6:.1f} MHz")
```

### Example 8: Points Per Decade Analysis

```python
from pytlwall.frequencies import Frequencies
import numpy as np

freqs = Frequencies(fmin=0, fmax=10, fstep=2)

# Analyze distribution
print(f"Points per decade analysis:")
for decade in range(0, 11):
    low = 10**decade
    high = 10**(decade + 1)
    count = np.sum((freqs.freq >= low) & (freqs.freq < high))
    print(f"  10^{decade:2d} - 10^{decade+1:2d} Hz: {count:4d} points")
```

### Example 9: Optimization Strategy

```python
from pytlwall.frequencies import Frequencies

print("SCENARIO: Optimizing computation time")
print("\nStep 1: Quick broad scan")
freqs_broad = Frequencies(fmin=0, fmax=10, fstep=1)  # Low resolution
print(f"  Points: {len(freqs_broad)}")
print(f"  Purpose: Identify impedance peaks")

print("\nStep 2: Detailed scan of critical region")
freqs_detail = Frequencies(fmin=6, fmax=8, fstep=3)  # High resolution
print(f"  Points: {len(freqs_detail)}")
print(f"  Purpose: Accurate characterization")

print("\nBenefit:")
total_points = len(freqs_broad) + len(freqs_detail)
all_high_res = len(Frequencies(fmin=0, fmax=10, fstep=3))
print(f"  Two-stage: {total_points} points")
print(f"  All high-res: {all_high_res} points")
print(f"  Time saved: {(1 - total_points/all_high_res)*100:.1f}%")
```

---

## Notes and Conventions

### Logarithmic Spacing Algorithm

The frequency array generation uses the following algorithm for exponent-based arrays:

For each decade `p` from 1 to `(fmax - fmin)`:
```
v1 = (1 + 10^(1-fstep)) × 10^(fmin-1+p)
v2 = 10^(fmin+p)
v3 = 10^(fmin-1+p-(fstep-1))
frequencies = arange(v1, v2 + v3, v3)
```

This creates a logarithmic distribution with finer spacing at the lower end of each decade.

### Typical Frequency Ranges

| Application | fmin | fmax | fstep | Range | Points |
|-------------|------|------|-------|-------|--------|
| LHC broad scan | 0 | 10 | 2 | 1 Hz - 10 GHz | ~5000 |
| SPS analysis | 3 | 9 | 2 | 1 kHz - 1 GHz | ~3000 |
| Cavity modes | 6 | 9 | 3 | 1 MHz - 1 GHz | ~3000 |
| Low frequency | 0 | 6 | 1 | 1 Hz - 1 MHz | ~6000 |

### Performance Considerations

- **Memory**: Each frequency point requires storage for complex impedance values
- **Computation time**: Scales linearly with number of frequency points
- **Resolution trade-off**: More points = better resolution but slower calculation
- **Recommendation**: Start with fstep=1 or 2, refine to fstep=3 if needed

### Best Practices

1. **Start broad**: Use fstep=1 or 2 for initial scans (fewer points, faster)
2. **Zoom in**: Use fstep=3 with narrower range for detailed analysis (more points, accurate)
3. **Check coverage**: Ensure frequency range covers all phenomena of interest
4. **Validate results**: Compare different resolutions to ensure convergence
5. **Document choice**: Always document frequency range and reasoning

### fstep Behavior

**Important:** The fstep parameter behavior is counterintuitive but intentional:
- `fstep=1`: **Low resolution** (fewer points per decade)
- `fstep=2`: **Medium resolution**
- `fstep=3`: **High resolution** (more points per decade)

This matches the original pytlwall algorithm. Larger fstep values give finer frequency sampling.

---

## See Also

- [beam Module](API_REFERENCE_BEAM.md) - Beam parameters that affect frequency-dependent impedance
- [layer Module](API_REFERENCE_LAYER.md) - Material properties vary with frequency
- [chamber Module](API_REFERENCE_CHAMBER.md) - Chamber geometry definitions
- [Main API Reference](API_REFERENCE.md) - Complete API documentation

---

*Last updated: December 2025*
