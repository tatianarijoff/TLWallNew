#!/usr/bin/env python3
"""
Console runner for PyTLWall.

This module contains the implementation for legacy CLI options:
- No arguments: print welcome + help
- -a <cfg_file>: batch run from configurator file
- -i: interactive text UI
- -g: (reserved) graphical UI (use `python -m pytlwall --gui` instead)

It is designed to be imported safely and to expose a reusable `main(argv=None)`.
"""

from __future__ import annotations

import sys
from typing import Sequence

import pytlwall
import pytlwall.shell_interface as shell


def _run_batch(cfg_filename: str) -> int:
    """Run a full computation from a configurator file."""
    cfg = pytlwall.CfgIo(cfg_filename)
    cfg.read_output()
    cfg.calc_wall()
    cfg.print_wall()
    cfg.plot_wall()
    return 0


def _run_interactive() -> int:
    """Run the interactive console interface."""
    choice = ""
    shell.welcome_message()
    myconfig = pytlwall.CfgIo()

    # Variables are defined dynamically based on user choices.
    # We keep the same behavior as the legacy script.
    while choice.upper() != "X" and choice.lower() != "exit":
        if (
            "chamber" in locals()
            and "beam" in locals()
            and "freq" in locals()
            and "wall" not in locals()
        ):
            if len(chamber.layers) > 0:
                wall = pytlwall.TlWall(chamber, beam, freq)

        shell.menu0_pytlwall()
        if "wall" in locals():
            shell.menu1_pytlwall()
        if "chamber" in locals() and "beam" in locals() and "freq" in locals():
            shell.menu2_pytlwall()
        shell.menuX_pytlwall()

        choice = input("your choice: ").strip()

        if choice.lower() == "chamber":
            chamber = shell.chamber_interface()
            myconfig.save_chamber(chamber)
            if len(chamber.layers) > 0:
                myconfig.save_layer(chamber.layers)
            else:
                print("Layer REQUIRED")

        elif choice.lower() == "beam":
            beam = shell.beam_interface()
            myconfig.save_beam(beam)

        elif choice.lower() == "freq":
            freq = shell.freq_interface()
            myconfig.save_freq(freq)

        elif choice.lower() == "config":
            cfg_name = input("Digit the configurator filename     ").strip()
            res = myconfig.read_pytlwall(cfg_name)
            if res is not None:
                wall = res
                chamber = wall.chamber
                beam = wall.beam
                freq = wall.freq

        elif choice.lower() == "calc":
            list_calc = shell.calc_interface()
            myconfig.save_calc(list_calc)
            myconfig.calc_wall()

        elif choice.lower() == "sav":
            file_output = shell.sav_interface(list_calc)
            myconfig.file_output = file_output
            myconfig.print_wall()

        elif choice.lower() == "plot":
            img_output = shell.plot_interface(list_calc)
            myconfig.img_output = img_output
            myconfig.plot_wall()

        elif choice.lower() == "sav_conf":
            cfg_name = input("Digit the configurator filename     ").strip()
            with open(cfg_name, "w", encoding="utf-8") as f_out:
                myconfig.config.write(f_out)

        elif choice.upper() == "X" or choice.lower() == "exit":
            print("Goodbye")

        else:
            print("Wrong choice, try again")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """
    Entry point for the console runner.

    Parameters
    ----------
    argv:
        CLI arguments excluding program name. If None, uses sys.argv[1:].

    Returns
    -------
    int
        Exit code.
    """
    if argv is None:
        argv = sys.argv[1:]
    argv = list(argv)

    if len(argv) == 0:
        shell.welcome_message()
        shell.help_pytlwall()
        return 0

    param = argv[0]

    if param == "-a":
        if len(argv) < 2:
            print("Error: '-a' requires a configurator filename.")
            shell.help_pytlwall()
            return 2
        return _run_batch(argv[1])

    if param == "-i":
        return _run_interactive()

    if param == "-g":
        # Keep legacy option for compatibility, but point users to the new entry.
        print("GUI mode: use 'python -m pytlwall --gui'")
        return 0

    shell.help_pytlwall()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
