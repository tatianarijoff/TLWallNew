# test_tlwall_wake.py - TLWallWake Class Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the `TLWallWake` class which performs the time-domain wake
function calculation — the time-domain counterpart of `TlWall`.

**Module tested**: `pytlwall.tlwall_wake`

**Run this test**:
```bash
python tests/test_tlwall_wake.py -v
```

See [WAKE.md](../WAKE.md) for the module documentation and
[WAKE_THEORY.md](../WAKE_THEORY.md) for the physical model.

---

## Test Classes

### TestTLWallWakeInitialization

Tests `TLWallWake` creation and input validation.

| Test Method | Description |
|-------------|-------------|
| `test_basic_initialization` | Tests creation and that inputs are stored |
| `test_custom_accuracy_factor` | Tests non-default accuracy factor is stored |
| `test_time_array_is_pushed_to_layers` | Verifies `time_s` is propagated to every layer |
| `test_empty_chamber_raises` | Verifies error for a chamber with no layers |
| `test_missing_attribute_raises` | Verifies error for a chamber lacking `pipe_rad_m` |
| `test_invalid_accuracy_factor_raises` | Verifies `accuracy_factor` must be strictly positive |

### TestTLWallWakeWakes

Tests the four computed wake functions: shape, dtype, finiteness, caching.

| Test Method | Description |
|-------------|-------------|
| `test_all_wakes_are_real_float64_arrays` | Verifies each wake is a real `float64` array of the right length |
| `test_all_wakes_are_finite` | Verifies no wake contains `NaN` or `inf` |
| `test_WLong_real_part_positive` | Verifies `WLong` (built on `Re ζ`) is non-negative |
| `test_caching_returns_same_object` | Verifies wake properties cache the result |
| `test_get_all_wakes_returns_eight_keys` | Verifies `get_all_wakes()` returns all 8 wakes |

### TestTLWallWakeAnalyticalLimits

Tests the four analytical-limit wakes against their known properties.

| Test Method | Description |
|-------------|-------------|
| `test_sigma_eff_is_max_over_cw_layers` | Verifies `sigma_eff` aggregates as max over `CW` layers |
| `test_thick_eff_is_sum_over_cw_layers` | Verifies `thick_eff` aggregates as sum over `CW` layers |
| `test_thick_limits_positive_and_finite` | Verifies `WLongThick` / `WTransThick` are positive and finite |
| `test_thin_limits_positive_and_finite` | Verifies `WLongThin` / `WTransThin` are positive and finite |
| `test_log_log_slope_thick_long` | Verifies `WLongThick` has log-log slope `-3/2` |
| `test_log_log_slope_thick_trans` | Verifies `WTransThick` has log-log slope `-1/2` |
| `test_log_log_slope_thin_long` | Verifies `WLongThin` has log-log slope `-2` |
| `test_log_log_slope_thin_trans` | Verifies `WTransThin` has log-log slope `-1` |
| `test_WTransThin_equals_4_WLongThin_t_c_over_r2` | Verifies the identity `WTransThin = 4·WLongThin·t·c/r²` |
| `test_limits_zero_when_no_cw_layer` | Verifies all four limits are zero when no `CW` layer is present |

### TestTLWallWakeBoundaryCases

Tests special boundary configurations.

| Test Method | Description |
|-------------|-------------|
| `test_single_pec_chamber_gives_zero_wakes` | Verifies a single-`PEC` chamber gives zero wakes |
| `test_vacuum_boundary_does_not_break_chain` | Verifies a vacuum boundary on top of a `CW` layer yields finite wakes |

### TestTLWallWakeStringRepresentation

Tests string output methods.

| Test Method | Description |
|-------------|-------------|
| `test_repr` | Verifies `__repr__` contains the class name and key counts |
| `test_str_uses_summary` | Verifies `__str__` produces the multi-line summary |

### TestTLWallWakePlots

Generates log-log comparison plots (full wake vs analytical limits) for
visual inspection. Each method exercises one boundary configuration and
writes two PNG files under `tests/wake/`; the assertion only checks that
the files were created.

| Test Method | Description |
|-------------|-------------|
| `test_plots_pec_boundary` | Comparison plots for the PEC-boundary chamber |
| `test_plots_cw_boundary` | Comparison plots for the CW-boundary chamber |
| `test_plots_vacuum_boundary` | Comparison plots for the vacuum-boundary chamber |

> **Note.** The comparison plots compare `WLong_base` and `WTrans_base`
> against the analytical limits — these are the wakes that physically
> overlap the thick-wall limit at short times and the thin-wall limit at
> long times. `WLong` (resistive part, different normalisation) and
> `WTrans_Bypass` (inductive bypass) are normalisation variants and are
> **not** used for the limit comparison. See
> [WAKE_THEORY.md](../WAKE_THEORY.md#asymptotic-matching).

---

## Wake Functions Tested

The `TLWallWake` class exposes eight quantities:

### Computed wakes

| Property | Description |
|----------|-------------|
| `WLong` | Longitudinal wake (resistive part of ζ) |
| `WLong_base` | Longitudinal base wake (reactive part of ζ) |
| `WTrans_base` | Transverse base wake |
| `WTrans_Bypass` | Transverse wake with inductive bypass |

### Analytical limits

| Property | Description | Log-log slope |
|----------|-------------|---------------|
| `WLongThick` | Longitudinal thick-wall limit | `-3/2` |
| `WTransThick` | Transverse thick-wall limit | `-1/2` |
| `WLongThin` | Longitudinal thin-wall limit | `-2` |
| `WTransThin` | Transverse thin-wall limit | `-1` |

---

## Key Properties Tested

```
Expected physical behaviour:
  short times  ->  calculated wake overlaps the THICK-wall limit
  long times   ->  calculated wake overlaps the THIN-wall limit

Limit aggregates (over CW layers only):
  sigma_eff = max(sigmaDC)     used by the thick limit
  thick_eff = sum(thick_m)     used by the thin limit

Analytical identity:
  WTransThin = 4 * WLongThin * t * c / r^2
```

---

## Example Usage

```python
from pytlwall import Chamber, Beam, Times, Layer, TLWallWake

# Chamber: copper inner layer + vacuum boundary
chamber = Chamber(pipe_rad_m=0.022, pipe_len_m=1.0,
                  chamber_shape="CIRCULAR")
chamber.layers = [
    Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7),
    Layer(boundary=True),
]

beam = Beam(gammarel=7460.52)
times = Times(tmin_exp=-12, tmax_exp=-1, n_points=401)

wake = TLWallWake(chamber=chamber, beam=beam, times=times)

# Computed wakes
w_long = wake.WLong_base
w_trans = wake.WTrans_base

# Analytical limits for benchmarking
w_thick = wake.WLongThick
w_thin = wake.WLongThin

# All wakes at once
all_wakes = wake.get_all_wakes()   # 8 keys
```

---

[← Back to Testing Documentation](../TESTING.md)
