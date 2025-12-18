#!/usr/bin/env python3
"""
Package entry point for PyTLWall.

This enables:
    python -m pytlwall --gui
    python -m pytlwall -a file.cfg
    python -m pytlwall -i

The GUI lives in a separate package (pytlwall_gui) and is imported only when
requested to keep console usage lightweight.
"""

from __future__ import annotations

import argparse
import sys
from typing import Sequence


def _run_gui() -> int:
    """Launch the GUI application."""
    # Imported lazily to avoid GUI dependencies for CLI users.
    from pytlwall_gui.main import main as gui_main

    gui_main()
    return 0


def _run_console(argv: Sequence[str]) -> int:
    """Run the console/CLI workflow (batch or interactive)."""
    from pytlwall.run_pytlwall import main as console_main

    return int(console_main(list(argv)))


def main(argv: Sequence[str] | None = None) -> int:
    """
    Dispatch PyTLWall execution.

    Parameters
    ----------
    argv:
        Command-line arguments *excluding* the program name. If None, defaults
        to sys.argv[1:].

    Returns
    -------
    int
        Process exit code.
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(prog="pytlwall")
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch the graphical user interface.",
    )

    # Pass through unparsed args to the console runner to preserve legacy CLI:
    # e.g. '-a file.cfg', '-i', etc.
    args, rest = parser.parse_known_args(list(argv))

    if args.gui:
        return _run_gui()

    return _run_console(rest)


if __name__ == "__main__":
    raise SystemExit(main())
