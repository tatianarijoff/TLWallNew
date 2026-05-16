"""
Unit tests for the :class:`TLWallWake` class (time-domain wake calculator).

These tests mirror the layout used by ``test_tlwall.py`` and exercise:
* construction and input validation;
* the four wake functions (``WLong``, ``WLong_base``, ``WTrans_base``,
  ``WTrans_Bypass``) — shape, dtype, finiteness, caching;
* the four analytical-limit wakes (``WLongThick``, ``WTransThick``,
  ``WLongThin``, ``WTransThin``) — log-log slopes and correct edge
  behaviour when no CW layer is present;
* boundary special cases (PEC-only chamber).
"""

import inspect
import os
import sys
import unittest

import numpy as np

# Allow `python tests/test_tlwall_wake.py` from the repository root.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall.tlwall_wake import (
    TLWallWake,
    TLWallWakeConfigurationError,
)
from pytlwall.chamber import Chamber
from pytlwall.beam import Beam
from pytlwall.layer import Layer
from pytlwall.times import Times


# ---------------------------------------------------------------------------
# Helpers shared by every test class
# ---------------------------------------------------------------------------

def create_beam_lhc():
    """Build an LHC-like beam (γ ≈ 7460.52) using whichever API Beam offers."""
    sig = inspect.signature(Beam.__init__)
    params = list(sig.parameters.keys())
    if "gamma" in params:
        return Beam(gamma=7460.52)
    if "gammarel" in params:
        return Beam(gammarel=7460.52)
    if "Ekin_MeV" in params:
        return Beam(Ekin_MeV=7e6)
    return Beam(gammarel=7460.52)


def make_default_chamber(with_pec_boundary: bool = False) -> Chamber:
    """Build a simple circular chamber with a copper layer + boundary."""
    chamber = Chamber(pipe_rad_m=0.022, pipe_len_m=1.0,
                      chamber_shape="CIRCULAR")
    copper = Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7)
    boundary = Layer(layer_type="PEC") if with_pec_boundary else Layer(boundary=True)
    chamber.layers = [copper, boundary]
    return chamber


def make_default_times(n: int = 401) -> Times:
    """Build a default logspace time grid 1 fs → 100 s."""
    return Times(tmin_exp=-15, tmax_exp=2, n_points=n)


# ---------------------------------------------------------------------------
# Initialization & validation
# ---------------------------------------------------------------------------

class TestTLWallWakeInitialization(unittest.TestCase):
    """Construction of TLWallWake and basic configuration."""

    def setUp(self):
        self.chamber = make_default_chamber()
        self.beam = create_beam_lhc()
        self.times = make_default_times(n=101)

    def test_basic_initialization(self):
        """Test that TLWallWake is built and stores its inputs."""
        wake = TLWallWake(chamber=self.chamber, beam=self.beam,
                          times=self.times)
        self.assertIsInstance(wake, TLWallWake)
        self.assertIs(wake.chamber, self.chamber)
        self.assertIs(wake.beam, self.beam)
        self.assertIs(wake.times, self.times)
        self.assertEqual(wake.accuracy_factor, 0.3)

    def test_custom_accuracy_factor(self):
        """Test custom accuracy_factor is stored."""
        wake = TLWallWake(chamber=self.chamber, beam=self.beam,
                          times=self.times, accuracy_factor=0.5)
        self.assertEqual(wake.accuracy_factor, 0.5)

    def test_time_array_is_pushed_to_layers(self):
        """Test that time_s is propagated to every layer in the chamber."""
        TLWallWake(chamber=self.chamber, beam=self.beam, times=self.times)
        for layer in self.chamber.layers:
            np.testing.assert_array_equal(layer.time_s, self.times.time_s)

    def test_empty_chamber_raises(self):
        """Test that a chamber with no layers is rejected."""
        bare = Chamber(pipe_rad_m=0.022, chamber_shape="CIRCULAR")
        with self.assertRaises(TLWallWakeConfigurationError):
            TLWallWake(chamber=bare, beam=self.beam, times=self.times)

    def test_missing_attribute_raises(self):
        """Test that a duck-typed chamber lacking pipe_rad_m is rejected."""
        class BadChamber:
            pipe_len_m = 1.0
            layers = []
        with self.assertRaises(TLWallWakeConfigurationError):
            TLWallWake(chamber=BadChamber(), beam=self.beam, times=self.times)

    def test_invalid_accuracy_factor_raises(self):
        """Test that accuracy_factor must be strictly positive."""
        with self.assertRaises(ValueError):
            TLWallWake(chamber=self.chamber, beam=self.beam,
                       times=self.times, accuracy_factor=0)


