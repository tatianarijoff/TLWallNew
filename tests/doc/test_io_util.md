# test_io_util.py - I/O Utilities Tests

[← Back to Testing Documentation](../TESTING.md)

---

## Overview

Tests for the unified `io_util` module which provides input/output functions for reading frequency files, impedance data, geometry configurations, and exporting impedance results.

**Module tested**: `pytlwall.io_util`

**Run this test**:
```bash
python tests/test_io_util.py -v
```

---

## Test Classes

### TestReadFrequencyTxt

Tests frequency file reading.

| Test Method | Description |
|-------------|-------------|
| `test_read_simple_frequency_file` | Tests basic frequency file (one column) |
| `test_read_frequency_with_header` | Tests skipping header rows |
| `test_read_frequency_specific_column` | Tests reading from specific column |
| `test_read_frequency_with_unit_conversion` | Tests Hz/kHz/MHz/GHz/THz conversion |
| `test_read_frequency_with_comma_separator` | Tests CSV format |

### TestReadSurfaceImpedanceTxt

Tests surface impedance file reading.

| Test Method | Description |
|-------------|-------------|
| `test_read_surface_impedance` | Tests 3-column format (freq, Re, Im) |
| `test_read_surface_impedance_with_header` | Tests header row skipping |

### TestReadImpedanceFile

Tests generic impedance file reading.

| Test Method | Description |
|-------------|-------------|
| `test_read_impedance_file_default` | Tests default column indices |
| `test_read_impedance_file_with_header` | Tests header handling |

### TestLoadGeometryFunctions

Tests geometry loading functions.

| Test Method | Description |
|-------------|-------------|
| `test_load_apertype` | Tests aperture type string loading |
| `test_load_b_L` | Tests (radius, length) loading |
| `test_load_b_L_betax_betay` | Tests (radius, length, βx, βy) loading |
| `test_load_x_y_L_betax_betay` | Tests (hor, ver, length, βx, βy) loading |

### TestPrintImpedanceOutput

Tests impedance export functionality.

| Test Method | Description |
|-------------|-------------|
| `test_print_single_impedance_csv` | Tests CSV export |
| `test_print_single_impedance_txt` | Tests TXT export |
| `test_print_single_impedance_dat` | Tests DAT export |
| `test_print_multiple_impedances` | Tests multi-impedance export |
| `test_print_with_standard_labels` | Tests standard label mapping |

### TestConvenienceFunctions

Tests convenience wrapper functions.

| Test Method | Description |
|-------------|-------------|
| `test_print_single_impedance_wrapper` | Tests print_single_impedance() |
| `test_export_impedance` | Tests export_impedance() alternative interface |
| `test_get_standard_label` | Tests label mapping (ZLong → "Longitudinal Impedance") |
| `test_list_supported_formats` | Tests format list retrieval |

### TestValidation

Tests input validation.

| Test Method | Description |
|-------------|-------------|
| `test_empty_freqs_raises` | Verifies ValueError for empty freqs |
| `test_empty_imped_dict_raises` | Verifies ValueError for empty dict |
| `test_length_mismatch_raises` | Verifies ValueError for mismatched lengths |
| `test_unsupported_extension_raises` | Verifies ValueError for .xyz extension |

### TestFallbackBehavior

Tests fallback when dependencies missing.

| Test Method | Description |
|-------------|-------------|
| `test_xlsx_fallback_to_txt` | Tests xlsx → txt fallback without openpyxl |
| `test_pandas_available_flag` | Tests PANDAS_AVAILABLE flag exists |

---

## Supported File Formats

### Input Formats

| Format | Function | Description |
|--------|----------|-------------|
| `.txt` | `read_frequency_txt()` | Plain text frequency files |
| `.dat` | `read_frequency_txt()` | Data files (same as .txt) |
| `.csv` | `read_frequency_txt()` | Comma-separated values |
| Surface Z | `read_surface_impedance_txt()` | 3-column (f, Re, Im) |
| Impedance | `read_impedance_file()` | Generic impedance files |

### Output Formats

| Extension | Description |
|-----------|-------------|
| `.xlsx` | Excel format (requires openpyxl) |
| `.csv` | Comma-separated values |
| `.tsv` | Tab-separated values |
| `.txt` | Plain text (tab-separated) |
| `.dat` | Data file (tab-separated) |

---

## Standard Labels

The module provides standard labels for common impedance types:

```python
STANDARD_LABELS = {
    'ZLong': 'Longitudinal Impedance',
    'ZTrans': 'Transverse Impedance',
    'ZDipX': 'Dipolar X Impedance',
    'ZDipY': 'Dipolar Y Impedance',
    'ZQuadX': 'Quadrupolar X Impedance',
    'ZQuadY': 'Quadrupolar Y Impedance',
    'ZLongSurf': 'Longitudinal Surface Impedance',
    'ZTransSurf': 'Transverse Surface Impedance',
    'ZLongDSC': 'Longitudinal Direct Space Charge',
    'ZLongISC': 'Longitudinal Indirect Space Charge',
    'ZTransDSC': 'Transverse Direct Space Charge',
    'ZTransISC': 'Transverse Indirect Space Charge',
}
```

---

## Dependency Fallbacks

The module handles missing dependencies gracefully:

| Dependency | Fallback Behavior |
|------------|-------------------|
| pandas | Use numpy-based file writing to .txt |
| openpyxl | Fall back to .txt from .xlsx |

---

## Example Usage

```python
from pytlwall import io_util
import numpy as np

# Read frequencies
freqs = io_util.read_frequency_txt('freq.txt', skipped_rows=1, unit='MHz')

# Read impedance data
f, Z = io_util.read_impedance_file('impedance.dat', skipped_rows=1)

# Export results
io_util.print_impedance_output(
    freqs=f,
    imped_dict={'ZLong': Z_long, 'ZDipX': Z_dipx},
    savedir='output/',
    savename='results.xlsx',
    use_standard_labels=True
)

# Get supported formats
formats = io_util.list_supported_formats()  # ['.csv', '.dat', '.tsv', '.txt', '.xlsx']

# Get label for key
label = io_util.get_standard_label('ZLong')  # 'Longitudinal Impedance'
```

---

[← Back to Testing Documentation](../TESTING.md)
