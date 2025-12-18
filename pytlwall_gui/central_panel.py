"""
Central panel widget for pytlwall GUI.

This module provides the CentralPanel widget that displays data tables
and plots for the calculated impedances.

Authors: Tatiana Rijoff
Date: December 2025
"""

from typing import Optional

from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout

from .data_panel import DataPanel
from .plot_panel import PlotPanel

class CentralPanel(QWidget):
    """
    Central panel widget with tabs for data display and plotting.
    
    The central panel contains:
    - Data tab: For displaying numerical results in tables
    - Plot tab: For visualizing impedance results
    
    Attributes:
        tabs: QTabWidget containing the data and plot tabs
        data_tab: Widget for tabular data display
        plot_tab: Widget for graphical plotting
    """
    def __init__(self, parent: Optional[QWidget] = None, main_window: Optional["MainWindow"] = None):
        super().__init__(parent)
        self._main_window = main_window

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)

        # Data tab: legacy DataPanel
        self.data_panel = DataPanel(self)
        self.tabs.addTab(self.data_panel, "Data")

        # Plot tab: use PlotPanel
        self.plot_panel = PlotPanel(self)
        self.tabs.addTab(self.plot_panel, "Plot")
        
    def _setup_plot_tab(self) -> None:
        """
        Setup the Plot tab layout.
        
        This is a placeholder for future implementation with matplotlib/pyqtgraph.
        """
        layout = QVBoxLayout(self.plot_tab)
        layout.setContentsMargins(4, 4, 4, 4)
        # TODO: Add plotting widget (matplotlib or pyqtgraph)
