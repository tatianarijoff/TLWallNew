"""
Test special configuration cases.

Tests edge cases like infinite thickness, test_config section, etc.
"""

import unittest
import tempfile
import os
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall.cfg_io import CfgIo, ConfigurationError


class TestSpecialCases(unittest.TestCase):
    """Test special configuration cases."""
    
    def test_infinite_thickness_layer(self):
        """Test layer with thick_m = inf."""
        config_text = """
[base_info]
component_name = test_infinite
chamber_shape = CIRCULAR
pipe_radius_m = 0.02425
pipe_len_m = 1.0
betax = 100.0
betay = 100.0

[layers_info]
nbr_layers = 2

[layer0]
type = CW
thick_m = 1e-3
muinf_Hz = 0
k_Hz = inf
sigmaDC = 1.67e6
epsr = 1.0
tau = 0.0
RQ = 0.0

[layer1]
type = CW
thick_m = inf
muinf_Hz = 500
k_Hz = 10000
sigmaDC = 1.0e6
epsr = 1.0
tau = 0.0
RQ = 0.0

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.01
gammarel = 10000
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            chamber = cfg.read_chamber()
            
            # Check layers
            self.assertEqual(len(chamber.layers), 3)  # 2 layers + boundary
            
            # Layer 0: finite thickness
            self.assertAlmostEqual(chamber.layers[0].thick_m, 1e-3, places=10)
            
            # Layer 1: infinite thickness
            self.assertTrue(chamber.layers[1].thick_m == float('inf'))
            
            print(f"✓ Layer 0 thickness: {chamber.layers[0].thick_m}")
            print(f"✓ Layer 1 thickness: {chamber.layers[1].thick_m} (infinite)")
        
        finally:
            os.unlink(temp_file)
    
    def test_frequency_file_section(self):
        """Test configuration with frequency_file section."""
        # Create frequency file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write("# Frequency [Hz]\n")
            f.write("1.0e3\n")
            f.write("1.0e4\n")
            f.write("1.0e5\n")
            freq_file = f.name
        
        config_text = f"""
[base_info]
component_name = test_freq_file
chamber_shape = CIRCULAR
pipe_radius_m = 0.022
pipe_len_m = 1.0
betax = 100.0
betay = 100.0

[frequency_file]
filename = {freq_file}
separator = whitespace
freq_col = 0
skip_rows = 1

[layers_info]
nbr_layers = 0

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.01
gammarel = 7460.52
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
            
            print(f"✓ Loaded {len(freq.freq)} frequencies from file")
        
        finally:
            os.unlink(freq_file)
            os.unlink(cfg_file)
    
    def test_test_config_section(self):
        """Test reading test_config section."""
        config_text = """
[base_info]
component_name = test_with_refs
chamber_shape = CIRCULAR
pipe_radius_m = 0.022
pipe_len_m = 1.0
betax = 100.0
betay = 100.0

[test_config]
ref_long_file = tests/ZlongW.dat
ref_long_skip_rows = 1
ref_trans_dip_file = tests/ZtransdipW.dat
ref_trans_dip_skip_rows = 1
ref_trans_quad_file = tests/ZtransquadW.dat
ref_trans_quad_skip_rows = 1

[layers_info]
nbr_layers = 0

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.01
gammarel = 7460.52

[frequency_info]
fmin = 1000
fmax = 1000000
fstep = 3
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            test_cfg = cfg.read_test_config()
            
            # Check test_config loaded
            self.assertIsNotNone(test_cfg)
            self.assertEqual(test_cfg['ref_long_file'], 'tests/ZlongW.dat')
            self.assertEqual(test_cfg['ref_long_skip_rows'], 1)
            self.assertEqual(test_cfg['ref_trans_dip_file'], 'tests/ZtransdipW.dat')
            self.assertEqual(test_cfg['ref_trans_dip_skip_rows'], 1)
            self.assertEqual(test_cfg['ref_trans_quad_file'], 'tests/ZtransquadW.dat')
            self.assertEqual(test_cfg['ref_trans_quad_skip_rows'], 1)
            
            print(f"✓ Test config loaded with {len(test_cfg)} entries")
        
        finally:
            os.unlink(temp_file)
    
    def test_complete_lhc_config(self):
        """Test complete LHC-style configuration."""
        # Create frequency file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write("# Frequency [Hz]\n")
            for i in range(10):
                f.write(f"{10**(3+i*0.5):.6e}\n")
            freq_file = f.name
        
        config_text = f"""
