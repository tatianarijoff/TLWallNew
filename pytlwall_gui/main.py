"""
Entry point for pytlwall GUI application.

This module provides the main() function to start the graphical interface.

Usage:
    python -m pytlwall_gui
    
Or:
    from pytlwall_gui import main
    main()

Authors: Tatiana Rijoff
Date: December 2025
"""

import sys
from PyQt5.QtWidgets import QApplication

from .main_window import MainWindow
from .style import apply_app_style


def main() -> None:
    """
    Start the pytlwall GUI application.
    
    Creates the QApplication, applies styling, and shows the main window.
    """
    app = QApplication(sys.argv)
    
    # Apply custom styling
    apply_app_style(app)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
