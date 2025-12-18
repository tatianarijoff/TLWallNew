"""
Transmission Line Wall Impedance Calculator

This module provides the TlWall class for calculating beam coupling impedances
using the transmission line approach with multi-layer chamber walls.

Authors: Tatiana Rijoff, Carlo Zannini
Original date: 01/03/2013
Refactored: December 2025
Copyright: CERN
"""

from typing import Optional, Tuple
import warnings
import numpy as np
import scipy.constants as const
from scipy.special import i0, i1, k0, k1, iv, kv
import cmath

# Note: When using this module, ensure Chamber, Beam, and Frequencies
# are properly imported from the pytlwall package
# from pytlwall.chamber import Chamber
# from pytlwall.beam import Beam  
# from pytlwall.frequencies import Frequencies


# Physical constants
Z0 = const.physical_constants['characteristic impedance of vacuum'][0]

# Numpy error handling
np.seterr(over='ignore')
np.seterr(invalid='ignore')


# Custom exceptions
class TlWallError(Exception):
    """Base exception for TlWall module."""
    pass


class TlWallCalculationError(TlWallError):
    """Raised when impedance calculation fails."""
    pass


class TlWallConfigurationError(TlWallError):
    """Raised when TlWall configuration is invalid."""
    pass


# Constants
DEFAULT_ACCURACY_FACTOR = 0.3
MIN_GAMMA_FOR_SC = 1.1  # Minimum gamma for space charge calculations
MAX_BESSEL_ARG = 500    # Conservative limit before Bessel overflow (i0(700) ≈ 1e304)
MAX_REASONABLE_Z = 1e100  # Maximum reasonable impedance value


def _safe_bessel_product_i0(argbess0: np.ndarray, argbess1: np.ndarray, 
                            order: str = 'long') -> np.ndarray:
    """
    Safely compute Bessel function products for space charge impedances.
    
    For longitudinal (order='long'):
        product = i0(a0)^2 * (-k0(a1)/i0(a1))
    
    For transverse (order='trans'):
        product = (i1(a0)/shift)^2 * (-k1(a1)/i1(a1))
        Note: 'shift' factor must be applied by caller
    
    Handles overflow for large arguments using asymptotic behavior:
    - For large x: i0(x) ~ exp(x)/sqrt(2πx), k0(x) ~ sqrt(π/(2x))*exp(-x)
    - Product ~ exp(2*(a0-a1)), which → 0 if a1 > a0, else overflows
    
    Parameters
    ----------
    argbess0 : np.ndarray
        First Bessel argument (typically k*test_beam_shift/gamma)
    argbess1 : np.ndarray
        Second Bessel argument (typically k*pipe_rad/gamma)
    order : str
        'long' for longitudinal (uses i0, k0), 'trans' for transverse (uses i1, k1)
    
    Returns
    -------
    product : np.ndarray
        Safe product of Bessel functions, with overflow handled
    """
    # Ensure arrays
    argbess0 = np.atleast_1d(argbess0)
    argbess1 = np.atleast_1d(argbess1)
    
    # Initialize result
    product = np.zeros(len(argbess0), dtype=float)
    
    # Identify regions by argument size
    small_args = (argbess0 < MAX_BESSEL_ARG) & (argbess1 < MAX_BESSEL_ARG)
    
    # Small arguments: direct calculation
    if np.any(small_args):
        with np.errstate(over='ignore', invalid='ignore'):
            a0_small = argbess0[small_args]
            a1_small = argbess1[small_args]
            
            if order == 'long':
                BessBeam = i0(a0_small)**2
                BessISC = -k0(a1_small) / i0(a1_small)
            else:  # trans
                BessBeam = i1(a0_small)**2  # caller handles /shift^2
                BessISC = -k1(a1_small) / i1(a1_small)
            
            prod_small = BessBeam * BessISC
            
            # Replace inf/nan with 0
            prod_small = np.where(np.isfinite(prod_small), prod_small, 0.0)
            
            # Also cap extremely large values (can happen before true overflow)
            prod_small = np.where(np.abs(prod_small) < 1e200, prod_small, 0.0)
            
            product[small_args] = prod_small
    
    # Large arguments: asymptotic behavior → 0
    # (product stays at 0 from initialization)
    
    return product


def _safe_bessel_product_dsc(argbess0: np.ndarray, order: str = 'long') -> np.ndarray:
    """
    Safely compute Bessel function products for DIRECT space charge.
    
    For longitudinal DSC (order='long'):
        product = i0(a0)^2 * k0(a0)/i0(a0) = i0(a0) * k0(a0)
        Asymptotic: ~ 1/(2*a0) for large a0
    
    For transverse DSC (order='trans'):
        product = i1(a0)^2 * k1(a0)/i1(a0) = i1(a0) * k1(a0)
        Asymptotic: ~ 1/(2*a0) for large a0
    
    Parameters
    ----------
    argbess0 : np.ndarray
        Bessel argument (k*test_beam_shift/gamma)
    order : str
        'long' for longitudinal (uses i0, k0), 'trans' for transverse (uses i1, k1)
    
    Returns
    -------
    product : np.ndarray
        Safe product of Bessel functions
    """
    argbess0 = np.atleast_1d(argbess0)
    product = np.zeros(len(argbess0), dtype=float)
    
    small_args = argbess0 < MAX_BESSEL_ARG
    large_args = ~small_args
    
    # Small arguments: direct calculation
    if np.any(small_args):
        with np.errstate(over='ignore', invalid='ignore'):
            a0_small = argbess0[small_args]
            
            if order == 'long':
                # i0(x)^2 * k0(x)/i0(x) = i0(x) * k0(x)
                prod_small = i0(a0_small) * k0(a0_small)
            else:  # trans
                prod_small = i1(a0_small) * k1(a0_small)
            
            prod_small = np.where(np.isfinite(prod_small), prod_small, 0.0)
            prod_small = np.where(np.abs(prod_small) < 1e200, prod_small, 0.0)
            product[small_args] = prod_small
    
    # Large arguments: use asymptotic i(x)*k(x) ~ 1/(2x)
    if np.any(large_args):
        product[large_args] = 1.0 / (2.0 * argbess0[large_args])
    
    return product


