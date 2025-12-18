#!/usr/bin/env python3
"""Example: Multiple Chamber Impedance Calculation.

This example demonstrates how to use :class:`pytlwall.MultipleChamber` to compute
impedances for multiple lattice elements with different chamber types.

Why this example exists
-----------------------
Historically, different PyTLWall versions exposed different method names to
trigger a full MultipleChamber computation (e.g. ``run()``, ``compute()``,
``calc()``). This script is written to be compatible across those versions by
detecting and calling the first available "runner" method.

Inputs expected in ``examples/ex_multiple/``
-------------------------------------------
- ``apertype2.txt``: list of aperture types for each element
- ``b_L_betax_betay.txt``: geometry and optics data (b, L, betax, betay)
- ``*.cfg``: configuration files for each aperture type (e.g. ``Round.cfg``)

Outputs
-------
Results are written to ``examples/output_multiple/``.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Callable, Iterable, Optional

# Add parent directory to sys.path when running from the repository checkout.
# This lets `python examples/example_multiple_chamber.py` work without install.
sys.path.insert(0, str(Path(__file__).parent.parent))

from pytlwall import MultipleChamber  # noqa: E402  (import after sys.path tweak)


def _find_runner(mc: object) -> tuple[str, Callable[[], object]]:
    """Return the name and callable used to run a MultipleChamber computation.

    The API changed across versions; this helper makes the example robust.
    """
    candidates: Iterable[str] = (
        # Most common names (newer/older):
        "run",
        "compute",
        "calc",
        "calculate",
        "process",
        "execute",
        # Less common fallbacks:
        "run_all",
        "do",
        "solve",
    )

    for name in candidates:
        fn = getattr(mc, name, None)
        if callable(fn):
            return name, fn

    available = [m for m in dir(mc) if not m.startswith("_")]
    msg = (
        "MultipleChamber does not expose a known runner method. "
        "Tried: {cands}.\n"
        "Available public attributes: {avail}"
    ).format(cands=", ".join(candidates), avail=", ".join(available))
    raise AttributeError(msg)


def main() -> None:
    """Run the multiple chamber example."""
    script_dir = Path(__file__).parent
    input_dir = script_dir / "ex_multiple"
    output_dir = script_dir / "output_multiple"

    print("=" * 60)
    print("Multiple Chamber Impedance Calculation Example")
    print("=" * 60)
    print(f"Input directory:  {input_dir}")
    print(f"Output directory: {output_dir}")
    print()

    if not input_dir.is_dir():
        raise SystemExit(
            f"Error: input directory not found: {input_dir}\n"
            "Please ensure the 'ex_multiple' folder exists with required files."
        )

    # Minimal set of files needed to run the example.
    required_files = ["apertype2.txt", "b_L_betax_betay.txt", "Round.cfg"]
    missing = [name for name in required_files if not (input_dir / name).exists()]
    if missing:
        missing_str = "\n".join(f"  - {name}" for name in missing)
        raise SystemExit(
            f"Error: missing required files in {input_dir}:\n{missing_str}"
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    mc = MultipleChamber(
        apertype_file="apertype2.txt",
        geom_file="b_L_betax_betay.txt",
        input_dir=input_dir,
        out_dir=output_dir,
    )

    runner_name, runner_fn = _find_runner(mc)
    print(f"Running MultipleChamber via method: {runner_name}()")
    runner_fn()

    print()
    print("=" * 60)
    print("Calculation complete!")
    print(f"Results saved to: {output_dir}")
    print("=" * 60)

    if output_dir.exists():
        print("\nOutput structure:")
        for item in sorted(output_dir.iterdir()):
            if item.is_dir():
                n_files = len([p for p in item.iterdir() if p.is_file()])
                print(f"  {item.name}/ ({n_files} files)")


if __name__ == "__main__":
    main()
