#!/usr/bin/env python3
"""
Deep Test Runner for PyTLWall

PURPOSE:
--------
This script generates output files for MANUAL ANALYSIS of impedance calculations.
It compares PyTLWall results with Wake2D references and creates:
- Text files with impedance values
- Excel files with side-by-side comparisons and differences
- Comparison plots for visual inspection

IMPORTANT:
----------
Automatic validation is NOT performed. Percentage differences can be misleading
for very small values. The files generated are meant for EXPERT ANALYSIS.

Use the Excel files and plots to manually inspect where differences occur
and determine if they are acceptable for your use case.

Automatically discovers and runs tests in tests/deep_test/ subdirectories.
Each test directory should contain:
- A .cfg configuration file
- Wake2D/ directory with reference data

Generates:
- Output text files (ZLong.txt, ZTrans.txt, etc.)
- Excel comparison files with differences
- Comparison plots (PNG)
- Detailed logs in each test directory
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional, List, Tuple
from dataclasses import dataclass

# Add parent directory to path
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

class DeepTestConfig:
    """Configuration for deep test execution."""
    
    # Base directory for deep tests
    DEEP_TEST_DIR: Path = Path("tests/deep_test")
    
    # Subdirectories to test (None = all subdirectories)
    TEST_SUBDIRS: Optional[List[str]] = None  # e.g., ["newCV", "newPEC"]
    
    # Config file pattern (None = first .cfg found, or specify pattern like "*Wake2D.cfg")
    CFG_PATTERN: Optional[str] = None  # e.g., "*Wake2D.cfg", "*OldTLWall.cfg"
    
    # Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)
    VERBOSITY: int = 2
    
    # Output subdirectories
    OUTPUT_SUBDIR: str = "output"
    IMG_SUBDIR: str = "img"
    LOGS_SUBDIR: str = "logs"
    
    # Reference data directory
    REFERENCE_SUBDIR: str = "Wake2D"
    REFERENCE_SUBDIR2: str = "OldTLWall"
    
    # File naming patterns
    OUTPUT_PREFIX: str = ""  # Prefix for output files
    COMPARISON_PREFIX: str = "NewTLWallvsWake2D"  # Prefix for comparison files
    COMPARISON_PREFIX2: str = "NewTLWallvsOld"  # Prefix for comparison files

# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class ImpedanceType:
    """Definition of an impedance type to compute and compare."""
    name: str  # Short name (e.g., "ZLong")
    label: str  # Display name (e.g., "Longitudinal Impedance")
    unit: str  # Unit (e.g., "Ω")
    compute_method: str  # Method name on Wall object (e.g., "calc_ZLong")
    result_attr: str  # Attribute name on Wall object (e.g., "ZLong")
    wake2d_file: str  # Wake2D reference file pattern
    output_file: str  # Output text file name
    plot_file: str  # Plot file name
    excel_file: str  # Excel comparison file name


# Standard impedance types
# The script compares BOTH with and without ISC to determine which matches Wake2D better

# =============================================================================
# LONGITUDINAL IMPEDANCES
# =============================================================================

# Longitudinal WITH ISC
ZLongTotal = ImpedanceType(
    name="ZLongTotal",
    label="Longitudinal (with ISC)",
    unit="Ω",
    compute_method="calc_ZLong",
    result_attr="ZLongTotal",
    wake2d_file="ZlongW*.dat",
    output_file="ZLongTotal.txt",
    plot_file="ZLongTotal.png",
    excel_file="LongTotal.xlsx"
)

# Longitudinal WITHOUT ISC
ZLong = ImpedanceType(
    name="ZLong",
    label="Longitudinal (no ISC)",
    unit="Ω",
    compute_method="calc_ZLong",
    result_attr="ZLong",
    wake2d_file="ZlongW*.dat",
    output_file="ZLong.txt",
    plot_file="ZLong.png",
    excel_file="Long.xlsx"
)

# =============================================================================
# TRANSVERSE IMPEDANCES (generic)
# =============================================================================

# Transverse WITH ISC
ZTransTotal = ImpedanceType(
    name="ZTransTotal",
    label="Transverse (with ISC)",
    unit="Ω/m",
    compute_method="calc_ZTrans",
    result_attr="ZTransTotal",
    wake2d_file="ZtransW*.dat",
    output_file="ZTransTotal.txt",
    plot_file="ZTransTotal.png",
    excel_file="TransTotal.xlsx"
)

# Transverse WITHOUT ISC
ZTrans = ImpedanceType(
    name="ZTrans",
    label="Transverse (no ISC)",
    unit="Ω/m",
    compute_method="calc_ZTrans",
    result_attr="ZTrans",
    wake2d_file="ZtransW*.dat",
    output_file="ZTrans.txt",
    plot_file="ZTrans.png",
    excel_file="Trans.xlsx"
)

# =============================================================================
# DIPOLAR X IMPEDANCES
# =============================================================================

# DipX WITH ISC
ZDipXTotal = ImpedanceType(
    name="ZDipXTotal",
    label="Dipolar X (with ISC)",
    unit="Ω/m",
    compute_method="calc_ZTrans",
    result_attr="ZDipXTotal",
    output_file="ZDipXTotal.txt",
    plot_file="ZDipXTotal.png",
    excel_file="DipXTotal.xlsx",
    wake2d_file="ZxdipW*.dat",
)

# DipX WITHOUT ISC
ZDipX = ImpedanceType(
    name="ZDipX",
    label="Dipolar X (no ISC)",
    unit="Ω/m",
    compute_method="calc_ZTrans",
    result_attr="ZDipX",
    output_file="ZDipX.txt",
    plot_file="ZDipX.png",
    excel_file="DipX.xlsx",
    wake2d_file="ZxdipW*.dat",
)

# =============================================================================
# DIPOLAR Y IMPEDANCES
# =============================================================================

# DipY WITH ISC
ZDipYTotal = ImpedanceType(
    name="ZDipYTotal",
    label="Dipolar Y (with ISC)",
    unit="Ω/m",        
    compute_method="calc_ZTrans",
    result_attr="ZDipYTotal",
    output_file="ZDipYTotal.txt",
    plot_file="ZDipYTotal.png",
    excel_file="DipYTotal.xlsx",
    wake2d_file="ZydipW*.dat",
)

# DipY WITHOUT ISC
ZDipY = ImpedanceType(
    name="ZDipY",
    label="Dipolar Y (no ISC)",
    unit="Ω/m",        
    compute_method="calc_ZTrans",
    result_attr="ZDipY",
    output_file="ZDipY.txt",
    plot_file="ZDipY.png",
    excel_file="DipY.xlsx",
    wake2d_file="ZydipW*.dat",
)

# =============================================================================
# QUADRUPOLAR X IMPEDANCES
# =============================================================================

# QuadX WITH ISC
ZQuadXTotal = ImpedanceType(
    name="ZQuadXTotal",
    label="Quadrupolar X (with ISC)",
    unit="Ω/m",        
    compute_method="calc_ZTrans",
    result_attr="ZQuadXTotal",
    output_file="ZQuadXTotal.txt",
    plot_file="ZQuadXTotal.png",
    excel_file="QuadXTotal.xlsx",
    wake2d_file="ZxquadW*.dat",
)

# QuadX WITHOUT ISC
ZQuadX = ImpedanceType(
    name="ZQuadX",
    label="Quadrupolar X (no ISC)",
    unit="Ω/m",        
    compute_method="calc_ZTrans",
    result_attr="ZQuadX",
    output_file="ZQuadX.txt",
    plot_file="ZQuadX.png",
    excel_file="QuadX.xlsx",
    wake2d_file="ZxquadW*.dat",
)

# =============================================================================
# QUADRUPOLAR Y IMPEDANCES
# =============================================================================

# QuadY WITH ISC
ZQuadYTotal = ImpedanceType(
    name="ZQuadYTotal",
    label="Quadrupolar Y (with ISC)",
    unit="Ω/m",        
    compute_method="calc_ZTrans",
    result_attr="ZQuadYTotal",
    output_file="ZQuadYTotal.txt",
    plot_file="ZQuadYTotal.png",
    excel_file="QuadYTotal.xlsx",
    wake2d_file="ZyquadW*.dat",
)

# QuadY WITHOUT ISC
ZQuadY = ImpedanceType(
    name="ZQuadY",
    label="Quadrupolar Y (no ISC)",
    unit="Ω/m",        
    compute_method="calc_ZTrans",
    result_attr="ZQuadY",
    output_file="ZQuadY.txt",
    plot_file="ZQuadY.png",
    excel_file="QuadY.xlsx",
    wake2d_file="ZyquadW*.dat",
)

# =============================================================================
# GROUPED IMPEDANCE PAIRS (with/without ISC for same Wake2D reference)
# =============================================================================

# Each tuple: (with_ISC, without_ISC) - both compared to the same Wake2D file
IMPEDANCE_PAIRS = {
    "Longitudinal": (ZLongTotal, ZLong),
    "Transverse": (ZTransTotal, ZTrans),
    "DipolarX": (ZDipXTotal, ZDipX),
    "DipolarY": (ZDipYTotal, ZDipY),
    "QuadrupolarX": (ZQuadXTotal, ZQuadX),
    "QuadrupolarY": (ZQuadYTotal, ZQuadY),
}

# Flat list for backward compatibility
IMPEDANCE_TYPES = [
    ZLongTotal, ZLong,
    ZTransTotal, ZTrans,
    ZDipXTotal, ZDipX,
    ZDipYTotal, ZDipY,
    ZQuadXTotal, ZQuadX,
    ZQuadYTotal, ZQuadY,
]

# Core types (always computed) - both with and without ISC
CORE_IMPEDANCE_TYPES = [ZLongTotal, ZLong, ZTransTotal, ZTrans]

# Separate X/Y types
SEPARATE_DIPQUAD_TYPES = [
    ZDipXTotal, ZDipX,
    ZDipYTotal, ZDipY,
    ZQuadXTotal, ZQuadX,
    ZQuadYTotal, ZQuadY,
]

# Generic (legacy)
GENERIC_DIPQUAD_TYPES = []


def get_impedance_types_for_test(wake2d_dir: Path) -> List[ImpedanceType]:
    """
    Determine which impedance types to compute based on available Wake2D reference files.
    
    This function automatically selects BOTH with-ISC and without-ISC versions
    for each impedance type to allow comparison of which matches Wake2D better.
    
    Parameters
    ----------
    wake2d_dir : Path
        Directory containing Wake2D reference files
        
    Returns
    -------
    List[ImpedanceType]
        List of impedance types to compute and compare
    """
    result = list(CORE_IMPEDANCE_TYPES)  # Always include core types (both with/without ISC)
    
    if not wake2d_dir.exists():
        # No Wake2D dir, include all types for output generation
        return CORE_IMPEDANCE_TYPES + SEPARATE_DIPQUAD_TYPES
    
    # Check for separate X/Y dipolar files
    has_xdip = len(list(wake2d_dir.glob("Zxdip*.dat"))) > 0
    has_ydip = len(list(wake2d_dir.glob("Zydip*.dat"))) > 0
    
    # Check for separate X/Y quadrupolar files
    has_xquad = len(list(wake2d_dir.glob("Zxquad*.dat"))) > 0
    has_yquad = len(list(wake2d_dir.glob("Zyquad*.dat"))) > 0
    
    # Dipolar: add both with-ISC and without-ISC versions
    if has_xdip:
        result.append(ZDipXTotal)  # with ISC
        result.append(ZDipX)       # without ISC
    if has_ydip:
        result.append(ZDipYTotal)  # with ISC
        result.append(ZDipY)       # without ISC
    
    # Quadrupolar: add both with-ISC and without-ISC versions
    if has_xquad:
        result.append(ZQuadXTotal)  # with ISC
        result.append(ZQuadX)       # without ISC
    if has_yquad:
        result.append(ZQuadYTotal)  # with ISC
        result.append(ZQuadY)       # without ISC
    
    # If no specific files found, add all for output generation
    if not (has_xdip or has_ydip or has_xquad or has_yquad):
        result.extend(SEPARATE_DIPQUAD_TYPES)
    
    return result

# Space charge impedances (if requested)
SPACE_CHARGE_TYPES = [
    ImpedanceType(
        name="ZLongDSC",
        label="Longitudinal Direct Space Charge",
        unit="Ω",
        compute_method="calc_ZLongDSC",
        result_attr="ZLongDSC",
        wake2d_file=None,
        output_file="ZLongDSC.txt",
        plot_file=None,
        excel_file=None
    ),
    ImpedanceType(
        name="ZLongISC",
        label="Longitudinal Indirect Space Charge",
        unit="Ω",
        compute_method="calc_ZLongISC",
        result_attr="ZLongISC",
        wake2d_file=None,
        output_file="ZLongISC.txt",
        plot_file=None,
        excel_file=None
    ),
    ImpedanceType(
        name="ZTransDSC",
        label="Transverse Direct Space Charge",
        unit="Ω/m",
        compute_method="calc_ZTransDSC",
        result_attr="ZTransDSC",
        wake2d_file=None,
        output_file="ZTransDSC.txt",
        plot_file=None,
        excel_file=None
    ),
    ImpedanceType(
        name="ZTransISC",
        label="Transverse Indirect Space Charge",
        unit="Ω/m",
        compute_method="calc_ZTransISC",
        result_attr="ZTransISC",
        wake2d_file=None,
        output_file="ZTransISC.txt",
        plot_file=None,
        excel_file=None
    ),
    ImpedanceType(
        name="ZDipDSC",
        label="Dipolar Direct Space Charge",
        unit="Ω/m",
        compute_method="calc_ZTransDSC",  # Triggers base calculation
        result_attr="ZDipDSC",  # Uses new TlWall property
        wake2d_file=None,
        output_file="ZDipDSC.txt",
        plot_file=None,
        excel_file=None
    ),
    ImpedanceType(
        name="ZDipISC",
        label="Dipolar Indirect Space Charge",
        unit="Ω/m",
        compute_method="calc_ZTransISC",  # Triggers base calculation
        result_attr="ZDipISC",  # Uses new TlWall property
        wake2d_file=None,
        output_file="ZDipISC.txt",
        plot_file=None,
        excel_file=None
    )
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
    """
    Read Wake2D reference file (3 columns: freq, Re(Z), Im(Z)).
    
    Parameters
    ----------
    filepath : Path
        Path to the Wake2D file
    skip_rows : int
        Number of header rows to skip
        
    Returns
    -------
    freqs : np.ndarray
        Frequency array [Hz]
    Z : np.ndarray
        Complex impedance array
    """
    data = np.loadtxt(filepath, skiprows=skip_rows)
    freqs = data[:, 0]
    z_real = data[:, 1]
    z_imag = data[:, 2]
    return freqs, z_real + 1j * z_imag


def read_oldtlwall_file(filepath: Path) -> Tuple[np.ndarray, np.ndarray]:
    """
    Read OldTLWall reference file (same format as PyTLWall output: 3 columns with header).
    
    The file format is:
    Frequency [Hz]	Re(Z)	Im(Z)
    1.000000e-03	2.345e+01	3.456e+02
    ...
    
    Parameters
    ----------
    filepath : Path
        Path to the OldTLWall file
        
    Returns
    -------
    freqs : np.ndarray
        Frequency array [Hz]
    Z : np.ndarray
        Complex impedance array
    """
    # Try to read with different skip_rows values to handle various header formats
    for skip_rows in [1, 0, 2]:
        try:
            data = np.loadtxt(filepath, skiprows=skip_rows)
            if data.ndim == 2 and data.shape[1] == 3:
                freqs = data[:, 0]
                z_real = data[:, 1]
                z_imag = data[:, 2]
                return freqs, z_real + 1j * z_imag
        except (ValueError, IndexError):
            continue
    
    # If all attempts fail, raise error with helpful message
    raise ValueError(
        f"Could not read OldTLWall file {filepath.name}. "
        f"Expected format: 3 columns (Frequency, Re(Z), Im(Z)) with optional header."
    )


def save_impedance_txt(
    filepath: Path,
    freqs: np.ndarray,
    Z: np.ndarray,
    header: str = "Frequency [Hz]\tRe(Z)\tIm(Z)"
) -> None:
    """
    Save impedance to text file.
    
    Parameters
    ----------
    filepath : Path
        Output file path
    freqs : np.ndarray
        Frequency array [Hz]
    Z : np.ndarray
        Complex impedance array
    header : str
        Header line for the file
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    data = np.column_stack([freqs, Z.real, Z.imag])
    np.savetxt(
        filepath,
        data,
        delimiter='\t',
        header=header,
        comments='',
        fmt='%.6e'
    )


