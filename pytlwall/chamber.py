"""
Chamber module for pytlwall.

This module defines the Chamber class which represents vacuum chamber geometries
with different cross-sectional shapes (circular, elliptical, rectangular) and
their associated Yokoya factors for impedance calculations.

@authors: Tatiana Rijoff, Carlo Zannini (original)
          Refactored to modern Python standards
@date:    01/03/2013 (original), 2025 (refactored)
@copyright: CERN
"""

from typing import List, Optional, Union
from dataclasses import dataclass, field
import numpy as np
import numpy.typing as npt

from .yokoya_factors.yokoya_q_factor import yoko_q
from .yokoya_factors.ellipt_long import ellipt_long
from .yokoya_factors.ellipt_drivx import ellipt_drivx
from .yokoya_factors.ellipt_drivy import ellipt_drivy
from .yokoya_factors.ellipt_detx import ellipt_detx
from .yokoya_factors.ellipt_dety import ellipt_dety
from .yokoya_factors.rect_long import rect_long
from .yokoya_factors.rect_drivx import rect_drivx
from .yokoya_factors.rect_drivy import rect_drivy
from .yokoya_factors.rect_detx import rect_detx
from .yokoya_factors.rect_dety import rect_dety


# Constants with descriptive names and type hints
DEFAULT_PIPE_LENGTH_M: float = 1.0
DEFAULT_PIPE_RADIUS_M: float = 1.0e-2
DEFAULT_PIPE_HORIZONTAL_M: float = 1.0e-2
DEFAULT_PIPE_VERTICAL_M: float = 1.0e-2
DEFAULT_CHAMBER_SHAPE: str = 'CIRCULAR'
DEFAULT_BETA_X: float = 1.0
DEFAULT_BETA_Y: float = 1.0
DEFAULT_COMPONENT_NAME: str = 'el'


class ChamberShapeError(ValueError):
    """Exception raised for invalid chamber shape specifications."""
    pass


class ChamberDimensionError(ValueError):
    """Exception raised for invalid chamber dimensions."""
    pass


