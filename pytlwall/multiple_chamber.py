#!/usr/bin/env python3
"""
Multiple-chamber impedance calculator for accelerator lattices.

This module processes multiple vacuum chamber elements from an accelerator
lattice, calculating wall impedances for each element and accumulating
total impedances.

Memory-efficient architecture:
- load(): Only loads apertype + geometry (lightweight)
- calculate_all(): Processes one element at a time, writes to file, keeps only totals
- get_element_data(i): Reads from file on-demand
- plot_element(i): Reads from file and plots on-demand

This prevents memory issues with large lattices (100+ elements).
"""

from __future__ import annotations

import gc
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from . import io_util
from .cfg_io import CfgIo
from .chamber import Chamber
from .beam import Beam
from .frequencies import Frequencies
from .tlwall import TlWall
from . import plot_util


# Default mapping from aperture type name to cfg filename
# Users can define custom mappings (e.g., "Oblong2" -> "Oblong2.cfg")
DEFAULT_APERTYPE_TO_CFG: Dict[str, str] = {
    "Oblong": "Oblong.cfg",
    "Rectangular": "Rectangular.cfg",
    "Round": "Round.cfg",
    "Diamond": "Diamond.cfg",
}


class MultipleChamber:
    """
    Memory-efficient multiple-chamber impedance calculator.

    Example usage:
        >>> from pytlwall import MultipleChamber
        >>> mc = MultipleChamber(
        ...     apertype_file="apertype2.txt",
        ...     geom_file="b_L_betax_betay.txt",
        ...     input_dir="./input/",
        ...     out_dir="./output/"
        ... )
        >>> mc.load()                    # Load input files
        >>> mc.calculate_all()           # Calculate all elements
        >>> totals = mc.get_totals()     # Get accumulated totals
        >>> mc.plot_totals()             # Plot total impedances
        >>> data = mc.get_element_data(5)  # Get data for element 5
        >>> mc.plot_element(5)           # Plot element 5
    """

    def __init__(
        self,
        apertype_file: str | Path,
        geom_file: str | Path,
        input_dir: str | Path = ".",
        out_dir: str | Path = "output",
        apertype_to_cfg: Optional[Dict[str, str]] = None,
    ) -> None:
        """
        Initialize MultipleChamber calculator.

        Args:
            apertype_file: Name of the aperture type file (e.g. 'apertype2.txt')
            geom_file: Name of the geometry file (e.g. 'b_L_betax_betay.txt')
            input_dir: Directory containing all input files
            out_dir: Base output directory
            apertype_to_cfg: Optional custom mapping aperture type -> cfg filename
        """
        self.input_dir = Path(input_dir).resolve()
        self.out_dir = Path(out_dir).resolve()

        # Resolve file paths
        aper_path = Path(apertype_file)
        if not aper_path.is_absolute():
            aper_path = self.input_dir / aper_path
        self.apertype_file = aper_path.resolve()

        geom_path = Path(geom_file)
        if not geom_path.is_absolute():
            geom_path = self.input_dir / geom_path
        self.geom_file = geom_path.resolve()

        # Mapping aperture type -> cfg filename
        if apertype_to_cfg is None:
            self.apertype_to_cfg = DEFAULT_APERTYPE_TO_CFG.copy()
        else:
            self.apertype_to_cfg = apertype_to_cfg

        # Cache of CfgIo objects
        self._cfg_cache: Dict[str, CfgIo] = {}

        # Input data (populated by load())
        self.apertypes: List[str] = []
        self.b_list: List[float] = []
        self.L_list: List[float] = []
        self.betax_list: List[float] = []
        self.betay_list: List[float] = []

        # Reference frequency object
        self._freq_obj_ref: Optional[Frequencies] = None
        self._freqs_array: Optional[np.ndarray] = None

        # Accumulated totals (kept in memory)
        self._total_impedances: Dict[str, np.ndarray] = {}
        
        # State flags
        self._loaded = False
        self._calculated = False

    @property
    def n_elements(self) -> int:
        """Number of elements in the lattice."""
        return len(self.apertypes)

    @property
    def is_loaded(self) -> bool:
        """Whether input data has been loaded."""
        return self._loaded

    @property
    def is_calculated(self) -> bool:
        """Whether calculations have been performed."""
        return self._calculated

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load(self) -> None:
        """
        Load input files (apertype and geometry).
        
        This is a lightweight operation that only reads the input files
        without performing any calculations.
        """
        self._load_input_data()
        self._loaded = True
        print(f"[MultipleChamber] Loaded {self.n_elements} elements")

    def calculate_all(
        self,
        progress_callback: Optional[callable] = None
    ) -> None:
        """
        Calculate impedances for all elements.
        
        Memory-efficient: processes one element at a time, writes to file,
        accumulates totals, then frees memory.
        
        Args:
            progress_callback: Optional callback(current, total, message) for progress updates
        """
        if not self._loaded:
            self.load()

        # Create output directories
        self.out_dir.mkdir(parents=True, exist_ok=True)
        chambers_dir = self.out_dir / "chambers"
        chambers_dir.mkdir(exist_ok=True)

        # Initialize totals
        self._total_impedances = {}
        
        n_total = self.n_elements
        
        for idx in range(n_total):
            if progress_callback:
                progress_callback(idx, n_total, f"Processing element {idx+1}/{n_total}")
            
            try:
                self._process_single_element(idx, chambers_dir)
            except Exception as e:
                print(f"[MultipleChamber] Error processing element {idx}: {e}")
                continue
            
            # Force garbage collection periodically
            if idx % 20 == 0:
                gc.collect()

        # Save total impedances
        self._save_totals()
        self._calculated = True
        
        if progress_callback:
            progress_callback(n_total, n_total, "Complete")
        
        print(f"[MultipleChamber] Calculation complete. Output in {self.out_dir}")

    def calculate_element(self, index: int) -> Dict[str, np.ndarray]:
        """
        Calculate impedances for a single element.
        
        Args:
            index: Element index (0-based)
            
        Returns:
            Dictionary of impedance arrays
        """
        if not self._loaded:
            self.load()
            
        if index < 0 or index >= self.n_elements:
            raise IndexError(f"Element index {index} out of range [0, {self.n_elements})")

        wall = self._build_wall_for_element(index)
        impedances = wall.get_all_impedances()
        
        return impedances

    def get_totals(self) -> Dict[str, np.ndarray]:
        """
        Get accumulated total impedances.
        
        Returns:
            Dictionary with total impedance arrays
        """
        if not self._calculated:
            raise RuntimeError("Call calculate_all() first")
        return self._total_impedances.copy()

    def get_frequencies(self) -> np.ndarray:
        """Get the frequency array."""
        if self._freqs_array is None:
            raise RuntimeError("Call load() or calculate_all() first")
        return self._freqs_array.copy()

    def get_element_data(self, index: int) -> Optional[Dict[str, Any]]:
        """
        Get data for a specific element by reading from file.
        
        Args:
            index: Element index (0-based)
            
        Returns:
            Dictionary with element data, or None if not found
        """
        chamber_dir = self.out_dir / "chambers" / f"chamber_{index:03d}"
        excel_file = chamber_dir / f"chamber_{index:03d}_impedances.xlsx"
        
        if not excel_file.exists():
            return None
        
        try:
            import pandas as pd
            data = pd.read_excel(excel_file, sheet_name=None)
            return {
                "index": index,
                "apertype": self.apertypes[index] if index < len(self.apertypes) else "unknown",
                "data": data
            }
        except Exception as e:
            print(f"[MultipleChamber] Error reading element {index}: {e}")
            return None

    def plot_element(
        self,
        index: int,
        save_dir: Optional[str | Path] = None,
        show: bool = False
    ) -> None:
        """
        Plot impedances for a specific element.
        
        Args:
            index: Element index (0-based)
            save_dir: Directory to save plots (default: element's chamber dir)
            show: Whether to display the plot
        """
        data = self.get_element_data(index)
        if data is None:
            print(f"[MultipleChamber] No data found for element {index}")
            return
        
        if save_dir is None:
            save_dir = self.out_dir / "chambers" / f"chamber_{index:03d}"
        else:
            save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        freqs = self.get_frequencies()
        
        for sheet_name, df in data["data"].items():
            if sheet_name == "frequencies":
                continue
            
            # Extract impedance values
            if "Real" in df.columns and "Imag" in df.columns:
                Z = df["Real"].values + 1j * df["Imag"].values
            elif "Magnitude" in df.columns:
                Z = df["Magnitude"].values
            else:
                continue
            
            if not self._is_non_trivial_impedance(Z):
                continue
            
            imped_type = self._guess_imped_type(sheet_name)
            title = f"Chamber {index:03d} - {sheet_name}"
            savename = f"{sheet_name}.png"
            
            plot_util.plot_Z_vs_f_simple(
                f=freqs,
                Z=Z,
                imped_type=imped_type,
                title=title,
                savedir=str(save_dir),
                savename=savename,
                xscale="log",
                yscale="log",
            )
        
        if not show:
            import matplotlib.pyplot as plt
            plt.close('all')

    def plot_totals(
        self,
        save_dir: Optional[str | Path] = None,
        show: bool = False
    ) -> None:
        """
        Plot total accumulated impedances.
        
        Args:
            save_dir: Directory to save plots (default: out_dir/total)
            show: Whether to display the plots
        """
        if not self._calculated:
            raise RuntimeError("Call calculate_all() first")
        
        if save_dir is None:
            save_dir = self.out_dir / "total"
        else:
            save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        freqs = self.get_frequencies()
        
        for name, Z in self._total_impedances.items():
            if not self._is_non_trivial_impedance(Z):
                continue
            
            imped_type = self._guess_imped_type(name)
            title = f"Total - {name}"
            savename = f"{name}_tot.png"
            
            plot_util.plot_Z_vs_f_simple(
                f=freqs,
                Z=Z,
                imped_type=imped_type,
                title=title,
                savedir=str(save_dir),
                savename=savename,
                xscale="log",
                yscale="log",
            )
        
        if not show:
            import matplotlib.pyplot as plt
            plt.close('all')

    # ------------------------------------------------------------------
    # Internal methods
    # ------------------------------------------------------------------

    def _load_input_data(self) -> None:
        """Load apertype and geometry files."""
        # Load aperture types
        self.apertypes = io_util.load_apertype(self.apertype_file)

        # Load geometry
        (
            self.b_list,
            self.L_list,
            self.betax_list,
            self.betay_list,
        ) = io_util.load_b_L_betax_betay(self.geom_file)

        # Validate lengths match
        n_aper = len(self.apertypes)
        n_geom = len(self.b_list)
        if n_aper != n_geom:
            raise ValueError(
                f"Mismatch: {n_aper} aperture types but {n_geom} geometry entries"
            )

        # Initialize frequency reference from first element
        if self.n_elements > 0:
            self._init_frequency_reference()

    def _init_frequency_reference(self) -> None:
        """Initialize the reference frequency object from the first element."""
        apertype = self.apertypes[0]
        cfg = self._get_cfg_handler(apertype)
        self._freq_obj_ref = cfg.read_freq()
        if self._freq_obj_ref is not None:
            self._freqs_array = self._freq_obj_ref.freq

    def _get_cfg_handler(self, apertype: str) -> CfgIo:
        """Get or create a CfgIo handler for the given aperture type."""
        key = apertype.lower()
        
        if key not in self._cfg_cache:
            cfg_filename = self._resolve_cfg_filename(apertype)
            cfg_path = self.input_dir / cfg_filename
            
            if not cfg_path.exists():
                raise FileNotFoundError(
                    f"Configuration file not found: {cfg_path}\n"
                    f"For aperture type '{apertype}', expected '{cfg_filename}'"
                )
            
            self._cfg_cache[key] = CfgIo(str(cfg_path))
        
        return self._cfg_cache[key]

    def _resolve_cfg_filename(self, apertype: str) -> str:
        """
        Resolve the cfg filename for an aperture type.
        
        First checks the mapping, then tries apertype + ".cfg"
        """
        # Check mapping (case-insensitive)
        for key, value in self.apertype_to_cfg.items():
            if key.lower() == apertype.lower():
                return value
        
        # Default: apertype + ".cfg"
        return f"{apertype}.cfg"

    def _build_wall_for_element(self, index: int) -> TlWall:
        """Build a TlWall object for one element."""
        apertype = self.apertypes[index]
        b = self.b_list[index]
        L = self.L_list[index]
        betax = self.betax_list[index]
        betay = self.betay_list[index]

        cfg = self._get_cfg_handler(apertype)
        chamber = cfg.read_chamber()
        beam = cfg.read_beam()

        if chamber is None or beam is None:
            raise RuntimeError(
                f"Incomplete configuration for aperture type '{apertype}'"
            )

        # Override geometry with per-element values
        chamber.pipe_len_m = L
        chamber.betax = betax
        chamber.betay = betay

        if hasattr(chamber, "pipe_rad_m"):
            chamber.pipe_rad_m = b
        if hasattr(chamber, "pipe_hor_m"):
            chamber.pipe_hor_m = b
        if hasattr(chamber, "pipe_ver_m"):
            chamber.pipe_ver_m = b

        # Apply Yokoya factors for rectangular chambers
        # Since we only have b (not separate hor/ver), we use theoretical factors
        if apertype.lower() == "rectangular":
            pi_sq = np.pi ** 2
            chamber.yokoya_drivx = pi_sq / 24.0
            chamber.yokoya_drivy = pi_sq / 12.0
            chamber.yokoya_detx = -pi_sq / 24.0
            chamber.yokoya_dety = pi_sq / 24.0

        wall = TlWall(chamber=chamber, beam=beam, frequencies=self._freq_obj_ref)
        return wall

    def _process_single_element(self, index: int, chambers_dir: Path) -> None:
        """Process a single element: calculate, save, accumulate, free."""
        # Build and calculate
        wall = self._build_wall_for_element(index)
        impedances = wall.get_all_impedances()
        
        # Save to file
        chamber_dir = chambers_dir / f"chamber_{index:03d}"
        chamber_dir.mkdir(exist_ok=True)
        
        output_path = chamber_dir / f"chamber_{index:03d}_impedances.xlsx"
        io_util.save_impedances_to_excel(
            freqs=self._freqs_array,
            imped_dict=impedances,
            output_path=output_path,
        )
        
        # Accumulate totals
        self._accumulate_impedances(impedances)
        
        # Free memory - don't keep the wall object
        del wall
        del impedances

    def _accumulate_impedances(self, impedances: Dict[str, np.ndarray]) -> None:
        """Add impedances to running totals."""
        for name, Z in impedances.items():
            if name not in self._total_impedances:
                self._total_impedances[name] = np.zeros_like(Z)
            self._total_impedances[name] += Z

    def _save_totals(self) -> None:
        """Save total impedances to file."""
        total_dir = self.out_dir / "total"
        total_dir.mkdir(exist_ok=True)
        
        output_path = total_dir / "total_impedances.xlsx"
        io_util.save_impedances_to_excel(
            freqs=self._freqs_array,
            imped_dict=self._total_impedances,
            output_path=output_path,
        )
        print(f"[MultipleChamber] Saved total impedances to {output_path}")

    @staticmethod
    def _is_non_trivial_impedance(Z: np.ndarray) -> bool:
        """Check if impedance is not all zeros or NaN."""
        if np.iscomplexobj(Z):
            mag = np.abs(Z)
        else:
            mag = np.asarray(Z)
        mask = ~np.isnan(mag)
        return mask.any() and np.any(mag[mask] != 0)

    @staticmethod
    def _guess_imped_type(name: str) -> str:
        """Guess impedance type from name."""
        name_lower = name.lower()
        if "long" in name_lower:
            return "long"
        elif "transx" in name_lower or "dipx" in name_lower:
            return "transx"
        elif "transy" in name_lower or "dipy" in name_lower:
            return "transy"
        elif "trans" in name_lower or "dip" in name_lower:
            return "trans"
        elif "quad" in name_lower:
            return "quad"
        return "long"