def create_comparison_excel(
    filepath: Path,
    freqs: np.ndarray,
    Z_tlwall: np.ndarray,
    Z_ref: np.ndarray,
    impedance_type: ImpedanceType,
    logger: logging_util.logging.Logger
) -> None:
    """
    Create Excel file with comparison between TLWall and reference data.
    
    Includes:
    - Frequency column
    - TLWall Real/Imag
    - Reference Real/Imag
    - Absolute differences
    - Percentage differences (NOTE: Can be misleading for small values!)
    
    IMPORTANT: This file is for MANUAL ANALYSIS. Automatic validation is not
    performed. Percentage differences can be huge for very small values and
    should be interpreted with caution. Use plots for visual comparison.
    
    Parameters
    ----------
    filepath : Path
        Output Excel file path
    freqs : np.ndarray
        Frequency array [Hz]
    Z_tlwall : np.ndarray
        TLWall impedance (complex)
    Z_ref : np.ndarray
        Reference impedance (complex)
    impedance_type : ImpedanceType
        Type of impedance being compared
    logger : Logger
        Logger instance
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Calculate differences
    diff_real = Z_tlwall.real - Z_ref.real
    diff_imag = Z_tlwall.imag - Z_ref.imag
    
    # Calculate percentage differences (can be misleading for small values!)
    with np.errstate(divide='ignore', invalid='ignore'):
        pct_real = (diff_real / np.abs(Z_ref.real)) * 100
        pct_imag = (diff_imag / np.abs(Z_ref.imag)) * 100
        pct_real = np.where(np.isfinite(pct_real), pct_real, 0)
        pct_imag = np.where(np.isfinite(pct_imag), pct_imag, 0)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Frequency [Hz]': freqs,
        f'{impedance_type.name} TLWall Real': Z_tlwall.real,
        f'{impedance_type.name} Reference Real': Z_ref.real,
        f'Diff Real (TLWall-Ref)': diff_real,
        f'Diff Real [%]': pct_real,
        f'{impedance_type.name} TLWall Imag': Z_tlwall.imag,
        f'{impedance_type.name} Reference Imag': Z_ref.imag,
        f'Diff Imag (TLWall-Ref)': diff_imag,
        f'Diff Imag [%]': pct_imag,
    })
    
    # Save to Excel (with fallback to CSV)
    try:
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Comparison', index=False)
            
            # Add a notes sheet with explanation
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
    """
    Prepare complex impedance data for log-log plotting.
    
    Handles inf, nan, and zero values robustly for matplotlib loglog plots.
    
    Parameters
    ----------
    Z : np.ndarray
        Complex impedance array
        
    Returns
    -------
    Z_real_abs : np.ndarray
        Absolute value of real part, with non-finite values replaced
    Z_imag_abs : np.ndarray
        Absolute value of imaginary part, with non-finite values replaced
    is_valid : bool
        True if data contains at least some valid (finite, non-zero) values
    """
    # Make a copy and replace inf with nan for uniform handling
    Z_clean = np.where(np.isfinite(Z), Z, np.nan)
    
    Z_real_abs = np.abs(Z_clean.real)
    Z_imag_abs = np.abs(Z_clean.imag)
    
    # Check if we have any valid data
    has_valid_real = np.any((Z_real_abs > 0) & np.isfinite(Z_real_abs))
    has_valid_imag = np.any((Z_imag_abs > 0) & np.isfinite(Z_imag_abs))
    
    if not (has_valid_real or has_valid_imag):
        return Z_real_abs, Z_imag_abs, False
    
    # Find minimum non-zero values for replacement
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
    
    # Replace zeros and non-finite values with small positive numbers
    Z_real_abs = np.where(
        (Z_real_abs > 0) & np.isfinite(Z_real_abs), 
        Z_real_abs, 
        min_real
    )
    Z_imag_abs = np.where(
        (Z_imag_abs > 0) & np.isfinite(Z_imag_abs), 
        Z_imag_abs, 
        min_imag
    )
    
    return Z_real_abs, Z_imag_abs, True


def create_comparison_plot(
    filepath: Path,
    freqs_tlwall: np.ndarray,
    Z_tlwall: np.ndarray,
    freqs_ref: np.ndarray,
    Z_ref: np.ndarray,
    impedance_type: ImpedanceType,
    logger: logging_util.logging.Logger,
    ref_label: str = "Reference"
) -> None:
    """
    Create comparison plot between TLWall and reference data.
    
    Parameters
    ----------
    filepath : Path
        Output PNG file path
    freqs_tlwall : np.ndarray
        TLWall frequency array [Hz]
    Z_tlwall : np.ndarray
        TLWall impedance (complex)
    freqs_ref : np.ndarray
        Reference frequency array [Hz]
    Z_ref : np.ndarray
        Reference impedance (complex)
    impedance_type : ImpedanceType
        Type of impedance being plotted
    logger : Logger
        Logger instance
    ref_label : str
        Label for reference data (default: "Reference")
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare data for plotting (handles inf/nan/zero)
    tlwall_real, tlwall_imag, tlwall_valid = _prepare_impedance_for_plot(Z_tlwall)
    ref_real, ref_imag, ref_valid = _prepare_impedance_for_plot(Z_ref)
    
    if not (tlwall_valid or ref_valid):
        logger.warning(f"    All values are inf/nan, skipping plot: {filepath.name}")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Real part
    ax1.loglog(
        freqs_tlwall, tlwall_real,
        'b-', linewidth=2.5, label='PyTLWall', alpha=0.8
    )
    ax1.loglog(
        freqs_ref, ref_real,
        'r--', linewidth=2, label=ref_label, alpha=0.8
    )
    ax1.set_xlabel('Frequency [Hz]', fontsize=14)
    ax1.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Real', fontsize=14)
    ax1.set_title(f'{impedance_type.label} - Real Part Comparison', fontsize=16, fontweight='bold')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.legend(fontsize=12, loc='best')
    ax1.tick_params(labelsize=12)
    
    # Imaginary part
    ax2.loglog(
        freqs_tlwall, tlwall_imag,
        'b-', linewidth=2.5, label='PyTLWall', alpha=0.8
    )
    ax2.loglog(
        freqs_ref, ref_imag,
        'r--', linewidth=2, label=ref_label, alpha=0.8
    )
    ax2.set_xlabel('Frequency [Hz]', fontsize=14)
    ax2.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Imag', fontsize=14)
    ax2.set_title(f'{impedance_type.label} - Imaginary Part Comparison', fontsize=16, fontweight='bold')
    ax2.grid(True, which='both', alpha=0.3)
    ax2.legend(fontsize=12, loc='best')
    ax2.tick_params(labelsize=12)
    
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    
    logger.info(f"    Saved plot: {filepath.name}")


