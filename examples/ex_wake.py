"""
Example: Compute time-domain wake functions from cfg files.

Demonstrates:
- How to load a wake-mode configuration from a .cfg file
- How to compute longitudinal/transverse wake functions
- How to save data to xlsx and produce log-log plots W(t)
- How to compare two boundary conditions:
    * V   - semi-infinite vacuum outside the resistive wall
    * PEC - perfect electric conductor outside

Two configurations are computed and saved side by side:

    examples/ex_wake_vacuum/   Cu 2 mm + V boundary
    examples/ex_wake_pec/      Cu 2 mm + PEC boundary

Both share the same beam (LHC 7 TeV, gammarel = 7460.52), the same
pipe geometry (r = 22 mm, L = 1 m), and the same time grid
(1 ps - 100 ms, 1401 log-spaced samples).

Note on the quantities plotted
------------------------------
For each configuration we plot the *base* wakes (reactive part):

    WLong_base  - reactive part of the longitudinal wake
    WTrans_base - reactive part of the transverse wake

These are the quantities that match the analytical limits Thick / Thin
in the appropriate time ranges. The full wakes ``WLong`` and
``WTrans_Bypass`` include extra contributions (resistive and bypass
terms) and are saved to xlsx for completeness but are NOT plotted
against the analytical limits, since those limits are derived only
from the reactive part.
"""

import os
import sys
import warnings

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# Add parent directory to path for non-installed package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytlwall

warnings.filterwarnings("ignore")


def _safe_loglog(ax, t, y, label, color, linestyle="-", linewidth=1.6):
    """Plot |y| vs t on a log-log axis, skipping zeros and negatives."""
    mask = np.abs(y) > 0
    if not np.any(mask):
        return
    ax.loglog(t[mask], np.abs(y[mask]),
              label=label, color=color, linestyle=linestyle, linewidth=linewidth)


