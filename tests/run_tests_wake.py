#!/usr/bin/env python3
"""
Wake Test Runner for PyTLWall.

Scans tests/wake/<case>/ subdirectories and runs each case. Two case types
are recognised, dispatched by the presence of a ``compare.cfg`` file:

1. SINGLE case — exactly one .cfg in the folder (and no compare.cfg):
   the cfg is executed and the wake quantities listed in WAKES_TO_PROCESS
   are computed, plotted (vs Thick / Thin analytical limits) and saved as
   .txt files.

2. COMPARE case — a compare.cfg orchestrates two sub-configs (caseA, caseB).
   Each sub-config is executed as a SINGLE case (with its own output/
   img/ logs/ subtree), and then a third comparison stage overlays the
   two results on the same plots and produces a .txt with the diff. When
   ``[additivity_check] enabled = true`` in compare.cfg, a PASS/FAIL is
   emitted based on max|A - B| / max|A| against the configured threshold.

Each SINGLE case directory ends up with:

    <case>/
    ├── <cfg files>
    ├── output/   ← <wake>.txt, columns: t, calc, Thick, Thin
    ├── img/      ← <wake>_vsThinThick.png
    └── logs/

Each COMPARE case directory ends up with:

    <case>/
    ├── compare.cfg
    ├── caseA.cfg, caseB.cfg
    ├── output/
    │   ├── caseA/  caseB/      ← outputs of each sub-run
    │   └── compare/            ← <wake>_AvsB.txt and additivity_check.txt
    ├── img/
    │   ├── caseA/  caseB/
    │   └── compare/            ← <wake>_AvsB.png
    └── logs/

USAGE
-----
    python tests/run_tests_wake.py
    python tests/run_tests_wake.py --subdirs single_cw_boundary_pec
    python tests/run_tests_wake.py --verbosity 3
"""

from __future__ import annotations

import os
import sys
import configparser
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

# Allow imports when running from tests/ or repo root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import matplotlib.pyplot as plt

import pytlwall
from pytlwall import logging_util
import pytlwall.plot_util as plot


# ============================================================================
# CONFIGURATION
# ============================================================================

class WakeTestConfig:
    """Configuration for wake test execution."""

    WAKE_TEST_DIR: Path = Path("tests/wake")
    VERBOSITY: int = 2

    OUTPUT_SUBDIR: str = "output"
    IMG_SUBDIR: str = "img"
    LOGS_SUBDIR: str = "logs"

    COMPARE_CFG_NAME: str = "compare.cfg"
    COMPARE_SUBDIR: str = "compare"  # under output/ and img/

    DEFAULT_ADDITIVITY_THRESHOLD: float = 1e-9


# ============================================================================
# WAKE QUANTITIES — edit WAKES_TO_PROCESS to enable / disable
# ============================================================================

@dataclass
class WakeQuantity:
    name: str
    label: str
    unit: str
    calc_attr: str
    thick_attr: str
    thin_attr: str
    wake_type: str        # "WL" or "WT"
    calc_label: str
    thick_label: str
    thin_label: str


_ALL_WAKES: Dict[str, WakeQuantity] = {
    "WLong": WakeQuantity(
        name="WLong", label="Longitudinal wake (resistive)",
        unit="V/C",
        calc_attr="WLong",
        thick_attr="WLongThick", thin_attr="WLongThin",
        wake_type="WL",
        calc_label="TLWallWake — WLong",
        thick_label="Thick-wall limit — WLongThick",
        thin_label="Thin-wall limit — WLongThin",
    ),
    "WLong_base": WakeQuantity(
        name="WLong_base", label="Longitudinal wake (reactive base)",
        unit="V/C",
        calc_attr="WLong_base",
        thick_attr="WLongThick", thin_attr="WLongThin",
        wake_type="WL",
        calc_label="TLWallWake — WLong_base",
        thick_label="Thick-wall limit — WLongThick",
        thin_label="Thin-wall limit — WLongThin",
    ),
    "WTrans": WakeQuantity(
        name="WTrans", label="Transverse wake (bypass)",
        unit="V/C/m",
        calc_attr="WTrans_Bypass",
        thick_attr="WTransThick", thin_attr="WTransThin",
        wake_type="WT",
        calc_label="TLWallWake — WTrans_Bypass",
        thick_label="Thick-wall limit — WTransThick",
        thin_label="Thin-wall limit — WTransThin",
    ),
    "WTrans_base": WakeQuantity(
        name="WTrans_base", label="Transverse wake (reactive base)",
        unit="V/C/m",
        calc_attr="WTrans_base",
        thick_attr="WTransThick", thin_attr="WTransThin",
        wake_type="WT",
        calc_label="TLWallWake — WTrans_base",
        thick_label="Thick-wall limit — WTransThick",
        thin_label="Thin-wall limit — WTransThin",
    ),
}

