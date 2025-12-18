"""
Application styling for pytlwall GUI.

This module provides functions to apply consistent styling across the
application using QPalette and stylesheets.

The color scheme is inspired by the pytlwall logo with a professional
light theme.

Authors: Tatiana Rijoff
Date: December 2025
"""

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor


def apply_app_style(app: QApplication) -> None:
    """
    Apply the application-wide color palette and stylesheet.
    
    This function sets up:
    - A light color palette with bluish tones
    - Accent colors from the pytlwall logo (soft green/blue)
    - Consistent styling for all major widgets
    
    Args:
        app: The QApplication instance to style.
    """
    palette = QPalette()
    
    # Base colors - slightly darker light theme
    background = QColor("#e4ebf3")   # Light bluish background
    window = QColor("#f7f9fc")       # Panel/window background
    text = QColor("#20252b")         # Dark text
    disabled_text = QColor("#8a94a3")
    
    # Accent colors from logo (soft green/blue)
    highlight = QColor("#4b8f82")    # Selected items, focus
    highlighted_text = QColor("#ffffff")
    
    # Window and base colors
    palette.setColor(QPalette.Window, window)
    palette.setColor(QPalette.WindowText, text)
    palette.setColor(QPalette.Base, background)
    palette.setColor(QPalette.AlternateBase, window)
    palette.setColor(QPalette.Text, text)
    palette.setColor(QPalette.ToolTipBase, window)
    palette.setColor(QPalette.ToolTipText, text)
    
    # Button colors
    palette.setColor(QPalette.Button, window)
    palette.setColor(QPalette.ButtonText, text)
    
    # Highlight colors
    palette.setColor(QPalette.Highlight, highlight)
    palette.setColor(QPalette.HighlightedText, highlighted_text)
    
    # Disabled state colors
    palette.setColor(QPalette.Disabled, QPalette.Text, disabled_text)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, disabled_text)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text)
    
    app.setPalette(palette)
    
    # Global stylesheet for specific widget styling
    app.setStyleSheet(_get_stylesheet())


def _get_stylesheet() -> str:
    """
    Get the application stylesheet.
    
    Returns:
        CSS-like stylesheet string for Qt widgets.
    """
    return """
        QMainWindow {
            background-color: #e4ebf3;
        }

        QMenuBar {
            background-color: #d1deec;
            border-bottom: 1px solid #b5c5d8;
        }
        QMenuBar::item {
            padding: 4px 10px;
            background: transparent;
        }
        QMenuBar::item:selected {
            background: #bfcfe3;
        }

        QMenu {
            background-color: #f7f9fc;
            border: 1px solid #b5c5d8;
        }
        QMenu::item:selected {
            background-color: #d1deec;
        }

        QStatusBar {
            background-color: #d1deec;
            border-top: 1px solid #b5c5d8;
        }

        QToolButton {
            background-color: transparent;
        }

        QTreeWidget {
            background-color: #ffffff;
            border: 1px solid #c3d0df;
        }

        QTabWidget::pane {
            border: 1px solid #c3d0df;
            background-color: #ffffff;
        }
        QTabBar::tab {
            background: #d1deec;
            border: 1px solid #c3d0df;
            padding: 4px 10px;
        }
        QTabBar::tab:selected {
            background: #ffffff;
        }

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
            border: 1px solid #b2bfd0;
            border-radius: 2px;
            padding: 2px 4px;
            background: #f7f9fc;
        }
        QLineEdit:focus, QComboBox:focus,
        QSpinBox:focus, QDoubleSpinBox:focus {
            border: 1px solid #4b8f82;
        }
        
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            border: 1px solid #b2bfd0;
            selection-background-color: #4b8f82;
            selection-color: #ffffff;
            outline: none;
        }
        QComboBox QAbstractItemView::item {
            min-height: 22px;
            padding: 4px;
            color: #20252b;
        }
        QComboBox QAbstractItemView::item:hover {
            background-color: #d1deec;
            color: #20252b;
        }
        QComboBox QAbstractItemView::item:selected {
            background-color: #4b8f82;
            color: #ffffff;
        }
        
        QPushButton {
            background-color: #4b8f82;
            color: #ffffff;
            border-radius: 3px;
            padding: 4px 10px;
        }
        QPushButton:hover {
            background-color: #437f74;
        }
        QPushButton:disabled {
            background-color: #b2bfd0;
        }

        QScrollArea {
            border: none;
        }

        QLabel {
            color: #20252b;
        }

        CollapsibleSection QToolButton {
            font-weight: bold;
            color: #2a3f5f;
        }
    """