class Chamber:
    """
    Represents a vacuum chamber with specified geometry and optical parameters.
    
    This class models vacuum chambers with various cross-sectional shapes
    (circular, elliptical, rectangular) and calculates associated Yokoya
    factors for impedance calculations. It supports multi-layer structures
    and beam optics parameters.
    
    Attributes:
        pipe_len_m (float): Pipe length in meters.
        pipe_rad_m (float): Pipe radius in meters (for circular chambers).
        pipe_hor_m (float): Horizontal half-aperture in meters.
        pipe_ver_m (float): Vertical half-aperture in meters.
        chamber_shape (str): Chamber cross-section shape ('CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR').
        betax (float): Horizontal beta function at chamber location (m).
        betay (float): Vertical beta function at chamber location (m).
        layers (List): List of material layers (Layer objects).
        component_name (str): Name identifier for the chamber component.
    
    Properties:
        yokoya_q (float): Asymmetry parameter for Yokoya factors.
        yokoya_q_idx (int): Index in Yokoya factor tables.
        long_yokoya_factor (float): Longitudinal Yokoya factor.
        drivx_yokoya_factor (float): Horizontal driving Yokoya factor.
        drivy_yokoya_factor (float): Vertical driving Yokoya factor.
        detx_yokoya_factor (float): Horizontal detuning Yokoya factor.
        dety_yokoya_factor (float): Vertical detuning Yokoya factor.
    
    Examples:
        >>> # Circular chamber
        >>> chamber = Chamber(pipe_rad_m=0.02, chamber_shape='CIRCULAR')
        >>> 
        >>> # Elliptical chamber
        >>> chamber = Chamber(
        ...     pipe_hor_m=0.03,
        ...     pipe_ver_m=0.02,
        ...     chamber_shape='ELLIPTICAL',
        ...     betax=100.0,
        ...     betay=50.0
        ... )
        >>> 
        >>> # Rectangular chamber
        >>> chamber = Chamber(
        ...     pipe_hor_m=0.04,
        ...     pipe_ver_m=0.02,
        ...     chamber_shape='RECTANGULAR'
        ... )
    
    Notes:
        - For circular chambers, pipe_rad_m sets both horizontal and vertical dimensions
        - Yokoya factors account for non-circular geometry effects on impedance
        - Beta functions are used for transverse impedance calculations
    """
    
    def __init__(
        self,
        pipe_len_m: float = DEFAULT_PIPE_LENGTH_M,
        pipe_rad_m: float = DEFAULT_PIPE_RADIUS_M,
        pipe_hor_m: Optional[float] = None,
        pipe_ver_m: Optional[float] = None,
        chamber_shape: str = DEFAULT_CHAMBER_SHAPE,
        betax: float = DEFAULT_BETA_X,
        betay: float = DEFAULT_BETA_Y,
        layers: Optional[List] = None,
        component_name: str = DEFAULT_COMPONENT_NAME
    ):
        """
        Initialize a Chamber object.
        
        Args:
            pipe_len_m: Pipe length in meters. Default is 1.0 m.
            pipe_rad_m: Pipe radius in meters (for circular). Default is 0.01 m.
            pipe_hor_m: Horizontal half-aperture in meters. If None, uses pipe_rad_m.
            pipe_ver_m: Vertical half-aperture in meters. If None, uses pipe_rad_m.
            chamber_shape: Cross-section shape. One of 'CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR'.
            betax: Horizontal beta function in meters. Default is 1.0 m.
            betay: Vertical beta function in meters. Default is 1.0 m.
            layers: List of Layer objects for multi-layer structure. Default is empty list.
            component_name: Name identifier for the component. Default is 'el'.
        
        Raises:
            ChamberDimensionError: If dimensions are invalid (negative or zero).
            ChamberShapeError: If chamber_shape is not recognized.
        """
        # Initialize layers first
        self.layers = layers if layers is not None else []
        
        # Set dimensions through properties (includes validation)
        self.pipe_len_m = pipe_len_m
        self.pipe_rad_m = pipe_rad_m
        
        # Handle horizontal and vertical dimensions
        if pipe_hor_m is not None:
            self.pipe_hor_m = pipe_hor_m
        else:
            self._pipe_hor_m = pipe_rad_m
            
        if pipe_ver_m is not None:
            self.pipe_ver_m = pipe_ver_m
        else:
            self._pipe_ver_m = pipe_rad_m
        
        # Set shape (must be after dimensions for Yokoya factor initialization)
        self.chamber_shape = chamber_shape
        
        # Set optical parameters
        self.betax = betax
        self.betay = betay
        
        # Set component name
        self.component_name = component_name
        
    # Property definitions with validation
    
    @property
    def pipe_len_m(self) -> float:
        """Get pipe length in meters."""
        return self._pipe_len_m
    
    @pipe_len_m.setter
    def pipe_len_m(self, value: float) -> None:
        """
        Set pipe length in meters.
        
        Args:
            value: New pipe length in meters.
        
        Raises:
            ChamberDimensionError: If value is not positive.
        """
        try:
            value_float = float(value)
        except (ValueError, TypeError) as e:
            raise ChamberDimensionError(
                f"Pipe length must be a numeric value, got {value}"
            ) from e
        
        if value_float <= 0:
            raise ChamberDimensionError(
                f"Pipe length must be positive, got {value_float}"
            )
        
        self._pipe_len_m = value_float
    
    @property
    def pipe_rad_m(self) -> float:
        """Get pipe radius in meters."""
        return self._pipe_rad_m
    
    @pipe_rad_m.setter
    def pipe_rad_m(self, value: float) -> None:
        """
        Set pipe radius in meters.
        
        For circular chambers, this also sets horizontal and vertical dimensions.
        
        Args:
            value: New pipe radius in meters.
        
        Raises:
            ChamberDimensionError: If value is not positive.
        """
        try:
            value_float = float(value)
        except (ValueError, TypeError) as e:
            raise ChamberDimensionError(
                f"Pipe radius must be a numeric value, got {value}"
            ) from e
        
        if value_float <= 0:
            raise ChamberDimensionError(
                f"Pipe radius must be positive, got {value_float}"
            )
        
        self._pipe_rad_m = value_float
        
        # For circular chambers, also update horizontal and vertical dimensions
        # Check if chamber_shape attribute exists (it won't during __init__)
        if hasattr(self, '_chamber_shape') and self._chamber_shape == 'CIRCULAR':
            self._pipe_hor_m = value_float
            self._pipe_ver_m = value_float
    
    @property
    def pipe_hor_m(self) -> float:
        """Get horizontal half-aperture in meters."""
        return self._pipe_hor_m
    
    @pipe_hor_m.setter
    def pipe_hor_m(self, value: float) -> None:
        """
        Set horizontal half-aperture in meters.
        
        Args:
            value: New horizontal dimension in meters.
        
        Raises:
            ChamberDimensionError: If value is not positive.
        """
        try:
            value_float = float(value)
        except (ValueError, TypeError) as e:
            raise ChamberDimensionError(
                f"Horizontal dimension must be a numeric value, got {value}"
            ) from e
        
        if value_float <= 0:
            raise ChamberDimensionError(
                f"Horizontal dimension must be positive, got {value_float}"
            )
        
        self._pipe_hor_m = value_float
    
    @property
    def pipe_ver_m(self) -> float:
        """Get vertical half-aperture in meters."""
        return self._pipe_ver_m
    
    @pipe_ver_m.setter
    def pipe_ver_m(self, value: float) -> None:
        """
        Set vertical half-aperture in meters.
        
        Args:
            value: New vertical dimension in meters.
        
        Raises:
            ChamberDimensionError: If value is not positive.
        """
        try:
            value_float = float(value)
        except (ValueError, TypeError) as e:
            raise ChamberDimensionError(
                f"Vertical dimension must be a numeric value, got {value}"
            ) from e
        
        if value_float <= 0:
            raise ChamberDimensionError(
                f"Vertical dimension must be positive, got {value_float}"
            )
        
        self._pipe_ver_m = value_float
    
    @property
    def betax(self) -> float:
        """Get horizontal beta function in meters."""
        return self._betax
    
    @betax.setter
    def betax(self, value: float) -> None:
        """
        Set horizontal beta function in meters.
        
        Args:
            value: New beta_x value in meters.
        
        Raises:
            ChamberDimensionError: If value is not positive.
        """
        try:
            value_float = float(value)
        except (ValueError, TypeError) as e:
            raise ChamberDimensionError(
                f"Beta_x must be a numeric value, got {value}"
            ) from e
        
        if value_float <= 0:
            raise ChamberDimensionError(
                f"Beta_x must be positive, got {value_float}"
            )
        
        self._betax = value_float
    
    @property
    def betay(self) -> float:
        """Get vertical beta function in meters."""
        return self._betay
    
    @betay.setter
    def betay(self, value: float) -> None:
        """
        Set vertical beta function in meters.
        
        Args:
            value: New beta_y value in meters.
        
        Raises:
            ChamberDimensionError: If value is not positive.
        """
        try:
            value_float = float(value)
        except (ValueError, TypeError) as e:
            raise ChamberDimensionError(
                f"Beta_y must be a numeric value, got {value}"
            ) from e
        
        if value_float <= 0:
            raise ChamberDimensionError(
                f"Beta_y must be positive, got {value_float}"
            )
        
        self._betay = value_float
    
    @property
    def chamber_shape(self) -> str:
        """Get chamber cross-section shape."""
        return self._chamber_shape
    
    @chamber_shape.setter
    def chamber_shape(self, value: str) -> None:
        """
        Set chamber cross-section shape and initialize Yokoya factors.
        
        Args:
            value: Chamber shape. Must be 'CIRCULAR', 'ELLIPTICAL', or 'RECTANGULAR'.
        
        Raises:
            ChamberShapeError: If shape is not recognized.
        """
        shape_upper = value.upper()
        
        if shape_upper == 'ELLIPTICAL':
            self._chamber_shape = shape_upper
            self._long_yoko_list = ellipt_long
            self._drivx_yoko_list = ellipt_drivx
            self._drivy_yoko_list = ellipt_drivy
            self._detx_yoko_list = ellipt_detx
            self._dety_yoko_list = ellipt_dety
            
        elif shape_upper == 'RECTANGULAR':
            self._chamber_shape = shape_upper
            self._long_yoko_list = rect_long
            self._drivx_yoko_list = rect_drivx
            self._drivy_yoko_list = rect_drivy
            self._detx_yoko_list = rect_detx
            self._dety_yoko_list = rect_dety
            
        elif shape_upper == 'CIRCULAR':
            self._chamber_shape = shape_upper
            # Circular chamber has unity Yokoya factors (no geometric correction)
            n_points = len(yoko_q)
            self._long_yoko_list = np.ones(n_points)
            self._drivx_yoko_list = np.ones(n_points)
            self._drivy_yoko_list = np.ones(n_points)
            self._detx_yoko_list = np.zeros(n_points)
            self._dety_yoko_list = np.zeros(n_points)
            
        else:
            raise ChamberShapeError(
                f"Unknown chamber shape '{value}'. "
                f"Must be one of: 'CIRCULAR', 'ELLIPTICAL', 'RECTANGULAR'"
            )
    
    @property
    def component_name(self) -> str:
        """Get component name identifier."""
        return self._component_name
    
    @component_name.setter
    def component_name(self, value: str) -> None:
        """Set component name identifier."""
        self._component_name = str(value)
    
    # Yokoya factor properties
    
    @property
    def yokoya_q(self) -> float:
        """
        Calculate Yokoya asymmetry parameter q.
        
        The asymmetry parameter is defined as:
            q = |h - v| / (h + v)
        where h is horizontal and v is vertical half-aperture.
        
        Returns:
            float: Yokoya asymmetry parameter (0 for circular, >0 for non-circular).
        
        Notes:
            - q = 0 for circular chambers
            - q > 0 for elliptical or rectangular chambers
            - Used to interpolate Yokoya correction factors
        """
        return abs(self.pipe_hor_m - self.pipe_ver_m) / (
            self.pipe_hor_m + self.pipe_ver_m
        )
    
    @property
    def yokoya_q_idx(self) -> int:
        """
        Get index in Yokoya factor tables for current asymmetry.
        
        Returns:
            int: Index in yoko_q array closest to current yokoya_q value.
        """
        return int(np.argmin(np.abs(yoko_q - self.yokoya_q)))
    
    @property
    def long_yokoya_factor(self) -> float:
        """
        Get longitudinal Yokoya correction factor.
        
        Returns:
            float: Yokoya factor for longitudinal impedance.
        """
        return float(self._long_yoko_list[self.yokoya_q_idx])
    
    @property
    def drivx_yokoya_factor(self) -> float:
        """
        Get horizontal driving Yokoya correction factor.
        
        Returns:
            float: Yokoya factor for horizontal driving impedance.
        
        Note:
            Swaps x/y factors when pipe_ver_m > pipe_hor_m to account
            for chamber orientation.
        """
        if self.pipe_ver_m > self.pipe_hor_m:
            # Chamber is taller than wide - swap x and y
            return float(self._drivy_yoko_list[self.yokoya_q_idx])
        else:
            return float(self._drivx_yoko_list[self.yokoya_q_idx])
    
    @property
    def drivy_yokoya_factor(self) -> float:
        """
        Get vertical driving Yokoya correction factor.
        
        Returns:
            float: Yokoya factor for vertical driving impedance.
        
        Note:
            Swaps x/y factors when pipe_ver_m > pipe_hor_m to account
            for chamber orientation.
        """
        if self.pipe_ver_m > self.pipe_hor_m:
            # Chamber is taller than wide - swap x and y
            return float(self._drivx_yoko_list[self.yokoya_q_idx])
        else:
            return float(self._drivy_yoko_list[self.yokoya_q_idx])
    
    @property
    def detx_yokoya_factor(self) -> float:
        """
        Get horizontal detuning Yokoya correction factor.
        
        Returns:
            float: Yokoya factor for horizontal detuning impedance.
        
        Note:
            Swaps x/y factors when pipe_ver_m > pipe_hor_m to account
            for chamber orientation.
        """
        if self.pipe_ver_m > self.pipe_hor_m:
            # Chamber is taller than wide - swap x and y
            return float(self._dety_yoko_list[self.yokoya_q_idx])
        else:
            return float(self._detx_yoko_list[self.yokoya_q_idx])
    
    @property
    def dety_yokoya_factor(self) -> float:
        """
        Get vertical detuning Yokoya correction factor.
        
        Returns:
            float: Yokoya factor for vertical detuning impedance.
        
        Note:
            Swaps x/y factors when pipe_ver_m > pipe_hor_m to account
            for chamber orientation.
        """
        if self.pipe_ver_m > self.pipe_hor_m:
            # Chamber is taller than wide - swap x and y
            return float(self._detx_yoko_list[self.yokoya_q_idx])
        else:
            return float(self._dety_yoko_list[self.yokoya_q_idx])
    
    # Utility methods
    
    def __repr__(self) -> str:
        """Return detailed string representation of Chamber."""
        return (
            f"Chamber("
            f"shape='{self.chamber_shape}', "
            f"length={self.pipe_len_m:.3f}m, "
            f"hor={self.pipe_hor_m*1000:.1f}mm, "
            f"ver={self.pipe_ver_m*1000:.1f}mm, "
            f"βx={self.betax:.1f}m, "
            f"βy={self.betay:.1f}m, "
            f"name='{self.component_name}'"
            f")"
        )
    
    def __str__(self) -> str:
        """Return user-friendly string representation of Chamber."""
        if self.chamber_shape == 'CIRCULAR':
            geom = f"radius={self.pipe_rad_m*1000:.1f} mm"
        else:
            geom = f"h={self.pipe_hor_m*1000:.1f} mm, v={self.pipe_ver_m*1000:.1f} mm"
        
        return f"{self.chamber_shape} chamber ({geom})"
    
    def get_yokoya_factors(self) -> dict:
        """
        Get all Yokoya factors as a dictionary.
        
        Returns:
            dict: Dictionary containing all Yokoya factors:
                - 'q': asymmetry parameter
                - 'longitudinal': longitudinal factor
                - 'drivx': horizontal driving factor
                - 'drivy': vertical driving factor
                - 'detx': horizontal detuning factor
                - 'dety': vertical detuning factor
        
        Example:
            >>> chamber = Chamber(pipe_hor_m=0.03, pipe_ver_m=0.02, 
            ...                   chamber_shape='ELLIPTICAL')
            >>> factors = chamber.get_yokoya_factors()
            >>> print(f"Longitudinal factor: {factors['longitudinal']:.3f}")
        """
        return {
            'q': self.yokoya_q,
            'longitudinal': self.long_yokoya_factor,
            'drivx': self.drivx_yokoya_factor,
            'drivy': self.drivy_yokoya_factor,
            'detx': self.detx_yokoya_factor,
            'dety': self.dety_yokoya_factor
        }
    
    def get_dimensions(self) -> dict:
        """
        Get chamber dimensions as a dictionary.
        
        Returns:
            dict: Dictionary containing chamber dimensions:
                - 'length': pipe length in meters
                - 'radius': pipe radius in meters (for circular)
                - 'horizontal': horizontal half-aperture in meters
                - 'vertical': vertical half-aperture in meters
        
        Example:
            >>> chamber = Chamber(pipe_rad_m=0.025)
            >>> dims = chamber.get_dimensions()
            >>> print(f"Chamber radius: {dims['radius']*1000:.1f} mm")
        """
        return {
            'length': self.pipe_len_m,
            'radius': self.pipe_rad_m,
            'horizontal': self.pipe_hor_m,
            'vertical': self.pipe_ver_m
        }
    
    def summary(self) -> str:
        """
        Generate a detailed summary of the chamber configuration.
        
        Returns:
            str: Multi-line formatted summary of chamber properties.
        
        Example:
            >>> chamber = Chamber(pipe_hor_m=0.03, pipe_ver_m=0.02, 
            ...                   chamber_shape='ELLIPTICAL')
            >>> print(chamber.summary())
        """
        lines = [
            "=" * 60,
            f"Chamber: {self.component_name}",
            "=" * 60,
            f"Shape:              {self.chamber_shape}",
            f"Length:             {self.pipe_len_m:.3f} m",
            f"Horizontal aperture: {self.pipe_hor_m*1000:.2f} mm",
            f"Vertical aperture:   {self.pipe_ver_m*1000:.2f} mm",
            f"Beta_x:             {self.betax:.2f} m",
            f"Beta_y:             {self.betay:.2f} m",
            f"Number of layers:   {len(self.layers)}",
            "",
            "Yokoya Factors:",
            f"  Asymmetry (q):    {self.yokoya_q:.4f}",
            f"  Longitudinal:     {self.long_yokoya_factor:.4f}",
            f"  Driv_x:           {self.drivx_yokoya_factor:.4f}",
            f"  Driv_y:           {self.drivy_yokoya_factor:.4f}",
            f"  Det_x:            {self.detx_yokoya_factor:.4f}",
            f"  Det_y:            {self.dety_yokoya_factor:.4f}",
            "=" * 60
        ]
        return "\n".join(lines)
