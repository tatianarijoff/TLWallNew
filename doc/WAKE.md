# Time-Domain Wake Module

**PyTlWall Wake Function Calculator (`TLWallWake`)**

## Authors

- **Tatiana Rijoff** — tatiana.rijoff@gmail.com
- **Carlo Zannini** — carlo.zannini@cern.ch

*Copyright: CERN*

---

[← Back to README](../README.md) | [Theory](WAKE_THEORY.md) | [Tests](testing/test_tlwall_wake.md) | [TESTING.md](TESTING.md)

---

## Table of Contents

1. [Overview](#overview)
2. [The Wake Functions](#the-wake-functions)
3. [Inputs](#inputs)
4. [Quick Start](#quick-start)
5. [Class Reference](#class-reference)
6. [Analytical Limits](#analytical-limits)
7. [Validation](#validation)
8. [Running the Calculator](#running-the-calculator)
   - [Programmatic Use](#programmatic-use-available)
   - [From the Shell](#from-the-shell-planned)
   - [With a Configuration File](#with-a-configuration-file-planned)
   - [From the Graphical Interface](#from-the-graphical-interface-planned)
9. [Troubleshooting](#troubleshooting)
10. [See Also](#see-also)

---

## Overview

`TLWallWake` is the **time-domain** counterpart of the `TlWall` impedance
calculator. While `TlWall` evaluates beam-coupling impedances on a
**frequency** grid, `TLWallWake` evaluates the real-valued **wake functions**
on a **time** grid.

The calculation transports a surface impedance ζ recursively through the
chamber's layer stack and combines the result with Bessel-function form
factors. The physical background — the transmission-line model, the
recursive transport, the Bessel form factors and the thick/thin analytical
limits — is described in the companion document
[WAKE_THEORY.md](WAKE_THEORY.md).

**Module location:** `pytlwall/tlwall_wake.py`

| Aspect | `TlWall` (impedance) | `TLWallWake` (wake) |
|--------|----------------------|---------------------|
| Domain | Frequency | Time |
| Grid input | `Frequencies` | `Times` |
| Main outputs | `ZLong`, `ZTrans`, … | `WLong`, `WLong_base`, `WTrans_base`, `WTrans_Bypass` |
| Reference checks | Wake2D / IW2D / OldTLWall | Thick-wall & Thin-wall analytical limits |

---

## The Wake Functions

`TLWallWake` exposes eight quantities — four computed wakes and four
analytical reference limits.

### Computed wakes

| Property | Description | Built from |
|----------|-------------|------------|
| `WLong` | Longitudinal wake from the resistive part of ζ | `Re{ζ_eff}` |
| `WLong_base` | Longitudinal "base" wake from the reactive part of ζ | `Im{ζ_eff}` |
| `WTrans_base` | Transverse "base" wake | `WLong_base` |
| `WTrans_Bypass` | Transverse wake including the inductive bypass | `WLong_base` + bypass |

### Analytical reference limits

| Property | Description | Power law |
|----------|-------------|-----------|
| `WLongThick` | Longitudinal thick-wall (deep skin-effect) limit | `t^(-3/2)` |
| `WTransThick` | Transverse thick-wall limit | `t^(-1/2)` |
| `WLongThin` | Longitudinal thin-wall (inductive) limit | `t^(-2)` |
| `WTransThin` | Transverse thin-wall limit | `t^(-1)` |

> **Note — which wake to compare against the limits.**
> The wakes that physically reproduce the analytical limits are
> **`WLong_base`** and **`WTrans_base`**: they overlap the *thick* limit at
> short times and the *thin* limit at long times. `WLong` (resistive part,
> different normalisation) and `WTrans_Bypass` (inductive bypass, which
> deliberately modifies the long-time behaviour) are normalisation variants
> and are **not** expected to overlap the limits. See
> [Validation](#validation) and [WAKE_THEORY.md](WAKE_THEORY.md).

---

## Inputs

`TLWallWake` is duck-typed and accepts the standard PyTlWall objects.

| Argument | Type | Must expose | Description |
|----------|------|-------------|-------------|
| `chamber` | `Chamber` | `layers`, `pipe_len_m`, `pipe_rad_m` | Chamber geometry and layer stack |
| `beam` | `Beam` | `gammarel`, `betarel` | Relativistic beam |
| `times` | `Times` | `time_s` | Time grid |
| `accuracy_factor` | `float` | — | Reserved for future use (default `0.3`) |

On construction the `time_s` array is pushed onto every layer of the
chamber — the same mechanism `TlWall` uses with `freq_Hz` — which activates
the time-domain layer properties.

---

## Quick Start

```python
from pytlwall import Chamber, Beam, Times, Layer, TLWallWake

# Chamber: 2 mm copper inner layer + vacuum boundary
chamber = Chamber(pipe_rad_m=0.022, pipe_len_m=1.0,
                  chamber_shape="CIRCULAR")
chamber.layers = [
    Layer(layer_type='CW', thick_m=2e-3, sigmaDC=5.96e7),
    Layer(boundary=True),
]

# Beam and time grid
beam = Beam(gammarel=7460.52)
times = Times(tmin_exp=-12, tmax_exp=-1, n_points=1401)

# Build the calculator
wake = TLWallWake(chamber, beam, times)

# Access the wakes (cached on first access)
w_long = wake.WLong_base
w_trans = wake.WTrans_base

# Or get everything at once
all_wakes = wake.get_all_wakes()   # dict with all 8 quantities
```

---

## Class Reference

### Constructor

```python
TLWallWake(chamber, beam, times, accuracy_factor=0.3)
```

Raises `TLWallWakeConfigurationError` if an input is missing a required
attribute, if the chamber has no layers, or if the time grid is empty.

### Properties

| Property | Returns | Description |
|----------|---------|-------------|
| `chamber`, `beam`, `times` | object | The inputs (read-only) |
| `accuracy_factor` | `float` | Accuracy selector (read/write, reserved) |
| `time_s` | `np.ndarray` | Shortcut to `times.time_s` |
| `kbess_time` | `np.ndarray` | Bessel argument scale, `2π/(c·β·t)` |
| `Zeta_eff` | `np.ndarray` (complex) | Effective surface impedance ζ transported through the stack |
| `WLong`, `WLong_base`, `WTrans_base`, `WTrans_Bypass` | `np.ndarray` (real) | Computed wakes (cached) |
| `WLongThick`, `WTransThick`, `WLongThin`, `WTransThin` | `np.ndarray` (real) | Analytical limits |
| `sigma_eff` | `float` | Effective conductivity used by the thick limit |
| `thick_eff` | `float` | Effective conductor thickness used by the thin limit |

### Methods

| Method | Description |
|--------|-------------|
| `calc_WLong()`, `calc_WLong_base()`, … | Force (re)computation of a wake |
| `calc_WLongThick()`, `calc_WLongThin()`, … | Force (re)computation of a limit |
| `get_all_wakes()` | Return all 8 wakes as a `dict` |
| `summary()` | Human-readable configuration summary |
| `__repr__`, `__str__` | String representations |

### Exceptions

| Exception | Raised when |
|-----------|-------------|
| `TLWallWakeError` | Base class for all module errors |
| `TLWallWakeConfigurationError` | The calculator is built with invalid inputs |
| `TLWallWakeCalculationError` | A wake calculation fails |

---

## Analytical Limits

The four limit wakes are closed-form references used to benchmark the full
transmission-line result. They depend only on the geometry and on two
single-number aggregates derived from the layer stack:

| Aggregate | Property | Definition | Used by |
|-----------|----------|------------|---------|
| Effective conductivity | `sigma_eff` | `max(sigmaDC)` over all `CW` layers | Thick limit |
| Effective thickness | `thick_eff` | `Σ thick_m` over all `CW` layers | Thin limit |

Layers of type `V` (vacuum) and `PEC` do not contribute to either
aggregate. When the chamber has no `CW` layer both aggregates are `0.0`
and the limit wakes degenerate to zero.

The formulas are given in [WAKE_THEORY.md](WAKE_THEORY.md#analytical-limits).

---

## Validation

The expected physical behaviour is:

- at **short times** (deep skin effect) the calculated wake overlaps the
  **thick-wall** limit;
- at **long times** (field fully penetrating a thin conductor) it overlaps
  the **thin-wall** limit.

This overlap holds for **`WLong_base`** and **`WTrans_base`**. The unit
test module `test_tlwall_wake.py` exercises this comparison and produces
log-log plots for visual inspection (see
[test_tlwall_wake.md](testing/test_tlwall_wake.md)).

---

## Running the Calculator

### Programmatic Use (available)

The programmatic interface shown in [Quick Start](#quick-start) is the
**only interface available today**. `TLWallWake` is built from `Chamber`,
`Beam` and `Times` objects and the wakes are read as properties.

The three interfaces below are **planned**. They mirror the interfaces
already provided for the impedance calculation (`run_tests_deep.py`, the
`.cfg` configuration files handled by `CfgIo`, and the graphical front-end).
They are documented here so the design is fixed in advance; the sections
will be completed when the corresponding code is merged.

### From the Shell (Planned)

> 🚧 **Planned feature — not yet implemented.**
> The commands below describe the intended interface and do not work yet.

Two equivalent entry points are planned, consistent with the rest of
PyTlWall:

```bash
# Dedicated runner script (mirrors run_tests_deep.py)
python run_wake.py [OPTIONS]

# Module execution entry point
python -m pytlwall.tlwall_wake [OPTIONS]
```

The intended options (final names to be confirmed on implementation):

| Option | Description |
|--------|-------------|
| `--config` | Path to a `.cfg` configuration file |
| `--tmin` / `--tmax` | Time-grid exponents (powers of 10) |
| `--n-points` | Number of time samples |
| `--output` | Directory for generated wake files and plots |
| `--verbosity` | Verbosity level (1=WARNING, 2=INFO, 3=DEBUG) |

This section will be expanded with concrete examples and sample output
once `run_wake.py` and the `__main__` entry point are merged.

### With a Configuration File (Planned)

> 🚧 **Planned feature — not yet implemented.**

Wake runs are planned to reuse the existing INI-style `.cfg` format read by
`CfgIo`, extended with time-domain sections. The intended additions are a
`[time_info]` section (time grid) and a `[wake_output]` section (which
wakes to export), alongside the existing `[base_info]`, `[layers_info]`,
`[layer*]`, `[boundary]` and `[beam_info]` sections already used for
impedance. The exact section and key names will be documented here once
the `CfgIo` extension is implemented.

### From the Graphical Interface (Planned)

> 🚧 **Planned feature — not yet implemented.**

A graphical front-end for wake runs is planned, mirroring the existing
impedance interface: load a configuration, choose the time grid, select the
wakes to compute, run, and inspect the resulting plots. This section will be
completed when the GUI support for the wake module is available.

---

## Troubleshooting

### `TLWallWakeConfigurationError` on construction

The `chamber`, `beam` or `times` object is missing a required attribute, the
chamber has no layers, or the time grid is empty. Check that `chamber`
exposes `layers`, `pipe_len_m` and `pipe_rad_m`, that `beam` exposes
`gammarel` and `betarel`, and that `times.time_s` is non-empty.

### All wakes are zero

A chamber whose only layer is `PEC` produces zero wakes by construction (a
perfect conductor short-circuits the boundary). Add a `CW` layer to obtain a
non-trivial result.

### Limit wakes are zero

`WLongThick`, `WTransThick`, `WLongThin` and `WTransThin` are zero when the
chamber contains no `CW` layer (`sigma_eff == 0` and `thick_eff == 0`).

### The calculated wake does not overlap the limits

Make sure you are comparing `WLong_base` / `WTrans_base` — not `WLong` /
`WTrans_Bypass` — against the analytical limits. See
[Validation](#validation).

---

## See Also

- [WAKE_THEORY.md](WAKE_THEORY.md) — Physical model and derivations
- [test_tlwall_wake.md](testing/test_tlwall_wake.md) — Wake module test suite
- [TESTING.md](TESTING.md) — Full testing documentation
- [RUN_TESTS_DEEP_README.md](RUN_TESTS_DEEP_README.md) — Impedance deep test runner (interface reference for the planned wake runner)
- [README.md](../README.md) — Main project documentation

---

*Last updated: May 2026*
