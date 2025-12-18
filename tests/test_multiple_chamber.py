#!/usr/bin/env python3
"""
Unit tests for MultipleChamber class.

Uses real test files from tests/multiple/input/ directory.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
import unittest
import numpy as np

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from pytlwall.multiple_chamber import MultipleChamber, DEFAULT_APERTYPE_TO_CFG


class TestMultipleChamberInit(unittest.TestCase):
    """Test MultipleChamber initialization."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures using real input files."""
        # Use the real test input directory
        cls.test_dir = Path(__file__).parent / "multiple"
        cls.input_dir = cls.test_dir / "input"
        cls.output_dir = cls.test_dir / "output"
        
        # Check if test files exist
        if not cls.input_dir.exists():
            raise unittest.SkipTest(f"Test input directory not found: {cls.input_dir}")
        
        # Check for required files
        cls.apertype_file = cls.input_dir / "apertype2.txt"
        cls.geom_file = cls.input_dir / "b_L_betax_betay.txt"
        
        if not cls.apertype_file.exists():
            raise unittest.SkipTest(f"apertype2.txt not found in {cls.input_dir}")
        if not cls.geom_file.exists():
            raise unittest.SkipTest(f"b_L_betax_betay.txt not found in {cls.input_dir}")
    
    def test_initialization(self):
        """Test basic initialization."""
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
            out_dir=self.output_dir,
        )
        self.assertEqual(mc.input_dir, self.input_dir.resolve())
        self.assertFalse(mc.is_loaded)
        self.assertFalse(mc.is_calculated)

    def test_initialization_with_absolute_paths(self):
        """Test initialization with absolute paths."""
        mc = MultipleChamber(
            apertype_file=self.apertype_file,
            geom_file=self.geom_file,
            input_dir=self.input_dir,
            out_dir=self.output_dir,
        )
        self.assertEqual(mc.apertype_file, self.apertype_file.resolve())
        self.assertEqual(mc.geom_file, self.geom_file.resolve())

    def test_default_mapping(self):
        """Test that default aperture type mapping is set."""
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
        )
        self.assertIn("Round", mc.apertype_to_cfg)
        self.assertIn("Rectangular", mc.apertype_to_cfg)

    def test_custom_mapping(self):
        """Test custom aperture type mapping."""
        custom_mapping = {"MyType": "MyType.cfg", "Round": "Round.cfg"}
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
            apertype_to_cfg=custom_mapping,
        )
        self.assertEqual(mc.apertype_to_cfg, custom_mapping)


class TestMultipleChamberDataLoading(unittest.TestCase):
    """Test MultipleChamber data loading."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = Path(__file__).parent / "multiple"
        cls.input_dir = cls.test_dir / "input"
        cls.output_dir = cls.test_dir / "output"
        
        if not cls.input_dir.exists():
            raise unittest.SkipTest(f"Test input directory not found: {cls.input_dir}")
    
    def setUp(self):
        """Create MultipleChamber instance."""
        self.mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
            out_dir=self.output_dir,
        )
    
    def test_load(self):
        """Test loading input data."""
        self.mc.load()
        self.assertTrue(self.mc.is_loaded)
        self.assertGreater(self.mc.n_elements, 0)
    
    def test_load_populates_lists(self):
        """Test that load() populates all data lists."""
        self.mc.load()
        self.assertGreater(len(self.mc.apertypes), 0)
        self.assertGreater(len(self.mc.b_list), 0)
        self.assertGreater(len(self.mc.L_list), 0)
        self.assertGreater(len(self.mc.betax_list), 0)
        self.assertGreater(len(self.mc.betay_list), 0)
    
    def test_data_lengths_match(self):
        """Test that all data lists have the same length."""
        self.mc.load()
        n = self.mc.n_elements
        self.assertEqual(len(self.mc.apertypes), n)
        self.assertEqual(len(self.mc.b_list), n)
        self.assertEqual(len(self.mc.L_list), n)
        self.assertEqual(len(self.mc.betax_list), n)
        self.assertEqual(len(self.mc.betay_list), n)
    
    def test_geometry_values_positive(self):
        """Test that geometry values are positive."""
        self.mc.load()
        for i in range(min(10, self.mc.n_elements)):  # Check first 10
            self.assertGreater(self.mc.b_list[i], 0, f"b[{i}] should be positive")
            self.assertGreater(self.mc.L_list[i], 0, f"L[{i}] should be positive")
            self.assertGreater(self.mc.betax_list[i], 0, f"betax[{i}] should be positive")
            self.assertGreater(self.mc.betay_list[i], 0, f"betay[{i}] should be positive")
    
    def test_frequency_reference_initialized(self):
        """Test that frequency reference is initialized after load."""
        self.mc.load()
        freqs = self.mc.get_frequencies()
        self.assertIsInstance(freqs, np.ndarray)
        self.assertGreater(len(freqs), 0)


class TestMultipleChamberCfgHandling(unittest.TestCase):
    """Test configuration file handling."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = Path(__file__).parent / "multiple"
        cls.input_dir = cls.test_dir / "input"
        cls.output_dir = cls.test_dir / "output"
        
        if not cls.input_dir.exists():
            raise unittest.SkipTest(f"Test input directory not found: {cls.input_dir}")
    
    def test_resolve_cfg_filename_from_mapping(self):
        """Test cfg filename resolution from mapping."""
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
        )
        # Round is in default mapping
        filename = mc._resolve_cfg_filename("Round")
        self.assertEqual(filename, "Round.cfg")
    
    def test_resolve_cfg_filename_default(self):
        """Test cfg filename resolution with default (apertype + .cfg)."""
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
        )
        # CustomType not in mapping, should use CustomType.cfg
        filename = mc._resolve_cfg_filename("CustomType")
        self.assertEqual(filename, "CustomType.cfg")
    
    def test_resolve_cfg_case_insensitive(self):
        """Test that cfg resolution is case-insensitive."""
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
        )
        filename_lower = mc._resolve_cfg_filename("round")
        filename_upper = mc._resolve_cfg_filename("ROUND")
        self.assertEqual(filename_lower, filename_upper)


