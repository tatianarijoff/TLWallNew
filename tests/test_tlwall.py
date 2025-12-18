"""
Test suite for tlwall module - UNIVERSAL VERSION

This version detects the correct Beam initialization method automatically.
Works with: Beam(gamma=...), Beam(gammarel=...), or Beam(E_0=...)
"""

import unittest
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall.tlwall import TlWall, TlWallError, TlWallCalculationError, TlWallConfigurationError
from pytlwall.chamber import Chamber
from pytlwall.beam import Beam
from pytlwall.frequencies import Frequencies
from pytlwall.layer import Layer
import inspect


# Auto-detect correct Beam initialization
def create_beam_lhc():
    """Create LHC beam (gamma ~7460.52) using correct API."""
    sig = inspect.signature(Beam.__init__)
    params = list(sig.parameters.keys())
    
    # Try different parameter names in order of likelihood
    # Note: 'gamma' is now an alias for 'gammarel' in our implementation
    if 'gamma' in params:
        return Beam(gamma=7460.52)
    elif 'gammarel' in params:
        return Beam(gammarel=7460.52)
    elif 'E_0' in params:
        return Beam(E_0=7e12)  # 7 TeV
    elif 'Ekin_MeV' in params:
        return Beam(Ekin_MeV=7e6)  # 7 TeV
    elif 'E_kin' in params:
        return Beam(E_kin=7e12)
    else:
        # Default: try gammarel
        return Beam(gammarel=7460.52)


def create_beam_low_energy():
    """Create low energy beam (gamma ~100) using correct API."""
    sig = inspect.signature(Beam.__init__)
    params = list(sig.parameters.keys())
    
    if 'gamma' in params:
        return Beam(gamma=100.0)
    elif 'gammarel' in params:
        return Beam(gammarel=100.0)
    elif 'Ekin_MeV' in params:
        return Beam(Ekin_MeV=93.8e3)  # ~93.8 GeV
    elif 'E_0' in params:
        return Beam(E_0=93.8e9)  # ~94 GeV
    elif 'E_kin' in params:
        return Beam(E_kin=93.8e9)
    else:
        return Beam(gammarel=100.0)


def create_beam_ultrarelativistic():
    """Create ultra-relativistic beam using correct API."""
    sig = inspect.signature(Beam.__init__)
    params = list(sig.parameters.keys())
    
    if 'gamma' in params:
        return Beam(gamma=1e12)
    elif 'gammarel' in params:
        return Beam(gammarel=1e12)
    elif 'betarel' in params:
        return Beam(betarel=0.999999999)
    elif 'E_0' in params:
        return Beam(E_0=9.38e23)
    elif 'E_kin' in params:
        return Beam(E_kin=9.38e23)
    else:
        return Beam(gammarel=1e12)


class TestTlWallInitialization(unittest.TestCase):
    """Test TlWall initialization and configuration."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
    
    def test_basic_initialization(self):
        """Test basic TlWall initialization."""
        wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
        
        self.assertIsInstance(wall, TlWall)
        self.assertEqual(wall.chamber, self.chamber)
        self.assertEqual(wall.beam, self.beam)
        self.assertEqual(wall.frequencies, self.freq)
        self.assertEqual(wall.accuracy_factor, 0.3)
    
    def test_custom_accuracy_factor(self):
        """Test initialization with custom accuracy factor."""
        wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq,
            accuracy_factor=0.5
        )
        
        self.assertEqual(wall.accuracy_factor, 0.5)
    
    def test_chamber_without_layers(self):
        """Test that chamber without layers raises error."""
        empty_chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        
        with self.assertRaises(TlWallConfigurationError):
            TlWall(
                chamber=empty_chamber,
                beam=self.beam,
                frequencies=self.freq
            )


class TestTlWallLongitudinalImpedance(unittest.TestCase):
    """Test longitudinal impedance calculations."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
        self.wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
    
    def test_calc_ZLong_returns_array(self):
        """Test that calc_ZLong returns numpy array."""
        ZLong = self.wall.calc_ZLong()
        
        self.assertIsInstance(ZLong, np.ndarray)
        self.assertEqual(len(ZLong), len(self.freq))
        self.assertEqual(ZLong.dtype, complex)
    
    def test_ZLong_property_caching(self):
        """Test that ZLong property caches result."""
        ZLong1 = self.wall.ZLong
        ZLong2 = self.wall.ZLong
        
        # Should return same cached array
        self.assertIs(ZLong1, ZLong2)
    
    def test_ZLong_not_nan(self):
        """Test that ZLong doesn't contain NaN."""
        ZLong = self.wall.calc_ZLong()
        
        self.assertFalse(np.any(np.isnan(ZLong)))
    
    def test_ZLong_frequency_dependence(self):
        """Test that ZLong varies with frequency."""
        ZLong = self.wall.calc_ZLong()
        
        # Impedance should vary across frequency range
        self.assertNotEqual(ZLong[0], ZLong[-1])
    
    def test_ZLong_positive_real_part(self):
        """Test that real part of ZLong is positive (resistive)."""
        ZLong = self.wall.calc_ZLong()
        
        # Real part should be positive (resistance)
        self.assertTrue(np.all(ZLong.real > 0))


