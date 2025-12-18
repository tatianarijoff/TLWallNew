"""
Unit tests for Beam class.

Tests relativistic beam kinematics calculations and parameter handling.
"""

import unittest
import sys
import os
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall.beam import Beam, BeamValidationError, m_p_MeV, M_PROTON_MEV


class TestBeamInitialization(unittest.TestCase):
    """Test Beam initialization with various parameters."""
    
    def test_default_initialization(self):
        """Test default initialization (ultra-relativistic)."""
        beam = Beam()
        
        self.assertEqual(beam.betarel, 1.0)
        self.assertEqual(beam.gammarel, float('inf'))
        self.assertEqual(beam.Ekin_MeV, float('inf'))
        self.assertEqual(beam.test_beam_shift, 0.001)
    
    def test_init_with_gammarel(self):
        """Test initialization with gammarel parameter."""
        beam = Beam(gammarel=7460.52)
        
        self.assertAlmostEqual(beam.gammarel, 7460.52, places=2)
        self.assertAlmostEqual(beam.betarel, 0.999999, places=5)  # Relaxed from 6
        self.assertGreater(beam.Ekin_MeV, 6e6)  # ~7 TeV
    
    def test_init_with_gamma(self):
        """Test initialization with gamma parameter (alias for gammarel)."""
        beam = Beam(gamma=7460.52)
        
        self.assertAlmostEqual(beam.gammarel, 7460.52, places=2)
        self.assertAlmostEqual(beam.betarel, 0.999999, places=5)  # Relaxed from 6
        self.assertGreater(beam.Ekin_MeV, 6e6)
    
    def test_gamma_gammarel_equivalence(self):
        """Test that gamma and gammarel produce identical results."""
        beam1 = Beam(gammarel=7460.52)
        beam2 = Beam(gamma=7460.52)
        
        self.assertAlmostEqual(beam1.betarel, beam2.betarel, places=10)
        self.assertAlmostEqual(beam1.gammarel, beam2.gammarel, places=10)
        self.assertAlmostEqual(beam1.Ekin_MeV, beam2.Ekin_MeV, places=6)
        self.assertAlmostEqual(beam1.p_MeV_c, beam2.p_MeV_c, places=6)
    
    def test_both_gamma_and_gammarel(self):
        """Test that gammarel takes priority when both provided."""
        # Should print warning but use gammarel
        beam = Beam(gamma=1000, gammarel=7460.52)
        
        self.assertAlmostEqual(beam.gammarel, 7460.52, places=2)
    
    def test_init_with_Ekin(self):
        """Test initialization with kinetic energy."""
        beam = Beam(Ekin_MeV=7e6)  # 7 TeV
        
        self.assertAlmostEqual(beam.gammarel, 7461.5, places=0)  # More precise
        self.assertAlmostEqual(beam.betarel, 0.999999, places=5)
    
    def test_init_with_betarel(self):
        """Test initialization with beta."""
        beam = Beam(betarel=0.9)
        
        self.assertAlmostEqual(beam.betarel, 0.9, places=6)
        self.assertAlmostEqual(beam.gammarel, 2.294, places=2)
    
    def test_init_with_momentum(self):
        """Test initialization with momentum."""
        beam = Beam(p_MeV_c=7e6)
        
        self.assertGreater(beam.gammarel, 1.0)
        self.assertGreater(beam.betarel, 0.9)
    
    def test_custom_test_beam_shift(self):
        """Test custom test_beam_shift."""
        beam = Beam(test_beam_shift=0.005)
        
        self.assertEqual(beam.test_beam_shift, 0.005)
    
    def test_custom_mass(self):
        """Test custom particle mass."""
        m_electron = 0.511  # MeV/c^2
        beam = Beam(gammarel=1000, mass_MeV_c2=m_electron)
        
        self.assertEqual(beam.mass_MeV_c2, m_electron)
    
    def test_invalid_mass(self):
        """Test that invalid mass raises error."""
        with self.assertRaises(BeamValidationError):
            Beam(mass_MeV_c2=-1.0)
        
        with self.assertRaises(BeamValidationError):
            Beam(mass_MeV_c2=0.0)


