#!/usr/bin/env python3
"""
Backward-compatible entry point for PyTLWall.

Historically, users executed the project via this script:
    python exec_pytlwall.py ...

The preferred way is now:
    python -m pytlwall ...

This module is intentionally a thin wrapper.
"""

from __future__ import annotations

from pytlwall.run_pytlwall import main


if __name__ == "__main__":
    raise SystemExit(main())
