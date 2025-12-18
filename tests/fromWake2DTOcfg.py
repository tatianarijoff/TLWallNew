#!/usr/bin/env python3
"""
Convert Wake2D/IW2D InputData*.txt files to PyTLWall .cfg format.

This script reads the input format used by Wake2D/IW2D and generates
a compatible configuration file for PyTLWall.

Authors: Original by user, corrections by Claude
Date: December 2025

Usage:
    1. Edit the CONFIGURATION section below with your paths
    2. Run: python3 fromWake2DTOcfg.py
    
    Or use command line:
    python3 fromWake2DTOcfg.py input.txt -o output.cfg --main-path path/to/wake2d/
"""

from __future__ import annotations

import argparse
import math
import re
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Optional


# =============================================================================
# CONFIGURATION - Edit these parameters directly here
# =============================================================================

# Set to True to use these parameters, False to use command line arguments
USE_HARDCODED_CONFIG = True

# Input file path (Wake2D/IW2D format)
INPUT_TXT_PATH = "tests/deep_test/Ti_Cer_Cu_Vac/Wake2D/InputDataWLHCvvTitCuVac_4layers18.40mm_some_element.dat"

# Output file path (PyTLWall .cfg format)
# Set to None to auto-generate from input filename
OUTPUT_CFG_PATH = "tests/deep_test/Ti_Cer_Cu_Vac/Ti_Cer_Cu_VacWake2D.cfg"

# Main path for Wake2D reference files
MAIN_PATH = "tests/deep_test/Ti_Cer_Cu_Vac/Wake2D/"

# Beta functions (set to 1.0 for direct comparison with Wake2D)
BETAX = 1.0
BETAY = 1.0

# Test beam shift in meters
TEST_BEAM_SHIFT = 0.001

# =============================================================================
# END OF CONFIGURATION
# =============================================================================


@dataclass
class LayerTxt:
    """Layer data from Wake2D/IW2D input file."""
    rho_ohm_m: float      # DC resistivity [Ohm.m]
    tau_ps: float         # Relaxation time for resistivity [ps]
    epsr: float           # Relative permittivity
    chi_m: float          # Magnetic susceptibility (mu_r - 1)
    mu_relax_mhz: float   # Relaxation frequency of permeability [MHz], can be inf
    thickness_mm: float   # Layer thickness [mm], can be inf


@dataclass
class InputTxt:
    """Complete input data from Wake2D/IW2D file."""
    machine: str
    gamma: float
    pipe_len_m: float
    n_layers_txt: int
    inner_radius_mm: float
    comment: str
    layers: List[LayerTxt]


def _parse_value(s: str) -> str:
    """Strip whitespace from value."""
    return s.strip()


def _parse_float_or_inf(s: str) -> float:
    """Parse float value, handling 'Infinity' strings."""
    s = _parse_value(s)
    if re.fullmatch(r"(?i)inf(inity)?", s):
        return math.inf
    return float(s)


def _radius_str(mm: float) -> str:
    """Format radius for filename: 18.4 -> 18p4mm, 18 -> 18mm."""
    s = f"{mm:.12g}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
        s = s.replace(".", "p")
    return f"{s}mm"


def _sigma_from_rho(rho: float) -> float:
    """Convert resistivity to conductivity."""
    if math.isinf(rho) or rho == 0.0:
        return 0.0
    return 1.0 / rho


def _format_float(value: float, default_format: str = "g") -> str:
    """Format float value, handling infinity."""
    if math.isinf(value):
        return "inf"
    return f"{value:{default_format}}"