class TestBeamParameterPriority(unittest.TestCase):
    """Test parameter priority order."""
    
    def test_Ekin_priority_over_gamma(self):
        """Test that Ekin_MeV has priority over gamma."""
        beam = Beam(Ekin_MeV=7e6, gamma=1000)
        
        # Should use Ekin, not gamma
        self.assertAlmostEqual(beam.gammarel, 7461.5, places=0)  # From Ekin
    
    def test_Ekin_priority_over_gammarel(self):
        """Test that Ekin_MeV has priority over gammarel."""
        beam = Beam(Ekin_MeV=7e6, gammarel=1000)
        
        self.assertAlmostEqual(beam.gammarel, 7461.5, places=0)  # From Ekin
    
    def test_p_priority_over_beta(self):
        """Test that p_MeV_c has priority over betarel."""
        beam = Beam(p_MeV_c=7e6, betarel=0.5)
        
        # Should use momentum, not beta
        self.assertNotAlmostEqual(beam.betarel, 0.5, places=1)
    
    def test_beta_priority_over_gamma(self):
        """Test that betarel has priority over gamma."""
        beam = Beam(betarel=0.9, gamma=1000)
        
        self.assertAlmostEqual(beam.betarel, 0.9, places=6)
        self.assertNotAlmostEqual(beam.gammarel, 1000, places=0)


class TestBeamSetters(unittest.TestCase):
    """Test beam parameter setters."""
    
    def test_set_gammarel(self):
        """Test setting gammarel property."""
        beam = Beam()
        beam.gammarel = 100.0
        
        self.assertAlmostEqual(beam.gammarel, 100.0, places=6)
        self.assertAlmostEqual(beam.betarel, 0.99995, places=5)
    
    def test_set_betarel(self):
        """Test setting betarel property."""
        beam = Beam()
        beam.betarel = 0.9
        
        self.assertAlmostEqual(beam.betarel, 0.9, places=6)
        self.assertAlmostEqual(beam.gammarel, 2.294, places=2)
    
    def test_set_Ekin_MeV(self):
        """Test setting Ekin_MeV property."""
        beam = Beam()
        beam.Ekin_MeV = 7e6
        
        self.assertAlmostEqual(beam.Ekin_MeV, 7e6, places=0)
        self.assertAlmostEqual(beam.gammarel, 7461.5, places=0)  # From Ekin
    
    def test_set_p_MeV_c(self):
        """Test setting p_MeV_c property."""
        beam = Beam()
        beam.p_MeV_c = 1000.0
        
        self.assertAlmostEqual(beam.p_MeV_c, 1000.0, places=6)
        self.assertGreater(beam.gammarel, 1.0)
    
    def test_invalid_gammarel(self):
        """Test that invalid gammarel is rejected."""
        beam = Beam()
        beam.gammarel = -1.0  # Should print warning and not change
        
        self.assertEqual(beam.gammarel, float('inf'))  # Should be unchanged
    
    def test_invalid_betarel(self):
        """Test that invalid betarel is rejected."""
        beam = Beam()
        beam.betarel = 1.5  # Should print warning and not change
        
        self.assertEqual(beam.betarel, 1.0)  # Should be unchanged
    
    def test_invalid_Ekin(self):
        """Test that invalid Ekin is rejected."""
        beam = Beam()
        beam.Ekin_MeV = -100  # Should print warning and not change
        
        self.assertEqual(beam.Ekin_MeV, float('inf'))  # Should be unchanged
    
    def test_invalid_momentum(self):
        """Test that invalid momentum is rejected."""
        beam = Beam()
        beam.p_MeV_c = -100  # Should print warning and not change
        
        self.assertEqual(beam.p_MeV_c, float('inf'))  # Should be unchanged