# Edit this list to enable / disable wake quantities globally.
WAKES_TO_PROCESS: List[str] = ["WLong", "WLong_base", "WTrans", "WTrans_base"]


def _selected_wakes() -> List[WakeQuantity]:
    out = []
    for name in WAKES_TO_PROCESS:
        if name not in _ALL_WAKES:
            raise ValueError(
                f"Unknown wake quantity {name!r} in WAKES_TO_PROCESS. "
                f"Allowed: {list(_ALL_WAKES.keys())}"
            )
        out.append(_ALL_WAKES[name])
    return out


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SingleRunResult:
    times_s: np.ndarray
    wakes: Dict[str, np.ndarray]
    thick: Dict[str, np.ndarray]
    thin: Dict[str, np.ndarray]
    sigma_eff: float
    thick_eff: float
    summary: str


@dataclass
class WakeCaseDirectory:
    path: Path
    name: str
    output_dir: Path
    img_dir: Path
    logs_dir: Path
    mode: str                           # "single" or "compare"
    cfg_file: Optional[Path] = None     # single mode
    compare_cfg: Optional[Path] = None  # compare mode
    caseA_cfg: Optional[Path] = None
    caseB_cfg: Optional[Path] = None
    labelA: str = "caseA"
    labelB: str = "caseB"
    description: str = ""
    additivity_enabled: bool = False
    additivity_threshold: float = WakeTestConfig.DEFAULT_ADDITIVITY_THRESHOLD


# ============================================================================
# I/O HELPERS
# ============================================================================

def save_wake_txt(
    filepath: Path,
    times_s: np.ndarray,
    calc: np.ndarray,
    thick: np.ndarray,
    thin: np.ndarray,
    calc_name: str,
    thick_name: str,
    thin_name: str,
) -> None:
    """Single-case wake txt: t, calc, thick, thin."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    header = "\t".join(["t [s]", calc_name, thick_name, thin_name])
    data = np.column_stack([times_s, calc, thick, thin])
    np.savetxt(filepath, data, header=header, comments="", delimiter="\t")


def save_compare_txt(
    filepath: Path,
    times_s: np.ndarray,
    A: np.ndarray,
    B: np.ndarray,
    labelA: str,
    labelB: str,
) -> None:
    """Compare txt: t, A, B, A-B, |A-B|/max|A|."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    diff = A - B
    maxA = float(np.max(np.abs(A)))
    with np.errstate(divide='ignore', invalid='ignore'):
        rel = np.where(maxA > 0, np.abs(diff) / maxA, 0.0)
    header = "\t".join([
        "t [s]", f"A:{labelA}", f"B:{labelB}",
        "A-B", "|A-B|/max|A|",
    ])
    data = np.column_stack([times_s, A, B, diff, rel])
    np.savetxt(filepath, data, header=header, comments="", delimiter="\t")