def create_single_plot(
    filepath: Path,
    freqs: np.ndarray,
    Z: np.ndarray,
    impedance_type: ImpedanceType,
    logger: logging_util.logging.Logger
) -> None:
    """
    Create single impedance plot (not comparison).
    
    Parameters
    ----------
    filepath : Path
        Output PNG file path
    freqs : np.ndarray
        Frequency array [Hz]
    Z : np.ndarray
        Complex impedance array
    impedance_type : ImpedanceType
        Type of impedance being plotted
    logger : Logger
        Logger instance
    """
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare data for plotting (handles inf/nan/zero)
    Z_real_abs, Z_imag_abs, is_valid = _prepare_impedance_for_plot(Z)
    
    if not is_valid:
        logger.warning(f"    All values are inf/nan, skipping plot: {filepath.name}")
        return
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
    
    # Real part
    ax1.loglog(freqs, Z_real_abs, 'b-', linewidth=2, alpha=0.8)
    ax1.set_xlabel('Frequency [Hz]', fontsize=14)
    ax1.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Real', fontsize=14)
    ax1.set_title(f'{impedance_type.label} - Real Part', fontsize=16, fontweight='bold')
    ax1.grid(True, which='both', alpha=0.3)
    ax1.tick_params(labelsize=12)
    
    # Imaginary part
    ax2.loglog(freqs, Z_imag_abs, 'b-', linewidth=2, alpha=0.8)
    ax2.set_xlabel('Frequency [Hz]', fontsize=14)
    ax2.set_ylabel(f'{impedance_type.label} [{impedance_type.unit}] - Imag', fontsize=14)
    ax2.set_title(f'{impedance_type.label} - Imaginary Part', fontsize=16, fontweight='bold')
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
    cfg_pattern: Optional[str] = None
) -> List[TestDirectory]:
    """
    Discover test directories in the deep_test folder.
    
    Parameters
    ----------
    base_dir : Path
        Base directory for deep tests (e.g., tests/deep_test)
    subdirs : Optional[List[str]]
        Specific subdirectories to test (None = all)
    cfg_pattern : Optional[str]
        Pattern for config file (e.g., "*Wake2D.cfg", "*OldTLWall.cfg")
        If None, uses the first .cfg file found
        
    Returns
    -------
    test_dirs : List[TestDirectory]
        List of discovered test directories
    """
    test_dirs = []
    
    if not base_dir.exists():
        raise FileNotFoundError(f"Deep test directory not found: {base_dir}")
    
    # Get subdirectories to scan
    if subdirs:
        scan_dirs = [base_dir / subdir for subdir in subdirs]
    else:
        # All subdirectories except 'log'
        scan_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name != 'log']
    
    for test_path in scan_dirs:
        if not test_path.is_dir():
            continue
        
        # Find .cfg file based on pattern
        if cfg_pattern:
            cfg_files = list(test_path.glob(cfg_pattern))
            if not cfg_files:
                print(f"Warning: No .cfg file matching '{cfg_pattern}' found in {test_path.name}, skipping")
                continue
        else:
            # Find any .cfg file
            cfg_files = list(test_path.glob("*.cfg"))
            if not cfg_files:
                continue
        
        if len(cfg_files) > 1:
            # Multiple .cfg files found
            if cfg_pattern:
                print(f"Warning: Multiple .cfg files matching '{cfg_pattern}' in {test_path.name}, using first: {cfg_files[0].name}")
            else:
                print(f"Warning: Multiple .cfg files in {test_path.name}, using first: {cfg_files[0].name}")
                print(f"         Use --cfg-pattern to specify which one to use")
        
        cfg_file = cfg_files[0]
        
        # Create test directory structure
        test_dir = TestDirectory(
            path=test_path,
            name=test_path.name,
            cfg_file=cfg_file,
            output_dir=test_path / DeepTestConfig.OUTPUT_SUBDIR,
            img_dir=test_path / DeepTestConfig.IMG_SUBDIR,
            logs_dir=test_path / DeepTestConfig.LOGS_SUBDIR,
            wake2d_dir=test_path / DeepTestConfig.REFERENCE_SUBDIR,
            oldtlwall_dir=test_path / DeepTestConfig.REFERENCE_SUBDIR2,
        )
        
        test_dirs.append(test_dir)
    
    return test_dirs


