"""
Unit tests for the Layer class.

These tests verify:
1. Layer initialization and properties
2. Material parameter validation
3. Frequency-dependent calculations
4. Surface impedance handling
5. Error handling
"""

# Add parent directory to path to allow imports when running standalone
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
import warnings
from pytlwall import Layer
from pytlwall.layer import LayerValidationError


class TestLayerInitialization(unittest.TestCase):
    """Test layer initialization scenarios."""
    
    def test_default_initialization(self):
        """Test default layer initialization."""
        layer = Layer()
        
        # Check default values
        self.assertEqual(layer.layer_type, "CW")
        self.assertEqual(layer.thick_m, 1e-2)
        self.assertEqual(layer.epsr, 1.0)
        self.assertEqual(layer.sigmaDC, 1.0e6)
        self.assertEqual(len(layer.freq_Hz), 0)
    
    def test_boundary_initialization(self):
        """Test boundary (vacuum) layer initialization."""
        layer = Layer(boundary=True)
        
        # Boundary should set type to 'V'
        self.assertEqual(layer.layer_type, "V")
    
    def test_custom_initialization(self):
        """Test initialization with custom parameters."""
        freq = np.logspace(3, 9, 100)
        layer = Layer(
            layer_type='CW',
            thick_m=0.001,
            sigmaDC=5.96e7,  # Copper
            epsr=1.0,
            RQ=1e-6,
            freq_Hz=freq
        )
        
        self.assertEqual(layer.layer_type, "CW")
        self.assertEqual(layer.thick_m, 0.001)
        self.assertEqual(layer.sigmaDC, 5.96e7)
        self.assertEqual(layer.RQ, 1e-6)
        self.assertEqual(len(layer.freq_Hz), 100)
    
    def test_initialization_with_frequencies(self):
        """Test initialization with frequency array."""
        freq = np.array([1e6, 1e7, 1e8])
        layer = Layer(freq_Hz=freq)
        
        np.testing.assert_array_equal(layer.freq_Hz, freq)


class TestLayerType(unittest.TestCase):
    """Test layer type property."""
    
    def test_valid_layer_types(self):
        """Test valid layer types."""
        for ltype in ['CW', 'V', 'PEC']:
            layer = Layer(layer_type=ltype)
            self.assertEqual(layer.layer_type, ltype)
    
    def test_case_insensitive(self):
        """Test that layer type is case insensitive."""
        for ltype in ['cw', 'Cw', 'CW']:
            layer = Layer(layer_type=ltype)
            self.assertEqual(layer.layer_type, 'CW')
    
    def test_invalid_layer_type(self):
        """Test that invalid layer type raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(layer_type='INVALID')
    
    def test_layer_type_setter(self):
        """Test layer type setter."""
        layer = Layer()
        layer.layer_type = 'PEC'
        self.assertEqual(layer.layer_type, 'PEC')
        
        with self.assertRaises(LayerValidationError):
            layer.layer_type = 'WRONG'


class TestLayerThickness(unittest.TestCase):
    """Test layer thickness property."""
    
    def test_positive_thickness(self):
        """Test valid positive thickness."""
        layer = Layer(thick_m=0.005)
        self.assertEqual(layer.thick_m, 0.005)
    
    def test_zero_thickness(self):
        """Test that zero thickness raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(thick_m=0.0)
    
    def test_negative_thickness(self):
        """Test that negative thickness raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(thick_m=-0.001)
    
    def test_thickness_setter(self):
        """Test thickness setter validation."""
        layer = Layer()
        layer.thick_m = 0.002
        self.assertEqual(layer.thick_m, 0.002)
        
        with self.assertRaises(LayerValidationError):
            layer.thick_m = -0.001


class TestLayerConductivity(unittest.TestCase):
    """Test electrical conductivity properties."""
    
    def test_positive_conductivity(self):
        """Test valid positive conductivity."""
        layer = Layer(sigmaDC=5.96e7)  # Copper
        self.assertEqual(layer.sigmaDC, 5.96e7)
    
    def test_zero_conductivity(self):
        """Test zero conductivity (insulator)."""
        layer = Layer(sigmaDC=0.0)
        self.assertEqual(layer.sigmaDC, 0.0)
    
    def test_negative_conductivity(self):
        """Test that negative conductivity raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(sigmaDC=-1000)
    
    def test_conductivity_range(self):
        """Test typical conductivity values."""
        # Copper
        copper = Layer(sigmaDC=5.96e7)
        self.assertAlmostEqual(copper.sigmaDC, 5.96e7)
        
        # Stainless steel
        steel = Layer(sigmaDC=1.45e6)
        self.assertAlmostEqual(steel.sigmaDC, 1.45e6)