def plot_compare_AvsB(
    filepath: Path,
    times_s: np.ndarray,
    A: np.ndarray,
    B: np.ndarray,
    labelA: str,
    labelB: str,
    title: str,
    ylabel: str,
) -> None:
    """Loglog overlay of A and B (absolute values)."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.loglog(times_s, np.abs(A), 'b-', linewidth=2.5,
              label=labelA, alpha=0.85)
    ax.loglog(times_s, np.abs(B), 'r--', linewidth=2,
              label=labelB, alpha=0.85)
    ax.set_xlabel("t [s]", fontsize=13)
    ax.set_ylabel(ylabel, fontsize=13)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.grid(True, which='both', alpha=0.3)
    ax.legend(fontsize=11, loc='best')
    ax.tick_params(labelsize=11)
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close(fig)


# ============================================================================
# CORE: run a single .cfg and return SingleRunResult
# ============================================================================

def run_wake_cfg(
    cfg_path: Path,
    output_dir: Path,
    img_dir: Path,
    logger,
    case_label: str,
) -> SingleRunResult:
    """
    Execute one wake .cfg and save per-case outputs (txt + png vs Thick/Thin).

    The caller is responsible for the cwd: any relative path inside the
    .cfg is resolved relative to os.getcwd() at the moment of the call.
    """
    logger.info(f"  [{case_label}] Loading configuration: {cfg_path.name}")
    cfg = pytlwall.CfgIo(str(cfg_path))
    result = cfg.read_wall_and_wake()
    wake = result.get('wake')
    if wake is None:
        raise RuntimeError(
            f"[{case_label}] CfgIo.read_wall_and_wake() returned no wake "
            f"object. Ensure CalcWake = wake or both in {cfg_path.name}."
        )
    logger.info(f"  [{case_label}] CalcWake flag: {result.get('calc_flag')}")
    summary = wake.summary()
    logger.info(summary)
    logger.info(f"  [{case_label}] sigma_eff = {wake.sigma_eff:.3e} S/m   "
                f"d_eff = {wake.thick_eff:.3e} m")

    output_dir.mkdir(parents=True, exist_ok=True)
    img_dir.mkdir(parents=True, exist_ok=True)

    times_s = np.asarray(wake.time_s, dtype=float)
    wakes_d: Dict[str, np.ndarray] = {}
    thick_d: Dict[str, np.ndarray] = {}
    thin_d:  Dict[str, np.ndarray] = {}

    for wq in _selected_wakes():
        logger.info(f"\n  [{case_label}] Processing {wq.name} ({wq.label})...")
        W_calc = getattr(wake, wq.calc_attr)
        W_thick = getattr(wake, wq.thick_attr)
        W_thin = getattr(wake, wq.thin_attr)

        wakes_d[wq.name] = np.asarray(W_calc, dtype=float)
        thick_d[wq.name] = np.asarray(W_thick, dtype=float)
        thin_d[wq.name] = np.asarray(W_thin, dtype=float)

        logger.info(f"    {wq.calc_attr} range: "
                    f"[{W_calc.min():.3e}, {W_calc.max():.3e}]")

        # txt
        txt_path = output_dir / f"{wq.name}.txt"
        save_wake_txt(
            txt_path, times_s,
            wakes_d[wq.name], thick_d[wq.name], thin_d[wq.name],
            wq.calc_attr, wq.thick_attr, wq.thin_attr,
        )
        logger.info(f"    Saved output: {txt_path.name}")

        # plot vs Thick / Thin
        png_name = f"{wq.name}_vsThinThick.png"
        plot.plot_wake_vs_limits(
            t=times_s,
            W_calc=W_calc,
            W_thick=W_thick,
            W_thin=W_thin,
            wake_type=wq.wake_type,
            title=f"{wq.label} vs analytical limits — {case_label}",
            savedir=str(img_dir),
            savename=png_name,
            calc_label=wq.calc_label,
            thick_label=wq.thick_label,
            thin_label=wq.thin_label,
        )
        logger.info(f"    Saved plot:   {png_name}")

    plot.close_all_figures()

    return SingleRunResult(
        times_s=times_s,
        wakes=wakes_d, thick=thick_d, thin=thin_d,
        sigma_eff=float(wake.sigma_eff),
        thick_eff=float(wake.thick_eff),
        summary=summary,
    )


# ============================================================================
# COMPARE MODE
# ============================================================================

def _parse_compare_cfg(compare_cfg_path: Path, case_dir: WakeCaseDirectory) -> None:
    """Populate compare-mode fields on case_dir from compare.cfg."""
    parser = configparser.ConfigParser(delimiters=('=', ':'))
    parser.read(str(compare_cfg_path))

    if not parser.has_section('compare'):
        raise RuntimeError(
            f"{compare_cfg_path}: missing [compare] section."
        )

    caseA_rel = parser.get('compare', 'caseA')
    caseB_rel = parser.get('compare', 'caseB')
    case_dir.caseA_cfg = (compare_cfg_path.parent / caseA_rel).resolve()
    case_dir.caseB_cfg = (compare_cfg_path.parent / caseB_rel).resolve()
    case_dir.labelA = parser.get('compare', 'labelA', fallback='caseA')
    case_dir.labelB = parser.get('compare', 'labelB', fallback='caseB')
    case_dir.description = parser.get('compare', 'description', fallback='')

    if parser.has_section('additivity_check'):
        case_dir.additivity_enabled = parser.getboolean(
            'additivity_check', 'enabled', fallback=False
        )
        case_dir.additivity_threshold = parser.getfloat(
            'additivity_check', 'threshold',
            fallback=WakeTestConfig.DEFAULT_ADDITIVITY_THRESHOLD,
        )
    else:
        case_dir.additivity_enabled = False


def _additivity_metric(A: np.ndarray, B: np.ndarray) -> Tuple[float, float]:
    """Return (max|A-B|, max|A-B|/max|A|)."""
    abs_diff = float(np.max(np.abs(A - B)))
    maxA = float(np.max(np.abs(A)))
    rel = abs_diff / maxA if maxA > 0 else float('inf')
    return abs_diff, rel


def run_compare_case(case_dir: WakeCaseDirectory, logger) -> bool:
    """Execute caseA, caseB, then build the comparison artefacts."""
    logging_util.log_section_header(
        logger, f"COMPARE: {case_dir.name}", char='-', width=70
    )
    logger.info(f"Description: {case_dir.description.strip()}")
    logger.info(f"caseA cfg: {case_dir.caseA_cfg}")
    logger.info(f"caseB cfg: {case_dir.caseB_cfg}")
    logger.info(f"labelA: {case_dir.labelA}")
    logger.info(f"labelB: {case_dir.labelB}")
    logger.info(f"Additivity check: enabled={case_dir.additivity_enabled}, "
                f"threshold={case_dir.additivity_threshold:.1e}")
    logger.info("")

    outA = case_dir.output_dir / "caseA"
    outB = case_dir.output_dir / "caseB"
    outC = case_dir.output_dir / WakeTestConfig.COMPARE_SUBDIR
    imgA = case_dir.img_dir / "caseA"
    imgB = case_dir.img_dir / "caseB"
    imgC = case_dir.img_dir / WakeTestConfig.COMPARE_SUBDIR

    resA = run_wake_cfg(case_dir.caseA_cfg, outA, imgA, logger, "A")
    resB = run_wake_cfg(case_dir.caseB_cfg, outB, imgB, logger, "B")

    # Sanity: shared time grid
    if resA.times_s.shape != resB.times_s.shape or \
            not np.allclose(resA.times_s, resB.times_s):
        logger.error("  caseA and caseB have different time grids; "
                     "cannot build the comparison.")
        return False

    outC.mkdir(parents=True, exist_ok=True)
    imgC.mkdir(parents=True, exist_ok=True)

    additivity_lines: List[str] = []
    overall_pass = True

    for wq in _selected_wakes():
        A = resA.wakes[wq.name]
        B = resB.wakes[wq.name]

        txt_path = outC / f"{wq.name}_AvsB.txt"
        save_compare_txt(
            txt_path, resA.times_s, A, B,
            case_dir.labelA, case_dir.labelB,
        )

        png_path = imgC / f"{wq.name}_AvsB.png"
        plot_compare_AvsB(
            png_path, resA.times_s, A, B,
            labelA=case_dir.labelA, labelB=case_dir.labelB,
            title=f"{wq.label} — {case_dir.name}",
            ylabel=f"|W| [{wq.unit}]",
        )
        logger.info(f"  [compare] {wq.name}: saved {txt_path.name} "
                    f"and {png_path.name}")

        if case_dir.additivity_enabled:
            abs_d, rel_d = _additivity_metric(A, B)
            verdict = "PASS" if rel_d < case_dir.additivity_threshold else "FAIL"
            if verdict == "FAIL":
                overall_pass = False
            line = (f"  {wq.name:<14} max|A-B|={abs_d:.3e}   "
                    f"max|A-B|/max|A|={rel_d:.3e}   -> {verdict}")
            additivity_lines.append(line)

    plot.close_all_figures()

    if case_dir.additivity_enabled:
        logger.info("\n" + "-" * 70)
        logger.info("ADDITIVITY CHECK")
        logger.info("-" * 70)
        logger.info(f"Threshold: {case_dir.additivity_threshold:.1e}")
        for line in additivity_lines:
            logger.info(line)
        logger.info("-" * 70)
        logger.info(f"OVERALL: {'PASS' if overall_pass else 'FAIL'}")
        logger.info("-" * 70)

        report_path = outC / "additivity_check.txt"
        with open(report_path, 'w') as f:
            f.write(f"Additivity check for case '{case_dir.name}'\n")
            f.write(f"Threshold: {case_dir.additivity_threshold:.1e}\n")
            f.write(f"labelA: {case_dir.labelA}\n")
            f.write(f"labelB: {case_dir.labelB}\n")
            f.write("-" * 70 + "\n")
            for line in additivity_lines:
                f.write(line + "\n")
            f.write("-" * 70 + "\n")
            f.write(f"OVERALL: {'PASS' if overall_pass else 'FAIL'}\n")
        logger.info(f"Saved report: {report_path.name}")

    return overall_pass


# ============================================================================
# DISPATCH (single vs compare)
# ============================================================================

def run_case(case_dir: WakeCaseDirectory, logger) -> bool:
    """Run one wake case (auto-dispatch single or compare)."""
    logging_util.log_section_header(
        logger, f"Running wake test: {case_dir.name} (mode={case_dir.mode})"
    )
    logger.info(f"Output directory: {case_dir.output_dir}")
    logger.info(f"Image directory:  {case_dir.img_dir}")

    old_cwd = os.getcwd()
    os.chdir(str(case_dir.path))
    logger.info(f"  Working directory: {case_dir.path}")

    try:
        if case_dir.mode == "single":
            run_wake_cfg(
                case_dir.cfg_file,
                case_dir.output_dir,
                case_dir.img_dir,
                logger,
                case_label=case_dir.name,
            )
            logger.info(f"\nWake test {case_dir.name} completed successfully")
            return True

        elif case_dir.mode == "compare":
            ok = run_compare_case(case_dir, logger)
            if ok:
                logger.info(f"\nCompare test {case_dir.name} "
                            f"completed (additivity OK)")
            else:
                logger.info(f"\nCompare test {case_dir.name} "
                            f"completed (additivity FAIL)")
            return ok

        else:  # pragma: no cover
            logger.error(f"Unknown mode '{case_dir.mode}' for {case_dir.name}")
            return False

    except Exception as exc:
        logger.error(f"\nWake test {case_dir.name} failed:")
        logger.error(f"  {type(exc).__name__}: {exc}")
        import traceback
        logger.error("  Traceback:\n%s", traceback.format_exc())
        return False
    finally:
        os.chdir(old_cwd)


# ============================================================================
# DISCOVERY
# ============================================================================

def discover_wake_directories(
    base_dir: Path,
    subdirs: Optional[List[str]] = None,
) -> List[WakeCaseDirectory]:
    """Discover wake test cases (auto-detect single vs compare)."""
    cases: List[WakeCaseDirectory] = []
    if not base_dir.exists():
        raise FileNotFoundError(f"Wake test directory not found: {base_dir}")

    if subdirs:
        scan = [base_dir / s for s in subdirs]
    else:
        scan = [d for d in base_dir.iterdir() if d.is_dir()]

    for test_path in scan:
        if not test_path.is_dir():
            continue
        test_path = test_path.resolve()

        compare_cfg = test_path / WakeTestConfig.COMPARE_CFG_NAME
        if compare_cfg.is_file():
            case = WakeCaseDirectory(
                path=test_path,
                name=test_path.name,
                output_dir=test_path / WakeTestConfig.OUTPUT_SUBDIR,
                img_dir=test_path / WakeTestConfig.IMG_SUBDIR,
                logs_dir=test_path / WakeTestConfig.LOGS_SUBDIR,
                mode="compare",
                compare_cfg=compare_cfg,
            )
            try:
                _parse_compare_cfg(compare_cfg, case)
            except Exception as exc:
                print(f"Warning: cannot parse {compare_cfg}: {exc}")
                continue
            cases.append(case)
            continue

        # Single mode: pick a .cfg in the folder
        cfg_files = sorted(test_path.glob("*.cfg"))
        if not cfg_files:
            continue
        if len(cfg_files) > 1:
            print(f"Warning: multiple .cfg in {test_path.name} (single mode), "
                  f"using {cfg_files[0].name}")

        cases.append(WakeCaseDirectory(
            path=test_path,
            name=test_path.name,
            output_dir=test_path / WakeTestConfig.OUTPUT_SUBDIR,
            img_dir=test_path / WakeTestConfig.IMG_SUBDIR,
            logs_dir=test_path / WakeTestConfig.LOGS_SUBDIR,
            mode="single",
            cfg_file=cfg_files[0],
        ))

    return cases


# ============================================================================
# TOP-LEVEL ENTRY POINT
# ============================================================================

def run_wake_tests(
    base_dir: Optional[Path] = None,
    subdirs: Optional[List[str]] = None,
    verbosity: int = 2,
) -> bool:
    """Run all (or selected) wake cases. True iff every case passed."""
    if base_dir is None:
        base_dir = WakeTestConfig.WAKE_TEST_DIR

    try:
        cases = discover_wake_directories(base_dir, subdirs)
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return False

    if not cases:
        print(f"No wake test directories found in {base_dir}")
        return False

    print(f"\nDiscovered {len(cases)} wake test cases:")
    for c in cases:
        tag = "compare" if c.mode == "compare" else "single "
        print(f"  [{tag}] {c.name}")
    print()

    results: List[Tuple[str, str, bool]] = []

    for case in cases:
        log_config = logging_util.LogConfig(
            log_dir=case.logs_dir,
            log_basename=f"wake_test_{case.name}",
            verbosity=verbosity,
            add_timestamp=True,
            console_output=True,
        )
        log_path = logging_util.setup_logging(log_config)
        logger = logging_util.get_logger(__name__)

        logger.info("=" * 80)
        logger.info(f"PYTLWALL WAKE TEST: {case.name}  (mode = {case.mode})")
        logger.info("=" * 80)
        logger.info(f"Timestamp: "
                    f"{logging_util.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Log file:  {log_path}")
        logger.info("")

        ok = run_case(case, logger)
        results.append((case.name, case.mode, ok))

        logger.info("\n" + "=" * 80)
        logger.info(f"WAKE TEST {case.name}: {'PASSED' if ok else 'FAILED'}")
        logger.info("=" * 80)
        logger.info(f"Log saved to: {log_path}\n")

        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    print("\n" + "=" * 80)
    print("WAKE TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, _, ok in results if ok)
    failed = len(results) - passed
    for name, mode, ok in results:
        tag = "compare" if mode == "compare" else "single "
        print(f"  [{tag}] {name}: {'PASSED' if ok else 'FAILED'}")
    print("\n" + "=" * 80)
    print(f"Total: {len(results)}   Passed: {passed}   Failed: {failed}")
    if failed == 0:
        print("\nALL WAKE TESTS PASSED")
    else:
        print(f"\n{failed} WAKE TEST(S) FAILED")
    print("=" * 80)
    return failed == 0


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Wake test runner for PyTLWall (single + compare modes).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_tests_wake.py
  python tests/run_tests_wake.py --subdirs single_cw_boundary_pec
  python tests/run_tests_wake.py --subdirs double_cw_cw_boundary_pec
        """,
    )
    parser.add_argument(
        "--base-dir", type=Path, default=WakeTestConfig.WAKE_TEST_DIR,
        help="Base directory for wake tests",
    )
    parser.add_argument(
        "--subdirs", nargs='+',
        help="Specific case subdirectories to test (default: all)",
    )
    parser.add_argument(
        "--verbosity", type=int, default=WakeTestConfig.VERBOSITY,
        choices=[1, 2, 3],
        help="Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)",
    )

    args = parser.parse_args()
    ok = run_wake_tests(
        base_dir=args.base_dir,
        subdirs=args.subdirs,
        verbosity=args.verbosity,
    )
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
