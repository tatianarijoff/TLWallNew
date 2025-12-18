"""
Main window for pytlwall GUI application.

This module provides the MainWindow class which serves as the primary
container for the application, managing chambers, menus, and the overall
layout.

Authors: Tatiana Rijoff
Date: December 2025
"""

import logging
import traceback
from datetime import datetime
from typing import List, Optional
from pathlib import Path

import numpy as np

from PyQt5.QtWidgets import (
    QMainWindow,
    QMenuBar,
    QStatusBar,
    QSplitter,
    QWidget,
    QVBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from .sidebar import SideBar
from .central_panel import CentralPanel
from .chamber_data import ChamberData
from .menu_bar import MainMenuBar

from pytlwall.chamber import Chamber
from pytlwall.layer import Layer
from pytlwall.beam import Beam
from pytlwall.frequencies import Frequencies
from pytlwall.tlwall import TlWall

from pytlwall.io_util import save_chamber_impedance
import pytlwall.plot_util as plot_util

from .impedance_constants import IMPEDANCE_NAMES

# Mandatory impedances - ZLong and ZTrans are the primary outputs
MANDATORY_IMPEDANCES = {"ZLong", "ZTrans"}

# =============================================================================
# Logging configuration for pytlwall_interface
# =============================================================================
# Create logger for this module
logger = logging.getLogger("pytlwall_interface")

# Default log directory: inside the package directory (same level as this file)
_DEFAULT_LOG_DIR = Path(__file__).parent / "log"


def get_log_directory() -> Path:
    """
    Get the log directory, creating it if necessary.
    
    Returns:
        Path to the log directory.
    """
    log_dir = _DEFAULT_LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_log_filepath(prefix: str = "pytlwall_gui") -> Path:
    """
    Generate a log file path with timestamp.
    
    Args:
        prefix: Prefix for the log filename.
    
    Returns:
        Path to the log file.
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_dir = get_log_directory()
    return log_dir / f"{prefix}_{timestamp}.log"


def setup_interface_logging(
    log_file: Optional[str] = None,
    log_dir: Optional[str] = None,
    level: int = logging.DEBUG,
    console: bool = True,
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    auto_file: bool = True
) -> logging.Logger:
    """
    Setup logging for pytlwall_interface.
    
    By default, logs are saved to ~/.pytlwall/log/ with DEBUG level,
    and also printed to console with INFO level.
    
    Args:
        log_file: Explicit path to log file. If None and auto_file=True, 
                  a timestamped file is created automatically.
        log_dir: Custom log directory. If None, uses ~/.pytlwall/log/
        level: Base logging level (default: DEBUG).
        console: Whether to also log to console (default: True).
        console_level: Logging level for console output (default: INFO).
        file_level: Logging level for file output (default: DEBUG).
        auto_file: If True and log_file is None, automatically create a 
                   timestamped log file (default: True).
    
    Returns:
        Configured logger instance.
    
    Example:
        >>> from pytlwall_gui.main_window import setup_interface_logging
        >>> # Use defaults (auto file in ~/.pytlwall/log/)
        >>> setup_interface_logging()
        >>> 
        >>> # Custom log file
        >>> setup_interface_logging(log_file="/path/to/my.log")
        >>> 
        >>> # Custom log directory
        >>> setup_interface_logging(log_dir="/path/to/logs/")
        >>>
        >>> # Console only (no file)
        >>> setup_interface_logging(auto_file=False)
    """
    global _DEFAULT_LOG_DIR
    
    # Update default log directory if custom one provided
    if log_dir:
        _DEFAULT_LOG_DIR = Path(log_dir)
    
    logger.setLevel(level)
    logger.handlers.clear()
    
    # Formatter for detailed logging
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s"
    )
    
    # Simpler formatter for console
    console_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%H:%M:%S"
    )
    
    # Console handler
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    # File handler
    actual_log_file = None
    if log_file:
        actual_log_file = Path(log_file)
        # Ensure parent directory exists
        actual_log_file.parent.mkdir(parents=True, exist_ok=True)
    elif auto_file:
        actual_log_file = get_log_filepath()
    
    if actual_log_file:
        file_handler = logging.FileHandler(
            actual_log_file, mode='a', encoding='utf-8'
        )
        file_handler.setLevel(file_level)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)
        logger.info(f"Log file: {actual_log_file}")
    
    logger.info("pytlwall_interface logging initialized")
    return logger


def get_current_log_file() -> Optional[Path]:
    """
    Get the path to the current log file, if any.
    
    Returns:
        Path to the current log file, or None if no file logging is active.
    """
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return Path(handler.baseFilename)
    return None


def cleanup_old_logs(max_files: int = 50, max_days: int = 30) -> int:
    """
    Remove old log files to prevent disk space issues.
    
    Args:
        max_files: Maximum number of log files to keep.
        max_days: Maximum age of log files in days.
    
    Returns:
        Number of files removed.
    """
    from datetime import datetime, timedelta
    
    log_dir = get_log_directory()
    if not log_dir.exists():
        return 0
    
    log_files = sorted(
        log_dir.glob("pytlwall_gui_*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True
    )
    
    removed = 0
    cutoff_time = datetime.now() - timedelta(days=max_days)
    
    for i, log_file in enumerate(log_files):
        should_remove = False
        
        # Remove if exceeds max_files
        if i >= max_files:
            should_remove = True
        
        # Remove if older than max_days
        file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
        if file_time < cutoff_time:
            should_remove = True
        
        if should_remove:
            try:
                log_file.unlink()
                removed += 1
            except OSError:
                pass
    
    if removed:
        logger.debug(f"Cleaned up {removed} old log file(s)")
    
    return removed


# Initialize default logging: console (INFO) + auto file (DEBUG)
if not logger.handlers:
    setup_interface_logging(
        level=logging.DEBUG,
        console=True,
        console_level=logging.INFO,
        file_level=logging.DEBUG,
        auto_file=True
    )
    # Cleanup old logs on startup
    cleanup_old_logs()

    
class MainWindow(QMainWindow):
    """
    Main application window for pytlwall GUI.
    
    The main window contains:
    - A menu bar with File, View, and Help menus
    - A sidebar for chamber selection and configuration
    - A central panel for data display and plotting
    - A status bar for messages
    
    Attributes:
        chambers: List of ChamberData objects representing all chambers
        sidebar: SideBar widget for configuration
        central_panel: CentralPanel widget for display
    """
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the main window.
        
        Args:
            parent: Parent widget (typically None for main window).
        """
        super().__init__(parent)
        
        self.setWindowTitle("pytlwall GUI")
        self.resize(1200, 800)
        
        # Central chambers data storage
        self.chambers: List[ChamberData] = []
        self.impedance_actions = {}  # type: dict[str, QAction]
        
        # Create UI components
        self._create_menu_bar()
        self._create_status_bar()
        self._create_central_layout()
        
        
    
    def _create_menu_bar(self) -> None:
        """Create the main menu bar."""
        menu_bar = MainMenuBar(self)
        self.setMenuBar(menu_bar)
        # Keep references if other methods rely on them
        self.file_menu = menu_bar.file_menu

        self.help_menu = menu_bar.help_menu
    

    def _create_status_bar(self) -> None:
        """Create the status bar."""
        status_bar = QStatusBar(self)
        self.setStatusBar(status_bar)
        status_bar.showMessage("Ready")
    
    def _create_central_layout(self) -> None:
        """Create the main layout with sidebar and central panel."""
        splitter = QSplitter(Qt.Horizontal, self)
        
        # Create sidebar and central panel
        self.sidebar = SideBar(self)
        self.central_panel = CentralPanel(self, main_window=self)
        
        splitter.addWidget(self.sidebar)
        splitter.addWidget(self.central_panel)
        
        # Set stretch factors for resizing behavior
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 4)
        
        # Set initial sizes (sidebar: 280px, central: rest of window)
        # Based on window width of 1200, this gives ~280 sidebar, ~920 central
        splitter.setSizes([280, 920])
        
        # Prevent full collapse
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        
        # Container
        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(splitter)
        
        # Initialize with one chamber
        self._add_chamber()
        
        # Update sidebar with initial chambers
        self.sidebar.set_chambers(self.chambers)
        
        # Connect sidebar signals
        self.sidebar.request_add_chamber.connect(self._add_chamber)
        self.sidebar.request_remove_chamber.connect(self._remove_chamber)
        self.sidebar.chamber_data_changed.connect(self._on_chamber_data_changed)
        
        # Connect data panel drop signal
        self.central_panel.data_panel.impedance_drop_requested.connect(
            self._on_impedance_dropped_to_data
        )
        
        # Connect plot panel drop signal
        self.central_panel.plot_panel.impedance_drop_requested.connect(
            self._on_impedance_dropped_to_plot
        )
        
        self.setCentralWidget(container)
    
    # =========================================================================
    # Chamber Management
    # =========================================================================
    
    def _create_new_chamber(self) -> ChamberData:
        """
        Create a new ChamberData with default values.
        
        Returns:
            New ChamberData instance with unique ID.
        """
        idx = len(self.chambers) + 1
        chamber_id = f"Chamber {idx}"
        return ChamberData.create_default(chamber_id)
    
    def _add_chamber(self) -> None:
        """Add a new chamber and update the sidebar."""
        chamber = self._create_new_chamber()
        self.chambers.append(chamber)
        self.sidebar.set_chambers(self.chambers)
        self.statusBar().showMessage(f"Added {chamber.id}", 3000)
    
    def _remove_chamber(self, index: int) -> None:
        """
        Remove chamber at given index and renumber remaining chambers.
        
        Args:
            index: Index of chamber to remove.
        """
        if 0 <= index < len(self.chambers):
            removed_id = self.chambers[index].id
            self.chambers.pop(index)
            
            # Renumber remaining chambers
            for i, ch in enumerate(self.chambers, start=1):
                ch.id = f"Chamber {i}"
            
            self.sidebar.set_chambers(self.chambers)
            self.statusBar().showMessage(f"Removed {removed_id}", 3000)
    
    def _on_chamber_data_changed(self, index: int, chamber: ChamberData) -> None:
        """Handle updates to a chamber and synchronize related UI state."""
        if 0 <= index < len(self.chambers):
            self.chambers[index] = chamber
            self.statusBar().showMessage(f"Updated {chamber.id}", 2000)
            #self._sync_impedance_menu_from_chamber(chamber)
    
    # ~ def _sync_impedance_menu_from_chamber(self, chamber: ChamberData) -> None:
        # ~ """Update impedance menu actions to reflect the given chamber state."""
        # ~ for key, action in self.impedance_actions.items():
            # ~ if key in chamber.output_flags:
                # ~ action.blockSignals(True)
                # ~ action.setChecked(bool(chamber.output_flags[key]))
                # ~ action.blockSignals(False)
    # =========================================================================
    # Impedance Management
    # =========================================================================

    def _duplicate_current_chamber(self) -> None:
        """Duplicate the currently selected chamber."""
        idx = self.sidebar.get_current_chamber_index()
        if idx < 0 or idx >= len(self.chambers):
            return

        original = self.chambers[idx]
        new_index = len(self.chambers) + 1
        new_id = f"Chamber {new_index}"

        duplicated = ChamberData.duplicate(
            original,
            new_id=new_id,
            component_name_suffix="_copy",
        )

        self.chambers.append(duplicated)
        self.sidebar.set_chambers(self.chambers)
        self.statusBar().showMessage(
            f"Duplicated {original.id} → {duplicated.id}", 3000
        )

    def register_impedance_action(self, key: str, action: "QAction") -> None:
        """Register a menu action associated with an impedance key."""
        self.impedance_actions[key] = action
        action.toggled.connect(
            lambda checked, k=key: self._on_impedance_menu_toggled(k, checked)
        )

    def _get_current_chamber(self) -> Optional[ChamberData]:
        """Return the currently selected chamber, or None if none is selected."""
        idx = self.sidebar.get_current_chamber_index()
        if idx < 0 or idx >= len(self.chambers):
            return None
        return self.chambers[idx]
    
    def _on_impedance_menu_toggled(self, key: str, checked: bool) -> None:
        """Update the current chamber model and sidebar when a menu action is toggled."""
        # Mandatory impedances cannot be deselected
        if key in MANDATORY_IMPEDANCES and not checked:
            # Restore the checked state
            if key in self.impedance_actions:
                self.impedance_actions[key].blockSignals(True)
                self.impedance_actions[key].setChecked(True)
                self.impedance_actions[key].blockSignals(False)
            return
        
        chamber = self._get_current_chamber()
        if chamber is None:
            return
        chamber.output_flags[key] = checked
        self.sidebar.update_impedance_checks_from_model()
    
    def _select_all_impedances(self) -> None:
        """Enable all impedance outputs for the current chamber and update the UI."""
        chamber = self._get_current_chamber()
        if chamber is None:
            return
        for key in IMPEDANCE_NAMES:
            chamber.output_flags[key] = True
        # ~ self._sync_impedance_menu_from_chamber(chamber)
        self.sidebar.update_impedance_checks_from_model()


    def _deselect_all_impedances(self) -> None:
        """Disable all impedance outputs for the current chamber and update the UI."""
        chamber = self._get_current_chamber()
        if chamber is None:
            return
        for key in IMPEDANCE_NAMES:
            
            if key in MANDATORY_IMPEDANCES:
                chamber.output_flags[key] = True
            else:
                chamber.output_flags[key] = False
        self.sidebar.update_impedance_checks_from_model()

    def _on_impedance_dropped_to_data(self, chamber_name: str, impedance_name: str) -> None:
        """
        Handle impedance drop from tree to DataPanel.
        
        Args:
            chamber_name: Name of the source chamber (e.g., "Chamber 1")
            impedance_name: Name of the impedance (e.g., "ZLong", "ZLongRe", "ZLongIm")
                          - If "ZLong": add both Re and Im columns
                          - If "ZLongRe": add only Re column
                          - If "ZLongIm": add only Im column
        """
        # Find the chamber by name
        target_chamber = None
        for ch in self.chambers:
            ch_label = ch.id.split(":")[0].strip()
            if ch_label == chamber_name or ch.id == chamber_name:
                target_chamber = ch
                break
        
        if target_chamber is None:
            QMessageBox.warning(
                self,
                "Chamber Not Found",
                f"Could not find chamber: {chamber_name}"
            )
            return
        
        # Check if impedance results exist
        if not hasattr(target_chamber, 'impedance_results') or not target_chamber.impedance_results:
            QMessageBox.warning(
                self,
                "No Data",
                f"No impedance data calculated for {chamber_name}.\n"
                "Please calculate impedances first using Chamber -> Calculate."
            )
            return
        
        frequencies = target_chamber.impedance_freq
        
        # Determine if this is a specific component (Re/Im) or the parent (both)
        if impedance_name.endswith("Re"):
            # Single component: only Re
            base_name = impedance_name[:-2]
            re_key = impedance_name
            
            if re_key not in target_chamber.impedance_results:
                QMessageBox.warning(
                    self, "Data Not Found",
                    f"Impedance '{re_key}' not found in {chamber_name}."
                )
                return
            
            re_data = target_chamber.impedance_results[re_key]
            self.central_panel.data_panel.add_impedance(
                chamber_name=chamber_name,
                impedance_name=base_name,
                data=re_data,
                frequencies=frequencies,
                component="Re"
            )
            self.statusBar().showMessage(
                f"Added {base_name} Re from {chamber_name} to data table", 3000
            )
            
        elif impedance_name.endswith("Im"):
            # Single component: only Im
            base_name = impedance_name[:-2]
            im_key = impedance_name
            
            if im_key not in target_chamber.impedance_results:
                QMessageBox.warning(
                    self, "Data Not Found",
                    f"Impedance '{im_key}' not found in {chamber_name}."
                )
                return
            
            im_data = target_chamber.impedance_results[im_key]
            self.central_panel.data_panel.add_impedance(
                chamber_name=chamber_name,
                impedance_name=base_name,
                data=im_data,
                frequencies=frequencies,
                component="Im"
            )
            self.statusBar().showMessage(
                f"Added {base_name} Im from {chamber_name} to data table", 3000
            )
            
        else:
            # Parent impedance: add both Re and Im
            base_name = impedance_name
            re_key = f"{base_name}Re"
            im_key = f"{base_name}Im"
            
            if re_key not in target_chamber.impedance_results:
                QMessageBox.warning(
                    self, "Data Not Found",
                    f"Impedance '{base_name}' not found in {chamber_name}."
                )
                return
            
            re_data = target_chamber.impedance_results[re_key]
            im_data = target_chamber.impedance_results.get(im_key, np.zeros_like(re_data))
            complex_data = re_data + 1j * im_data
            
            self.central_panel.data_panel.add_impedance(
                chamber_name=chamber_name,
                impedance_name=base_name,
                data=complex_data,
                frequencies=frequencies,
                component=None  # Add both Re and Im
            )
            self.statusBar().showMessage(
                f"Added {base_name} (Re+Im) from {chamber_name} to data table", 3000
            )

    def _on_impedance_dropped_to_plot(self, chamber_name: str, impedance_name: str) -> None:
        """
        Handle impedance drop from tree to PlotPanel.
        
        Args:
            chamber_name: Name of the source chamber (e.g., "Chamber 1")
            impedance_name: Name of the impedance (e.g., "ZLong", "ZLongRe", "ZLongIm")
                          - If "ZLong": add both Re and Im curves
                          - If "ZLongRe": add only Re curve
                          - If "ZLongIm": add only Im curve
        """
        try:
            logger.debug(f"Drop to plot: chamber='{chamber_name}', impedance='{impedance_name}'")
            
            # Find the chamber by name
            target_chamber = None
            for ch in self.chambers:
                ch_label = ch.id.split(":")[0].strip()
                logger.debug(f"  Checking: ch.id='{ch.id}', ch_label='{ch_label}'")
                if ch_label == chamber_name or ch.id == chamber_name:
                    target_chamber = ch
                    break
            
            if target_chamber is None:
                logger.warning(f"Chamber not found: '{chamber_name}'")
                QMessageBox.warning(
                    self,
                    "Chamber Not Found",
                    f"Could not find chamber: {chamber_name}"
                )
                return
            
            logger.debug(f"Found chamber: {target_chamber.id}")
            
            # Check if impedance results exist
            if not hasattr(target_chamber, 'impedance_results') or not target_chamber.impedance_results:
                logger.warning(f"No impedance_results for chamber: {target_chamber.id}")
                QMessageBox.warning(
                    self,
                    "No Data",
                    f"No impedance data calculated for {chamber_name}.\n"
                    "Please calculate impedances first using Chamber -> Calculate."
                )
                return
            
            frequencies = target_chamber.impedance_freq
            if frequencies is None:
                logger.error(f"impedance_freq is None for chamber: {target_chamber.id}")
                QMessageBox.warning(
                    self,
                    "No Frequency Data",
                    f"No frequency data available for {chamber_name}."
                )
                return
            
            logger.debug(f"Available keys: {list(target_chamber.impedance_results.keys())}")
            
            # Determine if this is a specific component (Re/Im) or the parent (both)
            if impedance_name.endswith("Re"):
                # Single component: only Re
                base_name = impedance_name[:-2]
                re_key = impedance_name
                
                if re_key not in target_chamber.impedance_results:
                    QMessageBox.warning(
                        self, "Data Not Found",
                        f"Impedance '{re_key}' not found in {chamber_name}."
                    )
                    return
                
                data = target_chamber.impedance_results[re_key]
                try:
                    self.central_panel.plot_panel.add_impedance(
                        chamber_name=chamber_name,
                        impedance_name=base_name,
                        data=data,
                        frequencies=frequencies,
                        component="Re"
                    )
                    self.statusBar().showMessage(
                        f"Added {base_name} Re from {chamber_name} to plot", 3000
                    )
                except ValueError as e:
                    if "log-scaled" in str(e):
                        QMessageBox.warning(
                            self,
                            "Plot Warning",
                            f"Cannot plot {base_name} Re with log scale:\n"
                            "Data contains zero or negative values.\n\n"
                            "Try switching to linear scale in the plot options."
                        )
                        logger.warning(f"Log scale error for {base_name} Re: {e}")
                    else:
                        raise
                
            elif impedance_name.endswith("Im"):
                # Single component: only Im
                base_name = impedance_name[:-2]
                im_key = impedance_name
                
                if im_key not in target_chamber.impedance_results:
                    QMessageBox.warning(
                        self, "Data Not Found",
                        f"Impedance '{im_key}' not found in {chamber_name}."
                    )
                    return
                
                data = target_chamber.impedance_results[im_key]
                try:
                    self.central_panel.plot_panel.add_impedance(
                        chamber_name=chamber_name,
                        impedance_name=base_name,
                        data=data,
                        frequencies=frequencies,
                        component="Im"
                    )
                    self.statusBar().showMessage(
                        f"Added {base_name} Im from {chamber_name} to plot", 3000
                    )
                except ValueError as e:
                    if "log-scaled" in str(e):
                        QMessageBox.warning(
                            self,
                            "Plot Warning",
                            f"Cannot plot {base_name} Im with log scale:\n"
                            "Data contains zero or negative values.\n\n"
                            "Try switching to linear scale in the plot options."
                        )
                        logger.warning(f"Log scale error for {base_name} Im: {e}")
                    else:
                        raise
                
            else:
                # Parent impedance: add both Re and Im as separate curves
                base_name = impedance_name
                re_key = f"{base_name}Re"
                im_key = f"{base_name}Im"
                
                if re_key not in target_chamber.impedance_results:
                    QMessageBox.warning(
                        self, "Data Not Found",
                        f"Impedance '{base_name}' not found in {chamber_name}.\n"
                        f"Available: {list(target_chamber.impedance_results.keys())}"
                    )
                    return
                
                # Add Re curve
                re_data = target_chamber.impedance_results[re_key]
                try:
                    self.central_panel.plot_panel.add_impedance(
                        chamber_name=chamber_name,
                        impedance_name=base_name,
                        data=re_data,
                        frequencies=frequencies,
                        component="Re"
                    )
                except ValueError as e:
                    if "log-scaled" in str(e):
                        QMessageBox.warning(
                            self,
                            "Plot Warning",
                            f"Cannot plot {base_name} Re with log scale:\n"
                            "Data contains zero or negative values.\n\n"
                            "Try switching to linear scale in the plot options."
                        )
                        logger.warning(f"Log scale error for {base_name} Re: {e}")
                    else:
                        raise
                
                # Add Im curve if available
                if im_key in target_chamber.impedance_results:
                    im_data = target_chamber.impedance_results[im_key]
                    try:
                        self.central_panel.plot_panel.add_impedance(
                            chamber_name=chamber_name,
                            impedance_name=base_name,
                            data=im_data,
                            frequencies=frequencies,
                            component="Im"
                        )
                    except ValueError as e:
                        if "log-scaled" in str(e):
                            QMessageBox.warning(
                                self,
                                "Plot Warning",
                                f"Cannot plot {base_name} Im with log scale:\n"
                                "Data contains zero or negative values.\n\n"
                                "Try switching to linear scale in the plot options."
                            )
                            logger.warning(f"Log scale error for {base_name} Im: {e}")
                        else:
                            raise
                
                self.statusBar().showMessage(
                    f"Added {base_name} (Re+Im) from {chamber_name} to plot", 3000
                )
                
        except Exception as e:
            logger.error(f"Error in _on_impedance_dropped_to_plot: {e}")
            import traceback
            logger.error(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add impedance to plot:\n{e}"
            )

    # =========================================================================
    # File Operations
    # =========================================================================
    
    def _on_open_config(self) -> None:
        """Handle Open Configuration menu action."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Open Configuration File",
            "",
            "Configuration Files (*.cfg *.ini);;All Files (*)"
        )
        
        if filepath:
            self._load_config_file(filepath)
    
    def _load_config_file(self, filepath: str) -> None:
        """
        Load a configuration file and create a new chamber.
        
        Args:
            filepath: Path to the configuration file.
        """
        try:
            from pytlwall.cfg_io import CfgIo
            cfg = CfgIo(filepath)
            chamber = ChamberData.from_cfgio(cfg)
            
            if chamber is not None:
                # Set ID based on current count
                idx = len(self.chambers) + 1
                chamber.id = f"Chamber {idx}"
                
                self.chambers.append(chamber)
                self.sidebar.set_chambers(self.chambers)
                
                self.statusBar().showMessage(
                    f"Loaded configuration from {Path(filepath).name}", 3000
                )
            else:
                QMessageBox.warning(
                    self,
                    "Load Error",
                    f"Failed to load configuration from:\n{filepath}"
                )
        except ImportError:
            QMessageBox.warning(
                self,
                "Import Error",
                "pytlwall is not installed. Cannot load configuration files."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load configuration:\n{str(e)}"
            )
    
    def _on_save_config(self) -> None:
        """Handle Save Configuration menu action."""
        # Get currently selected chamber
        idx = self.sidebar.get_current_chamber_index()
        if idx < 0 or idx >= len(self.chambers):
            QMessageBox.information(
                self,
                "No Chamber Selected",
                "Please select a chamber to save."
            )
            return
        
        chamber = self.chambers[idx]
        
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Configuration File",
            f"{chamber.component_name}.cfg",
            "Configuration Files (*.cfg *.ini);;All Files (*)"
        )
        
        if filepath:
            self._save_config_file(chamber, filepath)
    
    def _save_config_file(self, chamber: ChamberData, filepath: str) -> None:
        """
        Save a chamber's configuration to a file.
        
        Args:
            chamber: ChamberData to save.
            filepath: Destination file path.
        """
        try:
            from pytlwall.cfg_io import CfgIo
            cfg = CfgIo()
            chamber.to_cfgio(cfg)
            cfg.write_cfg(filepath)
            
            self.statusBar().showMessage(
                f"Saved configuration to {Path(filepath).name}", 3000
            )
        except ImportError:
            QMessageBox.warning(
                self,
                "Import Error",
                "pytlwall is not installed. Cannot save configuration files."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to save configuration:\n{str(e)}"
            )
    
    def _on_export_all(self) -> None:
        """Handle Export All Chambers menu action."""
        if not self.chambers:
            QMessageBox.information(
                self,
                "No Chambers",
                "There are no chambers to export."
            )
            return
        
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Export Directory"
        )
        
        if directory:
            self._export_all_chambers(directory)
    
    def _export_all_chambers(self, directory: str) -> None:
        """
        Export all chambers to configuration files.
        
        Args:
            directory: Target directory for exported files.
        """
        try:
            from pytlwall.cfg_io import CfgIo
            
            exported = 0
            for chamber in self.chambers:
                filepath = Path(directory) / f"{chamber.component_name}.cfg"
                
                cfg = CfgIo()
                chamber.to_cfgio(cfg)
                cfg.write_cfg(str(filepath))
                exported += 1
            
            self.statusBar().showMessage(
                f"Exported {exported} configuration(s) to {directory}", 3000
            )
        except ImportError:
            QMessageBox.warning(
                self,
                "Import Error",
                "pytlwall is not installed. Cannot export configuration files."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to export configurations:\n{str(e)}"
            )
    
    def _on_save_data(self) -> None:
        """
        Save the data table to a file.

        Opens a dialog to select the output file and saves the current
        data table if available.
        """
        data_panel = self.central_panel.data_panel

        # No data available → nothing to save
        if data_panel.get_column_count() == 0:
            QMessageBox.information(
                self,
                "No Data",
                (
                    "There is no data to save.\n"
                    "Add some impedances to the Data table first."
                ),
            )
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data Table",
            "impedance_data.csv",
            "Data Files (*.csv *.xlsx *.xls);;All Files (*)",
        )

        if not filepath:
            return

        success = data_panel.save_to_file(filepath)
        if success:
            filename = Path(filepath).name
            self.statusBar().showMessage(
                f"Saved data table to {filename}",
                3000,
            )


    def _on_save_plot(self) -> None:
        """
        Save the current plot to an image file.

        Opens a dialog to select the output file and saves the plot
        if there is at least one plotted impedance.
        """
        plot_panel = self.central_panel.plot_panel

        # No plotted items → nothing to save
        if plot_panel.get_item_count() == 0:
            QMessageBox.information(
                self,
                "No Plot",
                (
                    "There is no plot to save.\n"
                    "Add some impedances to the Plot panel first."
                ),
            )
            return

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot",
            "impedance_plot.png",
            (
                "Images (*.png *.jpg *.jpeg *.pdf *.svg);;"
                "All Files (*)"
            ),
        )

        if not filepath:
            return

        success = plot_panel.save_plot(filepath)
        if success:
            filename = Path(filepath).name
            self.statusBar().showMessage(
                f"Saved plot to {filename}",
                3000,
            )
        else:
            QMessageBox.critical(
                self,
                "Save Error",
                "Failed to save plot to file.",
            )

    def _on_save_chamber_impedance(self) -> None:
        """Save the calculated chamber impedance files to a user-selected directory."""
        chamber = self._get_current_chamber()
        if chamber is None:
            QMessageBox.information(
                self,
                "No Chamber Selected",
                "Please select a chamber to export.",
            )
            return

        if not getattr(chamber, "impedance_results", None):
            QMessageBox.information(
                self,
                "No Impedance Data",
                "No impedance data found. Please calculate impedances first.",
            )
            return

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            "",
            QFileDialog.ShowDirsOnly,
        )
        if not directory:
            return

        try:
            save_chamber_impedance(
                output_dir=Path(directory),
                impedance_freq=chamber.impedance_freq,
                impedance_results=chamber.impedance_results,
            )
            self.statusBar().showMessage(
                f"Saved chamber impedance files to {Path(directory).name}",
                3000,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save impedance files:\n{exc}",
            )

    def _on_save_chamber_complete(self) -> None:
        """Save cfg, impedance text files, and impedance plots to a user-selected directory."""
        chamber = self._get_current_chamber()
        if chamber is None:
            QMessageBox.information(
                self,
                "No Chamber Selected",
                "Please select a chamber to export.",
            )
            return

        if not getattr(chamber, "impedance_results", None):
            QMessageBox.information(
                self,
                "No Impedance Data",
                "No impedance data found. Please calculate impedances first.",
            )
            return

        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory",
            "",
            QFileDialog.ShowDirsOnly,
        )
        if not directory:
            return

        base_dir = Path(directory).expanduser()
        out_dir = base_dir / "output"
        plots_dir = base_dir / "img"

        out_dir.mkdir(parents=True, exist_ok=True)
        plots_dir.mkdir(parents=True, exist_ok=True)

        # Save the cfg file in the selected directory (outside output/).
        cfg_path = base_dir / f"{chamber.component_name}.cfg"
        try:
            self._save_config_file(chamber, str(cfg_path))
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save configuration file:\n{exc}",
            )
            return

        # Save impedance text files in output/.
        try:
            save_chamber_impedance(
                output_dir=out_dir,
                impedance_freq=chamber.impedance_freq,
                impedance_results=chamber.impedance_results,
            )
        except Exception as exc:
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save impedance text files:\n{exc}",
            )
            return

        # Generate one plot per impedance base name.
        bases = set()
        for key in chamber.impedance_results.keys():
            if key.endswith("Re") and len(key) > 2:
                bases.add(key[:-2])
            elif key.endswith("Im") and len(key) > 2:
                bases.add(key[:-2])

        for base in sorted(bases):
            re_key = f"{base}Re"
            im_key = f"{base}Im"
            if re_key not in chamber.impedance_results:
                continue

            re_arr = chamber.impedance_results[re_key]
            im_arr = chamber.impedance_results.get(im_key, np.zeros_like(re_arr))
            z_complex = re_arr + 1j * im_arr

            # Choose plotting unit based on impedance type.
            imped_type = "L"
            if base == "ZTrans" or "Trans" in base:
                imped_type = "T"

            plot_util.plot_Z_vs_f_simple(
                f=chamber.impedance_freq,
                Z=z_complex,
                imped_type=imped_type,
                title=base,
                savedir=str(plots_dir),
                savename=f"{base}.png",
                xscale="log",
                yscale="lin",
            )

        # Avoid accumulating matplotlib figures in long sessions.
        plot_util.close_all_figures()

        QMessageBox.information(
            self,
            "Save Complete",
            "Chamber saved successfully.",
        )

        self.statusBar().showMessage(
            f"Saved complete chamber export to {base_dir}",
            4000,
        )

    def _on_save_all_cfg(self) -> None:
        """Save cfg files for all chambers."""
        logger.info("Starting save all cfg files")
        base_dir = QFileDialog.getExistingDirectory(self, "Select output directory")
        if not base_dir:
            logger.debug("Save all cfg cancelled by user")
            return

        base_dir = Path(base_dir)
        logger.debug(f"Output directory: {base_dir}")
        
        saved_count = 0
        errors = []
        
        for chamber in self.chambers:
            try:
                # Use component_name instead of name
                cfg_path = base_dir / f"{chamber.component_name}.cfg"
                logger.debug(f"Saving chamber '{chamber.id}' to {cfg_path}")
                # Call the correct method with correct argument order
                self._save_config_file(chamber, str(cfg_path))
                saved_count += 1
            except Exception as e:
                error_msg = f"Failed to save {chamber.id}: {e}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                errors.append(error_msg)
        
        if errors:
            logger.warning(f"Save all cfg completed with {len(errors)} error(s)")
            QMessageBox.warning(
                self, 
                "Partial Success", 
                f"Saved {saved_count} of {len(self.chambers)} chambers.\n\nErrors:\n" + "\n".join(errors)
            )
        else:
            logger.info(f"Successfully saved all {saved_count} cfg files")
            QMessageBox.information(self, "Success", "All chambers saved successfully.")
    
    def _on_save_all_impedances(self) -> None:
        """Save impedance files for all chambers."""
        logger.info("Starting save all impedances")
        base_dir = QFileDialog.getExistingDirectory(self, "Select output directory")
        if not base_dir:
            logger.debug("Save all impedances cancelled by user")
            return

        base_dir = Path(base_dir)
        logger.debug(f"Output directory: {base_dir}")
        
        saved_count = 0
        skipped_count = 0
        errors = []

        for chamber in self.chambers:
            try:
                # Check if impedance data exists
                if not getattr(chamber, "impedance_results", None):
                    logger.warning(f"Skipping {chamber.id}: no impedance data")
                    skipped_count += 1
                    continue
                    
                out_dir = base_dir / f"output_{chamber.component_name}"
                out_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Saving impedances for '{chamber.id}' to {out_dir}")

                save_chamber_impedance(
                    output_dir=out_dir,
                    impedance_freq=chamber.impedance_freq,
                    impedance_results=chamber.impedance_results,
                )
                saved_count += 1
            except Exception as e:
                error_msg = f"Failed to save impedances for {chamber.id}: {e}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                errors.append(error_msg)

        msg_parts = [f"Saved impedances for {saved_count} chamber(s)."]
        if skipped_count:
            msg_parts.append(f"Skipped {skipped_count} (no data).")
        if errors:
            logger.warning(f"Save all impedances completed with {len(errors)} error(s)")
            QMessageBox.warning(
                self,
                "Partial Success",
                " ".join(msg_parts) + "\n\nErrors:\n" + "\n".join(errors)
            )
        else:
            logger.info(f"Successfully saved impedances for {saved_count} chambers")
            QMessageBox.information(self, "Success", " ".join(msg_parts))

    def _on_save_all_complete(self) -> None:
        """Save cfg, impedances and plots for all chambers."""
        logger.info("Starting save all complete (cfg + impedances + plots)")
        base_dir = QFileDialog.getExistingDirectory(self, "Select output directory")
        if not base_dir:
            logger.debug("Save all complete cancelled by user")
            return

        base_dir = Path(base_dir)
        logger.debug(f"Output directory: {base_dir}")
        
        saved_count = 0
        skipped_count = 0
        errors = []

        for chamber in self.chambers:
            chamber_name = chamber.component_name
            logger.info(f"Processing chamber: {chamber.id} ({chamber_name})")
            
            try:
                # --- cfg ---
                cfg_path = base_dir / f"{chamber_name}.cfg"
                logger.debug(f"Saving cfg to {cfg_path}")
                self._save_config_file(chamber, str(cfg_path))

                # Check if impedance data exists for impedance export
                if not getattr(chamber, "impedance_results", None):
                    logger.warning(f"Chamber {chamber.id}: no impedance data, skipping impedance/plot export")
                    skipped_count += 1
                    continue

                # --- impedance txt ---
                out_dir = base_dir / f"output_{chamber_name}"
                out_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Saving impedance files to {out_dir}")

                save_chamber_impedance(
                    output_dir=out_dir,
                    impedance_freq=chamber.impedance_freq,
                    impedance_results=chamber.impedance_results,
                )

                # --- plots ---
                img_dir = base_dir / f"img_{chamber_name}"
                img_dir.mkdir(parents=True, exist_ok=True)
                logger.debug(f"Saving plots to {img_dir}")

                for base in self._get_impedance_bases(chamber):
                    try:
                        z_re = chamber.impedance_results[f"{base}Re"]
                        z_im = chamber.impedance_results.get(f"{base}Im", np.zeros_like(z_re))
                        z = z_re + 1j * z_im

                        # Determine impedance type for plot
                        imped_type = "T" if "Trans" in base else "L"
                        
                        plot_util.plot_Z_vs_f_simple(
                            f=chamber.impedance_freq,
                            Z=z,
                            imped_type=imped_type,
                            title=base,
                            savedir=str(img_dir),
                            savename=f"{base}.png",
                            xscale="log",
                            yscale="lin",
                        )
                        logger.debug(f"Saved plot: {base}.png")
                    except Exception as plot_error:
                        logger.warning(f"Failed to plot {base}: {plot_error}")
                
                # Clean up matplotlib figures
                plot_util.close_all_figures()
                saved_count += 1
                
            except Exception as e:
                error_msg = f"Failed to save complete export for {chamber.id}: {e}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                errors.append(error_msg)

        msg_parts = [f"Saved complete export for {saved_count} chamber(s)."]
        if skipped_count:
            msg_parts.append(f"Skipped impedance/plots for {skipped_count} (no data).")
        if errors:
            logger.warning(f"Save all complete finished with {len(errors)} error(s)")
            QMessageBox.warning(
                self,
                "Partial Success",
                " ".join(msg_parts) + "\n\nErrors:\n" + "\n".join(errors)
            )
        else:
            logger.info(f"Successfully saved complete export for {saved_count} chambers")
            QMessageBox.information(self, "Success", " ".join(msg_parts))

    def _get_impedance_bases(self, chamber) -> set[str]:
        """Return impedance base names for a chamber (e.g. ZLong, ZTrans)."""
        bases = set()
        for key in chamber.impedance_results:
            if key.endswith(("Re", "Im")):
                bases.add(key[:-2])
        return bases

    # =========================================================================
    # Calculate impedances
    # =========================================================================
    def _calculate_impedances_for_current_chamber(self) -> None:
        """Calculate impedances for the current chamber and update the data model.
        
        Only calculates impedances that are selected (checked) in the output_flags.
        Also removes any existing columns for this chamber from the DataPanel
        to prevent stale data from being displayed.
        """
        logger.info("Starting impedance calculation for current chamber")
        ch_data = self._get_current_chamber()
        if ch_data is None:
            logger.warning("No chamber selected for calculation")
            return

        logger.debug(f"Chamber: {ch_data.id}, component: {ch_data.component_name}")
        
        # Remove existing columns for this chamber from DataPanel
        # This ensures stale data is not displayed after recalculation
        if hasattr(self, 'central_panel') and hasattr(self.central_panel, 'data_panel'):
            removed_count = self.central_panel.data_panel.remove_columns_for_chamber(ch_data.id)
            if removed_count > 0:
                logger.info(f"Removed {removed_count} stale column(s) for chamber '{ch_data.id}' from DataPanel")

        # Get list of selected impedances
        selected_impedances = [
            name for name, selected in ch_data.output_flags.items() if selected
        ]
        logger.debug(f"Selected impedances: {selected_impedances}")
        
        if not selected_impedances:
            logger.warning("No impedances selected for calculation")
            QMessageBox.warning(
                self,
                "No Impedances Selected",
                "Please select at least one impedance to calculate.\n"
            )
            return

        try:
            # Frequencies
            freq_cfg = ch_data.frequency
            logger.debug(f"Frequency config: mode={freq_cfg.mode}")
            
            if freq_cfg.mode == "range":
                freqs = Frequencies(
                    fmin=freq_cfg.fmin,
                    fmax=freq_cfg.fmax,
                    fstep=freq_cfg.fstep,
                )
                logger.debug(f"Frequency range: {freq_cfg.fmin} - {freq_cfg.fmax} Hz, step={freq_cfg.fstep}")
            else:
                freqs = Frequencies.from_file(
                    filename=freq_cfg.filename,
                    sep=freq_cfg.separator,
                    col=freq_cfg.freq_col,
                    skiprows=freq_cfg.skiprows,
                )
                logger.debug(f"Frequencies from file: {freq_cfg.filename}")

            # Beam
            beam_cfg = ch_data.beam
            gamma = beam_cfg.gammarel
            beam = Beam(gammarel=gamma)
            beam.test_beam_shift = beam_cfg.test_beam_shift
            logger.debug(f"Beam: gamma={gamma}, test_beam_shift={beam_cfg.test_beam_shift}")

            # Chamber geometry
            chamber = Chamber(
                pipe_rad_m=ch_data.base_info.pipe_radius_m,
                pipe_hor_m=ch_data.base_info.pipe_hor_m,
                pipe_ver_m=ch_data.base_info.pipe_ver_m,
                chamber_shape=ch_data.base_info.chamber_shape,
                pipe_len_m=ch_data.base_info.pipe_len_m,
            )
            
            logger.debug(f"Chamber: shape={ch_data.base_info.chamber_shape}, "
                        f"radius={ch_data.base_info.pipe_radius_m}m, "
                        f"length={ch_data.base_info.pipe_len_m}m")

            # Layers - with all required parameters
            layers = []
            for i, ld in enumerate(ch_data.layers):
                # k_Hz handling: 0 means infinity
                k_Hz = ld.k_Hz
                if k_Hz == 0 or k_Hz == 0.0:
                    k_Hz = float('inf')
                
                layer = Layer(
                    layer_type=ld.layer_type,
                    thick_m=ld.thick_m,
                    sigmaDC=ld.sigmaDC,
                    epsr=ld.epsr,
                    muinf_Hz=ld.muinf_Hz,
                    k_Hz=k_Hz,
                    tau=ld.tau,
                    RQ=ld.RQ,
                    boundary=False
                )
                layers.append(layer)
                logger.debug(f"Layer {i}: type={ld.layer_type}, thick={ld.thick_m}m, "
                            f"sigmaDC={ld.sigmaDC}")
            
            # Boundary layer (critical for the calculation)
            bd = ch_data.boundary
            k_Hz_bd = bd.k_Hz
            if k_Hz_bd == 0 or k_Hz_bd == 0.0:
                k_Hz_bd = float('inf')
            
            boundary_layer = Layer(
                layer_type=bd.layer_type,
                sigmaDC=bd.sigmaDC,
                epsr=bd.epsr,
                muinf_Hz=bd.muinf_Hz,
                k_Hz=k_Hz_bd,
                tau=bd.tau,
                RQ=bd.RQ,
                boundary=True
            )
            layers.append(boundary_layer)
            logger.debug(f"Boundary layer: type={bd.layer_type}, sigmaDC={bd.sigmaDC}")
            
            chamber.layers = layers

            # Beta functions
            chamber.betax = ch_data.base_info.betax
            chamber.betay = ch_data.base_info.betay
            logger.debug(f"Beta functions: betax={chamber.betax}, betay={chamber.betay}")

            # TlWall calculation
            logger.info("Creating TlWall and calculating impedances...")
            wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
            
            # Calculate only selected impedances
            ch_data.impedance_results = {}
            ch_data.impedance_table = {}
            ch_data.impedance_table["freq"] = freqs.freq  # array 1D
            ch_data.impedance_freq = freqs.freq
            
            calculated_count = 0
            for name in selected_impedances:
                # Get the impedance using the appropriate method
                try:
                    Z = wall.get_impedance(name)
                    if Z is not None:
                        ch_data.impedance_results[f"{name}Re"] = Z.real
                        ch_data.impedance_results[f"{name}Im"] = Z.imag
                        calculated_count += 1
                        logger.debug(f"Calculated {name}: shape={Z.shape}")
                except (AttributeError, KeyError) as e:
                    # If get_impedance doesn't exist or fails, try get_all_impedances
                    # and filter the results
                    logger.debug(f"get_impedance failed for {name}: {e}")
                    pass
            
            # Fallback: if no impedances were calculated, use get_all_impedances
            if calculated_count == 0:
                logger.debug("Using fallback: get_all_impedances()")
                imp = wall.get_all_impedances()
                for name in selected_impedances:
                    Z = imp.get(name)
                    if Z is not None:
                        ch_data.impedance_results[f"{name}Re"] = Z.real
                        ch_data.impedance_results[f"{name}Im"] = Z.imag
                        calculated_count += 1
                        logger.debug(f"Calculated {name} (fallback): shape={Z.shape}")

            idx = self.sidebar.get_current_chamber_index()
            if 0 <= idx < len(self.chambers):
                self.chambers[idx] = ch_data
                # aggiorna le etichette delle impedenze nella tree
                self.sidebar.update_impedance_item_labels(idx, ch_data)
                self.statusBar().showMessage(
                    f"Calculated {calculated_count} impedance(s) for {ch_data.id}", 3000
                )
            
            logger.info(f"Successfully calculated {calculated_count} impedance(s) for {ch_data.id}")
            
        except Exception as e:
            error_msg = f"Impedance calculation failed: {e}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Calculation Error",
                f"Failed to calculate impedances:\n{str(e)}\n\n"
                "Check the log for more details."
            )

    # =========================================================================
    # Accelerator Operations
    # =========================================================================
    def _on_load_accelerator(self) -> None:
        """
        Load accelerator data from a directory using MultipleChamber.
        
        The directory should contain:
        - apertype2.txt (or apertype2): list of aperture types, one per line
        - b_L_betax_betay.txt: geometry file (4 columns: b, L, betax, betay)
        - One .cfg file for each aperture type (e.g., Round.cfg, Rectangular.cfg)
        
        Creates one ChamberData for each element, with proper naming.
        """
        from PyQt5.QtWidgets import QFileDialog, QProgressDialog
        from PyQt5.QtCore import Qt
        
        logger.info("Starting Load Accelerator")
        
        # Select directory containing accelerator files
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Accelerator Data Directory",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not directory:
            logger.debug("Load Accelerator cancelled - no directory selected")
            return
        
        dir_path = Path(directory)
        
        # Find apertype file
        apertype_file = None
        for name in ["apertype2.txt", "apertype2", "apertype.txt", "apertype"]:
            candidate = dir_path / name
            if candidate.exists():
                apertype_file = name
                break
        
        if apertype_file is None:
            QMessageBox.warning(
                self,
                "Missing File",
                "Could not find apertype file in the selected directory.\n"
                "Expected: apertype2.txt or apertype2"
            )
            return
        
        # Find geometry file
        geom_file = None
        for name in ["b_L_betax_betay.txt", "b_L_betax_betay", "blbetaxbetay.txt"]:
            candidate = dir_path / name
            if candidate.exists():
                geom_file = name
                break
        
        if geom_file is None:
            QMessageBox.warning(
                self,
                "Missing File",
                "Could not find geometry file in the selected directory.\n"
                "Expected: b_L_betax_betay.txt"
            )
            return
        
        # Use MultipleChamber to load and validate data
        try:
            from pytlwall.multiple_chamber import MultipleChamber

            mc = MultipleChamber(
                apertype_file=apertype_file,
                geom_file=geom_file,
                input_dir=dir_path,
                out_dir=dir_path / "output"
            )
            mc.load()
            
            logger.info(f"MultipleChamber loaded {mc.n_elements} elements")
            
        except FileNotFoundError as e:
            QMessageBox.warning(
                self,
                "Missing Configuration",
                f"Configuration file not found:\n{e}"
            )
            return
        except ValueError as e:
            QMessageBox.warning(
                self,
                "Data Error",
                f"Error in input files:\n{e}"
            )
            return
        except ImportError:
            QMessageBox.critical(
                self,
                "Import Error",
                "pytlwall.multiple_chamber is not available."
            )
            return
        except Exception as e:
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load accelerator data:\n{e}"
            )
            logger.error(f"Load accelerator failed: {e}")
            return
        
        # Store MultipleChamber instance for later use
        self._multiple_chamber = mc
        self._accelerator_dir = dir_path
        
        # Clear all existing chambers
        self.chambers.clear()
        logger.info("Cleared all existing chambers")
        
        # Create ChamberData for each element
        created_count = 0
        
        # Progress dialog
        progress = QProgressDialog(
            "Loading chambers...", "Cancel", 0, mc.n_elements, self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(500)
        
        for i in range(mc.n_elements):
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            progress.setLabelText(f"Loading chamber {i+1}/{mc.n_elements}")
            
            try:
                apertype = mc.apertypes[i]
                cfg = mc._get_cfg_handler(apertype)
                chamber = ChamberData.from_cfgio(cfg)
                
                if chamber is not None:
                    # Set ID with aperture type
                    idx = len(self.chambers) + 1
                    chamber.id = f"Chamber{idx}: {apertype}"
                    
                    # Override geometry with per-element values from MultipleChamber
                    chamber.base_info.pipe_radius_m = mc.b_list[i]
                    chamber.base_info.pipe_hor_m = mc.b_list[i]
                    chamber.base_info.pipe_ver_m = mc.b_list[i]
                    chamber.base_info.pipe_len_m = mc.L_list[i]
                    chamber.base_info.betax = mc.betax_list[i]
                    chamber.base_info.betay = mc.betay_list[i]
                    
                    self.chambers.append(chamber)
                    created_count += 1
                    
            except Exception as e:
                logger.warning(f"Failed to create chamber {i}: {e}")
                continue
            
            # Process events to keep UI responsive
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
        
        progress.setValue(mc.n_elements)
        
        # Update sidebar
        self.sidebar.set_chambers(self.chambers)
        
        # Report results
        msg = f"Loaded {created_count} chamber(s) from accelerator data."
        logger.info(msg)
        self.statusBar().showMessage(msg, 5000)
        
        QMessageBox.information(
            self,
            "Load Accelerator Complete",
            msg
        )
    
    def _on_calculate_accelerator(self) -> None:
        """
        Calculate impedances for all chambers.
        
        Uses MultipleChamber for building TlWall objects but handles
        saving and accumulation directly to avoid dependency on
        io_util.save_impedances_to_excel.
        
        After calculation, creates a "Total" chamber with summed impedances.
        """
        from PyQt5.QtWidgets import QProgressDialog, QFileDialog
        from PyQt5.QtCore import Qt
        import numpy as np
        
        # Check if we have a MultipleChamber instance
        if not hasattr(self, '_multiple_chamber') or self._multiple_chamber is None:
            # Fallback: calculate using individual chamber method
            self._calculate_all_chambers_individually()
            return
        
        mc = self._multiple_chamber
        
        if not mc.is_loaded:
            QMessageBox.warning(
                self,
                "Not Loaded",
                "Accelerator data not loaded.\n"
                "Please use 'Load Accelerator' first."
            )
            return
        
        # Ask for output directory
        out_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Output Directory for Calculations",
            str(self._accelerator_dir) if hasattr(self, '_accelerator_dir') else "",
            QFileDialog.ShowDirsOnly
        )
        
        if not out_dir:
            return
        
        out_path = Path(out_dir)
        chambers_dir = out_path / "chambers"
        chambers_dir.mkdir(parents=True, exist_ok=True)
        
        # Progress dialog
        progress = QProgressDialog(
            "Calculating impedances...", "Cancel", 0, mc.n_elements, self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        
        # Import save function
        from pytlwall.io_util import save_chamber_impedance
        
        # Accumulate totals
        total_impedances = {}
        freqs = None
        success_count = 0
        error_count = 0
        
        try:
            for idx in range(mc.n_elements):
                if progress.wasCanceled():
                    raise InterruptedError("Calculation cancelled by user")
                
                progress.setValue(idx)
                progress.setLabelText(f"Processing element {idx+1}/{mc.n_elements}")
                
                try:
                    # Build TlWall and calculate using MultipleChamber's method
                    wall = mc._build_wall_for_element(idx)
                    impedances = wall.get_all_impedances()
                    
                    # Get frequencies from first element
                    if freqs is None:
                        freqs = mc.get_frequencies()
                    
                    # Save to .txt files
                    chamber_dir = chambers_dir / f"chamber_{idx:03d}"
                    chamber_dir.mkdir(exist_ok=True)
                    
                    # Convert to Re/Im format
                    impedance_results = {}
                    for name, Z in impedances.items():
                        impedance_results[f"{name}Re"] = Z.real
                        impedance_results[f"{name}Im"] = Z.imag
                    
                    save_chamber_impedance(
                        output_dir=chamber_dir,
                        impedance_freq=freqs,
                        impedance_results=impedance_results,
                    )
                    
                    # Update the chamber in GUI with calculated results
                    if idx < len(self.chambers):
                        gui_chamber = self.chambers[idx]
                        gui_chamber.impedance_results = impedance_results.copy()
                        gui_chamber.impedance_freq = freqs
                        logger.debug(f"Updated impedance_results for {gui_chamber.id}")
                    
                    # Accumulate totals (complex values)
                    for name, Z in impedances.items():
                        if name not in total_impedances:
                            total_impedances[name] = np.zeros_like(Z)
                        total_impedances[name] += Z
                    
                    success_count += 1
                    
                    # Free memory
                    del wall
                    del impedances
                    
                except Exception as e:
                    logger.error(f"Failed to process element {idx}: {e}")
                    error_count += 1
                    continue
                
                # Process events to keep UI responsive
                from PyQt5.QtWidgets import QApplication
                QApplication.processEvents()
            
            progress.setValue(mc.n_elements)
            
            # Save totals
            if total_impedances and freqs is not None:
                total_dir = out_path / "total"
                total_dir.mkdir(exist_ok=True)
                
                total_results = {}
                for name, Z in total_impedances.items():
                    total_results[f"{name}Re"] = Z.real
                    total_results[f"{name}Im"] = Z.imag
                
                save_chamber_impedance(
                    output_dir=total_dir,
                    impedance_freq=freqs,
                    impedance_results=total_results,
                )
                
                # Create "Total" chamber in GUI
                self._create_total_chamber_from_complex(total_impedances, freqs)
            
            msg = f"Calculation complete: {success_count} successful"
            if error_count > 0:
                msg += f", {error_count} failed"
            msg += f"\n\nResults saved to:\n{out_path}"
            
            logger.info(msg)
            
            QMessageBox.information(
                self,
                "Calculation Complete",
                msg
            )
            
        except InterruptedError:
            logger.info("Calculation cancelled by user")
            QMessageBox.information(
                self,
                "Cancelled",
                "Calculation was cancelled."
            )
        except Exception as e:
            logger.error(f"Calculation failed: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Calculation Error",
                f"Calculation failed:\n{e}"
            )
    
    def _create_total_chamber_from_complex(self, total_impedances: dict, freqs) -> None:
        """
        Create a 'Total' chamber from accumulated complex impedances.
        Total chamber is inserted at the beginning of the list.
        
        Args:
            total_impedances: Dictionary of summed complex impedance arrays
            freqs: Frequency array
        """
        from .chamber_data import ChamberData
        
        try:
            # Remove existing Total chamber if present
            self.chambers = [ch for ch in self.chambers if ch.id != "Total"]
            
            # Create a new ChamberData for Total
            total_chamber = ChamberData.create_default("Total")
            total_chamber.id = "Total"
            total_chamber.component_name = "Total (sum of all chambers)"
            
            # Set impedance results (convert complex to Re/Im)
            total_chamber.impedance_freq = freqs
            total_chamber.impedance_results = {}
            
            for name, Z in total_impedances.items():
                total_chamber.impedance_results[f"{name}Re"] = Z.real
                total_chamber.impedance_results[f"{name}Im"] = Z.imag
            
            # Insert Total at the beginning of the list
            self.chambers.insert(0, total_chamber)
            
            # Update sidebar
            self.sidebar.set_chambers(self.chambers)
            
            # Update impedance labels in the tree for the Total chamber (now at index 0)
            self.sidebar.update_impedance_item_labels(0, total_chamber)
            
            logger.info("Created Total chamber with summed impedances (at top)")
            
        except Exception as e:
            logger.error(f"Failed to create Total chamber: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    def _calculate_all_chambers_individually(self) -> None:
        """
        Fallback method: calculate impedances for all chambers one by one.
        Used when no MultipleChamber instance is available.
        
        Also creates a "Total" chamber with summed impedances.
        """
        from PyQt5.QtWidgets import QProgressDialog
        from PyQt5.QtCore import Qt
        import numpy as np
        
        if not self.chambers:
            QMessageBox.information(
                self,
                "No Chambers",
                "There are no chambers to calculate.\n"
                "Please load an accelerator or create chambers first."
            )
            return
        
        # Confirm calculation
        reply = QMessageBox.question(
            self,
            "Calculate All Impedances",
            f"This will calculate impedances for all {len(self.chambers)} chamber(s).\n"
            "This may take some time. Continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        if reply != QMessageBox.Yes:
            return
        
        logger.info(f"Starting individual calculation for {len(self.chambers)} chambers")
        
        # Progress dialog
        progress = QProgressDialog(
            "Calculating impedances...", "Cancel", 0, len(self.chambers), self
        )
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        
        success_count = 0
        error_count = 0
        
        # Accumulate totals
        total_impedances = {}
        total_freq = None
        
        for i, chamber in enumerate(self.chambers):
            # Skip if this is already a Total chamber
            if chamber.id == "Total":
                continue
                
            if progress.wasCanceled():
                break
            
            progress.setValue(i)
            progress.setLabelText(f"Calculating {i+1}/{len(self.chambers)}: {chamber.id}")
            
            try:
                # Select this chamber in the sidebar
                if hasattr(self.sidebar, 'chamber_select'):
                    self.sidebar.chamber_select.setCurrentIndex(i)
                
                # Calculate impedances
                self._calculate_impedances_for_current_chamber()
                success_count += 1
                
                # Accumulate totals if impedance results exist
                if hasattr(chamber, 'impedance_results') and chamber.impedance_results:
                    if total_freq is None and hasattr(chamber, 'impedance_freq'):
                        total_freq = chamber.impedance_freq
                    
                    for key, values in chamber.impedance_results.items():
                        if key not in total_impedances:
                            total_impedances[key] = np.zeros_like(values)
                        total_impedances[key] += values
                
            except Exception as e:
                logger.error(f"Failed to calculate {chamber.id}: {e}")
                error_count += 1
            
            # Process events
            from PyQt5.QtWidgets import QApplication
            QApplication.processEvents()
        
        progress.setValue(len(self.chambers))
        
        # Create Total chamber if we have accumulated impedances
        if total_impedances and total_freq is not None:
            self._create_total_chamber_from_results(total_impedances, total_freq)
        
        # Report results
        msg = f"Calculation complete: {success_count} successful"
        if error_count > 0:
            msg += f", {error_count} failed"
        msg += "\n\nTotal chamber created with summed impedances."
        
        logger.info(msg)
        self.statusBar().showMessage(msg, 5000)
        
        QMessageBox.information(
            self,
            "Calculation Complete",
            msg
        )
    
    def _create_total_chamber_from_results(self, total_impedances: dict, freqs) -> None:
        """
        Create a 'Total' chamber from accumulated impedance results.
        Total chamber is inserted at the beginning of the list.
        
        Args:
            total_impedances: Dictionary of summed impedance arrays (already in Re/Im format)
            freqs: Frequency array
        """
        from .chamber_data import ChamberData
        
        try:
            # Remove existing Total chamber if present
            self.chambers = [ch for ch in self.chambers if ch.id != "Total"]
            
            # Create a new ChamberData for Total
            total_chamber = ChamberData.create_default("Total")
            total_chamber.id = "Total"
            total_chamber.component_name = "Total (sum of all chambers)"
            
            # Set impedance results
            total_chamber.impedance_freq = freqs
            total_chamber.impedance_results = total_impedances
            
            # Insert Total at the beginning of the list
            self.chambers.insert(0, total_chamber)
            
            # Update sidebar
            self.sidebar.set_chambers(self.chambers)
            
            # Update impedance labels in the tree for the Total chamber (now at index 0)
            self.sidebar.update_impedance_item_labels(0, total_chamber)
            
            logger.info("Created Total chamber with summed impedances (at top)")
            
        except Exception as e:
            logger.error(f"Failed to create Total chamber: {e}")
            import traceback
            logger.debug(traceback.format_exc())

    # =========================================================================
    # Save/Load View
    # =========================================================================
    def _on_save_view(self) -> None:
        """
        Save complete View (all chambers, data, plot) to a directory.
        
        Creates a directory containing:
        - view_manifest.json: metadata and file references
        - *.cfg: chamber configuration files
        - output_*/: impedance data directories
        - data file (CSV)
        - plot file (PNG)
        """
        from .view_io import save_view, sanitize_filename
        from PyQt5.QtWidgets import QInputDialog
        
        logger.info("Starting Save View")
        
        # Check if there's anything to save
        if not self.chambers:
            QMessageBox.information(
                self,
                "Nothing to Save",
                "There are no chambers to save.\nPlease create or load a chamber first."
            )
            return
        
        # Get view name from user
        default_name = f"View_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        view_name, ok = QInputDialog.getText(
            self,
            "Save View",
            "Enter a name for this View:",
            text=default_name
        )
        
        if not ok or not view_name.strip():
            logger.debug("Save View cancelled by user")
            return
        
        view_name = view_name.strip()
        safe_name = sanitize_filename(view_name)
        
        # Select output directory
        base_dir = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Save View",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not base_dir:
            logger.debug("Save View cancelled - no directory selected")
            return
        
        # Create view directory
        view_dir = Path(base_dir) / safe_name
        
        # Check if directory exists
        if view_dir.exists():
            reply = QMessageBox.question(
                self,
                "Directory Exists",
                f"The directory '{safe_name}' already exists.\n"
                "Do you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Save view
        try:
            success = save_view(self, view_dir, view_name)
            
            if success:
                QMessageBox.information(
                    self,
                    "View Saved",
                    f"View saved successfully to:\n{view_dir}"
                )
                self.statusBar().showMessage(f"View saved to {view_dir}", 4000)
            else:
                QMessageBox.warning(
                    self,
                    "Save Warning",
                    "View saved with some errors.\nCheck the log for details."
                )
        except Exception as e:
            logger.error(f"Failed to save view: {e}")
            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Save Error",
                f"Failed to save view:\n{str(e)}"
            )
    
    def _on_load_view(self) -> None:
        """
        Load complete View from a directory.
        
        Restores:
        - All chambers with their configurations
        - Calculated impedances
        - Data panel content
        - Plot panel content and settings
        """
        from .view_io import load_view
        
        logger.info("Starting Load View")
        
        # Warn about losing current work
        if self.chambers:
            reply = QMessageBox.question(
                self,
                "Load View",
                "Loading a View will replace all current chambers and data.\n"
                "Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        # Select view directory
        view_dir = QFileDialog.getExistingDirectory(
            self,
            "Select View Directory to Load",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if not view_dir:
            logger.debug("Load View cancelled - no directory selected")
            return
        
        view_dir = Path(view_dir)
        
        # Check for manifest
        manifest_path = view_dir / "view_manifest.json"
        if not manifest_path.exists():
            QMessageBox.warning(
                self,
                "Invalid View",
                f"The selected directory is not a valid View.\n"
                f"Missing: view_manifest.json"
            )
            return
        
        # Load view
        try:
            success = load_view(self, view_dir)
            
            if success:
                QMessageBox.information(
                    self,
                    "View Loaded",
                    f"View loaded successfully from:\n{view_dir}\n\n"
                    f"Loaded {len(self.chambers)} chamber(s)."
                )
                self.statusBar().showMessage(f"View loaded from {view_dir}", 4000)
            else:
                QMessageBox.warning(
                    self,
                    "Load Warning",
                    "View loaded with some errors.\nCheck the log for details."
                )
        except Exception as e:
            logger.error(f"Failed to load view: {e}")
            logger.debug(traceback.format_exc())
            QMessageBox.critical(
                self,
                "Load Error",
                f"Failed to load view:\n{str(e)}"
            )
