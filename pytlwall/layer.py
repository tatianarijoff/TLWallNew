"""
Layer definition for material properties and surface impedance.

This module provides the Layer class for defining material layers in
vacuum chambers, including electrical and magnetic properties that
vary with frequency.

Authors: Tatiana Rijoff, Carlo Zannini
Date:    01/03/2013
Updated: December 2025
"""

from __future__ import annotations

import numpy as np
import scipy.constants as const
from typing import Optional, Union, Sequence
import warnings

# Default values for layer parameters
DEFAULT_TYPE = "CW"
DEFAULT_BOUNDARY_TYPE = "V"
DEFAULT_THICK_M = 1e-2
DEFAULT_MUINF_HZ = 0.0
DEFAULT_EPSR = 1.0
DEFAULT_SIGMADC = 1.0e6
DEFAULT_K_HZ = float("inf")
DEFAULT_TAU = 0.0
DEFAULT_RQ = 0.0


class LayerValidationError(Exception):
    """Exception raised for invalid layer parameters."""
    pass


class Layer:
    """
    Material layer with electromagnetic properties.
    
    This class represents a material layer in a vacuum chamber, including
    its electrical conductivity, magnetic permeability, thickness, and
    frequency-dependent properties.
    
    Parameters
    ----------
    layer_type : str, optional
        Layer type: 'CW' (conductor), 'V' (vacuum), 'PEC' (perfect conductor).
        Default is 'CW'.
    thick_m : float, optional
        Layer thickness in meters. Default is 0.01 m (1 cm).
    muinf_Hz : float, optional
        Magnetic permeability parameter. Default is 0.0.
    epsr : float, optional
        Relative permittivity (dielectric constant). Default is 1.0.
    sigmaDC : float, optional
        DC electrical conductivity in S/m. Default is 1e6 S/m (copper-like).
    k_Hz : float, optional
        Relaxation frequency for permeability in Hz. Default is inf.
    tau : float, optional
        Relaxation time for permittivity in seconds. Default is 0.0.
    RQ : float, optional
        Surface roughness parameter in meters. Default is 0.0.
    freq_Hz : array-like, optional
        Frequency array in Hz for calculations. Default is empty array.
    boundary : bool, optional
        If True, sets layer as boundary (vacuum). Default is False.
    
    Attributes
    ----------
    layer_type : str
        Layer type identifier.
    thick_m : float
        Layer thickness in meters.
    epsr : float
        Relative permittivity.
    muinf_Hz : float
        Magnetic permeability parameter.
    k_Hz : float
        Relaxation frequency for permeability.
    sigmaDC : float
        DC conductivity in S/m.
    tau : float
        Relaxation time for permittivity.
    RQ : float
        Surface roughness parameter.
    freq_Hz : np.ndarray
        Frequency array in Hz.
    
    Examples
    --------
    Create a copper layer:
    
    >>> copper = Layer(
    ...     layer_type='CW',
    ...     thick_m=0.001,  # 1 mm
    ...     sigmaDC=5.96e7,  # Copper conductivity
    ...     freq_Hz=np.logspace(3, 9, 100)
    ... )
    
    Create a vacuum boundary:
    
    >>> vacuum = Layer(boundary=True)
    
    Create a stainless steel layer with roughness:
    
    >>> steel = Layer(
    ...     layer_type='CW',
    ...     thick_m=0.002,  # 2 mm
    ...     sigmaDC=1.45e6,  # Stainless steel
    ...     RQ=1e-6,  # 1 micron roughness
    ...     freq_Hz=np.logspace(3, 9, 100)
    ... )
    
    Notes
    -----
    The Layer class calculates frequency-dependent properties such as:
    - AC conductivity (sigmaAC)
    - Magnetic permeability (mu, mur)
    - Skin depth (delta, deltaM)
    - Surface resistance (RS)
    - Surface impedance (KZ)
    
    These properties are computed on-demand when accessed as properties.
    """
    
    def __init__(
        self,
        layer_type: str = DEFAULT_TYPE,
        thick_m: float = DEFAULT_THICK_M,
        muinf_Hz: float = DEFAULT_MUINF_HZ,
        epsr: float = DEFAULT_EPSR,
        sigmaDC: float = DEFAULT_SIGMADC,
        k_Hz: float = DEFAULT_K_HZ,
        tau: float = DEFAULT_TAU,
        RQ: float = DEFAULT_RQ,
        freq_Hz: Optional[Sequence[float]] = None,
        boundary: bool = False,
    ) -> None:
        """Initialize Layer object."""
        
        # Initialize private attributes with defaults
        self._thick_m = DEFAULT_THICK_M
        self._muinf_Hz = DEFAULT_MUINF_HZ
        self._epsr = DEFAULT_EPSR
        self._sigmaDC = DEFAULT_SIGMADC
        self._k_Hz = DEFAULT_K_HZ
        self._tau = DEFAULT_TAU
        self._RQ = DEFAULT_RQ
        self._freq_Hz = np.array([], dtype=float)
        
        # Set layer type: boundary takes precedence
        if boundary:
            self._layer_type = DEFAULT_BOUNDARY_TYPE  # 'V'
        else:
            self._layer_type = layer_type.upper() if isinstance(layer_type, str) else DEFAULT_TYPE
        
        # Optional: surface impedance can be set directly
        self._KZ: Optional[np.ndarray] = None
        
        # Apply user inputs through setters (but NOT layer_type if boundary=True)
        if not boundary:
            self.layer_type = layer_type
        
        if freq_Hz is not None:
            self.freq_Hz = freq_Hz
        self.thick_m = thick_m
        self.muinf_Hz = muinf_Hz
        self.epsr = epsr
        self.sigmaDC = sigmaDC
        self.k_Hz = k_Hz
        self.tau = tau
        self.RQ = RQ
    
    # ========================================================================
    # Basic Properties
    # ========================================================================
    
    @property
    def layer_type(self) -> str:
        """
        Get layer type.
        
        Returns
        -------
        str
            Layer type: 'CW' (conductor), 'V' (vacuum), or 'PEC' (perfect conductor).
        """
        return self._layer_type
    
    @layer_type.setter
    def layer_type(self, newtype: str) -> None:
        """
        Set layer type.
        
        Parameters
        ----------
        newtype : str
            Layer type: 'CW', 'V', or 'PEC' (case insensitive).
        
        Raises
        ------
        LayerValidationError
            If layer type is not recognized.
        """
        upper = str(newtype).upper()
        if upper in ("CW", "V", "PEC"):
            self._layer_type = upper
        else:
            raise LayerValidationError(
                f"'{newtype}' is not a valid layer type. "
                f"Must be 'CW', 'V', or 'PEC'."
            )
    
    @property
    def thick_m(self) -> float:
        """
        Get layer thickness in meters.
        
        Returns
        -------
        float
            Thickness in meters.
        """
        return self._thick_m
    
    @thick_m.setter
    def thick_m(self, newthick: float) -> None:
        """
        Set layer thickness.
        
        Parameters
        ----------
        newthick : float
            Thickness in meters (must be positive).
        
        Raises
        ------
        LayerValidationError
            If thickness is not a positive number.
        """
        try:
            tmp_thick = float(newthick)
            if tmp_thick <= 0:
                raise LayerValidationError(
                    f"Thickness must be positive, got {tmp_thick} m"
                )
            self._thick_m = tmp_thick
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid thickness value '{newthick}': {e}"
            )
    
    @property
    def epsr(self) -> float:
        """
        Get relative permittivity (dielectric constant).
        
        Returns
        -------
        float
            Relative permittivity (dimensionless).
        """
        return self._epsr
    
    @epsr.setter
    def epsr(self, newepsr: float) -> None:
        """
        Set relative permittivity.
        
        Parameters
        ----------
        newepsr : float
            Relative permittivity (must be positive).
        
        Raises
        ------
        LayerValidationError
            If value is not positive.
        """
        try:
            tmp_epsr = float(newepsr)
            if tmp_epsr <= 0:
                raise LayerValidationError(
                    f"Relative permittivity must be positive, got {tmp_epsr}"
                )
            self._epsr = tmp_epsr
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid relative permittivity '{newepsr}': {e}"
            )
    
    @property
    def muinf_Hz(self) -> float:
        """
        Get magnetic permeability parameter.
        
        Returns
        -------
        float
            Magnetic permeability parameter.
        """
        return self._muinf_Hz
    
    @muinf_Hz.setter
    def muinf_Hz(self, newmuinf_Hz: float) -> None:
        """
        Set magnetic permeability parameter.
        
        Parameters
        ----------
        newmuinf_Hz : float
            Magnetic permeability parameter.
        
        Raises
        ------
        LayerValidationError
            If value is invalid.
        """
        try:
            self._muinf_Hz = float(newmuinf_Hz)
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid permeability parameter '{newmuinf_Hz}': {e}"
            )
    
    @property
    def k_Hz(self) -> float:
        """
        Get relaxation frequency for permeability.
        
        Returns
        -------
        float
            Relaxation frequency in Hz.
        """
        return self._k_Hz
    
    @k_Hz.setter
    def k_Hz(self, newk_Hz: float) -> None:
        """
        Set relaxation frequency for permeability.
        
        Parameters
        ----------
        newk_Hz : float
            Relaxation frequency in Hz (must be positive).
        
        Raises
        ------
        LayerValidationError
            If value is not positive.
        """
        try:
            tmp_k_Hz = float(newk_Hz)
            if tmp_k_Hz <= 0 and not np.isinf(tmp_k_Hz):
                raise LayerValidationError(
                    f"Relaxation frequency must be positive or inf, got {tmp_k_Hz}"
                )
            self._k_Hz = tmp_k_Hz
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid relaxation frequency '{newk_Hz}': {e}"
            )
    
    @property
    def sigmaDC(self) -> float:
        """
        Get DC electrical conductivity.
        
        Returns
        -------
        float
            DC conductivity in S/m.
        """
        return self._sigmaDC
    
    @sigmaDC.setter
    def sigmaDC(self, newsigmaDC: float) -> None:
        """
        Set DC electrical conductivity.
        
        Parameters
        ----------
        newsigmaDC : float
            DC conductivity in S/m (must be non-negative).
        
        Raises
        ------
        LayerValidationError
            If value is negative.
        """
        try:
            tmp_sigmaDC = float(newsigmaDC)
            if tmp_sigmaDC < 0:
                raise LayerValidationError(
                    f"DC conductivity must be non-negative, got {tmp_sigmaDC}"
                )
            self._sigmaDC = tmp_sigmaDC
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid DC conductivity '{newsigmaDC}': {e}"
            )
    
    @property
    def tau(self) -> float:
        """
        Get relaxation time for permittivity.
        
        Returns
        -------
        float
            Relaxation time in seconds.
        """
        return self._tau
    
    @tau.setter
    def tau(self, newtau: float) -> None:
        """
        Set relaxation time for permittivity.
        
        Parameters
        ----------
        newtau : float
            Relaxation time in seconds (must be non-negative).
        
        Raises
        ------
        LayerValidationError
            If value is negative.
        """
        try:
            tmp_tau = float(newtau)
            if tmp_tau < 0:
                raise LayerValidationError(
                    f"Relaxation time must be non-negative, got {tmp_tau}"
                )
            self._tau = tmp_tau
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid relaxation time '{newtau}': {e}"
            )
    
    @property
    def RQ(self) -> float:
        """
        Get surface roughness parameter.
        
        Returns
        -------
        float
            Surface roughness in meters.
        """
        return self._RQ
    
    @RQ.setter
    def RQ(self, newRQ: float) -> None:
        """
        Set surface roughness parameter.
        
        Parameters
        ----------
        newRQ : float
            Surface roughness in meters (must be non-negative).
        
        Raises
        ------
        LayerValidationError
            If value is negative.
        """
        try:
            tmp_RQ = float(newRQ)
            if tmp_RQ < 0:
                raise LayerValidationError(
                    f"Surface roughness must be non-negative, got {tmp_RQ}"
                )
            self._RQ = tmp_RQ
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid surface roughness '{newRQ}': {e}"
            )
    
    @property
    def freq_Hz(self) -> np.ndarray:
        """
        Get frequency array.
        
        Returns
        -------
        np.ndarray
            Frequency array in Hz.
        """
        return self._freq_Hz
    
    @freq_Hz.setter
    def freq_Hz(self, newfreq_Hz: Sequence[float]) -> None:
        """
        Set frequency array.
        
        Parameters
        ----------
        newfreq_Hz : array-like
            Frequency array in Hz (all values must be positive).
        
        Raises
        ------
        LayerValidationError
            If frequencies are invalid or not all positive.
        """
        try:
            tmp_freq_Hz = np.array(newfreq_Hz, dtype=float)
            if np.any(tmp_freq_Hz <= 0):
                raise LayerValidationError(
                    "All frequencies must be positive"
                )
            self._freq_Hz = tmp_freq_Hz
        except (TypeError, ValueError) as e:
            raise LayerValidationError(
                f"Invalid frequency array: {e}"
            )
    
    # ========================================================================
    # Surface Impedance
    # ========================================================================
    
    @property
    def KZ(self) -> np.ndarray:
        """
        Get surface impedance.
        
        Returns
        -------
        np.ndarray
            Complex surface impedance array.
        
        Notes
        -----
        If not explicitly set, calculates default surface impedance as:
        KZ = (1 + j) / (sigmaPM * deltaM)
        """
        if self._KZ is not None:
            return self._KZ
        
        # Calculate surface impedance based on material type
        omega = 2.0 * const.pi * self.freq_Hz
        
        # Complex permittivity: ε_complex = ε - j*σ/ω
        # (σ already includes AC effects via sigmaAC)
        eps_complex = self.eps - 1.0j * self.sigmaAC / omega
        
        # Surface impedance: KZ = sqrt(j*ω*μ / (σ + j*ω*ε)) = sqrt(μ / ε_complex)
        # ~ KZ = np.sqrt(self.mu / eps_complex)
        KZ = (1.0 + 1.0j) / (self.sigmaPM * self.deltaM)

        return KZ
    
    @KZ.setter
    def KZ(self, newKZ: np.ndarray) -> None:
        """
        Set surface impedance directly.
        
        Parameters
        ----------
        newKZ : array-like
            Complex surface impedance array (must be complex).
        
        Raises
        ------
        LayerValidationError
            If values are not complex.
        
        Notes
        -----
        Surface impedance must be set for the same frequency array
        as defined in freq_Hz. For different frequencies, use set_surf_imped().
        """
        is_complex = np.iscomplex(newKZ)
        if isinstance(is_complex, np.ndarray):
            valid = is_complex.all()
        else:
            valid = bool(is_complex)
        
        if not valid:
            raise LayerValidationError(
                "Surface impedance must be complex-valued"
            )
        
        self._KZ = np.array(newKZ, dtype=complex)
    
    def set_surf_imped(
        self,
        newfreq_Hz: Sequence[float],
        newKZ: Sequence[complex]
    ) -> None:
        """
        Set surface impedance with interpolation to layer frequencies.
        
        This method allows setting surface impedance values at specific
        frequencies, which are then interpolated to match the layer's
        frequency array.
        
        Parameters
        ----------
        newfreq_Hz : array-like
            Frequency array in Hz for the impedance data.
        newKZ : array-like
            Complex surface impedance values at the given frequencies.
        
        Raises
        ------
        LayerValidationError
            If input data is invalid.
        
        Examples
        --------
        >>> layer = Layer(freq_Hz=np.logspace(6, 9, 100))
        >>> measured_freq = np.array([1e6, 1e7, 1e8, 1e9])
        >>> measured_KZ = np.array([1+1j, 2+2j, 3+3j, 4+4j])
        >>> layer.set_surf_imped(measured_freq, measured_KZ)
        """
        # Validate complex nature
        is_complex = np.iscomplex(newKZ)
        if isinstance(is_complex, np.ndarray):
            valid = is_complex.all()
        else:
            valid = bool(is_complex)
        
        if not valid:
            raise LayerValidationError(
                "Surface impedance must be complex-valued"
            )
        
        # Validate frequencies
        try:
            freq = np.array(newfreq_Hz, dtype=float)
        except (TypeError, ValueError) as e:
            raise LayerValidationError(
                f"Invalid frequency array: {e}"
            )
        
        tmp_KZ = np.array(newKZ, dtype=complex)
        
        # Interpolate real and imaginary parts separately
        real_part = np.interp(self._freq_Hz, freq, tmp_KZ.real)
        imag_part = np.interp(self._freq_Hz, freq, tmp_KZ.imag)
        self._KZ = real_part + 1j * imag_part
    
    # ========================================================================
    # Calculated Properties
    # ========================================================================
    
    @property
    def sigmaAC(self) -> np.ndarray:
        """
        Get AC conductivity (frequency-dependent).
        
        Returns
        -------
        np.ndarray
            Complex AC conductivity array in S/m.
        
        Notes
        -----
        Calculated as: σ_AC = σ_DC_R / (1 + j·2π·τ·f)
        """
        return self._calc_sigmaAC()
    
    @property
    def sigmaPM(self) -> np.ndarray:
        """
        Get effective conductivity magnitude.
        
        Returns
        -------
        np.ndarray
            Effective conductivity magnitude in S/m.
        
        Notes
        -----
        Calculated as: σ_PM = √[(2πfε)² + |σ_AC|²]
        """
        return self._calc_sigmaPM()
    
    @property
    def eps(self) -> float:
        """
        Get absolute permittivity.
        
        Returns
        -------
        float
            Permittivity in F/m.
        
        Notes
        -----
        Calculated as: ε = ε₀ · εᵣ
        """
        return const.epsilon_0 * self._epsr
    
    @property
    def mur(self) -> np.ndarray:
        """
        Get relative permeability (frequency-dependent).
        
        Returns
        -------
        np.ndarray
            Complex relative permeability array.
        
        Notes
        -----
        Calculated as: μᵣ = 1 + μ_inf / (1 + j·f/k)
        """
        return self._calc_mur()
    
    @property
    def mu(self) -> np.ndarray:
        """
        Get absolute permeability (frequency-dependent).
        
        Returns
        -------
        np.ndarray
            Complex permeability array in H/m.
        
        Notes
        -----
        Calculated as: μ = μ₀ · μᵣ
        """
        mur = self._calc_mur()
        return const.mu_0 * mur
    
    @property
    def delta(self) -> np.ndarray:
        """
        Get skin depth.
        
        Returns
        -------
        np.ndarray
            Complex skin depth array in meters.
        
        Notes
        -----
        Classical skin depth formula including permittivity effects.
        """
        return self._calc_delta()
    
    @property
    def deltaM(self) -> np.ndarray:
        """
        Get modified skin depth.
        
        Returns
        -------
        np.ndarray
            Complex modified skin depth array in meters.
        
        Notes
        -----
        Modified skin depth with opposite sign for imaginary component.
        """
        return self._calc_deltaM()
    
    @property
    def RS(self) -> np.ndarray:
        """
        Get surface resistance including roughness effects.
        
        Returns
        -------
        np.ndarray
            Surface resistance array in Ohm.
        
        Notes
        -----
        Includes Hammerstad roughness correction model.
        """
        return self._calc_RS()
    
    @property
    def sigmaDC_R(self) -> np.ndarray:
        """
        Get DC conductivity with roughness correction.
        
        Returns
        -------
        np.ndarray
            Complex corrected conductivity array in S/m.
        """
        return self._calc_sigmaDC_R()
    
    @property
    def kprop(self) -> np.ndarray:
        """
        Get propagation constant.
        
        Returns
        -------
        np.ndarray
            Complex propagation constant in 1/m.
        
        Notes
        -----
        Calculated as: k = (1 - j) / δ
        """
        return (1.0 - 1.0j) / self.delta
    
    # ========================================================================
    # Calculation Methods
    # ========================================================================
    
    def _calc_sigmaAC(self) -> np.ndarray:
        """
        Calculate AC conductivity.
        
        Formula: σ_AC = σ_DC_R / (1 + j·2π·τ·f)
        """
        sigmaAC = self.sigmaDC_R / (
            1.0 + 2.0j * const.pi * self.tau * self.freq_Hz
        )
        return sigmaAC
    
    def _calc_mur(self) -> np.ndarray:
        """
        Calculate relative permeability.
        
        Formula: μᵣ = 1 + μ_inf / (1 + j·f/k)
        """
        mur = 1.0 + self.muinf_Hz / (1.0 + 1.0j * (self.freq_Hz / self.k_Hz))
        return mur
    
    def _calc_sigmaPM(self) -> np.ndarray:
        """
        Calculate effective conductivity magnitude.
        
        Formula: σ_PM = √[(2πfε)² + |σ_AC|²]
        """
        sigmaPM = np.sqrt(
            (2.0 * const.pi * self.freq_Hz * self.eps) ** 2
            + self.sigmaAC ** 2
        )
        return sigmaPM
    
    def _calc_delta(self) -> np.ndarray:
        """
        Calculate skin depth.
        
        Formula: δ = √[2 / (2πfμσ_AC + j·με(2πf)²)]
        """
        delta = np.sqrt(
            2.0
            / (
                2.0 * const.pi * self.freq_Hz * self.mu * self.sigmaAC
                + 1.0j * self.mu * self.eps * (2.0 * const.pi * self.freq_Hz) ** 2
            )
        )
        return delta
    
    def _calc_deltaM(self) -> np.ndarray:
        """
        Calculate modified skin depth.
        
        Formula: δ_M = √[2 / (2πfμσ_AC - j·με(2πf)²)]
        """
        deltaM = np.sqrt(
            2.0
            / (
                2.0 * const.pi * self.freq_Hz * self.mu * self.sigmaAC
                - 1.0j * self.mu * self.eps * (2.0 * const.pi * self.freq_Hz) ** 2
            )
        )
        return deltaM
    
    def _calc_RS(self) -> np.ndarray:
        """
        Calculate surface resistance with Hammerstad roughness model.
        
        Formula: Rs = √(μπf/σ_DC) · [1 + (2/π)·arctan(0.7·μ·2πf·σ_DC·RQ²)]
        """
        RS = (
            np.sqrt(self.mu * np.pi * self.freq_Hz / self.sigmaDC)
            * (
                1.0
                + (2.0 / np.pi)
                * np.arctan(
                    0.7
                    * self.mu
                    * 2.0
                    * np.pi
                    * self.freq_Hz
                    * self.sigmaDC
                    * self.RQ ** 2
                )
            )
        )
        return RS
    
    def _calc_sigmaDC_R(self) -> np.ndarray:
        """
        Calculate DC conductivity with roughness correction.
        
        The conductivity is corrected based on surface resistance.
        """
        sigmaDC = (
            np.ones(len(self.freq_Hz)) * self.sigmaDC
            + 1.0j * np.ones(len(self.freq_Hz))
        )
        RS_calc = self._calc_RS()
        mask = RS_calc != 0
        
        sigmaDC[mask] = (
            np.pi * self.freq_Hz[mask] * self.mu / RS_calc[mask] ** 2
        )
        return sigmaDC
    
    def __repr__(self) -> str:
        """
        String representation of Layer.
        
        Returns
        -------
        str
            String representation showing key parameters.
        """
        return (
            f"Layer(type='{self.layer_type}', "
            f"thick={self.thick_m:.3e} m, "
            f"σ_DC={self.sigmaDC:.3e} S/m, "
            f"εᵣ={self.epsr:.2f}, "
            f"n_freq={len(self.freq_Hz)})"
        )
    
    def __str__(self) -> str:
        """User-friendly string representation."""
        return repr(self)
