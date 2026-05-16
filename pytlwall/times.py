"""
Times utility for time-domain wake calculations.

This module provides the :class:`Times` class for managing the array of time
points (in seconds) at which wake functions are evaluated. It mirrors the
role of :class:`pytlwall.frequencies.Frequencies` in the frequency-domain
calculations performed by :class:`pytlwall.tlwall.TlWall`.

Two construction modes are supported:

* From an explicit array (passed via ``time_list``).
* Logarithmically, via :func:`numpy.logspace` (``10 ** tmin_exp`` to
  ``10 ** tmax_exp``, both included, with ``n_points`` total samples).

Authors: Tatiana Rijoff, Carlo Zannini
Date:    December 2025
Copyright: CERN
"""

from __future__ import annotations

import warnings
from typing import Optional, Sequence

import numpy as np


# Defaults: 10^-12 s ... 10^-1 s with 1401 samples (1400 log-decades sub-steps).
DEFAULT_TMIN_EXP: float = -12.0
DEFAULT_TMAX_EXP: float = -1.0
DEFAULT_N_POINTS: int = 1401


class Times:
    """
    Time array manager for wake function calculations.

    The class stores a 1-D, strictly positive, monotonically increasing array
    of time samples in seconds. The array can be supplied explicitly via
    ``time_list`` or generated through :func:`numpy.logspace`.

    Parameters
    ----------
    time_list : array-like, optional
        Explicit array of time samples in seconds. If provided (and
        non-empty), ``tmin_exp``/``tmax_exp``/``n_points`` are ignored.
    tmin_exp : float, optional
        Base-10 exponent of the minimum time. Default ``-12`` (i.e. 1 ps).
    tmax_exp : float, optional
        Base-10 exponent of the maximum time. Default ``-1`` (i.e. 100 ms).
    n_points : int, optional
        Number of samples produced by :func:`numpy.logspace`. The endpoints
        ``10 ** tmin_exp`` and ``10 ** tmax_exp`` are *both* included.
        Default ``1401``.

    Attributes
    ----------
    time_s : np.ndarray
        Array of times in seconds. Sorted and strictly positive.
    tmin_exp : float
        Minimum exponent (only meaningful when generated via logspace).
    tmax_exp : float
        Maximum exponent (only meaningful when generated via logspace).
    n_points : int
        Number of samples (only meaningful when generated via logspace).

    Examples
    --------
    Default logarithmic time array (1 ps to 100 ms, 1401 points):

    >>> t = Times()
    >>> len(t)
    1401

    Custom range:

    >>> t = Times(tmin_exp=-9, tmax_exp=-3, n_points=601)
    >>> t.time_s[0], t.time_s[-1]
    (1e-09, 0.001)

    From an explicit list:

    >>> import numpy as np
    >>> t = Times(time_list=np.array([1e-9, 1e-8, 1e-7]))
    >>> t.time_s
    array([1.e-09, 1.e-08, 1.e-07])

    Notes
    -----
    The :func:`numpy.logspace` convention is preserved: ``n_points`` is the
    number of samples produced and **both endpoints are included**. To obtain
    ``N`` logarithmic sub-intervals over a range ask for ``N + 1`` points.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(
        self,
        time_list: Optional[Sequence[float]] = None,
        tmin_exp: float = DEFAULT_TMIN_EXP,
        tmax_exp: float = DEFAULT_TMAX_EXP,
        n_points: int = DEFAULT_N_POINTS,
    ) -> None:
        # Initialise private state with safe defaults.
        self._tmin_exp: float = DEFAULT_TMIN_EXP
        self._tmax_exp: float = DEFAULT_TMAX_EXP
        self._n_points: int = DEFAULT_N_POINTS
        self._time_s: np.ndarray = np.array([], dtype=float)

        if time_list is not None and len(time_list) > 0:
            self._set_from_list(time_list)
        else:
            self._set_from_logspace(tmin_exp, tmax_exp, n_points)

    # ------------------------------------------------------------------
    # Private setters
    # ------------------------------------------------------------------

    def _set_from_list(self, time_list: Sequence[float]) -> None:
        """Populate ``_time_s`` from an explicit, user-provided array."""
        arr = np.asarray(time_list, dtype=float)

        if np.any(arr <= 0):
            raise ValueError("All time samples must be strictly positive.")

        arr = np.sort(arr)
        self._time_s = arr

        # When the user supplies the array directly we still record some
        # metadata to make `repr` informative, but mark ``n_points`` as the
        # array length and the exponents as the log10 of the endpoints.
        self._tmin_exp = float(np.log10(arr[0]))
        self._tmax_exp = float(np.log10(arr[-1]))
        self._n_points = int(arr.size)

    def _set_from_logspace(
        self,
        tmin_exp: float,
        tmax_exp: float,
        n_points: int,
    ) -> None:
        """Populate ``_time_s`` via :func:`numpy.logspace`."""
        self.tmin_exp = tmin_exp
        self.tmax_exp = tmax_exp
        self.n_points = n_points
        self._time_s = np.logspace(self._tmin_exp, self._tmax_exp, self._n_points)

    # ------------------------------------------------------------------
    # Public properties
    # ------------------------------------------------------------------

    @property
    def time_s(self) -> np.ndarray:
        """1-D array of time samples in seconds."""
        return self._time_s

    @property
    def tmin_exp(self) -> float:
        """Base-10 exponent of the minimum time."""
        return self._tmin_exp

    @tmin_exp.setter
    def tmin_exp(self, value: float) -> None:
        try:
            tmp = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid tmin_exp value '{value}': {exc}") from exc

        if tmp > self._tmax_exp:
            warnings.warn(
                f"tmin_exp ({tmp}) is greater than tmax_exp ({self._tmax_exp}); "
                "this will yield a decreasing time range.",
                UserWarning,
            )
        self._tmin_exp = tmp

    @property
    def tmax_exp(self) -> float:
        """Base-10 exponent of the maximum time."""
        return self._tmax_exp

    @tmax_exp.setter
    def tmax_exp(self, value: float) -> None:
        try:
            tmp = float(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid tmax_exp value '{value}': {exc}") from exc

        if tmp < self._tmin_exp:
            warnings.warn(
                f"tmax_exp ({tmp}) is less than tmin_exp ({self._tmin_exp}); "
                "this will yield a decreasing time range.",
                UserWarning,
            )
        self._tmax_exp = tmp

    @property
    def n_points(self) -> int:
        """Number of samples in the time array."""
        return self._n_points

    @n_points.setter
    def n_points(self, value: int) -> None:
        try:
            tmp = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid n_points value '{value}': {exc}") from exc

        if tmp < 2:
            raise ValueError(
                f"n_points must be at least 2 to define a range, got {tmp}."
            )
        self._n_points = tmp

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def update_from_logspace(
        self,
        tmin_exp: float,
        tmax_exp: float,
        n_points: int,
    ) -> None:
        """
        Regenerate the time array from new logspace parameters.

        Parameters
        ----------
        tmin_exp, tmax_exp : float
            New base-10 exponents for the range.
        n_points : int
            New number of samples.
        """
        self._set_from_logspace(tmin_exp, tmax_exp, n_points)

    def __len__(self) -> int:
        return int(self._time_s.size)

    def __repr__(self) -> str:
        return (
            f"Times(n={len(self)}, "
            f"range=[{self._time_s[0]:.2e}, {self._time_s[-1]:.2e}] s, "
            f"tmin_exp={self._tmin_exp}, tmax_exp={self._tmax_exp})"
        )

    def __str__(self) -> str:
        return repr(self)