class TestLayerPermittivity(unittest.TestCase):
    """Test permittivity properties."""
    
    def test_relative_permittivity(self):
        """Test relative permittivity."""
        layer = Layer(epsr=2.5)
        self.assertEqual(layer.epsr, 2.5)
    
    def test_absolute_permittivity(self):
        """Test absolute permittivity calculation."""
        layer = Layer(epsr=1.0)
        import scipy.constants as const
        expected = const.epsilon_0
        self.assertAlmostEqual(layer.eps, expected)
    
    def test_zero_permittivity(self):
        """Test that zero permittivity raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(epsr=0.0)
    
    def test_negative_permittivity(self):
        """Test that negative permittivity raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(epsr=-1.0)


class TestLayerRoughness(unittest.TestCase):
    """Test surface roughness property."""
    
    def test_zero_roughness(self):
        """Test smooth surface (zero roughness)."""
        layer = Layer(RQ=0.0)
        self.assertEqual(layer.RQ, 0.0)
    
    def test_positive_roughness(self):
        """Test positive roughness values."""
        layer = Layer(RQ=1e-6)  # 1 micron
        self.assertEqual(layer.RQ, 1e-6)
    
    def test_negative_roughness(self):
        """Test that negative roughness raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(RQ=-1e-6)


class TestFrequencyArray(unittest.TestCase):
    """Test frequency array handling."""
    
    def test_set_frequency_array(self):
        """Test setting frequency array."""
        freq = np.logspace(3, 9, 100)
        layer = Layer(freq_Hz=freq)
        
        np.testing.assert_array_equal(layer.freq_Hz, freq)
    
    def test_empty_frequency_array(self):
        """Test empty frequency array."""
        layer = Layer()
        self.assertEqual(len(layer.freq_Hz), 0)
    
    def test_negative_frequencies(self):
        """Test that negative frequencies raise error."""
        with self.assertRaises(LayerValidationError):
            Layer(freq_Hz=[-1e6, 1e6, 1e9])
    
    def test_zero_frequency(self):
        """Test that zero frequency raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(freq_Hz=[0, 1e6, 1e9])
    
    def test_frequency_setter(self):
        """Test frequency array setter."""
        layer = Layer()
        freq = np.array([1e6, 1e7, 1e8])
        layer.freq_Hz = freq
        
        np.testing.assert_array_equal(layer.freq_Hz, freq)


class TestCalculatedProperties(unittest.TestCase):
    """Test frequency-dependent calculated properties."""
    
    def setUp(self):
        """Set up test layer with frequencies."""
        self.freq = np.logspace(6, 9, 10)
        self.layer = Layer(
            sigmaDC=5.96e7,  # Copper
            epsr=1.0,
            freq_Hz=self.freq
        )
    
    def test_sigmaAC_shape(self):
        """Test that AC conductivity has correct shape."""
        sigmaAC = self.layer.sigmaAC
        self.assertEqual(len(sigmaAC), len(self.freq))
    
    def test_sigmaAC_is_complex(self):
        """Test that AC conductivity is complex."""
        sigmaAC = self.layer.sigmaAC
        self.assertTrue(np.iscomplexobj(sigmaAC))
    
    def test_sigmaPM_shape(self):
        """Test that effective conductivity has correct shape."""
        sigmaPM = self.layer.sigmaPM
        self.assertEqual(len(sigmaPM), len(self.freq))
    
    def test_sigmaPM_positive(self):
        """Test that effective conductivity magnitude is positive."""
        sigmaPM = self.layer.sigmaPM
        self.assertTrue(np.all(sigmaPM > 0))
    
    def test_mur_shape(self):
        """Test relative permeability shape."""
        mur = self.layer.mur
        self.assertEqual(len(mur), len(self.freq))
    
    def test_mu_shape(self):
        """Test absolute permeability shape."""
        mu = self.layer.mu
        self.assertEqual(len(mu), len(self.freq))
    
    def test_delta_shape(self):
        """Test skin depth shape."""
        delta = self.layer.delta
        self.assertEqual(len(delta), len(self.freq))
    
    def test_delta_positive_real(self):
        """Test that skin depth has positive real part."""
        delta = self.layer.delta
        self.assertTrue(np.all(delta.real > 0))
    
    def test_deltaM_shape(self):
        """Test modified skin depth shape."""
        deltaM = self.layer.deltaM
        self.assertEqual(len(deltaM), len(self.freq))
    
    def test_RS_shape(self):
        """Test surface resistance shape."""
        RS = self.layer.RS
        self.assertEqual(len(RS), len(self.freq))
    
    def test_RS_positive(self):
        """Test that surface resistance is positive."""
        RS = self.layer.RS
        self.assertTrue(np.all(RS.real > 0))
    
    def test_kprop_shape(self):
        """Test propagation constant shape."""
        kprop = self.layer.kprop
        self.assertEqual(len(kprop), len(self.freq))


