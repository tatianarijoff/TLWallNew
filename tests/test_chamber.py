#!/usr/bin/env python3
"""
Unit tests for the pytlwall.Chamber module.

This module contains comprehensive tests for the Chamber class including:
- Initialization with various parameters
- Property validation and error handling
- Yokoya factor calculations
- Different chamber geometries
- Edge cases and boundary conditions
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import numpy as np
import pytlwall
from pytlwall.chamber import (
    Chamber, 
    ChamberShapeError, 
    ChamberDimensionError,
    DEFAULT_PIPE_LENGTH_M,
    DEFAULT_PIPE_RADIUS_M,
    DEFAULT_CHAMBER_SHAPE,
    DEFAULT_BETA_X,
    DEFAULT_BETA_Y
)


class TestChamberInitialization(unittest.TestCase):
    """Test Chamber initialization with various parameters."""
    
    def test_default_initialization(self):
        """Test chamber creation with default parameters."""
        chamber = Chamber()
        
        self.assertEqual(chamber.pipe_len_m, DEFAULT_PIPE_LENGTH_M)
        self.assertEqual(chamber.pipe_rad_m, DEFAULT_PIPE_RADIUS_M)
        self.assertEqual(chamber.chamber_shape, DEFAULT_CHAMBER_SHAPE)
        self.assertEqual(chamber.betax, DEFAULT_BETA_X)
        self.assertEqual(chamber.betay, DEFAULT_BETA_Y)
        self.assertEqual(len(chamber.layers), 0)
    
    def test_circular_chamber(self):
        """Test circular chamber initialization."""
        radius = 0.025  # 25 mm
        chamber = Chamber(pipe_rad_m=radius, chamber_shape='CIRCULAR')
        
        self.assertEqual(chamber.pipe_rad_m, radius)
        self.assertEqual(chamber.pipe_hor_m, radius)
        self.assertEqual(chamber.pipe_ver_m, radius)
        self.assertEqual(chamber.chamber_shape, 'CIRCULAR')
        self.assertAlmostEqual(chamber.yokoya_q, 0.0, places=10)
    
    def test_elliptical_chamber(self):
        """Test elliptical chamber initialization."""
        hor = 0.030  # 30 mm
        ver = 0.020  # 20 mm
        chamber = Chamber(
            pipe_hor_m=hor,
            pipe_ver_m=ver,
            chamber_shape='ELLIPTICAL'
        )
        
        self.assertEqual(chamber.pipe_hor_m, hor)
        self.assertEqual(chamber.pipe_ver_m, ver)
        self.assertEqual(chamber.chamber_shape, 'ELLIPTICAL')
        self.assertGreater(chamber.yokoya_q, 0.0)
    
    def test_rectangular_chamber(self):
        """Test rectangular chamber initialization."""
        hor = 0.040  # 40 mm
        ver = 0.025  # 25 mm
        chamber = Chamber(
            pipe_hor_m=hor,
            pipe_ver_m=ver,
            chamber_shape='RECTANGULAR'
        )
        
        self.assertEqual(chamber.chamber_shape, 'RECTANGULAR')
        self.assertGreater(chamber.yokoya_q, 0.0)
    
    def test_with_beta_functions(self):
        """Test initialization with beta functions."""
        betax = 100.0
        betay = 50.0
        chamber = Chamber(betax=betax, betay=betay)
        
        self.assertEqual(chamber.betax, betax)
        self.assertEqual(chamber.betay, betay)
    
    def test_with_component_name(self):
        """Test initialization with custom component name."""
        name = "test_chamber_01"
        chamber = Chamber(component_name=name)
        
        self.assertEqual(chamber.component_name, name)


class TestChamberDimensions(unittest.TestCase):
    """Test chamber dimension properties and validation."""
    
    def test_set_pipe_length(self):
        """Test setting pipe length."""
        chamber = Chamber()
        new_length = 2.5
        chamber.pipe_len_m = new_length
        
        self.assertEqual(chamber.pipe_len_m, new_length)
    
    def test_negative_pipe_length(self):
        """Test that negative pipe length raises error."""
        chamber = Chamber()
        
        with self.assertRaises(ChamberDimensionError):
            chamber.pipe_len_m = -1.0
    
    def test_zero_pipe_length(self):
        """Test that zero pipe length raises error."""
        with self.assertRaises(ChamberDimensionError):
            chamber = Chamber(pipe_len_m=0.0)
    
    def test_set_pipe_radius(self):
        """Test setting pipe radius updates all dimensions."""
        chamber = Chamber()
        new_radius = 0.030
        chamber.pipe_rad_m = new_radius
        
        self.assertEqual(chamber.pipe_rad_m, new_radius)
        self.assertEqual(chamber.pipe_hor_m, new_radius)
        self.assertEqual(chamber.pipe_ver_m, new_radius)
    
    def test_negative_pipe_radius(self):
        """Test that negative pipe radius raises error."""
        with self.assertRaises(ChamberDimensionError):
            chamber = Chamber(pipe_rad_m=-0.01)
    
    def test_set_horizontal_dimension(self):
        """Test setting horizontal dimension."""
        chamber = Chamber()
        new_hor = 0.035
        chamber.pipe_hor_m = new_hor
        
        self.assertEqual(chamber.pipe_hor_m, new_hor)
    
    def test_negative_horizontal(self):
        """Test that negative horizontal dimension raises error."""
        chamber = Chamber()
        
        with self.assertRaises(ChamberDimensionError):
            chamber.pipe_hor_m = -0.01
    
    def test_set_vertical_dimension(self):
        """Test setting vertical dimension."""
        chamber = Chamber()
        new_ver = 0.025
        chamber.pipe_ver_m = new_ver
        
        self.assertEqual(chamber.pipe_ver_m, new_ver)
    
    def test_negative_vertical(self):
        """Test that negative vertical dimension raises error."""
        chamber = Chamber()
        
        with self.assertRaises(ChamberDimensionError):
            chamber.pipe_ver_m = -0.01
    
    def test_invalid_dimension_type(self):
        """Test that invalid dimension types raise errors."""
        chamber = Chamber()
        
        with self.assertRaises(ChamberDimensionError):
            chamber.pipe_len_m = "invalid"
        
        with self.assertRaises(ChamberDimensionError):
            chamber.pipe_rad_m = None


class TestBetaFunctions(unittest.TestCase):
    """Test beta function properties and validation."""
    
    def test_set_betax(self):
        """Test setting horizontal beta function."""
        chamber = Chamber()
        new_betax = 150.0
        chamber.betax = new_betax
        
        self.assertEqual(chamber.betax, new_betax)
    
    def test_set_betay(self):
        """Test setting vertical beta function."""
        chamber = Chamber()
        new_betay = 75.0
        chamber.betay = new_betay
        
        self.assertEqual(chamber.betay, new_betay)
    
    def test_negative_betax(self):
        """Test that negative beta_x raises error."""
        chamber = Chamber()
        
        with self.assertRaises(ChamberDimensionError):
            chamber.betax = -10.0
    
    def test_zero_betax(self):
        """Test that zero beta_x raises error."""
        with self.assertRaises(ChamberDimensionError):
            chamber = Chamber(betax=0.0)
    
    def test_negative_betay(self):
        """Test that negative beta_y raises error."""
        chamber = Chamber()
        
        with self.assertRaises(ChamberDimensionError):
            chamber.betay = -10.0
    
    def test_invalid_beta_type(self):
        """Test that invalid beta types raise errors."""
        chamber = Chamber()
        
        with self.assertRaises(ChamberDimensionError):
            chamber.betax = "invalid"


class TestChamberShapes(unittest.TestCase):
    """Test chamber shape specifications and Yokoya factors."""
    
    def test_circular_shape(self):
        """Test circular chamber shape."""
        chamber = Chamber(chamber_shape='CIRCULAR')
        
        self.assertEqual(chamber.chamber_shape, 'CIRCULAR')
        self.assertAlmostEqual(chamber.long_yokoya_factor, 1.0, places=5)
        self.assertAlmostEqual(chamber.drivx_yokoya_factor, 1.0, places=5)
        self.assertAlmostEqual(chamber.drivy_yokoya_factor, 1.0, places=5)
        self.assertAlmostEqual(chamber.detx_yokoya_factor, 0.0, places=5)
        self.assertAlmostEqual(chamber.dety_yokoya_factor, 0.0, places=5)
    
    def test_elliptical_shape(self):
        """Test elliptical chamber shape."""
        chamber = Chamber(
            pipe_hor_m=0.030,
            pipe_ver_m=0.020,
            chamber_shape='ELLIPTICAL'
        )
        
        self.assertEqual(chamber.chamber_shape, 'ELLIPTICAL')
        # Yokoya factors should differ from unity for non-circular
        self.assertNotAlmostEqual(chamber.long_yokoya_factor, 1.0, places=2)
    
    def test_rectangular_shape(self):
        """Test rectangular chamber shape."""
        chamber = Chamber(
            pipe_hor_m=0.040,
            pipe_ver_m=0.025,
            chamber_shape='RECTANGULAR'
        )
        
        self.assertEqual(chamber.chamber_shape, 'RECTANGULAR')
        self.assertNotAlmostEqual(chamber.long_yokoya_factor, 1.0, places=2)
    
    def test_case_insensitive_shape(self):
        """Test that shape specification is case-insensitive."""
        chamber1 = Chamber(chamber_shape='circular')
        chamber2 = Chamber(chamber_shape='CIRCULAR')
        chamber3 = Chamber(chamber_shape='Circular')
        
        self.assertEqual(chamber1.chamber_shape, chamber2.chamber_shape)
        self.assertEqual(chamber2.chamber_shape, chamber3.chamber_shape)
    
    def test_invalid_shape(self):
        """Test that invalid shape raises error."""
        with self.assertRaises(ChamberShapeError):
            chamber = Chamber(chamber_shape='INVALID')
    
    def test_change_shape(self):
        """Test changing chamber shape after initialization."""
        chamber = Chamber(chamber_shape='CIRCULAR')
        self.assertEqual(chamber.chamber_shape, 'CIRCULAR')
        
        chamber.chamber_shape = 'ELLIPTICAL'
        self.assertEqual(chamber.chamber_shape, 'ELLIPTICAL')


class TestYokoyaFactors(unittest.TestCase):
    """Test Yokoya factor calculations."""
    
    def test_circular_yokoya_q(self):
        """Test Yokoya q parameter for circular chamber."""
        chamber = Chamber(pipe_rad_m=0.025, chamber_shape='CIRCULAR')
        
        self.assertAlmostEqual(chamber.yokoya_q, 0.0, places=10)
    
    def test_elliptical_yokoya_q(self):
        """Test Yokoya q parameter for elliptical chamber."""
        hor = 0.030
        ver = 0.020
        chamber = Chamber(
            pipe_hor_m=hor,
            pipe_ver_m=ver,
            chamber_shape='ELLIPTICAL'
        )
        
        expected_q = abs(hor - ver) / (hor + ver)
        self.assertAlmostEqual(chamber.yokoya_q, expected_q, places=10)
    
    def test_rectangular_yokoya_q(self):
        """Test Yokoya q parameter for rectangular chamber."""
        hor = 0.040
        ver = 0.020
        chamber = Chamber(
            pipe_hor_m=hor,
            pipe_ver_m=ver,
            chamber_shape='RECTANGULAR'
        )
        
        expected_q = abs(hor - ver) / (hor + ver)
        self.assertAlmostEqual(chamber.yokoya_q, expected_q, places=10)
    
    def test_get_yokoya_factors_dict(self):
        """Test getting all Yokoya factors as dictionary."""
        chamber = Chamber(
            pipe_hor_m=0.030,
            pipe_ver_m=0.020,
            chamber_shape='ELLIPTICAL'
        )
        
        factors = chamber.get_yokoya_factors()
        
        self.assertIn('q', factors)
        self.assertIn('longitudinal', factors)
        self.assertIn('drivx', factors)
        self.assertIn('drivy', factors)
        self.assertIn('detx', factors)
        self.assertIn('dety', factors)
        
        self.assertIsInstance(factors['q'], float)
        self.assertIsInstance(factors['longitudinal'], float)
    
    def test_yokoya_factors_positive(self):
        """Test that driving Yokoya factors are positive."""
        chamber = Chamber(
            pipe_hor_m=0.030,
            pipe_ver_m=0.020,
            chamber_shape='ELLIPTICAL'
        )
        
        self.assertGreaterEqual(chamber.long_yokoya_factor, 0.0)
        self.assertGreaterEqual(chamber.drivx_yokoya_factor, 0.0)
        self.assertGreaterEqual(chamber.drivy_yokoya_factor, 0.0)


class TestChamberMethods(unittest.TestCase):
    """Test Chamber utility methods."""
    
    def test_get_dimensions(self):
        """Test get_dimensions method."""
        length = 1.5
        radius = 0.025
        chamber = Chamber(pipe_len_m=length, pipe_rad_m=radius)
        
        dims = chamber.get_dimensions()
        
        self.assertIn('length', dims)
        self.assertIn('radius', dims)
        self.assertIn('horizontal', dims)
        self.assertIn('vertical', dims)
        
        self.assertEqual(dims['length'], length)
        self.assertEqual(dims['radius'], radius)
    
    def test_summary(self):
        """Test summary method."""
        chamber = Chamber(
            pipe_hor_m=0.030,
            pipe_ver_m=0.020,
            chamber_shape='ELLIPTICAL',
            component_name='test_chamber'
        )
        
        summary = chamber.summary()
        
        self.assertIsInstance(summary, str)
        self.assertIn('ELLIPTICAL', summary)
        self.assertIn('test_chamber', summary)
        self.assertIn('Yokoya', summary)
    
    def test_repr(self):
        """Test __repr__ method."""
        chamber = Chamber(
            pipe_hor_m=0.030,
            pipe_ver_m=0.020,
            chamber_shape='ELLIPTICAL'
        )
        
        repr_str = repr(chamber)
        
        self.assertIsInstance(repr_str, str)
        self.assertIn('Chamber', repr_str)
        self.assertIn('ELLIPTICAL', repr_str)
    
    def test_str(self):
        """Test __str__ method."""
        chamber = Chamber(chamber_shape='CIRCULAR', pipe_rad_m=0.025)
        
        str_repr = str(chamber)
        
        self.assertIsInstance(str_repr, str)
        self.assertIn('CIRCULAR', str_repr)


class TestChamberLayers(unittest.TestCase):
    """Test Chamber with multiple layers."""
    
    def test_empty_layers(self):
        """Test chamber with no layers."""
        chamber = Chamber()
        
        self.assertEqual(len(chamber.layers), 0)
        self.assertIsInstance(chamber.layers, list)
    
    def test_with_layers(self):
        """Test chamber with layers list."""
        # Mock layer objects (in real use, these would be Layer instances)
        layers = ['layer1', 'layer2', 'layer3']
        chamber = Chamber(layers=layers)
        
        self.assertEqual(len(chamber.layers), 3)
        self.assertEqual(chamber.layers, layers)


class TestChamberEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""
    
    def test_very_small_dimensions(self):
        """Test chamber with very small dimensions."""
        small_dim = 1e-6  # 1 micrometer
        chamber = Chamber(pipe_rad_m=small_dim)
        
        self.assertEqual(chamber.pipe_rad_m, small_dim)
    
    def test_very_large_dimensions(self):
        """Test chamber with very large dimensions."""
        large_dim = 10.0  # 10 meters
        chamber = Chamber(pipe_rad_m=large_dim)
        
        self.assertEqual(chamber.pipe_rad_m, large_dim)
    
    def test_equal_hor_ver_elliptical(self):
        """Test elliptical chamber with equal dimensions."""
        dim = 0.025
        chamber = Chamber(
            pipe_hor_m=dim,
            pipe_ver_m=dim,
            chamber_shape='ELLIPTICAL'
        )
        
        # Should have q ≈ 0 (nearly circular)
        self.assertAlmostEqual(chamber.yokoya_q, 0.0, places=10)
    
    def test_extreme_aspect_ratio(self):
        """Test chamber with extreme aspect ratio."""
        chamber = Chamber(
            pipe_hor_m=0.100,  # 100 mm
            pipe_ver_m=0.010,  # 10 mm
            chamber_shape='ELLIPTICAL'
        )
        
        # q should be close to 1 for extreme aspect ratio
        self.assertGreater(chamber.yokoya_q, 0.8)
        self.assertLess(chamber.yokoya_q, 1.0)


class TestChamberIntegration(unittest.TestCase):
    """Integration tests for realistic chamber configurations."""
    
    def test_lhc_style_chamber(self):
        """Test LHC-style circular chamber."""
        # LHC beam screen: ~44 mm radius
        chamber = Chamber(
            pipe_rad_m=0.022,
            pipe_len_m=1.0,
            chamber_shape='CIRCULAR',
            betax=100.0,
            betay=100.0,
            component_name='LHC_arc_dipole'
        )
        
        self.assertEqual(chamber.chamber_shape, 'CIRCULAR')
        self.assertAlmostEqual(chamber.yokoya_q, 0.0)
        self.assertEqual(chamber.component_name, 'LHC_arc_dipole')
    
    def test_flat_chamber(self):
        """Test flat chamber for modern colliders."""
        # Typical flat chamber design
        chamber = Chamber(
            pipe_hor_m=0.040,  # 40 mm half-width
            pipe_ver_m=0.012,  # 12 mm half-height
            pipe_len_m=1.0,
            chamber_shape='ELLIPTICAL',
            betax=20.0,
            betay=5.0,
            component_name='flat_arc_chamber'
        )
        
        self.assertEqual(chamber.chamber_shape, 'ELLIPTICAL')
        self.assertGreater(chamber.yokoya_q, 0.5)
        self.assertNotEqual(chamber.betax, chamber.betay)


def run_tests():
    """Run all test suites."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestChamberInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestChamberDimensions))
    suite.addTests(loader.loadTestsFromTestCase(TestBetaFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestChamberShapes))
    suite.addTests(loader.loadTestsFromTestCase(TestYokoyaFactors))
    suite.addTests(loader.loadTestsFromTestCase(TestChamberMethods))
    suite.addTests(loader.loadTestsFromTestCase(TestChamberLayers))
    suite.addTests(loader.loadTestsFromTestCase(TestChamberEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestChamberIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
