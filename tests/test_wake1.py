#!/usr/bin/env python3
"""
Deep test: TLWallWake against Thick / Thin analytical limits — single-layer chambers.

This script computes the time-domain wake functions for three chamber
configurations that share the same inner copper layer but differ in the
boundary type:

================  ==============================================
Config name        Inner layer            Boundary layer
================  ==============================================
``pec``            Copper, 2 mm           PEC
``cw``             Copper, 2 mm           Stainless steel, 1 mm
``vacuum``         Copper, 2 mm           Vacuum
================  ==============================================

For each configuration the script:

* runs :class:`pytlwall.TLWallWake` on a 1 ps … 100 ms logspace grid;
* dumps ``WLong``, ``WLongThick``, ``WLongThin`` (and the corresponding
  transverse trio ``WTrans_Bypass``, ``WTransThick``, ``WTransThin``) to
  tab-separated text files under ``output/``;
* produces two comparison plots under ``img/`` — longitudinal and
  transverse, each overlaying the full calculation with the two
  analytical limits.

The deep test is intentionally not a pass/fail unit test: it is meant
for **expert visual inspection** of where the calculator transitions
between the inductive (Thin) and resistive (Thick) regimes, and how
that transition is affected by the boundary type.

Usage
-----
Run from the repository root::

    python tests/deep_test/wake_test1/wake_test1.py
"""

from __future__ import annotations

import logging
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np

# Allow running directly: add the repo root to sys.path.
HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parents[2]
sys.path.insert(0, str(REPO_ROOT))

import pytlwall                                # noqa: E402
import pytlwall.plot_util as plot               # noqa: E402


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

CHAMBER_RADIUS_M: float = 0.022       # 22 mm
CHAMBER_LENGTH_M: float = 1.0          # 1 m
COPPER_SIGMA: float = 5.96e7           # S/m
COPPER_THICKNESS_M: float = 2.0e-3     # 2 mm
SS_SIGMA: float = 1.4e6                # S/m  (stainless steel)
SS_THICKNESS_M: float = 1.0e-3         # 1 mm

GAMMAREL: float = 7460.52              # LHC at 7 TeV

TIME_MIN_EXP: float = -12
TIME_MAX_EXP: float = -1
TIME_N_POINTS: int = 1401              # 1400 log-decades sub-steps

OUTPUT_DIR: Path = HERE / "output"
IMG_DIR: Path = HERE / "img"
LOG_DIR: Path = HERE / "logs"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class ChamberCase:
    """A single chamber configuration to test."""
    name: str                          # short id, used in filenames
    description: str                   # human-readable summary
    boundary_layer: pytlwall.Layer     # outermost layer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_beam():
    """Build a beam object using whichever Beam API is available."""
    import inspect
    params = inspect.signature(pytlwall.Beam.__init__).parameters
    if "gamma" in params:
        return pytlwall.Beam(gamma=GAMMAREL)
    if "gammarel" in params:
        return pytlwall.Beam(gammarel=GAMMAREL)
    return pytlwall.Beam(gammarel=GAMMAREL)


def _make_inner_copper() -> pytlwall.Layer:
    """Inner copper layer shared by every configuration."""
    return pytlwall.Layer(
        layer_type="CW",
        thick_m=COPPER_THICKNESS_M,
        sigmaDC=COPPER_SIGMA,
    )


def _make_cases() -> List[ChamberCase]:
    """Build the three chamber configurations under test."""
    return [
        ChamberCase(
            name="pec",
            description="Copper inner layer (2 mm, σ = 5.96e7 S/m) + PEC boundary",
            boundary_layer=pytlwall.Layer(layer_type="PEC"),
        ),
        ChamberCase(
            name="cw",
            description=(
                "Copper inner layer (2 mm, σ = 5.96e7 S/m) + stainless-steel "
                "boundary (1 mm, σ = 1.4e6 S/m)"
            ),
            boundary_layer=pytlwall.Layer(
                layer_type="CW",
                thick_m=SS_THICKNESS_M,
                sigmaDC=SS_SIGMA,
            ),
        ),
        ChamberCase(
            name="vacuum",
            description="Copper inner layer (2 mm, σ = 5.96e7 S/m) + vacuum boundary",
            boundary_layer=pytlwall.Layer(boundary=True),
        ),
    ]


def _build_wake(case: ChamberCase, beam, times) -> pytlwall.TLWallWake:
    """Build a TLWallWake for a single chamber configuration."""
    chamber = pytlwall.Chamber(
        pipe_rad_m=CHAMBER_RADIUS_M,
        pipe_len_m=CHAMBER_LENGTH_M,
        chamber_shape="CIRCULAR",
    )
    chamber.layers = [_make_inner_copper(), case.boundary_layer]
    return pytlwall.TLWallWake(chamber=chamber, beam=beam, times=times)


