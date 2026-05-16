# Time-Domain Wake — Theory

**Physical model behind `TLWallWake`**

## Authors

- **Tatiana Rijoff** — tatiana.rijoff@gmail.com
- **Carlo Zannini** — carlo.zannini@cern.ch

*Copyright: CERN*

---

[← Back to Wake Module](WAKE.md) | [Tests](testing/test_tlwall_wake.md)

---

## Table of Contents

1. [Scope](#scope)
2. [Frequency Domain vs Time Domain](#frequency-domain-vs-time-domain)
3. [The Transmission-Line Model](#the-transmission-line-model)
4. [Boundary Treatment](#boundary-treatment)
5. [Bessel Form Factors](#bessel-form-factors)
6. [The Wake Functions](#the-wake-functions)
7. [The Inductive Bypass](#the-inductive-bypass)
8. [Analytical Limits](#analytical-limits)
9. [Asymptotic Matching](#asymptotic-matching)
10. [Notation](#notation)
11. [References](#references)

---

## Scope

This document describes the physical model implemented by the
`TLWallWake` class (`pytlwall/tlwall_wake.py`). It explains how the
real-valued wake functions are obtained on a time grid, and why the
calculated wakes are expected to reproduce two well-known analytical
limits — the **thick-wall** and **thin-wall** regimes.

For the practical interface (class API, how to run the calculator) see the
companion document [WAKE.md](WAKE.md).

---

## Frequency Domain vs Time Domain

The `TlWall` class evaluates beam-coupling **impedances** `Z(f)` on a
frequency grid. The wake function `W(t)` is the time-domain description of
the same physics, formally the inverse Fourier transform of the impedance.

`TLWallWake` does **not** compute the wake by transforming a previously
computed impedance. Instead it evaluates the wake **directly** on a time
grid: the surface impedance ζ is built with time-domain material properties
and transported through the layer stack with the same transmission-line
recursion used in the frequency domain, after which the wake formulas are
applied. This avoids the numerical cost and the truncation/windowing
artefacts of a discrete inverse transform.

---

## The Transmission-Line Model

The chamber wall is modelled as a stack of layers. Each layer is a section
of transmission line with its own characteristic surface impedance, and the
multilayer wall is collapsed into a single **effective surface impedance**
`ζ_eff` by transporting ζ recursively from the outermost layer inwards.

### Surface impedance of a layer

For a conducting (`CW`) layer the intrinsic surface impedance is

```
ζ_layer = (1 + j) / (σ_PM(t) · δ_M(t))
```

where `σ_PM(t)` is the time-domain conductivity and `δ_M(t)` the
time-domain skin depth of the layer. The propagation constant inside the
layer is

```
k_prop(t) = (1 - j) / δ_M(t)
```

A vacuum (`V`) layer is treated as free space, `ζ_layer = Z₀` with
`k_prop = (2π/t)/c`. A `PEC` layer is a perfect short.

### Recursive transport

Given the effective impedance accumulated so far, `ζ_eff`, transporting it
through a layer of thickness `d` uses the standard transmission-line
transport formula

```
                    ζ_eff + j · ζ_layer · tan(k_prop · d)
ζ_eff_new = ζ_layer · -------------------------------------
                    ζ_layer + j · ζ_eff · tan(k_prop · d)
```

The recursion is initialised at the boundary (see below) and walked inward,
layer by layer, down to the innermost layer facing the beam. A `PEC` layer
encountered along the way forces `ζ_eff = 0`.

This is the **same recursion** used by `TlWall` for the impedance; the only
difference is that every quantity is evaluated with time-domain material
properties instead of frequency-domain ones.

---

## Boundary Treatment

The recursion starts from the outermost ("boundary") layer:

| Boundary type | Initial `ζ_bound` |
|---------------|-------------------|
| `PEC` | `0` (perfect short) |
| `V` (vacuum) | conductive form with σ → displacement current only |
| `CW` | conductive form with the layer's own conductivity |

For a non-PEC boundary the initial impedance is

```
ζ_bound = (1 + j) / (σ_PM(t) · δ_M_boundary(t)) · (1 - Scil_W)
```

The factor `(1 - Scil_W)` is the **cylindrical-wave correction** at the
boundary, with

```
Scil_W = 1 / I₀(k_bess · r)
```

where `I₀` is the modified Bessel function of the first kind, `r` the pipe
radius and `k_bess` the Bessel argument scale defined below. The correction
accounts for the curvature of the chamber wall; in the flat-wall limit
`Scil_W → 0`.

---

## Bessel Form Factors

The Bessel argument scale in the time domain is

```
k_bess(t) = 2π / (c · β · t)
```

The wake formulas use a **beam form factor** evaluated at a rescaled
argument,

```
F_beam(t) = I₀( k_bess · r / (γ · β) )
```

which carries the dependence on the beam's relativistic factor γ. In the
ultra-relativistic limit (γ → ∞) the argument tends to zero and
`F_beam → 1`; for finite γ it accounts for the finite transverse extent of
the beam field.

---

## The Wake Functions

From the effective surface impedance `ζ_eff` and the form factor the module
builds four wakes. `L₁` is the chamber length and `r` the pipe radius.

### Longitudinal wake (resistive part)

```
WLong(t) = L₁ · Re{ζ_eff} / ( 2π·r · √(2π) · F_beam · t )
```

### Longitudinal base wake (reactive part)

```
WLong_base(t) = L₁ · Im{ζ_eff} / ( 4π²·r · F_beam² · t )
```

`WLong` and `WLong_base` are built from the real and the imaginary part of
ζ respectively and use **different normalisations** (a `√(2π)` factor and
`F_beam` versus `F_beam²`). They are therefore distinct quantities, not two
ways of writing the same wake.

### Transverse base wake

```
WTrans_base(t) = 4 · WLong_base(t) · t · c / r²
```

### Transverse wake with inductive bypass

```
WTrans_Bypass(t) = (4·c / r²) · F_b1
```

with the bypass factor described in the next section.

---

## The Inductive Bypass

The inductive bypass models a parallel inductive path of the chamber. With

```
L_b1 = μ₀ / (4π)
Y₁   = (2π / t) · L_b1 · L₁ / Z₀
Y₂   = WLong_base(t) · t
F_b1 = (Y₁ · Y₂) / (Y₁ + Y₂)
```

`F_b1` is the parallel ("bypass") combination of `Y₁` and `Y₂`. At short
times `Y₁ ≫ Y₂`, so `F_b1 → Y₂` and `WTrans_Bypass → WTrans_base`. At long
times `Y₁` and `Y₂` are comparable, the parallel combination is genuine, and
`WTrans_Bypass` departs from `WTrans_base`. The bypass is therefore an
**intentional modification of the long-time behaviour** — it is not
expected to reproduce the thin-wall limit.

---

## Analytical Limits

Two regimes of the resistive-wall wake have closed-form expressions. They
are used as benchmarks for the full transmission-line result. `σ_eff` is
the effective conductivity (`sigma_eff`) and `d_eff` the effective
conductor thickness (`thick_eff`).

### Thick-wall regime

When the skin depth is much smaller than the conductor thickness
(`δ ≪ d`), the field does not reach the back of the conductor: the wall
behaves as if infinitely thick. This is the **short-time** / deep
skin-effect regime.

```
WLongThick(t)  = L₁ / (4π·r)  · √( Z₀ / (π·c·σ_eff) ) · t^(-3/2)
WTransThick(t) = L₁ / (π·r³)  · √( c·Z₀ / (π·σ_eff) ) · t^(-1/2)
```

### Thin-wall regime

When the skin depth is much larger than the conductor thickness
(`δ ≫ d`), the field penetrates the conductor entirely and the response is
inductive. This is the **long-time** regime.

```
WLongThin(t)  = L₁ / (2π·r) · μ₀ · d_eff / t²
WTransThin(t) = 4 · WLongThin(t) · t · c / r²
```

### Power-law slopes

| Limit | Slope on a log-log plot |
|-------|--------------------------|
| `WLongThick` | `-3/2` |
| `WTransThick` | `-1/2` |
| `WLongThin` | `-2` |
| `WTransThin` | `-1` |

---

## Asymptotic Matching

The calculated transmission-line wake interpolates between the two limits:

- **Short times** — the transport factor `tan(k_prop·d)` saturates and
  `ζ_eff → ζ_layer` (the intrinsic impedance of the conductor). The wake
  follows the **thick-wall** limit.
- **Long times** — `tan(k_prop·d) → k_prop·d` and `ζ_eff` reduces to an
  inductive form proportional to the conductor thickness. The wake follows
  the **thin-wall** limit.

This matching is the central physical check of the module: a correct
calculation must overlap `WLongThick` / `WTransThick` at short times and
`WLongThin` / `WTransThin` at long times.

### Which wake matches the limits

The matching holds for **`WLong_base`** and **`WTrans_base`**.

`WLong` is built on the **resistive** part of ζ with a `√(2π)`
normalisation: in the thick-wall regime `Re{ζ} = Im{ζ}`, so `WLong` and
`WLong_base` differ by the constant factor `√(2π) ≈ 2.507`. Consequently
`WLong` runs parallel to — but offset from — `WLongThick` and does not
overlap it. `WTrans_Bypass` includes the inductive bypass and, as explained
above, deliberately departs from the thin limit at long times. The
limit-overlap benchmark must therefore use `WLong_base` and `WTrans_base`.

---

## Notation

| Symbol | Code | Meaning |
|--------|------|---------|
| ζ_eff | `Zeta_eff` | Effective surface impedance through the stack |
| ζ_layer | — | Intrinsic surface impedance of one layer |
| ζ_bound | — | Boundary-layer surface impedance |
| σ_PM(t) | `sigmaPM_time` | Time-domain conductivity |
| δ_M(t) | `deltaM_time` | Time-domain skin depth (internal layer) |
| δ_M,bound(t) | `deltaM_time_boundary` | Time-domain skin depth (boundary) |
| k_prop(t) | `kprop_time` | In-layer propagation constant |
| k_bess(t) | `kbess_time` | Bessel argument scale, `2π/(c·β·t)` |
| F_beam | — | Beam Bessel form factor `I₀(k_bess·r/(γβ))` |
| Scil_W | — | Cylindrical-wave boundary correction |
| L₁ | `pipe_len_m` | Chamber length |
| r | `pipe_rad_m` | Pipe radius |
| σ_eff | `sigma_eff` | Effective conductivity (thick limit) |
| d_eff | `thick_eff` | Effective conductor thickness (thin limit) |
| Z₀ | `Z0` | Characteristic impedance of vacuum |
| L_b1 | — | Chamber bypass inductance per unit length, `μ₀/(4π)` |

---

## References

The transmission-line wall model and the time-domain wake formulation are
internal PyTlWall developments. The current implementation was ported from
a MATLAB prototype (`testwake_SPSwakemodel.m`) used for the SPS wake model;
the Python module reproduces that prototype's formulas and adds the
thick/thin analytical-limit benchmarks.

No external publications are referenced at this time. This section will be
updated when associated notes or papers become available.

*Internal reference: T. Rijoff, C. Zannini — CERN.*

---

*Last updated: May 2026*
