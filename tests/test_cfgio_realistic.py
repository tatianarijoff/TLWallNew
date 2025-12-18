"""
Realistic unit tests for CfgIo class based on actual .cfg files.

Tests configuration I/O using real configuration files from pytlwall.
"""

import unittest
import os
from pathlib import Path
import numpy as np

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall.cfg_io import CfgIo, ConfigurationError
import pytlwall


class TestCfgIoRealistic(unittest.TestCase):
    """Test CfgIo with realistic .cfg files."""
    
    @classmethod
    def setUpClass(cls):
        """Set up paths to test configuration files."""
        base_dir = os.path.dirname(__file__)
        cls.input_dir = os.path.join(base_dir, "input")
        
        # Configuration files
        cls.cfg_one_layer = os.path.join(cls.input_dir, "one_layer.cfg")
        cls.cfg_test001 = os.path.join(cls.input_dir, "test001.cfg")
        cls.cfg_two_layers = os.path.join(cls.input_dir, "two_layers.cfg")
        cls.cfg_rectangular = os.path.join(cls.input_dir, "rectangular_chamber.cfg")
        cls.cfg_test_round = os.path.join(cls.input_dir, "test_round.cfg")
        cls.cfg_test_rect = os.path.join(cls.input_dir, "test_rect.cfg")
        
        # Frequency files (plain data, NOT cfg)
        cls.freq_input_txt = os.path.join(cls.input_dir, "freq_input.txt")
        cls.freq_input2_txt = os.path.join(cls.input_dir, "freq_input2.txt")
        cls.freq_input3_dat = os.path.join(cls.input_dir, "freq_input3.dat")
    
    # =========================================================================
    # Test: one_layer.cfg
    # =========================================================================
    
    def test_onelayer_chamber_base_info(self):
        """Test reading [base_info] from one_layer.cfg."""
        cfg = CfgIo()
        chamber = cfg.read_chamber(self.cfg_one_layer)
        
        # Base info
        self.assertEqual("mytest", chamber.component_name)
        self.assertAlmostEqual(2.0e-2, chamber.pipe_hor_m, places=10)
        self.assertAlmostEqual(1.0e-2, chamber.pipe_ver_m, places=10)
        self.assertAlmostEqual(1.0, chamber.pipe_len_m, places=10)
        self.assertAlmostEqual(1.0, chamber.betax, places=10)
        self.assertAlmostEqual(1.0, chamber.betay, places=10)
        
        # Chamber shape
        self.assertEqual("ELLIPTICAL", chamber.chamber_shape)
    
    def test_onelayer_layers_and_boundary(self):
        """Test reading layers from one_layer.cfg."""
        cfg = CfgIo()
        chamber = cfg.read_chamber(self.cfg_one_layer)
        
        # At least one layer + boundary
        self.assertGreaterEqual(len(chamber.layers), 1)
        
        layer0 = chamber.layers[0]
        
        # Layer properties
        self.assertEqual("CW", layer0.layer_type)
        self.assertAlmostEqual(0.001, layer0.thick_m, places=10)
        
        # Electromagnetic properties
        self.assertAlmostEqual(0.0, layer0.muinf_Hz, places=10)
        self.assertAlmostEqual(5.8e7, layer0.sigmaDC, places=5)
        self.assertAlmostEqual(1.0, layer0.epsr, places=10)
        self.assertAlmostEqual(0.0, layer0.tau, places=10)
        self.assertAlmostEqual(4.0e-6, layer0.RQ, places=10)
    
    def test_frequency_info_onelayer(self):
        """Test reading [frequency_info] from one_layer.cfg."""
        cfg = CfgIo()
        freq = cfg.read_freq(self.cfg_one_layer)
        
        # Check fstep
        self.assertEqual(2, freq.fstep)
        
        # Check range if attributes exist
        if hasattr(freq, 'fmin'):
            self.assertAlmostEqual(0.0, freq.fmin, places=10)
        if hasattr(freq, 'fmax'):
            self.assertAlmostEqual(12.0, freq.fmax, places=10)
    
    def test_beam_info_onelayer(self):
        """Test reading [beam_info] from one_layer.cfg."""
        cfg = CfgIo()
        beam = cfg.read_beam(self.cfg_one_layer)
        
        self.assertAlmostEqual(0.01, beam.test_beam_shift, places=10)
        self.assertAlmostEqual(1.0e5, beam.gammarel, places=2)
    
    def test_pytlwall_one_layer_global(self):
        """Test building complete TlWall from one_layer.cfg."""
        cfg = CfgIo(self.cfg_one_layer)
        wall = cfg.read_pytlwall()
        
        # Beam checks
        self.assertAlmostEqual(0.01, wall.beam.test_beam_shift, places=10)
        self.assertAlmostEqual(1.0e5, wall.beam.gammarel, places=2)
        
        # Chamber checks
        self.assertEqual("mytest", wall.chamber.component_name)
        self.assertAlmostEqual(2.0e-2, wall.chamber.pipe_hor_m, places=10)
        self.assertAlmostEqual(1.0e-2, wall.chamber.pipe_ver_m, places=10)
        
        # Layers
        self.assertGreaterEqual(len(wall.chamber.layers), 1)
        self.assertEqual("ELLIPTICAL", wall.chamber.chamber_shape)
        self.assertEqual("CW", wall.chamber.layers[0].layer_type)
    
    def test_pytlwall_one_layer_calculate(self):
        """Test calculating impedance from one_layer.cfg (replaces calc_wall)."""
        cfg = CfgIo(self.cfg_one_layer)
        wall = cfg.read_pytlwall()
        
        # Calculate impedances directly on TlWall object
        ZLong = wall.ZLong
        
        self.assertIsNotNone(ZLong)
        self.assertGreater(len(ZLong), 0)
    
    # =========================================================================
    # Test: test001.cfg
    # =========================================================================
    
    def test_pytlwall_test001_cfg(self):
        """Test building TlWall from test001.cfg."""
        cfg = CfgIo(self.cfg_test001)
        wall = cfg.read_pytlwall()
        
        # Frequencies must be increasing
        self.assertGreater(wall.f.size, 0)
        self.assertTrue(np.all(wall.f[1:] > wall.f[:-1]))
        
        # Beam must exist
        self.assertIsNotNone(wall.beam)
        self.assertTrue(hasattr(wall.beam, 'gammarel'))
        self.assertGreater(wall.beam.gammarel, 1.0)
        
        # Chamber must exist
        self.assertIsNotNone(wall.chamber)
        self.assertGreater(wall.chamber.pipe_rad_m, 0.0)
    
    # =========================================================================
    # Test: two_layers.cfg
    # =========================================================================
    
    @unittest.skipUnless(
        os.path.exists(os.path.join(os.path.dirname(__file__), "input", "two_layers.cfg")),
        "Requires two_layers.cfg"
    )
    def test_two_layers_chamber(self):
        """Test reading chamber with multiple layers."""
        cfg = CfgIo()
        chamber = cfg.read_chamber(self.cfg_two_layers)
        
        # At least 2 layers + boundary
        self.assertGreaterEqual(len(chamber.layers), 2)
        
        # Check layer types
        self.assertIsInstance(chamber.layers[0].layer_type, str)
        self.assertIsInstance(chamber.layers[1].layer_type, str)
    
    # =========================================================================
    # Test: rectangular_chamber.cfg
    # =========================================================================
    
    @unittest.skipUnless(
        os.path.exists(
            os.path.join(os.path.dirname(__file__), "input", "rectangular_chamber.cfg")
        ),
        "Requires rectangular_chamber.cfg"
    )
    def test_rectangular_chamber_shape(self):
        """Test reading RECTANGULAR chamber."""
        cfg = CfgIo()
        chamber = cfg.read_chamber(self.cfg_rectangular)
        
        # Chamber shape
        self.assertEqual("RECTANGULAR", chamber.chamber_shape)
        
        # Geometry
        self.assertGreater(chamber.pipe_hor_m, 0.0)
        self.assertGreater(chamber.pipe_ver_m, 0.0)
    
    # =========================================================================
    # Test: test_round.cfg (with : delimiters)
    # =========================================================================
    
    @unittest.skipUnless(
        os.path.exists(os.path.join(os.path.dirname(__file__), "input", "test_round.cfg")),
        "Requires test_round.cfg"
    )
    def test_round_chamber_with_colon_delimiter(self):
        """Test reading config with : as delimiter."""
        cfg = CfgIo()
        chamber = cfg.read_chamber(self.cfg_test_round)
        
        # Should handle : delimiter
        self.assertEqual("CIRCULAR", chamber.chamber_shape)
        self.assertAlmostEqual(18.4e-3, chamber.pipe_rad_m, places=6)
        
        # Check layers
        self.assertGreaterEqual(len(chamber.layers), 2)
    
    @unittest.skipUnless(
        os.path.exists(os.path.join(os.path.dirname(__file__), "input", "test_round.cfg")),
        "Requires test_round.cfg"
    )
    def test_round_beam_with_colon_delimiter(self):
        """Test reading beam with : delimiter."""
        cfg = CfgIo()
        beam = cfg.read_beam(self.cfg_test_round)
        
        # Should parse betarel correctly
        self.assertAlmostEqual(1.0, beam.betarel, places=6)
        self.assertAlmostEqual(0.003, beam.test_beam_shift, places=10)
    
    # =========================================================================
    # Test: test_rect.cfg (CW boundary)
    # =========================================================================
    
    @unittest.skipUnless(
        os.path.exists(os.path.join(os.path.dirname(__file__), "input", "test_rect.cfg")),
        "Requires test_rect.cfg"
    )
    def test_rect_chamber_with_cw_boundary(self):
        """Test reading RECTANGULAR with CW boundary."""
        cfg = CfgIo()
        chamber = cfg.read_chamber(self.cfg_test_rect)
        
        self.assertEqual("RECTANGULAR", chamber.chamber_shape)
        self.assertAlmostEqual(3.15e-2, chamber.pipe_hor_m, places=6)
        self.assertAlmostEqual(1.15e-2, chamber.pipe_ver_m, places=6)
        
        # Boundary layer should be CW type
        boundary = chamber.layers[-1]
        self.assertEqual("CW", boundary.layer_type)
        self.assertTrue(boundary.boundary)
    
    # =========================================================================
    # Test: Frequency files (plain data - should raise error)
    # =========================================================================
    
    def test_frequency_from_freq_input_txt_raises(self):
        """freq_input.txt is plain data, not cfg - should raise error."""
        cfg = CfgIo()
        with self.assertRaises(Exception):
            # This should fail because it's not a valid config file
            cfg.read_freq(self.freq_input_txt)
    
    def test_frequency_from_freq_input2_txt_raises(self):
        """freq_input2.txt is plain data, not cfg - should raise error."""
        cfg = CfgIo()
        with self.assertRaises(Exception):
            cfg.read_freq(self.freq_input2_txt)
    
    def test_frequency_from_freq_input3_dat_raises(self):
        """freq_input3.dat is plain data, not cfg - should raise error."""
        cfg = CfgIo()
        with self.assertRaises(Exception):
            cfg.read_freq(self.freq_input3_dat)
    
    # =========================================================================
    # Test: Frequency file section (if implemented)
    # =========================================================================
    
    def test_frequency_file_section(self):
        """Test reading frequencies from [frequency_file] section."""
        import tempfile
        
        # Create test frequency file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Frequency [Hz]\n")
            f.write("1.0e3\n")
            f.write("1.0e4\n")
            f.write("1.0e5\n")
            freq_file = f.name
        
        # Create config with frequency_file section
        config_text = f"""
[frequency_file]
filename = {freq_file}
separator = whitespace
freq_col = 0
skip_rows = 1
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(config_text)
            cfg_file = f.name
        
        try:
            cfg = CfgIo(cfg_file)
            freq = cfg.read_freq()
            
            # Check frequencies loaded
            self.assertEqual(len(freq.freq), 3)
            self.assertAlmostEqual(freq.freq[0], 1.0e3, places=2)
            self.assertAlmostEqual(freq.freq[1], 1.0e4, places=2)
            self.assertAlmostEqual(freq.freq[2], 1.0e5, places=2)
        finally:
            os.unlink(freq_file)
            os.unlink(cfg_file)
    
    # =========================================================================
    # Test: Edge cases
    # =========================================================================
    
    def test_missing_config_file(self):
        """Test error handling for missing file."""
        with self.assertRaises(ConfigurationError):
            cfg = CfgIo('nonexistent_file.cfg')
    
    def test_missing_section(self):
        """Test handling of missing sections."""
        cfg = CfgIo()
        
        chamber = cfg.read_chamber()
        self.assertIsNone(chamber)
        
        beam = cfg.read_beam()
        self.assertIsNone(beam)
    
    def test_thick_M_uppercase_support(self):
        """Test support for thick_M (uppercase M)."""
        # one_layer.cfg uses thick_M
        cfg = CfgIo()
        chamber = cfg.read_chamber(self.cfg_one_layer)
        
        # Should read thickness correctly despite uppercase M
        self.assertAlmostEqual(0.001, chamber.layers[0].thick_m, places=10)


if __name__ == '__main__':
    unittest.main(verbosity=2)
