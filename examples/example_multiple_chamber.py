#!/usr/bin/env python3
"""Multiple chamber impedance calculation example.

This example runs a lattice-like calculation with multiple vacuum chamber
elements using :class:`pytlwall.MultipleChamber`.

It is aligned with the current MultipleChamber API:
- load()
- calculate_all()
- plot_totals()
- plot_element(i) (optional)

Run from the repository root:
    python examples/example_multiple_chamber.py
"""

from __future__ import annotations

import sys
from pathlib import Path


# Allow running from a repository checkout without installing the package.
# This makes `python examples/...` work reliably.
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pytlwall import MultipleChamber  # noqa: E402  (import after sys.path tweak)


def main() -> None:
    """Run the multiple chamber example workflow."""
    script_dir = Path(__file__).resolve().parent
    input_dir = script_dir / "ex_multiple"
    output_dir = script_dir / "output_multiple"

    print("=" * 60)
    print("Multiple Chamber Impedance Calculation Example")
    print("=" * 60)
    print(f"Input directory:  {input_dir}")
    print(f"Output directory: {output_dir}")
    print()

    if not input_dir.is_dir():
        raise SystemExit(f"Error: input directory not found: {input_dir}")

    # Minimal required files for this example.
    # The cfg names depend on the aperture types used in apertype2.txt.
    required = [
        "apertype2.txt",
        "b_L_betax_betay.txt",
    ]
    missing = [name for name in required if not (input_dir / name).exists()]
    if missing:
        lines = "\n".join(f"  - {name}" for name in missing)
        raise SystemExit(f"Error: missing required files in {input_dir}:\n{lines}")

    output_dir.mkdir(parents=True, exist_ok=True)

    mc = MultipleChamber(
        apertype_file="apertype2.txt",
        geom_file="b_L_betax_betay.txt",
        input_dir=input_dir,
        out_dir=output_dir,
    )

    # Load inputs (lightweight).
    mc.load()

    # Perform the full calculation for all lattice elements.
    mc.calculate_all()

    # Plot total accumulated impedances (saved under out_dir/total).
    mc.plot_totals(show=False)

    # Optional: plot a few elements on demand.
    # (Files are read from disk; this stays memory-efficient.)
    if mc.n_elements > 0:
        mc.plot_element(0, show=False)

    print("\nDone.")
    print(f"Results written to: {output_dir}")


if __name__ == "__main__":
    main()
