"""I/O utilities for the pytlwall package.

This module groups file import/export helpers used by the GUI and by
the library tests.

Notes:
- Text-based formats are tab-separated to keep a consistent, easy-to-parse
  structure across .txt/.dat/.csv exports.
- Optional dependencies:
    * pandas: used for convenient DataFrame-based export when available.
    * openpyxl: required to write .xlsx files via pandas.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Tuple

import numpy as np

try:
    import pandas as pd  # type: ignore
    PANDAS_AVAILABLE = True
except Exception:  # pragma: no cover
    pd = None  # type: ignore
    PANDAS_AVAILABLE = False

try:
    import openpyxl  # noqa: F401  # type: ignore
    OPENPYXL_AVAILABLE = True
except Exception:  # pragma: no cover
    OPENPYXL_AVAILABLE = False


_SUPPORTED_FORMATS = (".csv", ".txt", ".dat", ".xlsx")


_STANDARD_LABELS: Mapping[str, str] = {
    "ZLong": "Longitudinal Impedance",
    "ZTrans": "Transverse Impedance",
    "ZDipX": "Dipolar X Impedance",
    "ZDipY": "Dipolar Y Impedance",
    "ZQuadX": "Quadrupolar X Impedance",
    "ZQuadY": "Quadrupolar Y Impedance",
}


def list_supported_formats() -> List[str]:
    """Return the list of supported export file extensions."""
    return list(_SUPPORTED_FORMATS)


def get_standard_label(key: str) -> str:
    """Return a human-readable standard label for a known impedance key."""
    return _STANDARD_LABELS.get(key, key)


def _unit_scale(unit: str | None) -> float:
    """Return a multiplicative scale factor for a frequency unit."""
    if unit is None:
        return 1.0

    unit_norm = unit.strip().lower()
    scales = {
        "hz": 1.0,
        "khz": 1.0e3,
        "mhz": 1.0e6,
        "ghz": 1.0e9,
    }
    if unit_norm not in scales:
        raise ValueError(f"Unsupported unit: {unit}")
    return scales[unit_norm]


def read_frequency_txt(
    filepath: str | Path,
    *,
    separator: str | None = None,
    column: int = 0,
    skipped_rows: int = 0,
    unit: str | None = None,
) -> np.ndarray:
    """Read a frequency vector from a text/CSV-like file.

    Args:
        filepath: Input file.
        separator: Column separator. If None, any whitespace is used.
        column: 0-based column index containing the frequency values.
        skipped_rows: Number of header rows to skip.
        unit: Optional unit conversion for the read values (Hz/kHz/MHz/GHz).

    Returns:
        1D numpy array of frequencies in Hz.
    """
    data = np.loadtxt(
        Path(filepath),
        delimiter=separator,
        skiprows=skipped_rows,
        ndmin=2,
    )
    if data.size == 0:
        return np.array([], dtype=float)

    if column < 0 or column >= data.shape[1]:
        raise ValueError(f"Invalid column index {column} for file with {data.shape[1]} columns.")

    freqs = np.asarray(data[:, column], dtype=float)
    return freqs * _unit_scale(unit)


def read_surface_impedance_txt(
    filepath: str | Path,
    *,
    separator: str | None = None,
    skipped_rows: int = 0,
    unit: str | None = None,
    freq_column: int = 0,
    re_column: int = 1,
    im_column: int = 2,
) -> Tuple[np.ndarray, np.ndarray]:
    """Read surface impedance file.

    Expected columns: f, Re(Zs), Im(Zs)

    Returns:
        (freqs, Zs) where Zs is a complex numpy array.
    """
    data = np.loadtxt(
        Path(filepath),
        delimiter=separator,
        skiprows=skipped_rows,
        ndmin=2,
    )
    freqs = np.asarray(data[:, freq_column], dtype=float) * _unit_scale(unit)
    re_ = np.asarray(data[:, re_column], dtype=float)
    im_ = np.asarray(data[:, im_column], dtype=float)
    return freqs, re_ + 1j * im_


def read_impedance_file(
    filepath: str | Path,
    *,
    separator: str | None = "\t",
    skipped_rows: int = 0,
    freq_column: int = 0,
    re_column: int = 1,
    im_column: int = 2,
    unit: str | None = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Read a generic impedance file with columns (f, Re(Z), Im(Z))."""
    data = np.loadtxt(
        Path(filepath),
        delimiter=separator if separator is not None else None,
        skiprows=skipped_rows,
        ndmin=2,
    )
    freqs = np.asarray(data[:, freq_column], dtype=float) * _unit_scale(unit)
    re_ = np.asarray(data[:, re_column], dtype=float)
    im_ = np.asarray(data[:, im_column], dtype=float)
    return freqs, re_ + 1j * im_