class TlWall:
    """
    Transmission line wall impedance calculator.
    
    This class calculates longitudinal and transverse beam coupling impedances
    for multi-layer vacuum chamber walls using the transmission line method.
    
    The calculation includes:
    - Longitudinal impedance (ZLong)
    - Transverse impedance (ZTrans)
    - Dipolar impedances (ZDipX, ZDipY) with Yokoya factors
    - Quadrupolar impedances (ZQuadX, ZQuadY)
    - Space charge impedances (direct and indirect)
    
    Attributes:
        chamber: Chamber geometry and layer configuration
        beam: Beam parameters (gamma, beta)
        frequencies: Frequency array for calculations
        accuracy_factor: Accuracy factor for corrections (default 0.3)
    
    Important Note on accuracy_factor:
        The accuracy_factor parameter is currently NOT used in calculations.
        It is stored for potential future implementation to control precision
        vs. speed trade-offs. The most likely intended use is to control
        whether to apply the longitudinal correction factor 
        (calc_corr_imp_long_factor). See ACCURACY_FACTOR_ANALYSIS.md for
        detailed analysis.
    
    Example:
        >>> from pytlwall import TlWall, Chamber, Beam, Frequencies, Layer
        >>> import numpy as np
        >>> 
        >>> # Setup
        >>> freqs = Frequencies(fmin=3, fmax=9, fstep=2)
        >>> beam = Beam(gammarel=7460.52)
        >>> chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        >>> copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=freqs.freq)
        >>> chamber.layers = [copper]
        >>> 
        >>> # Calculate impedances
        >>> wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
        >>> ZLong = wall.calc_ZLong()
        >>> ZTrans = wall.calc_ZTrans()
        >>> 
        >>> print(f"Calculated at {len(freqs)} frequencies")
        >>> print(f"ZLong range: {abs(ZLong[0]):.3e} to {abs(ZLong[-1]):.3e} Ω")
    """
    
    def __init__(
        self,
        chamber,  # Chamber object
        beam,     # Beam object
        frequencies,  # Frequencies object
        accuracy_factor: float = DEFAULT_ACCURACY_FACTOR
    ):
        """
        Initialize TlWall impedance calculator.
        
        The TlWall object performs the impedances calculations.
        
        Args:
            chamber: Chamber object with geometry and layers
            beam: Beam object with relativistic parameters
            frequencies: Frequencies object with frequency array
            accuracy_factor: Accuracy factor for corrections (default 0.3)
        
        Raises:
            TlWallConfigurationError: If configuration is invalid
            ValueError: If accuracy_factor is not positive
        
        Example:
            >>> wall = TlWall(
            ...     chamber=chamber,
            ...     beam=beam,
            ...     frequencies=freqs,
            ...     accuracy_factor=0.3
            ... )
        """
        # Validate inputs - check they have required attributes
        required_chamber_attrs = ['layers', 'pipe_len_m', 'pipe_rad_m', 'chamber_shape']
        required_beam_attrs = ['gammarel', 'betarel']
        required_freq_attrs = ['freq']
        
        for attr in required_chamber_attrs:
            if not hasattr(chamber, attr):
                raise TlWallConfigurationError(
                    f"chamber must have '{attr}' attribute"
                )
        
        for attr in required_beam_attrs:
            if not hasattr(beam, attr):
                raise TlWallConfigurationError(
                    f"beam must have '{attr}' attribute"
                )
        
        for attr in required_freq_attrs:
            if not hasattr(frequencies, attr):
                raise TlWallConfigurationError(
                    f"frequencies must have '{attr}' attribute"
                )
        
        if accuracy_factor <= 0:
            raise ValueError("accuracy_factor must be positive")
        
        if not chamber.layers:
            raise TlWallConfigurationError(
                "chamber must have at least one layer"
            )
        
        self._chamber = chamber
        self._beam = beam
        self._frequencies = frequencies
        
        # Accuracy factor - currently not used in calculations
        # Reserved for future implementation (see class documentation)
        self._accuracy_factor = accuracy_factor
        
        # Shortcut to frequency array
        self.f = self._frequencies.freq
        
        # Update layer frequencies
        for layer in self._chamber.layers:
            layer.freq_Hz = self.f
        
        # Calculate correction impedance factor
        self._corr_imp = self._calc_corr_imp_factor()
        
        # Cache for calculated impedances
        self._ZLong: Optional[np.ndarray] = None
        self._ZTrans: Optional[np.ndarray] = None
        self._ZLongDSC: Optional[np.ndarray]  = None
        self._ZLongISC: Optional[np.ndarray]  = None
        self._ZTransDSC: Optional[np.ndarray]  = None
        self._ZTransISC: Optional[np.ndarray]  = None
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def chamber(self):
        """Chamber geometry and configuration."""
        return self._chamber
    
    @property
    def beam(self):
        """Beam parameters."""
        return self._beam
    
    @property
    def frequencies(self):
        """Frequency array."""
        return self._frequencies
    
    @property
    def freq(self) -> np.ndarray:
        """Frequency array in Hz (alias for frequencies.freq)."""
        return self._frequencies.freq
    
    # =========================================================================
    # ACCURACY FACTOR - FUTURE IMPLEMENTATION
    # =========================================================================
    # 
    # IMPORTANT NOTE FOR FUTURE DEVELOPMENT:
    # 
    # The accuracy_factor parameter is currently NOT used in any calculations.
    # It is stored for potential future implementation of precision control.
    # 
    # SUGGESTED FUTURE USE:
    # The most likely intended use (based on commented code and analysis) is
    # to control whether to apply the longitudinal correction factor:
    # 
    #   if self.accuracy_factor < 0.5:
    #       # High precision mode: apply longitudinal correction
    #       corr_imp_long = self._calc_corr_imp_long_factor(KZeff)
    #       ZLong_corr = ZLong * corr_imp_long / self._corr_imp
    #   else:
    #       # Fast mode: skip correction (current implementation)
    #       ZLong_corr = ZLong / self._corr_imp
    # 
    # EVIDENCE:
    # 1. Method _calc_corr_imp_long_factor() exists but is not used
    # 2. Comment in calc_ZLong() mentions "for future refinement"
    # 3. Default value 0.3 suggests "use fast approximation"
    # 
    # See ACCURACY_FACTOR_ANALYSIS.md for detailed analysis of possible uses.
    # 
    # WARNING: Implementing this feature will change numerical results!
    # Extensive testing required before activation.
    # =========================================================================
    
    @property
    def accuracy_factor(self) -> float:
        """
        Accuracy factor for corrections (currently not used in calculations).
        
        Returns:
            float: Accuracy factor value (default: 0.3)
        
        Note:
            This parameter is stored but not currently used in any calculations.
            It is reserved for future implementation of precision control,
            most likely to control application of the longitudinal correction
            factor. See class documentation for details.
        """
        return self._accuracy_factor
    
    @accuracy_factor.setter
    def accuracy_factor(self, value: float):
        """
        Set accuracy factor.
        
        Args:
            value: New accuracy factor (must be positive)
        
        Raises:
            ValueError: If value is not positive
        
        Note:
            Currently, changing accuracy_factor does NOT affect impedance
            calculations. It is stored for future implementation.
            See class documentation for suggested future use.
        """
        if value <= 0:
            raise ValueError("accuracy_factor must be positive")
        self._accuracy_factor = value
        # NOTE: We do NOT recalculate corr_imp or invalidate cache
        # because accuracy_factor is not actually used in calculations!
    
    # =========================================================================
    # Longitudinal Impedance
    # =========================================================================
    
    def calc_ZLong(self) -> np.ndarray:
        """
        Calculate longitudinal impedance.
        
        Formula:
            ZLong = (L * KZeff) / (2π * r)
        
        where:
            L = pipe length
            r = pipe radius
            KZeff = effective surface impedance
        
        Returns:
            Complex array of longitudinal impedance [Ω]
        
        Raises:
            TlWallCalculationError: If calculation fails
        
        Example:
            >>> ZLong = wall.calc_ZLong()
            >>> print(f"ZLong at 1 MHz: {abs(ZLong[0]):.3e} Ω")
        """
        try:
            KZeff = self._calc_KZeff()
            
            # Zlong = pipe_len * KZeff / (2 * pi * pipe_rad_m)
            ZLong = (self.chamber.pipe_len_m * KZeff / 
                    (2.0 * const.pi * self.chamber.pipe_rad_m))
            
            # For future refinement we foresee a longitudinal correction factor
            # not fully implemented at the moment
            # corr_imp_long = self._calc_corr_imp_long_factor(KZeff)
            # ZLong_corr = ZLong * corr_imp_long / self._corr_imp
            
            # Apply correction factor
            ZLong_corr = ZLong / self._corr_imp
            
            # For corr_imp equal to infinity we need to change the results of
            # 1 / inf from nan to 0
            ZLong_corr[np.isnan(ZLong_corr)] = 0
            
            self._ZLong = ZLong_corr
            return ZLong_corr
            
        except Exception as e:
            raise TlWallCalculationError(
                f"Failed to calculate longitudinal impedance: {e}"
            ) from e
    
    @property
    def ZLong(self) -> np.ndarray:
        """
        Longitudinal impedance (cached).
        
        Automatically calculates if not already computed.
        
        Returns:
            Complex array of longitudinal impedance [Ω]
        """
        if self._ZLong is None:
            self._ZLong = self.calc_ZLong()
        return self._ZLong
    
    # =========================================================================
    # Transverse Impedance
    # =========================================================================
    
    def calc_ZTrans(self) -> np.ndarray:
        """
        Calculate transverse impedance.
        
        Formula:
            ZTrans = (2 * Zlongin * bypass) / (r² * β)
        
        where:
            Zlongin = inner longitudinal impedance
            bypass = inductive bypass factor
            r = pipe radius
            β = electromagnetic wave factor
        
        Returns:
            Complex array of transverse impedance [Ω/m]
        
        Raises:
            TlWallCalculationError: If calculation fails
        
        Example:
            >>> ZTrans = wall.calc_ZTrans()
            >>> print(f"ZTrans at 1 MHz: {abs(ZTrans[0]):.3e} Ω/m")
        """
        try:
            KZeffin = self._calc_KZeffin()
            
            # Inner longitudinal impedance
            Zlongin = (self.chamber.pipe_len_m * KZeffin / 
                      (2 * const.pi * self.chamber.pipe_rad_m))
            
            # Electromagnetic wave factor
            beta = (2 * const.pi * self.f * 
                   np.sqrt(const.epsilon_0 * const.mu_0) / 
                   self.beam.betarel)
            
            # Check if boundary is PEC - no bypass in that case
            if self.chamber.layers[-1].layer_type.upper() == 'PEC':
                # No bypass for PEC boundary
                ZTrans = (2 * Zlongin / 
                         (self.chamber.pipe_rad_m**2 * beta))
            else:
                # Inductive term
                Ind = (const.mu_0 * self.chamber.layers[-1].mu / 
                      (const.mu_0 + self.chamber.layers[-1].mu))
                Zind = 1j * self.f * Ind * self.chamber.pipe_len_m
                
                # Bypass factor
                bypass = Zind / (Zlongin + Zind)
                
                # Z_dip = 2 * Zlongin * bypass / (pipe_rad_m**2 * beta)
                ZTrans = (2 * Zlongin * bypass / 
                         (self.chamber.pipe_rad_m**2 * beta))
            
            # Apply correction factor
            ZTrans_corr = ZTrans / self._corr_imp
            
            # For corr_imp equal to infinity we need to change the results of
            # 1 / inf from nan to 0
            ZTrans_corr[np.isnan(ZTrans_corr)] = 0
            
            self._ZTrans = ZTrans_corr
            return ZTrans_corr
            
        except Exception as e:
            raise TlWallCalculationError(
                f"Failed to calculate transverse impedance: {e}"
            ) from e
    
    @property
    def ZTrans(self) -> np.ndarray:
        """
        Transverse impedance (cached).
        
        Automatically calculates if not already computed.
        
        Returns:
            Complex array of transverse impedance [Ω/m]
        """
        if self._ZTrans is None:
            self._ZTrans = self.calc_ZTrans()
        return self._ZTrans
    
    # =========================================================================
    # Dipolar and Quadrupolar Impedances (with Yokoya factors)
    # =========================================================================
    
    @property
    def ZDipX(self) -> np.ndarray:
        """
        Horizontal dipolar impedance.
        
        Includes Yokoya driving factor and betatron function.
        
        Formula:
            ZDipX = ZTrans * yokoya_drivx * betax
        
        Returns:
            Complex array of horizontal dipolar impedance [Ω]
        """
        if self._ZTrans is None:
            self._ZTrans = self.calc_ZTrans()
        
        # For circular chamber, Yokoya factor = 1
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            return self._ZTrans * self.chamber.betax
        else:
            return (self._ZTrans * self.chamber.drivx_yokoya_factor * 
                    self.chamber.betax)
    
    @property
    def ZDipY(self) -> np.ndarray:
        """
        Vertical dipolar impedance.
        
        Includes Yokoya driving factor and betatron function.
        
        Formula:
            ZDipY = ZTrans * yokoya_drivy * betay
        
        Returns:
            Complex array of vertical dipolar impedance [Ω]
        """
        if self._ZTrans is None:
            self._ZTrans = self.calc_ZTrans()
        
        # For circular chamber, Yokoya factor = 1
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            return self._ZTrans * self.chamber.betay
        else:
            return (self._ZTrans * self.chamber.drivy_yokoya_factor * 
                    self.chamber.betay)
    
    @property
    def ZQuadX(self) -> np.ndarray:
        """
        Horizontal quadrupolar impedance (wall contribution only).
        
        Includes Yokoya detuning factor and betatron function.
        
        Formula (non-circular):
            ZQuadX = ZTrans * yokoya_detx * betax
        
        Formula (circular, Wake2D compatible):
            ZQuadX = ZLong * k / (2*γ²)
            where k = 2πf/(βc)
        
        Returns:
            Complex array of horizontal quadrupolar impedance [Ω/m]
        
        Note:
            For circular chambers, Wake2D calculates a non-zero quadrupolar
            impedance proportional to ZLong, not using Yokoya factors.
            
            OLD APPROACH (Yokoya-based, returns 0 for circular):
            For circular chambers, yokoya_detx = 0, so ZQuadX = 0.
            This assumes no geometric quadrupolar coupling in circular symmetry.
        """
        if self._ZTrans is None:
            self._ZTrans = self.calc_ZTrans()
        
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            # -----------------------------------------------------------------
            # OLD APPROACH: Yokoya-based (returns 0 for circular chamber)
            # -----------------------------------------------------------------
            # return np.zeros_like(self._ZTrans)
            
            # -----------------------------------------------------------------
            # NEW APPROACH: Wake2D formula (non-zero for circular chamber)
            # ZQuad = ZLong * k / (2*γ²)
            # This comes from the transmission line theory used in Wake2D
            # -----------------------------------------------------------------
            if self._ZLong is None:
                self._ZLong = self.calc_ZLong()
            k = 2 * const.pi * self.f / (self.beam.betarel * const.c)
            return self._ZLong * k / (2 * self.beam.gammarel**2)
        else:
            return (self._ZTrans * self.chamber.detx_yokoya_factor * 
                    self.chamber.betax)
    
    @property
    def ZQuadY(self) -> np.ndarray:
        """
        Vertical quadrupolar impedance (wall contribution only).
        
        Includes Yokoya detuning factor and betatron function.
        
        Formula (non-circular):
            ZQuadY = ZTrans * yokoya_dety * betay
        
        Formula (circular, Wake2D compatible):
            ZQuadY = ZLong * k / (2*γ²)
            where k = 2πf/(βc)
        
        Returns:
            Complex array of vertical quadrupolar impedance [Ω/m]
        
        Note:
            For circular chambers, Wake2D calculates a non-zero quadrupolar
            impedance proportional to ZLong, not using Yokoya factors.
            
            OLD APPROACH (Yokoya-based, returns 0 for circular):
            For circular chambers, yokoya_dety = 0, so ZQuadY = 0.
            This assumes no geometric quadrupolar coupling in circular symmetry.
        """
        if self._ZTrans is None:
            self._ZTrans = self.calc_ZTrans()
        
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            # -----------------------------------------------------------------
            # OLD APPROACH: Yokoya-based (returns 0 for circular chamber)
            # -----------------------------------------------------------------
            # return np.zeros_like(self._ZTrans)
            
            # -----------------------------------------------------------------
            # NEW APPROACH: Wake2D formula (non-zero for circular chamber)
            # ZQuad = ZLong * k / (2*γ²)
            # This comes from the transmission line theory used in Wake2D
            # -----------------------------------------------------------------
            if self._ZLong is None:
                self._ZLong = self.calc_ZLong()
            k = 2 * const.pi * self.f / (self.beam.betarel * const.c)
            return self._ZLong * k / (2 * self.beam.gammarel**2)
        else:
            return (self._ZTrans * self.chamber.dety_yokoya_factor * 
                    self.chamber.betay)
    
    # =========================================================================
    # Surface Impedances
    # =========================================================================
    
    @property
    def ZLongSurf(self) -> np.ndarray:
        """
        Longitudinal surface impedance.
        
        Formula:
            ZLongSurf = ZLong * 2π * r
        
        Returns:
            Complex array of longitudinal surface impedance [Ω]
        """
        if self._ZLong is None:
            self._ZLong = self.calc_ZLong()
        
        return self._ZLong * 2 * const.pi * self.chamber.pipe_rad_m
    
    @property
    def ZTransSurf(self) -> np.ndarray:
        """
        Transverse surface impedance.
        
        Formula:
            ZTransSurf = ZTrans * 2π² * f * r³ / (β * c)
        
        Returns:
            Complex array of transverse surface impedance [Ω]
        """
        if self._ZTrans is None:
            self._ZTrans = self.calc_ZTrans()
        
        return (self._ZTrans * 2 * const.pi**2 * self.f * 
                self.chamber.pipe_rad_m**3 / (self.beam.betarel * const.c))
    
    # =========================================================================
    # Space Charge Impedances
    # =========================================================================
    
    def calc_ZLongDSC(self) -> np.ndarray:
        """
        Calculate longitudinal direct space charge impedance.
        
        Direct space charge arises from beam-beam interaction at test_beam_shift.
        For ultra-relativistic beams (gamma → ∞), returns zero.
        
        Formula:
            ZLong_DSC = -(jπfL * I₀(k·d/γ) * K₀(k·d/γ)) / (ε₀π(γβc)²)
        
        where:
            k = 2πf/(βc)
            d = test_beam_shift
            I₀, K₀ = modified Bessel functions
            L = pipe length
        
        Returns:
            np.ndarray: Complex array of longitudinal direct space charge impedance [Ω]
            
        Raises:
            TlWallCalculationError: If calculation fails
        """
        try:
            # Ultra-relativistic case
            if self.beam.gammarel == float('inf'):
                self._ZLongDSC = np.zeros(len(self.f), dtype=complex)
                return self._ZLongDSC
            
            kbess = 2 * const.pi * self.f / (self.beam.betarel * const.c)
            argbess0 = kbess * self.beam.test_beam_shift / self.beam.gammarel
            
            # Compute Bessel product safely (handles overflow with asymptotic)
            product = _safe_bessel_product_dsc(argbess0, order='long')
            
            # Longitudinal direct space charge
            ZLong_DSC = -(1j * const.pi * self.f * self.chamber.pipe_len_m * 
                         product / 
                         (const.epsilon_0 * const.pi * 
                          (self.beam.gammarel * self.beam.betarel * const.c)**2))
            
            self._ZLongDSC = ZLong_DSC
            return ZLong_DSC
            
        except Exception as e:
            raise TlWallCalculationError(
                f"Failed to calculate longitudinal direct space charge: {e}"
            ) from e
    
    @property
    def ZLongDSC(self) -> np.ndarray:
        """
        Longitudinal direct space charge impedance (cached).
        
        Automatically calculates if not already computed.
        
        Returns:
            Complex array of longitudinal direct space charge impedance [Ω]
        """
        if self._ZLongDSC is None:
            self._ZLongDSC = self.calc_ZLongDSC()
        return self._ZLongDSC
    
    def calc_ZLongISC(self) -> np.ndarray:
        """
        Calculate longitudinal indirect space charge impedance.
        
        Indirect space charge arises from chamber wall image current.
        For ultra-relativistic beams (gamma → ∞), returns zero.
        
        Formula:
            ZLong_ISC = -(jπfL * I₀²(k·d/γ) * (-K₀(k·r/γ)/I₀(k·r/γ))) / (ε₀π(γβc)²)
        
        where:
            k = 2πf/(βc)
            d = test_beam_shift
            r = pipe radius
            I₀, K₀ = modified Bessel functions
            L = pipe length
        
        Returns:
            np.ndarray: Complex array of longitudinal indirect space charge impedance [Ω]
            
        Raises:
            TlWallCalculationError: If calculation fails
        """
        try:
            # Ultra-relativistic case
            if self.beam.gammarel == float('inf'):
                self._ZLongISC = np.zeros(len(self.f), dtype=complex)
                return self._ZLongISC
            
            kbess = 2 * const.pi * self.f / (self.beam.betarel * const.c)
            argbess0 = kbess * self.beam.test_beam_shift / self.beam.gammarel
            argbess1 = kbess * self.chamber.pipe_rad_m / self.beam.gammarel
            
            # Compute Bessel product safely (handles overflow)
            product = _safe_bessel_product_i0(argbess0, argbess1, order='long')
            
            # Longitudinal indirect space charge
            ZLong_ISC = -(1j * const.pi * self.f * self.chamber.pipe_len_m * 
                         product / 
                         (const.epsilon_0 * const.pi * 
                          (self.beam.gammarel * self.beam.betarel * const.c)**2))
            
            self._ZLongISC = ZLong_ISC
            return ZLong_ISC
            
        except Exception as e:
            raise TlWallCalculationError(
                f"Failed to calculate longitudinal indirect space charge: {e}"
            ) from e
    
    @property
    def ZLongISC(self) -> np.ndarray:
        """
        Longitudinal indirect space charge impedance (cached).
        
        Automatically calculates if not already computed.
        
        Returns:
            Complex array of longitudinal indirect space charge impedance [Ω]
        """
        if self._ZLongISC is None:
            self._ZLongISC = self.calc_ZLongISC()
        return self._ZLongISC
    
    @property
    def ZLongTotal(self) -> np.ndarray:
        """
        Total longitudinal impedance including indirect space charge.
        
        This combines the wall impedance with indirect space charge effects,
        providing a more complete picture for comparison with codes like IW2D/Wake2D.
        
        Formula:
            ZLongTotal = ZLong + ZLongISC
        
        Returns:
            Complex array of total longitudinal impedance [Ω]
        
        Note:
            - ZLong: wall impedance (resistive wall contribution)
            - ZLongISC: indirect space charge (image current contribution)
            - For ultra-relativistic beams, ZLongISC → 0, so ZLongTotal ≈ ZLong
        
        Example:
            >>> wall = TlWall(chamber=chamber, beam=beam, frequencies=freqs)
            >>> ZTotal = wall.ZLongTotal
            >>> print(f"ZLongTotal at 1 MHz: {abs(ZTotal[0]):.3e} Ω")
        """
        return self.ZLong + self.ZLongISC
    
    def calc_ZTransDSC(self) -> np.ndarray:
        """
        Calculate transverse direct space charge impedance.
        
        Direct space charge arises from beam-beam interaction at test_beam_shift.
        For ultra-relativistic beams (gamma → ∞), returns zero.
        
        Formula:
            ZTrans_DSC = -(jZ₀L * I₁(k·d/γ) * K₁(k·d/γ) / d²) / (πγ²β)
        
        where:
            k = 2πf/(βc)
            d = test_beam_shift
            I₁, K₁ = modified Bessel functions of order 1
            L = pipe length
            Z₀ = impedance of free space
        
        Returns:
            np.ndarray: Complex array of transverse direct space charge impedance [Ω/m]
            
        Raises:
            TlWallCalculationError: If calculation fails
        """
        try:
            # Ultra-relativistic case
            if self.beam.gammarel == float('inf'):
                self._ZTransDSC = np.zeros(len(self.f), dtype=complex)
                return self._ZTransDSC
            
            kbess = 2 * const.pi * self.f / (self.beam.betarel * const.c)
            argbess0 = kbess * self.beam.test_beam_shift / self.beam.gammarel
            
            # Compute Bessel product safely: i1(a0)*k1(a0) with asymptotic ~ 1/(2*a0)
            product = _safe_bessel_product_dsc(argbess0, order='trans')
            
            # Apply the 1/d^2 factor
            product = product / (self.beam.test_beam_shift**2)
            
            ZTrans_DSC = -(1j * Z0 * self.chamber.pipe_len_m * product / 
                          (const.pi * self.beam.gammarel**2 * self.beam.betarel))
            
            self._ZTransDSC = ZTrans_DSC
            return ZTrans_DSC
            
        except Exception as e:
            raise TlWallCalculationError(
                f"Failed to calculate transverse direct space charge: {e}"
            ) from e
    
    @property
    def ZTransDSC(self) -> np.ndarray:
        """
        Transverse direct space charge impedance (cached).
        
        Automatically calculates if not already computed.
        
        Returns:
            Complex array of transverse direct space charge impedance [Ω/m]
        """
        if self._ZTransDSC is None:
            self._ZTransDSC = self.calc_ZTransDSC()
        return self._ZTransDSC
    
    def calc_ZTransISC(self) -> np.ndarray:
        """
        Calculate transverse indirect space charge impedance.
        
        Indirect space charge arises from chamber wall image current.
        For ultra-relativistic beams (gamma → ∞), returns zero.
        Special handling for on-axis beam (test_beam_shift = 0).
        
        Formula (off-axis):
            ZTrans_ISC = -(jZ₀L * I₁²(k·d/γ) * (-K₁(k·r/γ)/I₁(k·r/γ)) / d²) / (πγ²β)
        
        Formula (on-axis):
            ZTrans_ISC = (jZ₀L * k²/(2γ²) * K₁(k·r/γ)/I₁(k·r/γ)) / (2πγ²β)
        
        where:
            k = 2πf/(βc)
            d = test_beam_shift
            r = pipe radius
            I₁, K₁ = modified Bessel functions of order 1
        
        Returns:
            np.ndarray: Complex array of transverse indirect space charge impedance [Ω/m]
            
        Raises:
            TlWallCalculationError: If calculation fails
        """
        try:
            # Ultra-relativistic case
            if self.beam.gammarel == float('inf'):
                self._ZTransISC = np.zeros(len(self.f), dtype=complex)
                return self._ZTransISC
            
            kbess = 2 * const.pi * self.f / (self.beam.betarel * const.c)
            argbess0 = kbess * self.beam.test_beam_shift / self.beam.gammarel
            argbess1 = kbess * self.chamber.pipe_rad_m / self.beam.gammarel
            
            # Special case: on-axis beam
            if self.beam.test_beam_shift == 0.0:
                # k1(a1)/i1(a1) for large a1 → 0
                small_args = argbess1 < MAX_BESSEL_ARG
                BessA = np.zeros(len(self.f), dtype=float)
                
                if np.any(small_args):
                    with np.errstate(over='ignore', invalid='ignore'):
                        ratio = k1(argbess1[small_args]) / i1(argbess1[small_args])
                        ratio = np.where(np.isfinite(ratio), ratio, 0.0)
                        BessA[small_args] = (kbess[small_args]**2 / 
                                            (2 * self.beam.gammarel**2) * ratio)
                
                ZTrans_ISC = (1j * Z0 * self.chamber.pipe_len_m * BessA / 
                             (2 * const.pi * self.beam.gammarel**2 * self.beam.betarel))
            else:
                # Off-axis beam: use helper for i1^2 * (-k1/i1)
                product = _safe_bessel_product_i0(argbess0, argbess1, order='trans')
                
                # Apply 1/d^2 factor
                product = product / (self.beam.test_beam_shift**2)
                
                ZTrans_ISC = -(1j * Z0 * self.chamber.pipe_len_m * product / 
                             (const.pi * self.beam.gammarel**2 * self.beam.betarel))
            
            self._ZTransISC = ZTrans_ISC
            return ZTrans_ISC
            
        except Exception as e:
            raise TlWallCalculationError(
                f"Failed to calculate transverse indirect space charge: {e}"
            ) from e
    
    @property
    def ZTransISC(self) -> np.ndarray:
        """
        Transverse indirect space charge impedance (cached).
        
        Automatically calculates if not already computed.
        
        Returns:
            Complex array of transverse indirect space charge impedance [Ω/m]
        """
        if self._ZTransISC is None:
            self._ZTransISC = self.calc_ZTransISC()
        return self._ZTransISC
    
    @property
    def ZTransTotal(self) -> np.ndarray:
        """
        Total transverse impedance including indirect space charge.
        
        Formula:
            ZTransTotal = ZTrans + ZTransISC
        
        Returns:
            Complex array of total transverse impedance [Ω/m]
        """
        return self.ZTrans + self.ZTransISC
    
    @property
    def ZDipXTotal(self) -> np.ndarray:
        """
        Total horizontal dipolar impedance including indirect space charge.
        
        Formula:
            ZDipXTotal = ZDipX + ZDipISC (with appropriate Yokoya factor)
        
        Returns:
            Complex array of total horizontal dipolar impedance [Ω]
        """
        # For circular chamber, Yokoya factor = 1
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            return (self.ZTrans + self.ZTransISC) * self.chamber.betax
        else:
            return ((self.ZTrans + self.ZTransISC) * 
                    self.chamber.drivx_yokoya_factor * self.chamber.betax)
    
    @property
    def ZDipYTotal(self) -> np.ndarray:
        """
        Total vertical dipolar impedance including indirect space charge.
        
        Formula:
            ZDipYTotal = ZDipY + ZDipISC (with appropriate Yokoya factor)
        
        Returns:
            Complex array of total vertical dipolar impedance [Ω]
        """
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            return (self.ZTrans + self.ZTransISC) * self.chamber.betay
        else:
            return ((self.ZTrans + self.ZTransISC) * 
                    self.chamber.drivy_yokoya_factor * self.chamber.betay)
    
    @property
    def ZQuadXTotal(self) -> np.ndarray:
        """
        Total horizontal quadrupolar impedance including indirect space charge.
        
        Formula:
            ZQuadXTotal = ZQuadX + ZQuadISC
        
        For circular chambers (NEW, Wake2D compatible):
            ZQuadXTotal = ZLong * k/(2*γ²) + ZTransISC * betax
        
        For circular chambers (OLD, Yokoya-based):
            ZQuadXTotal = ZTransISC * betax  (wall contribution was 0)
        
        Returns:
            Complex array of total horizontal quadrupolar impedance [Ω/m]
        """
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            # -----------------------------------------------------------------
            # OLD APPROACH: Only ISC (wall contribution = 0 with Yokoya)
            # -----------------------------------------------------------------
            # return self.ZTransISC * self.chamber.betax
            
            # -----------------------------------------------------------------
            # NEW APPROACH: Wake2D formula for wall + ISC
            # ZQuadX now uses Wake2D formula (non-zero)
            # ZQuadISC uses transverse ISC with betax
            # -----------------------------------------------------------------
            return self.ZQuadX + self.ZTransISC * self.chamber.betax
        else:
            return ((self.ZTrans + self.ZTransISC) * 
                    self.chamber.detx_yokoya_factor * self.chamber.betax)
    
    @property
    def ZQuadYTotal(self) -> np.ndarray:
        """
        Total vertical quadrupolar impedance including indirect space charge.
        
        Formula:
            ZQuadYTotal = ZQuadY + ZQuadISC
        
        For circular chambers (NEW, Wake2D compatible):
            ZQuadYTotal = ZLong * k/(2*γ²) + ZTransISC * betay
        
        For circular chambers (OLD, Yokoya-based):
            ZQuadYTotal = ZTransISC * betay  (wall contribution was 0)
        
        Returns:
            Complex array of total vertical quadrupolar impedance [Ω/m]
        """
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            # -----------------------------------------------------------------
            # OLD APPROACH: Only ISC (wall contribution = 0 with Yokoya)
            # -----------------------------------------------------------------
            # return self.ZTransISC * self.chamber.betay
            
            # -----------------------------------------------------------------
            # NEW APPROACH: Wake2D formula for wall + ISC
            # ZQuadY now uses Wake2D formula (non-zero)
            # ZQuadISC uses transverse ISC with betay
            # -----------------------------------------------------------------
            return self.ZQuadY + self.ZTransISC * self.chamber.betay
        else:
            return ((self.ZTrans + self.ZTransISC) * 
                    self.chamber.dety_yokoya_factor * self.chamber.betay)
    
    # =========================================================================
    # Dipolar and Quadrupolar Space Charge Impedances
    # =========================================================================
    
    @property
    def ZDipDSC(self) -> np.ndarray:
        """
        Dipolar direct space charge impedance.
        
        Calculated as ZTransDSC multiplied by Yokoya driving factors.
        Uses average of X and Y driving factors for circular symmetry.
        
        Formula:
            ZDipDSC = ZTransDSC * (yokoya_drivx + yokoya_drivy) / 2
        
        Returns:
            Complex array of dipolar direct space charge impedance [Ω/m]
        """
        yokoya_avg = (self.chamber.drivx_yokoya_factor + 
                      self.chamber.drivy_yokoya_factor) / 2
        return self.ZTransDSC * yokoya_avg
    
    @property
    def ZDipISC(self) -> np.ndarray:
        """
        Dipolar indirect space charge impedance.
        
        Calculated as ZTransISC multiplied by Yokoya driving factors.
        Uses average of X and Y driving factors for circular symmetry.
        
        Formula:
            ZDipISC = ZTransISC * (yokoya_drivx + yokoya_drivy) / 2
        
        Returns:
            Complex array of dipolar indirect space charge impedance [Ω/m]
        """
        yokoya_avg = (self.chamber.drivx_yokoya_factor + 
                      self.chamber.drivy_yokoya_factor) / 2
        return self.ZTransISC * yokoya_avg
    
    @property
    def ZQuadDSC(self) -> np.ndarray:
        """
        Quadrupolar direct space charge impedance.
        
        Calculated as ZTransDSC multiplied by Yokoya detuning factors.
        Uses average of X and Y detuning factors for circular symmetry.
        
        Formula:
            ZQuadDSC = ZTransDSC * (yokoya_detx + yokoya_dety) / 2
        
        Returns:
            Complex array of quadrupolar direct space charge impedance [Ω/m]
        
        Note:
            For circular chambers, returns zero (direct space charge has no
            quadrupolar component in circular symmetry).
        """
        # For circular chamber, quadrupolar DSC = 0
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            return np.zeros_like(self.ZTransDSC)
        yokoya_avg = (self.chamber.detx_yokoya_factor + 
                      self.chamber.dety_yokoya_factor) / 2
        return self.ZTransDSC * yokoya_avg
    
    @property
    def ZQuadISC(self) -> np.ndarray:
        """
        Quadrupolar indirect space charge impedance.
        
        Calculated as ZTransISC multiplied by Yokoya detuning factors.
        Uses average of X and Y detuning factors.
        
        Formula:
            ZQuadISC = ZTransISC * (yokoya_detx + yokoya_dety) / 2
        
        Returns:
            Complex array of quadrupolar indirect space charge impedance [Ω/m]
        
        Note:
            For circular chambers, Yokoya factor = 1 for ISC.
            Unlike wall impedance, ISC has a quadrupolar component even 
            for circular chambers in non-relativistic regime.
        """
        # For circular chamber, ISC Yokoya factor = 1 (ISC exists even for circular)
        if self.chamber.chamber_shape.upper() == 'CIRCULAR':
            return self.ZTransISC
        yokoya_avg = (self.chamber.detx_yokoya_factor + 
                      self.chamber.dety_yokoya_factor) / 2
        return self.ZTransISC * yokoya_avg
        
    # =========================================================================
    # Internal Calculation Methods
    # =========================================================================
    
    def _calc_corr_imp_factor(self) -> np.ndarray:
        """
        Calculate correction impedance factor.
        
        Uses modified Bessel function to account for finite beam size.
        
        Returns:
            Array of reduction factors
        """
        reduct_factor = iv(
            0,
            2 * const.pi * self.f * self.chamber.pipe_rad_m / 
            (self.beam.betarel * const.c * self.beam.gammarel)
        )**2
        
        return reduct_factor
    
    def _calc_corr_imp_long_factor(self, KZeff: np.ndarray) -> np.ndarray:
        """
        Calculate longitudinal correction impedance factor.
        
        This factor is not used for the moment.
        For future refinement we foresee a longitudinal correction factor
        not fully implemented at the moment.
        
        Args:
            KZeff: Effective surface impedance
        
        Returns:
            Array of longitudinal correction factors
        
        Note:
            FUTURE IMPLEMENTATION: This method exists but is not called.
            It could be activated based on accuracy_factor:
            
            if self.accuracy_factor < 0.5:
                corr_imp_long = self._calc_corr_imp_long_factor(KZeff)
                ZLong_corr = ZLong * corr_imp_long / self._corr_imp
            else:
                ZLong_corr = ZLong / self._corr_imp
            
            See ACCURACY_FACTOR_ANALYSIS.md for detailed analysis.
        """
        reduct_factor = 1 + (1j * (const.epsilon_0 * self.f * KZeff *
                                    (self.chamber.pipe_rad_m + 3.85 *
                                     self.chamber.layers[0].thick_m)**2) /
                             self.chamber.pipe_rad_m)
        return reduct_factor
    
    def _calc_KZeff(self) -> np.ndarray:
        """
        Calculate effective surface impedance (KZeff) recursively.
        
        KZeff is calculated recursively with the formula:
            KZeff = KZ * (KZeff + j*KZ*tan(k*t)) / (KZ + j*KZeff*tan(k*t))
        
        For boundary layer:
            if PEC:    KZeff = 0
            elif V:    KZeff = Z0 * (1 - Scil)
            else:      KZeff = sqrt(mu/eps) = KZ
        
        It is used in the longitudinal calculation.
        
        Returns:
            Complex array of effective surface impedance
        
        Note:
            Scil correction factor accounts for finite beam size effects.
        """
        # Initialize with boundary layer
        if self.chamber.layers[-1].layer_type.upper() == 'PEC':
            KZeff = 0
            
        elif self.chamber.layers[-1].layer_type.upper() == 'V':
            kprop = 2 * const.pi * self.f / const.c
            
            # Scil is abs(1/i0(k r)) - abs(k0(k*r/(beta * gamma)))
            # First we calculate the first term and convert the nan obtained
            # when i0 is infinity to 0, then we subtract the second term
            Scil = np.abs(1 / iv(0, kprop * self.chamber.pipe_rad_m))
            Scil[np.isnan(Scil)] = 0
            
            arg = (kprop * self.chamber.pipe_rad_m / 
                  (self.beam.betarel * self.beam.gammarel))
            Scil = Scil - np.abs(kv(0, arg) * (1 - self.beam.betarel) / 
                                self.beam.gammarel**2)
            
            KZeff = Z0 * (1 - Scil)
        else:
            kprop = self.chamber.layers[-1].kprop
            KZ = self.chamber.layers[-1].KZ
            
            # ==========================================================
            # This part could be useful for magnetic boundary, to do in the
            # future a differentiation of this case to apply the correction
            # ==========================================================
            # Scil = 1 / iv(0, abs(kprop) * self.chamber.pipe_rad_m)
            # Scil[np.isnan(Scil)] = 0
            # KZeff = KZ * (1 - Scil)
            KZeff = KZ
        
        # Recursively calculate through layers (from outer to inner)
        for i in range(len(self.chamber.layers) - 2, -1, -1):
            layer = self.chamber.layers[i]
            
            if layer.layer_type.upper() == 'PEC':
                KZ = 0
            elif layer.layer_type.upper() == 'V':
                KZ = Z0
                kprop = 2 * const.pi * self.f / const.c
            else:
                kprop = layer.kprop
                KZ = layer.KZ
            
            # Handle infinite thickness: for an infinitely thick layer,
            # the effective impedance is simply KZ (no recursive formula needed)
            if np.isinf(layer.thick_m):
                # Scil correction factor for infinite layer
                Scil = 1 / np.abs(iv(0, 1j * kprop * self.chamber.pipe_rad_m))
                Scil[np.isnan(Scil)] = 0
                KZeff = KZ * (1 - Scil)
            else:
                # Tangent of propagation through layer
                tan_t_kprop = np.tan(kprop * layer.thick_m)
                
                # Scil correction factor
                Scil = 1 / (np.abs(iv(0, 1j * kprop * self.chamber.pipe_rad_m)) * 
                           np.abs(iv(0, 1j * kprop * layer.thick_m * 
                                    self.beam.gammarel * self.beam.betarel)))
                Scil[np.isnan(Scil)] = 0
                
                KZ = KZ * (1 - Scil)
                
                # Recursive formula
                KZeff = KZ * ((KZeff + 1j * KZ * tan_t_kprop) / 
                             (KZ + 1j * KZeff * tan_t_kprop))
        
        return KZeff
    
    def _calc_KZeffin(self) -> np.ndarray:
        """
        Calculate inner effective surface impedance (KZeffin) recursively.
        
        KZeffin is calculated recursively with the formula:
            KZeffin = KZ * (KZeffin + j*KZ*tan(k*t)) / (KZ + j*KZeffin*tan(k*t))
        
        For boundary layer:
            if PEC:    KZeffin = 0
            elif V:    KZeffin = Z0
            else:      KZeffin = sqrt(mu/eps) = KZ
        
        It is used in transverse calculation.
        
        Returns:
            Complex array of inner effective surface impedance
        
        Note:
            Unlike KZeff, this does not include Scil corrections.
        """
        # Initialize with boundary layer
        if self.chamber.layers[-1].layer_type.upper() == 'PEC':
            KZeffin = 0
        elif self.chamber.layers[-1].layer_type.upper() == 'V':
            KZeffin = Z0
        else:
            KZ = self.chamber.layers[-1].KZ
            KZeffin = KZ
        
        # Recursively calculate through layers (from outer to inner)
        for i in range(len(self.chamber.layers) - 2, -1, -1):
            layer = self.chamber.layers[i]
            
            if layer.layer_type.upper() == 'PEC':
                KZ = 0
            elif layer.layer_type.upper() == 'V':
                KZ = Z0
                kprop = 2 * const.pi * self.f / const.c
            else:
                kprop = layer.kprop
                KZ = layer.KZ
            
            # Handle infinite thickness: for an infinitely thick layer,
            # the effective impedance is simply KZ (no recursive formula needed)
            if np.isinf(layer.thick_m):
                KZeffin = KZ
            else:
                # Tangent of propagation through layer (using cmath for stability)
                try:
                    tan_t_kprop = np.array([
                        cmath.tan(k * layer.thick_m) for k in kprop
                    ])
                except TypeError:
                    # Single value case
                    tan_t_kprop = cmath.tan(kprop * layer.thick_m)
                
                # Recursive formula
                KZeffin = KZ * ((KZeffin + 1j * KZ * tan_t_kprop) / 
                               (KZ + 1j * KZeffin * tan_t_kprop))
        
        return KZeffin
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def get_all_impedances(self) -> dict:
        """
        Calculate and return all impedances.
        
        Returns:
            Dictionary with all impedance arrays:
                - 'ZLong': Longitudinal impedance
                - 'ZTrans': Transverse impedance
                - 'ZDipX': Horizontal dipolar
                - 'ZDipY': Vertical dipolar
                - 'ZQuadX': Horizontal quadrupolar
                - 'ZQuadY': Vertical quadrupolar
                - 'ZLongSurf': Longitudinal surface
                - 'ZTransSurf': Transverse surface
                - 'ZLongDSC': Longitudinal direct space charge
                - 'ZLongISC': Longitudinal indirect space charge
                - 'ZTransDSC': Transverse direct space charge
                - 'ZTransISC': Transverse indirect space charge
                - 'ZDipDSC': Dipolar direct space charge
                - 'ZDipISC': Dipolar indirect space charge
                - 'ZQuadDSC': Quadrupolar direct space charge
                - 'ZQuadISC': Quadrupolar indirect space charge
                - 'ZLongTotal': Total longitudinal (ZLong + ZLongISC)
                - 'ZTransTotal': Total transverse (ZTrans + ZTransISC)
                - 'ZDipXTotal': Total horizontal dipolar
                - 'ZDipYTotal': Total vertical dipolar
                - 'ZQuadXTotal': Total horizontal quadrupolar
                - 'ZQuadYTotal': Total vertical quadrupolar
        
        Example:
            >>> impedances = wall.get_all_impedances()
            >>> for name, Z in impedances.items():
            ...     print(f"{name}: {abs(Z[0]):.3e} Ω")
        """
        return {
            'ZLong': self.ZLong,
            'ZTrans': self.ZTrans,
            'ZDipX': self.ZDipX,
            'ZDipY': self.ZDipY,
            'ZQuadX': self.ZQuadX,
            'ZQuadY': self.ZQuadY,
            'ZLongSurf': self.ZLongSurf,
            'ZTransSurf': self.ZTransSurf,
            'ZLongDSC': self.ZLongDSC,
            'ZLongISC': self.ZLongISC,
            'ZTransDSC': self.ZTransDSC,
            'ZTransISC': self.ZTransISC,
            'ZDipDSC': self.ZDipDSC,
            'ZDipISC': self.ZDipISC,
            'ZQuadDSC': self.ZQuadDSC,
            'ZQuadISC': self.ZQuadISC,
            'ZLongTotal': self.ZLongTotal,
            'ZTransTotal': self.ZTransTotal,
            'ZDipXTotal': self.ZDipXTotal,
            'ZDipYTotal': self.ZDipYTotal,
            'ZQuadXTotal': self.ZQuadXTotal,
            'ZQuadYTotal': self.ZQuadYTotal,
        }
    
    def summary(self) -> str:
        """
        Generate summary string of TlWall configuration.
        
        Returns:
            Formatted string with configuration details
        
        Example:
            >>> print(wall.summary())
        """
        lines = [
            "TlWall Configuration",
            "=" * 50,
            f"Beam: gamma={self.beam.gammarel:.2f}, beta={self.beam.betarel:.6f}",
            f"Chamber: {self.chamber.chamber_shape}, r={self.chamber.pipe_rad_m*1000:.1f} mm",
            f"Frequencies: {len(self.f)} points from {self.f[0]:.2e} to {self.f[-1]:.2e} Hz",
            f"Layers: {len(self.chamber.layers)}",
            f"Accuracy factor: {self.accuracy_factor}",
        ]
        
        # Add layer info
        for i, layer in enumerate(self.chamber.layers):
            lines.append(f"  Layer {i+1}: {layer.layer_type}, t={layer.thick_m*1000:.3f} mm")
        
        # Add impedance status
        lines.append("")
        lines.append("Calculated Impedances:")
        if self._ZLong is not None:
            lines.append(f"  ZLong: ✓ (range: {abs(self._ZLong[0]):.3e} to {abs(self._ZLong[-1]):.3e} Ω)")
        else:
            lines.append("  ZLong: not calculated")
        
        if self._ZTrans is not None:
            lines.append(f"  ZTrans: ✓ (range: {abs(self._ZTrans[0]):.3e} to {abs(self._ZTrans[-1]):.3e} Ω/m)")
        else:
            lines.append("  ZTrans: not calculated")
        
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        """String representation."""
        return (f"TlWall(chamber={self.chamber.chamber_shape}, "
                f"beam_gamma={self.beam.gammarel:.2f}, "
                f"n_freq={len(self.f)}, "
                f"n_layers={len(self.chamber.layers)})")
    
    def __str__(self) -> str:
        """Human-readable string."""
        return self.summary()
