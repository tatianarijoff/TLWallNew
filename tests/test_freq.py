"""
Unit tests for the Frequencies class.

These tests verify:
1. Correct frequency array generation
2. Parameter consistency
3. Error handling and validation
4. Edge cases
5. Array properties
"""

# Add parent directory to path to allow imports when running standalone
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
import warnings
from pytlwall import Frequencies


class TestFrequenciesGeneration(unittest.TestCase):
    """Test frequency array generation from exponents."""
    
    def test_default_generation(self):
        """Test default frequency generation."""
        freq = Frequencies()
        
        # Check default parameters
        self.assertEqual(freq.fmin, 0)
        self.assertEqual(freq.fmax, 8)
        self.assertEqual(freq.fstep, 2)
        
        # Array should not be empty
        self.assertGreater(len(freq.freq), 0)
        
        # All frequencies should be positive
        self.assertTrue(np.all(freq.freq > 0))
        
        # Frequencies should be sorted
        self.assertTrue(np.all(np.diff(freq.freq) > 0))
    
    def test_custom_exponents(self):
        """Test frequency generation with custom exponents."""
        freq = Frequencies(fmin=3, fmax=6, fstep=1)
        
        self.assertEqual(freq.fmin, 3)
        self.assertEqual(freq.fmax, 6)
        self.assertEqual(freq.fstep, 1)
        
        # Check range (approximately)
        self.assertGreater(freq.freq[0], 10**2.5)  # Above 10^3 minimum
        self.assertLess(freq.freq[-1], 10**6.5)    # Below 10^7 maximum
    
    def test_frequency_coverage(self):
        """Test that frequency array covers expected range."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        
        # Minimum should be close to 10^0 = 1 Hz
        self.assertAlmostEqual(freq.freq[0], 1.0, delta=1.0)
        
        # Maximum should be close to 10^6 = 1 MHz
        self.assertAlmostEqual(freq.freq[-1], 1e6, delta=1e5)
    
    def test_step_resolution(self):
        """Test that larger fstep produces more points."""
        freq_coarse = Frequencies(fmin=0, fmax=6, fstep=1)   # Small step = FEWER points
        freq_medium = Frequencies(fmin=0, fmax=6, fstep=2)   # Medium step = medium points
        freq_fine = Frequencies(fmin=0, fmax=6, fstep=3)     # Large step = MORE points
        
        # In the current algorithm: LARGER fstep → MORE points (counterintuitive!)
        self.assertLess(len(freq_coarse), len(freq_medium))
        self.assertLess(len(freq_medium), len(freq_fine))
    
    def test_logarithmic_spacing(self):
        """Test that frequencies are logarithmically spaced."""
        freq = Frequencies(fmin=0, fmax=3, fstep=1)
        
        # Check that ratio between consecutive points is roughly constant
        ratios = freq.freq[1:] / freq.freq[:-1]
        
        # Ratios should be relatively consistent (within 20% variation)
        mean_ratio = np.mean(ratios)
        std_ratio = np.std(ratios)
        self.assertLess(std_ratio / mean_ratio, 0.2)


class TestFrequenciesExplicitList(unittest.TestCase):
    """Test frequency creation from explicit list."""
    
    def test_explicit_list(self):
        """Test using explicit frequency list."""
        freq_list = [1e3, 1e4, 1e5, 1e6]
        freq = Frequencies(freq_list=freq_list)
        
        # Should match input
        np.testing.assert_array_equal(freq.freq, np.array(freq_list))
        
        # fmin and fmax should reflect the list
        self.assertEqual(freq.fmin, 1e3)
        self.assertEqual(freq.fmax, 1e6)
        
        # fstep should be 0 for explicit list
        self.assertEqual(freq.fstep, 0.0)
    
    def test_unsorted_list_gets_sorted(self):
        """Test that unsorted frequency list is automatically sorted."""
        freq_list = [1e6, 1e3, 1e5, 1e4]
        freq = Frequencies(freq_list=freq_list)
        
        # Should be sorted
        expected = np.sort(np.array(freq_list))
        np.testing.assert_array_equal(freq.freq, expected)
    
    def test_single_frequency(self):
        """Test with single frequency."""
        freq_list = [1e6]
        freq = Frequencies(freq_list=freq_list)
        
        self.assertEqual(len(freq.freq), 1)
        self.assertEqual(freq.freq[0], 1e6)
        self.assertEqual(freq.fmin, 1e6)
        self.assertEqual(freq.fmax, 1e6)
    
    def test_empty_list_uses_defaults(self):
        """Test that empty list falls back to exponent generation."""
        freq = Frequencies(freq_list=[])
        
        # Should use default exponents
        self.assertEqual(freq.fmin, 0)
        self.assertEqual(freq.fmax, 8)
        self.assertGreater(len(freq.freq), 0)
    
    def test_explicit_list_ignores_exponents(self):
        """Test that providing freq_list ignores exponent parameters."""
        freq_list = [100, 200, 300]
        freq = Frequencies(freq_list=freq_list, fmin=5, fmax=10, fstep=1)
        
        # Should use freq_list and ignore exponents
        np.testing.assert_array_equal(freq.freq, np.array([100, 200, 300]))


class TestFrequenciesValidation(unittest.TestCase):
    """Test error handling and validation."""
    
    def test_negative_frequencies_rejected(self):
        """Test that negative frequencies raise error."""
        with self.assertRaises(ValueError):
            Frequencies(freq_list=[-100, 1e6, 1e9])
    
    def test_zero_frequency_rejected(self):
        """Test that zero frequency raises error."""
        with self.assertRaises(ValueError):
            Frequencies(freq_list=[0, 1e6, 1e9])
    
    def test_invalid_fmin_raises_error(self):
        """Test that invalid fmin type raises error."""
        freq = Frequencies()
        
        with self.assertRaises(ValueError):
            freq.fmin = "not a number"
    
    def test_invalid_fmax_raises_error(self):
        """Test that invalid fmax type raises error."""
        freq = Frequencies()
        
        with self.assertRaises(ValueError):
            freq.fmax = "not a number"
    
    def test_invalid_fstep_raises_error(self):
        """Test that invalid fstep type raises error."""
        freq = Frequencies()
        
        with self.assertRaises(ValueError):
            freq.fstep = "not a number"
    
    def test_fmin_greater_than_fmax_warning(self):
        """Test that fmin > fmax triggers warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            freq = Frequencies(fmin=8, fmax=3, fstep=2)
            self.assertTrue(len(w) > 0)
            self.assertTrue(issubclass(w[0].category, UserWarning))
    
    def test_negative_fstep_warning(self):
        """Test that negative fstep triggers warning."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            freq = Frequencies(fmin=0, fmax=6, fstep=-1)
            self.assertTrue(len(w) > 0)
            self.assertTrue(issubclass(w[0].category, UserWarning))


class TestFrequenciesProperties(unittest.TestCase):
    """Test property getters and setters."""
    
    def test_freq_is_readonly(self):
        """Test that freq property cannot be set directly."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        
        # Should not have setter (will raise AttributeError)
        with self.assertRaises(AttributeError):
            freq.freq = np.array([1, 2, 3])
    
    def test_fmin_setter(self):
        """Test fmin setter."""
        freq = Frequencies()
        old_fmin = freq.fmin
        
        freq.fmin = 2.0
        self.assertEqual(freq.fmin, 2.0)
        self.assertNotEqual(freq.fmin, old_fmin)
    
    def test_fmax_setter(self):
        """Test fmax setter."""
        freq = Frequencies()
        old_fmax = freq.fmax
        
        freq.fmax = 10.0
        self.assertEqual(freq.fmax, 10.0)
        self.assertNotEqual(freq.fmax, old_fmax)
    
    def test_fstep_setter(self):
        """Test fstep setter."""
        freq = Frequencies()
        old_fstep = freq.fstep
        
        freq.fstep = 1.0
        self.assertEqual(freq.fstep, 1.0)
        self.assertNotEqual(freq.fstep, old_fstep)
    
    def test_setter_with_warning(self):
        """Test that setter with invalid value triggers warning."""
        freq = Frequencies(fmin=3, fmax=6, fstep=2)
        
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            freq.fmax = 1.0  # Less than fmin
            self.assertTrue(len(w) > 0)