def read_input_txt(path: Path) -> InputTxt:
    """
    Read Wake2D/IW2D input file.
    
    Parameters
    ----------
    path : Path
        Path to InputData*.txt file
        
    Returns
    -------
    InputTxt
        Parsed input data
    """
    raw = path.read_text(encoding="utf-8", errors="replace").splitlines()
    kv: Dict[str, str] = {}
    
    for line in raw:
        if not line.strip():
            continue
        if "\t" in line:
            k, v = line.split("\t", 1)
        elif ":" in line:
            k, v = line.split(":", 1)
        else:
            continue
        kv[k.strip()] = v.strip()

    machine = kv.get("Machine", kv.get("Machine:", "Unknown"))
    gamma = float(kv.get("Relativistic Gamma", kv.get("Relativistic Gamma:", "7461")))
    pipe_len_m = float(kv.get("Impedance Length in m", kv.get("Impedance Length in m:", "1")))
    n_layers = int(kv.get("Number of layers", kv.get("Number of layers:", "1")))
    inner_radius_mm = float(kv.get("Layer 1 inner radius in mm", kv.get("Layer 1 inner radius in mm:", "10")))
    comment = kv.get("Comments for the output files names", kv.get("Comments for the output files names:", ""))
    
    if comment and not comment.startswith("_"):
        comment = "_" + comment

    layers: List[LayerTxt] = []
    for i in range(1, n_layers + 1):
        # Try both formats (with and without colon)
        def get_layer_param(param_name: str) -> str:
            key1 = f"Layer {i} {param_name}"
            key2 = f"Layer {i} {param_name}:"
            return kv.get(key1, kv.get(key2, ""))
        
        rho = _parse_float_or_inf(get_layer_param("DC resistivity (Ohm.m)") or "1e5")
        tau_ps = float(get_layer_param("relaxation time for resistivity (ps)") or "0")
        epsr = float(get_layer_param("real part of dielectric constant") or "1")
        chi_m = float(get_layer_param("magnetic susceptibility") or "0")
        mu_relax = _parse_float_or_inf(get_layer_param("relaxation frequency of permeability (MHz)") or "Infinity")
        thick = _parse_float_or_inf(get_layer_param("thickness in mm") or "Infinity")
        
        layers.append(LayerTxt(rho, tau_ps, epsr, chi_m, mu_relax, thick))

    return InputTxt(
        machine=machine,
        gamma=gamma,
        pipe_len_m=pipe_len_m,
        n_layers_txt=n_layers,
        inner_radius_mm=inner_radius_mm,
        comment=comment,
        layers=layers,
    )


