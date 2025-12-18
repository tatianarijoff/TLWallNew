"""
Unit tests for CfgIo class.

Tests configuration I/O for pytlwall package.
"""

import unittest
import tempfile
import os
from pathlib import Path
import configparser

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall.cfg_io import CfgIo, ConfigurationError
from pytlwall.chamber import Chamber
from pytlwall.beam import Beam
from pytlwall.frequencies import Frequencies
from pytlwall.layer import Layer


class TestCfgIoInitialization(unittest.TestCase):
    """Test CfgIo initialization."""
    
    def test_default_initialization(self):
        """Test default initialization without file."""
        cfg = CfgIo()
        
        self.assertIsInstance(cfg.config, configparser.ConfigParser)
        self.assertEqual(len(cfg.list_output), 0)
        self.assertEqual(len(cfg.file_output), 0)
        self.assertEqual(len(cfg.img_output), 0)
    
    def test_initialization_with_file(self):
        """Test initialization with config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[base_info]\n")
            f.write("component_name = test\n")
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            self.assertTrue(cfg.config.has_section('base_info'))
            self.assertEqual(cfg.config.get('base_info', 'component_name'), 'test')
        finally:
            os.unlink(temp_file)
    
    def test_initialization_with_nonexistent_file(self):
        """Test initialization with nonexistent file raises error."""
        with self.assertRaises(ConfigurationError):
            cfg = CfgIo('nonexistent_file.ini')


class TestCfgIoReadCfg(unittest.TestCase):
    """Test read_cfg method."""
    
    def test_read_existing_file(self):
        """Test reading existing config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write("[section1]\n")
            f.write("key1 = value1\n")
            temp_file = f.name
        
        try:
            cfg = CfgIo()
            cfg.read_cfg(temp_file)
            self.assertTrue(cfg.config.has_section('section1'))
            self.assertEqual(cfg.config.get('section1', 'key1'), 'value1')
        finally:
            os.unlink(temp_file)
    
    def test_read_nonexistent_file(self):
        """Test reading nonexistent file raises error."""
        cfg = CfgIo()
        with self.assertRaises(ConfigurationError):
            cfg.read_cfg('nonexistent.ini')


class TestCfgIoChamberIO(unittest.TestCase):
    """Test chamber reading and writing."""
    
    def test_read_circular_chamber(self):
        """Test reading circular chamber configuration."""
        config_text = """
[base_info]
pipe_len_m = 10.0
pipe_radius_m = 0.022
chamber_shape = CIRCULAR
component_name = test_chamber
betax = 100.0
betay = 50.0

[layers_info]
nbr_layers = 1

[layer0]
type = CW
thick_m = 0.001
muinf_Hz = 1.0
epsr = 1.0
sigmaDC = 5.96e7
k_Hz = inf
tau = 0.0
RQ = 1.0

[boundary]
type = PEC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            chamber = cfg.read_chamber()
            
            self.assertIsNotNone(chamber)
            self.assertEqual(chamber.chamber_shape, 'CIRCULAR')
            self.assertEqual(chamber.pipe_rad_m, 0.022)
            self.assertEqual(chamber.pipe_len_m, 10.0)
            self.assertEqual(chamber.betax, 100.0)
            self.assertEqual(chamber.component_name, 'test_chamber')
            self.assertEqual(len(chamber.layers), 2)  # 1 layer + boundary
        finally:
            os.unlink(temp_file)
    
    def test_read_elliptical_chamber(self):
        """Test reading elliptical chamber configuration."""
        config_text = """
[base_info]
pipe_len_m = 10.0
pipe_hor_m = 0.030
pipe_ver_m = 0.020
chamber_shape = ELLIPTICAL
betax = 100.0
betay = 50.0

[layers_info]
nbr_layers = 0

