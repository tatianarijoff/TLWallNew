"""
Example: Build a coated-wall chamber directly in Python (no .cfg),
compute impedances and export results.

Demonstrates:
- How to define Beam, Frequencies, Layers and Chamber in code
- How to construct a TlWall object
- How to save impedance data to Excel
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


def example_without_cfg():
    """Example: Coated-wall chamber defined directly in Python."""
    print("=" * 70)
    print("Example: Coated-Wall Chamber Defined in Code (no cfg)")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Define Beam
    # ------------------------------------------------------------------
    beam = pytlwall.Beam(betarel=0.9, test_beam_shift=0.002)

    # ------------------------------------------------------------------
    # Define Frequencies
    # ------------------------------------------------------------------
    freqs = pytlwall.Frequencies(fmin=2, fmax=8, fstep=2)

    # ------------------------------------------------------------------
    # Define Layers
    # ------------------------------------------------------------------
    layers = []

    layer0 = pytlwall.Layer(
        layer_type="CW",
        thick_m=0.1,
        muinf_Hz=0.0,
        epsr=1.0,
        sigmaDC=1.0e6,
        k_Hz=float("inf"),
        tau=0.0,
        RQ=0.0,
        boundary=False,
    )
    layers.append(layer0)

    boundary = pytlwall.Layer(layer_type="V", boundary=True)
    layers.append(boundary)

    # ------------------------------------------------------------------
    # Define Chamber characteristics
    # ------------------------------------------------------------------
    chamber = pytlwall.Chamber(
        pipe_len_m=1.0,
        pipe_rad_m=0.0184,
        chamber_shape="CIRCULAR",
        betax=1.0,
        betay=1.0,
        layers=layers,
        component_name="newCW",
    )

    # ------------------------------------------------------------------
    # Run TlWall
    # ------------------------------------------------------------------
    wall = pytlwall.TlWall(chamber, beam, freqs)
    ZLong = wall.ZLong
    ZTrans = wall.ZTrans
    ZLongSurf = wall.ZLongSurf
    ZTransSurf = wall.ZTransSurf

    # ------------------------------------------------------------------
    # Save data to Excel
    # ------------------------------------------------------------------
    outdir_data = os.path.join("examples/ex_without_cfg", "output")
    os.makedirs(outdir_data, exist_ok=True)

    data = {
        "f [Hz]": wall.f,
        "ZLong real [Ohm]": ZLong.real,
        "ZLong imag [Ohm]": ZLong.imag,
        "ZTrans real [Ohm/m]": ZTrans.real,
        "ZTrans imag [Ohm/m]": ZTrans.imag,
    }
    df = pd.DataFrame(data)

    excel_path = os.path.join(outdir_data, "output.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Saved impedance data to: {excel_path}")

    # ------------------------------------------------------------------
    # Plot impedances
    # ------------------------------------------------------------------
    outdir_img = os.path.join("examples/ex_without_cfg", "img")
    os.makedirs(outdir_img, exist_ok=True)

    print("Generating impedance plots...")

    # Longitudinal
    savename = "ZLong.png"
    title = "Longitudinal impedance"
    plot.plot_Z_vs_f_simple(
        wall.f,
        ZLong,
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
        ZTrans,
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
    print(f"  |ZLong| min/max: {np.min(np.abs(ZLong)):.3e} / "
          f"{np.max(np.abs(ZLong)):.3e} Ohm")
    print(f"  |ZTrans| min/max: {np.min(np.abs(ZTrans)):.3e} / "
          f"{np.max(np.abs(ZTrans)):.3e} Ohm/m")
    print()


if __name__ == "__main__":
    example_without_cfg()
    print("=" * 70)
    print("Example without cfg completed successfully!")
    print("=" * 70)