class TestSkinDepth(unittest.TestCase):
    """Test skin depth calculations."""
    
    def test_copper_skin_depth_at_1MHz(self):
        """Test copper skin depth at 1 MHz."""
        freq = np.array([1e6])
        layer = Layer(sigmaDC=5.96e7, epsr=1.0, freq_Hz=freq)
        
        delta = layer.delta
        
        # Approximate skin depth at 1 MHz for copper: ~66 microns
        self.assertAlmostEqual(abs(delta[0]), 66e-6, delta=10e-6)
    
    def test_skin_depth_frequency_dependence(self):
        """Test that skin depth decreases with frequency."""
        freq = np.array([1e6, 1e7, 1e8, 1e9])
        layer = Layer(sigmaDC=5.96e7, epsr=1.0, freq_Hz=freq)
        
        delta = abs(layer.delta)
        
        # Skin depth should decrease with frequency
        self.assertGreater(delta[0], delta[1])
        self.assertGreater(delta[1], delta[2])
        self.assertGreater(delta[2], delta[3])


class TestSurfaceImpedance(unittest.TestCase):
    """Test surface impedance handling."""
    
    def test_default_surface_impedance(self):
        """Test default surface impedance calculation."""
        freq = np.logspace(6, 9, 10)
        layer = Layer(sigmaDC=5.96e7, freq_Hz=freq)
        
        KZ = layer.KZ
        
        self.assertEqual(len(KZ), len(freq))
        self.assertTrue(np.iscomplexobj(KZ))
    
    def test_set_surface_impedance_directly(self):
        """Test setting surface impedance directly."""
        freq = np.array([1e6, 1e7, 1e8])
        layer = Layer(freq_Hz=freq)
        
        KZ_custom = np.array([1+1j, 2+2j, 3+3j])
        layer.KZ = KZ_custom
        
        np.testing.assert_array_equal(layer.KZ, KZ_custom)
    
    def test_surface_impedance_must_be_complex(self):
        """Test that surface impedance must be complex."""
        layer = Layer(freq_Hz=np.array([1e6, 1e7]))
        
        with self.assertRaises(LayerValidationError):
            layer.KZ = np.array([1.0, 2.0])  # Real values
    
    def test_set_surf_imped_with_interpolation(self):
        """Test set_surf_imped with interpolation."""
        layer_freq = np.logspace(6, 9, 100)
        layer = Layer(freq_Hz=layer_freq)
        
        # Provide impedance at fewer frequencies
        data_freq = np.array([1e6, 1e8, 1e9])
        data_KZ = np.array([1+1j, 2+2j, 3+3j])
        
        layer.set_surf_imped(data_freq, data_KZ)
        
        # Check that KZ is set and has correct length
        self.assertEqual(len(layer.KZ), len(layer_freq))
        self.assertTrue(np.iscomplexobj(layer.KZ))


class TestRoughnessEffects(unittest.TestCase):
    """Test surface roughness effects."""
    
    def test_roughness_increases_resistance(self):
        """Test that roughness increases surface resistance."""
        freq = np.logspace(6, 9, 10)
        
        # Smooth surface
        layer_smooth = Layer(sigmaDC=5.96e7, RQ=0.0, freq_Hz=freq)
        
        # Rough surface
        layer_rough = Layer(sigmaDC=5.96e7, RQ=1e-6, freq_Hz=freq)
        
        # Rough surface should have higher resistance
        self.assertTrue(np.all(layer_rough.RS >= layer_smooth.RS))
    
    def test_roughness_effect_frequency_dependent(self):
        """Test that roughness effect increases with frequency."""
        freq = np.array([1e6, 1e9])
        layer = Layer(sigmaDC=5.96e7, RQ=1e-6, freq_Hz=freq)
        
        RS = layer.RS
        
        # At higher frequencies, roughness effect should be more pronounced
        self.assertGreater(RS[1], RS[0])