# ============================================================================
# TEST EXECUTION
# ============================================================================

def run_single_test(
    test_dir: TestDirectory,
    logger: logging_util.logging.Logger,
    compute_space_charge: bool = True
) -> bool:
    """
    Run a single deep test.
    
    Parameters
    ----------
    test_dir : TestDirectory
        Test directory information
    logger : Logger
        Logger instance
    compute_space_charge : bool
        Whether to compute space charge impedances
        
    Returns
    -------
    success : bool
        True if test completed successfully
    """
    logging_util.log_section_header(logger, f"Running test: {test_dir.name}")
    logger.info(f"Configuration: {test_dir.cfg_file}")
    logger.info(f"Output directory: {test_dir.output_dir}")
    logger.info(f"Image directory: {test_dir.img_dir}")
    logger.info(f"Wake2D directory: {test_dir.wake2d_dir}")
    logger.info("")
    
    try:
        # 1. Load configuration
        logger.info("Loading configuration...")
        cfg = pytlwall.CfgIo(str(test_dir.cfg_file))
        
        boundary_type = cfg.config.get('boundary', 'type', fallback='UNKNOWN')
        logger.info(f"  Boundary type: {boundary_type}")
        
        wall = cfg.read_pytlwall()
        logger.info(f"  Configuration loaded successfully")
        logger.info(f"  Chamber: {wall.chamber.chamber_shape}")
        logger.info(f"  Frequencies: {len(wall.f)} points")
        logger.info(f"  Frequency range: {wall.f[0]:.2e} - {wall.f[-1]:.2e} Hz")
        logger.info("")
        
        # Determine which comparisons to perform based on config file name
        cfg_name = test_dir.cfg_file.stem.lower()
        do_wake2d_comparison = 'wake2d' in cfg_name or 'wake' in cfg_name
        do_oldtlwall_comparison = 'old' in cfg_name or 'oldtlwall' in cfg_name
        
        # If no specific pattern in name, do both comparisons (backward compatible)
        if not do_wake2d_comparison and not do_oldtlwall_comparison:
            do_wake2d_comparison = True
            do_oldtlwall_comparison = True
        
        logger.info(f"Config file: {test_dir.cfg_file.name}")
        logger.info(f"  Will compare with Wake2D: {do_wake2d_comparison}")
        logger.info(f"  Will compare with OldTLWall: {do_oldtlwall_comparison}")
        logger.info("")
        
        # 2. Create output directories
        test_dir.output_dir.mkdir(parents=True, exist_ok=True)
        test_dir.img_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy README to output directory for user guidance
        readme_source = Path(__file__).parent / 'OUTPUT_ANALYSIS_README.md'
        readme_dest = test_dir.output_dir / 'README.md'
        if readme_source.exists():
            import shutil
            shutil.copy2(readme_source, readme_dest)
            logger.info(f"  Copied analysis README to {readme_dest.relative_to(test_dir.path)}")
        
        # 3. Determine which impedance types to process based on available reference files
        impedance_types = get_impedance_types_for_test(test_dir.wake2d_dir)
        logger.info(f"\n  Impedance types to process: {[t.name for t in impedance_types]}")
        
        # 3. Process standard impedances
        logger.info("Computing and comparing impedances...")
        
        for imp_type in impedance_types:
            logger.info(f"\n  Processing {imp_type.name} ({imp_type.label})...")
            
            # Check if result attribute exists
            if not hasattr(wall, imp_type.result_attr):
                logger.warning(f"    Skipping {imp_type.name}: attribute '{imp_type.result_attr}' not available")
                continue
            
            try:
                # Compute impedance
                compute_method = getattr(wall, imp_type.compute_method)
                compute_method()
                Z_tlwall = getattr(wall, imp_type.result_attr)
            except Exception as e:
                logger.error(f"    Failed to compute {imp_type.name}: {e}")
                continue
            
            # Save TLWall output (ALWAYS)
            output_path = test_dir.output_dir / imp_type.output_file
            save_impedance_txt(output_path, wall.f, Z_tlwall)
            logger.info(f"    Saved output: {output_path.name}")
            
            # Create single plot (ALWAYS)
            single_plot_path = test_dir.img_dir / imp_type.plot_file
            create_single_plot(single_plot_path, wall.f, Z_tlwall, imp_type, logger)
            
            # Compare with Wake2D if requested
            if do_wake2d_comparison and imp_type.wake2d_file:
                # Find Wake2D reference file
                if test_dir.wake2d_dir.exists():
                    wake2d_files = list(test_dir.wake2d_dir.glob(imp_type.wake2d_file))
                else:
                    wake2d_files = []
                
                if not wake2d_files:
                    logger.warning(f"    No Wake2D reference file found: {imp_type.wake2d_file}")
                else:
                    if len(wake2d_files) > 1:
                        logger.warning(f"    Multiple Wake2D files found, using first: {wake2d_files[0].name}")
                    
                    wake2d_file = wake2d_files[0]
                    logger.info(f"    Wake2D reference: {wake2d_file.name}")
                    
                    # Load Wake2D data
                    freqs_wake2d, Z_wake2d = read_wake2d_file(wake2d_file)
                    
                    # Check if frequencies match
                    if len(freqs_wake2d) != len(wall.f):
                        logger.warning(
                            f"    Frequency count mismatch: "
                            f"TLWall={len(wall.f)}, Wake2D={len(freqs_wake2d)}"
                        )
                    
                    # Create comparison Excel
                    excel_path = test_dir.output_dir / (
                        DeepTestConfig.COMPARISON_PREFIX + imp_type.excel_file
                    )
                    create_comparison_excel(
                        excel_path, wall.f, Z_tlwall, Z_wake2d, imp_type, logger
                    )
                    
                    # Create comparison plot - WakeVsNew_*.png
                    plot_filename = f"WakeVsNew_{imp_type.name}.png"
                    plot_path = test_dir.img_dir / plot_filename
                    create_comparison_plot(
                        plot_path, wall.f, Z_tlwall, freqs_wake2d, Z_wake2d, 
                        imp_type, logger, ref_label="Wake2D"
                    )
        
        # 3b. Compare with OldTLWall if requested and available
        if do_oldtlwall_comparison and test_dir.oldtlwall_dir.exists():
            logger.info("\n  Comparing with OldTLWall reference data...")
            
            # For OldTLWall, check all possible impedance types
            for imp_type in IMPEDANCE_TYPES:
                # Check if OldTLWall file exists
                oldtlwall_file = test_dir.oldtlwall_dir / imp_type.output_file
                
                if not oldtlwall_file.exists():
                    # Skip silently - not all types may be available
                    continue
                
                # Check if we can get the result attribute
                if not hasattr(wall, imp_type.result_attr):
                    logger.warning(f"    {imp_type.name}: Result attribute '{imp_type.result_attr}' not available")
                    continue
                
                logger.info(f"    Processing {imp_type.name} vs OldTLWall...")
                logger.info(f"      OldTLWall reference: {oldtlwall_file.name}")
                
                # Load OldTLWall data
                try:
                    freqs_old, Z_old = read_oldtlwall_file(oldtlwall_file)
                except Exception as e:
                    logger.error(f"      Failed to read OldTLWall file: {e}")
                    continue
                
                # Get PyTLWall data (may need to compute first)
                try:
                    # Ensure computation is done
                    if hasattr(wall, imp_type.compute_method):
                        compute_method = getattr(wall, imp_type.compute_method)
                        compute_method()
                    Z_tlwall = getattr(wall, imp_type.result_attr)
                except Exception as e:
                    logger.error(f"      Failed to get PyTLWall data for {imp_type.name}: {e}")
                    continue
                
                # Check if frequencies match
                if len(freqs_old) != len(wall.f):
                    logger.warning(
                        f"      Frequency count mismatch: "
                        f"PyTLWall={len(wall.f)}, OldTLWall={len(freqs_old)}"
                    )
                
                # Create comparison Excel with OldTLWall
                excel_path = test_dir.output_dir / (
                    DeepTestConfig.COMPARISON_PREFIX2 + imp_type.excel_file
                )
                create_comparison_excel(
                    excel_path, wall.f, Z_tlwall, Z_old, imp_type, logger
                )
                
                # Create comparison plot with OldTLWall - OldVsNew_*.png
                plot_filename = f"OldVsNew_{imp_type.name}.png"
                plot_path = test_dir.img_dir / plot_filename
                create_comparison_plot(
                    plot_path, wall.f, Z_tlwall, freqs_old, Z_old, 
                    imp_type, logger, ref_label="OldTLWall"
                )
        elif do_oldtlwall_comparison:
            logger.info("\n  OldTLWall comparison requested but directory not found, skipping")
        
        # 3c. Compare with OldTLWall for space charge impedances if requested and available
        if do_oldtlwall_comparison and test_dir.oldtlwall_dir.exists() and compute_space_charge:
            logger.info("\n  Comparing space charge impedances with OldTLWall...")
            
            for imp_type in SPACE_CHARGE_TYPES:
                # Check if OldTLWall file exists
                oldtlwall_file = test_dir.oldtlwall_dir / imp_type.output_file
                
                if not oldtlwall_file.exists():
                    continue
                
                logger.info(f"    Processing {imp_type.name} vs OldTLWall...")
                
                # Check if method exists
                if not hasattr(wall, imp_type.compute_method):
                    logger.warning(f"      Method {imp_type.compute_method} not available")
                    continue
                
                # Compute impedance if not already done
                compute_method = getattr(wall, imp_type.compute_method)
                compute_method()
                Z_tlwall = getattr(wall, imp_type.result_attr)
                
                # Load OldTLWall data
                try:
                    freqs_old, Z_old = read_oldtlwall_file(oldtlwall_file)
                except Exception as e:
                    logger.error(f"      Failed to read OldTLWall file: {e}")
                    continue
                
                # Create comparison Excel
                excel_path = test_dir.output_dir / (
                    DeepTestConfig.COMPARISON_PREFIX2 + imp_type.name + ".xlsx"
                )
                create_comparison_excel(
                    excel_path, wall.f, Z_tlwall, Z_old, imp_type, logger
                )
                
                # Create comparison plot - OldVsNew_*.png
                plot_filename = f"OldVsNew_{imp_type.name}.png"
                plot_path = test_dir.img_dir / plot_filename
                create_comparison_plot(
                    plot_path, wall.f, Z_tlwall, freqs_old, Z_old, 
                    imp_type, logger, ref_label="OldTLWall"
                )
        
        # 4. Process space charge impedances (if requested)
        if compute_space_charge:
            logger.info("\n  Computing space charge impedances...")
            
            for imp_type in SPACE_CHARGE_TYPES:
                logger.info(f"    Processing {imp_type.name}...")
                
                # Check if method exists
                if not hasattr(wall, imp_type.compute_method):
                    logger.warning(f"      Method {imp_type.compute_method} not available")
                    continue
                
                # Compute base impedance (triggers calculation if needed)
                compute_method = getattr(wall, imp_type.compute_method)
                compute_method()
                
                # Get the result (may be derived property like ZDipDSC)
                Z = getattr(wall, imp_type.result_attr)
                
                # Save output (ALWAYS)
                output_path = test_dir.output_dir / imp_type.output_file
                save_impedance_txt(output_path, wall.f, Z)
                logger.info(f"      Saved: {output_path.name}")
                
                # Create single plot (ALWAYS)
                plot_filename = f"{imp_type.name}.png"
                plot_path = test_dir.img_dir / plot_filename
                create_single_plot(plot_path, wall.f, Z, imp_type, logger)
        
        logger.info(f"\n✓ Test {test_dir.name} completed successfully")
        
        # 5. Generate ISC comparison summary if Wake2D comparison was done
        if do_wake2d_comparison:
            generate_isc_comparison_summary(test_dir, logger)
        
        return True
        
    except Exception as e:
        logger.error(f"\n✗ Test {test_dir.name} failed with error:")
        logger.error(f"  {type(e).__name__}: {e}")
        import traceback
        logger.error(f"  Traceback:\n{traceback.format_exc()}")
        return False


