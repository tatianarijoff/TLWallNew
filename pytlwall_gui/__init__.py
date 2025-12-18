"""
PyTlWall GUI - Graphical User Interface for pytlwall.

This package provides a PyQt5-based graphical interface for the pytlwall
resistive wall impedance calculation library.

Usage:
    python -m pytlwall_gui

Or:
    from pytlwall_gui import main
    main()

Authors: Tatiana Rijoff
Date: December 2025
"""

from .main import main
from .main_window import MainWindow
from .menu_bar import MainMenuBar
from .sidebar import SideBar
from .central_panel import CentralPanel
from .data_panel import DataPanel
from .plot_panel import PlotPanel
from .chamber_data import (
    ChamberData,
    LayerData,
    BoundaryData,
    FrequencyData,
    BeamData,
    BaseInfoData,
)

__version__ = "1.0.0"

__all__ = [
    "MainWindow",
    "MainMenuBar",
    "SideBar",
    "CentralPanel",
    "DataPanel",
    "PlotPanel",
    "ChamberData",
    "LayerData",
    "BoundaryData",
    "FrequencyData",
    "BeamData",
    "BaseInfoData",
    "main",
]