def build_cfg(
    inp: InputTxt, 
    main_path: str,
    betax: float = 1.0,
    betay: float = 1.0,
    test_beam_shift: float = 0.001
) -> str:
    """
    Build PyTLWall configuration file content.
    
    Parameters
    ----------
    inp : InputTxt
        Parsed input data from Wake2D/IW2D
    main_path : str
        Path to Wake2D reference files
    betax : float
        Horizontal beta function (default 1.0 for Wake2D comparison)
    betay : float
        Vertical beta function (default 1.0 for Wake2D comparison)
    test_beam_shift : float
        Test beam shift in meters
        
    Returns
    -------
    str
        Configuration file content
    """
    r_mm = inp.inner_radius_mm
    r_m = r_mm / 1000.0
    rtag = _radius_str(r_mm)

    component_name = f"{inp.machine}_{inp.n_layers_txt}layers_{rtag}{inp.comment}"

    # Check if last layer is boundary-like (infinite resistivity and thickness)
    last = inp.layers[-1]
    last_is_boundary_like = math.isinf(last.rho_ohm_m) and math.isinf(last.thickness_mm)

    layers_for_cfg = inp.layers[:-1] if last_is_boundary_like else inp.layers
    nbr_layers_cfg = len(layers_for_cfg)

    # File naming following Wake2D convention
    base_tag = f"{inp.machine}_{inp.n_layers_txt}layers{r_mm:.2f}mm{inp.comment}"
    zlong = f"ZlongW{base_tag}.dat"
    zxdip = f"ZxdipW{base_tag}.dat"
    zydip = f"ZydipW{base_tag}.dat"
    zxquad = f"ZxquadW{base_tag}.dat"
    zyquad = f"ZyquadW{base_tag}.dat"

    lines: List[str] = []
    lines += [
        "# PyTLWall Configuration File",
        f"# Machine: {inp.machine}",
        f"# Description: auto-generated from {inp.n_layers_txt}-layer TXT input, {r_mm} mm radius",
        "",
        "",
        "[base_info]",
        f"component_name = {component_name}",
        "chamber_shape = CIRCULAR",
        f"pipe_radius_m = {r_m:.4g}",
        f"pipe_len_m = {inp.pipe_len_m}",
        f"betax = {betax}",
        f"betay = {betay}",
        "",
        "[layers_info]",
        f"nbr_layers = {nbr_layers_cfg}",
        "",
    ]

    # Layer sections
    for j, lay in enumerate(layers_for_cfg):
        # Thickness conversion: mm -> m
        if math.isinf(lay.thickness_mm):
            thick_m = math.inf
            thick_str = "inf"
        else:
            thick_m = lay.thickness_mm / 1000.0
            thick_str = f"{thick_m:g}"
        
        # Conductivity from resistivity
        sigma = _sigma_from_rho(lay.rho_ohm_m)
        sigma_str = f"{sigma:.8e}" if sigma != 0.0 else "0.0"
        
        # Resistivity string for comment
        rho_str = "Infinity" if math.isinf(lay.rho_ohm_m) else f"{lay.rho_ohm_m:g}"
        
        # =====================================================================
        # MAGNETIC PERMEABILITY PARAMETERS - CRITICAL FIX!
        # =====================================================================
        # Wake2D formula: mu(f) = 1 + chi / (1 + j*f/f_mu)
        # PyTLWall formula: mu(f) = 1 + muinf_Hz / (1 + j*f/k_Hz)
        # 
        # Mapping:
        #   muinf_Hz = chi_m (magnetic susceptibility)
        #   k_Hz = mu_relax_mhz * 1e6 (convert MHz to Hz)
        # =====================================================================
        
        muinf_Hz = lay.chi_m  # Magnetic susceptibility (chi = mu_r - 1)
        
        # Convert relaxation frequency from MHz to Hz
        if math.isinf(lay.mu_relax_mhz):
            k_Hz = math.inf
            k_Hz_str = "inf"
        else:
            k_Hz = lay.mu_relax_mhz * 1e6  # MHz -> Hz
            k_Hz_str = f"{k_Hz:g}"
        
        muinf_str = f"{muinf_Hz:g}"
        
        # Relaxation time for conductivity: ps -> s
        tau_s = lay.tau_ps * 1e-12
        tau_str = f"{tau_s:g}"
        
        # Build comment with all relevant info
        comment_parts = [
            f"rho = {rho_str} Ohm.m -> sigma = {sigma_str} S/m",
            f"thickness = {thick_str} m",
            f"epsr = {lay.epsr:g}",
        ]
        if lay.chi_m != 0:
            comment_parts.append(f"chi_m = {lay.chi_m:g}")
        if not math.isinf(lay.mu_relax_mhz):
            comment_parts.append(f"f_mu = {lay.mu_relax_mhz:g} MHz")
        
        lines += [
            f"# Layer {j} (TXT Layer {j+1}): {', '.join(comment_parts)}",
            f"[layer{j}]",
            "type = CW",
            f"thick_m = {thick_str}",
            f"muinf_Hz = {muinf_str}",
            f"k_Hz = {k_Hz_str}",
            f"sigmaDC = {sigma_str}",
            f"epsr = {lay.epsr:g}",
            f"tau = {tau_str}",
            "RQ = 0.0",
            "",
        ]

    # Boundary section
    if last_is_boundary_like:
        boundary_comment = "# Boundary (TXT last layer): Infinity resistivity/thickness -> vacuum-like boundary"
    else:
        boundary_comment = "# Boundary: vacuum-like boundary"

    lines += [
        boundary_comment,
        "[boundary]",
        "type = CW",
        "muinf_Hz = 0",
        "k_Hz = inf",
        "sigmaDC = 0.0",
        "epsr = 1.0",
        "tau = 0.0",
        "RQ = 0.0",
        "",
        "[beam_info]",
        f"test_beam_shift = {test_beam_shift}",
        f"gammarel = {inp.gamma:g}",
        "            ",
        "",
        "[path_info]",
        f"main_path = {main_path}",
        "",
        "[frequency_file]",
        f"filename = {zlong}",
        "separator = whitespace",
        "freq_col = 0",
        "skip_rows = 1",
        "",
        "[test_config]",
        "# Longitudinal",
        f"ref_LongRe_file = {zlong}",
        "ref_LongRe_skip_rows = 1",
        "ref_LongRe_column = 1",
        f"ref_LongIm_file = {zlong}",
        "ref_LongIm_skip_rows = 1",
        "ref_LongIm_column = 2",
        "    ",
        "# Dipolar X",
        f"ref_XDipRe_file = {zxdip}",
        "ref_XDipRe_skip_rows = 1",
        "ref_XDipRe_column = 1",
        f"ref_XDipIm_file = {zxdip}",
        "ref_XDipIm_skip_rows = 1",
        "ref_XDipIm_column = 2",
        "",
        "# Dipolar Y",
        f"ref_YDipRe_file = {zydip}",
        "ref_YDipRe_skip_rows = 1",
        "ref_YDipRe_column = 1",
        f"ref_YDipIm_file = {zydip}",
        "ref_YDipIm_skip_rows = 1",
        "ref_YDipIm_column = 2",
        "",
        "# Quadrupolar X",
        f"ref_XQuadRe_file = {zxquad}",
        "ref_XQuadRe_skip_rows = 1",
        "ref_XQuadRe_column = 1",
        f"ref_XQuadIm_file = {zxquad}",
        "ref_XQuadIm_skip_rows = 1",
        "ref_XQuadIm_column = 2",
        "",
        "# Quadrupolar Y",
        f"ref_YQuadRe_file = {zyquad}",
        "ref_YQuadRe_skip_rows = 1",
        "ref_YQuadRe_column = 1",
        f"ref_YQuadIm_file = {zyquad}",
        "ref_YQuadIm_skip_rows = 1",
        "ref_YQuadIm_column = 2",
        "",
    ]

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    
    if USE_HARDCODED_CONFIG:
        # Use configuration from top of file
        input_path = Path(INPUT_TXT_PATH)
        output_path = Path(OUTPUT_CFG_PATH) if OUTPUT_CFG_PATH else input_path.with_suffix(".cfg")
        main_path = MAIN_PATH
        betax = BETAX
        betay = BETAY
        test_beam_shift = TEST_BEAM_SHIFT
        
        print(f"Using hardcoded configuration:")
        print(f"  Input:  {input_path}")
        print(f"  Output: {output_path}")
        print(f"  Main path: {main_path}")
        print(f"  Beta X/Y: {betax}, {betay}")
        print(f"  Test beam shift: {test_beam_shift}")
        print()
        
    else:
        # Use command line arguments
        ap = argparse.ArgumentParser(
            description="Convert Wake2D/IW2D InputData*.txt to PyTLWall .cfg format."
        )
        ap.add_argument("input_txt", type=Path, help="Path to InputData*.txt")
        ap.add_argument(
            "-o", "--output",
            type=Path,
            default=None,
            help="Output .cfg path (default: same name as input with .cfg)",
        )
        ap.add_argument(
            "--main-path",
            default="tests/deep_test/AutoGenerated/Wake2D/",
            help="Value for [path_info].main_path in the cfg",
        )
        ap.add_argument(
            "--betax",
            type=float,
            default=1.0,
            help="Beta X function (default: 1.0 for Wake2D comparison)",
        )
        ap.add_argument(
            "--betay",
            type=float,
            default=1.0,
            help="Beta Y function (default: 1.0 for Wake2D comparison)",
        )
        ap.add_argument(
            "--test-beam-shift",
            type=float,
            default=0.001,
            help="Test beam shift in meters (default: 0.001)",
        )
        args = ap.parse_args()
        
        input_path = args.input_txt
        output_path = args.output if args.output else input_path.with_suffix(".cfg")
        main_path = args.main_path
        betax = args.betax
        betay = args.betay
        test_beam_shift = args.test_beam_shift

    # Read input file
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}")
        return 1
    
    inp = read_input_txt(input_path)
    
    # Print summary of parsed data
    print(f"Parsed input file: {input_path.name}")
    print(f"  Machine: {inp.machine}")
    print(f"  Gamma: {inp.gamma}")
    print(f"  Pipe length: {inp.pipe_len_m} m")
    print(f"  Inner radius: {inp.inner_radius_mm} mm")
    print(f"  Number of layers: {inp.n_layers_txt}")
    print()
    
    for i, lay in enumerate(inp.layers):
        print(f"  Layer {i+1}:")
        print(f"    Resistivity: {lay.rho_ohm_m} Ohm.m")
        print(f"    Thickness: {lay.thickness_mm} mm")
        print(f"    Epsilon_r: {lay.epsr}")
        print(f"    Chi_m (mu_r-1): {lay.chi_m}")
        print(f"    f_mu: {lay.mu_relax_mhz} MHz")
    print()
    
    # Build configuration
    out_cfg = build_cfg(
        inp, 
        main_path=main_path,
        betax=betax,
        betay=betay,
        test_beam_shift=test_beam_shift
    )
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(out_cfg, encoding="utf-8")
    print(f"Wrote: {output_path}")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