def generate_isc_comparison_summary(test_dir: TestDirectory, logger) -> None:
    """
    Generate a summary comparing with-ISC vs without-ISC results against Wake2D.
    
    Reads the comparison Excel files and determines which version (with or without ISC)
    gives better agreement with Wake2D reference data.
    
    Parameters
    ----------
    test_dir : TestDirectory
        Test directory configuration
    logger : Logger
        Logger instance
    """
    logger.info("\n" + "="*80)
    logger.info("ISC COMPARISON SUMMARY: Which version matches Wake2D better?")
    logger.info("="*80)
    
    # Define pairs to compare
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
        with_isc_path = test_dir.output_dir / (DeepTestConfig.COMPARISON_PREFIX + with_isc_file)
        without_isc_path = test_dir.output_dir / (DeepTestConfig.COMPARISON_PREFIX + without_isc_file)
        
        # Check if both files exist
        if not with_isc_path.exists() or not without_isc_path.exists():
            continue
        
        try:
            # Read Excel files
            df_with = pd.read_excel(with_isc_path, sheet_name='Comparison')
            df_without = pd.read_excel(without_isc_path, sheet_name='Comparison')
            
            # Calculate mean absolute percentage difference for Real and Imag parts
            # Use median to be more robust to outliers
            with_isc_real_diff = np.nanmedian(np.abs(df_with['Diff Real [%]'].values))
            with_isc_imag_diff = np.nanmedian(np.abs(df_with['Diff Imag [%]'].values))
            
            without_isc_real_diff = np.nanmedian(np.abs(df_without['Diff Real [%]'].values))
            without_isc_imag_diff = np.nanmedian(np.abs(df_without['Diff Imag [%]'].values))
            
            # Combined score (average of real and imag)
            with_isc_score = (with_isc_real_diff + with_isc_imag_diff) / 2
            without_isc_score = (without_isc_real_diff + without_isc_imag_diff) / 2
            
            # Determine winner
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
                'ratio': ratio
            })
            
        except Exception as e:
            logger.warning(f"  Could not compare {name}: {e}")
            continue
    
    # Print summary table
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
        
        # Save summary to file
        summary_path = test_dir.output_dir / "ISC_comparison_summary.txt"
        with open(summary_path, 'w') as f:
            f.write("ISC COMPARISON SUMMARY\n")
            f.write("=" * 80 + "\n\n")
            f.write("Which version (with or without ISC) matches Wake2D better?\n\n")
            f.write(f"{'Impedance':<16} | {'With ISC Score':<15} | {'Without ISC Score':<18} | {'Better Match':<15}\n")
            f.write("-" * 80 + "\n")
            for r in results:
                f.write(f"{r['name']:<16} | {r['with_isc_score']:>15.2f} | {r['without_isc_score']:>18.2f} | {r['winner']:<15}\n")
            f.write("\n\nScore = median absolute percentage difference (Real + Imag) / 2\n")
            f.write("Lower score = better match with Wake2D\n")
        
        logger.info(f"\n  Summary saved to: {summary_path.name}")
    else:
        logger.info("  No comparison data available for ISC analysis")


