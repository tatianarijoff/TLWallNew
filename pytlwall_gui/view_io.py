"""
View I/O module for pytlwall GUI.

This module handles saving and loading complete "Views" which include:
- All chamber configurations and calculated impedances
- Data panel content and settings
- Plot panel content and settings

A View is saved as a directory containing:
- view_manifest.json: metadata and references to all files
- *.cfg files: chamber configurations
- output_*/: impedance data directories
- data_*.csv: data panel export
- plot_*.png: plot panel export

Authors: Tatiana Rijoff
Date: December 2025
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Any, Optional
import numpy as np

if TYPE_CHECKING:
    from .main_window import MainWindow
    from .chamber_data import ChamberData

logger = logging.getLogger("pytlwall_interface")


def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename.
    
    Replaces spaces, slashes, and other problematic characters with underscores.
    
    Args:
        name: Original string
        
    Returns:
        Sanitized string safe for use as filename
    """
    if not name:
        return "unnamed"
    
    # Characters to replace with underscore
    invalid_chars = [' ', '/', '\\', ':', '*', '?', '"', '<', '>', '|', '\t', '\n']
    result = name
    for char in invalid_chars:
        result = result.replace(char, '_')
    
    # Remove multiple consecutive underscores
    while '__' in result:
        result = result.replace('__', '_')
    
    # Remove leading/trailing underscores
    result = result.strip('_')
    
    return result if result else "unnamed"


