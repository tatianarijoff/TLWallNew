#!/usr/bin/env python3
"""
CompareWake2D Test Runner for PyTLWall

PURPOSE:
--------
This script generates output files for MANUAL ANALYSIS of impedance
calculations. It compares PyTLWall results with Wake2D and/or OldTLWall
references and creates text files, Excel comparisons and plots.

Renamed from run_tests_deep.py and moved under tests/ so it sits next to
run_tests_wake.py and run_tests_base.py. The directory it scans was also
renamed from tests/deep_test/ to tests/compareWake2D/.

Automatic validation is NOT performed. Percentage differences can be
misleading for very small values. The files generated are meant for
EXPERT ANALYSIS.

Automatically discovers and runs cases in tests/compareWake2D/
subdirectories. Each case directory should contain:
- A .cfg configuration file
- Optionally a Wake2D/ directory with reference data
- Optionally an OldTLWall/ directory with legacy reference data
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass

# Allow imports when running from tests/ or repo root
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import pytlwall
from pytlwall import logging_util


# ============================================================================
# CONFIGURATION
# ============================================================================

class CompareW2DConfig:
    """Configuration for compareWake2D deep test execution."""

    # Base directory
    BASE_DIR: Path = Path("tests/compareWake2D")

    # Subdirectories to test (None = all subdirectories)
    TEST_SUBDIRS: Optional[List[str]] = None

    # Config file pattern (None = first .cfg found)
    CFG_PATTERN: Optional[str] = None

    # Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)
    VERBOSITY: int = 2

    # Output subdirectories
    OUTPUT_SUBDIR: str = "output"
    IMG_SUBDIR: str = "img"
    LOGS_SUBDIR: str = "logs"

    # Reference data directories
    REFERENCE_SUBDIR: str = "Wake2D"
    REFERENCE_SUBDIR2: str = "OldTLWall"

    # File naming patterns
    OUTPUT_PREFIX: str = ""
    COMPARISON_PREFIX: str = "NewTLWallvsWake2D"
    COMPARISON_PREFIX2: str = "NewTLWallvsOld"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ImpedanceType:
    """Definition of an impedance type to compute and compare."""
    name: str
    label: str
    unit: str
    compute_method: str
    result_attr: str
    wake2d_file: str
    output_file: str
    plot_file: str
    excel_file: str


# -- Longitudinal -----------------------------------------------------------
ZLongTotal = ImpedanceType(
    name="ZLongTotal", label="Longitudinal (with ISC)", unit="Ω",
    compute_method="calc_ZLong", result_attr="ZLongTotal",
    wake2d_file="ZlongW*.dat",
    output_file="ZLongTotal.txt", plot_file="ZLongTotal.png",
    excel_file="LongTotal.xlsx",
)
ZLong = ImpedanceType(
    name="ZLong", label="Longitudinal (no ISC)", unit="Ω",
    compute_method="calc_ZLong", result_attr="ZLong",
    wake2d_file="ZlongW*.dat",
    output_file="ZLong.txt", plot_file="ZLong.png",
    excel_file="Long.xlsx",
)

# -- Transverse (generic) ---------------------------------------------------
ZTransTotal = ImpedanceType(
    name="ZTransTotal", label="Transverse (with ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZTransTotal",
    wake2d_file="ZtransW*.dat",
    output_file="ZTransTotal.txt", plot_file="ZTransTotal.png",
    excel_file="TransTotal.xlsx",
)
ZTrans = ImpedanceType(
    name="ZTrans", label="Transverse (no ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZTrans",
    wake2d_file="ZtransW*.dat",
    output_file="ZTrans.txt", plot_file="ZTrans.png",
    excel_file="Trans.xlsx",
)

# -- Dipolar X / Y ----------------------------------------------------------
ZDipXTotal = ImpedanceType(
    name="ZDipXTotal", label="Dipolar X (with ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZDipXTotal",
    output_file="ZDipXTotal.txt", plot_file="ZDipXTotal.png",
    excel_file="DipXTotal.xlsx", wake2d_file="ZxdipW*.dat",
)
ZDipX = ImpedanceType(
    name="ZDipX", label="Dipolar X (no ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZDipX",
    output_file="ZDipX.txt", plot_file="ZDipX.png",
    excel_file="DipX.xlsx", wake2d_file="ZxdipW*.dat",
)
ZDipYTotal = ImpedanceType(
    name="ZDipYTotal", label="Dipolar Y (with ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZDipYTotal",
    output_file="ZDipYTotal.txt", plot_file="ZDipYTotal.png",
    excel_file="DipYTotal.xlsx", wake2d_file="ZydipW*.dat",
)
ZDipY = ImpedanceType(
    name="ZDipY", label="Dipolar Y (no ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZDipY",
    output_file="ZDipY.txt", plot_file="ZDipY.png",
    excel_file="DipY.xlsx", wake2d_file="ZydipW*.dat",
)

# -- Quadrupolar X / Y ------------------------------------------------------
ZQuadXTotal = ImpedanceType(
    name="ZQuadXTotal", label="Quadrupolar X (with ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZQuadXTotal",
    output_file="ZQuadXTotal.txt", plot_file="ZQuadXTotal.png",
    excel_file="QuadXTotal.xlsx", wake2d_file="ZxquadW*.dat",
)
ZQuadX = ImpedanceType(
    name="ZQuadX", label="Quadrupolar X (no ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZQuadX",
    output_file="ZQuadX.txt", plot_file="ZQuadX.png",
    excel_file="QuadX.xlsx", wake2d_file="ZxquadW*.dat",
)
ZQuadYTotal = ImpedanceType(
    name="ZQuadYTotal", label="Quadrupolar Y (with ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZQuadYTotal",
    output_file="ZQuadYTotal.txt", plot_file="ZQuadYTotal.png",
    excel_file="QuadYTotal.xlsx", wake2d_file="ZyquadW*.dat",
)
ZQuadY = ImpedanceType(
    name="ZQuadY", label="Quadrupolar Y (no ISC)", unit="Ω/m",
    compute_method="calc_ZTrans", result_attr="ZQuadY",
    output_file="ZQuadY.txt", plot_file="ZQuadY.png",
    excel_file="QuadY.xlsx", wake2d_file="ZyquadW*.dat",
)

# Grouping
IMPEDANCE_PAIRS = {
    "Longitudinal": (ZLongTotal, ZLong),
    "Transverse": (ZTransTotal, ZTrans),
    "DipolarX": (ZDipXTotal, ZDipX),
    "DipolarY": (ZDipYTotal, ZDipY),
    "QuadrupolarX": (ZQuadXTotal, ZQuadX),
    "QuadrupolarY": (ZQuadYTotal, ZQuadY),
}

IMPEDANCE_TYPES = [
    ZLongTotal, ZLong,
    ZTransTotal, ZTrans,
    ZDipXTotal, ZDipX,
    ZDipYTotal, ZDipY,
    ZQuadXTotal, ZQuadX,
    ZQuadYTotal, ZQuadY,
]

CORE_IMPEDANCE_TYPES = [ZLongTotal, ZLong, ZTransTotal, ZTrans]

SEPARATE_DIPQUAD_TYPES = [
    ZDipXTotal, ZDipX, ZDipYTotal, ZDipY,
    ZQuadXTotal, ZQuadX, ZQuadYTotal, ZQuadY,
]


def get_impedance_types_for_test(wake2d_dir: Path) -> List[ImpedanceType]:
    """Determine which impedance types to compute based on Wake2D files present."""
    result = list(CORE_IMPEDANCE_TYPES)

    if not wake2d_dir.exists():
        return CORE_IMPEDANCE_TYPES + SEPARATE_DIPQUAD_TYPES

    has_xdip = len(list(wake2d_dir.glob("Zxdip*.dat"))) > 0
    has_ydip = len(list(wake2d_dir.glob("Zydip*.dat"))) > 0
    has_xquad = len(list(wake2d_dir.glob("Zxquad*.dat"))) > 0
    has_yquad = len(list(wake2d_dir.glob("Zyquad*.dat"))) > 0

    if has_xdip:
        result.append(ZDipXTotal); result.append(ZDipX)
    if has_ydip:
        result.append(ZDipYTotal); result.append(ZDipY)
    if has_xquad:
        result.append(ZQuadXTotal); result.append(ZQuadX)
    if has_yquad:
        result.append(ZQuadYTotal); result.append(ZQuadY)

    if not (has_xdip or has_ydip or has_xquad or has_yquad):
        result.extend(SEPARATE_DIPQUAD_TYPES)

    return result


SPACE_CHARGE_TYPES = [
    ImpedanceType(
        name="ZLongDSC", label="Longitudinal Direct Space Charge", unit="Ω",
        compute_method="calc_ZLongDSC", result_attr="ZLongDSC",
        wake2d_file=None, output_file="ZLongDSC.txt",
        plot_file=None, excel_file=None,
    ),
    ImpedanceType(
        name="ZLongISC", label="Longitudinal Indirect Space Charge", unit="Ω",
        compute_method="calc_ZLongISC", result_attr="ZLongISC",
        wake2d_file=None, output_file="ZLongISC.txt",
        plot_file=None, excel_file=None,
    ),
    ImpedanceType(
        name="ZTransDSC", label="Transverse Direct Space Charge", unit="Ω/m",
        compute_method="calc_ZTransDSC", result_attr="ZTransDSC",
        wake2d_file=None, output_file="ZTransDSC.txt",
        plot_file=None, excel_file=None,
    ),
    ImpedanceType(
        name="ZTransISC", label="Transverse Indirect Space Charge", unit="Ω/m",
        compute_method="calc_ZTransISC", result_attr="ZTransISC",
        wake2d_file=None, output_file="ZTransISC.txt",
        plot_file=None, excel_file=None,
    ),
    ImpedanceType(
        name="ZDipDSC", label="Dipolar Direct Space Charge", unit="Ω/m",
        compute_method="calc_ZTransDSC", result_attr="ZDipDSC",
        wake2d_file=None, output_file="ZDipDSC.txt",
        plot_file=None, excel_file=None,
    ),
    ImpedanceType(
        name="ZDipISC", label="Dipolar Indirect Space Charge", unit="Ω/m",
        compute_method="calc_ZTransISC", result_attr="ZDipISC",
        wake2d_file=None, output_file="ZDipISC.txt",
        plot_file=None, excel_file=None,
    ),
]


@dataclass
class TestDirectory:
    """Information about a test directory."""
    path: Path
    name: str
    cfg_file: Path
    output_dir: Path
    img_dir: Path
    logs_dir: Path
    wake2d_dir: Path
    oldtlwall_dir: Path


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def read_wake2d_file(filepath: Path, skip_rows: int = 1) -> Tuple[np.ndarray, np.ndarray]:
    data = np.loadtxt(filepath, skiprows=skip_rows)
    freqs = data[:, 0]
    return freqs, data[:, 1] + 1j * data[:, 2]


def read_oldtlwall_file(filepath: Path) -> Tuple[np.ndarray, np.ndarray]:
    for skip_rows in [1, 0, 2]:
        try:
            data = np.loadtxt(filepath, skiprows=skip_rows)
            if data.ndim == 2 and data.shape[1] == 3:
                return data[:, 0], data[:, 1] + 1j * data[:, 2]
        except (ValueError, IndexError):
            continue
    raise ValueError(
        f"Could not read OldTLWall file {filepath.name}. "
        f"Expected format: 3 columns (Frequency, Re(Z), Im(Z)) with optional header."
    )


def save_impedance_txt(
    filepath: Path, freqs: np.ndarray, Z: np.ndarray,
    header: str = "Frequency [Hz]\tRe(Z)\tIm(Z)",
) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    data = np.column_stack([freqs, Z.real, Z.imag])
    np.savetxt(filepath, data, delimiter='\t', header=header,
               comments='', fmt='%.6e')


def create_comparison_excel(
    filepath: Path, freqs: np.ndarray,
    Z_tlwall: np.ndarray, Z_ref: np.ndarray,
    impedance_type: ImpedanceType, logger,
) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)

    diff_real = Z_tlwall.real - Z_ref.real
    diff_imag = Z_tlwall.imag - Z_ref.imag

    with np.errstate(divide='ignore', invalid='ignore'):
        pct_real = (diff_real / np.abs(Z_ref.real)) * 100
        pct_imag = (diff_imag / np.abs(Z_ref.imag)) * 100
        pct_real = np.where(np.isfinite(pct_real), pct_real, 0)
        pct_imag = np.where(np.isfinite(pct_imag), pct_imag, 0)

    df = pd.DataFrame({
        'Frequency [Hz]': freqs,
        f'{impedance_type.name} TLWall Real': Z_tlwall.real,
        f'{impedance_type.name} Reference Real': Z_ref.real,
        'Diff Real (TLWall-Ref)': diff_real,
        'Diff Real [%]': pct_real,
        f'{impedance_type.name} TLWall Imag': Z_tlwall.imag,
        f'{impedance_type.name} Reference Imag': Z_ref.imag,
        'Diff Imag (TLWall-Ref)': diff_imag,
        'Diff Imag [%]': pct_imag,
    })

    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Comparison', index=False)
            notes_df = pd.DataFrame({
                'IMPORTANT NOTES': [
                    '1. This file is for MANUAL ANALYSIS by experts',
                    '2. Percentage differences can be MISLEADING for very small values',
                    '3. Large percentages do NOT necessarily mean errors',
                    '4. Use PLOTS for visual comparison',
                    '5. Compare absolute differences with typical impedance magnitudes',
                    '6. Differences near zero crossing are expected to be large (percentage)',
                    '',
                    'ANALYSIS WORKFLOW:',
                    '1. Open comparison plots (*.png) for visual inspection',
                    '2. Identify frequency ranges with significant differences',
                    '3. Check if differences are in regions of interest',
                    '4. Compare with typical impedance values for your application',
                    '5. Consult with impedance experts for interpretation',
                ]
            })
            notes_df.to_excel(writer, sheet_name='README', index=False, header=True)
        logger.info(f"  Saved Excel: {filepath.name}")
    except ImportError:
        csv_path = filepath.with_suffix('.csv')
        df.to_csv(csv_path, index=False, sep='\t')
        logger.warning(f"  openpyxl not installed, saved CSV: {csv_path.name}")


def _prepare_impedance_for_plot(Z: np.ndarray) -> Tuple[np.ndarray, np.ndarray, bool]:
    Z_clean = np.where(np.isfinite(Z), Z, np.nan)
    Z_real_abs = np.abs(Z_clean.real)
    Z_imag_abs = np.abs(Z_clean.imag)

    has_valid_real = np.any((Z_real_abs > 0) & np.isfinite(Z_real_abs))
    has_valid_imag = np.any((Z_imag_abs > 0) & np.isfinite(Z_imag_abs))

    if not (has_valid_real or has_valid_imag):
        return Z_real_abs, Z_imag_abs, False

    if has_valid_real:
        valid_real = Z_real_abs[(Z_real_abs > 0) & np.isfinite(Z_real_abs)]
        min_real = np.min(valid_real) * 0.1
    else:
        min_real = 1e-30
    if has_valid_imag:
        valid_imag = Z_imag_abs[(Z_imag_abs > 0) & np.isfinite(Z_imag_abs)]
        min_imag = np.min(valid_imag) * 0.1
    else:
        min_imag = 1e-30

    Z_real_abs = np.where((Z_real_abs > 0) & np.isfinite(Z_real_abs),
                          Z_real_abs, min_real)
    Z_imag_abs = np.where((Z_imag_abs > 0) & np.isfinite(Z_imag_abs),
                          Z_imag_abs, min_imag)
    return Z_real_abs, Z_imag_abs, True


def create_comparison_plot(
    filepath: Path,
    freqs_tlwall: np.ndarray, Z_tlwall: np.ndarray,
    freqs_ref: np.ndarray, Z_ref: np.ndarray,
    impedance_type: ImpedanceType, logger,
    ref_label: str = "Reference",
) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    tlwall_real, tlwall_imag, tlwall_valid = _prepare_impedance_for_plot(Z_tlwall)
    ref_real, ref_imag, ref_valid = _prepare_impedance_for_plot(Z_ref)

    if not (tlwall_valid or ref_valid):
        logger.warning(f"    All values are inf/nan, skipping plot: {filepath.name}")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    ax1.loglog(freqs_tlwall, tlwall_real, 'b-', linewidth=2.5,
               label='PyTLWall', alpha=0.8)
    ax1.loglog(freqs_ref, ref_real, 'r--', linewidth=2,
               label=ref_label, alpha=0.8)
    ax1.set_xlabel('Frequency [Hz]', fontsize=14)
    ax1.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Real', fontsize=14)
    ax1.set_title(f'{impedance_type.label} - Real Part Comparison',
                  fontsize=16, fontweight='bold')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.legend(fontsize=12, loc='best')
    ax1.tick_params(labelsize=12)

    ax2.loglog(freqs_tlwall, tlwall_imag, 'b-', linewidth=2.5,
               label='PyTLWall', alpha=0.8)
    ax2.loglog(freqs_ref, ref_imag, 'r--', linewidth=2,
               label=ref_label, alpha=0.8)
    ax2.set_xlabel('Frequency [Hz]', fontsize=14)
    ax2.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Imag', fontsize=14)
    ax2.set_title(f'{impedance_type.label} - Imaginary Part Comparison',
                  fontsize=16, fontweight='bold')
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend(fontsize=12, loc='best')
    ax2.tick_params(labelsize=12)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"    Saved plot: {filepath.name}")


def create_single_plot(
    filepath: Path, freqs: np.ndarray, Z: np.ndarray,
    impedance_type: ImpedanceType, logger,
) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    Z_real_abs, Z_imag_abs, is_valid = _prepare_impedance_for_plot(Z)

    if not is_valid:
        logger.warning(f"    All values are inf/nan, skipping plot: {filepath.name}")
        return

    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))

    ax1.loglog(freqs, Z_real_abs, 'b-', linewidth=2, alpha=0.8)
    ax1.set_xlabel('Frequency [Hz]', fontsize=14)
    ax1.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Real', fontsize=14)
    ax1.set_title(f'{impedance_type.label} - Real Part',
                  fontsize=16, fontweight='bold')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.tick_params(labelsize=12)

    ax2.loglog(freqs, Z_imag_abs, 'b-', linewidth=2, alpha=0.8)
    ax2.set_xlabel('Frequency [Hz]', fontsize=14)
    ax2.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Imag', fontsize=14)
    ax2.set_title(f'{impedance_type.label} - Imaginary Part',
                  fontsize=16, fontweight='bold')
    ax2.grid(True, which='both', alpha=0.3)
    ax2.tick_params(labelsize=12)

    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    logger.info(f"    Saved plot: {filepath.name}")


# ============================================================================
# TEST DISCOVERY
# ============================================================================

def discover_test_directories(
    base_dir: Path,
    subdirs: Optional[List[str]] = None,
    cfg_pattern: Optional[str] = None,
) -> List[TestDirectory]:
    test_dirs = []

    if not base_dir.exists():
        raise FileNotFoundError(f"CompareWake2D directory not found: {base_dir}")

    if subdirs:
        scan_dirs = [base_dir / subdir for subdir in subdirs]
    else:
        scan_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name != 'log']

    for test_path in scan_dirs:
        if not test_path.is_dir():
            continue

        # Resolve to an absolute path so that the per-case `os.chdir`
        # done by run_single_test (to make cfg-internal relative paths
        # work) cannot break subsequent path operations.
        test_path = test_path.resolve()

        if cfg_pattern:
            cfg_files = list(test_path.glob(cfg_pattern))
            if not cfg_files:
                print(f"Warning: No .cfg file matching '{cfg_pattern}' "
                      f"found in {test_path.name}, skipping")
                continue
        else:
            cfg_files = list(test_path.glob("*.cfg"))
            if not cfg_files:
                continue

        if len(cfg_files) > 1:
            if cfg_pattern:
                print(f"Warning: Multiple .cfg files matching '{cfg_pattern}' "
                      f"in {test_path.name}, using first: {cfg_files[0].name}")
            else:
                print(f"Warning: Multiple .cfg files in {test_path.name}, "
                      f"using first: {cfg_files[0].name}")
                print(f"         Use --cfg-pattern to specify which one to use")

        cfg_file = cfg_files[0]

        test_dirs.append(TestDirectory(
            path=test_path,
            name=test_path.name,
            cfg_file=cfg_file,
            output_dir=test_path / CompareW2DConfig.OUTPUT_SUBDIR,
            img_dir=test_path / CompareW2DConfig.IMG_SUBDIR,
            logs_dir=test_path / CompareW2DConfig.LOGS_SUBDIR,
            wake2d_dir=test_path / CompareW2DConfig.REFERENCE_SUBDIR,
            oldtlwall_dir=test_path / CompareW2DConfig.REFERENCE_SUBDIR2,
        ))

    return test_dirs


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_single_test(
    test_dir: TestDirectory,
    logger,
    compute_space_charge: bool = True,
) -> bool:
    logging_util.log_section_header(logger, f"Running test: {test_dir.name}")
    logger.info(f"Configuration: {test_dir.cfg_file}")
    logger.info(f"Output directory: {test_dir.output_dir}")
    logger.info(f"Image directory: {test_dir.img_dir}")
    logger.info(f"Wake2D directory: {test_dir.wake2d_dir}")
    logger.info("")

    # Switch cwd to the case directory so that relative paths inside the
    # .cfg (e.g. [path_info] main_path = Wake2D, or [frequency_file]
    # filename = ...) are resolved relative to it. test_dir.* paths were
    # already resolved to absolute in discover_test_directories, so they
    # keep working under the chdir.
    old_cwd = os.getcwd()
    os.chdir(str(test_dir.path))
    logger.info(f"  Working directory: {test_dir.path}")

    try:
        logger.info("Loading configuration...")
        cfg = pytlwall.CfgIo(test_dir.cfg_file.name)

        boundary_type = cfg.config.get('boundary', 'type', fallback='UNKNOWN')
        logger.info(f"  Boundary type: {boundary_type}")

        wall = cfg.read_pytlwall()
        logger.info(f"  Configuration loaded successfully")
        logger.info(f"  Chamber: {wall.chamber.chamber_shape}")
        logger.info(f"  Frequencies: {len(wall.f)} points")
        logger.info(f"  Frequency range: {wall.f[0]:.2e} - {wall.f[-1]:.2e} Hz")
        logger.info("")

        cfg_name = test_dir.cfg_file.stem.lower()
        do_wake2d_comparison = 'wake2d' in cfg_name or 'wake' in cfg_name
        do_oldtlwall_comparison = 'old' in cfg_name or 'oldtlwall' in cfg_name

        if not do_wake2d_comparison and not do_oldtlwall_comparison:
            do_wake2d_comparison = True
            do_oldtlwall_comparison = True

        logger.info(f"Config file: {test_dir.cfg_file.name}")
        logger.info(f"  Will compare with Wake2D: {do_wake2d_comparison}")
        logger.info(f"  Will compare with OldTLWall: {do_oldtlwall_comparison}")
        logger.info("")

        test_dir.output_dir.mkdir(parents=True, exist_ok=True)
        test_dir.img_dir.mkdir(parents=True, exist_ok=True)

        readme_source = Path(__file__).parent / 'OUTPUT_ANALYSIS_README.md'
        readme_dest = test_dir.output_dir / 'README.md'
        if readme_source.exists():
            import shutil
            shutil.copy2(readme_source, readme_dest)
            logger.info(f"  Copied analysis README to {readme_dest.relative_to(test_dir.path)}")

        impedance_types = get_impedance_types_for_test(test_dir.wake2d_dir)
        logger.info(f"\n  Impedance types to process: {[t.name for t in impedance_types]}")

        logger.info("Computing and comparing impedances...")

        for imp_type in impedance_types:
            logger.info(f"\n  Processing {imp_type.name} ({imp_type.label})...")

            if not hasattr(wall, imp_type.result_attr):
                logger.warning(f"    Skipping {imp_type.name}: attribute "
                               f"'{imp_type.result_attr}' not available")
                continue

            try:
                compute_method = getattr(wall, imp_type.compute_method)
                compute_method()
                Z_tlwall = getattr(wall, imp_type.result_attr)
            except Exception as e:
                logger.error(f"    Failed to compute {imp_type.name}: {e}")
                continue

            output_path = test_dir.output_dir / imp_type.output_file
            save_impedance_txt(output_path, wall.f, Z_tlwall)
            logger.info(f"    Saved output: {output_path.name}")

            single_plot_path = test_dir.img_dir / imp_type.plot_file
            create_single_plot(single_plot_path, wall.f, Z_tlwall, imp_type, logger)

            if do_wake2d_comparison and imp_type.wake2d_file:
                if test_dir.wake2d_dir.exists():
                    wake2d_files = list(test_dir.wake2d_dir.glob(imp_type.wake2d_file))
                else:
                    wake2d_files = []

                if not wake2d_files:
                    logger.warning(f"    No Wake2D reference file found: "
                                   f"{imp_type.wake2d_file}")
                else:
                    if len(wake2d_files) > 1:
                        logger.warning(f"    Multiple Wake2D files found, "
                                       f"using first: {wake2d_files[0].name}")

                    wake2d_file = wake2d_files[0]
                    logger.info(f"    Wake2D reference: {wake2d_file.name}")

                    freqs_wake2d, Z_wake2d = read_wake2d_file(wake2d_file)

                    if len(freqs_wake2d) != len(wall.f):
                        logger.warning(
                            f"    Frequency count mismatch: "
                            f"TLWall={len(wall.f)}, Wake2D={len(freqs_wake2d)}"
                        )

                    excel_path = test_dir.output_dir / (
                        CompareW2DConfig.COMPARISON_PREFIX + imp_type.excel_file
                    )
                    create_comparison_excel(
                        excel_path, wall.f, Z_tlwall, Z_wake2d, imp_type, logger
                    )

                    plot_filename = f"WakeVsNew_{imp_type.name}.png"
                    plot_path = test_dir.img_dir / plot_filename
                    create_comparison_plot(
                        plot_path, wall.f, Z_tlwall, freqs_wake2d, Z_wake2d,
                        imp_type, logger, ref_label="Wake2D",
                    )

        if do_oldtlwall_comparison and test_dir.oldtlwall_dir.exists():
            logger.info("\n  Comparing with OldTLWall reference data...")

            for imp_type in IMPEDANCE_TYPES:
                oldtlwall_file = test_dir.oldtlwall_dir / imp_type.output_file
                if not oldtlwall_file.exists():
                    continue

                if not hasattr(wall, imp_type.result_attr):
                    logger.warning(f"    {imp_type.name}: Result attribute "
                                   f"'{imp_type.result_attr}' not available")
                    continue

                logger.info(f"    Processing {imp_type.name} vs OldTLWall...")
                logger.info(f"      OldTLWall reference: {oldtlwall_file.name}")

                try:
                    freqs_old, Z_old = read_oldtlwall_file(oldtlwall_file)
                except Exception as e:
                    logger.error(f"      Failed to read OldTLWall file: {e}")
                    continue

                try:
                    if hasattr(wall, imp_type.compute_method):
                        compute_method = getattr(wall, imp_type.compute_method)
                        compute_method()
                    Z_tlwall = getattr(wall, imp_type.result_attr)
                except Exception as e:
                    logger.error(f"      Failed to get PyTLWall data for "
                                 f"{imp_type.name}: {e}")
                    continue

                if len(freqs_old) != len(wall.f):
                    logger.warning(
                        f"      Frequency count mismatch: "
                        f"PyTLWall={len(wall.f)}, OldTLWall={len(freqs_old)}"
                    )

                excel_path = test_dir.output_dir / (
                    CompareW2DConfig.COMPARISON_PREFIX2 + imp_type.excel_file
                )
                create_comparison_excel(
                    excel_path, wall.f, Z_tlwall, Z_old, imp_type, logger
                )

                plot_filename = f"OldVsNew_{imp_type.name}.png"
                plot_path = test_dir.img_dir / plot_filename
                create_comparison_plot(
                    plot_path, wall.f, Z_tlwall, freqs_old, Z_old,
                    imp_type, logger, ref_label="OldTLWall",
                )
        elif do_oldtlwall_comparison:
            logger.info("\n  OldTLWall comparison requested but directory not "
                        "found, skipping")

        if (do_oldtlwall_comparison and test_dir.oldtlwall_dir.exists()
                and compute_space_charge):
            logger.info("\n  Comparing space charge impedances with OldTLWall...")

            for imp_type in SPACE_CHARGE_TYPES:
                oldtlwall_file = test_dir.oldtlwall_dir / imp_type.output_file
                if not oldtlwall_file.exists():
                    continue

                logger.info(f"    Processing {imp_type.name} vs OldTLWall...")

                if not hasattr(wall, imp_type.compute_method):
                    logger.warning(f"      Method {imp_type.compute_method} "
                                   f"not available")
                    continue

                compute_method = getattr(wall, imp_type.compute_method)
                compute_method()
                Z_tlwall = getattr(wall, imp_type.result_attr)

                try:
                    freqs_old, Z_old = read_oldtlwall_file(oldtlwall_file)
                except Exception as e:
                    logger.error(f"      Failed to read OldTLWall file: {e}")
                    continue

                excel_path = test_dir.output_dir / (
                    CompareW2DConfig.COMPARISON_PREFIX2 + imp_type.name + ".xlsx"
                )
                create_comparison_excel(
                    excel_path, wall.f, Z_tlwall, Z_old, imp_type, logger
                )

                plot_filename = f"OldVsNew_{imp_type.name}.png"
                plot_path = test_dir.img_dir / plot_filename
                create_comparison_plot(
                    plot_path, wall.f, Z_tlwall, freqs_old, Z_old,
                    imp_type, logger, ref_label="OldTLWall",
                )

        if compute_space_charge:
            logger.info("\n  Computing space charge impedances...")

            for imp_type in SPACE_CHARGE_TYPES:
                logger.info(f"    Processing {imp_type.name}...")

                if not hasattr(wall, imp_type.compute_method):
                    logger.warning(f"      Method {imp_type.compute_method} "
                                   f"not available")
                    continue

                compute_method = getattr(wall, imp_type.compute_method)
                compute_method()
                Z = getattr(wall, imp_type.result_attr)

                output_path = test_dir.output_dir / imp_type.output_file
                save_impedance_txt(output_path, wall.f, Z)
                logger.info(f"      Saved: {output_path.name}")

                plot_filename = f"{imp_type.name}.png"
                plot_path = test_dir.img_dir / plot_filename
                create_single_plot(plot_path, wall.f, Z, imp_type, logger)

        logger.info(f"\nTest {test_dir.name} completed successfully")

        if do_wake2d_comparison:
            generate_isc_comparison_summary(test_dir, logger)

        return True

    except Exception as e:
        logger.error(f"\nTest {test_dir.name} failed with error:")
        logger.error(f"  {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  Traceback:\n{traceback.format_exc()}")
        return False
    finally:
        os.chdir(old_cwd)


def generate_isc_comparison_summary(test_dir: TestDirectory, logger) -> None:
    logger.info("\n" + "=" * 80)
    logger.info("ISC COMPARISON SUMMARY: Which version matches Wake2D better?")
    logger.info("=" * 80)

    pairs_to_compare = [
        ("Longitudinal", "LongTotal.xlsx", "Long.xlsx"),
        ("Transverse", "TransTotal.xlsx", "Trans.xlsx"),
        ("Dipolar X", "DipXTotal.xlsx", "DipX.xlsx"),
        ("Dipolar Y", "DipYTotal.xlsx", "DipY.xlsx"),
        ("Quadrupolar X", "QuadXTotal.xlsx", "QuadX.xlsx"),
        ("Quadrupolar Y", "QuadYTotal.xlsx", "QuadY.xlsx"),
    ]

    results = []
    for name, with_isc_file, without_isc_file in pairs_to_compare:
        with_isc_path = test_dir.output_dir / (CompareW2DConfig.COMPARISON_PREFIX + with_isc_file)
        without_isc_path = test_dir.output_dir / (CompareW2DConfig.COMPARISON_PREFIX + without_isc_file)

        if not with_isc_path.exists() or not without_isc_path.exists():
            continue

        try:
            df_with = pd.read_excel(with_isc_path, sheet_name='Comparison')
            df_without = pd.read_excel(without_isc_path, sheet_name='Comparison')

            with_isc_real_diff = np.nanmedian(np.abs(df_with['Diff Real [%]'].values))
            with_isc_imag_diff = np.nanmedian(np.abs(df_with['Diff Imag [%]'].values))
            without_isc_real_diff = np.nanmedian(np.abs(df_without['Diff Real [%]'].values))
            without_isc_imag_diff = np.nanmedian(np.abs(df_without['Diff Imag [%]'].values))

            with_isc_score = (with_isc_real_diff + with_isc_imag_diff) / 2
            without_isc_score = (without_isc_real_diff + without_isc_imag_diff) / 2

            if with_isc_score < without_isc_score:
                winner = "WITH ISC"
                ratio = without_isc_score / with_isc_score if with_isc_score > 0 else float('inf')
            else:
                winner = "WITHOUT ISC"
                ratio = with_isc_score / without_isc_score if without_isc_score > 0 else float('inf')

            results.append({
                'name': name,
                'with_isc_real': with_isc_real_diff,
                'with_isc_imag': with_isc_imag_diff,
                'with_isc_score': with_isc_score,
                'without_isc_real': without_isc_real_diff,
                'without_isc_imag': without_isc_imag_diff,
                'without_isc_score': without_isc_score,
                'winner': winner,
                'ratio': ratio,
            })
        except Exception as e:
            logger.warning(f"  Could not compare {name}: {e}")
            continue

    if results:
        logger.info("")
        logger.info(f"{'Impedance':<16} | {'With ISC':<20} | {'Without ISC':<20} | {'Better Match':<15}")
        logger.info(f"{'':<16} | {'Real%':>8} {'Imag%':>8} | {'Real%':>8} {'Imag%':>8} | {'':<15}")
        logger.info("-" * 80)
        for r in results:
            logger.info(
                f"{r['name']:<16} | "
                f"{r['with_isc_real']:>8.1f} {r['with_isc_imag']:>8.1f} | "
                f"{r['without_isc_real']:>8.1f} {r['without_isc_imag']:>8.1f} | "
                f"{r['winner']:<15}"
            )
        logger.info("-" * 80)
        logger.info("")
        logger.info("NOTE: Lower percentage difference = better match with Wake2D")
        logger.info("      Values show median |diff %| across all frequencies")

        summary_path = test_dir.output_dir / "ISC_comparison_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("ISC COMPARISON SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write("Which version (with or without ISC) matches Wake2D better?\n\n")
            f.write(f"{'Impedance':<16} | {'With ISC Score':<15} | {'Without ISC Score':<18} | {'Better Match':<15}\n")
            f.write("-" * 80 + "\n")
            for r in results:
                f.write(f"{r['name']:<16} | {r['with_isc_score']:>15.2f} | "
                        f"{r['without_isc_score']:>18.2f} | {r['winner']:<15}\n")
            f.write("\n\nScore = median absolute percentage difference (Real + Imag) / 2\n")
            f.write("Lower score = better match with Wake2D\n")
        logger.info(f"\n  Summary saved to: {summary_path.name}")
    else:
        logger.info("  No comparison data available for ISC analysis")


def run_compareW2D_tests(
    base_dir: Optional[Path] = None,
    subdirs: Optional[List[str]] = None,
    cfg_pattern: Optional[str] = None,
    verbosity: int = 2,
    compute_space_charge: bool = True,
) -> bool:
    """
    Run all (or selected) compareWake2D tests.

    Returns
    -------
    success : bool
        True if all tests passed.
    """
    if base_dir is None:
        base_dir = CompareW2DConfig.BASE_DIR

    try:
        test_dirs = discover_test_directories(base_dir, subdirs, cfg_pattern)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return False

    if not test_dirs:
        print(f"No test directories found in {base_dir}")
        return False

    print(f"\nDiscovered {len(test_dirs)} test directories:")
    for td in test_dirs:
        print(f"  - {td.name}")
    print()

    results = []
    for test_dir in test_dirs:
        log_config = logging_util.LogConfig(
            log_dir=test_dir.logs_dir,
            log_basename=f"compareW2D_{test_dir.name}",
            verbosity=verbosity,
            add_timestamp=True,
            console_output=True,
        )
        log_path = logging_util.setup_logging(log_config)
        logger = logging_util.get_logger(__name__)

        logger.info("=" * 80)
        logger.info(f"PYTLWALL COMPARE-WAKE2D TEST: {test_dir.name}")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {logging_util.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Log file: {log_path}")
        logger.info("")

        success = run_single_test(test_dir, logger, compute_space_charge)
        results.append((test_dir.name, success))

        logger.info("\n" + "=" * 80)
        logger.info(f"TEST {test_dir.name}: {'PASSED' if success else 'FAILED'}")
        logger.info("=" * 80)
        logger.info(f"Log saved to: {log_path}\n")

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    print("\n" + "=" * 80)
    print("COMPARE-WAKE2D TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    for name, success in results:
        status = "PASSED" if success else "FAILED"
        print(f"  {name}: {status}")
    print("\n" + "=" * 80)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    if failed == 0:
        print("\nALL TESTS PASSED")
        print("=" * 80)
        return True
    else:
        print(f"\n{failed} TEST(S) FAILED")
        print("=" * 80)
        return False


# Back-compat alias: external callers can still use run_deep_tests().
run_deep_tests = run_compareW2D_tests


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="CompareWake2D test runner for PyTLWall",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with default config files
  python tests/run_tests_compareW2D.py

  # Run specific subdirectory with Wake2D config
  python tests/run_tests_compareW2D.py --subdirs newCV --cfg-pattern "*Wake2D.cfg"

  # Run specific subdirectory with OldTLWall config
  python tests/run_tests_compareW2D.py --subdirs newCV --cfg-pattern "*OldTLWall.cfg"
        """,
    )
    parser.add_argument(
        "--base-dir", type=Path, default=CompareW2DConfig.BASE_DIR,
        help="Base directory for compareWake2D tests",
    )
    parser.add_argument(
        "--subdirs", nargs='+',
        help="Specific subdirectories to test (default: all)",
    )
    parser.add_argument(
        "--cfg-pattern", type=str,
        help="Pattern for config file (e.g., '*Wake2D.cfg', '*OldTLWall.cfg').",
    )
    parser.add_argument(
        "--verbosity", type=int, default=CompareW2DConfig.VERBOSITY,
        choices=[1, 2, 3],
        help="Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)",
    )
    parser.add_argument(
        "--no-space-charge", action="store_true",
        help="Skip space charge impedance calculations",
    )

    args = parser.parse_args()

    success = run_compareW2D_tests(
        base_dir=args.base_dir,
        subdirs=args.subdirs,
        cfg_pattern=args.cfg_pattern,
        verbosity=args.verbosity,
        compute_space_charge=not args.no_space_charge,
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