# ---------------------------------------------------------------------------
# Wake functions: shape, dtype, finiteness, caching
# ---------------------------------------------------------------------------

class TestTLWallWakeWakes(unittest.TestCase):
    """Verify each wake function is computed correctly and cached."""

    def setUp(self):
        self.chamber = make_default_chamber()
        self.beam = create_beam_lhc()
        self.times = make_default_times(n=201)
        self.wake = TLWallWake(chamber=self.chamber, beam=self.beam,
                               times=self.times)

    def test_all_wakes_are_real_float64_arrays(self):
        """Test that every wake returns a real float64 array of the right length."""
        n = len(self.times.time_s)
        for name in ("WLong", "WLong_base", "WTrans_base", "WTrans_Bypass"):
            with self.subTest(wake=name):
                arr = getattr(self.wake, name)
                self.assertIsInstance(arr, np.ndarray)
                self.assertEqual(arr.dtype, np.float64)
                self.assertEqual(arr.shape, (n,))

    def test_all_wakes_are_finite(self):
        """Test no wake contains NaN or inf."""
        for name in ("WLong", "WLong_base", "WTrans_base", "WTrans_Bypass"):
            with self.subTest(wake=name):
                self.assertTrue(np.all(np.isfinite(getattr(self.wake, name))))

    def test_WLong_real_part_positive(self):
        """Test WLong (built on Re ζ) is non-negative up to round-off."""
        # WLong is built on Re{ζ_eff}, which is >= 0 for a passive wall.
        # At very long times Re{ζ_eff} collapses to ~0 for a non-conducting
        # boundary, and the recursive complex arithmetic can leave a
        # vanishingly small negative residue (round-off, ~1e-29 of the
        # signal). Allow a tolerance scaled by the wake's own magnitude;
        # a genuine sign error would be order-1 relative and still caught.
        w = self.wake.WLong
        tol = 1e-9 * np.abs(w).max()
        self.assertTrue(np.all(w >= -tol))

    def test_caching_returns_same_object(self):
        """Test that wake properties cache the result."""
        a = self.wake.WLong
        b = self.wake.WLong
        self.assertIs(a, b)

    def test_get_all_wakes_returns_eight_keys(self):
        """Test the convenience dict contains all 8 wakes."""
        wakes = self.wake.get_all_wakes()
        expected = {"WLong", "WLong_base", "WTrans_base", "WTrans_Bypass",
                    "WLongThick", "WTransThick", "WLongThin", "WTransThin"}
        self.assertEqual(set(wakes.keys()), expected)


# ---------------------------------------------------------------------------
# Analytical limits (Thick / Thin)
# ---------------------------------------------------------------------------

