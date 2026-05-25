"""
Time-domain wake function calculator for multi-layer chamber walls.

This module provides :class:`TLWallWake`, the time-domain counterpart of
:class:`pytlwall.tlwall.TlWall`. While :class:`TlWall` evaluates beam-coupling
impedances on a frequency grid, :class:`TLWallWake` evaluates the
**real-valued** wake functions on a time grid by recursively transporting a
surface impedance ``ζ`` through the chamber's layer stack and combining the
result with the appropriate Bessel-function form factors.

Deliverables
------------
* ``WLong``        — longitudinal wake from the resistive part of ζ.
* ``WLong_base``   — longitudinal wake "base" from the reactive part of ζ.
* ``WTrans_base``  — transverse wake "base", derived from ``WLong_base``.
* ``WTrans_Bypass``— transverse wake including the inductive bypass.

Naming convention
-----------------
The recursive surface impedance is denoted ``Zeta`` — the romanised form
of the Greek letter ζ conventionally used for surface impedance throughout
this module; inside the implementation we use the suffix scheme agreed with
the calling team:

* ``Zeta_bound`` — boundary-layer impedance (outermost, includes Scil
  correction).
* ``Zeta_layer`` — intrinsic impedance of the current internal layer
  (no Scil correction).
* ``Zeta_eff``   — impedance transported through the stack; also the final
  result returned to the wake formulas.

Authors: Tatiana Rijoff, Carlo Zannini
Date:    December 2025
Copyright: CERN
"""

from __future__ import annotations

from typing import Optional

import numpy as np
import scipy.constants as const
from scipy.special import i0


# Physical constants
# The speed of light and the vacuum permeability are referenced directly as
# ``const.c`` and ``const.mu_0`` — both are universally recognised symbols
# and read more clearly inline. Only the vacuum impedance keeps a local
# alias, since its ``physical_constants`` lookup is otherwise verbose.
Z0: float = const.physical_constants['characteristic impedance of vacuum'][0]

# Numerical safety: silence overflow / invalid in element-wise math; the
# downstream formulas already produce finite results when intermediate
# overflows occur (e.g. ``1 / i0(big) → 0``).
np.seterr(over='ignore', invalid='ignore')


# Defaults
DEFAULT_ACCURACY_FACTOR: float = 0.3


# --------------------------------------------------------------------------
# Custom exceptions
# --------------------------------------------------------------------------

class TLWallWakeError(Exception):
    """Base exception for the time-domain wake calculator."""


class TLWallWakeConfigurationError(TLWallWakeError):
    """Raised when the calculator is constructed with invalid inputs."""


class TLWallWakeCalculationError(TLWallWakeError):
    """Raised when a wake calculation fails."""


# --------------------------------------------------------------------------
# Main class
# --------------------------------------------------------------------------