[base_info]
component_name = LHC_2layers_24p25mm_some_element
chamber_shape = CIRCULAR
pipe_radius_m = 0.02425
pipe_len_m = 1.0
betax = 100.0
betay = 100.0

[frequency_file]
filename = {freq_file}
separator = whitespace
freq_col = 0
skip_rows = 1

[test_config]
ref_long_file = tests/complete/newCV/ZlongWLHC2layers24p25mm_some_element.dat
ref_long_skip_rows = 1
ref_trans_dip_file = tests/complete/newCV/ZtransdipWLHC2layers24p25mm_some_element.dat
ref_trans_dip_skip_rows = 1
ref_trans_quad_file = tests/complete/newCV/ZtransquadWLHC2layers24p25mm_some_element.dat
ref_trans_quad_skip_rows = 1

[layers_info]
nbr_layers = 2

[layer0]
type = CW
thick_m = 1e-3
muinf_Hz = 0
k_Hz = inf
sigmaDC = 1.670000e+06
epsr = 1.000000e+00
tau = 0.000000e+00
RQ = 0.00

[layer1]
type = CW
thick_m = inf
muinf_Hz = 500
k_Hz = 10000
sigmaDC = 1.000000e+06
epsr = 1.000000e+00
tau = 0.000000e+00
RQ = 0.00

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.01
gammarel = 10000
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cfg', delete=False) as f:
            f.write(config_text)
            cfg_file = f.name
        
        try:
            cfg = CfgIo(cfg_file)
            
            # Read all components
            chamber = cfg.read_chamber()
            beam = cfg.read_beam()
            freq = cfg.read_freq()
            test_cfg = cfg.read_test_config()
            
            # Verify chamber
            self.assertEqual(chamber.component_name, 'LHC_2layers_24p25mm_some_element')
            self.assertEqual(chamber.chamber_shape, 'CIRCULAR')
            self.assertAlmostEqual(chamber.pipe_rad_m, 0.02425, places=5)
            self.assertEqual(len(chamber.layers), 3)  # 2 layers + boundary
            
            # Verify layers
            self.assertAlmostEqual(chamber.layers[0].thick_m, 1e-3, places=10)
            self.assertTrue(chamber.layers[1].thick_m == float('inf'))
            
            # Verify beam
            self.assertAlmostEqual(beam.gammarel, 10000, places=2)
            self.assertAlmostEqual(beam.test_beam_shift, 0.01, places=10)
            
            # Verify frequencies
            self.assertEqual(len(freq.freq), 10)
            
            # Verify test config
            self.assertIsNotNone(test_cfg)
            self.assertIn('ref_long_file', test_cfg)
            
            print(f"✓ Complete LHC config loaded successfully")
            print(f"  Chamber: {chamber.component_name}")
            print(f"  Layers: {len(chamber.layers)} (including boundary)")
            print(f"  Layer 0: {chamber.layers[0].thick_m*1000:.3f} mm")
            print(f"  Layer 1: infinite thickness")
            print(f"  Beam gamma: {beam.gammarel:.0f}")
            print(f"  Frequencies: {len(freq.freq)} points")
        
        finally:
            os.unlink(freq_file)
            os.unlink(cfg_file)


if __name__ == '__main__':
    unittest.main(verbosity=2)
