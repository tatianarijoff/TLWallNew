"""
Unit tests for io_util module.

Tests unified I/O utilities for pytlwall package.
"""

import unittest
import tempfile
import os
from pathlib import Path
import numpy as np

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pytlwall import io_util


class TestReadFrequencyTxt(unittest.TestCase):
    """Test read_frequency_txt function."""
    
    def test_read_simple_frequency_file(self):
        """Test reading simple frequency file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("1.0e3\n")
            f.write("1.0e4\n")
            f.write("1.0e5\n")
            f.write("1.0e6\n")
            temp_file = f.name
        
        try:
            freqs = io_util.read_frequency_txt(temp_file)
            
            self.assertEqual(len(freqs), 4)
            self.assertAlmostEqual(freqs[0], 1.0e3)
            self.assertAlmostEqual(freqs[1], 1.0e4)
            self.assertAlmostEqual(freqs[2], 1.0e5)
            self.assertAlmostEqual(freqs[3], 1.0e6)
        finally:
            os.unlink(temp_file)
    
    def test_read_frequency_with_header(self):
        """Test reading frequency file with header rows."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Header line 1\n")
            f.write("# Header line 2\n")
            f.write("1.0e3\n")
            f.write("1.0e4\n")
            temp_file = f.name
        
        try:
            freqs = io_util.read_frequency_txt(temp_file, skipped_rows=2)
            
            self.assertEqual(len(freqs), 2)
            self.assertAlmostEqual(freqs[0], 1.0e3)
            self.assertAlmostEqual(freqs[1], 1.0e4)
        finally:
            os.unlink(temp_file)
    
    def test_read_frequency_specific_column(self):
        """Test reading frequency from specific column."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("0 1.0e3 100\n")
            f.write("1 1.0e4 200\n")
            f.write("2 1.0e5 300\n")
            temp_file = f.name
        
        try:
            freqs = io_util.read_frequency_txt(temp_file, column=1)
            
            self.assertEqual(len(freqs), 3)
            self.assertAlmostEqual(freqs[0], 1.0e3)
            self.assertAlmostEqual(freqs[1], 1.0e4)
            self.assertAlmostEqual(freqs[2], 1.0e5)
        finally:
            os.unlink(temp_file)
    
    def test_read_frequency_with_unit_conversion(self):
        """Test reading frequency with unit conversion."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("1.0\n")  # 1 MHz
            f.write("10.0\n")  # 10 MHz
            temp_file = f.name
        
        try:
            freqs = io_util.read_frequency_txt(temp_file, unit='MHz')
            
            self.assertEqual(len(freqs), 2)
            self.assertAlmostEqual(freqs[0], 1.0e6)
            self.assertAlmostEqual(freqs[1], 1.0e7)
        finally:
            os.unlink(temp_file)
    
    def test_read_frequency_with_comma_separator(self):
        """Test reading CSV frequency file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("index,frequency,amplitude\n")
            f.write("0,1.0e3,0.5\n")
            f.write("1,1.0e4,0.6\n")
            temp_file = f.name
        
        try:
            freqs = io_util.read_frequency_txt(temp_file, separator=',', 
                                                column=1, skipped_rows=1)
            
            self.assertEqual(len(freqs), 2)
            self.assertAlmostEqual(freqs[0], 1.0e3)
            self.assertAlmostEqual(freqs[1], 1.0e4)
        finally:
            os.unlink(temp_file)


class TestReadSurfaceImpedanceTxt(unittest.TestCase):
    """Test read_surface_impedance_txt function."""
    
    def test_read_surface_impedance(self):
        """Test reading surface impedance file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("1.0e3 1.5e-3 2.5e-3\n")
            f.write("1.0e4 1.6e-3 2.6e-3\n")
            f.write("1.0e5 1.7e-3 2.7e-3\n")
            temp_file = f.name
        
        try:
            freqs, Z = io_util.read_surface_impedance_txt(temp_file)
            
            self.assertEqual(len(freqs), 3)
            self.assertEqual(len(Z), 3)
            
            self.assertAlmostEqual(freqs[0], 1.0e3)
            self.assertAlmostEqual(Z[0].real, 1.5e-3)
            self.assertAlmostEqual(Z[0].imag, 2.5e-3)
        finally:
            os.unlink(temp_file)
    
    def test_read_surface_impedance_with_header(self):
        """Test reading surface impedance with header."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("# Frequency  Real  Imag\n")
            f.write("1.0e3 1.5e-3 2.5e-3\n")
            temp_file = f.name
        
        try:
            freqs, Z = io_util.read_surface_impedance_txt(temp_file, skipped_rows=1)
            
            self.assertEqual(len(freqs), 1)
            self.assertAlmostEqual(freqs[0], 1.0e3)
        finally:
            os.unlink(temp_file)


class TestReadImpedanceFile(unittest.TestCase):
    """Test read_impedance_file function."""
    
    def test_read_impedance_file_default(self):
        """Test reading impedance file with default columns."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write("1.0e3\t1.5e-3\t2.5e-3\n")
            f.write("1.0e4\t1.6e-3\t2.6e-3\n")
            temp_file = f.name
        
        try:
            freqs, Z = io_util.read_impedance_file(temp_file)
            
            self.assertEqual(len(freqs), 2)
            self.assertIsInstance(Z[0], complex)
            self.assertAlmostEqual(freqs[0], 1.0e3)
            self.assertAlmostEqual(Z[0].real, 1.5e-3)
            self.assertAlmostEqual(Z[0].imag, 2.5e-3)
        finally:
            os.unlink(temp_file)
    
    def test_read_impedance_file_with_header(self):
        """Test reading impedance file with header."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.dat', delete=False) as f:
            f.write("Frequency [Hz]\tRe(Z) [Ohm/m]\tIm(Z) [Ohm/m]\n")
            f.write("1.0e3\t1.5e-3\t2.5e-3\n")
            f.write("1.0e4\t1.6e-3\t2.6e-3\n")
            temp_file = f.name
        
        try:
            freqs, Z = io_util.read_impedance_file(temp_file, skipped_rows=1)
            
            self.assertEqual(len(freqs), 2)
            self.assertAlmostEqual(freqs[0], 1.0e3)
        finally:
            os.unlink(temp_file)


class TestLoadGeometryFunctions(unittest.TestCase):
    """Test geometry loading functions."""
    
    def test_load_apertype(self):
        """Test loading aperture types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("CIRCULAR\n")
            f.write("ELLIPTICAL\n")
            f.write("RECTANGULAR\n")
            temp_file = f.name
        
        try:
            types = io_util.load_apertype(temp_file)
            
            self.assertEqual(len(types), 3)
            self.assertEqual(types[0], 'CIRCULAR')
            self.assertEqual(types[1], 'ELLIPTICAL')
            self.assertEqual(types[2], 'RECTANGULAR')
        finally:
            os.unlink(temp_file)
    
    def test_load_b_L(self):
        """Test loading radius and length data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("0.022 10.0\n")
            f.write("0.030 5.0\n")
            f.write("0.025 15.0\n")
            temp_file = f.name
        
        try:
            radii, lengths = io_util.load_b_L(temp_file)
            
            self.assertEqual(len(radii), 3)
            self.assertEqual(len(lengths), 3)
            self.assertAlmostEqual(radii[0], 0.022)
            self.assertAlmostEqual(lengths[0], 10.0)
        finally:
            os.unlink(temp_file)
    
    def test_load_b_L_betax_betay(self):
        """Test loading geometry with beta functions."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("0.022 10.0 100.0 50.0\n")
            f.write("0.030 5.0 80.0 40.0\n")
            temp_file = f.name
        
        try:
            radii, lengths, betax, betay = io_util.load_b_L_betax_betay(temp_file)
            
            self.assertEqual(len(radii), 2)
            self.assertAlmostEqual(radii[0], 0.022)
            self.assertAlmostEqual(betax[0], 100.0)
            self.assertAlmostEqual(betay[0], 50.0)
        finally:
            os.unlink(temp_file)
    
    def test_load_x_y_L_betax_betay(self):
        """Test loading rectangular geometry with beta."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("0.030 0.020 10.0 100.0 50.0\n")
            f.write("0.025 0.015 5.0 80.0 40.0\n")
            temp_file = f.name
        
        try:
            hor, ver, lengths, betax, betay = io_util.load_x_y_L_betax_betay(temp_file)
            
            self.assertEqual(len(hor), 2)
            self.assertAlmostEqual(hor[0], 0.030)
            self.assertAlmostEqual(ver[0], 0.020)
            self.assertAlmostEqual(lengths[0], 10.0)
        finally:
            os.unlink(temp_file)


class TestPrintImpedanceOutput(unittest.TestCase):
    """Test print_impedance_output function."""
    
    def test_print_single_impedance_csv(self):
        """Test exporting single impedance to CSV."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = io_util.print_impedance_output(
                freqs=freqs,
                imped_dict={'ZLong': Z},
                savedir=tmpdir,
                savename='test.csv'
            )
            
            self.assertTrue(output_path.exists())
            
            # Read back and verify
            import pandas as pd
            df = pd.read_csv(output_path, sep='\t')
            
            self.assertEqual(len(df), 3)
            self.assertIn('f [Hz]', df.columns)
    
    def test_print_single_impedance_txt(self):
        """Test exporting single impedance to TXT."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = io_util.print_impedance_output(
                freqs=freqs,
                imped_dict={'ZLong': Z},
                savedir=tmpdir,
                savename='test.txt'
            )
            
            self.assertTrue(output_path.exists())
    
    def test_print_single_impedance_dat(self):
        """Test exporting single impedance to DAT."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = io_util.print_impedance_output(
                freqs=freqs,
                imped_dict={'ZLong': Z},
                savedir=tmpdir,
                savename='test.dat'
            )
            
            self.assertTrue(output_path.exists())
            self.assertEqual(output_path.suffix, '.dat')
            
            # Read back and verify content
            with open(output_path, 'r') as f:
                lines = f.readlines()
            
            # Should have header + 3 data lines
            self.assertEqual(len(lines), 4)
    
    def test_print_multiple_impedances(self):
        """Test exporting multiple impedances."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z1 = np.array([1+2j, 3+4j, 5+6j])
        Z2 = np.array([7+8j, 9+10j, 11+12j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = io_util.print_impedance_output(
                freqs=freqs,
                imped_dict={'ZLong': Z1, 'ZTrans': Z2},
                savedir=tmpdir,
                savename='test.csv'
            )
            
            self.assertTrue(output_path.exists())
            
            # Read back and verify
            import pandas as pd
            df = pd.read_csv(output_path, sep='\t')
            
            # Should have freq + 2 real + 2 imag columns
            self.assertGreaterEqual(len(df.columns), 5)
    
    def test_print_with_standard_labels(self):
        """Test exporting with standard labels."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = io_util.print_impedance_output(
                freqs=freqs,
                imped_dict={'ZLong': Z},
                savedir=tmpdir,
                savename='test.csv',
                use_standard_labels=True
            )
            
            import pandas as pd
            df = pd.read_csv(output_path, sep='\t')
            
            # Should have standard label
            col_str = ' '.join(df.columns)
            self.assertIn('Longitudinal', col_str)


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions."""
    
    def test_print_single_impedance_wrapper(self):
        """Test print_single_impedance convenience function."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = io_util.print_single_impedance(
                freqs=freqs,
                impedance=Z,
                savedir=tmpdir,
                savename='test.csv',
                label='MyZ'
            )
            
            self.assertTrue(output_path.exists())
    
    def test_export_impedance(self):
        """Test export_impedance alternative interface."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = io_util.export_impedance(
                freqs=freqs,
                imped_dict={'ZLong': Z},
                output_path=os.path.join(tmpdir, 'test.csv')
            )
            
            self.assertTrue(output_path.exists())
    
    def test_get_standard_label(self):
        """Test get_standard_label function."""
        label = io_util.get_standard_label('ZLong')
        self.assertEqual(label, 'Longitudinal Impedance')
        
        label = io_util.get_standard_label('ZDipX')
        self.assertEqual(label, 'Dipolar X Impedance')
        
        # Unknown key returns itself
        label = io_util.get_standard_label('CustomZ')
        self.assertEqual(label, 'CustomZ')
    
    def test_list_supported_formats(self):
        """Test list_supported_formats function."""
        formats = io_util.list_supported_formats()
        
        self.assertIn('.csv', formats)
        self.assertIn('.txt', formats)
        self.assertIn('.dat', formats)
        self.assertIn('.xlsx', formats)


class TestValidation(unittest.TestCase):
    """Test input validation."""
    
    def test_empty_freqs_raises(self):
        """Test that empty freqs raises error."""
        freqs = np.array([])
        Z = np.array([])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                io_util.print_impedance_output(
                    freqs=freqs,
                    imped_dict={'Z': Z},
                    savedir=tmpdir,
                    savename='test.csv'
                )
    
    def test_empty_imped_dict_raises(self):
        """Test that empty imped_dict raises error."""
        freqs = np.array([1e3, 1e4])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                io_util.print_impedance_output(
                    freqs=freqs,
                    imped_dict={},
                    savedir=tmpdir,
                    savename='test.csv'
                )
    
    def test_length_mismatch_raises(self):
        """Test that length mismatch raises error."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j])  # Wrong length
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                io_util.print_impedance_output(
                    freqs=freqs,
                    imped_dict={'Z': Z},
                    savedir=tmpdir,
                    savename='test.csv'
                )
    
    def test_unsupported_extension_raises(self):
        """Test that unsupported extension raises error."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                io_util.print_impedance_output(
                    freqs=freqs,
                    imped_dict={'Z': Z},
                    savedir=tmpdir,
                    savename='test.xyz'  # Unsupported
                )


class TestFallbackBehavior(unittest.TestCase):
    """Test fallback behavior when dependencies are missing."""
    
    def test_xlsx_fallback_to_txt(self):
        """Test that xlsx falls back to txt when openpyxl is missing."""
        freqs = np.array([1e3, 1e4, 1e5])
        Z = np.array([1+2j, 3+4j, 5+6j])
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Request xlsx - if openpyxl not installed, should fallback to txt
            output_path = io_util.print_impedance_output(
                freqs=freqs,
                imped_dict={'ZLong': Z},
                savedir=tmpdir,
                savename='test.xlsx',
                save_csv_fallback=True
            )
            
            # Should have created a file (either xlsx or txt fallback)
            self.assertTrue(output_path.exists())
            
            # If openpyxl is not installed, extension should be .txt
            if output_path.suffix == '.txt':
                # Verify it's readable
                with open(output_path, 'r') as f:
                    lines = f.readlines()
                self.assertGreater(len(lines), 0)
    
    def test_pandas_available_flag(self):
        """Test that PANDAS_AVAILABLE flag is set correctly."""
        # This just verifies the flag exists and is boolean
        self.assertIsInstance(io_util.PANDAS_AVAILABLE, bool)


class TestSaveChamberImpedance(unittest.TestCase):
    """Test save_chamber_impedance export."""

    @unittest.skipUnless(
        hasattr(io_util, 'save_chamber_impedance'),
        'save_chamber_impedance not implemented in io_util',
    )
    def test_save_chamber_impedance_writes_expected_files(self):
        """Test exporting impedance files for longitudinal/transverse and extras."""
        freqs = np.array([1e3, 1e4, 1e5])
        impedance_results = {
            'ZLongRe': np.array([1.0, 2.0, 3.0]),
            'ZLongIm': np.array([0.1, 0.2, 0.3]),
            'ZTransRe': np.array([4.0, 5.0, 6.0]),
            'ZTransIm': np.array([0.4, 0.5, 0.6]),
            'ZDipXRe': np.array([7.0, 8.0, 9.0]),
            'ZDipXIm': np.array([0.7, 0.8, 0.9]),
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            written = io_util.save_chamber_impedance(
                output_dir=tmpdir,
                impedance_freq=freqs,
                impedance_results=impedance_results,
            )

            expected_files = {
                Path(tmpdir) / 'ZLong.txt',
                Path(tmpdir) / 'ZTrans.txt',
                Path(tmpdir) / 'ZDipX.txt',
            }

            # Verify return value includes at least the expected files.
            self.assertTrue(expected_files.issubset(set(written)))

            for file_path in expected_files:
                self.assertTrue(file_path.exists(), str(file_path))

                # Header must include the expected column names.
                with open(file_path, 'r', encoding='utf-8') as f:
                    header = f.readline().strip().lstrip('#').strip()

                base = file_path.stem
                self.assertIn('f', header)
                self.assertIn(f'{base}Re', header)
                self.assertIn(f'{base}Im', header)

                # Verify numeric content (3 rows x 3 cols) and frequency column.
                data = np.loadtxt(file_path, comments='#', skiprows=1)
                self.assertEqual(data.shape, (3, 3))
                np.testing.assert_allclose(data[:, 0], freqs)

    @unittest.skipUnless(
        hasattr(io_util, 'save_chamber_impedance'),
        'save_chamber_impedance not implemented in io_util',
    )
    def test_save_chamber_impedance_missing_mandatory_raises(self):
        """Test that missing ZLong/ZTrans components raise ValueError."""
        freqs = np.array([1e3, 1e4, 1e5])
        impedance_results = {
            'ZLongRe': np.array([1.0, 2.0, 3.0]),
            'ZLongIm': np.array([0.1, 0.2, 0.3]),
            # ZTrans missing on purpose.
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            with self.assertRaises(ValueError):
                io_util.save_chamber_impedance(
                    output_dir=tmpdir,
                    impedance_freq=freqs,
                    impedance_results=impedance_results,
                )


if __name__ == '__main__':
    unittest.main(verbosity=2)