class TLWallWake:
    """
    Time-domain wake function calculator.

    Parameters
    ----------
    chamber : pytlwall.chamber.Chamber
        Chamber geometry and layer stack. Must expose ``layers``,
        ``pipe_len_m`` and ``pipe_rad_m``.
    beam : pytlwall.beam.Beam
        Relativistic beam. Must expose ``gammarel`` and ``betarel``.
    times : pytlwall.times.Times
        Time grid. Must expose ``time_s``.
    accuracy_factor : float, optional
        Accuracy/precision selector. Currently stored for symmetry with
        :class:`pytlwall.tlwall.TlWall` and reserved for future use; it
        does **not** affect the present numerical results.

    Attributes
    ----------
    chamber, beam, times : object
        The user-supplied inputs (read-only properties).
    time_s : np.ndarray
        Shortcut to ``times.time_s``.
    Zeta_eff : np.ndarray
        Complex effective surface impedance transported through the stack.
    WLong : np.ndarray
        Longitudinal wake built from the resistive part of ζ_eff. This is a
        normalisation variant (``√(2π)`` factor, single ``I₀``) and does
        **not** reproduce the Thick/Thin analytical limits; use
        :attr:`WLong_base` when comparing against ``WLongThick`` /
        ``WLongThin``.
    WLong_base : np.ndarray
        Real-valued longitudinal "base" wake (from the reactive part of ζ).
    WTrans_base : np.ndarray
        Real-valued transverse "base" wake.
    WTrans_Bypass : np.ndarray
        Real-valued transverse wake including the inductive bypass.

    Notes
    -----
    On construction the ``time_s`` array is pushed onto every layer of the
    chamber, just like :class:`TlWall` pushes ``freq_Hz``. This is the
    mechanism through which the time-domain layer properties
    (``sigmaPM_time``, ``deltaM_time`` ...) become available.

    Example
    -------
    >>> from pytlwall import Chamber, Beam, Times, Layer, TLWallWake
    >>> chamber = Chamber(pipe_rad_m=0.022, pipe_len_m=1.0)
    >>> chamber.layers = [
    ...     Layer(layer_type='CW', thick_m=2e-3, sigmaDC=5.96e7),
    ...     Layer(boundary=True),
    ... ]
    >>> beam = Beam(gammarel=7460.52)
    >>> times = Times(tmin_exp=-12, tmax_exp=-1, n_points=1401)
    >>> wake = TLWallWake(chamber, beam, times)
    >>> w_long = wake.WLong
    >>> w_base = wake.WLong_base
    """

    # ---------------------------------------------------------------------
    # Construction
    # ---------------------------------------------------------------------

    def __init__(
        self,
        chamber,
        beam,
        times,
        accuracy_factor: float = DEFAULT_ACCURACY_FACTOR,
    ):
        # --- Validate duck-typed inputs ---------------------------------
        for attr in ("layers", "pipe_len_m", "pipe_rad_m"):
            if not hasattr(chamber, attr):
                raise TLWallWakeConfigurationError(
                    f"chamber must expose a '{attr}' attribute."
                )
        for attr in ("gammarel", "betarel"):
            if not hasattr(beam, attr):
                raise TLWallWakeConfigurationError(
                    f"beam must expose a '{attr}' attribute."
                )
        if not hasattr(times, "time_s"):
            raise TLWallWakeConfigurationError(
                "times must expose a 'time_s' attribute."
            )
        if not chamber.layers:
            raise TLWallWakeConfigurationError(
                "chamber must contain at least one layer."
            )
        if accuracy_factor <= 0:
            raise ValueError("accuracy_factor must be strictly positive.")

        # --- Store ------------------------------------------------------
        self._chamber = chamber
        self._beam = beam
        self._times = times
        self._accuracy_factor = float(accuracy_factor)

        # Shortcut
        self.time_s: np.ndarray = np.asarray(self._times.time_s, dtype=float)
        if self.time_s.size == 0:
            raise TLWallWakeConfigurationError(
                "times.time_s is empty; cannot evaluate wakes on an empty grid."
            )

        # Push the time grid onto every layer (same pattern as TlWall does
        # with freq_Hz). This activates the time-domain properties on each
        # Layer (``sigmaPM_time``, ``deltaM_time`` ...).
        for layer in self._chamber.layers:
            layer.time_s = self.time_s

        # --- Cache -------------------------------------------------------
        self._Zeta_eff: Optional[np.ndarray] = None
        self._WLong: Optional[np.ndarray] = None
        self._WLong_base: Optional[np.ndarray] = None
        self._WTrans_base: Optional[np.ndarray] = None
        self._WTrans_Bypass: Optional[np.ndarray] = None
        # Analytical reference wakes (thick-wall and thin-wall limits)
        self._WLongThick: Optional[np.ndarray] = None
        self._WTransThick: Optional[np.ndarray] = None
        self._WLongThin: Optional[np.ndarray] = None
        self._WTransThin: Optional[np.ndarray] = None

    # ---------------------------------------------------------------------
    # Read-only access to the inputs
    # ---------------------------------------------------------------------

    @property
    def chamber(self):
        """Chamber object passed at construction."""
        return self._chamber

    @property
    def beam(self):
        """Beam object passed at construction."""
        return self._beam

    @property
    def times(self):
        """Times object passed at construction."""
        return self._times

    @property
    def accuracy_factor(self) -> float:
        """Accuracy/precision selector (reserved for future use)."""
        return self._accuracy_factor

    @accuracy_factor.setter
    def accuracy_factor(self, value: float) -> None:
        if value <= 0:
            raise ValueError("accuracy_factor must be strictly positive.")
        self._accuracy_factor = float(value)

    # ---------------------------------------------------------------------
    # Derived quantities
    # ---------------------------------------------------------------------

    @property
    def kbess_time(self) -> np.ndarray:
        """
        Bessel argument scale in the time domain.

        Formula
        -------
        ``k_bess(t) = 2π / (c · β · t)``

        Notes
        -----
        Used both in the Scil correction at the boundary and in the wake
        formulas (where it is rescaled by ``r / (γ·β)``).
        """
        return 2.0 * const.pi / (const.c * self._beam.betarel * self.time_s)

    # ---------------------------------------------------------------------
    # Effective surface impedance ζ_eff (recursive transport)
    # ---------------------------------------------------------------------

    def _calc_Zeta_eff(self) -> np.ndarray:
        """
        Compute ``Zeta_eff`` by recursive transport through the layer stack.

        Algorithm
        ---------
        1. Initialise ``Zeta_eff = Zeta_bound`` from the outermost layer.

           * If the boundary is PEC:           ``Zeta_bound = 0`` (Scil = 0).
           * Otherwise:
             ``Scil_W   = 1 / I₀( k_bess · r )``
             ``Zeta_bound = (1 + j) / (σ_PM(t) · δ_M_boundary(t)) · (1 − Scil_W)``.

        2. Walk inwards from layer ``N-2`` down to layer ``0``. For each
           internal layer, compute its intrinsic impedance ``Zeta_layer``
           and propagate ``Zeta_eff`` through it using the standard
           transmission-line transport formula:

           ::

               Zeta_eff_new =
                   Zeta_layer
                   * ( Zeta_eff_old + j · Zeta_layer · tan(k_prop · t_layer) )
                   / ( Zeta_layer  + j · Zeta_eff_old · tan(k_prop · t_layer) ).

           Special cases for the internal layer:
             * PEC  → ``Zeta_eff`` is forced to 0 (perfect short).
             * V    → ``Zeta_layer = Z₀``, ``k_prop = (2π/t) / c``.
             * CW   → ``Zeta_layer = (1+j) / (σ_PM(t) · δ_M(t))``,
                       ``k_prop  = (1−j) / δ_M(t)``.

        Returns
        -------
        np.ndarray
            Complex effective surface impedance on the time grid.
        """
        layers = self._chamber.layers
        boundary = layers[-1]
        r = self._chamber.pipe_rad_m

        # ---- Boundary contribution -----------------------------------
        if boundary.layer_type.upper() == "PEC":
            # Perfect conductor short-circuits the boundary.
            Zeta_bound = np.zeros_like(self.time_s, dtype=complex)
        else:
            Scil_W = 1.0 / i0(self.kbess_time * r)
            # 1/inf → 0 silently; any NaN from intermediate overflow is
            # forced to zero (matches the convention used by TlWall).
            Scil_W = np.where(np.isfinite(Scil_W), Scil_W, 0.0)

            Zeta_bound = (
                (1.0 + 1.0j)
                / (boundary.sigmaPM_time * boundary.deltaM_time_boundary)
                * (1.0 - Scil_W)
            )

        Zeta_eff = np.asarray(Zeta_bound, dtype=complex)

        # ---- Transport from layer N-2 down to layer 0 ---------------
        for i in range(len(layers) - 2, -1, -1):
            layer = layers[i]
            t_layer = layer.thick_m
            ltype = layer.layer_type.upper()

            if ltype == "PEC":
                # PEC short: regardless of the previous Zeta_eff, the
                # transport collapses to zero.
                Zeta_eff = np.zeros_like(self.time_s, dtype=complex)
                continue

            if ltype == "V":
                Zeta_layer = Z0 * np.ones_like(self.time_s, dtype=complex)
                kprop_time = (2.0 * const.pi / self.time_s) / const.c
            else:
                # 'CW' or any other conductive-like layer.
                Zeta_layer = (1.0 + 1.0j) / (
                    layer.sigmaPM_time * layer.deltaM_time
                )
                kprop_time = layer.kprop_time

            tan_term = np.tan(kprop_time * t_layer)

            Zeta_eff = (
                Zeta_layer
                * (Zeta_eff + 1.0j * Zeta_layer * tan_term)
                / (Zeta_layer + 1.0j * Zeta_eff * tan_term)
            )

        # Any NaN/inf at this stage means a numerically degenerate sample;
        # zero them out so they cannot poison downstream wake formulas.
        Zeta_eff = np.where(np.isfinite(Zeta_eff), Zeta_eff, 0.0 + 0.0j)

        return Zeta_eff

    @property
    def Zeta_eff(self) -> np.ndarray:
        """Effective surface impedance ζ_eff (cached, complex)."""
        if self._Zeta_eff is None:
            self._Zeta_eff = self._calc_Zeta_eff()
        return self._Zeta_eff

    # ---------------------------------------------------------------------
    # Wake functions
    # ---------------------------------------------------------------------

    def _bessel_beam_factor(self) -> np.ndarray:
        """
        Bessel form factor evaluated at ``k_bess · r / (γ·β)``.

        Used by both :meth:`calc_WLong` and :meth:`calc_WLong_base`.
        """
        r = self._chamber.pipe_rad_m
        gamma = self._beam.gammarel
        beta = self._beam.betarel
        return i0(self.kbess_time * r / (gamma * beta))

    def calc_WLong(self) -> np.ndarray:
        """
        Longitudinal wake.

        Formula
        -------
        ``W_long(t) =
            L₁ · Re{ζ_eff(t)} / ( 2π·r · √(2π) · I₀( k_bess·r/(γβ) ) · t )``

        with ``L₁ = chamber.pipe_len_m``. The wake scales **linearly with
        the chamber length**, exactly like the coupling impedance and like
        the analytical limits :meth:`calc_WLongThick` /
        :meth:`calc_WLongThin`.

        MATLAB reference: ``WL1noR`` (line 238); the explicit ``L₁`` is
        absent there only because the reference model fixes ``L1 = 1`` and
        re-applies the per-element length afterwards. The ``√(2π)`` factor
        in the denominator is part of the time-domain normalisation and is
        **not** present in :meth:`calc_WLong_base`.

        Returns
        -------
        np.ndarray
            Real-valued longitudinal wake on the time grid.
        """
        try:
            r = self._chamber.pipe_rad_m
            L1 = self._chamber.pipe_len_m
            denom = (
                2.0 * const.pi * r
                * np.sqrt(2.0 * const.pi)
                * self._bessel_beam_factor() * self.time_s
            )
            wlong = L1 * np.real(self.Zeta_eff) / denom
            wlong = np.where(np.isfinite(wlong), wlong, 0.0)
            self._WLong = wlong.astype(float)
            return self._WLong
        except Exception as exc:  # pragma: no cover
            raise TLWallWakeCalculationError(
                f"Failed to compute WLong: {exc}"
            ) from exc

    @property
    def WLong(self) -> np.ndarray:
        """Longitudinal wake (cached, real)."""
        if self._WLong is None:
            self._WLong = self.calc_WLong()
        return self._WLong

    def calc_WLong_base(self) -> np.ndarray:
        """
        Longitudinal "base" wake (reactive part of ζ_eff).

        Formula
        -------
        ``W_long_base(t) =
            L₁ · Im{ζ_eff(t)} / ( 4π² · r · [I₀( k_bess · r / (γβ) )]² · t )``

        with ``L₁ = chamber.pipe_len_m`` — the wake scales linearly with
        the chamber length, consistently with :meth:`calc_WLong` and the
        analytical limits. MATLAB reference: ``WL1noRbase`` (line 240),
        evaluated there with ``L1 = 1``.

        Returns
        -------
        np.ndarray
            Real-valued longitudinal base wake.
        """
        try:
            r = self._chamber.pipe_rad_m
            L1 = self._chamber.pipe_len_m
            bessel = self._bessel_beam_factor()
            denom = 4.0 * const.pi ** 2 * r * bessel ** 2 * self.time_s
            wbase = L1 * np.imag(self.Zeta_eff) / denom
            wbase = np.where(np.isfinite(wbase), wbase, 0.0)
            self._WLong_base = wbase.astype(float)
            return self._WLong_base
        except Exception as exc:  # pragma: no cover
            raise TLWallWakeCalculationError(
                f"Failed to compute WLong_base: {exc}"
            ) from exc

    @property
    def WLong_base(self) -> np.ndarray:
        """Longitudinal base wake (cached, real)."""
        if self._WLong_base is None:
            self._WLong_base = self.calc_WLong_base()
        return self._WLong_base

    def calc_WTrans_base(self) -> np.ndarray:
        """
        Transverse "base" wake.

        Formula
        -------
        ``W_trans_base(t) = 4 · W_long_base(t) · t · c / r²``

        MATLAB reference: ``WY1noR`` (line 248) — the transverse TL-wall
        wake without the inductive bypass. It inherits the linear
        ``chamber.pipe_len_m`` scaling through :attr:`WLong_base`.

        Returns
        -------
        np.ndarray
            Real-valued transverse base wake.
        """
        try:
            r = self._chamber.pipe_rad_m
            wbase = 4.0 * self.WLong_base * self.time_s * const.c / r ** 2
            self._WTrans_base = wbase.astype(float)
            return self._WTrans_base
        except Exception as exc:  # pragma: no cover
            raise TLWallWakeCalculationError(
                f"Failed to compute WTrans_base: {exc}"
            ) from exc

    @property
    def WTrans_base(self) -> np.ndarray:
        """Transverse base wake (cached, real)."""
        if self._WTrans_base is None:
            self._WTrans_base = self.calc_WTrans_base()
        return self._WTrans_base

    def calc_WTrans_Bypass(self) -> np.ndarray:
        """
        Transverse wake with inductive bypass.

        Derivation (pre-simplification, for traceability)
        -------------------------------------------------
        Defining

        ::

            L_b1 = μ₀ / (4π)        (chamber bypass inductance per unit length)
            L_1  = chamber.pipe_len_m
            Y_1  = (2π / t) · L_b1 · L_1 / Z_0
            Y_2  = W_long_base(t) · t
            F_b1 = (Y_1 · Y_2) / (Y_1 + Y_2)

        the wake is

        ::

            W_trans_bypass(t) = (4 · t · c / r²) · F_b1 / t
                              = (4 · c / r²) · F_b1   ← the t's cancel.

        The implementation below uses the simplified form; the explicit
        ``Y_1, Y_2, F_b1`` decomposition is retained in the code for
        traceability against the analytical derivation.

        Since :attr:`WLong_base` scales with ``L₁``, both ``Y_1`` and
        ``Y_2`` are proportional to ``L₁``; hence ``F_b1`` and the returned
        wake also scale linearly with the chamber length, consistently
        with every other wake of this class.

        Returns
        -------
        np.ndarray
            Real-valued transverse bypass wake.
        """
        try:
            r = self._chamber.pipe_rad_m
            L1 = self._chamber.pipe_len_m
            Lb1 = const.mu_0 / (4.0 * const.pi)
            t = self.time_s

            # Pre-simplification (kept for traceability):
            #   Y1 = (2π/t) * Lb1 * L1 / Z0
            #   Y2 = WLong_base * t
            #   F  = (Y1 * Y2) / (Y1 + Y2)
            #   W  = (4 * t * c / r²) * F / t  →  (4 * c / r²) * F
            Y1 = (2.0 * const.pi / t) * Lb1 * L1 / Z0
            Y2 = self.WLong_base * t
            denom_F = Y1 + Y2
            # Guard against the (rare) sample where Y1 + Y2 = 0.
            F_b1 = np.where(denom_F != 0.0, (Y1 * Y2) / denom_F, 0.0)

            wbypass = (4.0 * const.c / r ** 2) * F_b1
            wbypass = np.where(np.isfinite(wbypass), wbypass, 0.0)
            self._WTrans_Bypass = wbypass.astype(float)
            return self._WTrans_Bypass
        except Exception as exc:  # pragma: no cover
            raise TLWallWakeCalculationError(
                f"Failed to compute WTrans_Bypass: {exc}"
            ) from exc

    @property
    def WTrans_Bypass(self) -> np.ndarray:
        """Transverse bypass wake (cached, real)."""
        if self._WTrans_Bypass is None:
            self._WTrans_Bypass = self.calc_WTrans_Bypass()
        return self._WTrans_Bypass

    # ---------------------------------------------------------------------
    # Analytical limits (Thick / Thin wall)
    # ---------------------------------------------------------------------
    #
    # The four properties below provide closed-form analytical wake limits
    # used for benchmarking the full transmission-line result. They depend
    # only on the geometry (chamber length L_1 and radius r), the beam
    # speed of light constant and on two single-number aggregates derived
    # from the chamber's layer stack:
    #
    #   * sigma_eff (Thick limit) — the **maximum** DC conductivity among
    #     all 'CW'-type layers. Rationale: in the deep-skin-effect regime
    #     the dissipation is dominated by the most conductive material.
    #
    #   * thick_eff (Thin limit) — the **sum** of the thicknesses of all
    #     'CW'-type layers. Rationale: the inductive thin-wall limit treats
    #     the conducting coating as a lumped element whose total cross
    #     section scales with the total conductor thickness.
    #
    # Layers of type 'V' (vacuum) and 'PEC' do not contribute to either
    # aggregate.

    def _cw_layers(self) -> list:
        """Return the list of CW (resistive) non-boundary layers in the chamber.

        Boundary layers are excluded even when their `layer_type` is
        'CW': a boundary is semi-infinite by definition, so its
        `thick_m` is a placeholder with no physical meaning, and its
        inclusion in `thick_eff` would contaminate the Thin-wall limit.

        Before the Layer.__init__ fix this exclusion was implicit (the
        old bug forced every boundary to type='V', which already
        filtered it out via the layer_type check). Now that the fix
        lets boundary layers keep their declared type, the exclusion
        must be explicit.
        """
        return [l for l in self._chamber.layers
                if l.layer_type.upper() == "CW"
                and not getattr(l, "boundary", False)]

    @property
    def sigma_eff(self) -> float:
        """
        Effective DC conductivity used by the Thick-wall analytical limit.

        Equal to ``max(layer.sigmaDC)`` taken over all 'CW' layers in the
        chamber. Returns ``0.0`` when no CW layer is present, in which
        case the Thick wakes degenerate to zero.
        """
        cw = self._cw_layers()
        return max((l.sigmaDC for l in cw), default=0.0)

    @property
    def thick_eff(self) -> float:
        """
        Effective total conductor thickness used by the Thin-wall limit.

        Equal to ``sum(layer.thick_m)`` taken over all 'CW' layers in the
        chamber. Returns ``0.0`` when no CW layer is present.
        """
        return sum(l.thick_m for l in self._cw_layers())

    def calc_WLongThick(self) -> np.ndarray:
        r"""
        Longitudinal wake - Thick-wall (resistive, deep skin-effect) limit.

        Formula::

            W_long_thick(t) = L_1 / (4 pi r) * sqrt( Z_0 / (pi c sigma_eff) ) * t^(-3/2)

        with ``sigma_eff = max_layer(sigmaDC)`` (see :attr:`sigma_eff`).

        Returns
        -------
        np.ndarray
            Real-valued Thick-wall longitudinal wake on the time grid.
            All zeros if no CW layer is present.
        """
        sigma = self.sigma_eff
        if sigma <= 0.0:
            return np.zeros_like(self.time_s, dtype=float)

        r = self._chamber.pipe_rad_m
        L1 = self._chamber.pipe_len_m
        coeff = (L1 / (4.0 * const.pi * r)) * np.sqrt(
            Z0 / (const.pi * const.c * sigma)
        )
        return (coeff * self.time_s ** (-1.5)).astype(float)

    @property
    def WLongThick(self) -> np.ndarray:
        """Thick-wall longitudinal wake limit (cached, real)."""
        return self.calc_WLongThick()

    def calc_WTransThick(self) -> np.ndarray:
        r"""
        Transverse wake - Thick-wall (resistive) limit.

        Formula::

            W_trans_thick(t) = L_1 / (pi r^3) * sqrt( c Z_0 / (pi sigma_eff) ) * t^(-1/2)

        MATLAB reference: ``WY1theory`` (line 260). Equivalently this is
        ``W_long_thick(t) * 4 c t / r^2``. Note that ``c`` sits in the
        **numerator** inside the square root (``c Z_0/(pi sigma)``), unlike
        the longitudinal thick-wall limit which has ``Z_0/(pi c sigma)``.

        Returns
        -------
        np.ndarray
            Real-valued Thick-wall transverse wake.
        """
        sigma = self.sigma_eff
        if sigma <= 0.0:
            return np.zeros_like(self.time_s, dtype=float)

        r = self._chamber.pipe_rad_m
        L1 = self._chamber.pipe_len_m
        coeff = (L1 / (const.pi * r ** 3)) * np.sqrt(
            const.c * Z0 / (const.pi * sigma)
        )
        return (coeff * self.time_s ** (-0.5)).astype(float)

    @property
    def WTransThick(self) -> np.ndarray:
        """Thick-wall transverse wake limit (cached, real)."""
        return self.calc_WTransThick()

    def calc_WLongThin(self) -> np.ndarray:
        r"""
        Longitudinal wake - Thin-wall (inductive) limit.

        Formula::

            W_long_thin(t) = L_1 / (2 pi r) * mu_0 * d_eff / t^2

        with ``d_eff = sum_layer thick_m`` taken over CW layers
        (see :attr:`thick_eff`).

        Returns
        -------
        np.ndarray
            Real-valued Thin-wall longitudinal wake.
        """
        d_eff = self.thick_eff
        if d_eff <= 0.0:
            return np.zeros_like(self.time_s, dtype=float)

        r = self._chamber.pipe_rad_m
        L1 = self._chamber.pipe_len_m
        coeff = (L1 / (2.0 * const.pi * r)) * const.mu_0 * d_eff
        return (coeff / self.time_s ** 2).astype(float)

    @property
    def WLongThin(self) -> np.ndarray:
        """Thin-wall longitudinal wake limit (cached, real)."""
        return self.calc_WLongThin()

    def calc_WTransThin(self) -> np.ndarray:
        r"""
        Transverse wake - Thin-wall (inductive) limit.

        Formula::

            W_trans_thin(t) = 4 * W_long_thin(t) * t * c / r^2

        Returns
        -------
        np.ndarray
            Real-valued Thin-wall transverse wake.
        """
        r = self._chamber.pipe_rad_m
        return (4.0 * self.WLongThin * self.time_s * const.c / r ** 2).astype(float)

    @property
    def WTransThin(self) -> np.ndarray:
        """Thin-wall transverse wake limit (cached, real)."""
        return self.calc_WTransThin()

    # ---------------------------------------------------------------------
    # Utility
    # ---------------------------------------------------------------------

    def get_all_wakes(self) -> dict:
        """
        Compute and return all wake functions in a single dictionary.

        Returns
        -------
        dict
            Mapping ``{name -> np.ndarray}`` containing every wake provided
            by this class: ``WLong``, ``WLong_base``, ``WTrans_base``,
            ``WTrans_Bypass``, plus the analytical reference wakes
            ``WLongThick``, ``WTransThick``, ``WLongThin``, ``WTransThin``.
        """
        return {
            "WLong": self.WLong,
            "WLong_base": self.WLong_base,
            "WTrans_base": self.WTrans_base,
            "WTrans_Bypass": self.WTrans_Bypass,
            "WLongThick": self.WLongThick,
            "WTransThick": self.WTransThick,
            "WLongThin": self.WLongThin,
            "WTransThin": self.WTransThin,
        }

    def summary(self) -> str:
        """Human-readable summary of the calculator configuration."""
        n_t = len(self.time_s)
        layers_info = "\n".join(
            f"  Layer {i + 1}: {l.layer_type}, t={l.thick_m * 1e3:.3f} mm"
            for i, l in enumerate(self._chamber.layers)
        )
        return (
            "TLWallWake configuration\n"
            "=========================\n"
            f"Beam:    gamma={self._beam.gammarel:.4g}, "
            f"beta={self._beam.betarel:.6f}\n"
            f"Chamber: r={self._chamber.pipe_rad_m * 1e3:.2f} mm, "
            f"L={self._chamber.pipe_len_m:.3f} m\n"
            f"Times:   {n_t} samples, "
            f"range=[{self.time_s[0]:.2e}, {self.time_s[-1]:.2e}] s\n"
            f"Layers ({len(self._chamber.layers)}):\n{layers_info}\n"
            f"Accuracy factor: {self._accuracy_factor}"
        )

    def __repr__(self) -> str:
        return (
            f"TLWallWake(n_layers={len(self._chamber.layers)}, "
            f"n_time={len(self.time_s)}, "
            f"beam_gamma={self._beam.gammarel:.3g})"
        )

    def __str__(self) -> str:
        return self.summary()