def load_apertype(filepath: str | Path) -> List[str]:
    """Load a list of aperture type strings from a file (one per line)."""
    types: List[str] = []
    with open(Path(filepath), "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if s:
                types.append(s)
    return types


def load_b_L(filepath: str | Path) -> Tuple[np.ndarray, np.ndarray]:
    """Load circular geometry as (b, L)."""
    data = np.loadtxt(Path(filepath), ndmin=2)
    return np.asarray(data[:, 0], dtype=float), np.asarray(data[:, 1], dtype=float)


def load_b_L_betax_betay(filepath: str | Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load circular geometry with beta functions as (b, L, betax, betay)."""
    data = np.loadtxt(Path(filepath), ndmin=2)
    return (
        np.asarray(data[:, 0], dtype=float),
        np.asarray(data[:, 1], dtype=float),
        np.asarray(data[:, 2], dtype=float),
        np.asarray(data[:, 3], dtype=float),
    )


def load_x_y_L_betax_betay(filepath: str | Path) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Load rectangular geometry with beta functions as (x, y, L, betax, betay)."""
    data = np.loadtxt(Path(filepath), ndmin=2)
    return (
        np.asarray(data[:, 0], dtype=float),
        np.asarray(data[:, 1], dtype=float),
        np.asarray(data[:, 2], dtype=float),
        np.asarray(data[:, 3], dtype=float),
        np.asarray(data[:, 4], dtype=float),
    )


def _validate_export_inputs(freqs: np.ndarray, imped_dict: Mapping[str, np.ndarray]) -> None:
    """Validate export inputs for impedance output functions."""
    freqs = np.asarray(freqs).reshape(-1)
    if freqs.size == 0:
        raise ValueError("freqs is empty.")

    if not imped_dict:
        raise ValueError("imped_dict is empty.")

    n = freqs.size
    for key, arr in imped_dict.items():
        arr = np.asarray(arr).reshape(-1)
        if arr.size != n:
            raise ValueError(f"Length mismatch for '{key}': freqs={n}, Z={arr.size}")


def _build_table(
    freqs: np.ndarray,
    imped_dict: Mapping[str, np.ndarray],
    *,
    use_standard_labels: bool = False,
) -> Tuple[List[str], np.ndarray]:
    """Build header and 2D numeric table for export."""
    header: List[str] = ["f [Hz]"]
    cols: List[np.ndarray] = [np.asarray(freqs).reshape(-1)]

    for key in imped_dict.keys():
        label = get_standard_label(key) if use_standard_labels else key
        header.append(f"Re({label})")
        header.append(f"Im({label})")

        z = np.asarray(imped_dict[key]).reshape(-1)
        cols.append(np.real(z))
        cols.append(np.imag(z))

    data = np.column_stack(cols)
    return header, data


def print_impedance_output(
    *,
    freqs: np.ndarray,
    imped_dict: Mapping[str, np.ndarray],
    savedir: str | Path,
    savename: str,
    use_standard_labels: bool = False,
    save_csv_fallback: bool = False,
) -> Path:
    """Export impedance data to a file.

    Args:
        freqs: Frequency vector.
        imped_dict: Mapping from impedance name to complex vector.
        savedir: Output directory.
        savename: Output filename (extension selects the format).
        use_standard_labels: Use standard impedance labels in headers.
        save_csv_fallback: If True, .xlsx export falls back to a text format
            when openpyxl is unavailable.

    Returns:
        Path to the written file.
    """
    _validate_export_inputs(freqs, imped_dict)

    out_dir = Path(savedir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    out_path = out_dir / savename
    ext = out_path.suffix.lower()
    if ext not in _SUPPORTED_FORMATS:
        raise ValueError(f"Unsupported extension: {ext}")

    # Handle xlsx dependency/fallback.
    if ext == ".xlsx" and not OPENPYXL_AVAILABLE:
        if not save_csv_fallback:
            raise ValueError("openpyxl is required for .xlsx export.")
        out_path = out_path.with_suffix(".txt")
        ext = ".txt"

    header, data = _build_table(freqs, imped_dict, use_standard_labels=use_standard_labels)

    if ext == ".xlsx":
        if not PANDAS_AVAILABLE:
            raise ValueError("pandas is required for .xlsx export.")
        df = pd.DataFrame(data, columns=header)  # type: ignore[name-defined]
        df.to_excel(out_path, index=False)
        return out_path

    # Text-like exports: tab-separated, single header line.
    header_line = "\t".join(header)
    np.savetxt(out_path, data, delimiter="\t", header=header_line, comments="")
    return out_path


def print_single_impedance(
    *,
    freqs: np.ndarray,
    impedance: np.ndarray,
    savedir: str | Path,
    savename: str,
    label: str = "Z",
    use_standard_labels: bool = False,
) -> Path:
    """Convenience wrapper to export a single impedance."""
    return print_impedance_output(
        freqs=freqs,
        imped_dict={label: impedance},
        savedir=savedir,
        savename=savename,
        use_standard_labels=use_standard_labels,
    )


def export_impedance(
    *,
    freqs: np.ndarray,
    imped_dict: Mapping[str, np.ndarray],
    output_path: str | Path,
    use_standard_labels: bool = False,
    save_csv_fallback: bool = False,
) -> Path:
    """Alternative interface that takes a full output path."""
    output_path = Path(output_path)
    return print_impedance_output(
        freqs=freqs,
        imped_dict=imped_dict,
        savedir=output_path.parent,
        savename=output_path.name,
        use_standard_labels=use_standard_labels,
        save_csv_fallback=save_csv_fallback,
    )


# ----------------------------------------------------------------------
# New functionality: chamber impedance split export
# ----------------------------------------------------------------------


def save_chamber_impedance(
    output_dir: str | Path,
    impedance_freq: np.ndarray,
    impedance_results: Dict[str, np.ndarray],
) -> List[Path]:
    """Save all available chamber impedance results to text files.

    The function writes one file per *base* impedance name, where the base name
    is obtained by stripping the trailing 'Re'/'Im' suffix from keys.

    Required files:
        - ZLong.txt with columns: f, ZLongRe, ZLongIm
        - ZTrans.txt with columns: f, ZTransRe, ZTransIm

    For any additional impedances present in the results dictionary, a file
    '<BaseName>.txt' is created with columns: f, <BaseName>Re, <BaseName>Im.

    Args:
        output_dir: Destination folder.
        impedance_freq: Frequency array (same length as impedance arrays).
        impedance_results: Mapping from impedance component name to array,
            e.g. {'ZLongRe': ..., 'ZLongIm': ..., 'ZTransRe': ..., ...}.

    Returns:
        A list of paths for the files that were written.

    Raises:
        ValueError: If mandatory impedance components are missing or
            array sizes are inconsistent.
    """
    out_path = Path(output_dir).expanduser().resolve()
    out_path.mkdir(parents=True, exist_ok=True)

    freq = np.asarray(impedance_freq).reshape(-1)
    if freq.size == 0:
        raise ValueError("impedance_freq is empty.")

    bases = _collect_impedance_bases(impedance_results)
    _validate_mandatory_impedances(impedance_results, bases)

    written: List[Path] = []
    for base in sorted(bases):
        re_key = f"{base}Re"
        im_key = f"{base}Im"

        if re_key not in impedance_results or im_key not in impedance_results:
            # Skip incomplete entries; mandatory ones are validated above.
            continue

        re_arr = np.asarray(impedance_results[re_key]).reshape(-1)
        im_arr = np.asarray(impedance_results[im_key]).reshape(-1)

        _validate_sizes(freq, re_arr, im_arr, base)

        file_path = out_path / f"{base}.txt"
        _write_impedance_file(
            file_path=file_path,
            freq=freq,
            re_arr=re_arr,
            im_arr=im_arr,
            re_name=re_key,
            im_name=im_key,
        )
        written.append(file_path)

    return written

def save_impedances_to_excel(
    *,
    freqs: np.ndarray,
    imped_dict: Mapping[str, np.ndarray],
    output_path: str | Path,
    use_standard_labels: bool = False,
    save_csv_fallback: bool = True,
) -> Path:
    """Save impedances to an Excel file (or a safe fallback).

    This function is kept for backward compatibility with older scripts that
    expect an explicit ``save_impedances_to_excel`` helper. Internally it uses
    :func:`export_impedance` / :func:`print_impedance_output` and supports a
    graceful fallback to a text format when Excel dependencies are missing.
    """
    output_path = Path(output_path)
    if output_path.suffix == "":
        output_path = output_path.with_suffix(".xlsx")

    return export_impedance(
        freqs=freqs,
        imped_dict=imped_dict,
        output_path=output_path,
        use_standard_labels=use_standard_labels,
        save_csv_fallback=save_csv_fallback,
    )

def _collect_impedance_bases(impedance_results: Dict[str, np.ndarray]) -> Iterable[str]:
    """Collect base names from impedance results keys."""
    bases: set[str] = set()
    for key in impedance_results.keys():
        if key.endswith("Re") and len(key) > 2:
            bases.add(key[:-2])
        elif key.endswith("Im") and len(key) > 2:
            bases.add(key[:-2])
    return bases


def _validate_mandatory_impedances(
    impedance_results: Dict[str, np.ndarray],
    bases: Iterable[str],
) -> None:
    """Ensure the mandatory impedances are available."""
    bases_set = set(bases)
    missing: List[str] = []

    for base in ("ZLong", "ZTrans"):
        if base not in bases_set:
            missing.append(base)
            continue
        if f"{base}Re" not in impedance_results:
            missing.append(f"{base}Re")
        if f"{base}Im" not in impedance_results:
            missing.append(f"{base}Im")

    if missing:
        raise ValueError("Missing mandatory impedance data: " + ", ".join(missing))


def _validate_sizes(freq: np.ndarray, re_arr: np.ndarray, im_arr: np.ndarray, base: str) -> None:
    """Validate that arrays have consistent sizes."""
    n = freq.size
    if re_arr.size != n or im_arr.size != n:
        raise ValueError(
            f"Size mismatch for {base}: f={n}, Re={re_arr.size}, Im={im_arr.size}"
        )


def _write_impedance_file(
    file_path: Path,
    freq: np.ndarray,
    re_arr: np.ndarray,
    im_arr: np.ndarray,
    re_name: str,
    im_name: str,
) -> None:
    """Write a single impedance file with a header and tab-separated columns."""
    data = np.column_stack((freq, re_arr, im_arr))
    header = f"f\t{re_name}\t{im_name}"
    np.savetxt(file_path, data, header=header, comments="", delimiter="\t")
