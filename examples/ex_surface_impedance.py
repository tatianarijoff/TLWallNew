"""
Example: Equivalent surface impedance, compute impedances and export results.

Demonstrates:
- How to load a tlwall configuration from a .cfg file (equivalent surface-impedance case)
- How to compute longitudinal and transverse impedances and their equivalent surface impedances
- How to save data (including surface impedances) to Excel
- How to produce simple log-log plots of Z_surf(f)
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


def example_equivalent_surface_impedance():
    """Example: equivalent surface impedance from configuration file."""
    print("=" * 70)
    print("Example: Equivalent surface impedance from ex_surface_impedance.cfg")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Read configuration and build TlWall object
    # ------------------------------------------------------------------
    cfg_path = os.path.join("examples/ex_surface_impedance", "ex_surface_impedance.cfg")
    print(f"Loading configuration from: {cfg_path}")
    read_cfg = pytlwall.CfgIo(cfg_path)
    wall = read_cfg.read_pytlwall()

    # ------------------------------------------------------------------
    # Calculate longitudinal and transverse impedances
    # (and corresponding equivalent surface impedances)
    # ------------------------------------------------------------------
    print("Calculating longitudinal and transverse impedances...")
    wall.calc_ZLong()
    wall.calc_ZTrans()

    # ------------------------------------------------------------------
    # Save data to Excel
    # ------------------------------------------------------------------
    outdir_data = os.path.join("examples/ex_surface_impedance", "output")
    os.makedirs(outdir_data, exist_ok=True)

    data = {
        "f [Hz]": wall.f,
        "ZLong real [Ohm]": wall.ZLong.real,
        "ZLong imag [Ohm]": wall.ZLong.imag,
        "ZTrans real [Ohm/m]": wall.ZTrans.real,
        "ZTrans imag [Ohm/m]": wall.ZTrans.imag,
        "ZLongSurf real [Ohm]": wall.ZLongSurf.real,
        "ZLongSurf imag [Ohm]": wall.ZLongSurf.imag,
        "ZTransSurf real [Ohm/m]": wall.ZTransSurf.real,
        "ZTransSurf imag [Ohm/m]": wall.ZTransSurf.imag,
    }
    df = pd.DataFrame(data)

    excel_path = os.path.join(outdir_data, "output.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Saved impedance and surface-impedance data to: {excel_path}")

    # ------------------------------------------------------------------
    # Plot equivalent surface impedances
    # ------------------------------------------------------------------
    outdir_img = os.path.join("examples/ex_surface_impedance", "img")
    os.makedirs(outdir_img, exist_ok=True)

    print("Generating equivalent surface-impedance plots...")

    # Longitudinal equivalent surface impedance
    savename = "ZLongSurf.png"
    title = "Equivalent longitudinal surface impedance"
    plot.plot_Z_vs_f_simple(
        wall.f,
        wall.ZLongSurf,
        "S",
        title,
        outdir_img,
        savename,
        xscale="log",
        yscale="log",
    )
    print(f"  Saved: {os.path.join(outdir_img, savename)}")

    # Transverse equivalent surface impedance
    savename = "ZTransSurf.png"
    title = "Equivalent transverse surface impedance"
    plot.plot_Z_vs_f_simple(
        wall.f,
        wall.ZTransSurf,
        "S",
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
    print(
        f"  |ZLongSurf| min/max: {np.min(np.abs(wall.ZLongSurf)):.3e} / "
        f"{np.max(np.abs(wall.ZLongSurf)):.3e} Ohm"
    )
    print(
        f"  |ZTransSurf| min/max: {np.min(np.abs(wall.ZTransSurf)):.3e} / "
        f"{np.max(np.abs(wall.ZTransSurf)):.3e} Ohm/m"
    )
    print()


if __name__ == "__main__":
    example_equivalent_surface_impedance()
    print("=" * 70)
    print("Equivalent surface-impedance example completed successfully!")
    print("=" * 70)
