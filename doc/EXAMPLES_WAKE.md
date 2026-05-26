# tlwall_wake Module Examples

![PyTlWall Logo](logo005.png)

**Time-Domain Wake Function Calculation Engine**

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
| frequencies | [EXAMPLES_FREQUENCIES.md](EXAMPLES_FREQUENCIES.md) |
| layer | [EXAMPLES_LAYER.md](EXAMPLES_LAYER.md) |
| chamber | [EXAMPLES_CHAMBER.md](EXAMPLES_CHAMBER.md) |
| tlwall | [EXAMPLES_TLWALL.md](EXAMPLES_TLWALL.md) |
| **tlwall_wake** | *You are here* |
| multiple | [EXAMPLES_MULTIPLE.md](EXAMPLES_MULTIPLE.md) |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |

---

## Table of Contents

- [Overview](#overview)
- [Example 1: Minimal Usage](#example-1-minimal-usage)
- [Example 2: All Wake Quantities](#example-2-all-wake-quantities)
- [Example 3: Reactive Wake vs Analytical Limits](#example-3-reactive-wake-vs-analytical-limits)
- [Example 4: Boundary Comparison (V vs PEC)](#example-4-boundary-comparison-v-vs-pec)
- [Example 5: Wall Thickness Scan](#example-5-wall-thickness-scan)
- [Example 6: Full vs Reactive Wakes](#example-6-full-vs-reactive-wakes)
- [Example 7: Custom Time Grid](#example-7-custom-time-grid)
- [cfg-based Usage](#cfg-based-usage)
- [Wake Reference](#wake-reference)

---

## Overview

The `TLWallWake` class is the time-domain counterpart of `TlWall`. While
`TlWall` returns beam-coupling impedances on a frequency grid, `TLWallWake`
returns the real-valued wake functions W(t) on a time grid, by recursively
transporting a surface impedance through the layer stack and applying the
appropriate Bessel form factors.

It combines:
- Beam parameters
- Chamber geometry
- Material layers
- Time grid

```python
import pytlwall

# Setup components
times = pytlwall.Times()                       # 10^-12 to 10^-1 s, 1401 points
beam = pytlwall.Beam(gammarel=7460.52)
chamber = pytlwall.Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
copper = pytlwall.Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
boundary = pytlwall.Layer(layer_type="V", boundary=True)
chamber.layers = [copper, boundary]

# Create calculator and get wakes
wake = pytlwall.TLWallWake(chamber, beam, times)
WLong = wake.WLong          # full longitudinal wake
WLong_base = wake.WLong_base   # reactive part only
```

**Key concept - full vs reactive wakes**

`TLWallWake` exposes two flavours of each wake function:

- **Full wakes** (`WLong`, `WTrans_Bypass`): include all contributions
  (reactive + resistive + bypass). These are the quantities to use for
  beam-dynamics calculations.

- **Reactive base wakes** (`WLong_base`, `WTrans_base`): contain only the
  reactive part of the surface impedance. These are the quantities that
  match the analytical Thick / Thin limits, since those limits are derived
  from the reactive part only. The full wakes include extra contributions
  that the analytical limits do not capture.

---

## Example 1: Minimal Usage

LHC-style circular copper chamber with vacuum boundary.

```python
import pytlwall

# Setup
times = pytlwall.Times()                       # default: 10^-12 to 10^-1 s, 1401 points
beam = pytlwall.Beam(gammarel=7460.52)         # LHC 7 TeV protons

copper = pytlwall.Layer(
    layer_type="CW",
    thick_m=2e-3,
    sigmaDC=5.96e7,
    boundary=False,
)
boundary = pytlwall.Layer(layer_type="V", boundary=True)

chamber = pytlwall.Chamber(
    pipe_len_m=1.0,
    pipe_rad_m=0.022,
    chamber_shape="CIRCULAR",
    betax=1.0,
    betay=1.0,
    layers=[copper, boundary],
)

# Calculate wakes
wake = pytlwall.TLWallWake(chamber, beam, times)

print(f"Configuration:")
print(f"  Beam: LHC protons, γ = {beam.gammarel:.2f}")
print(f"  Chamber: circular, r = {chamber.pipe_rad_m*1000:.1f} mm")
print(f"  Layers: CW + V boundary")
print(f"  Times: {len(times)} points from {times.time_s[0]:.0e} to {times.time_s[-1]:.0e} s")

print(f"\nResults:")
print(f"  WLong at t = {times.time_s[0]:.0e} s:  {wake.WLong[0]:.3e} V/C")
print(f"  WLong at t = {times.time_s[-1]:.0e} s: {wake.WLong[-1]:.3e} V/C")
print(f"  WTrans_Bypass at t = {times.time_s[0]:.0e} s:  {wake.WTrans_Bypass[0]:.3e} V/(C·m)")
```

---

## Example 2: All Wake Quantities

Inspect every wake quantity exposed by `TLWallWake`.

```python
import pytlwall
import numpy as np

# Setup
times = pytlwall.Times()
beam = pytlwall.Beam(gammarel=7460.52)
copper = pytlwall.Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
boundary = pytlwall.Layer(layer_type="V", boundary=True)
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022, pipe_len_m=1.0, chamber_shape="CIRCULAR",
    betax=1.0, betay=1.0, layers=[copper, boundary],
)

wake = pytlwall.TLWallWake(chamber, beam, times)

quantities = {
    "WLong":         (wake.WLong,        "V/C        (full)"),
    "WLong_base":    (wake.WLong_base,   "V/C        (reactive part)"),
    "WTrans_base":   (wake.WTrans_base,  "V/(C·m)    (reactive part)"),
    "WTrans_Bypass": (wake.WTrans_Bypass, "V/(C·m)    (full)"),
    "WLongThick":    (wake.WLongThick,   "V/C        (analytical thick limit)"),
    "WLongThin":     (wake.WLongThin,    "V/C        (analytical thin limit)"),
    "WTransThick":   (wake.WTransThick,  "V/(C·m)    (analytical thick limit)"),
    "WTransThin":    (wake.WTransThin,   "V/(C·m)    (analytical thin limit)"),
}

print(f"{'Quantity':<18} {'|max|':<14} {'Unit / role'}")
print("-" * 70)
for name, (arr, role) in quantities.items():
    print(f"  {name:<16} {np.max(np.abs(arr)):<14.3e} {role}")
```

---

## Example 3: Reactive Wake vs Analytical Limits

Plot `WLong_base` and `WTrans_base` against the analytical Thick and Thin
limits. The numerical reactive wake follows the thick-wall limit closely
in the resistive-wall regime.

```python
import pytlwall
import matplotlib.pyplot as plt
import numpy as np

# Setup (see Example 2 for the full setup boilerplate)
times = pytlwall.Times()
beam = pytlwall.Beam(gammarel=7460.52)
copper = pytlwall.Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
boundary = pytlwall.Layer(layer_type="V", boundary=True)
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022, pipe_len_m=1.0, chamber_shape="CIRCULAR",
    betax=1.0, betay=1.0, layers=[copper, boundary],
)

wake = pytlwall.TLWallWake(chamber, beam, times)
t = times.time_s

def safe_loglog(ax, t, y, label, **kw):
    mask = np.abs(y) > 0
    if np.any(mask):
        ax.loglog(t[mask], np.abs(y[mask]), label=label, **kw)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

safe_loglog(ax1, t, wake.WLong_base, "WLong_base (numerical)", color="C0", linewidth=1.6)
safe_loglog(ax1, t, wake.WLongThick, "Thick-wall limit",       color="C3", linestyle="--")
safe_loglog(ax1, t, wake.WLongThin,  "Thin-wall limit",        color="C2", linestyle=":")
ax1.set_xlabel("t [s]"); ax1.set_ylabel("|W| [V/C]")
ax1.set_title("Longitudinal reactive wake")
ax1.grid(True, which="both", alpha=0.3); ax1.legend()

safe_loglog(ax2, t, wake.WTrans_base, "WTrans_base (numerical)", color="C0", linewidth=1.6)
safe_loglog(ax2, t, wake.WTransThick, "Thick-wall limit",        color="C3", linestyle="--")
safe_loglog(ax2, t, wake.WTransThin,  "Thin-wall limit",         color="C2", linestyle=":")
ax2.set_xlabel("t [s]"); ax2.set_ylabel("|W| [V/(C·m)]")
ax2.set_title("Transverse reactive wake")
ax2.grid(True, which="both", alpha=0.3); ax2.legend()

plt.tight_layout()
plt.savefig("wake_base_vs_limits.png", dpi=150)
```

**Notes:**
- `WLong_base` matches `WLongThick` in the regime where the wall is
  electromagnetically thick.
- At very long times, the field has fully diffused through the layer and
  the wake approaches the thin-wall behaviour.
- The full `WLong` is NOT plotted here: it differs from `WLongThick` by
  a constant factor (resistive contribution) that the analytical limit
  does not include.

---

## Example 4: Boundary Comparison (V vs PEC)

Compare two outer-boundary conditions on the reactive wakes.

```python
import pytlwall
import matplotlib.pyplot as plt
import numpy as np

times = pytlwall.Times()
beam = pytlwall.Beam(gammarel=7460.52)

def build_chamber(boundary_type):
    copper = pytlwall.Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
    boundary = pytlwall.Layer(layer_type=boundary_type, boundary=True)
    return pytlwall.Chamber(
        pipe_rad_m=0.022, pipe_len_m=1.0, chamber_shape="CIRCULAR",
        betax=1.0, betay=1.0, layers=[copper, boundary],
    )

wake_v = pytlwall.TLWallWake(build_chamber("V"), beam, times)
wake_pec = pytlwall.TLWallWake(build_chamber("PEC"), beam, times)

t = times.time_s
fig, ax = plt.subplots(figsize=(8, 5))

mask = wake_v.WLong_base > 0
ax.loglog(t[mask], wake_v.WLong_base[mask], label="V boundary", color="C0", linewidth=1.6)
mask = wake_pec.WLong_base > 0
ax.loglog(t[mask], wake_pec.WLong_base[mask], label="PEC boundary", color="C3", linewidth=1.6)

ax.set_xlabel("t [s]"); ax.set_ylabel("|WLong_base| [V/C]")
ax.set_title("Longitudinal reactive wake - V vs PEC")
ax.grid(True, which="both", alpha=0.3); ax.legend()
plt.tight_layout()
plt.savefig("wake_V_vs_PEC.png", dpi=150)
```

**Notes:**
- For Cu 2 mm the wall is electromagnetically thick in most of the
  relevant time range, so V and PEC give very similar wakes.
- Differences appear only at extreme times where the field has fully
  reached the outer boundary.
- The **CW** boundary type is still under mathematical review and is
  not advertised in the examples; use V or PEC.

---

## Example 5: Wall Thickness Scan

Effect of the inner-layer thickness on the longitudinal reactive wake.

```python
import pytlwall
import matplotlib.pyplot as plt
import numpy as np

times = pytlwall.Times()
beam = pytlwall.Beam(gammarel=7460.52)
t = times.time_s

fig, ax = plt.subplots(figsize=(8, 5))

for thk_mm in [0.5, 1.0, 2.0, 5.0]:
    copper = pytlwall.Layer(layer_type="CW", thick_m=thk_mm * 1e-3, sigmaDC=5.96e7)
    boundary = pytlwall.Layer(layer_type="V", boundary=True)
    chamber = pytlwall.Chamber(
        pipe_rad_m=0.022, pipe_len_m=1.0, chamber_shape="CIRCULAR",
        betax=1.0, betay=1.0, layers=[copper, boundary],
    )
    wake = pytlwall.TLWallWake(chamber, beam, times)
    mask = wake.WLong_base > 0
    ax.loglog(t[mask], wake.WLong_base[mask], label=f"{thk_mm:.1f} mm", linewidth=1.6)

ax.set_xlabel("t [s]"); ax.set_ylabel("|WLong_base| [V/C]")
ax.set_title("Reactive wake - Cu thickness scan, V boundary")
ax.grid(True, which="both", alpha=0.3)
ax.legend(title="Cu thickness")
plt.tight_layout()
plt.savefig("wake_thickness_scan.png", dpi=150)
```

**Notes:**
- Thicker walls keep the reactive wake on the thick-wall trend for
  longer.
- Thinner walls leave that trend earlier as the field reaches the outer
  boundary sooner.

---

## Example 6: Full vs Reactive Wakes

Visualise the difference between full and reactive wakes.

```python
import pytlwall
import matplotlib.pyplot as plt
import numpy as np

times = pytlwall.Times()
beam = pytlwall.Beam(gammarel=7460.52)
copper = pytlwall.Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
boundary = pytlwall.Layer(layer_type="V", boundary=True)
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022, pipe_len_m=1.0, chamber_shape="CIRCULAR",
    betax=1.0, betay=1.0, layers=[copper, boundary],
)
wake = pytlwall.TLWallWake(chamber, beam, times)
t = times.time_s

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

ax1.loglog(t, np.abs(wake.WLong),      label="WLong (full)",         color="C0", linewidth=1.6)
ax1.loglog(t, np.abs(wake.WLong_base), label="WLong_base (reactive)", color="C1", linewidth=1.2)
ax1.set_xlabel("t [s]"); ax1.set_ylabel("|WLong| [V/C]")
ax1.set_title("Longitudinal: full vs reactive")
ax1.grid(True, which="both", alpha=0.3); ax1.legend()

ax2.loglog(t, np.abs(wake.WTrans_Bypass), label="WTrans_Bypass (full)",  color="C0", linewidth=1.6)
ax2.loglog(t, np.abs(wake.WTrans_base),   label="WTrans_base (reactive)", color="C1", linewidth=1.2)
ax2.set_xlabel("t [s]"); ax2.set_ylabel("|WTrans| [V/(C·m)]")
ax2.set_title("Transverse: full vs reactive")
ax2.grid(True, which="both", alpha=0.3); ax2.legend()

plt.tight_layout()
plt.savefig("wake_full_vs_base.png", dpi=150)
```

**Notes:**
- Full wakes include both reactive and resistive contributions.
- The reactive part alone is what matches the analytical limits.
- The resistive part adds an extra term on top of it (visible as a
  roughly constant ratio between the two curves).

---

## Example 7: Custom Time Grid

Zoom into a specific time region.

```python
import pytlwall

beam = pytlwall.Beam(gammarel=7460.52)
copper = pytlwall.Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
boundary = pytlwall.Layer(layer_type="V", boundary=True)
chamber = pytlwall.Chamber(
    pipe_rad_m=0.022, pipe_len_m=1.0, chamber_shape="CIRCULAR",
    betax=1.0, betay=1.0, layers=[copper, boundary],
)

# Custom log-spaced grid: 1 ns to 10 us, 401 samples
times = pytlwall.Times(tmin_exp=-9, tmax_exp=-5, n_points=401)
wake = pytlwall.TLWallWake(chamber, beam, times)

print(f"Custom grid: {len(times)} points from "
      f"{times.time_s[0]:.0e} to {times.time_s[-1]:.0e} s")
print(f"WLong_base shape:  {wake.WLong_base.shape}")
print(f"WTrans_base shape: {wake.WTrans_base.shape}")
```

**Times constructor:**

```python
Times(tmin_exp=-12, tmax_exp=-1, n_points=1401)
```

Creates a log-spaced grid from `10^tmin_exp` to `10^tmax_exp` seconds.

---

## cfg-based Usage

Wake calculations can also be driven by a configuration file. The
`CalcWake` flag in the `[calc_info]` section selects the calculation
mode:

- `impedance` (default) — frequency-domain calculation only (use `TlWall`)
- `wake` — time-domain wake only (use `TLWallWake`)
- `both` — frequency-domain *and* time-domain

### Example cfg

```ini
[base_info]
component_name = my_wake_case
pipe_radius_m = 0.022
pipe_len_m = 1.0
betax = 1.0
betay = 1.0
chamber_shape = CIRCULAR

[layers_info]
nbr_layers = 1

[layer0]
type = CW
thick_m = 2e-3
muinf_Hz = 0
k_Hz = inf
sigmaDC = 5.96e7
epsr = 1.0
tau = 0.0
RQ = 0.0

[boundary]
type = V

[beam_info]
gammarel = 7460.52

[calc_info]
CalcWake = wake

[time_info]
tmin_exp = -12
tmax_exp = -1
n_points = 1401
```

### Loading the cfg

```python
import pytlwall

cfg = pytlwall.CfgIo('my_wake_case.cfg')
result = cfg.read_wall_and_wake()

# Result is a dict with keys 'calc_flag', 'wall', 'wake'
print(f"Mode: {result['calc_flag']}")
wake = result['wake']        # TLWallWake instance (or None)
wall = result['wall']        # TlWall instance (or None)

if wake is not None:
    WLong = wake.WLong
    WLong_base = wake.WLong_base
    t = wake.times.time_s
```

A complete cfg-based example is available at `examples/ex_wake.py`,
which runs two cases (Cu 2 mm + V boundary, Cu 2 mm + PEC boundary)
and produces side-by-side plots.

---

## Wake Reference

### Wake Functions

| Attribute | Unit | Description |
|-----------|------|-------------|
| `WLong` | V/C | Full longitudinal wake |
| `WLong_base` | V/C | Reactive part of longitudinal wake |
| `WTrans_Bypass` | V/(C·m) | Full transverse wake (with inductive bypass) |
| `WTrans_base` | V/(C·m) | Reactive part of transverse wake |

### Analytical Limits

| Attribute | Unit | Description |
|-----------|------|-------------|
| `WLongThick` | V/C | Thick-wall analytical longitudinal limit |
| `WLongThin` | V/C | Thin-wall analytical longitudinal limit |
| `WTransThick` | V/(C·m) | Thick-wall analytical transverse limit |
| `WTransThin` | V/(C·m) | Thin-wall analytical transverse limit |

The analytical limits are derived from the reactive part of the surface
impedance only. The natural comparison is therefore:

- `WLong_base` ↔ `WLongThick` / `WLongThin`
- `WTrans_base` ↔ `WTransThick` / `WTransThin`

### Additional Attributes

| Attribute | Description |
|-----------|-------------|
| `times` | The `Times` object used (access seconds via `times.time_s`) |
| `chamber` | The `Chamber` object |
| `beam` | The `Beam` object |
| `accuracy_factor` | Numerical accuracy parameter (default 0.3) |
| `sigma_eff` | Effective conductivity |
| `thick_eff` | Effective thickness |

### Constructor

```python
TLWallWake(chamber, beam, times, accuracy_factor=0.3)
```

**Arguments:**
- `chamber`: a `Chamber` instance with at least one CW layer and one
  boundary layer (V or PEC are the validated boundary types)
- `beam`: a `Beam` instance
- `times`: a `Times` instance defining the time grid
- `accuracy_factor`: numerical accuracy parameter; smaller values
  improve accuracy at the cost of speed

### Recommended Boundary Types

Only **V** (semi-infinite vacuum) and **PEC** (perfect electric
conductor) boundaries are recommended for production use:

- **V**: vacuum outside the resistive wall, semi-infinite extent
- **PEC**: perfect mirror outside, acts as a perfect reflector

The **CW** boundary type is still under mathematical review and is
not advertised in the examples.

---

## Complete Workflow Example

```python
import pytlwall
import numpy as np
import matplotlib.pyplot as plt

# 1. Setup time grid
times = pytlwall.Times()                       # 10^-12 to 10^-1 s

# 2. Setup beam
beam = pytlwall.Beam(gammarel=7460.52)         # LHC 7 TeV

# 3. Setup layers
copper = pytlwall.Layer(
    layer_type="CW",
    thick_m=2e-3,
    sigmaDC=5.96e7,
)
boundary = pytlwall.Layer(layer_type="V", boundary=True)

# 4. Setup chamber
chamber = pytlwall.Chamber(
    pipe_len_m=1.0,
    pipe_rad_m=0.022,
    chamber_shape="CIRCULAR",
    betax=1.0,
    betay=1.0,
    layers=[copper, boundary],
)

# 5. Create wake calculator
wake = pytlwall.TLWallWake(chamber, beam, times)

# 6. Get wakes
WLong = wake.WLong                # full
WLong_base = wake.WLong_base      # reactive only (matches Thick limit)
WTrans = wake.WTrans_Bypass       # full
WTrans_base = wake.WTrans_base    # reactive only

# 7. Analyse results
t = times.time_s
idx_peak = np.argmax(np.abs(WLong))
print(f"Peak |WLong|: {abs(WLong[idx_peak]):.3e} V/C "
      f"at t = {t[idx_peak]:.2e} s")

# 8. Export or plot...
```

---

## See Also

- [API Reference - TLWallWake](API_REFERENCE_TLWALL_WAKE.md) - Complete API documentation
- [Examples Main Page](EXAMPLES.md) - All module examples
- [tlwall Examples](EXAMPLES_TLWALL.md) - Frequency-domain counterpart

---

**[◀ Back to Examples](EXAMPLES.md)** | **[◀ Previous: tlwall](EXAMPLES_TLWALL.md)** | **[Next: multiple ▶](EXAMPLES_MULTIPLE.md)**