# ---------------------------------------------------------------------------
# I/O
# ---------------------------------------------------------------------------

def _save_wakes_txt(
    path: Path,
    times_s: np.ndarray,
    wakes: Dict[str, np.ndarray],
) -> None:
    """Write a tab-separated text file with columns ``t [s]  W1  W2  ...``."""
    path.parent.mkdir(parents=True, exist_ok=True)
    header = "\t".join(["t [s]"] + list(wakes.keys()))
    data = np.column_stack([times_s] + [wakes[k] for k in wakes])
    np.savetxt(path, data, header=header, comments="", delimiter="\t")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    """Run the deep test and produce all outputs."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Logging setup
    log_config = pytlwall.logging_util.LogConfig(
        log_dir=LOG_DIR,
        log_basename="wake_test1",
        verbosity=2,
        add_timestamp=True,
        console_output=True,
    )
    pytlwall.logging_util.setup_logging(log_config)
    logger = pytlwall.logging_util.get_logger(__name__)

    pytlwall.logging_util.log_section_header(
        logger, "DEEP TEST — wake_test1 (TLWallWake vs analytical limits)"
    )

    # Shared inputs
    beam = _make_beam()
    times = pytlwall.Times(
        tmin_exp=TIME_MIN_EXP, tmax_exp=TIME_MAX_EXP, n_points=TIME_N_POINTS
    )
    logger.info("Beam:   γ = %.4g, β = %.6f", beam.gammarel, beam.betarel)
    logger.info("Times:  %d points on [%.1e, %.1e] s",
                len(times), times.time_s[0], times.time_s[-1])

    cases = _make_cases()

    # Per-case computation and output
    for case in cases:
        logger.info("")
        pytlwall.logging_util.log_section_header(
            logger, f"Configuration: {case.name}", char="-", width=60
        )
        logger.info(case.description)

        wake = _build_wake(case, beam, times)

        wlong = wake.WLong
        wlong_thick = wake.WLongThick
        wlong_thin = wake.WLongThin
        wtrans = wake.WTrans_Bypass
        wtrans_thick = wake.WTransThick
        wtrans_thin = wake.WTransThin

        logger.info("σ_eff = %.3e S/m   d_eff = %.3e m",
                    wake.sigma_eff, wake.thick_eff)
        logger.info("WLong          range: [%.3e, %.3e]",
                    wlong.min(), wlong.max())
        logger.info("WTrans_Bypass  range: [%.3e, %.3e]",
                    wtrans.min(), wtrans.max())

        # Save raw data
        _save_wakes_txt(
            OUTPUT_DIR / f"WLong_{case.name}.txt",
            times.time_s,
            {"WLong": wlong, "WLongThick": wlong_thick, "WLongThin": wlong_thin},
        )
        _save_wakes_txt(
            OUTPUT_DIR / f"WTrans_{case.name}.txt",
            times.time_s,
            {"WTrans_Bypass": wtrans,
             "WTransThick": wtrans_thick,
             "WTransThin": wtrans_thin},
        )

        # Plots
        plot.plot_wake_vs_limits(
            t=times.time_s,
            W_calc=wlong,
            W_thick=wlong_thick,
            W_thin=wlong_thin,
            wake_type="WL",
            title=f"Longitudinal wake — {case.name} boundary",
            savedir=str(IMG_DIR),
            savename=f"WLong_{case.name}.png",
            calc_label="TLWallWake — WLong",
            thick_label="Thick-wall limit — WLongThick",
            thin_label="Thin-wall limit — WLongThin",
        )
        plot.plot_wake_vs_limits(
            t=times.time_s,
            W_calc=wtrans,
            W_thick=wtrans_thick,
            W_thin=wtrans_thin,
            wake_type="WT",
            title=f"Transverse wake — {case.name} boundary",
            savedir=str(IMG_DIR),
            savename=f"WTrans_{case.name}.png",
            calc_label="TLWallWake — WTrans_Bypass",
            thick_label="Thick-wall limit — WTransThick",
            thin_label="Thin-wall limit — WTransThin",
        )

    # Close all open figures to free memory
    plot.close_all_figures()

    logger.info("")
    pytlwall.logging_util.log_section_header(logger, "DONE")
    logger.info("Output text files: %s", OUTPUT_DIR)
    logger.info("Comparison plots:  %s", IMG_DIR)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