class TestTLWallWakeAnalyticalLimits(unittest.TestCase):
    """Verify the four analytical-limit wakes against their known properties."""

    def setUp(self):
        self.chamber = make_default_chamber()
        self.beam = create_beam_lhc()
        self.times = make_default_times(n=401)
        self.wake = TLWallWake(chamber=self.chamber, beam=self.beam,
                               times=self.times)

    def test_sigma_eff_is_max_over_cw_layers(self):
        """Test sigma_eff aggregates as max over CW layers."""
        # The chamber has one CW layer with sigmaDC = 5.96e7; the boundary is V.
        self.assertEqual(self.wake.sigma_eff, 5.96e7)

    def test_thick_eff_is_sum_over_cw_layers(self):
        """Test thick_eff aggregates as sum over CW layers."""
        self.assertAlmostEqual(self.wake.thick_eff, 2e-3, places=12)

    def test_thick_limits_positive_and_finite(self):
        """Test WLongThick / WTransThick are positive and finite."""
        for name in ("WLongThick", "WTransThick"):
            with self.subTest(wake=name):
                w = getattr(self.wake, name)
                self.assertEqual(w.dtype, np.float64)
                self.assertTrue(np.all(w > 0))
                self.assertTrue(np.all(np.isfinite(w)))

    def test_thin_limits_positive_and_finite(self):
        """Test WLongThin / WTransThin are positive and finite."""
        for name in ("WLongThin", "WTransThin"):
            with self.subTest(wake=name):
                w = getattr(self.wake, name)
                self.assertEqual(w.dtype, np.float64)
                self.assertTrue(np.all(w > 0))
                self.assertTrue(np.all(np.isfinite(w)))

    def test_log_log_slope_thick_long(self):
        """Test WLongThick has log-log slope = -3/2 (pure power law)."""
        t = self.times.time_s
        w = self.wake.WLongThick
        slope = (np.log(w[-1]) - np.log(w[0])) / (np.log(t[-1]) - np.log(t[0]))
        self.assertAlmostEqual(slope, -1.5, places=10)

    def test_log_log_slope_thick_trans(self):
        """Test WTransThick has log-log slope = -1/2."""
        t = self.times.time_s
        w = self.wake.WTransThick
        slope = (np.log(w[-1]) - np.log(w[0])) / (np.log(t[-1]) - np.log(t[0]))
        self.assertAlmostEqual(slope, -0.5, places=10)

    def test_log_log_slope_thin_long(self):
        """Test WLongThin has log-log slope = -2 (μ₀d/t² behaviour)."""
        t = self.times.time_s
        w = self.wake.WLongThin
        slope = (np.log(w[-1]) - np.log(w[0])) / (np.log(t[-1]) - np.log(t[0]))
        self.assertAlmostEqual(slope, -2.0, places=10)

    def test_log_log_slope_thin_trans(self):
        """Test WTransThin has log-log slope = -1 (since WLongThin·t·c/r²)."""
        t = self.times.time_s
        w = self.wake.WTransThin
        slope = (np.log(w[-1]) - np.log(w[0])) / (np.log(t[-1]) - np.log(t[0]))
        self.assertAlmostEqual(slope, -1.0, places=10)

    def test_WTransThin_equals_4_WLongThin_t_c_over_r2(self):
        """Test the analytical identity WTransThin = 4·WLongThin·t·c/r²."""
        import scipy.constants as const
        r = self.chamber.pipe_rad_m
        expected = 4.0 * self.wake.WLongThin * self.times.time_s * const.c / r ** 2
        np.testing.assert_allclose(self.wake.WTransThin, expected, rtol=1e-12)

    def test_limits_zero_when_no_cw_layer(self):
        """Test all four limits are zero when the chamber has no CW layer."""
        ch = Chamber(pipe_rad_m=0.022, pipe_len_m=1.0,
                     chamber_shape="CIRCULAR")
        ch.layers = [Layer(layer_type="PEC")]
        wake = TLWallWake(chamber=ch, beam=self.beam, times=self.times)
        self.assertEqual(wake.sigma_eff, 0.0)
        self.assertEqual(wake.thick_eff, 0.0)
        for name in ("WLongThick", "WTransThick", "WLongThin", "WTransThin"):
            with self.subTest(wake=name):
                self.assertTrue(np.all(getattr(wake, name) == 0.0))


# ---------------------------------------------------------------------------
# Special boundary cases
# ---------------------------------------------------------------------------