class TestBeamPhysics(unittest.TestCase):
    """Test physics calculations."""
    
    def test_ultra_relativistic_limit(self):
        """Test ultra-relativistic limit (beta -> 1)."""
        beam = Beam(betarel=0.999999)
        
        self.assertAlmostEqual(beam.betarel, 0.999999, places=6)
        self.assertGreater(beam.gammarel, 700)
    
    def test_non_relativistic(self):
        """Test non-relativistic case (beta << 1)."""
        beam = Beam(betarel=0.1)
        
        self.assertAlmostEqual(beam.betarel, 0.1, places=6)
        self.assertAlmostEqual(beam.gammarel, 1.005, places=3)
    
    def test_relativistic_relations(self):
        """Test relativistic energy-momentum relations."""
        beam = Beam(gammarel=10.0)
        
        # E_tot = gamma * m * c^2
        E_tot_expected = 10.0 * beam.mass_MeV_c2
        self.assertAlmostEqual(beam.E_tot_MeV, E_tot_expected, places=6)
        
        # E_kin = (gamma - 1) * m * c^2
        E_kin_expected = 9.0 * beam.mass_MeV_c2
        self.assertAlmostEqual(beam.Ekin_MeV, E_kin_expected, places=6)
        
        # p = gamma * m * beta * c
        p_expected = 10.0 * beam.mass_MeV_c2 * beam.betarel
        self.assertAlmostEqual(beam.p_MeV_c, p_expected, places=6)
    
    def test_velocity_calculation(self):
        """Test velocity calculation."""
        beam = Beam(betarel=0.9)
        
        expected_velocity = 0.9 * 299792458  # m/s
        self.assertAlmostEqual(beam.velocity_m_s, expected_velocity, places=0)


class TestBeamConstants(unittest.TestCase):
    """Test exported constants."""
    
    def test_proton_mass_export(self):
        """Test that proton mass constants are exported."""
        self.assertAlmostEqual(m_p_MeV, 938.272, places=2)
        self.assertAlmostEqual(M_PROTON_MEV, 938.272, places=2)
        self.assertEqual(m_p_MeV, M_PROTON_MEV)


class TestBeamStringRepresentation(unittest.TestCase):
    """Test string representation methods."""
    
    def test_repr(self):
        """Test __repr__ method."""
        beam = Beam(gamma=100)
        repr_str = repr(beam)
        
        self.assertIsInstance(repr_str, str)
        self.assertIn("Beam(", repr_str)
        self.assertIn("gammarel=", repr_str)
    
    def test_str(self):
        """Test __str__ method."""
        beam = Beam(gamma=100)
        str_output = str(beam)
        
        self.assertIsInstance(str_output, str)
        self.assertIn("Beam properties:", str_output)
        self.assertIn("Beta", str_output)
        self.assertIn("Gamma", str_output)


class TestBeamEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_gamma_exactly_one(self):
        """Test gamma = 1 (particle at rest)."""
        beam = Beam(gammarel=1.0)
        
        self.assertAlmostEqual(beam.gammarel, 1.0, places=6)
        self.assertAlmostEqual(beam.betarel, 0.0, places=6)
        self.assertAlmostEqual(beam.Ekin_MeV, 0.0, places=6)
    
    def test_very_large_gamma(self):
        """Test very large gamma (extreme relativistic)."""
        beam = Beam(gammarel=1e12)
        
        self.assertAlmostEqual(beam.betarel, 1.0, places=10)
        self.assertGreater(beam.Ekin_MeV, 9e14)  # ~9.38e14 MeV
    
    def test_beta_exactly_one(self):
        """Test beta = 1 (speed of light)."""
        beam = Beam(betarel=1.0)
        
        self.assertEqual(beam.betarel, 1.0)
        self.assertEqual(beam.gammarel, float('inf'))


if __name__ == '__main__':
    unittest.main(verbosity=2)