class ViewManifest:
    """
    Manifest file for a saved View.
    
    Contains metadata about all saved files and their relationships.
    """
    
    VERSION = "1.0"
    
    def __init__(self):
        self.version = self.VERSION
        self.created_at = datetime.now().isoformat()
        self.view_name = ""
        self.chambers: List[Dict[str, Any]] = []
        self.data_file: Optional[str] = None
        self.data_title: Optional[str] = None
        self.data_settings: Dict[str, Any] = {}  # Data panel settings including columns
        self.plot_file: Optional[str] = None
        self.plot_title: Optional[str] = None
        self.plot_settings: Dict[str, Any] = {}
    
    def add_chamber(self, chamber_id: str, component_name: str, 
                    cfg_file: str, impedance_dir: Optional[str] = None,
                    impedances: Optional[List[str]] = None):
        """Add a chamber entry to the manifest."""
        self.chambers.append({
            "id": chamber_id,
            "component_name": component_name,
            "cfg_file": cfg_file,
            "impedance_dir": impedance_dir,
            "impedances": impedances or []
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert manifest to dictionary for JSON serialization."""
        return {
            "version": self.version,
            "created_at": self.created_at,
            "view_name": self.view_name,
            "chambers": self.chambers,
            "data_file": self.data_file,
            "data_title": self.data_title,
            "data_settings": self.data_settings,
            "plot_file": self.plot_file,
            "plot_title": self.plot_title,
            "plot_settings": self.plot_settings,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ViewManifest":
        """Create manifest from dictionary."""
        manifest = cls()
        manifest.version = data.get("version", cls.VERSION)
        manifest.created_at = data.get("created_at", "")
        manifest.view_name = data.get("view_name", "")
        manifest.chambers = data.get("chambers", [])
        manifest.data_file = data.get("data_file")
        manifest.data_title = data.get("data_title")
        manifest.data_settings = data.get("data_settings", {})
        manifest.plot_file = data.get("plot_file")
        manifest.plot_title = data.get("plot_title")
        manifest.plot_settings = data.get("plot_settings", {})
        return manifest
    
    def save(self, filepath: Path):
        """Save manifest to JSON file."""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
    
    @classmethod
    def load(cls, filepath: Path) -> "ViewManifest":
        """Load manifest from JSON file."""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


def save_view(main_window: "MainWindow", base_dir: Path, view_name: str) -> bool:
    """
    Save complete View to directory.
    
    Args:
        main_window: MainWindow instance
        base_dir: Base directory for the view
        view_name: Name of the view
        
    Returns:
        True if successful, False otherwise
    """
    from pytlwall.cfg_io import CfgIo
    from .chamber_data import save_chamber_to_cfgio
    from pytlwall.io_util import save_chamber_impedance
    
    logger.info(f"Saving view '{view_name}' to {base_dir}")
    
    try:
        # Create directory
        base_dir.mkdir(parents=True, exist_ok=True)
        
        # Create manifest
        manifest = ViewManifest()
        manifest.view_name = view_name
        
        # Save all chambers
        for chamber in main_window.chambers:
            chamber_name = sanitize_filename(chamber.component_name)
            
            # Save cfg file
            cfg_filename = f"{chamber_name}.cfg"
            cfg_path = base_dir / cfg_filename
            
            try:
                cfg = CfgIo()
                save_chamber_to_cfgio(chamber, cfg)
                cfg.write_cfg(str(cfg_path))
                logger.debug(f"Saved cfg: {cfg_filename}")
            except Exception as e:
                logger.error(f"Failed to save cfg for {chamber.id}: {e}")
                continue
            
            # Save impedances if calculated
            impedance_dir = None
            impedances = []
            
            if getattr(chamber, "impedance_results", None):
                impedance_dir_name = f"output_{chamber_name}"
                impedance_dir = base_dir / impedance_dir_name
                impedance_dir.mkdir(parents=True, exist_ok=True)
                
                try:
                    save_chamber_impedance(
                        output_dir=impedance_dir,
                        impedance_freq=chamber.impedance_freq,
                        impedance_results=chamber.impedance_results,
                    )
                    
                    # List calculated impedances
                    for key in chamber.impedance_results:
                        if key.endswith("Re"):
                            impedances.append(key[:-2])
                    
                    impedance_dir = impedance_dir_name  # Store relative path
                    logger.debug(f"Saved impedances: {impedances}")
                except Exception as e:
                    logger.error(f"Failed to save impedances for {chamber.id}: {e}")
                    impedance_dir = None
            
            manifest.add_chamber(
                chamber_id=chamber.id,
                component_name=chamber.component_name,
                cfg_file=cfg_filename,
                impedance_dir=impedance_dir,
                impedances=impedances
            )
        
        # Save Data panel
        data_panel = main_window.central_panel.data_panel
        if data_panel.get_column_count() > 0:
            data_title = data_panel.get_title()
            data_filename = f"{sanitize_filename(data_title)}.csv"
            data_path = base_dir / data_filename
            
            try:
                data_panel.save_to_file(str(data_path))
                manifest.data_file = data_filename
                manifest.data_title = data_title
                
                # Save data panel settings including column info
                manifest.data_settings = {
                    "title": data_title,
                    "freq_column_name": data_panel._freq_column_name,
                    "columns": []
                }
                
                # Save column info for reconstruction
                for col in data_panel._columns:
                    manifest.data_settings["columns"].append({
                        "chamber_name": col.chamber_name,
                        "impedance_name": col.impedance_name,
                        "component": col.component,
                        "custom_name": col._custom_name
                    })
                
                logger.debug(f"Saved data: {data_filename} with {len(data_panel._columns)} columns")
            except Exception as e:
                logger.error(f"Failed to save data panel: {e}")
        
        # Save Plot panel
        plot_panel = main_window.central_panel.plot_panel
        if plot_panel.get_item_count() > 0:
            # Get plot title from the title edit
            plot_title = plot_panel._title_edit.text() or "Impedance"
            plot_filename = f"{sanitize_filename(plot_title)}.png"
            plot_path = base_dir / plot_filename
            
            try:
                plot_panel.save_plot(str(plot_path))
                manifest.plot_file = plot_filename
                manifest.plot_title = plot_title
                
                # Save plot settings
                manifest.plot_settings = {
                    "title": plot_title,
                    "xlabel": plot_panel._xlabel_edit.text(),
                    "ylabel": plot_panel._ylabel_edit.text(),
                    "xscale": plot_panel._xscale_combo.currentText(),
                    "yscale": plot_panel._yscale_combo.currentText(),
                    "items": []
                }
                
                # Save plot items for reconstruction
                for item in plot_panel._items:
                    manifest.plot_settings["items"].append({
                        "chamber_name": item.chamber_name,
                        "impedance_name": item.impedance_name,
                        "component": item.component,
                        "visible": item.visible,
                        "color": item.color,
                        "custom_label": item._custom_label
                    })
                
                logger.debug(f"Saved plot: {plot_filename}")
            except Exception as e:
                logger.error(f"Failed to save plot panel: {e}")
        
        # Save manifest
        manifest_path = base_dir / "view_manifest.json"
        manifest.save(manifest_path)
        logger.info(f"View saved successfully: {manifest_path}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to save view: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def load_view(main_window: "MainWindow", base_dir: Path) -> bool:
    """
    Load complete View from directory.
    
    Args:
        main_window: MainWindow instance
        base_dir: Directory containing the view
        
    Returns:
        True if successful, False otherwise
    """
    from pytlwall.cfg_io import CfgIo
    from .chamber_data import create_chamber_from_cfgio, ChamberData
    
    logger.info(f"Loading view from {base_dir}")
    
    try:
        # Load manifest
        manifest_path = base_dir / "view_manifest.json"
        if not manifest_path.exists():
            logger.error(f"Manifest not found: {manifest_path}")
            return False
        
        manifest = ViewManifest.load(manifest_path)
        logger.debug(f"Loaded manifest: view_name={manifest.view_name}")
        
        # Clear current state
        main_window.chambers.clear()
        main_window.central_panel.data_panel.clear()
        main_window.central_panel.plot_panel.clear()
        
        # Load chambers
        for chamber_info in manifest.chambers:
            cfg_file = chamber_info.get("cfg_file")
            if not cfg_file:
                continue
            
            cfg_path = base_dir / cfg_file
            if not cfg_path.exists():
                logger.warning(f"Chamber cfg not found: {cfg_path}")
                continue
            
            try:
                cfg = CfgIo()
                cfg.read_cfg(str(cfg_path))
                chamber_data = create_chamber_from_cfgio(cfg)
                chamber_data.id = chamber_info.get("id", chamber_data.id)
                
                # Load impedance data if available
                impedance_dir = chamber_info.get("impedance_dir")
                if impedance_dir:
                    imp_path = base_dir / impedance_dir
                    if imp_path.exists():
                        _load_impedance_data(chamber_data, imp_path)
                        logger.info(f"Loaded impedances for {chamber_data.id}: {list(chamber_data.impedance_results.keys())}")
                
                main_window.chambers.append(chamber_data)
                logger.debug(f"Loaded chamber: {chamber_data.id}")
                
            except Exception as e:
                logger.error(f"Failed to load chamber from {cfg_file}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
        
        # Update sidebar
        main_window.sidebar.set_chambers(main_window.chambers)
        
        # Update impedance labels in sidebar for each chamber
        for idx, chamber in enumerate(main_window.chambers):
            if hasattr(chamber, 'impedance_results') and chamber.impedance_results:
                main_window.sidebar.update_impedance_item_labels(idx, chamber)
        
        # Restore Data panel
        _restore_data_panel(main_window, manifest, base_dir)
        
        # Restore Plot panel
        if manifest.plot_settings:
            _restore_plot_panel(main_window, manifest.plot_settings)
        
        logger.info(f"View loaded successfully: {len(main_window.chambers)} chambers")
        return True
        
    except Exception as e:
        logger.error(f"Failed to load view: {e}")
        import traceback
        logger.debug(traceback.format_exc())
        return False


def _load_impedance_data(chamber_data: "ChamberData", imp_dir: Path):
    """
    Load impedance data from files into chamber_data.
    
    Args:
        chamber_data: ChamberData to populate
        imp_dir: Directory containing impedance files
        
    File format expected (pytlwall output):
        - Tab-separated values  
        - First row: header (f, ZLongRe, ZLongIm, etc.)
        - Columns: frequency, Real part, Imaginary part
    """
    import numpy as np
    
    chamber_data.impedance_results = {}
    chamber_data.impedance_freq = None
    
    logger.info(f"Loading impedances from: {imp_dir}")
    
    # Look for impedance files (format: ZLong.txt, ZTrans.txt, etc.)
    txt_files = list(imp_dir.glob("*.txt"))
    logger.debug(f"Found {len(txt_files)} txt files: {[f.name for f in txt_files]}")
    
    for imp_file in txt_files:
        try:
            # Load data with header skip (pytlwall saves with header row)
            # Format: f<tab>ZxxxRe<tab>ZxxxIm
            data = np.loadtxt(imp_file, skiprows=1)  # Skip header row
            
            if data.ndim == 1:
                # Single row, reshape
                data = data.reshape(1, -1)
            
            if data.size == 0:
                logger.warning(f"Empty file: {imp_file.name}")
                continue
                
            # Extract impedance name from filename (e.g., "ZLong" from "ZLong.txt")
            imp_name = imp_file.stem
            
            logger.debug(f"Loading {imp_name}: shape={data.shape}")
            
            # First column is always frequency
            if chamber_data.impedance_freq is None:
                chamber_data.impedance_freq = data[:, 0]
                logger.debug(f"Set frequency array: {len(chamber_data.impedance_freq)} points")
            
            # Handle different file formats
            if data.shape[1] >= 3:
                # Format: freq, Re, Im
                chamber_data.impedance_results[f"{imp_name}Re"] = data[:, 1]
                chamber_data.impedance_results[f"{imp_name}Im"] = data[:, 2]
                logger.info(f"Loaded {imp_name}: Re and Im ({len(data)} points)")
            elif data.shape[1] == 2:
                # Format: freq, value (assume Real)
                chamber_data.impedance_results[f"{imp_name}Re"] = data[:, 1]
                chamber_data.impedance_results[f"{imp_name}Im"] = np.zeros_like(data[:, 1])
                logger.info(f"Loaded {imp_name}: Re only ({len(data)} points)")
            else:
                logger.warning(f"Unexpected format in {imp_file.name}: {data.shape[1]} columns")
            
        except Exception as e:
            logger.error(f"Failed to load impedance file {imp_file}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
    
    logger.info(f"Loaded impedances: {list(chamber_data.impedance_results.keys())}")


def _restore_data_panel(main_window: "MainWindow", manifest: ViewManifest, base_dir: Path):
    """
    Restore data panel from manifest and chamber data.
    
    Args:
        main_window: MainWindow instance
        manifest: View manifest
        base_dir: Base directory of the view
    """
    import numpy as np
    
    data_panel = main_window.central_panel.data_panel
    
    # Get data settings from manifest
    data_settings = manifest.data_settings
    
    logger.info(f"Restoring data panel. data_settings: {data_settings}")
    logger.info(f"Available chambers: {[ch.id for ch in main_window.chambers]}")
    
    # Check what impedances each chamber has
    for ch in main_window.chambers:
        has_results = hasattr(ch, 'impedance_results') and ch.impedance_results
        has_freq = hasattr(ch, 'impedance_freq') and ch.impedance_freq is not None
        logger.info(f"Chamber {ch.id}: has_results={has_results}, has_freq={has_freq}")
        if has_results:
            logger.info(f"  Impedance keys: {list(ch.impedance_results.keys())}")
    
    # Set title if available
    if manifest.data_title:
        data_panel.set_title(manifest.data_title)
    
    # Set frequency column name if available
    if data_settings.get("freq_column_name"):
        data_panel._freq_column_name = data_settings["freq_column_name"]
    
    data_columns = data_settings.get("columns", [])
    
    if data_columns:
        # Restore from saved column info
        logger.info(f"Restoring {len(data_columns)} data columns from manifest")
        
        for col_info in data_columns:
            chamber_name = col_info.get("chamber_name")
            imp_name = col_info.get("impedance_name")
            component = col_info.get("component")
            custom_name = col_info.get("custom_name")
            
            logger.debug(f"Looking for column: chamber={chamber_name}, imp={imp_name}, comp={component}")
            
            # Find chamber
            chamber = None
            for ch in main_window.chambers:
                if ch.id == chamber_name:
                    chamber = ch
                    break
            
            if chamber is None:
                logger.warning(f"Chamber not found for data column: {chamber_name}")
                continue
            
            if not hasattr(chamber, 'impedance_results') or not chamber.impedance_results:
                logger.warning(f"No impedance results for chamber: {chamber_name}")
                continue
            
            if not hasattr(chamber, 'impedance_freq') or chamber.impedance_freq is None:
                logger.warning(f"No frequency data for chamber: {chamber_name}")
                continue
            
            key = f"{imp_name}{component}"
            if key not in chamber.impedance_results:
                logger.warning(f"Impedance {key} not found in chamber {chamber_name}")
                logger.warning(f"  Available keys: {list(chamber.impedance_results.keys())}")
                continue
            
            logger.info(f"Adding column: {chamber_name} {imp_name} {component}")
            
            # Add to data panel
            data_panel.add_impedance(
                chamber_name=chamber_name,
                impedance_name=imp_name,
                data=chamber.impedance_results[key],
                frequencies=chamber.impedance_freq,
                component=component
            )
            
            # Set custom name if available
            if custom_name and data_panel._columns:
                data_panel._columns[-1].set_custom_name(custom_name)
        
        # Rebuild table to show custom names
        data_panel._rebuild_table()
        logger.info(f"Restored data panel with {data_panel.get_column_count()} columns")
    
    else:
        # Fallback: add all impedances from chambers that have calculated results
        logger.info("No column info in manifest, restoring all impedances")
        
        for chamber in main_window.chambers:
            if not hasattr(chamber, 'impedance_results') or not chamber.impedance_results:
                logger.debug(f"Skipping chamber {chamber.id}: no impedance_results")
                continue
            if not hasattr(chamber, 'impedance_freq') or chamber.impedance_freq is None:
                logger.debug(f"Skipping chamber {chamber.id}: no impedance_freq")
                continue
            
            frequencies = chamber.impedance_freq
            logger.info(f"Adding impedances from chamber {chamber.id}")
            
            # Add each impedance to data panel
            for key, data in chamber.impedance_results.items():
                if key.endswith("Re"):
                    imp_name = key[:-2]
                    re_data = data
                    im_key = f"{imp_name}Im"
                    im_data = chamber.impedance_results.get(im_key, np.zeros_like(re_data))
                    
                    # Create complex data
                    complex_data = re_data + 1j * im_data
                    
                    logger.debug(f"Adding {imp_name} from {chamber.id}")
                    data_panel.add_impedance(
                        chamber_name=chamber.id,
                        impedance_name=imp_name,
                        data=complex_data,
                        frequencies=frequencies,
                        component=None  # Add both Re and Im
                    )
        
        logger.info(f"Restored data panel from chamber impedances: {data_panel.get_column_count()} columns")


def _restore_plot_panel(main_window: "MainWindow", plot_settings: Dict[str, Any]):
    """
    Restore plot panel state from settings.
    
    Args:
        main_window: MainWindow instance
        plot_settings: Plot settings dictionary
    """
    plot_panel = main_window.central_panel.plot_panel
    
    logger.info(f"Restoring plot panel. Items to restore: {len(plot_settings.get('items', []))}")
    
    # Restore settings
    if plot_settings.get("title"):
        plot_panel._title_edit.setText(plot_settings["title"])
    if plot_settings.get("xlabel"):
        plot_panel._xlabel_edit.setText(plot_settings["xlabel"])
    if plot_settings.get("ylabel"):
        plot_panel._ylabel_edit.setText(plot_settings["ylabel"])
    if plot_settings.get("xscale"):
        idx = plot_panel._xscale_combo.findText(plot_settings["xscale"])
        if idx >= 0:
            plot_panel._xscale_combo.setCurrentIndex(idx)
    if plot_settings.get("yscale"):
        idx = plot_panel._yscale_combo.findText(plot_settings["yscale"])
        if idx >= 0:
            plot_panel._yscale_combo.setCurrentIndex(idx)
    
    # Restore plot items
    for item_info in plot_settings.get("items", []):
        chamber_name = item_info.get("chamber_name")
        impedance_name = item_info.get("impedance_name")
        component = item_info.get("component", "Re")
        
        logger.debug(f"Looking for plot item: chamber={chamber_name}, imp={impedance_name}, comp={component}")
        
        # Find chamber
        chamber = None
        for ch in main_window.chambers:
            if ch.id == chamber_name or ch.component_name == chamber_name:
                chamber = ch
                break
        
        if chamber is None:
            logger.warning(f"Chamber not found for plot: {chamber_name}")
            continue
            
        if not getattr(chamber, "impedance_results", None):
            logger.warning(f"No impedance_results for chamber: {chamber_name}")
            continue
        
        # Get impedance data
        key = f"{impedance_name}{component}"
        if key not in chamber.impedance_results:
            logger.warning(f"Impedance {key} not found in chamber {chamber_name}")
            logger.warning(f"  Available keys: {list(chamber.impedance_results.keys())}")
            continue
        
        if not hasattr(chamber, 'impedance_freq') or chamber.impedance_freq is None:
            logger.warning(f"No frequency data for chamber: {chamber_name}")
            continue
        
        data = chamber.impedance_results[key]
        frequencies = chamber.impedance_freq
        
        logger.info(f"Adding plot item: {chamber_name} {impedance_name} {component}")
        
        # Add to plot
        plot_panel.add_impedance(
            chamber_name=chamber_name,
            impedance_name=impedance_name,
            data=data,
            frequencies=frequencies,
            component=component
        )
        
        # Restore visibility and custom label
        for plot_item in plot_panel._items:
            if (plot_item.chamber_name == chamber_name and 
                plot_item.impedance_name == impedance_name and
                plot_item.component == component):
                
                plot_item.visible = item_info.get("visible", True)
                if item_info.get("custom_label"):
                    plot_item._custom_label = item_info["custom_label"]
                
                # Update color if saved
                if item_info.get("color"):
                    plot_item.color = item_info["color"]
                
                break
    
    # Update the list widget to reflect changes
    plot_panel._list.clear()
    from .plot_panel import ImpedanceListItem
    for plot_item in plot_panel._items:
        list_item = ImpedanceListItem(plot_item)
        plot_panel._list.addItem(list_item)
    
    # Update plot
    plot_panel._update_plot()
    plot_panel._update_info()