def _run_one_case(case_dir, cfg_name, label):
    """Run a single wake cfg, save .xlsx and summary plots, return reactive wakes."""
    cfg_path = os.path.join(case_dir, cfg_name)
    print(f"\n{'-' * 70}")
    print(f"Case: {label}")
    print(f"  cfg: {cfg_path}")
    print(f"{'-' * 70}")

    # Read configuration and build the wake calculator.
    cfg = pytlwall.CfgIo(cfg_path)
    result = cfg.read_wall_and_wake()
    wake = result['wake']
    if wake is None:
        raise RuntimeError(
            f"CalcWake flag did not produce a TLWallWake object. "
            f"calc_flag = {result.get('calc_flag')}"
        )

    t = wake.times.time_s

    # Numerical wakes: full and reactive-only versions.
    WLong = wake.WLong                 # full longitudinal wake
    WLong_base = wake.WLong_base       # reactive part (matches Thick)
    WTrans = wake.WTrans_Bypass        # full transverse wake (with bypass)
    WTrans_base = wake.WTrans_base     # reactive part (matches Thick)

    # Analytical reference limits.
    WLong_thick = wake.WLongThick
    WLong_thin = wake.WLongThin
    WTrans_thick = wake.WTransThick
    WTrans_thin = wake.WTransThin

    # Save data to xlsx
    outdir_data = os.path.join(case_dir, "output")
    os.makedirs(outdir_data, exist_ok=True)

    data = {
        "t [s]": t,
        "WLong [V/C]": WLong,
        "WLong_base [V/C]": WLong_base,
        "WLongThick (analytical) [V/C]": WLong_thick,
        "WLongThin (analytical) [V/C]": WLong_thin,
        "WTrans_Bypass [V/(C*m)]": WTrans,
        "WTrans_base [V/(C*m)]": WTrans_base,
        "WTransThick (analytical) [V/(C*m)]": WTrans_thick,
        "WTransThin (analytical) [V/(C*m)]": WTrans_thin,
    }
    df = pd.DataFrame(data)
    excel_path = os.path.join(outdir_data, "wake.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"  Saved wake data to: {excel_path}")

    # Plot reactive wakes vs analytical limits (matches the test plots)
    outdir_img = os.path.join(case_dir, "img")
    os.makedirs(outdir_img, exist_ok=True)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    _safe_loglog(ax1, t, WLong_base,  "WLong_base (reactive)",   "C0")
    _safe_loglog(ax1, t, WLong_thick, "Thick-wall limit",        "C3", "--")
    _safe_loglog(ax1, t, WLong_thin,  "Thin-wall limit",         "C2", ":")
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("|W| [V/C]")
    ax1.set_title(f"Longitudinal wake (reactive) - {label}")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend()

    _safe_loglog(ax2, t, WTrans_base, "WTrans_base (reactive)",  "C0")
    _safe_loglog(ax2, t, WTrans_thick, "Thick-wall limit",       "C3", "--")
    _safe_loglog(ax2, t, WTrans_thin,  "Thin-wall limit",        "C2", ":")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("|W| [V/(C*m)]")
    ax2.set_title(f"Transverse wake (reactive) - {label}")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    img_path = os.path.join(outdir_img, "wake_vsThinThick.png")
    fig.savefig(img_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved wake (vs analytical limits) plot to: {img_path}")

    # Plot full wakes (no analytical comparison)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    _safe_loglog(ax1, t, WLong, "WLong (full)", "C0")
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("|WLong| [V/C]")
    ax1.set_title(f"Longitudinal wake (full) - {label}")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend()

    _safe_loglog(ax2, t, WTrans, "WTrans_Bypass (full)", "C0")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("|WTrans| [V/(C*m)]")
    ax2.set_title(f"Transverse wake (full) - {label}")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    img_path2 = os.path.join(outdir_img, "wake_full.png")
    fig.savefig(img_path2, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved full wake plot to: {img_path2}")

    # Minimal textual summary
    print(f"\n  Summary ({label}):")
    print(f"    Time points: {len(t)}")
    print(f"    t range:     {t[0]:.2e} - {t[-1]:.2e} s")
    print(
        f"    |WLong_base| min/max:  {np.min(np.abs(WLong_base)):.3e} / "
        f"{np.max(np.abs(WLong_base)):.3e} V/C"
    )
    print(
        f"    |WTrans_base| min/max: {np.min(np.abs(WTrans_base)):.3e} / "
        f"{np.max(np.abs(WTrans_base)):.3e} V/(C*m)"
    )

    return t, WLong_base, WTrans_base


def _comparison_plot(t_vac, WL_vac, WT_vac,
                     t_pec, WL_pec, WT_pec,
                     out_path):
    """Plot V vs PEC reactive wakes side by side for direct comparison."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

    _safe_loglog(ax1, t_vac, WL_vac, "V boundary",   "C0")
    _safe_loglog(ax1, t_pec, WL_pec, "PEC boundary", "C3")
    ax1.set_xlabel("t [s]")
    ax1.set_ylabel("|WLong_base| [V/C]")
    ax1.set_title("Longitudinal wake (reactive): V vs PEC")
    ax1.grid(True, which="both", alpha=0.3)
    ax1.legend()

    _safe_loglog(ax2, t_vac, WT_vac, "V boundary",   "C0")
    _safe_loglog(ax2, t_pec, WT_pec, "PEC boundary", "C3")
    ax2.set_xlabel("t [s]")
    ax2.set_ylabel("|WTrans_base| [V/(C*m)]")
    ax2.set_title("Transverse wake (reactive): V vs PEC")
    ax2.grid(True, which="both", alpha=0.3)
    ax2.legend()

    plt.tight_layout()
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    fig.savefig(out_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"\nComparison plot saved to: {out_path}")


def main():
    """Run both cfg-based wake cases and produce a comparison."""
    print("=" * 70)
    print("Example: Time-domain wake from cfg files")
    print("=" * 70)

    here = os.path.dirname(os.path.abspath(__file__))

    # Each case is run from its own directory so that any relative paths
    # in the cfg (input data files, etc.) resolve correctly.
    vac_dir = os.path.join(here, "ex_wake_vacuum")
    pec_dir = os.path.join(here, "ex_wake_pec")

    cwd_save = os.getcwd()
    try:
        os.chdir(vac_dir)
        t_vac, WL_vac, WT_vac = _run_one_case(
            vac_dir, "ex_wake_vacuum.cfg", "Cu 2 mm + V boundary"
        )
    finally:
        os.chdir(cwd_save)

    try:
        os.chdir(pec_dir)
        t_pec, WL_pec, WT_pec = _run_one_case(
            pec_dir, "ex_wake_pec.cfg", "Cu 2 mm + PEC boundary"
        )
    finally:
        os.chdir(cwd_save)

    # Direct comparison V vs PEC (on the reactive wakes)
    comparison_path = os.path.join(here, "ex_wake_vacuum", "img", "compare_vs_pec.png")
    _comparison_plot(t_vac, WL_vac, WT_vac, t_pec, WL_pec, WT_pec, comparison_path)

    print()
    print("=" * 70)
    print("Wake example completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