[boundary]
type = PEC
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            chamber = cfg.read_chamber()
            
            self.assertIsNotNone(chamber)
            self.assertEqual(chamber.chamber_shape, 'ELLIPTICAL')
            self.assertEqual(chamber.pipe_hor_m, 0.030)
            self.assertEqual(chamber.pipe_ver_m, 0.020)
        finally:
            os.unlink(temp_file)
    
    def test_read_chamber_no_section(self):
        """Test reading chamber returns None if section missing."""
        cfg = CfgIo()
        chamber = cfg.read_chamber()
        self.assertIsNone(chamber)
    
    def test_save_and_read_chamber(self):
        """Test saving and reading chamber configuration."""
        from pytlwall.chamber import Chamber
        from pytlwall.layer import Layer
        
        # Create chamber
        layers = [
            Layer(layer_type='CW', thick_m=0.001, sigmaDC=5.96e7, boundary=False),
            Layer(layer_type='PEC', boundary=True)
        ]
        chamber = Chamber(
            pipe_len_m=10.0,
            pipe_rad_m=0.022,
            chamber_shape='CIRCULAR',
            betax=100.0,
            betay=50.0,
            layers=layers,
            component_name='test'
        )
        
        # Save configuration
        cfg = CfgIo()
        cfg.save_chamber(chamber)
        cfg.save_layer(layers)
        
        # Verify sections exist
        self.assertTrue(cfg.config.has_section('base_info'))
        self.assertTrue(cfg.config.has_section('layers_info'))
        
        # Verify values
        self.assertEqual(cfg.config.get('base_info', 'component_name'), 'test')
        self.assertEqual(cfg.config.getfloat('base_info', 'pipe_len_m'), 10.0)


class TestCfgIoBeamIO(unittest.TestCase):
    """Test beam reading and writing."""
    
    def test_read_beam_with_gamma(self):
        """Test reading beam with gammarel."""
        config_text = """
[beam_info]
test_beam_shift = 0.001
gammarel = 7460.52
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            beam = cfg.read_beam()
            
            self.assertIsNotNone(beam)
            self.assertAlmostEqual(beam.gammarel, 7460.52, places=2)
            self.assertEqual(beam.test_beam_shift, 0.001)
        finally:
            os.unlink(temp_file)
    
    def test_read_beam_with_beta(self):
        """Test reading beam with betarel."""
        config_text = """
[beam_info]
test_beam_shift = 0.001
betarel = 0.9
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            beam = cfg.read_beam()
            
            self.assertIsNotNone(beam)
            self.assertAlmostEqual(beam.betarel, 0.9, places=6)
        finally:
            os.unlink(temp_file)
    
    def test_read_beam_with_mass(self):
        """Test reading beam with custom mass."""
        config_text = """
[beam_info]
test_beam_shift = 0.001
gammarel = 1000.0
mass_MeV_c2 = 0.511
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            beam = cfg.read_beam()
            
            self.assertIsNotNone(beam)
            self.assertEqual(beam.mass_MeV_c2, 0.511)
        finally:
            os.unlink(temp_file)
    
    def test_read_beam_no_section(self):
        """Test reading beam returns None if section missing."""
        cfg = CfgIo()
        beam = cfg.read_beam()
        self.assertIsNone(beam)
    
    def test_save_beam(self):
        """Test saving beam configuration."""
        from pytlwall.beam import Beam
        
        beam = Beam(gamma=7460.52, test_beam_shift=0.002)
        
        cfg = CfgIo()
        cfg.save_beam(beam)
        
        self.assertTrue(cfg.config.has_section('beam_info'))
        self.assertAlmostEqual(
            cfg.config.getfloat('beam_info', 'gammarel'),
            7460.52,
            places=2
        )


class TestCfgIoFrequencyIO(unittest.TestCase):
    """Test frequency reading and writing."""
    
    def test_read_frequency_range(self):
        """Test reading frequency range."""
        config_text = """
[frequency_info]
fmin = 3
fmax = 9
fstep = 3
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            freq = cfg.read_freq()
            
            self.assertIsNotNone(freq)
            self.assertEqual(freq.fmin, 3)
            self.assertEqual(freq.fmax, 9)
            self.assertEqual(freq.fstep, 3)
        finally:
            os.unlink(temp_file)
    
    def test_read_frequency_default(self):
        """Test reading default frequencies."""
        cfg = CfgIo()
        freq = cfg.read_freq()
        
        self.assertIsNotNone(freq)
        # Should return default Frequencies object
    
    def test_save_frequency(self):
        """Test saving frequency configuration."""
        from pytlwall.frequencies import Frequencies
        
        freq = Frequencies(fmin=3, fmax=9, fstep=3)
        
        cfg = CfgIo()
        cfg.save_freq(freq)
        
        self.assertTrue(cfg.config.has_section('frequency_info'))
        self.assertEqual(cfg.config.getint('frequency_info', 'fmin'), 3)


