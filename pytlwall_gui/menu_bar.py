""" Menu bar for pytlwall GUI application.

This module provides the MainMenuBar class, which encapsulates the File, View,
and Help menus, together with the pytlwall logo on the right side.
"""

from pathlib import Path
from typing import TYPE_CHECKING, Dict

from PyQt5.QtWidgets import QMenuBar, QLabel, QMessageBox, QAction, QMenu
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

if TYPE_CHECKING:
    # Only for type checkers; at runtime MainWindow imports this module.
    from .main_window import MainWindow


# Import impedance names
try:
    from .impedance_constants import (
        IMPEDANCE_NAMES, 
        MANDATORY_IMPEDANCES, 
        DEFAULT_IMPEDANCES
    )
except ImportError:
    # Fallback if impedance_constants is not available
    IMPEDANCE_NAMES = [
        "ZLong", "ZLongTotal", "ZLongSurf", "ZLongDSC", "ZLongISC",
        "ZTrans", "ZTransTotal", "ZTransSurf", "ZTransDSC", "ZTransISC",
        "ZDipX", "ZDipY", "ZDipXTotal", "ZDipYTotal",
        "ZQuadX", "ZQuadY", "ZQuadXTotal", "ZQuadYTotal",
    ]
    MANDATORY_IMPEDANCES = {"ZLong", "ZTrans"}
    DEFAULT_IMPEDANCES = {
        "ZLong", "ZTrans", "ZLongISC", "ZLongTotal",
        "ZDipX", "ZDipY", "ZQuadX", "ZQuadY",
    }


