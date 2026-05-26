# PyTlWall Examples

![PyTlWall Logo](logo005.png)

**Comprehensive Examples for PyTlWall Modules**

## Authors

- **Tatiana Rijoff** - tatiana.rijoff@gmail.com
- **Carlo Zannini** - carlo.zannini@cern.ch

*Copyright: CERN*

---

## Table of Contents

- [Quick Start](#quick-start)
- [Module Examples](#module-examples)
- [Complete Workflows](#complete-workflows)
- [Configuration Files](#configuration-files)
- [Running the Examples](#running-the-examples)

---

## Quick Start

### Minimal Impedance Calculation

```python
from pytlwall import Beam, Frequencies, Layer, Chamber, TlWall

# 1. Define frequency range (1 kHz to 1 GHz)
freqs = Frequencies(fmin=3, fmax=9, fstep=2)

# 2. Define beam (LHC 7 TeV protons)
beam = Beam(gammarel=7460.52)

# 3. Define chamber
chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')

# 4. Define material layer
copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
chamber.layers = [copper]

# 5. Calculate impedances
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.ZLong
ZTrans = wall.ZTrans

print(f"Max |ZLong|: {abs(ZLong).max():.3e} Ω")
print(f"Max |ZTrans|: {abs(ZTrans).max():.3e} Ω/m")
```

### Minimal Wake Calculation

```python
from pytlwall import Beam, Times, Layer, Chamber, TLWallWake

# 1. Define time grid (1 ps to 100 ms, 1401 log-spaced points)
times = Times()

# 2. Define beam
beam = Beam(gammarel=7460.52)

# 3. Define layers and chamber
copper = Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
boundary = Layer(layer_type="V", boundary=True)
chamber = Chamber(
    pipe_rad_m=0.022, pipe_len_m=1.0, chamber_shape="CIRCULAR",
    betax=1.0, betay=1.0, layers=[copper, boundary],
)

# 4. Calculate wakes
wake = TLWallWake(chamber, beam, times)
WLong = wake.WLong              # full longitudinal wake (V/C)
WLong_base = wake.WLong_base    # reactive part only
```

### Using Configuration File

```python
from pytlwall import CfgIo

cfg = CfgIo('config.cfg')
wall = cfg.read_pytlwall()
ZLong = wall.calc_ZLong()
ZTrans = wall.calc_ZTrans()
```

---

## Module Examples

### Beam Module

**Purpose:** Handle particle beam parameters with relativistic calculations.

| Example | Description |
|---------|-------------|
| LHC protons | 7 TeV beam with γ = 7460 |
| Electrons | Different mass, same energy |
| Parameter conversion | γ ↔ β ↔ E ↔ p |
| Error handling | Validation examples |

**Quick Example:**
```python
from pytlwall import Beam

# LHC 7 TeV protons
beam = Beam(gammarel=7460.52)
print(f"β = {beam.betarel:.10f}")
print(f"E_kin = {beam.Ekin_MeV/1e6:.1f} TeV")
```

**[→ Full Beam Examples](EXAMPLES_BEAM.md)**

---

### Frequencies Module

**Purpose:** Manage frequency arrays for impedance calculations.

| Example | Description |
|---------|-------------|
| Logarithmic array | Standard 10^fmin to 10^fmax |
| Explicit list | Specific resonant frequencies |
| Resolution | fstep comparison |
| Dynamic update | Zoom into regions |

**Quick Example:**
```python
from pytlwall import Frequencies

# 1 kHz to 1 GHz, medium resolution
freqs = Frequencies(fmin=3, fmax=9, fstep=2)
print(f"{len(freqs)} frequency points")
```

**Note:** Larger `fstep` = MORE points (higher resolution)

**[→ Full Frequencies Examples](EXAMPLES_FREQUENCIES.md)**

---

### Layer Module

**Purpose:** Define material layers with electromagnetic properties.

| Example | Description |
|---------|-------------|
| Copper | Standard RF material |
| Stainless steel | With surface roughness |
| Vacuum boundary | Outer boundary |
| Multi-layer | Coating on substrate |

**Quick Example:**
```python
from pytlwall import Layer
import numpy as np

freq = np.logspace(3, 9, 100)
copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freq)
```

**Common Conductivities:**
- Copper: 5.96×10⁷ S/m
- Aluminum: 3.77×10⁷ S/m
- Stainless Steel: 1.45×10⁶ S/m

**[→ Full Layer Examples](EXAMPLES_LAYER.md)**

---

### Chamber Module

**Purpose:** Define vacuum chamber geometries and Yokoya factors.

| Example | Description |
|---------|-------------|
| Circular | Simple cylindrical chamber |
| Elliptical | Flat beam chambers |
| Rectangular | Kickers, septa |
| Yokoya factors | Geometric corrections |

**Quick Example:**
```python
from pytlwall import Chamber

# Elliptical chamber
chamber = Chamber(
    pipe_hor_m=0.030,
    pipe_ver_m=0.020,
    chamber_shape='ELLIPTICAL'
)
print(f"Yokoya q = {chamber.yokoya_q:.4f}")
```

**[→ Full Chamber Examples](EXAMPLES_CHAMBER.md)**

---

### TlWall Module

**Purpose:** Main impedance calculation engine (frequency domain).

| Example | Description |
|---------|-------------|
| Basic calculation | ZLong, ZTrans |
| Yokoya corrections | Non-circular chambers |
| Multi-layer | Coated structures |
| Space charge | Low energy effects |
| All impedances | Complete calculation |

**Quick Example:**
```python
from pytlwall import TlWall

wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
all_Z = wall.get_all_impedances()
```

**Available Impedances:**
- `ZLong`, `ZTrans` (primary)
- `ZDipX`, `ZDipY` (dipolar)
- `ZQuadX`, `ZQuadY` (quadrupolar)
- `ZLongDSC`, `ZTransDSC` (direct space charge)
- `ZLongISC`, `ZTransISC` (indirect space charge)

**[→ Full TlWall Examples](EXAMPLES_TLWALL.md)**

---

### TLWallWake Module

**Purpose:** Main wake calculation engine (time domain).

| Example | Description |
|---------|-------------|
| Minimal usage | Cu pipe + V boundary |
| All wake quantities | Full and reactive wakes |
| Reactive vs analytical limits | Thick / Thin reference |
| Boundary comparison | V vs PEC |
| Wall thickness scan | Effect of layer thickness |
| Full vs reactive | Resistive contribution |
| Custom time grid | Zoom into a region |

**Quick Example:**
```python
from pytlwall import TLWallWake, Times

times = Times()  # 10^-12 to 10^-1 s, 1401 points
wake = TLWallWake(chamber=chamber, beam=beam, times=times)

# Full wakes (use for beam dynamics)
WLong = wake.WLong              # V/C
WTrans = wake.WTrans_Bypass     # V/(C·m)

# Reactive base wakes (match the analytical limits)
WLong_base = wake.WLong_base
WTrans_base = wake.WTrans_base

# Analytical references
WLong_thick = wake.WLongThick   # thick-wall limit
WLong_thin = wake.WLongThin     # thin-wall limit
```

**Wake Quantities:**
- Full: `WLong`, `WTrans_Bypass`
- Reactive part only: `WLong_base`, `WTrans_base`
- Analytical limits: `WLongThick/Thin`, `WTransThick/Thin`

**[→ Full TLWallWake Examples](EXAMPLES_WAKE.md)**

---

### MultipleChamber Module

**Purpose:** Lattice-level impedance calculations.

| Example | Description |
|---------|-------------|
| Basic usage | Process entire lattice |
| Output structure | Per-element and total |
| Custom mapping | Aperture to cfg |
| GUI integration | Load Accelerator |

**Quick Example:**
```python
from pytlwall import MultipleChamber

mc = MultipleChamber(
    apertype_file="apertype2.txt",
    geom_file="b_L_betax_betay.txt",
    input_dir="./input/",
    out_dir="./output/"
)
mc.run()
```

**[→ Full MultipleChamber Examples](EXAMPLES_MULTIPLE.md)**

---

### Logging Module

**Purpose:** Centralized logging for calculations.

| Example | Description |
|---------|-------------|
| Quick setup | Simple logging start |
| Configuration | Detailed settings |
| Section headers | Organized output |
| File-only | Silent batch processing |

**Quick Example:**
```python
from pytlwall import logging_util

log_path, logger = logging_util.quick_setup(
    log_dir="./logs/",
    verbosity=2
)
logger.info("Starting calculation...")
```

**[→ Full Logging Examples](EXAMPLES_LOGGING.md)**

---

## Complete Workflows

### LHC-style Chamber Analysis

```python
from pytlwall import Beam, Frequencies, Layer, Chamber, TlWall
import numpy as np

# Setup
freqs = Frequencies(fmin=0, fmax=10, fstep=2)
beam = Beam(gammarel=7460.52)
chamber = Chamber(
    pipe_rad_m=0.022,
    pipe_len_m=14.3,  # Dipole length
    chamber_shape='CIRCULAR',
    betax=180.0,
    betay=180.0
)

# Multi-layer beam screen
copper = Layer(thick_m=50e-6, sigmaDC=5.96e7, freq_Hz=freqs.freq)
steel = Layer(thick_m=1e-3, sigmaDC=1.45e6, freq_Hz=freqs.freq)
chamber.layers = [copper, steel]

# Calculate
wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
ZLong = wall.ZLong
ZTrans = wall.ZTrans

# Find peak
idx_peak = np.argmax(np.abs(ZLong))
print(f"Peak |ZLong| = {abs(ZLong[idx_peak]):.3e} Ω at {freqs.freq[idx_peak]:.2e} Hz")
```

### Batch Processing Multiple Configurations

```python
from pytlwall import CfgIo
import glob

results = {}
for cfg_file in glob.glob("configs/*.cfg"):
    cfg = CfgIo(cfg_file)
    wall = cfg.read_pytlwall()
    
    ZLong = wall.calc_ZLong()
    results[cfg_file] = {
        'max_ZLong': abs(ZLong).max(),
        'n_freq': len(wall.freq)
    }

for name, data in results.items():
    print(f"{name}: max |ZLong| = {data['max_ZLong']:.3e} Ω")
```

---

## Configuration Files

### Basic Configuration

```ini
[base_info]
component_name = my_chamber
pipe_radius_m = 0.022
pipe_len_m = 1.0
chamber_shape = CIRCULAR
betax = 100.0
betay = 100.0

[layers_info]
nbr_layers = 1

[layer0]
type = CW
thick_m = 0.001
sigmaDC = 5.96e7
muinf_Hz = 0
k_Hz = inf
epsr = 1
tau = 0
RQ = 0

[boundary]
type = PEC

[frequency_info]
fmin = 1e3
fmax = 1e9
fstep = 10

[beam_info]
gammarel = 7460.52
```

### Wake-mode Configuration

To run a time-domain wake calculation instead of an impedance one, replace
the `[frequency_info]` section with a `[time_info]` section and set the
`CalcWake` flag:

```ini
[calc_info]
CalcWake = wake

[time_info]
tmin_exp = -12
tmax_exp = -1
n_points = 1401
```

Then load with `CfgIo.read_wall_and_wake()`, which returns a dict with
keys `'calc_flag'`, `'wall'`, and `'wake'`.

### Supported Chamber Shapes

| Shape | Aliases | Parameters |
|-------|---------|------------|
| CIRCULAR | ROUND | pipe_radius_m |
| ELLIPTICAL | ELLIPTIC | pipe_hor_m, pipe_ver_m |
| RECTANGULAR | RECT, RECTANGLE | pipe_hor_m, pipe_ver_m |

---

## Running the Examples

Each example module can be run directly from the repository root:

```bash
# Impedance examples
python examples/example_beam_usage.py
python examples/example_frequencies_usage.py
python examples/example_layer_usage.py
python examples/example_chamber_usage.py
python examples/example_tlwall_usage.py

# Wake examples (time-domain)
python examples/example_wake_usage.py
python examples/ex_wake.py

# Lattice-level impedance
python examples/example_multiple_chamber_usage.py

# Logging
python examples/example_logging_usage.py
```

Each script is self-contained: it prints to stdout, saves any generated
files under `examples/<case>/output/` and `examples/<case>/img/`, and
exits cleanly. Output directories are auto-created and ignored by git.

---

## See Also

- [API Reference](API_REFERENCE.md) - Complete API documentation
- [Installation Guide](INSTALLATION.md) - Setup instructions
- [README](README.md) - Project overview

---

*Last updated: May 2026*
