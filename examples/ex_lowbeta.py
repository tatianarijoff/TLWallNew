"""
Example: Low-beta configuration with image currents, compute impedances and export results.

Demonstrates:
- How to load a tlwall configuration from a .cfg file (low-beta case)
- How to compute longitudinal/transverse impedances including image currents
- How to save data to Excel
- How to produce simple log-log plots of Z(f)
"""

import os
import sys
import warnings

import numpy as np
import pandas as pd

# Add parent directory to path for non-installed package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Prefer package import
    import pytlwall
    import pytlwall.plot_util as plot
except ModuleNotFoundError:
    # Fallback: assume local package layout
    import pytlwall
    import pytlwall.plot_util as plot

warnings.filterwarnings("ignore")


def example_lowbeta_from_cfg():
    """Example: Low-beta chamber with image-current contribution."""
    print("=" * 70)
    print("Example: Low-beta Configuration from ex_lowbeta.cfg")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Read configuration and build TlWall object
    # ------------------------------------------------------------------
    cfg_path = os.path.join("examples/ex_lowbeta", "ex_lowbeta.cfg")
    print(f"Loading configuration from: {cfg_path}")
    read_cfg = pytlwall.CfgIo(cfg_path)
    wall = read_cfg.read_pytlwall()

    # Calculate impedances (including image-current terms)
    print("Calculating longitudinal and transverse impedances (with ISC)...")
    wall.calc_ZLong()
    wall.calc_ZTrans()

    # Total impedances including image currents
    ZLong_tot = wall.ZLong + wall.ZLongISC
    ZTrans_tot = wall.ZTrans + wall.ZTransISC

    # ------------------------------------------------------------------
    # Save data to Excel
    # ------------------------------------------------------------------
    outdir_data = os.path.join("examples/ex_lowbeta", "output")
    os.makedirs(outdir_data, exist_ok=True)

    data = {
        "f [Hz]": wall.f,
        "ZLong real [Ohm]": ZLong_tot.real,
        "ZLong imag [Ohm]": ZLong_tot.imag,
        "ZTrans real [Ohm/m]": ZTrans_tot.real,
        "ZTrans imag [Ohm/m]": ZTrans_tot.imag,
    }
    df = pd.DataFrame(data)

    excel_path = os.path.join(outdir_data, "output.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Saved impedance data to: {excel_path}")

    # ------------------------------------------------------------------
    # Plot impedances
    # ------------------------------------------------------------------
    outdir_img = os.path.join("examples/ex_lowbeta", "img")
    os.makedirs(outdir_img, exist_ok=True)

    print("Generating impedance plots (including ISC)...")

    # Longitudinal (with ISC)
    savename = "ZLong_total.png"
    title = "Longitudinal impedance (ZLong + ZLongISC)"
    plot.plot_Z_vs_f_simple(
        wall.f,
        ZLong_tot,
        "L",
        title,
        outdir_img,
        savename,
        xscale="log",
        yscale="log",
    )
    print(f"  Saved: {os.path.join(outdir_img, savename)}")

    # Transverse (with ISC)
    savename = "ZTrans_total.png"
    title = "Transverse impedance (ZTrans + ZTransISC)"
    plot.plot_Z_vs_f_simple(
        wall.f,
        ZTrans_tot,
        "T",
        title,
        outdir_img,
        savename,
        xscale="log",
        yscale="log",
    )
    print(f"  Saved: {os.path.join(outdir_img, savename)}")

    # ------------------------------------------------------------------
    # Minimal textual summary
    # ------------------------------------------------------------------
    print("\nSummary:")
    print(f"  Frequency points: {len(wall.f)}")
    print(f"  f range: {wall.f[0]:.2e} – {wall.f[-1]:.2e} Hz")
    print(f"  |ZLong_tot| min/max: {np.min(np.abs(ZLong_tot)):.3e} / "
          f"{np.max(np.abs(ZLong_tot)):.3e} Ohm")
    print(f"  |ZTrans_tot| min/max: {np.min(np.abs(ZTrans_tot)):.3e} / "
          f"{np.max(np.abs(ZTrans_tot)):.3e} Ohm/m")
    print()


if __name__ == "__main__":
    example_lowbeta_from_cfg()
    print("=" * 70)
    print("Low-beta example completed successfully!")
    print("=" * 70)