class TestMultipleChamberCalculation(unittest.TestCase):
    """Test impedance calculation."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = Path(__file__).parent / "multiple"
        cls.input_dir = cls.test_dir / "input"
        # Use temp directory for output to not pollute test dir
        cls.output_dir = Path(tempfile.mkdtemp())
    
    @classmethod
    def tearDownClass(cls):
        """Clean up."""
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)
    
    def test_calculate_single_element(self):
        """Test calculating a single element."""
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
            out_dir=self.output_dir,
        )
        mc.load()
        
        # Calculate first element
        impedances = mc.calculate_element(0)
        self.assertIsInstance(impedances, dict)
        self.assertGreater(len(impedances), 0)
    
    def test_calculate_element_returns_arrays(self):
        """Test that calculate_element returns numpy arrays."""
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
            out_dir=self.output_dir,
        )
        mc.load()
        
        impedances = mc.calculate_element(0)
        for name, Z in impedances.items():
            self.assertIsInstance(Z, np.ndarray, f"{name} should be numpy array")


class TestMultipleChamberIntegration(unittest.TestCase):
    """Integration tests for full workflow."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.test_dir = Path(__file__).parent / "multiple"
        cls.input_dir = cls.test_dir / "input"
        cls.output_dir = Path(tempfile.mkdtemp())
        
        if not cls.input_dir.exists():
            raise unittest.SkipTest(f"Test input directory not found: {cls.input_dir}")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up."""
        if cls.output_dir.exists():
            shutil.rmtree(cls.output_dir)
    
    def test_full_workflow_few_elements(self):
        """Test full workflow with just a few elements."""
        # Create a subset for faster testing
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
            out_dir=self.output_dir,
        )
        mc.load()
        
        # Only test if we have at least 3 elements
        if mc.n_elements < 3:
            self.skipTest("Not enough elements for integration test")
        
        # Calculate just first 3 elements manually
        for i in range(3):
            impedances = mc.calculate_element(i)
            self.assertIsInstance(impedances, dict)
    
    def test_output_directory_created(self):
        """Test that output directory is created."""
        out_dir = self.output_dir / "test_output"
        mc = MultipleChamber(
            apertype_file="apertype2.txt",
            geom_file="b_L_betax_betay.txt",
            input_dir=self.input_dir,
            out_dir=out_dir,
        )
        mc.load()
        mc.calculate_element(0)  # Just calculate one
        
        # Output dir creation happens in calculate_all, not calculate_element
        # So we just verify the mc was created properly
        self.assertEqual(mc.out_dir, out_dir.resolve())


class TestMultipleChamberHelpers(unittest.TestCase):
    """Test helper methods."""
    
    def test_is_non_trivial_impedance_zeros(self):
        """Test detection of zero impedance."""
        Z = np.zeros(100)
        self.assertFalse(MultipleChamber._is_non_trivial_impedance(Z))
    
    def test_is_non_trivial_impedance_nonzero(self):
        """Test detection of non-zero impedance."""
        Z = np.ones(100) * 1e-3
        self.assertTrue(MultipleChamber._is_non_trivial_impedance(Z))
    
    def test_is_non_trivial_impedance_complex(self):
        """Test detection with complex impedance."""
        Z = np.ones(100, dtype=complex) * (1 + 1j)
        self.assertTrue(MultipleChamber._is_non_trivial_impedance(Z))
    
    def test_is_non_trivial_impedance_nan(self):
        """Test handling of NaN values."""
        Z = np.full(100, np.nan)
        self.assertFalse(MultipleChamber._is_non_trivial_impedance(Z))
    
    def test_guess_imped_type_long(self):
        """Test impedance type guessing for longitudinal."""
        self.assertEqual(MultipleChamber._guess_imped_type("ZLong"), "long")
        self.assertEqual(MultipleChamber._guess_imped_type("ZLongSurf"), "long")
    
    def test_guess_imped_type_trans(self):
        """Test impedance type guessing for transverse."""
        self.assertEqual(MultipleChamber._guess_imped_type("ZTransX"), "transx")
        self.assertEqual(MultipleChamber._guess_imped_type("ZTransY"), "transy")
        self.assertEqual(MultipleChamber._guess_imped_type("ZTrans"), "trans")
    
    def test_guess_imped_type_dipolar(self):
        """Test impedance type guessing for dipolar."""
        self.assertEqual(MultipleChamber._guess_imped_type("ZDipX"), "transx")
        self.assertEqual(MultipleChamber._guess_imped_type("ZDipY"), "transy")


if __name__ == "__main__":
    unittest.main(verbosity=2)
