"""
Example: Surface-impedance input, compute impedances and export results.

Demonstrates:
- How to load a tlwall configuration from a .cfg file (surface-impedance case)
- How to read a surface-impedance text file and apply it to a layer
- How to compute longitudinal and transverse impedances
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
    import pytlwall.io_util as io
except ModuleNotFoundError:
    # Fallback: assume local package layout
    import pytlwall
    import pytlwall.plot_util as plot
    import pytlwall.io_util as io

warnings.filterwarnings("ignore")


def example_surface_impedance_from_txt():
    """Example: surface-impedance input applied to first layer from configuration file."""
    print("=" * 70)
    print("Example: Surface-impedance input from ex_surface_impedance_input.cfg")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Read configuration and build TlWall object
    # ------------------------------------------------------------------
    cfg_path = os.path.join("examples/ex_surface_impedance_input", "ex_surface_impedance_input.cfg")
    print(f"Loading configuration from: {cfg_path}")
    read_cfg = pytlwall.CfgIo(cfg_path)
    wall = read_cfg.read_pytlwall()

    # ------------------------------------------------------------------
    # Read surface-impedance table and apply to first layer
    # ------------------------------------------------------------------
    txt_path = os.path.join("examples/ex_surface_impedance_input", "surface_impedance_input.txt")
    print(f"Reading surface-impedance table from: {txt_path}")
    new_f, new_KZ = io.read_surface_impedance_txt(txt_path, skipped_rows=1)

    print("Applying surface impedance to first chamber layer...")
    wall.chamber.layers[0].set_surf_imped(new_f, new_KZ)

    # ------------------------------------------------------------------
    # Calculate longitudinal and transverse impedances
    # ------------------------------------------------------------------
    print("Calculating longitudinal and transverse impedances...")
    wall.calc_ZLong()
    wall.calc_ZTrans()

    # ------------------------------------------------------------------
    # Save data to Excel
    # ------------------------------------------------------------------
    outdir_data = os.path.join("examples/ex_surface_impedance_input", "output")
    os.makedirs(outdir_data, exist_ok=True)

    data = {
        "f [Hz]": wall.f,
        "ZLong real [Ohm]": wall.ZLong.real,
        "ZLong imag [Ohm]": wall.ZLong.imag,
        "ZTrans real [Ohm/m]": wall.ZTrans.real,
        "ZTrans imag [Ohm/m]": wall.ZTrans.imag,
    }
    df = pd.DataFrame(data)

    excel_path = os.path.join(outdir_data, "output.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Saved impedance data to: {excel_path}")

    # ------------------------------------------------------------------
    # Plot impedances
    # ------------------------------------------------------------------
    outdir_img = os.path.join("examples/ex_surface_impedance_input", "img")
    os.makedirs(outdir_img, exist_ok=True)

    print("Generating impedance plots...")

    # Longitudinal
    savename = "ZLong.png"
    title = "Longitudinal impedance"
    plot.plot_Z_vs_f_simple(
        wall.f,
        wall.ZLong,
        "L",
        title,
        outdir_img,
        savename,
        xscale="log",
        yscale="log",
    )
    print(f"  Saved: {os.path.join(outdir_img, savename)}")

    # Transverse
    savename = "ZTrans.png"
    title = "Transverse impedance"
    plot.plot_Z_vs_f_simple(
        wall.f,
        wall.ZTrans,
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
    print(
        f"  |ZLong| min/max: {np.min(np.abs(wall.ZLong)):.3e} / "
        f"{np.max(np.abs(wall.ZLong)):.3e} Ohm"
    )
    print(
        f"  |ZTrans| min/max: {np.min(np.abs(wall.ZTrans)):.3e} / "
        f"{np.max(np.abs(wall.ZTrans)):.3e} Ohm/m"
    )
    print()


if __name__ == "__main__":
    example_surface_impedance_from_txt()
    print("=" * 70)
    print("Surface-impedance example completed successfully!")
    print("=" * 70)