class TestMaterialExamples(unittest.TestCase):
    """Test with realistic material parameters."""
    
    def test_copper_layer(self):
        """Test copper layer with typical parameters."""
        freq = np.logspace(3, 9, 100)
        copper = Layer(
            layer_type='CW',
            thick_m=0.001,  # 1 mm
            sigmaDC=5.96e7,  # S/m
            epsr=1.0,
            freq_Hz=freq
        )
        
        self.assertEqual(copper.layer_type, 'CW')
        self.assertAlmostEqual(copper.sigmaDC, 5.96e7)
        self.assertEqual(len(copper.freq_Hz), 100)
    
    def test_stainless_steel_layer(self):
        """Test stainless steel layer."""
        freq = np.logspace(3, 9, 100)
        steel = Layer(
            layer_type='CW',
            thick_m=0.002,  # 2 mm
            sigmaDC=1.45e6,  # S/m
            epsr=1.0,
            RQ=1e-6,  # 1 micron roughness
            freq_Hz=freq
        )
        
        self.assertEqual(steel.layer_type, 'CW')
        self.assertAlmostEqual(steel.sigmaDC, 1.45e6)
        self.assertEqual(steel.RQ, 1e-6)
    
    def test_vacuum_layer(self):
        """Test vacuum boundary layer."""
        vacuum = Layer(boundary=True)
        
        self.assertEqual(vacuum.layer_type, 'V')
    
    def test_perfect_conductor(self):
        """Test perfect electrical conductor."""
        pec = Layer(layer_type='PEC')
        
        self.assertEqual(pec.layer_type, 'PEC')


class TestLayerValidation(unittest.TestCase):
    """Test comprehensive validation."""
    
    def test_invalid_type_value(self):
        """Test that invalid types raise appropriate errors."""
        with self.assertRaises(LayerValidationError):
            Layer(thick_m="not a number")
    
    def test_invalid_conductivity_value(self):
        """Test that invalid conductivity raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(sigmaDC="invalid")
    
    def test_invalid_frequency_array(self):
        """Test that invalid frequency array raises error."""
        with self.assertRaises(LayerValidationError):
            Layer(freq_Hz="not an array")


class TestLayerRepresentation(unittest.TestCase):
    """Test string representations."""
    
    def test_repr(self):
        """Test __repr__ method."""
        layer = Layer(sigmaDC=5.96e7, thick_m=0.001)
        repr_str = repr(layer)
        
        self.assertIn("Layer", repr_str)
        self.assertIn("type", repr_str)
        self.assertIn("thick", repr_str)
    
    def test_str(self):
        """Test __str__ method."""
        layer = Layer(sigmaDC=5.96e7)
        str_repr = str(layer)
        
        self.assertIsInstance(str_repr, str)
        self.assertGreater(len(str_repr), 0)


class TestLayerConsistency(unittest.TestCase):
    """Test that properties remain consistent."""
    
    def test_property_update_consistency(self):
        """Test that updating one property doesn't break others."""
        freq = np.logspace(6, 9, 10)
        layer = Layer(sigmaDC=5.96e7, freq_Hz=freq)
        
        # Get initial values
        initial_delta = layer.delta.copy()
        
        # Change conductivity
        layer.sigmaDC = 1e7
        
        # Delta should change
        new_delta = layer.delta
        self.assertFalse(np.allclose(new_delta, initial_delta))
    
    def test_frequency_change_updates_calculations(self):
        """Test that changing frequencies updates calculations."""
        layer = Layer(sigmaDC=5.96e7, freq_Hz=np.array([1e6, 1e7]))
        
        delta1 = layer.delta.copy()
        self.assertEqual(len(delta1), 2)
        
        # Change to different number of frequencies
        layer.freq_Hz = np.array([1e9])
        
        delta2 = layer.delta
        
        # Should have different length now
        self.assertEqual(len(delta2), 1)
        self.assertNotEqual(len(delta1), len(delta2))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and extreme values."""
    
    def test_very_high_conductivity(self):
        """Test with very high conductivity (superconductor-like)."""
        freq = np.array([1e6])
        layer = Layer(sigmaDC=1e10, freq_Hz=freq)
        
        # Should not raise errors
        delta = layer.delta
        self.assertTrue(np.isfinite(delta[0]))
    
    def test_very_low_conductivity(self):
        """Test with very low conductivity (insulator-like)."""
        freq = np.array([1e6])
        layer = Layer(sigmaDC=1e-10, freq_Hz=freq)
        
        # Should not raise errors
        delta = layer.delta
        self.assertTrue(np.isfinite(delta[0]))
    
    def test_single_frequency(self):
        """Test with single frequency point."""
        layer = Layer(sigmaDC=5.96e7, freq_Hz=np.array([1e6]))
        
        self.assertEqual(len(layer.delta), 1)
        self.assertEqual(len(layer.RS), 1)
    
    def test_many_frequencies(self):
        """Test with many frequency points."""
        freq = np.logspace(3, 12, 10000)
        layer = Layer(sigmaDC=5.96e7, freq_Hz=freq)
        
        self.assertEqual(len(layer.delta), 10000)


if __name__ == "__main__":
    print("\n" + "="*10 + " Testing layer module " + "="*10)
    unittest.main(verbosity=2)