class TestFrequenciesUpdate(unittest.TestCase):
    """Test dynamic frequency array updates."""
    
    def test_update_from_exponents(self):
        """Test update_from_exponents method."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        old_len = len(freq.freq)
        old_range = (freq.freq[0], freq.freq[-1])
        
        # Update to new range
        freq.update_from_exponents(fmin=3, fmax=9, fstep=1)
        
        # Parameters should be updated
        self.assertEqual(freq.fmin, 3)
        self.assertEqual(freq.fmax, 9)
        self.assertEqual(freq.fstep, 1)
        
        # Array should be different
        self.assertNotEqual(len(freq.freq), old_len)
        self.assertNotEqual((freq.freq[0], freq.freq[-1]), old_range)
    
    def test_update_maintains_consistency(self):
        """Test that update maintains array consistency."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        
        freq.update_from_exponents(fmin=2, fmax=8, fstep=1)
        
        # All frequencies should still be positive and sorted
        self.assertTrue(np.all(freq.freq > 0))
        self.assertTrue(np.all(np.diff(freq.freq) > 0))


class TestFrequenciesEdgeCases(unittest.TestCase):
    """Test edge cases and special values."""
    
    def test_very_small_range(self):
        """Test with very small frequency range."""
        # When fmin = fmax, the range is just one decade
        freq = Frequencies(fmin=5, fmax=6, fstep=1)
        
        # Should have at least one frequency
        self.assertGreater(len(freq.freq), 0)
    
    def test_very_large_range(self):
        """Test with very large frequency range."""
        freq = Frequencies(fmin=0, fmax=15, fstep=3)
        
        # Should generate array without errors
        self.assertGreater(len(freq.freq), 0)
        self.assertTrue(np.all(np.isfinite(freq.freq)))
    
    def test_fractional_exponents(self):
        """Test with fractional exponents."""
        freq = Frequencies(fmin=1.5, fmax=4.5, fstep=0.5)
        
        self.assertEqual(freq.fmin, 1.5)
        self.assertEqual(freq.fmax, 4.5)
        self.assertEqual(freq.fstep, 0.5)
        self.assertGreater(len(freq.freq), 0)
    
    def test_large_step(self):
        """Test with very large step (dense array)."""
        # Large fstep actually produces MORE points in current implementation
        freq_large = Frequencies(fmin=0, fmax=10, fstep=5)
        freq_small = Frequencies(fmin=0, fmax=10, fstep=1)
        
        # Large step produces MORE points than small step
        self.assertGreater(len(freq_large.freq), len(freq_small.freq))
        
        # Both should cover similar range
        self.assertLess(freq_large.freq[0], 100)
        self.assertGreater(freq_large.freq[-1], 1e9)


