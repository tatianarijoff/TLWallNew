"""
Chamber data model for pytlwall GUI.

This module provides a ChamberData class that bridges the GUI widgets
with the pytlwall configuration system (CfgIo). Each chamber in the GUI
maintains its own ChamberData instance with all cfg-related parameters.

Authors: Tatiana Rijoff
Date: December 2025
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import copy
# =============================================================================
# Default values for new chambers (matching ex_CW.cfg structure)
# =============================================================================

# [base_info] defaults
DEFAULT_COMPONENT_NAME = "newCW"
DEFAULT_PIPE_RADIUS_M = 0.0184
DEFAULT_PIPE_HOR_M = 0.0184
DEFAULT_PIPE_VER_M = 0.0184
DEFAULT_PIPE_LEN_M = 1.0
DEFAULT_BETAX = 1.0
DEFAULT_BETAY = 1.0
DEFAULT_CHAMBER_SHAPE = "CIRCULAR"

# [layer] defaults (standard layer)
DEFAULT_LAYER_TYPE = "CW"
DEFAULT_LAYER_THICK_M = 5e-7
DEFAULT_LAYER_MUINF_HZ = 0.0
DEFAULT_LAYER_K_HZ = float("inf")
DEFAULT_LAYER_SIGMA_DC = 1e6
DEFAULT_LAYER_EPSR = 1.0
DEFAULT_LAYER_TAU = 0.0
DEFAULT_LAYER_RQ = 0.0

# [boundary] defaults
DEFAULT_BOUNDARY_TYPE = "CW"
DEFAULT_BOUNDARY_MUINF_HZ = 0.0
DEFAULT_BOUNDARY_K_HZ = float("inf")
DEFAULT_BOUNDARY_SIGMA_DC = 1e9
DEFAULT_BOUNDARY_EPSR = 1.0
DEFAULT_BOUNDARY_TAU = 0.0
DEFAULT_BOUNDARY_RQ = 0.0

# [frequency_info] defaults
DEFAULT_FREQ_MODE = "range"  # "range" or "file"
DEFAULT_FMIN = 0.0
DEFAULT_FMAX = 12.0
DEFAULT_FSTEP = 2.0

# [frequency_file] defaults
DEFAULT_FREQ_FILENAME = ""
DEFAULT_FREQ_SEPARATOR = "whitespace"
DEFAULT_FREQ_COL = 0
DEFAULT_SKIP_ROWS = 0

# [beam_info] defaults
DEFAULT_TEST_BEAM_SHIFT = 0.01
DEFAULT_GAMMA_REL = 10000.0
DEFAULT_MASS_MEV_C2 = 938.272  # proton mass

# [output] defaults - which impedances to calculate
# ZLongTotal and ZTransTotal are the primary outputs (sum of all contributions)
DEFAULT_OUTPUT_LIST = [
    "ZLongTotal", "ZTransTotal",
    "ZLong", "ZTrans", "ZDipX", "ZDipY",
    "ZQuadX", "ZQuadY",
    "ZLongDSC", "ZLongISC", "ZTransDSC", "ZTransISC",
    "ZDipDSC", "ZDipISC",
]

# Default selection: ZLongTotal and ZTransTotal are the default outputs
# Basic impedances ON, DSC/ISC OFF
DEFAULT_OUTPUT_SELECTION = {
    "ZLongTotal": True,
    "ZTransTotal": True,
    "ZLong": False,
    "ZTrans": False,
    "ZDipX": False,
    "ZDipY": False,
    "ZQuadX": False,
    "ZQuadY": False,
    "ZLongDSC": False,
    "ZLongISC": False,
    "ZTransDSC": False,
    "ZTransISC": False,
    "ZDipDSC": False,
    "ZDipISC": False,
}


@dataclass
class LayerData:
    """
    Data container for a single material layer.

    Attributes:
        layer_type: Layer type ('CW', 'PEC', 'PMC', 'V').
                    Note: 'RW' in config files is converted to 'CW' on load.
        thick_m: Layer thickness in meters
        muinf_Hz: Magnetic permeability parameter
        k_Hz: Relaxation frequency for permeability in Hz
        sigmaDC: DC electrical conductivity in S/m
        epsr: Relative permittivity
        tau: Relaxation time for permittivity in seconds
        RQ: Surface roughness parameter in meters
    """
    layer_type: str = DEFAULT_LAYER_TYPE
    thick_m: float = DEFAULT_LAYER_THICK_M
    muinf_Hz: float = DEFAULT_LAYER_MUINF_HZ
    k_Hz: float = DEFAULT_LAYER_K_HZ
    sigmaDC: float = DEFAULT_LAYER_SIGMA_DC
    epsr: float = DEFAULT_LAYER_EPSR
    tau: float = DEFAULT_LAYER_TAU
    RQ: float = DEFAULT_LAYER_RQ

    def to_dict(self) -> Dict[str, Any]:
        """Convert layer data to dictionary for CfgIo compatibility."""
        return {
            "type": self.layer_type,
            "thick_m": self.thick_m,
            "muinf_Hz": self.muinf_Hz,
            "k_Hz": self.k_Hz,
            "sigmaDC": self.sigmaDC,
            "epsr": self.epsr,
            "tau": self.tau,
            "RQ": self.RQ,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LayerData":
        """Create LayerData from dictionary."""
        return cls(
            layer_type=data.get("type", DEFAULT_LAYER_TYPE),
            thick_m=data.get("thick_m", DEFAULT_LAYER_THICK_M),
            muinf_Hz=data.get("muinf_Hz", DEFAULT_LAYER_MUINF_HZ),
            k_Hz=data.get("k_Hz", DEFAULT_LAYER_K_HZ),
            sigmaDC=data.get("sigmaDC", DEFAULT_LAYER_SIGMA_DC),
            epsr=data.get("epsr", DEFAULT_LAYER_EPSR),
            tau=data.get("tau", DEFAULT_LAYER_TAU),
            RQ=data.get("RQ", DEFAULT_LAYER_RQ),
        )


@dataclass
class BoundaryData:
    """
    Data container for the boundary layer.

    Boundary layers never have thickness - they represent the outermost
    condition of the chamber (typically infinite extent).

    Attributes:
        layer_type: Boundary type ('CW', 'PEC', 'PMC', 'V').
                    Note: 'RW' in config files is converted to 'CW' on load.
        muinf_Hz: Magnetic permeability parameter
        k_Hz: Relaxation frequency for permeability in Hz
        sigmaDC: DC electrical conductivity in S/m
        epsr: Relative permittivity
        tau: Relaxation time for permittivity in seconds
        RQ: Surface roughness parameter in meters
    """
    layer_type: str = DEFAULT_BOUNDARY_TYPE
    muinf_Hz: float = DEFAULT_BOUNDARY_MUINF_HZ
    k_Hz: float = DEFAULT_BOUNDARY_K_HZ
    sigmaDC: float = DEFAULT_BOUNDARY_SIGMA_DC
    epsr: float = DEFAULT_BOUNDARY_EPSR
    tau: float = DEFAULT_BOUNDARY_TAU
    RQ: float = DEFAULT_BOUNDARY_RQ

    def to_dict(self) -> Dict[str, Any]:
        """Convert boundary data to dictionary for CfgIo compatibility."""
        return {
            "type": self.layer_type,
            "muinf_Hz": self.muinf_Hz,
            "k_Hz": self.k_Hz,
            "sigmaDC": self.sigmaDC,
            "epsr": self.epsr,
            "tau": self.tau,
            "RQ": self.RQ,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BoundaryData":
        """Create BoundaryData from dictionary."""
        return cls(
            layer_type=data.get("type", DEFAULT_BOUNDARY_TYPE),
            muinf_Hz=data.get("muinf_Hz", DEFAULT_BOUNDARY_MUINF_HZ),
            k_Hz=data.get("k_Hz", DEFAULT_BOUNDARY_K_HZ),
            sigmaDC=data.get("sigmaDC", DEFAULT_BOUNDARY_SIGMA_DC),
            epsr=data.get("epsr", DEFAULT_BOUNDARY_EPSR),
            tau=data.get("tau", DEFAULT_BOUNDARY_TAU),
            RQ=data.get("RQ", DEFAULT_BOUNDARY_RQ),
        )


@dataclass
class FrequencyData:
    """
    Data container for frequency configuration.

    Supports two modes:
    - Range mode: frequencies generated from fmin, fmax, fstep exponents
    - File mode: frequencies read from an external file

    Attributes:
        mode: Frequency mode ('range' or 'file')
        fmin: Minimum frequency exponent (for range mode)
        fmax: Maximum frequency exponent (for range mode)
        fstep: Step exponent (for range mode)
        filename: Path to frequency file (for file mode)
        separator: Column separator in file ('whitespace', ',', ';', 'tab')
        freq_col: Column index containing frequencies (for file mode)
        skip_rows: Number of header rows to skip (for file mode)
    """
    mode: str = DEFAULT_FREQ_MODE
    fmin: float = DEFAULT_FMIN
    fmax: float = DEFAULT_FMAX
    fstep: float = DEFAULT_FSTEP
    filename: str = DEFAULT_FREQ_FILENAME
    separator: str = DEFAULT_FREQ_SEPARATOR
    freq_col: int = DEFAULT_FREQ_COL
    skip_rows: int = DEFAULT_SKIP_ROWS

    def to_dict(self) -> Dict[str, Any]:
        """Convert frequency data to dictionary."""
        return {
            "mode": self.mode,
            "fmin": self.fmin,
            "fmax": self.fmax,
            "fstep": self.fstep,
            "filename": self.filename,
            "separator": self.separator,
            "freq_col": self.freq_col,
            "skip_rows": self.skip_rows,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FrequencyData":
        """Create FrequencyData from dictionary."""
        return cls(
            mode=data.get("mode", DEFAULT_FREQ_MODE),
            fmin=data.get("fmin", DEFAULT_FMIN),
            fmax=data.get("fmax", DEFAULT_FMAX),
            fstep=data.get("fstep", DEFAULT_FSTEP),
            filename=data.get("filename", DEFAULT_FREQ_FILENAME),
            separator=data.get("separator", DEFAULT_FREQ_SEPARATOR),
            freq_col=data.get("freq_col", DEFAULT_FREQ_COL),
            skip_rows=data.get("skip_rows", DEFAULT_SKIP_ROWS),
        )


@dataclass
class BeamData:
    """
    Data container for beam configuration.

    Attributes:
        test_beam_shift: Test beam distance offset in meters
        gammarel: Lorentz gamma factor
        mass_MeV_c2: Particle rest mass energy in MeV/c²
    """
    test_beam_shift: float = DEFAULT_TEST_BEAM_SHIFT
    gammarel: float = DEFAULT_GAMMA_REL
    mass_MeV_c2: float = DEFAULT_MASS_MEV_C2

    def to_dict(self) -> Dict[str, Any]:
        """Convert beam data to dictionary."""
        return {
            "test_beam_shift": self.test_beam_shift,
            "gammarel": self.gammarel,
            "mass_MeV_c2": self.mass_MeV_c2,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BeamData":
        """Create BeamData from dictionary."""
        return cls(
            test_beam_shift=data.get("test_beam_shift", DEFAULT_TEST_BEAM_SHIFT),
            gammarel=data.get("gammarel", DEFAULT_GAMMA_REL),
            mass_MeV_c2=data.get("mass_MeV_c2", DEFAULT_MASS_MEV_C2),
        )


@dataclass
class BaseInfoData:
    """
    Data container for chamber base geometry information.

    Attributes:
        component_name: Name identifier for the chamber component
        chamber_shape: Cross-section shape ('CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR')
        pipe_len_m: Pipe length in meters
        pipe_radius_m: Pipe radius in meters (for circular)
        pipe_hor_m: Horizontal half-aperture in meters
        pipe_ver_m: Vertical half-aperture in meters
        betax: Horizontal beta function at chamber location (m)
        betay: Vertical beta function at chamber location (m)
    """
    component_name: str = DEFAULT_COMPONENT_NAME
    chamber_shape: str = DEFAULT_CHAMBER_SHAPE
    pipe_len_m: float = DEFAULT_PIPE_LEN_M
    pipe_radius_m: float = DEFAULT_PIPE_RADIUS_M
    pipe_hor_m: float = DEFAULT_PIPE_HOR_M
    pipe_ver_m: float = DEFAULT_PIPE_VER_M
    betax: float = DEFAULT_BETAX
    betay: float = DEFAULT_BETAY

    def to_dict(self) -> Dict[str, Any]:
        """Convert base info to dictionary."""
        return {
            "component_name": self.component_name,
            "chamber_shape": self.chamber_shape,
            "pipe_len_m": self.pipe_len_m,
            "pipe_radius_m": self.pipe_radius_m,
            "pipe_hor_m": self.pipe_hor_m,
            "pipe_ver_m": self.pipe_ver_m,
            "betax": self.betax,
            "betay": self.betay,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseInfoData":
        """Create BaseInfoData from dictionary."""
        return cls(
            component_name=data.get("component_name", DEFAULT_COMPONENT_NAME),
            chamber_shape=data.get("chamber_shape", DEFAULT_CHAMBER_SHAPE),
            pipe_len_m=data.get("pipe_len_m", DEFAULT_PIPE_LEN_M),
            pipe_radius_m=data.get("pipe_radius_m", DEFAULT_PIPE_RADIUS_M),
            pipe_hor_m=data.get("pipe_hor_m", DEFAULT_PIPE_HOR_M),
            pipe_ver_m=data.get("pipe_ver_m", DEFAULT_PIPE_VER_M),
            betax=data.get("betax", DEFAULT_BETAX),
            betay=data.get("betay", DEFAULT_BETAY),
        )


@dataclass
class ChamberData:
    """
    Complete data container for a chamber configuration.

    This class holds all the data needed to create pytlwall objects
    via CfgIo. Each chamber in the GUI has one ChamberData instance.

    Attributes:
        id: Chamber identifier (e.g., "Chamber 1")
        base_info: Chamber geometry parameters
        layers: List of material layers
        boundary: Boundary layer configuration
        frequency: Frequency configuration
        beam: Beam parameters
        output_flags: Dictionary of impedance calculation flags
    """
    id: str = "Chamber 1"
    base_info: BaseInfoData = field(default_factory=BaseInfoData)
    layers: List[LayerData] = field(default_factory=lambda: [LayerData()])
    boundary: BoundaryData = field(default_factory=BoundaryData)
    frequency: FrequencyData = field(default_factory=FrequencyData)
    beam: BeamData = field(default_factory=BeamData)
    output_flags: Dict[str, bool] = field(default_factory=lambda: dict(DEFAULT_OUTPUT_SELECTION))

    @property
    def component_name(self) -> str:
        """Get component name from base_info."""
        return self.base_info.component_name

    @component_name.setter
    def component_name(self, value: str) -> None:
        """Set component name in base_info."""
        self.base_info.component_name = value

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert complete chamber data to nested dictionary.

        Returns:
            Dictionary with all chamber configuration data.
        """
        return {
            "id": self.id,
            "base_info": self.base_info.to_dict(),
            "layers": [layer.to_dict() for layer in self.layers],
            "boundary": self.boundary.to_dict(),
            "frequency": self.frequency.to_dict(),
            "beam": self.beam.to_dict(),
            "output_flags": dict(self.output_flags),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChamberData":
        """
        Create ChamberData from dictionary.

        Args:
            data: Dictionary with chamber configuration data.

        Returns:
            New ChamberData instance.
        """
        layers_data = data.get("layers", [{}])
        layers = [LayerData.from_dict(ld) for ld in layers_data]
        if not layers:
            layers = [LayerData()]

        output_flags = data.get("output_flags", {})
        default_flags = dict(DEFAULT_OUTPUT_SELECTION)
        default_flags.update(output_flags)

        return cls(
            id=data.get("id", "Chamber 1"),
            base_info=BaseInfoData.from_dict(data.get("base_info", {})),
            layers=layers,
            boundary=BoundaryData.from_dict(data.get("boundary", {})),
            frequency=FrequencyData.from_dict(data.get("frequency", {})),
            beam=BeamData.from_dict(data.get("beam", {})),
            output_flags=default_flags,
        )

    @classmethod
    def create_default(cls, chamber_id: str = "Chamber 1") -> "ChamberData":
        """
        Create a new ChamberData with default values.

        Args:
            chamber_id: Chamber identifier string.

        Returns:
            New ChamberData instance with defaults.
        """
        return cls(
            id=chamber_id,
            base_info=BaseInfoData(component_name=chamber_id),
            layers=[LayerData()],
            boundary=BoundaryData(),
            frequency=FrequencyData(),
            beam=BeamData(),
            output_flags=dict(DEFAULT_OUTPUT_SELECTION),
        )
    @classmethod
    def duplicate(
        cls,
        chamber: "ChamberData",
        new_id: Optional[str] = None,
        component_name_suffix: str = "_copy",
    ) -> "ChamberData":
        """Create a deep copy of a ChamberData instance.

        Deep-copies all nested dataclasses (layers, boundary, frequency,
        beam, output_flags). Optionally updates id and component_name.
        """
        new_chamber = copy.deepcopy(chamber)
        if new_id is not None:
            new_chamber.id = new_id
        if new_chamber.base_info.component_name:
            new_chamber.base_info.component_name = (
                f"{new_chamber.base_info.component_name}{component_name_suffix}"
            )
        return new_chamber

    @classmethod
    def from_cfgio(cls, cfg) -> Optional["ChamberData"]:
        """
        Create ChamberData from a pytlwall CfgIo object.

        This function reads configuration from a CfgIo instance and
        creates a ChamberData object with all the extracted parameters.

        Args:
            cfg: CfgIo instance with loaded configuration.

        Returns:
            ChamberData instance or None if configuration is invalid.

        Note:
            Requires pytlwall to be installed. If not available, returns None.
        """
        try:
            from pytlwall.cfg_io import CfgIo
        except ImportError:
            print("Warning: pytlwall not installed, cannot read CfgIo")
            return None

        chamber_data = cls()

        # Read base_info
        if cfg.config.has_section('base_info'):
            base = chamber_data.base_info
            base.component_name = cfg.config.get('base_info', 'component_name',
                                                  fallback=DEFAULT_COMPONENT_NAME)
            base.chamber_shape = cfg.config.get('base_info', 'chamber_shape',
                                                fallback=DEFAULT_CHAMBER_SHAPE)
            base.pipe_len_m = cfg.config.getfloat('base_info', 'pipe_len_m',
                                                   fallback=DEFAULT_PIPE_LEN_M)
            base.betax = cfg.config.getfloat('base_info', 'betax',
                                             fallback=DEFAULT_BETAX)
            base.betay = cfg.config.getfloat('base_info', 'betay',
                                             fallback=DEFAULT_BETAY)

            # Handle pipe dimensions
            if cfg.config.has_option('base_info', 'pipe_radius_m'):
                radius = cfg.config.getfloat('base_info', 'pipe_radius_m')
                base.pipe_radius_m = radius
                base.pipe_hor_m = radius
                base.pipe_ver_m = radius
            else:
                base.pipe_ver_m = cfg.config.getfloat('base_info', 'pipe_ver_m',
                                                       fallback=DEFAULT_PIPE_VER_M)
                base.pipe_hor_m = cfg.config.getfloat('base_info', 'pipe_hor_m',
                                                       fallback=base.pipe_ver_m)
                base.pipe_radius_m = base.pipe_ver_m

        # Read layers
        if cfg.config.has_section('layers_info'):
            nbr_layers = cfg.config.getint('layers_info', 'nbr_layers', fallback=1)
            chamber_data.layers = []

            for i in range(nbr_layers):
                section = f'layer{i}'
                if cfg.config.has_section(section):
                    layer = LayerData()
                    layer.layer_type = cfg.config.get(section, 'type',
                                                       fallback=DEFAULT_LAYER_TYPE)

                    # Convert RW to CW (RW is an alias for CW)
                    if layer.layer_type == 'RW':
                        layer.layer_type = 'CW'

                    # Handle thickness (support both thick_m and thick_M)
                    if cfg.config.has_option(section, 'thick_m'):
                        thick_str = cfg.config.get(section, 'thick_m')
                        layer.thick_m = float('inf') if thick_str.lower() == 'inf' else float(thick_str)
                    elif cfg.config.has_option(section, 'thick_M'):
                        thick_str = cfg.config.get(section, 'thick_M')
                        layer.thick_m = float('inf') if thick_str.lower() == 'inf' else float(thick_str)

                    # Read CW parameters if applicable
                    if layer.layer_type == 'CW':
                        layer.muinf_Hz = cfg.config.getfloat(section, 'muinf_Hz',
                                                             fallback=DEFAULT_LAYER_MUINF_HZ)
                        k_str = cfg.config.get(section, 'k_Hz', fallback='inf')
                        layer.k_Hz = float('inf') if k_str in ('0', '0.0', 'inf') else float(k_str)
                        layer.sigmaDC = cfg.config.getfloat(section, 'sigmaDC',
                                                             fallback=DEFAULT_LAYER_SIGMA_DC)
                        layer.epsr = cfg.config.getfloat(section, 'epsr',
                                                          fallback=DEFAULT_LAYER_EPSR)
                        layer.tau = cfg.config.getfloat(section, 'tau',
                                                         fallback=DEFAULT_LAYER_TAU)
                        layer.RQ = cfg.config.getfloat(section, 'RQ',
                                                        fallback=DEFAULT_LAYER_RQ)

                    chamber_data.layers.append(layer)

            if not chamber_data.layers:
                chamber_data.layers = [LayerData()]

        # Read boundary
        if cfg.config.has_section('boundary'):
            boundary = chamber_data.boundary
            boundary.layer_type = cfg.config.get('boundary', 'type',
                                                  fallback=DEFAULT_BOUNDARY_TYPE)

            # Convert RW to CW (RW is an alias for CW)
            if boundary.layer_type == 'RW':
                boundary.layer_type = 'CW'

            if boundary.layer_type == 'CW':
                boundary.muinf_Hz = cfg.config.getfloat('boundary', 'muinf_Hz',
                                                         fallback=DEFAULT_BOUNDARY_MUINF_HZ)
                k_str = cfg.config.get('boundary', 'k_Hz', fallback='inf')
                boundary.k_Hz = float('inf') if k_str in ('0', '0.0', 'inf') else float(k_str)
                boundary.sigmaDC = cfg.config.getfloat('boundary', 'sigmaDC',
                                                        fallback=DEFAULT_BOUNDARY_SIGMA_DC)
                boundary.epsr = cfg.config.getfloat('boundary', 'epsr',
                                                     fallback=DEFAULT_BOUNDARY_EPSR)
                boundary.tau = cfg.config.getfloat('boundary', 'tau',
                                                    fallback=DEFAULT_BOUNDARY_TAU)
                boundary.RQ = cfg.config.getfloat('boundary', 'RQ',
                                                   fallback=DEFAULT_BOUNDARY_RQ)

        # Read frequency
        if cfg.config.has_section('frequency_file'):
            chamber_data.frequency.mode = "file"
            chamber_data.frequency.filename = cfg.config.get('frequency_file', 'filename',
                                                              fallback=DEFAULT_FREQ_FILENAME)
            sep = cfg.config.get('frequency_file', 'separator', fallback='')
            chamber_data.frequency.separator = sep if sep else "whitespace"
            chamber_data.frequency.freq_col = cfg.config.getint('frequency_file', 'freq_col',
                                                                 fallback=DEFAULT_FREQ_COL)
            chamber_data.frequency.skip_rows = cfg.config.getint('frequency_file', 'skip_rows',
                                                                  fallback=DEFAULT_SKIP_ROWS)
        elif cfg.config.has_section('frequency_info'):
            chamber_data.frequency.mode = "range"
            chamber_data.frequency.fmin = cfg.config.getfloat('frequency_info', 'fmin',
                                                               fallback=DEFAULT_FMIN)
            chamber_data.frequency.fmax = cfg.config.getfloat('frequency_info', 'fmax',
                                                               fallback=DEFAULT_FMAX)
            chamber_data.frequency.fstep = cfg.config.getfloat('frequency_info', 'fstep',
                                                                fallback=DEFAULT_FSTEP)

        # Read beam
        if cfg.config.has_section('beam_info'):
            chamber_data.beam.test_beam_shift = cfg.config.getfloat(
                'beam_info', 'test_beam_shift', fallback=DEFAULT_TEST_BEAM_SHIFT
            )
            # Priority: gammarel > betarel > Ekin_MeV
            if cfg.config.has_option('beam_info', 'gammarel'):
                chamber_data.beam.gammarel = cfg.config.getfloat('beam_info', 'gammarel')

            if cfg.config.has_option('beam_info', 'mass_MeV_c2'):
                chamber_data.beam.mass_MeV_c2 = cfg.config.getfloat('beam_info', 'mass_MeV_c2')

        return chamber_data



    def to_cfgio(self, cfg) -> None:
        """Write this chamber to a pytlwall CfgIo object.

        Args:
            cfg: CfgIo instance to write to.
        """
        # Save base_info
        if not cfg.config.has_section('base_info'):
            cfg.config.add_section('base_info')

        base = self.base_info
        cfg.config.set('base_info', 'component_name', base.component_name)
        cfg.config.set('base_info', 'chamber_shape', base.chamber_shape)
        cfg.config.set('base_info', 'pipe_len_m', str(base.pipe_len_m))
        cfg.config.set('base_info', 'betax', str(base.betax))
        cfg.config.set('base_info', 'betay', str(base.betay))

        if base.chamber_shape == 'CIRCULAR':
            cfg.config.set('base_info', 'pipe_radius_m', str(base.pipe_radius_m))
        else:
            cfg.config.set('base_info', 'pipe_hor_m', str(base.pipe_hor_m))
            cfg.config.set('base_info', 'pipe_ver_m', str(base.pipe_ver_m))

        print(f"DEBUG to_cfgio: shape={base.chamber_shape}, pipe_hor_m={base.pipe_hor_m}, pipe_ver_m={base.pipe_ver_m}, pipe_radius_m={base.pipe_radius_m}")
        # Save layers_info
        if not cfg.config.has_section('layers_info'):
            cfg.config.add_section('layers_info')

        cfg.config.set('layers_info', 'nbr_layers', str(len(self.layers)))

        for i, layer in enumerate(self.layers):
            section = f'layer{i}'
            if not cfg.config.has_section(section):
                cfg.config.add_section(section)

            cfg.config.set(section, 'type', layer.layer_type)

            if layer.thick_m == float('inf'):
                cfg.config.set(section, 'thick_m', 'inf')
            else:
                cfg.config.set(section, 'thick_m', str(layer.thick_m))

            # CW type has additional parameters (RW is converted to CW on load)
            if layer.layer_type == 'CW':
                cfg.config.set(section, 'muinf_Hz', str(layer.muinf_Hz))
                cfg.config.set(section, 'k_Hz', str(layer.k_Hz) if layer.k_Hz != float('inf') else '0')
                cfg.config.set(section, 'sigmaDC', str(layer.sigmaDC))
                cfg.config.set(section, 'epsr', str(layer.epsr))
                cfg.config.set(section, 'tau', str(layer.tau))
                cfg.config.set(section, 'RQ', str(layer.RQ))

        # Save boundary
        if not cfg.config.has_section('boundary'):
            cfg.config.add_section('boundary')

        boundary = self.boundary
        cfg.config.set('boundary', 'type', boundary.layer_type)

        # CW type has additional parameters (RW is converted to CW on load)
        if boundary.layer_type == 'CW':
            cfg.config.set('boundary', 'muinf_Hz', str(boundary.muinf_Hz))
            cfg.config.set('boundary', 'k_Hz', str(boundary.k_Hz) if boundary.k_Hz != float('inf') else '0')
            cfg.config.set('boundary', 'sigmaDC', str(boundary.sigmaDC))
            cfg.config.set('boundary', 'epsr', str(boundary.epsr))
            cfg.config.set('boundary', 'tau', str(boundary.tau))
            cfg.config.set('boundary', 'RQ', str(boundary.RQ))

        # Save frequency
        freq = self.frequency
        if freq.mode == "file":
            if not cfg.config.has_section('frequency_file'):
                cfg.config.add_section('frequency_file')
            cfg.config.set('frequency_file', 'filename', freq.filename)
            cfg.config.set('frequency_file', 'separator', freq.separator)
            cfg.config.set('frequency_file', 'freq_col', str(freq.freq_col))
            cfg.config.set('frequency_file', 'skip_rows', str(freq.skip_rows))
        else:
            if not cfg.config.has_section('frequency_info'):
                cfg.config.add_section('frequency_info')
            cfg.config.set('frequency_info', 'fmin', str(int(freq.fmin)))
            cfg.config.set('frequency_info', 'fmax', str(int(freq.fmax)))
            cfg.config.set('frequency_info', 'fstep', str(int(freq.fstep)))

        # Save beam
        if not cfg.config.has_section('beam_info'):
            cfg.config.add_section('beam_info')

        beam = self.beam
        cfg.config.set('beam_info', 'test_beam_shift', str(beam.test_beam_shift))
        cfg.config.set('beam_info', 'gammarel', str(beam.gammarel))
        cfg.config.set('beam_info', 'mass_MeV_c2', str(beam.mass_MeV_c2))



    def add_layer(self) -> LayerData:
        """
        Add a new layer with default values.

        Returns:
            The newly created LayerData instance.
        """
        new_layer = LayerData()
        self.layers.append(new_layer)
        return new_layer

    def remove_layer(self, index: int) -> bool:
        """
        Remove layer at specified index.

        Args:
            index: Index of layer to remove.

        Returns:
            True if layer was removed, False if index was invalid.
        """
        if 0 <= index < len(self.layers):
            self.layers.pop(index)
            return True
        return False

    @property
    def nbr_layers(self) -> int:
        """Get number of layers (excluding boundary)."""
        return len(self.layers)



def create_chamber_from_cfgio(cfg) -> Optional[ChamberData]:
    """Backward-compatible wrapper for ChamberData.from_cfgio()."""
    return ChamberData.from_cfgio(cfg)


def save_chamber_to_cfgio(chamber_data: ChamberData, cfg) -> None:
    """Backward-compatible wrapper for ChamberData.to_cfgio()."""
    chamber_data.to_cfgio(cfg)

