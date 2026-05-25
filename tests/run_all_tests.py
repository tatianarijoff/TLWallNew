#!/usr/bin/env python3
"""
Master test runner for PyTLWall.

Runs the three families of tests in sequence:

1. Base unit tests in tests/test_*.py (via run_tests_base.run_selected_unittests_with_log).
2. CompareWake2D deep tests in tests/compareWake2D/ (via run_tests_compareW2D.run_compareW2D_tests).
3. Wake deep tests in tests/wake/ (via run_tests_wake.run_wake_tests).

Two exclusion lists at the top of the file let you skip individual
items without modifying anything else.

USAGE:
------
    # Run everything
    python tests/run_all_tests.py

    # Skip the base suite
    python tests/run_all_tests.py --skip base

    # Skip both deep suites
    python tests/run_all_tests.py --skip compareW2D wake

    # Verbosity
    python tests/run_all_tests.py --verbosity 3
"""

from __future__ import annotations

import os
import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Allow imports when run from repo root or from tests/
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

# Local imports — siblings under tests/
from run_tests_base import run_selected_unittests_with_log, TestConfig          # noqa: E402
from run_tests_compareW2D import run_compareW2D_tests, CompareW2DConfig        # noqa: E402
from run_tests_wake import run_wake_tests, WakeTestConfig                      # noqa: E402


# ============================================================================
# EXCLUSION LISTS — edit these to skip individual items
# ============================================================================

# Base unit test files (e.g. "test_multiple_chamber.py") to skip.
# When empty, every test_*.py file under TestConfig.TEST_DIR is run.
EXCLUDE_BASE_TESTS: List[str] = [
    # "test_multiple_chamber.py",
]

# Deep-test case subdirectories to skip.
# Applies to BOTH compareWake2D/ and wake/ (single shared list, per spec).
# A name listed here will be excluded from whichever family contains it.
EXCLUDE_DEEP_DIRS: List[str] = [
    # "NewCV",
    # "pec",
]


# ============================================================================
# HELPERS
# ============================================================================

def _resolve_base_modules(test_dir: Path, exclude: List[str]) -> Optional[List[str]]:
    """
    Return the list of test_*.py module filenames to run, or None to let
    run_tests_base do auto-discovery when nothing is excluded.
    """
    if not exclude:
        return None

    if not test_dir.exists():
        print(f"Warning: base test directory {test_dir} does not exist.")
        return None

    all_files = sorted(p.name for p in test_dir.glob("test_*.py"))
    selected = [f for f in all_files if f not in exclude]

    skipped = [f for f in all_files if f in exclude]
    if skipped:
        print(f"  Excluding base tests: {', '.join(skipped)}")

    return selected if selected else None


def _resolve_deep_subdirs(base_dir: Path, exclude: List[str]) -> Optional[List[str]]:
    """
    Return the list of subdirectory names to run under base_dir, after
    applying EXCLUDE_DEEP_DIRS. Returns None when nothing should be
    excluded, so the runner falls back to its own auto-discovery.
    """
    if not base_dir.exists():
        # Let the underlying runner produce the usual error message
        return None

    all_dirs = sorted(p.name for p in base_dir.iterdir()
                      if p.is_dir() and p.name not in ('logs', 'log'))
    if not exclude:
        return None

    selected = [d for d in all_dirs if d not in exclude]
    skipped = [d for d in all_dirs if d in exclude]
    if skipped:
        print(f"  Excluding {base_dir.name} cases: {', '.join(skipped)}")

    return selected if selected else None


# ============================================================================
# STAGES
# ============================================================================

def run_base_stage(verbosity: int) -> bool:
    """Run the base unit-test suite via run_tests_base helpers."""
    print("\n" + "=" * 80)
    print("STAGE 1/3 — BASE UNIT TESTS")
    print("=" * 80)

    test_dir = Path(TestConfig.TEST_DIR)
    selected = _resolve_base_modules(test_dir, EXCLUDE_BASE_TESTS)

    return run_selected_unittests_with_log(
        test_dir=TestConfig.TEST_DIR,
        logdir=TestConfig.LOG_DIR,
        logfile="run_all_base",
        pattern=TestConfig.PATTERN,
        verbosity=verbosity,
        selected_modules=selected,
    )


def run_compareW2D_stage(verbosity: int, compute_space_charge: bool) -> bool:
    """Run the compareWake2D deep tests."""
    print("\n" + "=" * 80)
    print("STAGE 2/3 — COMPARE-WAKE2D DEEP TESTS")
    print("=" * 80)

    subdirs = _resolve_deep_subdirs(CompareW2DConfig.BASE_DIR, EXCLUDE_DEEP_DIRS)
    return run_compareW2D_tests(
        base_dir=CompareW2DConfig.BASE_DIR,
        subdirs=subdirs,
        cfg_pattern=None,
        verbosity=verbosity,
        compute_space_charge=compute_space_charge,
    )


def run_wake_stage(verbosity: int) -> bool:
    """Run the wake deep tests."""
    print("\n" + "=" * 80)
    print("STAGE 3/3 — WAKE DEEP TESTS")
    print("=" * 80)

    subdirs = _resolve_deep_subdirs(WakeTestConfig.WAKE_TEST_DIR, EXCLUDE_DEEP_DIRS)
    return run_wake_tests(
        base_dir=WakeTestConfig.WAKE_TEST_DIR,
        subdirs=subdirs,
        cfg_pattern=None,
        verbosity=verbosity,
    )


# ============================================================================
# MAIN
# ============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Master test runner: base + compareWake2D + wake.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_all_tests.py
  python tests/run_all_tests.py --skip base
  python tests/run_all_tests.py --skip compareW2D wake
  python tests/run_all_tests.py --verbosity 3 --no-space-charge
        """,
    )
    parser.add_argument(
        "--skip",
        nargs='+',
        default=[],
        choices=['base', 'compareW2D', 'wake'],
        help="Stages to skip entirely.",
    )
    parser.add_argument(
        "--verbosity", type=int, default=2, choices=[1, 2, 3],
        help="Verbosity level (1=WARNING, 2=INFO, 3=DEBUG)",
    )
    parser.add_argument(
        "--no-space-charge", action="store_true",
        help="Skip space charge impedance calculations in compareWake2D stage.",
    )
    args = parser.parse_args()

    skip = set(args.skip)
    stage_results = []

    if 'base' not in skip:
        ok = run_base_stage(args.verbosity)
        stage_results.append(("base", ok))
    else:
        print("Skipping STAGE 1 — base unit tests.")

    if 'compareW2D' not in skip:
        ok = run_compareW2D_stage(args.verbosity, not args.no_space_charge)
        stage_results.append(("compareW2D", ok))
    else:
        print("Skipping STAGE 2 — compareWake2D deep tests.")

    if 'wake' not in skip:
        ok = run_wake_stage(args.verbosity)
        stage_results.append(("wake", ok))
    else:
        print("Skipping STAGE 3 — wake deep tests.")

    # Final summary
    print("\n" + "#" * 80)
    print("# OVERALL SUMMARY")
    print("#" * 80)
    for name, ok in stage_results:
        print(f"  {name:<12} : {'PASSED' if ok else 'FAILED'}")
    all_ok = all(ok for _, ok in stage_results) and bool(stage_results)
    print("#" * 80)
    if all_ok:
        print("# ALL STAGES PASSED")
    else:
        print("# SOME STAGES FAILED")
    print("#" * 80)

    sys.exit(0 if all_ok else 1)


if __name__ == "__main__":
    main()