class TestTLWallWakeBoundaryCases(unittest.TestCase):
    """Special-case behaviour: PEC-only chamber, sign of Zita_eff, …"""

    def setUp(self):
        self.beam = create_beam_lhc()
        self.times = make_default_times(n=101)

    def test_single_pec_chamber_gives_zero_wakes(self):
        """Test that a chamber consisting of a single PEC layer gives zero wakes."""
        ch = Chamber(pipe_rad_m=0.022, pipe_len_m=1.0,
                     chamber_shape="CIRCULAR")
        ch.layers = [Layer(layer_type="PEC")]
        wake = TLWallWake(chamber=ch, beam=self.beam, times=self.times)
        for name in ("WLong", "WLong_base", "WTrans_base", "WTrans_Bypass"):
            with self.subTest(wake=name):
                self.assertTrue(np.all(getattr(wake, name) == 0))

    def test_vacuum_boundary_does_not_break_chain(self):
        """Test that a vacuum boundary on top of a CW layer yields finite wakes."""
        ch = make_default_chamber(with_pec_boundary=False)  # CW + vacuum
        wake = TLWallWake(chamber=ch, beam=self.beam, times=self.times)
        for name in ("WLong", "WLong_base", "WTrans_base", "WTrans_Bypass"):
            with self.subTest(wake=name):
                self.assertTrue(np.all(np.isfinite(getattr(wake, name))))


# ---------------------------------------------------------------------------
# String representation
# ---------------------------------------------------------------------------

class TestTLWallWakeStringRepresentation(unittest.TestCase):
    """Test __repr__ / __str__ / summary()."""

    def setUp(self):
        self.wake = TLWallWake(
            chamber=make_default_chamber(),
            beam=create_beam_lhc(),
            times=make_default_times(n=51),
        )

    def test_repr(self):
        """Test __repr__ contains class name and key counts."""
        s = repr(self.wake)
        self.assertIsInstance(s, str)
        self.assertIn("TLWallWake", s)
        self.assertIn("n_time", s)

    def test_str_uses_summary(self):
        """Test that __str__ produces the multi-line summary."""
        s = str(self.wake)
        self.assertIsInstance(s, str)
        self.assertIn("TLWallWake configuration", s)
        self.assertIn("Beam:", s)
        self.assertIn("Chamber:", s)
        self.assertIn("Times:", s)


# ---------------------------------------------------------------------------
# Visual comparison plots (TLWallWake full vs Thick/Thin analytical limits)
# ---------------------------------------------------------------------------
#
# These "tests" produce PNG files for visual inspection — following the same
# convention used by ``test_plot.py``. Each method exercises one chamber
# configuration (PEC, CW or Vacuum boundary) and dumps two comparison plots
# under ``tests/wake/``. The unittest assertion only checks that the file
# was created successfully; physical interpretation is left to the user.
#
# A coarser time grid is used than in the deep test (``wake_test1``), so
# these run in seconds rather than tens of seconds.