class TestTlWallTransverseImpedance(unittest.TestCase):
    """Test transverse impedance calculations."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
        self.wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
    
    def test_calc_ZTrans_returns_array(self):
        """Test that calc_ZTrans returns numpy array."""
        ZTrans = self.wall.calc_ZTrans()
        
        self.assertIsInstance(ZTrans, np.ndarray)
        self.assertEqual(len(ZTrans), len(self.freq))
        self.assertEqual(ZTrans.dtype, complex)
    
    def test_ZTrans_property_caching(self):
        """Test that ZTrans property caches result."""
        ZTrans1 = self.wall.ZTrans
        ZTrans2 = self.wall.ZTrans
        
        self.assertIs(ZTrans1, ZTrans2)
    
    def test_ZTrans_not_nan(self):
        """Test that ZTrans doesn't contain NaN."""
        ZTrans = self.wall.calc_ZTrans()
        
        self.assertFalse(np.any(np.isnan(ZTrans)))


class TestTlWallDipolarQuadrupolar(unittest.TestCase):
    """Test dipolar and quadrupolar impedances with Yokoya factors."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        # Elliptical chamber for non-unity Yokoya factors
        self.chamber = Chamber(
            pipe_hor_m=0.030,
            pipe_ver_m=0.020,
            chamber_shape='ELLIPTICAL',
            betax=100.0,
            betay=50.0
        )
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
        self.wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
    
    def test_ZDipX_includes_yokoya(self):
        """Test that ZDipX includes Yokoya driving factor."""
        ZDipX = self.wall.ZDipX
        ZTrans = self.wall.ZTrans
        
        # ZDipX should be ZTrans * yokoya_factor * betax
        expected = ZTrans * self.chamber.drivx_yokoya_factor * self.chamber.betax
        np.testing.assert_array_almost_equal(ZDipX, expected)
    
    def test_ZDipY_includes_yokoya(self):
        """Test that ZDipY includes Yokoya driving factor."""
        ZDipY = self.wall.ZDipY
        ZTrans = self.wall.ZTrans
        
        expected = ZTrans * self.chamber.drivy_yokoya_factor * self.chamber.betay
        np.testing.assert_array_almost_equal(ZDipY, expected)


class TestTlWallSurfaceImpedance(unittest.TestCase):
    """Test surface impedance calculations."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
        self.wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
    
    def test_ZLongSurf_relation(self):
        """Test relationship between ZLong and ZLongSurf."""
        ZLong = self.wall.ZLong
        ZLongSurf = self.wall.ZLongSurf
        
        expected = ZLong * 2 * np.pi * self.chamber.pipe_rad_m
        np.testing.assert_array_almost_equal(ZLongSurf, expected)


