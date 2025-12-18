#!/usr/bin/env python3
"""Launcher script for PyTlWall GUI."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ~ from QT_interface.main import main
from pytlwall_gui.main import main

if __name__ == "__main__":
    main()