class TestFrequenciesMethods(unittest.TestCase):
    """Test utility methods."""
    
    def test_len(self):
        """Test __len__ method."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        
        self.assertEqual(len(freq), len(freq.freq))
        self.assertIsInstance(len(freq), int)
        self.assertGreater(len(freq), 0)
    
    def test_repr(self):
        """Test __repr__ method."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        repr_str = repr(freq)
        
        # Should contain key information
        self.assertIn("Frequencies", repr_str)
        self.assertIn("n=", repr_str)
        self.assertIn("fmin", repr_str)
        self.assertIn("fmax", repr_str)
        self.assertIn("fstep", repr_str)
    
    def test_repr_explicit_list(self):
        """Test __repr__ for explicit frequency list."""
        freq = Frequencies(freq_list=[1e3, 1e6, 1e9])
        repr_str = repr(freq)
        
        # Should indicate explicit list
        self.assertIn("Frequencies", repr_str)
        self.assertIn("explicit list", repr_str)
    
    def test_str(self):
        """Test __str__ method."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        str_repr = str(freq)
        
        # Should be readable
        self.assertIsInstance(str_repr, str)
        self.assertGreater(len(str_repr), 0)


class TestFrequenciesArrayProperties(unittest.TestCase):
    """Test properties of the generated frequency array."""
    
    def test_all_positive(self):
        """Test that all frequencies are positive."""
        freq = Frequencies(fmin=-2, fmax=6, fstep=2)
        
        self.assertTrue(np.all(freq.freq > 0))
    
    def test_strictly_increasing(self):
        """Test that frequencies are strictly increasing."""
        freq = Frequencies(fmin=0, fmax=8, fstep=2)
        
        # All differences should be positive
        self.assertTrue(np.all(np.diff(freq.freq) > 0))
    
    def test_no_duplicates(self):
        """Test that there are no duplicate frequencies."""
        freq = Frequencies(fmin=0, fmax=8, fstep=1)
        
        unique_freqs = np.unique(freq.freq)
        self.assertEqual(len(unique_freqs), len(freq.freq))
    
    def test_finite_values(self):
        """Test that all frequencies are finite."""
        freq = Frequencies(fmin=0, fmax=10, fstep=2)
        
        self.assertTrue(np.all(np.isfinite(freq.freq)))
    
    def test_reasonable_values(self):
        """Test that frequencies are in reasonable range."""
        freq = Frequencies(fmin=0, fmax=10, fstep=2)
        
        # Should be between 1 Hz and 100 GHz
        self.assertGreaterEqual(np.min(freq.freq), 0.1)
        self.assertLessEqual(np.max(freq.freq), 1e11)


class TestFrequenciesNumericalStability(unittest.TestCase):
    """Test numerical stability and precision."""
    
    def test_round_trip_exponents(self):
        """Test that updating with same exponents gives same result."""
        freq1 = Frequencies(fmin=3, fmax=7, fstep=2)
        original_freq = freq1.freq.copy()
        
        # Update with same parameters
        freq1.update_from_exponents(fmin=3, fmax=7, fstep=2)
        
        # Should be identical
        np.testing.assert_array_equal(freq1.freq, original_freq)
    
    def test_precision_maintained(self):
        """Test that frequency values maintain precision."""
        freq = Frequencies(fmin=6, fmax=6, fstep=1)
        
        # Frequencies around 1 MHz should have good precision
        for f in freq.freq:
            if 9e5 < f < 1.1e6:
                # Should have at least 6 significant figures
                relative_error = abs(f - round(f)) / f
                self.assertLess(relative_error, 1e-6)


class TestFrequenciesComparison(unittest.TestCase):
    """Test comparison between different frequency configurations."""
    
    def test_different_steps_same_range(self):
        """Test that different steps cover same range."""
        freq1 = Frequencies(fmin=3, fmax=6, fstep=1)
        freq2 = Frequencies(fmin=3, fmax=6, fstep=2)
        freq3 = Frequencies(fmin=3, fmax=6, fstep=3)
        
        # All should cover approximately same range
        for freq in [freq1, freq2, freq3]:
            self.assertGreater(freq.freq[0], 1e2)
            self.assertLess(freq.freq[0], 1e4)
            self.assertGreater(freq.freq[-1], 1e5)
            self.assertLess(freq.freq[-1], 1e7)
    
    def test_points_per_decade_consistent(self):
        """Test that points per decade follows expected pattern."""
        freq = Frequencies(fmin=0, fmax=6, fstep=2)
        
        # Count points in each decade
        for decade in range(0, 6):
            low = 10**decade
            high = 10**(decade + 1)
            count = np.sum((freq.freq >= low) & (freq.freq < high))
            
            # Should have reasonable number of points
            self.assertGreater(count, 0)
            self.assertLess(count, 1000)  # Not excessive


class TestFrequenciesIntegration(unittest.TestCase):
    """Test integration scenarios with typical use cases."""
    
    def test_lhc_range(self):
        """Test typical LHC frequency range."""
        freq = Frequencies(fmin=0, fmax=10, fstep=2)
        
        # Should cover 1 Hz to 10 GHz
        self.assertLess(freq.freq[0], 10)
        self.assertGreater(freq.freq[-1], 1e9)
        
        # Should have reasonable number of points
        self.assertGreater(len(freq), 100)
        self.assertLess(len(freq), 100000)
    
    def test_resonance_frequencies(self):
        """Test specific resonance frequency analysis."""
        # Typical cavity resonances
        resonances = [
            400.79e6,   # LHC 400 MHz system
            800e6,      # Harmonic
            1200e6,     # Harmonic
        ]
        
        freq = Frequencies(freq_list=resonances)
        
        self.assertEqual(len(freq), 3)
        self.assertTrue(np.allclose(freq.freq, resonances))


if __name__ == "__main__":
    print("\n" + "="*10 + " Testing frequencies module " + "="*10)
    unittest.main(verbosity=2)