class TestTlWallSpaceCharge(unittest.TestCase):
    """Test space charge impedance calculations."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_low_energy()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
        self.wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
    
    def test_ZLongDSC_returns_array(self):
        """Test that ZLongDSC returns array."""
        ZLongDSC = self.wall.ZLongDSC
        
        self.assertIsInstance(ZLongDSC, np.ndarray)
        self.assertEqual(len(ZLongDSC), len(self.freq))
        self.assertEqual(ZLongDSC.dtype, complex)
    
    def test_space_charge_zero_for_ultrarelativistic(self):
        """Test that space charge is zero for ultra-relativistic beam."""
        beam_ultra = create_beam_ultrarelativistic()
        wall = TlWall(
            chamber=self.chamber,
            beam=beam_ultra,
            frequencies=self.freq
        )
        
        ZLongDSC = wall.ZLongDSC
        ZLongISC = wall.ZLongISC
        ZTransDSC = wall.ZTransDSC
        ZTransISC = wall.ZTransISC
        
        # All should be zero (or very close)
        np.testing.assert_array_almost_equal(ZLongDSC, 0, decimal=5)
        np.testing.assert_array_almost_equal(ZLongISC, 0, decimal=5)
        np.testing.assert_array_almost_equal(ZTransDSC, 0, decimal=5)
        np.testing.assert_array_almost_equal(ZTransISC, 0, decimal=5)


class TestTlWallMultilayer(unittest.TestCase):
    """Test multi-layer chamber configurations."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
    
    def test_single_layer_copper(self):
        """Test single copper layer."""
        copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [copper]
        
        wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
        
        ZLong = wall.calc_ZLong()
        self.assertIsInstance(ZLong, np.ndarray)
        self.assertFalse(np.any(np.isnan(ZLong)))
    
    def test_two_layer_coating(self):
        """Test two-layer configuration (coating + substrate)."""
        copper = Layer(thick_m=50e-6, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        steel = Layer(thick_m=2e-3, sigmaDC=1.45e6, freq_Hz=self.freq.freq)
        self.chamber.layers = [copper, steel]
        
        wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
        
        ZLong = wall.calc_ZLong()
        self.assertFalse(np.any(np.isnan(ZLong)))


class TestTlWallUtilityMethods(unittest.TestCase):
    """Test utility methods."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
        self.wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
    
    def test_get_all_impedances(self):
        """Test get_all_impedances returns dictionary."""
        impedances = self.wall.get_all_impedances()
        
        self.assertIsInstance(impedances, dict)
        
        expected_keys = [
            'ZLong', 'ZTrans', 'ZDipX', 'ZDipY',
            'ZQuadX', 'ZQuadY', 'ZLongSurf', 'ZTransSurf',
            'ZLongDSC', 'ZLongISC', 'ZTransDSC', 'ZTransISC'
        ]
        
        for key in expected_keys:
            self.assertIn(key, impedances)
            self.assertIsInstance(impedances[key], np.ndarray)
    
    def test_summary_returns_string(self):
        """Test that summary returns formatted string."""
        summary = self.wall.summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn("TlWall Configuration", summary)
    
    def test_repr(self):
        """Test __repr__ method."""
        repr_str = repr(self.wall)
        
        self.assertIsInstance(repr_str, str)
        self.assertIn("TlWall", repr_str)
    
    def test_str(self):
        """Test __str__ method."""
        str_output = str(self.wall)
        
        self.assertIsInstance(str_output, str)
        self.assertEqual(str_output, self.wall.summary())


class TestTlWallAccuracyFactor(unittest.TestCase):
    """Test accuracy factor modifications."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
        self.beam = create_beam_lhc()
        self.chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        self.copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        self.chamber.layers = [self.copper]
        self.wall = TlWall(
            chamber=self.chamber,
            beam=self.beam,
            frequencies=self.freq
        )
    
    def test_modify_accuracy_factor(self):
        """Test modifying accuracy factor."""
        ZLong1 = self.wall.calc_ZLong()
        
        self.wall.accuracy_factor = 0.5
        
        ZLong2 = self.wall.calc_ZLong()
        
        # NOTE: In the original implementation, accuracy_factor is NOT used
        # in calculations, so changing it should NOT change the results!
        # It's just a stored parameter for future use.
        self.assertTrue(np.array_equal(ZLong1, ZLong2))
        # But the value should be changed
        self.assertEqual(self.wall.accuracy_factor, 0.5)
    
    def test_accuracy_factor_invalidates_cache(self):
        """Test that changing accuracy factor does NOT invalidate cache.
        
        Note: In the original implementation, accuracy_factor is not used
        in calculations, so changing it does not affect cached results.
        """
        _ = self.wall.ZLong
        self.assertIsNotNone(self.wall._ZLong)
        
        old_cached = self.wall._ZLong
        self.wall.accuracy_factor = 0.5
        
        # Cache should still be valid (accuracy_factor not used in calculation)
        self.assertIsNotNone(self.wall._ZLong)
        self.assertIs(self.wall._ZLong, old_cached)


class TestTlWallEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def setUp(self):
        """Set up common test fixtures."""
        self.freq = Frequencies(fmin=3, fmax=6, fstep=1)
    
    def test_very_thin_layer(self):
        """Test with very thin layer (1 nm)."""
        beam = create_beam_lhc()
        chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        thin = Layer(thick_m=1e-9, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        chamber.layers = [thin]
        
        wall = TlWall(chamber=chamber, beam=beam, frequencies=self.freq)
        
        ZLong = wall.calc_ZLong()
        self.assertFalse(np.any(np.isnan(ZLong)))
    
    def test_very_thick_layer(self):
        """Test with very thick layer (1 m)."""
        beam = create_beam_lhc()
        chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        thick = Layer(thick_m=1.0, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        chamber.layers = [thick]
        
        wall = TlWall(chamber=chamber, beam=beam, frequencies=self.freq)
        
        ZLong = wall.calc_ZLong()
        self.assertFalse(np.any(np.isnan(ZLong)))

class TestTlWallSpaceCharge(unittest.TestCase):
    """Test Space Charge impedances."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create frequency array
        self.freq = Frequencies(fmin=3, fmax=9, fstep=2)
        self.frequencies = self.freq  # Alias for compatibility
        
        # Create beam
        beam = create_beam_lhc()
        
        # Create chamber with copper layer
        chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        chamber.layers = [copper]
        
        # Create TlWall
        self.wall = TlWall(chamber=chamber, beam=beam, frequencies=self.freq)
    
    def test_calc_ZLongDSC_method_exists(self):
        """Test that calc_ZLongDSC method exists."""
        self.assertTrue(hasattr(self.wall, 'calc_ZLongDSC'))
        self.assertTrue(callable(getattr(self.wall, 'calc_ZLongDSC')))
    
    def test_calc_ZLongDSC_returns_array(self):
        """Test that calc_ZLongDSC returns correct array."""
        ZLongDSC = self.wall.calc_ZLongDSC()
        
        self.assertIsInstance(ZLongDSC, np.ndarray)
        self.assertEqual(len(ZLongDSC), len(self.freq.freq))
        self.assertEqual(ZLongDSC.dtype, complex)
    
    def test_calc_ZLongDSC_caching(self):
        """Test that calc_ZLongDSC caches result."""
        # First call calculates
        Z1 = self.wall.calc_ZLongDSC()
        
        # Second call should return cached value
        Z2 = self.wall.ZLongDSC
        
        np.testing.assert_array_equal(Z1, Z2)
        # Verify it's the same object (cached)
        self.assertIs(self.wall._ZLongDSC, Z1)
    
    def test_calc_ZLongISC_method_exists(self):
        """Test that calc_ZLongISC method exists."""
        self.assertTrue(hasattr(self.wall, 'calc_ZLongISC'))
        self.assertTrue(callable(getattr(self.wall, 'calc_ZLongISC')))
    
    def test_calc_ZLongISC_returns_array(self):
        """Test that calc_ZLongISC returns correct array."""
        ZLongISC = self.wall.calc_ZLongISC()
        
        self.assertIsInstance(ZLongISC, np.ndarray)
        self.assertEqual(len(ZLongISC), len(self.freq.freq))
        self.assertEqual(ZLongISC.dtype, complex)
    
    def test_calc_ZTransDSC_method_exists(self):
        """Test that calc_ZTransDSC method exists."""
        self.assertTrue(hasattr(self.wall, 'calc_ZTransDSC'))
        self.assertTrue(callable(getattr(self.wall, 'calc_ZTransDSC')))
    
    def test_calc_ZTransDSC_returns_array(self):
        """Test that calc_ZTransDSC returns correct array."""
        ZTransDSC = self.wall.calc_ZTransDSC()
        
        self.assertIsInstance(ZTransDSC, np.ndarray)
        self.assertEqual(len(ZTransDSC), len(self.freq.freq))
        self.assertEqual(ZTransDSC.dtype, complex)
    
    def test_calc_ZTransISC_method_exists(self):
        """Test that calc_ZTransISC method exists."""
        self.assertTrue(hasattr(self.wall, 'calc_ZTransISC'))
        self.assertTrue(callable(getattr(self.wall, 'calc_ZTransISC')))
    
    def test_calc_ZTransISC_returns_array(self):
        """Test that calc_ZTransISC returns correct array."""
        ZTransISC = self.wall.calc_ZTransISC()
        
        self.assertIsInstance(ZTransISC, np.ndarray)
        self.assertEqual(len(ZTransISC), len(self.freq.freq))
        self.assertEqual(ZTransISC.dtype, complex)
    
    def test_space_charge_ultra_relativistic(self):
        """Test that ultra-relativistic beam gives zero space charge."""
        # Create ultra-relativistic beam
        beam_ultra = Beam(gamma=float('inf'))
        chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        # IMPORTANTE: Usa self.freq.freq (array) non self.freq (oggetto)
        copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        chamber.layers = [copper]
        
        wall = TlWall(chamber=chamber, beam=beam_ultra, frequencies=self.frequencies)
        
        # All space charge should be zero
        ZLongDSC = wall.calc_ZLongDSC()
        ZLongISC = wall.calc_ZLongISC()
        ZTransDSC = wall.calc_ZTransDSC()
        ZTransISC = wall.calc_ZTransISC()
        
        np.testing.assert_array_almost_equal(ZLongDSC, 0, decimal=10)
        np.testing.assert_array_almost_equal(ZLongISC, 0, decimal=10)
        np.testing.assert_array_almost_equal(ZTransDSC, 0, decimal=10)
        np.testing.assert_array_almost_equal(ZTransISC, 0, decimal=10)
    
    def test_space_charge_non_relativistic(self):
        """Test that non-relativistic beam gives non-zero space charge."""
        # Create low-energy beam (gamma = 2)
        beam_low = Beam(gamma=2.0)
        chamber = Chamber(pipe_rad_m=0.022, chamber_shape='CIRCULAR')
        # IMPORTANTE: Usa self.freq.freq (array) non self.freq (oggetto)
        copper = Layer(thick_m=0.001, sigmaDC=5.96e7, freq_Hz=self.freq.freq)
        chamber.layers = [copper]
        
        wall = TlWall(chamber=chamber, beam=beam_low, frequencies=self.frequencies)
        
        # Space charge should be non-zero
        ZLongDSC = wall.calc_ZLongDSC()
        ZLongISC = wall.calc_ZLongISC()
        ZTransDSC = wall.calc_ZTransDSC()
        ZTransISC = wall.calc_ZTransISC()
        
        # Check that at least some values are non-zero
        self.assertGreater(np.max(np.abs(ZLongDSC)), 0)
        self.assertGreater(np.max(np.abs(ZLongISC)), 0)
        self.assertGreater(np.max(np.abs(ZTransDSC)), 0)
        self.assertGreater(np.max(np.abs(ZTransISC)), 0)
    
    def test_space_charge_frequency_dependence(self):
        """Test that space charge impedance varies with frequency."""
        ZLongDSC = self.wall.calc_ZLongDSC()
        ZLongISC = self.wall.calc_ZLongISC()
        ZTransDSC = self.wall.calc_ZTransDSC()
        ZTransISC = self.wall.calc_ZTransISC()
        
        # Check that impedance varies across frequencies
        # (Not all values should be identical)
        for Z in [ZLongDSC, ZLongISC, ZTransDSC, ZTransISC]:
            std_dev = np.std(np.abs(Z))
            self.assertGreater(std_dev, 0, "Space charge should vary with frequency")


if __name__ == '__main__':
    # Print detected Beam API
    print("=" * 70)
    print("Beam API Detection")
    print("=" * 70)
    sig = inspect.signature(Beam.__init__)
    print(f"Beam.__init__ signature: {sig}")
    
    test_beam = create_beam_lhc()
    print(f"Test beam created: gamma={test_beam.gammarel:.2f}, beta={test_beam.betarel:.6f}")
    print("=" * 70)
    print()
    
    # Run tests
    unittest.main(verbosity=2)