class MainMenuBar(QMenuBar):
    """Main menu bar for pytlwall GUI.

    This menu bar contains:
    - File menu with configuration actions
    - Chamber menu with single-chamber operations
    - Accelerator menu with multi-chamber operations
    - Help menu with documentation links and About dialog
    """

    def __init__(self, main_window: "MainWindow") -> None:
        """Initialize the menu bar and attach it to the given main window.

        Args:
            main_window: The application's main window instance.
        """
        super().__init__(main_window)
        self._main_window = main_window
        
        # Store impedance actions for accelerator-wide selection
        self._accel_impedance_actions: Dict[str, QAction] = {}

        # File menu
        self.file_menu = self.addMenu("File")
        self._setup_file_menu()

        # Chamber menu
        self.chamber_menu = self.addMenu("Chamber")
        self._setup_chamber_menu()
        
        # Accelerator menu
        self.accelerator_menu = self.addMenu("Accelerator")
        self._setup_accelerator_menu()
        
        # Help menu
        self.help_menu = self.addMenu("Help")
        self._setup_help_menu()

        # Logo on the right side
        logo_label = QLabel(self)
        logo_path = Path(__file__).parent / "logo.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            pixmap = pixmap.scaledToHeight(30, Qt.SmoothTransformation)
            logo_label.setPixmap(pixmap)
            logo_label.setContentsMargins(8, 0, 8, 0)
        self.setCornerWidget(logo_label, Qt.TopRightCorner)

    # ------------------------------------------------------------------
    # File menu
    # ------------------------------------------------------------------
    def _setup_file_menu(self) -> None:
        """Setup File menu actions."""
        # Save chamber configuration (cfg)
        save_action = self.file_menu.addAction("Save Chamber cfg...")
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self._main_window._on_save_config)

        # Save chamber impedance text files
        save_impedance_action = self.file_menu.addAction("Save Chamber impedance...")
        save_impedance_action.triggered.connect(
            self._main_window._on_save_chamber_impedance
        )

        # Save cfg + impedance text files + plots in a single export
        save_complete_action = self.file_menu.addAction("Save Chamber Complete...")
        save_complete_action.triggered.connect(
            self._main_window._on_save_chamber_complete
        )

        self.file_menu.addSeparator()
        
        # Save all chamber configuration files
        save_all_cfg_action = self.file_menu.addAction("Save All cfg...")
        save_all_cfg_action.triggered.connect(
            self._main_window._on_save_all_cfg
        )

        # Save all chamber impedance files
        save_all_imp_action = self.file_menu.addAction("Save All impedances...")
        save_all_imp_action.triggered.connect(
            self._main_window._on_save_all_impedances
        )

        # Save all chamber cfg + impedances + plots
        save_all_complete_action = self.file_menu.addAction("Save All Complete...")
        save_all_complete_action.triggered.connect(
            self._main_window._on_save_all_complete
        )

        self.file_menu.addSeparator()
        
        # Save data table
        save_data_action = self.file_menu.addAction("Save Data...")
        save_data_action.triggered.connect(self._main_window._on_save_data)

        # Save plot
        save_plot_action = self.file_menu.addAction("Save Plot...")
        save_plot_action.triggered.connect(self._main_window._on_save_plot)

        self.file_menu.addSeparator()
        
        # Save View (complete workspace)
        save_view_action = self.file_menu.addAction("Save View...")
        save_view_action.setShortcut("Ctrl+Shift+S")
        save_view_action.triggered.connect(self._main_window._on_save_view)
        
        # Load View
        load_view_action = self.file_menu.addAction("Load View...")
        load_view_action.setShortcut("Ctrl+Shift+O")
        load_view_action.triggered.connect(self._main_window._on_load_view)

        self.file_menu.addSeparator()

        # Exit
        exit_action = self.file_menu.addAction("Exit")
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self._main_window.close)

    # ------------------------------------------------------------------
    # Chamber menu
    # ------------------------------------------------------------------
    def _setup_chamber_menu(self) -> None:
        """Create the Chamber menu with chamber actions and impedance tools."""
        new_action = self.chamber_menu.addAction("New Chamber")
        new_action.setShortcut("Ctrl+N")
        new_action.triggered.connect(self._main_window._add_chamber)

        config_action = self.chamber_menu.addAction("New Chamber with config...")
        config_action.setShortcut("Ctrl+O")
        config_action.triggered.connect(self._main_window._on_open_config)

        duplicate_action = QAction("Duplicate Chamber", self._main_window)
        duplicate_action.setShortcut("Ctrl+D")
        duplicate_action.triggered.connect(
            self._main_window._duplicate_current_chamber
        )
        self.chamber_menu.addAction(duplicate_action)

        self.chamber_menu.addSeparator()

        # Select all impedances
        action = QAction("Select All", self._main_window)
        action.triggered.connect(self._main_window._select_all_impedances)
        self.chamber_menu.addAction(action)

        # Deselect all impedances (mandatory ones remain selected)
        action = QAction("Deselect All", self._main_window)
        action.triggered.connect(self._main_window._deselect_all_impedances)
        self.chamber_menu.addAction(action)

        self.chamber_menu.addSeparator()

        # Calculate impedances for the current chamber
        action = QAction("Calculate", self._main_window)
        action.triggered.connect(
            self._main_window._calculate_impedances_for_current_chamber
        )
        self.chamber_menu.addAction(action)
        self.chamber_menu.addSeparator()

    # ------------------------------------------------------------------
    # Accelerator menu
    # ------------------------------------------------------------------
    def _setup_accelerator_menu(self) -> None:
        """Create the Accelerator menu with load and calculate actions."""
        # Load Accelerator
        load_action = self.accelerator_menu.addAction("Load Accelerator...")
        load_action.triggered.connect(self._main_window._on_load_accelerator)
        
        self.accelerator_menu.addSeparator()
        
        # =================================================================
        # Impedance Selection submenu (applies to ALL chambers)
        # =================================================================
        impedance_menu = self.accelerator_menu.addMenu("Impedance Selection")
        
        # Select All / Deselect All for all chambers
        select_all_action = impedance_menu.addAction("Select All (All Chambers)")
        select_all_action.triggered.connect(self._select_all_impedances_all_chambers)
        
        deselect_all_action = impedance_menu.addAction("Deselect All (All Chambers)")
        deselect_all_action.triggered.connect(self._deselect_all_impedances_all_chambers)
        
        impedance_menu.addSeparator()
        
        # Group impedances by category for better organization
        # ---- Base impedances (mandatory and default) ----
        base_menu = impedance_menu.addMenu("Base Impedances")
        base_impedances = [name for name in IMPEDANCE_NAMES 
                          if "Total" not in name and "DSC" not in name 
                          and "ISC" not in name and "Surf" not in name]
        for name in base_impedances:
            self._add_impedance_checkbox(base_menu, name)
        
        # ---- Total impedances (wall + space charge) ----
        total_menu = impedance_menu.addMenu("Total Impedances (wall + SC)")
        total_impedances = [name for name in IMPEDANCE_NAMES if "Total" in name]
        for name in total_impedances:
            self._add_impedance_checkbox(total_menu, name)
        
        # ---- Surface impedances ----
        surf_menu = impedance_menu.addMenu("Surface Impedances")
        surf_impedances = [name for name in IMPEDANCE_NAMES if "Surf" in name]
        for name in surf_impedances:
            self._add_impedance_checkbox(surf_menu, name)
        
        # ---- Space Charge impedances ----
        sc_menu = impedance_menu.addMenu("Space Charge (DSC/ISC)")
        sc_impedances = [name for name in IMPEDANCE_NAMES if "DSC" in name or "ISC" in name]
        for name in sc_impedances:
            self._add_impedance_checkbox(sc_menu, name)
        
        self.accelerator_menu.addSeparator()
        
        # Calculate (for all accelerator chambers)
        calc_action = self.accelerator_menu.addAction("Calculate All")
        calc_action.triggered.connect(self._main_window._on_calculate_accelerator)

    def _add_impedance_checkbox(self, menu: QMenu, name: str) -> None:
        """Add a checkable action for an impedance type.
        
        Args:
            menu: Parent menu to add the action to
            name: Impedance name (e.g., "ZLongTotal")
        """
        action = QAction(name, self._main_window)
        action.setCheckable(True)
        
        # Mandatory impedances are always checked and disabled
        if name in MANDATORY_IMPEDANCES:
            action.setChecked(True)
            action.setEnabled(False)
            action.setText(f"{name} (mandatory)")
        else:
            # Default based on DEFAULT_IMPEDANCES
            action.setChecked(name in DEFAULT_IMPEDANCES)
            action.triggered.connect(
                lambda checked, n=name: self._on_accel_impedance_toggled(n, checked)
            )
        
        menu.addAction(action)
        self._accel_impedance_actions[name] = action

    def _on_accel_impedance_toggled(self, name: str, checked: bool) -> None:
        """Handle toggling of an impedance for all chambers.
        
        Args:
            name: Impedance name
            checked: New checked state
        """
        # Apply to all chambers
        for chamber in self._main_window.chambers:
            chamber.output_flags[name] = checked
        
        # Update the sidebar tree checkboxes for all chambers
        self._main_window.sidebar.update_all_impedance_checks()

    def _select_all_impedances_all_chambers(self) -> None:
        """Enable all impedance outputs for ALL chambers."""
        for chamber in self._main_window.chambers:
            for name in IMPEDANCE_NAMES:
                chamber.output_flags[name] = True
        
        # Update menu checkboxes
        for name, action in self._accel_impedance_actions.items():
            if name not in MANDATORY_IMPEDANCES:
                action.setChecked(True)
        
        # Update sidebar
        self._main_window.sidebar.update_all_impedance_checks()

    def _deselect_all_impedances_all_chambers(self) -> None:
        """Disable non-mandatory impedance outputs for ALL chambers."""
        for chamber in self._main_window.chambers:
            for name in IMPEDANCE_NAMES:
                if name in MANDATORY_IMPEDANCES:
                    chamber.output_flags[name] = True
                else:
                    chamber.output_flags[name] = False
        
        # Update menu checkboxes
        for name, action in self._accel_impedance_actions.items():
            if name not in MANDATORY_IMPEDANCES:
                action.setChecked(False)
        
        # Update sidebar
        self._main_window.sidebar.update_all_impedance_checks()

    def sync_impedance_menu_from_chambers(self) -> None:
        """Synchronize impedance menu checkboxes with current chamber states.
        
        Call this after loading chambers, changing impedance selections in sidebar,
        or any other operation that modifies chamber output_flags.
        """
        if not self._main_window.chambers:
            # No chambers - reset to defaults
            for name, action in self._accel_impedance_actions.items():
                if name not in MANDATORY_IMPEDANCES:
                    action.setChecked(name in DEFAULT_IMPEDANCES)
            return
        
        # For each impedance, check if it's enabled in ALL chambers
        for name, action in self._accel_impedance_actions.items():
            if name in MANDATORY_IMPEDANCES:
                continue
            
            # Check if enabled in all chambers
            all_enabled = all(
                chamber.output_flags.get(name, name in DEFAULT_IMPEDANCES) 
                for chamber in self._main_window.chambers
            )
            action.setChecked(all_enabled)

    # ------------------------------------------------------------------
    # Help menu
    # ------------------------------------------------------------------
    def _setup_help_menu(self) -> None:
        """Setup Help menu with documentation links and about dialog."""
        import webbrowser

        # Documentation submenu
        docs_menu = self.help_menu.addMenu("Documentation")

        # Main documentation pages
        docs_menu.addAction("Index", lambda: self._open_doc("index.html"))

        # GUI documentation (as a dedicated submenu)
        gui_docs_menu = docs_menu.addMenu("Pytlwall Graphical Interface")
        gui_docs_menu.addAction(
            "Pytlwall interface", lambda: self._open_doc("GUI.html")
        )
        gui_docs_menu.addSeparator()
        gui_docs_menu.addAction(
            "Gui menu bar", lambda: self._open_doc("GUI_MENU_BAR.html")
        )
        gui_docs_menu.addAction(
            "Gui sidebar", lambda: self._open_doc("GUI_SIDEBAR.html")
        )
        gui_docs_menu.addAction(
            "Gui data panel", lambda: self._open_doc("GUI_DATA_PANEL.html")
        )
        gui_docs_menu.addAction(
            "Gui plot panel", lambda: self._open_doc("GUI_PLOT_PANEL.html")
        )
        gui_docs_menu.addAction(
            "Gui view IO", lambda: self._open_doc("GUI_VIEW_IO.html")
        )

        docs_menu.addAction("README", lambda: self._open_doc("README.html"))
        docs_menu.addAction("Installation", lambda: self._open_doc("INSTALLATION.html"))
        docs_menu.addSeparator()

        # API Reference submenu
        api_menu = docs_menu.addMenu("API Reference")
        api_menu.addAction("Overview", lambda: self._open_doc("API_REFERENCE.html"))
        api_menu.addAction("Beam", lambda: self._open_doc("API_REFERENCE_BEAM.html"))
        api_menu.addAction("Chamber", lambda: self._open_doc("API_REFERENCE_CHAMBER.html"))
        api_menu.addAction("Layer", lambda: self._open_doc("API_REFERENCE_LAYER.html"))
        api_menu.addAction("Frequencies", lambda: self._open_doc("API_REFERENCE_FREQUENCIES.html"))
        api_menu.addAction("TlWall", lambda: self._open_doc("API_REFERENCE_TLWALL.html"))
        api_menu.addAction("CfgIo", lambda: self._open_doc("API_REFERENCE_CFGIO.html"))
        api_menu.addAction("Multiple Chamber", lambda: self._open_doc("API_REFERENCE_MULTIPLE.html"))

        # Examples submenu
        examples_menu = docs_menu.addMenu("Examples")
        examples_menu.addAction("Overview", lambda: self._open_doc("EXAMPLES.html"))
        examples_menu.addAction("README", lambda: self._open_doc("EXAMPLES_README.html"))
        examples_menu.addAction("Beam", lambda: self._open_doc("EXAMPLES_BEAM.html"))
        examples_menu.addAction("Chamber", lambda: self._open_doc("EXAMPLES_CHAMBER.html"))
        examples_menu.addAction("Layer", lambda: self._open_doc("EXAMPLES_LAYER.html"))
        examples_menu.addAction("Frequencies", lambda: self._open_doc("EXAMPLES_FREQUENCIES.html"))
        examples_menu.addAction("TlWall", lambda: self._open_doc("EXAMPLES_TLWALL.html"))
        examples_menu.addAction("Multiple Chamber", lambda: self._open_doc("EXAMPLES_MULTIPLE.html"))
        examples_menu.addAction("Logging", lambda: self._open_doc("EXAMPLES_LOGGING.html"))

        docs_menu.addSeparator()

        # Reference pages
        docs_menu.addAction(
            "Chamber Shapes Reference",
            lambda: self._open_doc("CHAMBER_SHAPES_REFERENCE.html"),
        )
        docs_menu.addAction(
            "Multiple Chamber README",
            lambda: self._open_doc("README_MULTIPLE_CHAMBER.html"),
        )

        self.help_menu.addSeparator()

        # About action
        about_action = self.help_menu.addAction("About pytlwall GUI")
        about_action.triggered.connect(self._show_about_dialog)

    def _open_doc(self, filename: str) -> None:
        """Open a documentation file in the default web browser.

        Args:
            filename: Name of the HTML file in doc/html directory.
        """
        import webbrowser

        # Try to find documentation directory
        doc_paths = [
            Path(__file__).parent.parent / "doc" / "html" / filename,
            Path(__file__).parent / "doc" / "html" / filename,
            Path.cwd() / "doc" / "html" / filename,
        ]
        for doc_path in doc_paths:
            if doc_path.exists():
                webbrowser.open(doc_path.as_uri())
                return

        # Documentation not found
        QMessageBox.warning(
            self._main_window,
            "Documentation Not Found",
            (
                "Could not find documentation file:\n"
                f"{filename}\n\n"
                "Please ensure the 'doc/html' directory is present."
            ),
        )

    def _show_about_dialog(self) -> None:
        """Show the About dialog."""
        about_text = """
**Version:** 1.0.0

Graphical User Interface for pytlwall - Python Transmission Line Wall Impedance Calculator.

**Authors:**

Tatiana Rijoff, Carlo Zannini

**Institution:**

CERN - European Organization for Nuclear Research

pytlwall calculates resistive wall impedance for particle accelerator vacuum chambers with multi-layer structures.
"""
        QMessageBox.about(self._main_window, "About pytlwall GUI", about_text)