def run_deep_tests(
    base_dir: Optional[Path] = None,
    subdirs: Optional[List[str]] = None,
    cfg_pattern: Optional[str] = None,
    verbosity: int = 2,
    compute_space_charge: bool = True
) -> bool:
    """
    Run all deep tests.
    
    Parameters
    ----------
    base_dir : Optional[Path]
        Base directory for deep tests (default: from config)
    subdirs : Optional[List[str]]
        Specific subdirectories to test (None = all)
    cfg_pattern : Optional[str]
        Pattern for config file (e.g., "*Wake2D.cfg", "*OldTLWall.cfg")
        If None, uses the first .cfg file found
    verbosity : int
        Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)
    compute_space_charge : bool
        Whether to compute space charge impedances
        
    Returns
    -------
    success : bool
        True if all tests passed
    """
    if base_dir is None:
        base_dir = DeepTestConfig.DEEP_TEST_DIR
    
    # Discover test directories
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
    
    # Run tests
    results = []
    
    for test_dir in test_dirs:
        # Setup logging for this test
        log_config = logging_util.LogConfig(
            log_dir=test_dir.logs_dir,
            log_basename=f"deep_test_{test_dir.name}",
            verbosity=verbosity,
            add_timestamp=True,
            console_output=True,
        )
        log_path = logging_util.setup_logging(log_config)
        logger = logging_util.get_logger(__name__)
        
        logger.info("=" * 80)
        logger.info(f"PYTLWALL DEEP TEST: {test_dir.name}")
        logger.info("=" * 80)
        logger.info(f"Timestamp: {logging_util.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Log file: {log_path}")
        logger.info("")
        
        # Run test
        success = run_single_test(test_dir, logger, compute_space_charge)
        results.append((test_dir.name, success))
        
        logger.info("\n" + "=" * 80)
        if success:
            logger.info(f"TEST {test_dir.name}: PASSED ✓")
        else:
            logger.info(f"TEST {test_dir.name}: FAILED ✗")
        logger.info("=" * 80)
        logger.info(f"Log saved to: {log_path}\n")
        
        # Close logging handlers for this test
        # Note: logging_util doesn't have close_logging(), handlers are auto-managed
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
    
    # Final summary
    print("\n" + "=" * 80)
    print("DEEP TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, success in results if success)
    failed = len(results) - passed
    
    for name, success in results:
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"  {name}: {status}")
    
    print("\n" + "=" * 80)
    print(f"Total: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\nALL TESTS PASSED ✓")
        print("=" * 80)
        return True
    else:
        print(f"\n{failed} TEST(S) FAILED ✗")
        print("=" * 80)
        return False


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main() -> None:
    """Main entry point for deep test runner."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Deep test runner for PyTLWall",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests with default config files
  python run_tests_deep.py
  
  # Run specific subdirectory with Wake2D config
  python run_tests_deep.py --subdirs newCV --cfg-pattern "*Wake2D.cfg"
  
  # Run specific subdirectory with OldTLWall config
  python run_tests_deep.py --subdirs newCV --cfg-pattern "*OldTLWall.cfg"
        """
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=DeepTestConfig.DEEP_TEST_DIR,
        help="Base directory for deep tests"
    )
    parser.add_argument(
        "--subdirs",
        nargs='+',
        help="Specific subdirectories to test (default: all)"
    )
    parser.add_argument(
        "--cfg-pattern",
        type=str,
        help="Pattern for config file (e.g., '*Wake2D.cfg', '*OldTLWall.cfg'). "
             "If not specified, uses the first .cfg file found."
    )
    parser.add_argument(
        "--verbosity",
        type=int,
        default=DeepTestConfig.VERBOSITY,
        choices=[1, 2, 3],
        help="Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)"
    )
    parser.add_argument(
        "--no-space-charge",
        action="store_true",
        help="Skip space charge impedance calculations"
    )
    
    args = parser.parse_args()
    
    success = run_deep_tests(
        base_dir=args.base_dir,
        subdirs=args.subdirs,
        cfg_pattern=args.cfg_pattern,
        verbosity=args.verbosity,
        compute_space_charge=not args.no_space_charge,
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

