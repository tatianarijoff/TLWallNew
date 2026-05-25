#!/usr/bin/env python3
"""
Example usage of the pytlwall.TLWallWake module.

This script demonstrates how to use the TLWallWake class to compute
time-domain wake functions from a multi-layer chamber, building all
the objects directly in Python (no .cfg file required).

The TLWallWake class is the time-domain counterpart of TlWall: while
TlWall returns beam-coupling impedances on a frequency grid,
TLWallWake returns the real-valued wake functions W(t) on a time
grid, by recursively transporting a surface impedance through the
layer stack and applying the appropriate Bessel form factors.

Key deliverables of TLWallWake:
  * WLong         - full longitudinal wake (V/C)
  * WLong_base    - reactive part only (matches the analytical limits)
  * WTrans_base   - transverse wake, reactive part
  * WTrans_Bypass - full transverse wake (with inductive bypass)

Analytical reference limits (also exposed by the class):
  * WLongThick / WTransThick - thick-wall limit
  * WLongThin  / WTransThin  - thin-wall limit

These limits are derived from the reactive part of the surface
impedance, so the natural comparison is against WLong_base and
WTrans_base, NOT against the full WLong / WTrans_Bypass. The full
wakes include extra contributions (resistive and bypass terms) that
the analytical limits do not capture.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt

import pytlwall


def print_separator():
    print("\n" + "=" * 80 + "\n")


def _safe_loglog(ax, t, y, label, **kwargs):
    """Plot |y| vs t on a log-log axis, skipping zeros and negatives."""
    mask = np.abs(y) > 0
    if not np.any(mask):
        return
    ax.loglog(t[mask], np.abs(y[mask]), label=label, **kwargs)


def _save_img(fig, name):
    """Save a figure under examples/img/ (ignored by .gitignore)."""
    img_dir = os.path.join(os.path.dirname(__file__), "img")
    os.makedirs(img_dir, exist_ok=True)
    out = os.path.join(img_dir, name)
    fig.savefig(out, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Figure saved: {out}")


def _build_lhc_beam():
    """LHC 7 TeV proton beam."""
    return pytlwall.Beam(gammarel=7460.52)


def _build_chamber(layer_type_boundary, copper_thickness_m=2e-3):
    """Round 22 mm Cu pipe of length 1 m + chosen boundary type.

    Parameters
    ----------
    layer_type_boundary : str
        Either 'V' (vacuum) or 'PEC' (perfect electric conductor).
        These are the two boundary types we recommend for production
        wake calculations.
    copper_thickness_m : float
        Thickness of the inner CW layer in meters.
    """
    copper = pytlwall.Layer(
        layer_type="CW",
        thick_m=copper_thickness_m,
        sigmaDC=5.96e7,
        epsr=1.0,
        muinf_Hz=0.0,
        k_Hz=float("inf"),
        tau=0.0,
        RQ=0.0,
        boundary=False,
    )
    boundary = pytlwall.Layer(layer_type=layer_type_boundary, boundary=True)
    chamber = pytlwall.Chamber(
        pipe_len_m=1.0,
        pipe_rad_m=0.022,
        chamber_shape="CIRCULAR",
        betax=1.0,
        betay=1.0,
        layers=[copper, boundary],
        component_name=f"demo_{layer_type_boundary}",
    )
    return chamber


# ----------------------------------------------------------------------
# Example 1 - Minimal: build a wake calculator and access W(t)
# ----------------------------------------------------------------------

def example_minimal():
    """Example 1: Minimal usage with a vacuum boundary."""
    print_separator()
    print("EXAMPLE 1: Minimal usage - Cu 2 mm pipe with vacuum boundary")
    print_separator()

    beam = _build_lhc_beam()
    chamber = _build_chamber("V")
    times = pytlwall.Times()  # default: 10^-12 to 10^-1 s, 1401 log-spaced

    print(f"Chamber: round, r = {chamber.pipe_rad_m * 1000:.1f} mm, "
          f"L = {chamber.pipe_len_m:.1f} m")
    print(f"Layers:  {len(chamber.layers)} (CW + V boundary)")
    print(f"Beam:    gammarel = {beam.gammarel:.2f}")
    print(f"Times:   {len(times)} points from "
          f"{times.time_s[0]:.0e} to {times.time_s[-1]:.0e} s")

    wake = pytlwall.TLWallWake(chamber, beam, times)

    print("\nAccess the wakes as attributes:")
    print(f"  wake.WLong[:3]         = {wake.WLong[:3]}    (full)")
    print(f"  wake.WLong_base[:3]    = {wake.WLong_base[:3]}    (reactive only)")
    print(f"  wake.WTrans_Bypass[:3] = {wake.WTrans_Bypass[:3]}    (full)")
    print(f"  wake.WTrans_base[:3]   = {wake.WTrans_base[:3]}    (reactive only)")
    print(f"  wake.WLongThick[:3]    = {wake.WLongThick[:3]}    (analytical thick limit)")


# ----------------------------------------------------------------------
# Example 2 - All wake quantities exposed
# ----------------------------------------------------------------------

def example_all_quantities():
    """Example 2: Inspect all wake quantities."""
    print_separator()
    print("EXAMPLE 2: All wake quantities of TLWallWake")
    print_separator()

    beam = _build_lhc_beam()
    chamber = _build_chamber("V")
    times = pytlwall.Times()
    wake = pytlwall.TLWallWake(chamber, beam, times)

    quantities = {
        "WLong":         (wake.WLong,        "V/C        (full)"),
        "WLong_base":    (wake.WLong_base,   "V/C        (reactive part)"),
        "WTrans_base":   (wake.WTrans_base,  "V/(C*m)    (reactive part)"),
        "WTrans_Bypass": (wake.WTrans_Bypass, "V/(C*m)    (full)"),
        "WLongThick":    (wake.WLongThick,   "V/C        (analytical thick limit)"),
        "WLongThin":     (wake.WLongThin,    "V/C        (analytical thin limit)"),
        "WTransThick":   (wake.WTransThick,  "V/(C*m)    (analytical thick limit)"),
        "WTransThin":    (wake.WTransThin,   "V/(C*m)    (analytical thin limit)"),
    }

    print(f"{'Quantity':<18} {'|max|':<14} {'Unit / role'}")
    print("-" * 70)
    for name, (arr, role) in quantities.items():
        m = np.max(np.abs(arr))
        print(f"  {name:<16} {m:<14.3e} {role}")


# ----------------------------------------------------------------------
# Example 3 - Plot reactive wake vs analytical thick + thin limits
# ----------------------------------------------------------------------

def example_plot_vs_limits():
    """Example 3: Plot reactive wake vs analytical thick and thin limits."""
    print_separator()
    print("EXAMPLE 3: WLong_base, WTrans_base vs Thick & Thin limits (V boundary)")
    print_separator()

    beam = _build_lhc_beam()
    chamber = _build_chamber("V")
    times = pytlwall.Times()
    wake = pytlwall.TLWallWake(chamber, beam, times)

    t = times.time_s
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    _safe_loglog(ax1, t, wake.WLong_base, "WLong_base (numerical)", color="C0", linewidth=1.6)
    _safe_loglog(ax1, t, wake.WLongThick, "Thick-wall limit",       color="C3", linestyle="--")
    _safe_loglog(ax1, t, wake.WLongThin,  "Thin-wall limit",        color="C2", linestyle=":")
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("|W| [V/C]")
    ax1.set_title("Longitudinal reactive wake - Cu 2 mm + V boundary")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend()

    _safe_loglog(ax2, t, wake.WTrans_base, "WTrans_base (numerical)", color="C0", linewidth=1.6)
    _safe_loglog(ax2, t, wake.WTransThick, "Thick-wall limit",        color="C3", linestyle="--")
    _safe_loglog(ax2, t, wake.WTransThin,  "Thin-wall limit",         color="C2", linestyle=":")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("|W| [V/(C*m)]")
    ax2.set_title("Transverse reactive wake - Cu 2 mm + V boundary")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    _save_img(fig, "wake_base_vs_limits_V.png")

    print("\nObservation:")
    print("  The reactive base wakes (WLong_base, WTrans_base) follow the")
    print("  thick-wall limit closely in the resistive-wall regime, and")
    print("  approach the thin-wall limit only at extreme times where the")
    print("  field has fully diffused through the layer thickness.")


# ----------------------------------------------------------------------
# Example 4 - Boundary comparison: V vs PEC
# ----------------------------------------------------------------------

def example_boundary_comparison():
    """Example 4: Compare V and PEC boundary conditions (reactive part)."""
    print_separator()
    print("EXAMPLE 4: Boundary comparison V vs PEC (reactive wakes)")
    print_separator()

    beam = _build_lhc_beam()
    times = pytlwall.Times()

    wake_v = pytlwall.TLWallWake(_build_chamber("V"), beam, times)
    wake_pec = pytlwall.TLWallWake(_build_chamber("PEC"), beam, times)

    t = times.time_s
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    _safe_loglog(ax1, t, wake_v.WLong_base,   "V boundary",   color="C0", linewidth=1.6)
    _safe_loglog(ax1, t, wake_pec.WLong_base, "PEC boundary", color="C3", linewidth=1.6)
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("|WLong_base| [V/C]")
    ax1.set_title("Longitudinal reactive wake - V vs PEC")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend()

    _safe_loglog(ax2, t, wake_v.WTrans_base,   "V boundary",   color="C0", linewidth=1.6)
    _safe_loglog(ax2, t, wake_pec.WTrans_base, "PEC boundary", color="C3", linewidth=1.6)
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("|WTrans_base| [V/(C*m)]")
    ax2.set_title("Transverse reactive wake - V vs PEC")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    _save_img(fig, "wake_V_vs_PEC.png")

    print("\nObservation:")
    print("  For Cu 2 mm the wall is electromagnetically thick in most of")
    print("  the relevant time range, so V and PEC boundaries give very")
    print("  similar wakes. Differences appear only at extreme times where")
    print("  the field has fully reached the outer boundary.")


# ----------------------------------------------------------------------
# Example 5 - Effect of wall thickness on the reactive wake
# ----------------------------------------------------------------------

def example_thickness_scan():
    """Example 5: Scan the inner-layer thickness (V boundary)."""
    print_separator()
    print("EXAMPLE 5: Effect of wall thickness on the reactive wake (V boundary)")
    print_separator()

    beam = _build_lhc_beam()
    times = pytlwall.Times()
    t = times.time_s

    thicknesses_mm = [0.5, 1.0, 2.0, 5.0]
    fig, ax = plt.subplots(figsize=(8, 5))

    for thk_mm in thicknesses_mm:
        chamber = _build_chamber("V", copper_thickness_m=thk_mm * 1e-3)
        wake = pytlwall.TLWallWake(chamber, beam, times)
        _safe_loglog(ax, t, wake.WLong_base, f"{thk_mm:.1f} mm", linewidth=1.6)

    ax.set_xlabel("t [s]")
    ax.set_ylabel("|WLong_base| [V/C]")
    ax.set_title("Longitudinal reactive wake - Cu thickness scan, V boundary")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend(title="Cu thickness")
    plt.tight_layout()
    _save_img(fig, "wake_thickness_scan_V.png")

    print("\nObservation:")
    print("  Thicker walls keep the reactive wake on the thick-wall trend")
    print("  for longer; thinner walls leave that trend earlier as the")
    print("  field reaches the outer boundary sooner.")


# ----------------------------------------------------------------------
# Example 6 - Full wake (WLong, WTrans_Bypass) - no analytical comparison
# ----------------------------------------------------------------------

def example_full_wakes():
    """Example 6: Full wakes (WLong and WTrans_Bypass)."""
    print_separator()
    print("EXAMPLE 6: Full wakes WLong and WTrans_Bypass (V boundary)")
    print_separator()

    beam = _build_lhc_beam()
    chamber = _build_chamber("V")
    times = pytlwall.Times()
    wake = pytlwall.TLWallWake(chamber, beam, times)

    t = times.time_s
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    _safe_loglog(ax1, t, wake.WLong,      "WLong (full)",        color="C0", linewidth=1.6)
    _safe_loglog(ax1, t, wake.WLong_base, "WLong_base (reactive)", color="C1", linewidth=1.2)
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("|WLong| [V/C]")
    ax1.set_title("Longitudinal: full vs reactive (V boundary)")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend()

    _safe_loglog(ax2, t, wake.WTrans_Bypass, "WTrans_Bypass (full)",  color="C0", linewidth=1.6)
    _safe_loglog(ax2, t, wake.WTrans_base,   "WTrans_base (reactive)", color="C1", linewidth=1.2)
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("|WTrans| [V/(C*m)]")
    ax2.set_title("Transverse: full vs reactive (V boundary)")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    _save_img(fig, "wake_full_vs_base_V.png")

    print("\nObservation:")
    print("  The full wakes include both reactive and resistive contributions.")
    print("  The reactive part alone is what matches the analytical limits;")
    print("  the resistive part adds an extra term on top of it.")


# ----------------------------------------------------------------------
# Example 7 - Custom time grid
# ----------------------------------------------------------------------

def example_custom_time_grid():
    """Example 7: Custom time grid for a specific region of interest."""
    print_separator()
    print("EXAMPLE 7: Custom time grid (zoom on 1 ns - 10 us)")
    print_separator()

    beam = _build_lhc_beam()
    chamber = _build_chamber("V")

    # Custom log-spaced grid: 1 ns to 10 us, 401 samples.
    times = pytlwall.Times(tmin_exp=-9, tmax_exp=-5, n_points=401)
    wake = pytlwall.TLWallWake(chamber, beam, times)

    print(f"Custom grid: {len(times)} points from "
          f"{times.time_s[0]:.0e} to {times.time_s[-1]:.0e} s")
    print(f"WLong_base shape:  {wake.WLong_base.shape}")
    print(f"WTrans_base shape: {wake.WTrans_base.shape}")

    fig, ax = plt.subplots(figsize=(8, 5))
    _safe_loglog(ax, times.time_s, wake.WLong_base, "WLong_base (numerical)", color="C0", linewidth=1.6)
    _safe_loglog(ax, times.time_s, wake.WLongThick, "Thick-wall limit",       color="C3", linestyle="--")
    ax.set_xlabel("t [s]")
    ax.set_ylabel("|W| [V/C]")
    ax.set_title("Reactive wake on a custom time grid (1 ns - 10 us)")
    ax.grid(True, which="both", alpha=0.3)
    ax.legend()
    plt.tight_layout()
    _save_img(fig, "wake_custom_time_grid.png")


# ----------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------

def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print(" " * 12 + "EXAMPLES OF USAGE OF THE PYTLWALL.TLWallWake MODULE")
    print("=" * 80)

    example_minimal()
    example_all_quantities()
    example_plot_vs_limits()
    example_boundary_comparison()
    example_thickness_scan()
    example_full_wakes()
    example_custom_time_grid()

    print_separator()
    print("SUMMARY")
    print_separator()
    print("The pytlwall.TLWallWake module allows you to:")
    print("  - Compute longitudinal and transverse wake functions W(t)")
    print("  - Use the reactive base wakes (WLong_base, WTrans_base) for")
    print("    direct comparison with the analytical thick/thin limits")
    print("  - Use the full wakes (WLong, WTrans_Bypass) for practical")
    print("    beam-dynamics calculations")
    print("  - Switch between V (vacuum) and PEC (perfect conductor)")
    print("    boundary types, both physically validated")
    print("  - Build wakes from cfg files (see ex_wake.py)")
    print("    or from Python objects (this script)")
    print()
    print("For more information, see:")
    print("  - examples/ex_wake.py : cfg-based wake example")
    print("  - docs/                : full API documentation")
    print_separator()


if __name__ == "__main__":
    main()