class TestTLWallWakePlots(unittest.TestCase):
    """Generate comparison plots: TLWallWake full vs analytical Thick/Thin limits."""

    @classmethod
    def setUpClass(cls):
        """Build the three chamber configurations once for the whole class."""
        # Lazy import: only this class needs matplotlib/plot_util.
        import pytlwall.plot_util as plot
        cls.plot = plot

        cls.savedir = os.path.join(os.path.dirname(__file__), "wake")
        os.makedirs(cls.savedir, exist_ok=True)

        cls.beam = create_beam_lhc()
        cls.times = Times(tmin_exp=-15, tmax_exp=2, n_points=401)

        # Three configurations sharing a common 2 mm copper inner layer,
        # differing only in the boundary type.
        cls.wakes = {
            "pec":    cls._make_wake(pytlwall_layer_pec()),
            "cw":     cls._make_wake(pytlwall_layer_cw_steel()),
            "vacuum": cls._make_wake(pytlwall_layer_vacuum()),
        }

    @classmethod
    def _make_wake(cls, boundary_layer: Layer) -> TLWallWake:
        """Build a TLWallWake with copper inner + the given boundary."""
        ch = Chamber(pipe_rad_m=0.022, pipe_len_m=1.0,
                     chamber_shape="CIRCULAR")
        ch.layers = [
            Layer(layer_type="CW", thick_m=2e-3, sigmaDC=5.96e7),
            boundary_layer,
        ]
        return TLWallWake(chamber=ch, beam=cls.beam, times=cls.times)

    def _plot_pair(self, case: str) -> None:
        """Produce the WLong_base and WTrans_base comparison plots for one case.

        The wakes compared against the analytical limits are ``WLong_base``
        (reactive part of ζ) and ``WTrans_base``. These are the quantities
        that physically reproduce the Thick-wall limit at low times and the
        Thin-wall limit at high times.

        ``WLong`` (resistive part, ``√(2π)`` / single-``I₀`` normalisation)
        and ``WTrans_Bypass`` (inductive bypass, which deliberately changes
        the long-time behaviour) are *different* normalisation variants and
        do **not** overlap the limits — they must not be used here. This
        mirrors the MATLAB reference ``testwake_SPSwakemodel.m``, whose
        figures plot ``WL1noRbase`` and ``WY1noR`` — not ``WL1noR`` /
        ``WY1noRbypass`` — against the Thick/Thin limits.
        """
        wake = self.wakes[case]
        t = self.times.time_s

        # Longitudinal: WLong_base (full) vs WLongThick vs WLongThin.
        self.plot.plot_wake_vs_limits(
            t=t,
            W_calc=wake.WLong_base,
            W_thick=wake.WLongThick,
            W_thin=wake.WLongThin,
            wake_type="WL",
            title=f"WLong_base vs analytical limits — {case} boundary",
            savedir=self.savedir,
            savename=f"WLong_{case}.png",
            calc_label="TLWallWake — WLong_base",
            thick_label="Thick-wall — WLongThick",
            thin_label="Thin-wall — WLongThin",
        )

        # Transverse: WTrans_base (full) vs WTransThick vs WTransThin.
        self.plot.plot_wake_vs_limits(
            t=t,
            W_calc=wake.WTrans_base,
            W_thick=wake.WTransThick,
            W_thin=wake.WTransThin,
            wake_type="WT",
            title=f"WTrans_base vs analytical limits — {case} boundary",
            savedir=self.savedir,
            savename=f"WTrans_{case}.png",
            calc_label="TLWallWake — WTrans_base",
            thick_label="Thick-wall — WTransThick",
            thin_label="Thin-wall — WTransThin",
        )

        # Assertions: both files must exist on disk.
        for name in (f"WLong_{case}.png", f"WTrans_{case}.png"):
            full_path = os.path.join(self.savedir, name)
            self.assertTrue(
                os.path.isfile(full_path),
                f"Expected plot was not created: {full_path}",
            )

    def test_plots_pec_boundary(self):
        """Generate WLong/WTrans comparison plots for the PEC-boundary chamber."""
        self._plot_pair("pec")

    def test_plots_cw_boundary(self):
        """Generate WLong/WTrans comparison plots for the CW-boundary chamber."""
        self._plot_pair("cw")

    def test_plots_vacuum_boundary(self):
        """Generate WLong/WTrans comparison plots for the vacuum-boundary chamber."""
        self._plot_pair("vacuum")

    @classmethod
    def tearDownClass(cls):
        """Close any figures left open by the plotting helpers."""
        try:
            cls.plot.close_all_figures()
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Boundary layer factories — module-level so the plot class can keep its
# setUpClass tidy. Defined after the class consumes them via a forward
# function reference (Python resolves names at call time).
# ---------------------------------------------------------------------------

def pytlwall_layer_pec() -> Layer:
    """Boundary layer factory: perfect electric conductor."""
    return Layer(layer_type="PEC")


def pytlwall_layer_cw_steel() -> Layer:
    """Boundary layer factory: 1 mm stainless-steel-like CW layer."""
    return Layer(layer_type="CW", thick_m=1e-3, sigmaDC=1.4e6)


def pytlwall_layer_vacuum() -> Layer:
    """Boundary layer factory: vacuum (V) boundary."""
    return Layer(boundary=True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