class TestCfgIoOutputConfiguration(unittest.TestCase):
    """Test output configuration reading."""
    
    def test_read_output_list(self):
        """Test reading output impedance list."""
        config_text = """
[output]
ZLong = True
ZTrans = False
ZDipX = True
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            cfg.read_output()
            
            self.assertIn('ZLong', cfg.list_output)
            self.assertNotIn('ZTrans', cfg.list_output)
            self.assertIn('ZDipX', cfg.list_output)
        finally:
            os.unlink(temp_file)
    
    def test_save_calc(self):
        """Test saving calculation configuration."""
        list_calc = {
            'ZLong': True,
            'ZTrans': False,
            'ZDipX': True
        }
        
        cfg = CfgIo()
        cfg.save_calc(list_calc)
        
        self.assertTrue(cfg.config.has_section('output'))
        self.assertEqual(cfg.config.getboolean('output', 'ZLong'), True)
        self.assertEqual(cfg.config.getboolean('output', 'ZTrans'), False)


class TestCfgIoHighLevel(unittest.TestCase):
    """Test high-level operations."""
    
    def test_read_pytlwall_complete(self):
        """Test reading complete pytlwall configuration."""
        config_text = """
[base_info]
pipe_len_m = 10.0
pipe_radius_m = 0.022
chamber_shape = CIRCULAR
betax = 100.0
betay = 50.0

[layers_info]
nbr_layers = 0

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.001
gammarel = 7460.52

[frequency_info]
fmin = 3
fmax = 9
fstep = 3
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            wall = cfg.read_pytlwall()
            
            self.assertIsNotNone(wall)
            self.assertAlmostEqual(wall.beam.gammarel, 7460.52, places=2)
            self.assertEqual(wall.chamber.chamber_shape, 'CIRCULAR')
        finally:
            os.unlink(temp_file)
    
    def test_write_cfg(self):
        """Test writing configuration to file."""
        cfg = CfgIo()
        cfg.config.add_section('test')
        cfg.config.set('test', 'key', 'value')
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            temp_file = f.name
        
        try:
            cfg.write_cfg(temp_file)
            
            # Read back
            cfg2 = CfgIo(temp_file)
            self.assertTrue(cfg2.config.has_section('test'))
            self.assertEqual(cfg2.config.get('test', 'key'), 'value')
        finally:
            os.unlink(temp_file)
    
    def test_read_pytlwall_and_calculate(self):
        """Test reading config and performing calculation (replaces calc_wall)."""
        config_text = """
[base_info]
pipe_len_m = 10.0
pipe_radius_m = 0.022
chamber_shape = CIRCULAR
betax = 100.0
betay = 50.0

[layers_info]
nbr_layers = 1

[layer0]
type = CW
thick_m = 0.001
muinf_Hz = 1.0
epsr = 1.0
sigmaDC = 5.96e7
k_Hz = inf
tau = 0.0
RQ = 1.0

[boundary]
type = PEC

[beam_info]
test_beam_shift = 0.001
gammarel = 7460.52

[frequency_info]
fmin = 3
fmax = 6
fstep = 3
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ini', delete=False) as f:
            f.write(config_text)
            temp_file = f.name
        
        try:
            cfg = CfgIo(temp_file)
            wall = cfg.read_pytlwall()
            
            # Calculate impedances directly on TlWall object
            # (this is the new pattern replacing calc_wall)
            ZLong = wall.ZLong
            
            self.assertIsNotNone(ZLong)
            self.assertGreater(len(ZLong), 0)
        finally:
            os.unlink(temp_file)


class TestCfgIoStringRepresentation(unittest.TestCase):
    """Test string representation methods."""
    
    def test_repr(self):
        """Test __repr__ method."""
        cfg = CfgIo()
        cfg.config.add_section('test')
        
        repr_str = repr(cfg)
        self.assertIsInstance(repr_str, str)
        self.assertIn('CfgIo', repr_str)
        self.assertIn('test', repr_str)
    
    def test_str(self):
        """Test __str__ method."""
        cfg = CfgIo()
        cfg.config.add_section('test')
        
        str_output = str(cfg)
        self.assertIsInstance(str_output, str)
        self.assertIn('sections', str_output.lower())


if __name__ == '__main__':
    unittest.main(verbosity=2)
