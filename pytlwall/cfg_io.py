"""
Configuration I/O for pytlwall package.

This module provides classes for reading and writing pytlwall configurations
from/to INI-style configuration files.

Authors: Tatiana Rijoff, Carlo Zannini
Date:    01/03/2013
Revised: December 2025
Copyright: CERN
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import configparser

from pytlwall.chamber import Chamber
from pytlwall.beam import Beam
from pytlwall.frequencies import Frequencies
from pytlwall.layer import Layer
from pytlwall.tlwall import TlWall


class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass


class CfgIo:
    """
    Configuration I/O handler for pytlwall.
    
    This class handles reading pytlwall configurations from INI files and
    writing configurations back to files. It supports chamber, beam, frequency,
    and output specifications.
    
    Attributes:
        config: ConfigParser object containing the configuration
        list_output: List of impedance types to calculate
        file_output: Dictionary of file output specifications
        img_output: Dictionary of image output specifications
    
    Example:
        >>> from pytlwall.cfg_io import CfgIo
        >>> 
        >>> # Read configuration
        >>> cfg = CfgIo('config.ini')
        >>> chamber = cfg.read_chamber()
        >>> beam = cfg.read_beam()
        >>> freq = cfg.read_freq()
        >>> 
        >>> # Create TlWall and calculate
        >>> wall = pytlwall.TlWall(chamber, beam, freq)
        >>> ZLong = wall.calc_ZLong()
    """
    
    def __init__(self, cfg_file: Optional[str] = None):
        """
        Initialize configuration handler.
        
        Args:
            cfg_file: Path to configuration file (optional)
        """
        # Allow both '=' and ':' as delimiters for compatibility
        self.config = configparser.ConfigParser(delimiters=('=', ':'))
        
        # Output specifications
        self.list_output: List[str] = []
        self.file_output: Dict[str, Dict[str, Any]] = {}
        self.img_output: Dict[str, Dict[str, Any]] = {}
        
        if cfg_file is not None:
            self.read_cfg(cfg_file)
    
    # =========================================================================
    # Path Resolution
    # =========================================================================
    
    @property
    def main_path(self) -> Optional[Path]:
        """
        Get main_path from configuration.
        
        Returns:
            Path object or None if not configured
        """
        if self.config.has_section('path_info'):
            path_str = self.config.get('path_info', 'main_path', fallback='')
            if path_str:
                return Path(path_str)
        return None
    
    def resolve_path(self, filename: str) -> Path:
        """
        Resolve a filename to a full path.
        
        If filename is absolute, returns it as-is.
        If filename is relative, tries to resolve against main_path.
        
        Args:
            filename: File name or path to resolve
            
        Returns:
            Resolved Path object
        """
        file_path = Path(filename)
        
        # If absolute or exists as-is, return it
        if file_path.is_absolute() or file_path.exists():
            return file_path
        
        # Try with main_path
        if self.main_path is not None:
            resolved = self.main_path / filename
            if resolved.exists():
                return resolved
        
        # Return original (will likely fail later with better error message)
        return file_path
    
    # =========================================================================
    # Core I/O Methods
    # =========================================================================
    
    def read_cfg(self, cfg_file: str) -> None:
        """
        Read configuration from INI file.
        
        Args:
            cfg_file: Path to configuration file
        
        Raises:
            ConfigurationError: If file doesn't exist
        """
        cfg_path = Path(cfg_file)
        if not cfg_path.exists():
            raise ConfigurationError(
                f"Configuration file '{cfg_file}' does not exist"
            )
        
        self.config.read(cfg_file)
    
    # =========================================================================
    # Chamber Reading
    # =========================================================================
    
    def read_chamber(self, cfg_file: Optional[str] = None) -> Optional[Chamber]:
        """
        Read chamber configuration from file.
        
        Args:
            cfg_file: Path to configuration file (optional if already loaded)
        
        Returns:
            Chamber object or None if section not found
        
        Example:
            >>> cfg = CfgIo('config.ini')
            >>> chamber = cfg.read_chamber()
            >>> print(f"Chamber: {chamber.chamber_shape}, r={chamber.pipe_rad_m}m")
        """
        if cfg_file is not None:
            self.read_cfg(cfg_file)
        
        if not self.config.has_section('base_info'):
            return None
        
        # Read base chamber parameters
        pipe_len_m = self.config.getfloat('base_info', 'pipe_len_m')
        chamber_shape_raw = self.config.get('base_info', 'chamber_shape')
        
        # Normalize chamber shape names (support common aliases)
        # Valid shapes: CIRCULAR, ELLIPTICAL, RECTANGULAR
        # Aliases: ROUND -> CIRCULAR, ELLIPTIC -> ELLIPTICAL, RECT -> RECTANGULAR
        SHAPE_ALIASES = {
            'ROUND': 'CIRCULAR',
            'ELLIPTIC': 'ELLIPTICAL',
            'RECT': 'RECTANGULAR',
            'RECTANGLE': 'RECTANGULAR'
        }
        chamber_shape = SHAPE_ALIASES.get(chamber_shape_raw, chamber_shape_raw)
        
        betax = self.config.getfloat('base_info', 'betax')
        betay = self.config.getfloat('base_info', 'betay')
        
        # Component name (optional)
        component_name = self.config.get(
            'base_info', 'component_name', fallback='chamber'
        )
        
        # Pipe dimensions
        if self.config.has_option('base_info', 'pipe_radius_m'):
            pipe_rad_m = self.config.getfloat('base_info', 'pipe_radius_m')
            pipe_hor_m = pipe_rad_m
            pipe_ver_m = pipe_rad_m
        else:
            # For non-circular chambers, read hor and ver separately
            pipe_ver_m = self.config.getfloat('base_info', 'pipe_ver_m')
            pipe_hor_m = pipe_ver_m  # default, will be overwritten if pipe_hor_m exists
            
            if self.config.has_option('base_info', 'pipe_hor_m'):
                pipe_hor_m = self.config.getfloat('base_info', 'pipe_hor_m')
            
            # For non-circular, use smaller dimension as radius for calculations
            pipe_rad_m = min(pipe_hor_m, pipe_ver_m)
        
        # Read layers
        layers = self._read_layers()
        
        # Create chamber
        chamber = Chamber(
            pipe_len_m=pipe_len_m,
            pipe_rad_m=pipe_rad_m,
            pipe_hor_m=pipe_hor_m,
            pipe_ver_m=pipe_ver_m,
            chamber_shape=chamber_shape,
            betax=betax,
            betay=betay,
            layers=layers,
            component_name=component_name
        )
        
        return chamber
    
    def _read_layers(self) -> List[Layer]:
        """
        Read layer configurations.
        
        Returns:
            List of Layer objects
        
        Raises:
            ConfigurationError: If layers_info section not found
        """
        if not self.config.has_section('layers_info'):
            raise ConfigurationError("Section 'layers_info' not found")
        
        nbr_layers = self.config.getint('layers_info', 'nbr_layers')
        layers = []
        
        # Read regular layers
        for i in range(nbr_layers):
            layer = self._read_single_layer(f'layer{i}', boundary=False)
            layers.append(layer)
        
        # Read boundary layer
        boundary_layer = self._read_single_layer('boundary', boundary=True)
        layers.append(boundary_layer)
        
        return layers
    
    def _read_single_layer(self, section: str, boundary: bool) -> Layer:
        """
        Read a single layer configuration.
        
        Args:
            section: Configuration section name
            boundary: Whether this is a boundary layer
        
        Returns:
            Layer object
        
        Note:
            Supports thick_m = inf for semi-infinite layers
            Boundary layers NEVER have thickness regardless of type
        """
        layer_type = self.config.get(section, 'type')
        
        # CRITICAL: Boundaries NEVER have thickness, regardless of type
        if boundary:
            # CW and RW boundaries need CW parameters but NO thickness
            if layer_type in ('CW', 'RW'):
                # Handle k_Hz = 0 (should be inf)
                k_Hz_str = self.config.get(section, 'k_Hz')
                if k_Hz_str == '0' or k_Hz_str == '0.0':
                    k_Hz = float('inf')
                else:
                    k_Hz = self.config.getfloat(section, 'k_Hz')
                
                # For RW, Layer class expects 'CW' as type
                effective_type = 'CW'
                
                return Layer(
                    layer_type=effective_type,
                    muinf_Hz=self.config.getfloat(section, 'muinf_Hz'),
                    epsr=self.config.getfloat(section, 'epsr'),
                    sigmaDC=self.config.getfloat(section, 'sigmaDC'),
                    k_Hz=k_Hz,
                    tau=self.config.getfloat(section, 'tau'),
                    RQ=self.config.getfloat(section, 'RQ'),
                    boundary=True
                )
            else:
                # PEC, PMC, V boundaries - just type
                return Layer(layer_type=layer_type, boundary=True)
        
        # Regular layers (non-boundary) MUST have thickness
        # Support both thick_m and thick_M (case variations in config files)
        if self.config.has_option(section, 'thick_m'):
            thick_str = self.config.get(section, 'thick_m')
            # Handle 'inf' as infinite thickness
            if thick_str.lower() == 'inf':
                thick_m = float('inf')
            else:
                thick_m = float(thick_str)
        elif self.config.has_option(section, 'thick_M'):
            thick_str = self.config.get(section, 'thick_M')
            if thick_str.lower() == 'inf':
                thick_m = float('inf')
            else:
                thick_m = float(thick_str)
        else:
            thick_m = 0.001  # Default 1mm if not specified
        
        # CW and RW have the same parameters
        if layer_type in ('CW', 'RW'):
            # Cole-Cole-Wideband or Resistive-Wall material
            # Handle k_Hz = 0 (should be inf)
            k_Hz_str = self.config.get(section, 'k_Hz')
            if k_Hz_str == '0' or k_Hz_str == '0.0':
                k_Hz = float('inf')
            else:
                k_Hz = self.config.getfloat(section, 'k_Hz')
            
            # For RW, Layer class expects 'CW' as type
            # (RW is handled internally by Layer as a variant of CW)
            effective_type = 'CW'  # Layer class uses 'CW' for both CW and RW
            
            layer = Layer(
                layer_type=effective_type,
                thick_m=thick_m,
                muinf_Hz=self.config.getfloat(section, 'muinf_Hz'),
                epsr=self.config.getfloat(section, 'epsr'),
                sigmaDC=self.config.getfloat(section, 'sigmaDC'),
                k_Hz=k_Hz,
                tau=self.config.getfloat(section, 'tau'),
                RQ=self.config.getfloat(section, 'RQ'),
                boundary=False
            )
        else:
            # Simple material (V, PEC, PMC)
            layer = Layer(
                layer_type=layer_type,
                thick_m=thick_m,
                boundary=False
            )
        
        return layer
    
    # =========================================================================
    # Beam Reading
    # =========================================================================
    
    def read_beam(self, cfg_file: Optional[str] = None) -> Optional[Beam]:
        """
        Read beam configuration from file.
        
        Args:
            cfg_file: Path to configuration file (optional if already loaded)
        
        Returns:
            Beam object or None if section not found
        
        Example:
            >>> cfg = CfgIo('config.ini')
            >>> beam = cfg.read_beam()
            >>> print(f"Beam: gamma={beam.gammarel:.2f}")
        """
        if cfg_file is not None:
            self.read_cfg(cfg_file)
        
        if not self.config.has_section('beam_info'):
            return None
        
        # Read test beam shift
        test_beam_shift = self.config.getfloat('beam_info', 'test_beam_shift')
        
        # Read mass (optional)
        mass_MeV_c2 = self.config.getfloat(
            'beam_info', 'mass_MeV_c2', fallback=None
        )
        
        # Priority order: betarel > gammarel > Ekin_MeV > p_MeV_c
        if self.config.has_option('beam_info', 'betarel'):
            betarel = self.config.getfloat('beam_info', 'betarel')
            beam = Beam(
                betarel=betarel,
                test_beam_shift=test_beam_shift,
                mass_MeV_c2=mass_MeV_c2
            ) if mass_MeV_c2 else Beam(
                betarel=betarel,
                test_beam_shift=test_beam_shift
            )
        
        elif self.config.has_option('beam_info', 'gammarel'):
            gammarel = self.config.getfloat('beam_info', 'gammarel')
            beam = Beam(
                gammarel=gammarel,
                test_beam_shift=test_beam_shift,
                mass_MeV_c2=mass_MeV_c2
            ) if mass_MeV_c2 else Beam(
                gammarel=gammarel,
                test_beam_shift=test_beam_shift
            )
        
        elif self.config.has_option('beam_info', 'Ekin_MeV'):
            Ekin_MeV = self.config.getfloat('beam_info', 'Ekin_MeV')
            beam = Beam(
                Ekin_MeV=Ekin_MeV,
                test_beam_shift=test_beam_shift,
                mass_MeV_c2=mass_MeV_c2
            ) if mass_MeV_c2 else Beam(
                Ekin_MeV=Ekin_MeV,
                test_beam_shift=test_beam_shift
            )
        
        elif self.config.has_option('beam_info', 'p_MeV_c'):
            p_MeV_c = self.config.getfloat('beam_info', 'p_MeV_c')
            beam = Beam(
                p_MeV_c=p_MeV_c,
                test_beam_shift=test_beam_shift,
                mass_MeV_c2=mass_MeV_c2
            ) if mass_MeV_c2 else Beam(
                p_MeV_c=p_MeV_c,
                test_beam_shift=test_beam_shift
            )
        
        else:
            raise ConfigurationError(
                "No valid beam parameter found in beam_info section"
            )
        
        return beam
    
    # =========================================================================
    # Frequency Reading
    # =========================================================================
    
    def read_freq(self, cfg_file: Optional[str] = None) -> Frequencies:
        """
        Read frequency configuration from file.
        
        Args:
            cfg_file: Path to configuration file (optional if already loaded)
        
        Returns:
            Frequencies object
        
        Example:
            >>> cfg = CfgIo('config.ini')
            >>> freq = cfg.read_freq()
            >>> print(f"Frequencies: {len(freq)} points")
        
        Note:
            Supports two modes:
            1. [frequency_info]: fmin, fmax, fstep (generates range)
            2. [frequency_file]: reads from external file
            
            For frequency_file mode, if filename is relative, it is resolved
            relative to main_path (from [path_info] section) if available.
        """
        if cfg_file is not None:
            self.read_cfg(cfg_file)
        
        # Priority 1: frequency_file section (read from file)
        if self.config.has_section('frequency_file'):
            import numpy as np
            
            filename = self.config.get('frequency_file', 'filename')
            
            # Handle separator
            sep = self.config.get('frequency_file', 'separator', fallback='')
            if sep == '' or sep.lower() == 'whitespace':
                sep = None  # Use whitespace delimiter
            
            freq_col = self.config.getint('frequency_file', 'freq_col', fallback=0)
            skip_rows = self.config.getint('frequency_file', 'skip_rows', fallback=0)
            
            # Resolve file path - use main_path if filename is relative
            file_path = self.resolve_path(filename)
            
            if not file_path.exists():
                raise ConfigurationError(f"Frequency file not found: {filename}")
            
            # Load data
            if sep is None:
                data = np.loadtxt(file_path, skiprows=skip_rows)
            else:
                data = np.loadtxt(file_path, skiprows=skip_rows, delimiter=sep)
            
            # Extract frequency column
            if data.ndim == 1:
                freqs = data
            else:
                freqs = data[:, freq_col]
            
            # Create Frequencies object with custom array
            freq = Frequencies()
            freq._freq = freqs  # Use private attribute since freq is read-only property
            
            # Store metadata for potential saving
            if not hasattr(freq, 'filename'):
                freq.filename = filename
            if not hasattr(freq, 'freq_column'):
                freq.freq_column = freq_col
            if not hasattr(freq, 'skipped_rows'):
                freq.skipped_rows = skip_rows
            
            return freq
        
        # Priority 2: frequency_info section (generate range)
        elif self.config.has_section('frequency_info'):
            fmin = self.config.getfloat('frequency_info', 'fmin')
            fmax = self.config.getfloat('frequency_info', 'fmax')
            fstep = self.config.getfloat('frequency_info', 'fstep')
            freq = Frequencies(fmin=fmin, fmax=fmax, fstep=fstep)
            return freq
        
        # Default: return default Frequencies
        else:
            freq = Frequencies()
            return freq
    
    # =========================================================================
    # Chamber Writing
    # =========================================================================
    
    def save_chamber(self, chamber: Chamber) -> None:
        """
        Save chamber configuration to config object.
        
        Args:
            chamber: Chamber object to save
        """
        if not self.config.has_section('base_info'):
            self.config.add_section('base_info')
        
        self.config.set('base_info', 'component_name', chamber.component_name)
        self.config.set('base_info', 'chamber_shape', chamber.chamber_shape)
        self.config.set('base_info', 'pipe_len_m', str(chamber.pipe_len_m))
        self.config.set('base_info', 'betax', str(chamber.betax))
        self.config.set('base_info', 'betay', str(chamber.betay))
        
        # Save dimensions based on shape
        if chamber.chamber_shape == 'CIRCULAR':
            self.config.set('base_info', 'pipe_radius_m', str(chamber.pipe_rad_m))
        else:
            self.config.set('base_info', 'pipe_hor_m', str(chamber.pipe_hor_m))
            self.config.set('base_info', 'pipe_ver_m', str(chamber.pipe_ver_m))
    
    def save_layer(self, layers: List[Layer]) -> None:
        """
        Save layer configurations to config object.
        
        Args:
            layers: List of Layer objects to save
        """
        if not self.config.has_section('layers_info'):
            self.config.add_section('layers_info')
        
        # Save number of regular layers (excluding boundary)
        self.config.set('layers_info', 'nbr_layers', str(len(layers) - 1))
        
        # Save regular layers
        for i in range(len(layers) - 1):
            section = f'layer{i}'
            if not self.config.has_section(section):
                self.config.add_section(section)
            
            self._save_single_layer(section, layers[i])
        
        # Save boundary layer
        if not self.config.has_section('boundary'):
            self.config.add_section('boundary')
        self._save_single_layer('boundary', layers[-1])
    
    def _save_single_layer(self, section: str, layer: Layer) -> None:
        """
        Save a single layer to configuration.
        
        Args:
            section: Configuration section name
            layer: Layer object to save
        """
        self.config.set(section, 'type', layer.layer_type)
        
        # Only save thickness for non-boundary layers
        # Check if boundary attribute exists (for backward compatibility)
        is_boundary = getattr(layer, 'boundary', False)
        if not is_boundary and layer.thick_m is not None:
            if layer.thick_m == float('inf'):
                self.config.set(section, 'thick_m', 'inf')
            else:
                self.config.set(section, 'thick_m', str(layer.thick_m))
        
        # Save CW parameters if applicable
        if layer.layer_type == 'CW':
            self.config.set(section, 'muinf_Hz', str(layer.muinf_Hz))
            self.config.set(section, 'k_Hz', str(layer.k_Hz))
            self.config.set(section, 'sigmaDC', str(layer.sigmaDC))
            self.config.set(section, 'epsr', str(layer.epsr))
            self.config.set(section, 'tau', str(layer.tau))
            self.config.set(section, 'RQ', str(layer.RQ))
    
    # =========================================================================
    # Beam Writing
    # =========================================================================
    
    def save_beam(self, beam: Beam) -> None:
        """
        Save beam configuration to config object.
        
        Args:
            beam: Beam object to save
        """
        if not self.config.has_section('beam_info'):
            self.config.add_section('beam_info')
        
        self.config.set('beam_info', 'test_beam_shift', str(beam.test_beam_shift))
        self.config.set('beam_info', 'betarel', str(beam.betarel))
        self.config.set('beam_info', 'gammarel', str(beam.gammarel))
        self.config.set('beam_info', 'mass_MeV_c2', str(beam.mass_MeV_c2))
        self.config.set('beam_info', 'Ekin_MeV', str(beam.Ekin_MeV))
        self.config.set('beam_info', 'p_MeV_c', str(beam.p_MeV_c))
    
    # =========================================================================
    # Frequency Writing
    # =========================================================================
    
    def save_freq(self, freq: Frequencies) -> None:
        """
        Save frequency configuration to config object.
        
        Args:
            freq: Frequencies object to save
        """
        
        # Check if frequencies from file or range
        if hasattr(freq, 'filename'):
            if not self.config.has_section('frequency_file'):
                self.config.add_section('frequency_file')
            self.config.set('frequency_file', 'filename', freq.filename)
            self.config.set('frequency_file', 'freq_column', str(freq.freq_column))
            self.config.set('frequency_file', 'skipped_rows', str(freq.skipped_rows))
        else:
            if not self.config.has_section('frequency_info'):
                self.config.add_section('frequency_info')
            self.config.set('frequency_info', 'fmin', str(int(freq.fmin)))
            self.config.set('frequency_info', 'fmax', str(int(freq.fmax)))
            self.config.set('frequency_info', 'fstep', str(int(freq.fstep)))
    
    # =========================================================================
    # Output Configuration
    # =========================================================================
    
    def read_test_config(self, cfg_file: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Read test configuration section for validation.
        
        Args:
            cfg_file: Path to configuration file (optional if already loaded)
        
        Returns:
            Dictionary with test configuration or None if section missing
        
        Example:
            >>> cfg = CfgIo('config.cfg')
            >>> test_cfg = cfg.read_test_config()
            >>> if test_cfg:
            ...     print(f"Reference file: {test_cfg['ref_long_file']}")
        """
        if cfg_file is not None:
            self.read_cfg(cfg_file)
        
        if not self.config.has_section('test_config'):
            return None
        
        test_config = {
            'ref_long_file': self.config.get('test_config', 'ref_long_file'),
            'ref_long_skip_rows': self.config.getint('test_config', 'ref_long_skip_rows', fallback=1),
            'ref_trans_dip_file': self.config.get('test_config', 'ref_trans_dip_file'),
            'ref_trans_dip_skip_rows': self.config.getint('test_config', 'ref_trans_dip_skip_rows', fallback=1),
            'ref_trans_quad_file': self.config.get('test_config', 'ref_trans_quad_file'),
            'ref_trans_quad_skip_rows': self.config.getint('test_config', 'ref_trans_quad_skip_rows', fallback=1),
        }
        
        return test_config
    
    def read_output(self, cfg_file: Optional[str] = None) -> None:
        """
        Read output configuration from file.
        
        Args:
            cfg_file: Path to configuration file (optional if already loaded)
        
        Note:
            Sets self.list_output, self.file_output, and self.img_output
        """
        if cfg_file is not None:
            self.read_cfg(cfg_file)
        
        # List of available impedance types
        output_list = [
            'ZLong', 'ZTrans', 'ZDipX', 'ZDipY',
            'ZQuadX', 'ZQuadY', 'ZLongSurf', 'ZTransSurf',
            'ZLongDSC', 'ZLongISC', 'ZTransDSC', 'ZTransISC'
        ]
        
        # Read which impedances to calculate
        self.list_output = []
        for imped in output_list:
            if (self.config.has_option('output', imped) and
                self.config.getboolean('output', imped)):
                self.list_output.append(imped)
        
        # Read file output specifications
        self._read_file_outputs()
        
        # Read image output specifications
        self._read_image_outputs()
    
    def _read_file_outputs(self) -> None:
        """Read file output specifications from config."""
        self.file_output = {}
        i = 1
        
        while self.config.has_section(f'output{i}'):
            section = f'output{i}'
            filename = self.config.get(section, 'output_name')
            
            self.file_output[filename] = {
                'imped': [],
                'prefix': ''
            }
            
            # Check if using component name as prefix
            if (self.config.has_option(section, 'use_name_flag') and
                self.config.getboolean(section, 'use_name_flag')):
                self.file_output[filename]['prefix'] = self.config.get(
                    'base_info', 'component_name'
                )
            
            # Parse impedance list
            imped_list = self.config.get(section, 'output_list').split(',')
            for imped in imped_list:
                self.file_output[filename]['imped'].append(imped.strip())
            
            i += 1
    
    def _read_image_outputs(self) -> None:
        """Read image output specifications from config."""
        self.img_output = {}
        i = 1
        
        while self.config.has_section(f'img_output{i}'):
            section = f'img_output{i}'
            filename = self.config.get(section, 'img_name')
            
            self.img_output[filename] = {
                'imped': [],
                'prefix': '',
                'real_imag': 'both',
                'title': None,
                'xscale': 'lin',
                'yscale': 'lin'
            }
            
            # Check if using component name as prefix
            if (self.config.has_option(section, 'use_name_flag') and
                self.config.getboolean(section, 'use_name_flag')):
                self.img_output[filename]['prefix'] = self.config.get(
                    'base_info', 'component_name'
                )
            
            # Parse real/imag flag
            if self.config.has_option(section, 're_im_flag'):
                re_im = self.config.get(section, 're_im_flag').lower()
                if re_im in ['real', 'imag', 'both']:
                    self.img_output[filename]['real_imag'] = re_im
            
            # Parse optional parameters
            if self.config.has_option(section, 'title'):
                self.img_output[filename]['title'] = self.config.get(section, 'title')
            
            if self.config.has_option(section, 'xscale'):
                self.img_output[filename]['xscale'] = self.config.get(section, 'xscale')
            
            if self.config.has_option(section, 'yscale'):
                self.img_output[filename]['yscale'] = self.config.get(section, 'yscale')
            
            # Parse impedance list
            imped_list = self.config.get(section, 'imped_list').split(',')
            for imped in imped_list:
                self.img_output[filename]['imped'].append(imped.strip())
            
            i += 1
    
    def save_calc(self, list_calc: Dict[str, bool]) -> None:
        """
        Save calculation configuration.
        
        Args:
            list_calc: Dictionary mapping impedance names to boolean flags
        """
        self.list_output = []
        
        if not self.config.has_section('output'):
            self.config.add_section('output')
        
        for imped, calc in list_calc.items():
            self.config.set('output', imped, str(calc))
            if calc:
                self.list_output.append(imped)
    
    # =========================================================================
    # High-Level Operations
    # =========================================================================
    
    def read_pytlwall(self, cfg_file: Optional[str] = None) -> Optional[TlWall]:
        """
        Read complete pytlwall configuration and create TlWall object.
        
        Args:
            cfg_file: Path to configuration file (optional if already loaded)
        
        Returns:
            TlWall object or None if components missing
        
        Example:
            >>> cfg = CfgIo('config.ini')
            >>> wall = cfg.read_pytlwall()
            >>> ZLong = wall.ZLong  # Calculate longitudinal impedance
        """
        if cfg_file is not None:
            self.read_cfg(cfg_file)
        
        chamber = self.read_chamber()
        beam = self.read_beam()
        freq = self.read_freq()
        
        if chamber is not None and beam is not None and freq is not None:
            return TlWall(chamber, beam, freq)
        
        return None
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def write_cfg(self, filename: str) -> None:
        """
        Write configuration to file.
        
        Args:
            filename: Output file path
        """
        with open(filename, 'w') as f:
            self.config.write(f)
    
    def __repr__(self) -> str:
        """String representation of CfgIo object."""
        sections = list(self.config.sections())
        return f"CfgIo(sections={sections})"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        sections = list(self.config.sections())
        return f"CfgIo with {len(sections)} sections: {', '.join(sections)}"


if __name__ == "__main__":
    print("Configuration I/O module for pytlwall")
    print("Use: from pytlwall.cfg_io import CfgIo")
