"""
Layer definition for material properties and surface impedance.

This module provides the Layer class for defining material layers in
vacuum chambers, including electrical and magnetic properties that
vary with frequency.

In addition to the original frequency-domain properties (``sigmaAC``,
``sigmaPM``, ``mu``, ``deltaM``, ``KZ`` ...), this revision also exposes
time-domain analogues used by the new :class:`pytlwall.tlwall_wake.TLWallWake`
calculator (``sigmaPM_time``, ``deltaM_time``, ``deltaM_time_boundary``,
``kprop_time``). The existing frequency-domain API is left untouched, so
every script that worked against the previous version keeps working
unchanged.

Authors: Tatiana Rijoff, Carlo Zannini
Date:    01/03/2013
Updated: December 2025
"""

from __future__ import annotations

import numpy as np
import scipy.constants as const
from typing import Optional, Sequence
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
    frequency- or time-dependent properties.

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
        Frequency array in Hz for frequency-domain calculations. Default is
        an empty array.
    time_s : array-like, optional
        Time array in seconds for time-domain wake calculations. Default is
        an empty array. Independent of ``freq_Hz``: either, both or neither
        may be set.
    boundary : bool, optional
        If True, sets layer as boundary (vacuum). Default is False.

    Notes
    -----
    Frequency-domain calculated quantities (``sigmaAC``, ``sigmaPM``, ``mur``,
    ``mu``, ``delta``, ``deltaM``, ``RS``, ``sigmaDC_R``, ``kprop``, ``KZ``)
    operate on ``freq_Hz``. Time-domain calculated quantities
    (``sigmaPM_time``, ``deltaM_time``, ``deltaM_time_boundary``,
    ``kprop_time``) operate on ``time_s``.

    The two pipelines are independent — accessing a time-domain property does
    not require ``freq_Hz`` to be populated, and vice versa.

    Roughness correction
    --------------------
    The frequency-domain conductivity ``sigmaAC`` includes a Hammerstad-type
    roughness correction via ``sigmaDC_R``. The current revision of the
    time-domain pipeline intentionally uses the raw ``sigmaDC`` *without*
    such a correction; a roughness model for the time domain is deferred to
    a future revision.
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
        time_s: Optional[Sequence[float]] = None,
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
        self._time_s = np.array([], dtype=float)

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
        if time_s is not None:
            self.time_s = time_s
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
        """Layer type: 'CW' (conductor), 'V' (vacuum), or 'PEC'."""
        return self._layer_type

    @layer_type.setter
    def layer_type(self, newtype: str) -> None:
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
        """Layer thickness in meters."""
        return self._thick_m

    @thick_m.setter
    def thick_m(self, newthick: float) -> None:
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
        """Relative permittivity (dielectric constant)."""
        return self._epsr

    @epsr.setter
    def epsr(self, newepsr: float) -> None:
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
        """Magnetic permeability parameter."""
        return self._muinf_Hz

    @muinf_Hz.setter
    def muinf_Hz(self, newmuinf_Hz: float) -> None:
        try:
            self._muinf_Hz = float(newmuinf_Hz)
        except (ValueError, TypeError) as e:
            raise LayerValidationError(
                f"Invalid permeability parameter '{newmuinf_Hz}': {e}"
            )

    @property
    def k_Hz(self) -> float:
        """Relaxation frequency for permeability (Hz)."""
        return self._k_Hz

    @k_Hz.setter
    def k_Hz(self, newk_Hz: float) -> None:
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
        """DC electrical conductivity (S/m)."""
        return self._sigmaDC

    @sigmaDC.setter
    def sigmaDC(self, newsigmaDC: float) -> None:
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
        """Relaxation time for permittivity (seconds)."""
        return self._tau

    @tau.setter
    def tau(self, newtau: float) -> None:
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
        """Surface roughness parameter (meters)."""
        return self._RQ

    @RQ.setter
    def RQ(self, newRQ: float) -> None:
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
        """Frequency array (Hz) used by the frequency-domain pipeline."""
        return self._freq_Hz

    @freq_Hz.setter
    def freq_Hz(self, newfreq_Hz: Sequence[float]) -> None:
        try:
            tmp_freq_Hz = np.array(newfreq_Hz, dtype=float)
            if np.any(tmp_freq_Hz <= 0):
                raise LayerValidationError("All frequencies must be positive")
            self._freq_Hz = tmp_freq_Hz
        except (TypeError, ValueError) as e:
            raise LayerValidationError(f"Invalid frequency array: {e}")

    @property
    def time_s(self) -> np.ndarray:
        """
        Time array (s) used by the time-domain wake pipeline.

        This attribute is independent of :attr:`freq_Hz` and is consumed by
        :class:`pytlwall.tlwall_wake.TLWallWake` and by the time-domain
        properties of this class (``sigmaPM_time``, ``deltaM_time`` ...).
        """
        return self._time_s

    @time_s.setter
    def time_s(self, newtime_s: Sequence[float]) -> None:
        try:
            tmp_time_s = np.array(newtime_s, dtype=float)
            if tmp_time_s.size > 0 and np.any(tmp_time_s <= 0):
                raise LayerValidationError("All time samples must be positive")
            self._time_s = tmp_time_s
        except (TypeError, ValueError) as e:
            raise LayerValidationError(f"Invalid time array: {e}")

    # ========================================================================
    # Surface Impedance (frequency domain - unchanged)
    # ========================================================================

    @property
    def KZ(self) -> np.ndarray:
        """
        Get surface impedance (frequency domain).

        Returns
        -------
        np.ndarray
            Complex surface impedance array.

        Notes
        -----
        If not explicitly set, calculates default surface impedance as
        ``KZ = (1 + j) / (sigmaPM * deltaM)``.
        """
        if self._KZ is not None:
            return self._KZ

        omega = 2.0 * const.pi * self.freq_Hz
        eps_complex = self.eps - 1.0j * self.sigmaAC / omega
        KZ = (1.0 + 1.0j) / (self.sigmaPM * self.deltaM)
        return KZ

    @KZ.setter
    def KZ(self, newKZ: np.ndarray) -> None:
        is_complex = np.iscomplex(newKZ)
        if isinstance(is_complex, np.ndarray):
            valid = is_complex.all()
        else:
            valid = bool(is_complex)

        if not valid:
            raise LayerValidationError("Surface impedance must be complex-valued")

        self._KZ = np.array(newKZ, dtype=complex)

    def set_surf_imped(
        self,
        newfreq_Hz: Sequence[float],
        newKZ: Sequence[complex],
    ) -> None:
        """
        Set surface impedance with interpolation to layer frequencies.
        """
        is_complex = np.iscomplex(newKZ)
        if isinstance(is_complex, np.ndarray):
            valid = is_complex.all()
        else:
            valid = bool(is_complex)

        if not valid:
            raise LayerValidationError("Surface impedance must be complex-valued")

        try:
            freq = np.array(newfreq_Hz, dtype=float)
        except (TypeError, ValueError) as e:
            raise LayerValidationError(f"Invalid frequency array: {e}")

        tmp_KZ = np.array(newKZ, dtype=complex)

        real_part = np.interp(self._freq_Hz, freq, tmp_KZ.real)
        imag_part = np.interp(self._freq_Hz, freq, tmp_KZ.imag)
        self._KZ = real_part + 1j * imag_part

    # ========================================================================
    # Calculated Properties — Frequency Domain (unchanged)
    # ========================================================================

    @property
    def sigmaAC(self) -> np.ndarray:
        """AC conductivity (frequency-dependent)."""
        return self._calc_sigmaAC()

    @property
    def sigmaPM(self) -> np.ndarray:
        """Effective conductivity magnitude (frequency-dependent)."""
        return self._calc_sigmaPM()

    @property
    def eps(self) -> float:
        """Absolute permittivity ``ε = ε₀ · εᵣ`` (F/m)."""
        return const.epsilon_0 * self._epsr

    @property
    def mur(self) -> np.ndarray:
        """Relative permeability (frequency-dependent, complex)."""
        return self._calc_mur()

    @property
    def mu(self) -> np.ndarray:
        """Absolute permeability ``μ = μ₀ · μᵣ`` (frequency-dependent, complex)."""
        return const.mu_0 * self._calc_mur()

    @property
    def delta(self) -> np.ndarray:
        """Skin depth (frequency-dependent, complex)."""
        return self._calc_delta()

    @property
    def deltaM(self) -> np.ndarray:
        """Modified skin depth (frequency-dependent, complex)."""
        return self._calc_deltaM()

    @property
    def RS(self) -> np.ndarray:
        """Surface resistance with Hammerstad roughness correction."""
        return self._calc_RS()

    @property
    def sigmaDC_R(self) -> np.ndarray:
        """DC conductivity with roughness correction."""
        return self._calc_sigmaDC_R()

    @property
    def kprop(self) -> np.ndarray:
        """Propagation constant ``(1 - j) / δ`` (frequency domain)."""
        return (1.0 - 1.0j) / self.delta

    # ========================================================================
    # Calculation Methods — Frequency Domain (unchanged)
    # ========================================================================

    def _calc_sigmaAC(self) -> np.ndarray:
        """``σ_AC = σ_DC_R / (1 + j·2π·τ·f)``."""
        return self.sigmaDC_R / (
            1.0 + 2.0j * const.pi * self.tau * self.freq_Hz
        )

    def _calc_mur(self) -> np.ndarray:
        """``μᵣ = 1 + μ_inf / (1 + j·f/k)``."""
        return 1.0 + self.muinf_Hz / (1.0 + 1.0j * (self.freq_Hz / self.k_Hz))

    def _calc_sigmaPM(self) -> np.ndarray:
        """``σ_PM = √[(2πfε)² + |σ_AC|²]``."""
        return np.sqrt(
            (2.0 * const.pi * self.freq_Hz * self.eps) ** 2
            + self.sigmaAC ** 2
        )

    def _calc_delta(self) -> np.ndarray:
        """``δ = √[2 / (2πfμσ_AC + j·με(2πf)²)]``."""
        return np.sqrt(
            2.0
            / (
                2.0 * const.pi * self.freq_Hz * self.mu * self.sigmaAC
                + 1.0j * self.mu * self.eps * (2.0 * const.pi * self.freq_Hz) ** 2
            )
        )

    def _calc_deltaM(self) -> np.ndarray:
        """``δ_M = √[2 / (2πfμσ_AC - j·με(2πf)²)]``."""
        return np.sqrt(
            2.0
            / (
                2.0 * const.pi * self.freq_Hz * self.mu * self.sigmaAC
                - 1.0j * self.mu * self.eps * (2.0 * const.pi * self.freq_Hz) ** 2
            )
        )

    def _calc_RS(self) -> np.ndarray:
        """Surface resistance with Hammerstad roughness model."""
        return (
            np.sqrt(self.mu * np.pi * self.freq_Hz / self.sigmaDC)
            * (
                1.0
                + (2.0 / np.pi)
                * np.arctan(
                    0.7 * self.mu * 2.0 * np.pi * self.freq_Hz
                    * self.sigmaDC * self.RQ ** 2
                )
            )
        )

    def _calc_sigmaDC_R(self) -> np.ndarray:
        """DC conductivity with roughness correction."""
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

    # ========================================================================
    # Calculated Properties — Time Domain (new in this revision)
    # ========================================================================
    #
    # Roughness correction
    # --------------------
    # In contrast with the frequency-domain pipeline (which uses ``sigmaAC``
    # built from the roughness-corrected ``sigmaDC_R``), the time-domain
    # quantities below intentionally use the raw, user-supplied ``sigmaDC``
    # without any Hammerstad-type correction. A time-domain roughness model
    # is deferred to a future revision.
    #
    # The permeability ``mu`` enters the time-domain formulas in the same
    # complex, frequency-dependent form as in the frequency domain. When
    # ``freq_Hz`` is empty, ``mu`` reduces to the DC limit ``μ₀·(1 + μ_inf)``
    # via the standard relaxation formula; this is the value of interest
    # for the wake calculation.
    #
    # NOTE — formulas validated against the MATLAB reference model
    # (``testwake_SPSwakemodel.m``):
    #
    #   * ``sigmaPM_time``        ↔ MATLAB ``sigma1noR`` / ``sigmaBC1``
    #   * ``deltaM_time``         ↔ MATLAB ``delta1noR`` (numerator 2)
    #   * ``deltaM_time_boundary``↔ MATLAB ``deltaBC1``  (numerator 4π)
    #
    # The dielectric term in both skin-depth formulas is ``(2π/t)²``
    # (i.e. ``4π²/t²``), matching the MATLAB ``4*pi*pi./t./t``. Both
    # skin-depth formulas use the raw, type-aware conductivity
    # ``_sigma_dc_effective``; the effective ``σ_PM(t)`` appears only in
    # the impedance prefactor of ``Zita_bound`` inside ``TLWallWake``,
    # never in the skin depth.

    @property
    def mu_time(self) -> np.ndarray:
        """
        Absolute permeability evaluated on the time-domain grid.

        Notes
        -----
        Returned as a complex array broadcast to the shape of ``time_s``.
        The relaxation model is the same as ``mu`` but the frequency that
        enters it is the heuristic ``f → 1/time_s``. When ``muinf_Hz == 0``
        (the default), this reduces to ``μ₀`` exactly.
        """
        mur_time = 1.0 + self.muinf_Hz / (
            1.0 + 1.0j * ((1.0 / self._time_s) / self.k_Hz)
        )
        return const.mu_0 * mur_time

    @property
    def _sigma_dc_effective(self) -> float:
        """
        Effective DC conductivity used by the time-domain formulas.

        Selected by layer type, mirroring the explicit conductivity
        constants used by the MATLAB reference model:

        * ``'V'``   → ``0.0``      — vacuum: no free charges
                      (MATLAB ``sigma0BC1 = 0``).
        * ``'PEC'`` → ``1.0e120``  — perfect conductor: a large finite
                      value (MATLAB ``sigma0BCPEC = 1e120``); avoids a
                      literal ``inf`` propagating through the formulas.
        * else      → :attr:`sigmaDC` — a real ``'CW'`` conductor.

        This is the single source of truth for "which conductivity does a
        time-domain formula see", so that the vacuum boundary is treated
        with ``σ = 0`` regardless of the (irrelevant) ``sigmaDC`` value
        stored on a ``'V'`` layer.
        """
        layer_type = self.layer_type.upper()
        if layer_type == "V":
            return 0.0
        if layer_type == "PEC":
            return 1.0e120
        return self.sigmaDC

    @property
    def sigmaPM_time(self) -> np.ndarray:
        """
        Time-domain effective conductivity magnitude.

        Formula
        -------
        ``σ_PM(t) = √[ (2π·ε/t)² + σ_DC² ]``

        with ``σ_DC`` taken from :attr:`_sigma_dc_effective` (type-aware:
        ``0`` for a vacuum layer). MATLAB reference: ``sigma1noR`` /
        ``sigmaBC1``.

        Notes
        -----
        Uses the raw conductivity without the roughness (Hammerstad)
        correction applied in the frequency domain — see the roughness
        note at the top of the time-domain section.
        """
        return np.sqrt(
            (2.0 * const.pi * self.eps / self._time_s) ** 2
            + self._sigma_dc_effective ** 2
        )

    @property
    def deltaM_time(self) -> np.ndarray:
        """
        Time-domain modified skin depth — formula for an internal layer.

        Formula
        -------
        ``δ_M(t) = √[ 2 / ( (2π/t)·μ·σ_DC − j·(2π/t)²·μ·ε ) ]``

        with ``σ_DC`` from :attr:`_sigma_dc_effective`. MATLAB reference:
        ``delta1noR`` (line 174 of the SPS model).

        Notes
        -----
        This is the formula used inside :class:`TLWallWake` for any layer
        that is **not** the boundary. The dielectric term uses ``(2π/t)²``
        — i.e. ``4π²/t²`` — matching the MATLAB ``4*pi*pi./t./t``.
        """
        omega_t = 2.0 * const.pi / self._time_s
        omega_t_sq = omega_t ** 2
        return np.sqrt(
            2.0
            / (
                omega_t * self.mu_time * self._sigma_dc_effective
                - 1.0j * omega_t_sq * self.mu_time * self.eps
            )
        )

    @property
    def deltaM_time_boundary(self) -> np.ndarray:
        """
        Time-domain modified skin depth — formula for a boundary layer.

        Formula
        -------
        ``δ_M(t) = √[ 4π / ( (2π/t)·μ·σ_DC − j·(2π/t)²·μ·ε ) ]``

        with ``σ_DC`` from :attr:`_sigma_dc_effective`. MATLAB reference:
        ``deltaBC1`` (line 167), where ``sqrt(2π)·sqrt(2/(…))`` collapses
        to ``sqrt(4π/(…))``.

        Notes
        -----
        Used inside :class:`TLWallWake` when this layer is the outermost
        layer (boundary). It differs from :attr:`deltaM_time` *only* in
        the numerator (``4π`` vs ``2``). Both use the **raw** conductivity
        ``σ_DC`` — the boundary skin depth does *not* use the effective
        ``σ_PM(t)`` (that quantity appears only in the impedance
        prefactor of ``Zita_bound``).
        """
        omega_t = 2.0 * const.pi / self._time_s
        omega_t_sq = omega_t ** 2
        return np.sqrt(
            4.0 * const.pi
            / (
                omega_t * self.mu_time * self._sigma_dc_effective
                - 1.0j * omega_t_sq * self.mu_time * self.eps
            )
        )

    @property
    def kprop_time(self) -> np.ndarray:
        """
        Time-domain propagation constant.

        Formula
        -------
        ``k_prop(t) = (1 − j) / δ_M(t)``

        Notes
        -----
        Built on :attr:`deltaM_time` (the internal-layer formula). It is
        consumed by :class:`TLWallWake` inside the layer-by-layer transport
        loop, where it multiplies the layer thickness inside ``tan(...)``.
        It is not used for the outermost (boundary) layer.
        """
        return (1.0 - 1.0j) / self.deltaM_time

    # ========================================================================
    # Dunder methods
    # ========================================================================

    def __repr__(self) -> str:
        return (
            f"Layer(type='{self.layer_type}', "
            f"thick={self.thick_m:.3e} m, "
            f"σ_DC={self.sigmaDC:.3e} S/m, "
            f"εᵣ={self.epsr:.2f}, "
            f"n_freq={len(self.freq_Hz)}, "
            f"n_time={len(self.time_s)})"
        )

    def __str__(self) -> str:
        return repr(self)
