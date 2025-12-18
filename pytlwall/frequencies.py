"""
Frequencies utilities for impedance calculations.

This module provides the Frequencies class for managing frequency arrays
used in impedance calculations. Frequencies can be specified explicitly
or generated logarithmically from exponents.

Authors: Tatiana Rijoff, Carlo Zannini
Date:    01/03/2013
Updated: December 2025
"""

from __future__ import annotations

import numpy as np
from typing import Optional, Union, Sequence
import warnings

# Default values
DEFAULT_FMIN = 0
DEFAULT_FMAX = 8
DEFAULT_FSTEP = 2
DEFAULT_FREQ_UNIT = "Hz"
DEFAULT_SEP = " "


class Frequencies:
    """
    Frequency array manager for impedance calculations.
    
    This class handles frequency arrays in Hertz at which impedances are calculated.
    Frequencies can be provided as an explicit list or generated logarithmically
    from minimum and maximum exponents.
    
    The logarithmic generation creates an array from 10^fmin to 10^fmax with
    intermediate points based on fstep.
    
    Parameters
    ----------
    freq_list : array-like, optional
        Explicit list of frequencies in Hz. If provided, fmin/fmax/fstep are ignored.
    fmin : float, optional
        Minimum frequency exponent (base 10). Default is 0 (1 Hz).
    fmax : float, optional
        Maximum frequency exponent (base 10). Default is 8 (100 MHz).
    fstep : float, optional
        Step exponent for logarithmic spacing. Default is 2.
        **Note**: In the current implementation, LARGER fstep values produce
        MORE frequency points (higher resolution), and SMALLER fstep values
        produce FEWER points. This is counterintuitive but matches the
        original algorithm behavior.
    
    Attributes
    ----------
    freq : np.ndarray
        Array of frequencies in Hz.
    fmin : float
        Minimum frequency or its exponent.
    fmax : float
        Maximum frequency or its exponent.
    fstep : float
        Step exponent (0 if using explicit list).
    
    Examples
    --------
    Create frequencies from exponents:
    
    >>> freqs = Frequencies(fmin=0, fmax=6, fstep=1)
    >>> print(freqs.freq[:5])
    [1.e+00 2.e+00 3.e+00 ... ]
    
    Create from explicit list:
    
    >>> freq_list = [1e3, 1e4, 1e5, 1e6]
    >>> freqs = Frequencies(freq_list=freq_list)
    >>> print(freqs.freq)
    [1.e+03 1.e+04 1.e+05 1.e+06]
    
    Notes
    -----
    When using exponents (fmin, fmax, fstep), the frequency array is generated
    logarithmically to provide good coverage across orders of magnitude.
    """
    
    def __init__(
        self,
        freq_list: Optional[Sequence[float]] = None,
        fmin: float = DEFAULT_FMIN,
        fmax: float = DEFAULT_FMAX,
        fstep: float = DEFAULT_FSTEP,
    ) -> None:
        """Initialize Frequencies object."""
        # Initialize private attributes
        self._fmin = DEFAULT_FMIN
        self._fmax = DEFAULT_FMAX
        self._fstep = DEFAULT_FSTEP
        self._freq = np.array([])
        
        if freq_list is not None and len(freq_list) > 0:
            # Use the provided list of frequencies directly
            self._set_from_list(freq_list)
        else:
            # Generate frequencies from exponents
            self._set_from_exponents(fmin, fmax, fstep)
    
    def _set_from_list(self, freq_list: Sequence[float]) -> None:
        """
        Set frequencies from an explicit list.
        
        Parameters
        ----------
        freq_list : array-like
            List of frequencies in Hz.
        """
        try:
            self._freq = np.array(freq_list, dtype=float)
            
            # Validate frequencies are positive
            if np.any(self._freq <= 0):
                raise ValueError("All frequencies must be positive")
            
            # Sort frequencies
            self._freq = np.sort(self._freq)
            
            # Update min/max from the list
            self._fmin = float(np.min(self._freq))
            self._fmax = float(np.max(self._freq))
            self._fstep = 0.0  # Step not applicable for explicit list
            
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid frequency list: {e}")
    
    def _set_from_exponents(self, fmin: float, fmax: float, fstep: float) -> None:
        """
        Set frequencies by generating from exponents.
        
        Parameters
        ----------
        fmin : float
            Minimum frequency exponent.
        fmax : float
            Maximum frequency exponent.
        fstep : float
            Step exponent.
        """
        self.fmin = fmin
        self.fmax = fmax
        self.fstep = fstep
        self._freq = self._calc_freq_array(self._fmin, self._fmax, self._fstep)
    
    @property
    def freq(self) -> np.ndarray:
        """
        Get frequency array in Hz.
        
        Returns
        -------
        np.ndarray
            Array of frequencies in Hz.
        """
        return self._freq
    
    @property
    def fmin(self) -> float:
        """
        Get minimum frequency or exponent.
        
        Returns
        -------
        float
            Minimum frequency (Hz) or its exponent.
        """
        return self._fmin
    
    @fmin.setter
    def fmin(self, newfmin: float) -> None:
        """
        Set minimum frequency exponent.
        
        Parameters
        ----------
        newfmin : float
            New minimum frequency exponent.
        
        Raises
        ------
        ValueError
            If newfmin is not a valid number.
        """
        try:
            tmp_fmin = float(newfmin)
            if tmp_fmin > self._fmax:
                warnings.warn(
                    f"fmin ({tmp_fmin}) is greater than fmax ({self._fmax}). "
                    "This may produce unexpected results.",
                    UserWarning
                )
            self._fmin = tmp_fmin
        except (ValueError, TypeError):
            raise ValueError(
                f"{newfmin} is not a valid value for minimum frequency exponent"
            )
    
    @property
    def fmax(self) -> float:
        """
        Get maximum frequency or exponent.
        
        Returns
        -------
        float
            Maximum frequency (Hz) or its exponent.
        """
        return self._fmax
    
    @fmax.setter
    def fmax(self, newfmax: float) -> None:
        """
        Set maximum frequency exponent.
        
        Parameters
        ----------
        newfmax : float
            New maximum frequency exponent.
        
        Raises
        ------
        ValueError
            If newfmax is not a valid number.
        """
        try:
            tmp_fmax = float(newfmax)
            if tmp_fmax < self._fmin:
                warnings.warn(
                    f"fmax ({tmp_fmax}) is less than fmin ({self._fmin}). "
                    "This may produce unexpected results.",
                    UserWarning
                )
            self._fmax = tmp_fmax
        except (ValueError, TypeError):
            raise ValueError(
                f"{newfmax} is not a valid value for maximum frequency exponent"
            )
    
    @property
    def fstep(self) -> float:
        """
        Get frequency step exponent.
        
        Returns
        -------
        float
            Step exponent (0 if using explicit frequency list).
        
        Notes
        -----
        **Counterintuitive behavior**: LARGER fstep → MORE points (finer resolution).
        Example: fstep=3 gives more points than fstep=1.
        This matches the original algorithm implementation.
        """
        return self._fstep
    
    @fstep.setter
    def fstep(self, newfstep: float) -> None:
        """
        Set frequency step exponent.
        
        Parameters
        ----------
        newfstep : float
            New step exponent.
        
        Raises
        ------
        ValueError
            If newfstep is not a valid number.
        """
        try:
            tmp_fstep = float(newfstep)
            if tmp_fstep < 0:
                warnings.warn(
                    f"fstep ({tmp_fstep}) is negative. "
                    "This may produce unexpected results.",
                    UserWarning
                )
            self._fstep = tmp_fstep
        except (ValueError, TypeError):
            raise ValueError(
                f"{newfstep} is not a valid value for step frequency exponent"
            )
    
    def _calc_freq_array(self, fmin: float, fmax: float, fstep: float) -> np.ndarray:
        """
        Compute the frequency array from the given exponents.
        
        This method generates a logarithmically-spaced frequency array
        from 10^fmin to 10^fmax with intermediate steps based on fstep.
        
        Parameters
        ----------
        fmin : float
            Minimum frequency exponent (base 10).
        fmax : float
            Maximum frequency exponent (base 10).
        fstep : float
            Step exponent for intermediate points.
        
        Returns
        -------
        np.ndarray
            Array of frequencies in Hz.
        
        Notes
        -----
        The algorithm creates multiple points per decade based on fstep,
        providing better resolution at lower frequencies while covering
        a wide range.
        """
        if fmax < fmin:
            warnings.warn(
                f"fmax ({fmax}) < fmin ({fmin}). Returning empty array.",
                UserWarning
            )
            return np.array([])
        
        if fstep <= 0:
            warnings.warn(
                f"fstep ({fstep}) <= 0. Using default value.",
                UserWarning
            )
            fstep = DEFAULT_FSTEP
        
        f = np.array([])
        
        for p in np.arange(1, fmax - fmin + 1):
            v1 = (1 + (10 ** (1 - fstep))) * 10.0 ** (fmin - 1 + p)
            v2 = 10.0 ** (fmin + p)
            v3 = 10.0 ** (fmin - 1 + p - (fstep - 1))
            f = np.append(f, np.arange(v1, v2 + v3, v3))
        
        return f
    
    def update_from_exponents(self, fmin: float, fmax: float, fstep: float) -> None:
        """
        Update frequency array from new exponents.
        
        Parameters
        ----------
        fmin : float
            Minimum frequency exponent.
        fmax : float
            Maximum frequency exponent.
        fstep : float
            Step exponent.
        
        Examples
        --------
        >>> freqs = Frequencies(fmin=0, fmax=6, fstep=2)
        >>> freqs.update_from_exponents(fmin=2, fmax=8, fstep=1)
        """
        self._set_from_exponents(fmin, fmax, fstep)
    
    def __len__(self) -> int:
        """
        Get number of frequencies.
        
        Returns
        -------
        int
            Number of frequency points.
        """
        return len(self._freq)
    
    def __repr__(self) -> str:
        """
        String representation of Frequencies object.
        
        Returns
        -------
        str
            String representation.
        """
        if self._fstep == 0:
            return (
                f"Frequencies(n={len(self._freq)}, "
                f"range=[{self._fmin:.2e}, {self._fmax:.2e}] Hz, "
                f"explicit list)"
            )
        else:
            return (
                f"Frequencies(n={len(self._freq)}, "
                f"fmin={self._fmin}, fmax={self._fmax}, fstep={self._fstep})"
            )
    
    def __str__(self) -> str:
        """
        User-friendly string representation.
        
        Returns
        -------
        str
            Formatted string.
        """
        return repr(self)
