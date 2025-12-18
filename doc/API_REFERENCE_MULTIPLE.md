# 📄 **API_REFERENCE_MULTIPLE.md**

````md
# MultipleChamber API Reference

## Overview

The `multiple_chamber` module provides the `MultipleChamber` class to perform **lattice-level impedance calculations** using the PyTLWall transmission line model. It:

- reads aperture types and geometry/optics from text files  
- maps each aperture type to a chamber configuration (`*.cfg`)  
- builds a `TlWall` instance per element  
- computes longitudinal and transverse impedances  
- exports per-element and total impedance data  
- generates plots for all non-trivial impedances.

---

## Table of Contents

- [MultipleChamber Class](#multiplechamber-class)
- [Constructor](#constructor)
- [Attributes](#attributes)
- [Methods](#methods)
- [File Formats](#file-formats)
- [Directory Structure](#directory-structure)
- [Examples](#examples)
- [Notes](#notes)

---

## MultipleChamber Class

```python
class MultipleChamber:
    """
    Multiple-chamber impedance calculator for accelerator lattices.
    """
````

Coordinates the entire multi-element impedance workflow.

---

## Constructor

```python
MultipleChamber(
    apertype_file: str | Path,
    geom_file: str | Path,
    input_dir: str | Path = ".",
    out_dir: str | Path = "output",
    apertype_to_cfg: Optional[Dict[str, str]] = None,
)
```

### Parameters

| Name              | Type      | Default    | Description                                                         |
| ----------------- | --------- | ---------- | ------------------------------------------------------------------- |
| `apertype_file`   | str/Path  | —          | Aperture type list file; resolved inside `input_dir` if relative.   |
| `geom_file`       | str/Path  | —          | Geometry/optics list file; resolved inside `input_dir` if relative. |
| `input_dir`       | str/Path  | `"."`      | Directory containing all input files including `.cfg`.              |
| `out_dir`         | str/Path  | `"output"` | Base directory for generated outputs.                               |
| `apertype_to_cfg` | dict/None | None       | Optional map aperture→cfg (case-insensitive).                       |

### Default Mapping

```python
{
    "Oblong": "Oblong.cfg",
    "Rectangular": "Rectangular.cfg",
    "Round": "Round.cfg",
    "Diamond": "Diamond.cfg",
}
```

Matching is case-insensitive for both keys and filenames.

---

## Attributes

### `input_dir : Path`

Absolute path of the directory containing input files.

### `out_dir : Path`

Absolute output directory for all results.

### `apertype_file : Path`

Resolved path to the aperture list file.

### `geom_file : Path`

Resolved path to the geometry list file.

### `apertype_to_cfg : Dict[str, str]`

Mapping of aperture types to `.cfg` templates (lowercased internally).

### `apertypes : List[str]`

Aperture type string for each lattice element.

### `b_list, L_list, betax_list, betay_list`

Lists of geometry/optics values read from `geom_file`.

### `_freq_obj_ref : Optional[Frequencies]`

Internal reference to the **shared** frequency grid (taken from first element).

---

## Methods

### `run()`

```python
def run(self) -> None:
    """
    Execute the multi-chamber impedance calculation.
    """
```

Performs the complete workflow:

1. Loads aperture, geometry, optics
2. Builds `TlWall` objects for all elements
3. Computes all impedances
4. Saves per-element impedance data (Excel)
5. Generates plots for non-zero impedances
6. Sums impedances and writes total results.

---

### `_load_input_data()`

Loads and validates:

* `apertypes`
* `b_list`
* `L_list`
* `betax_list`
* `betay_list`

Ensures identical list lengths.

---

### `_get_cfg_path_for_apertype(apertype)`

Resolves aperture type → appropriate `.cfg` file:

* normalizes to lowercase
* looks up in the mapping
* searches in `input_dir` case-insensitively

Raises `KeyError` or `FileNotFoundError` on mismatch.

---

### `_get_cfg_handler(apertype)`

Creates or retrieves a cached `CfgIo` instance for the given aperture type.

---

### `_build_wall_for_element(...)`

```python
def _build_wall_for_element(
    apertype, b, L, betax, betay,
    freq_override: Optional[Frequencies] = None
) -> TlWall:
```

Builds a `TlWall` instance for one element:

* reads chamber/beam/frequencies from `.cfg`
* overrides geometry (`b`, `L`) and optics (`betax`, `betay`)
* uses `freq_override` if provided (enforced common frequency grid)

Raises `RuntimeError` if configuration is incomplete.

---

### `_save_element_impedance(...)`

Writes per-element results:

* directory: `out_dir/chamberXXX/`
* file: `impedance.xlsx`
* generates plots for non-trivial impedances using `plot_util.plot_Z_vs_f_simple()`.

Plot naming scheme:

* `ZLong.png`
* `ZTrans.png`
* `ZDipX.png`, `ZDipY.png`
* `ZQuadX.png`, `ZQuadY.png`
* etc.

---

### `_save_total_impedance(...)`

Creates `out_dir/total/` and writes:

* `total_impedance.xlsx`
* `<name>_tot.png` plots for all summed impedances.

---

## File Formats

### Aperture Type File (`apertype2.txt`)

```
Oblong
Rectangular
Round
Diamond
...
```

One line per lattice element.

---

### Geometry File (`b_L_betax_betay.txt`)

Format:

```
b     L       betax    betay
0.04  0.419   5.8405   4.425
0.02  1.126   5.7071   4.2467
...
```

Number of rows must match the aperture file.

---

## Directory Structure

Output after running:

```
output/
    chamber001/
        impedance.xlsx
        ZLong.png
        ZTrans.png
        ...
    chamber002/
        impedance.xlsx
        ...
    ...
    total/
        total_impedance.xlsx
        ZLong_tot.png
        ZTrans_tot.png
        ...
```

---

## Examples

### Basic Usage

```python
from pytlwall import MultipleChamber

mc = MultipleChamber(
    apertype_file="apertype2.txt",
    geom_file="b_L_betax_betay.txt",
    input_dir="./examples/ex_multiple/",
    out_dir="output"
)
mc.run()
```

---

### Custom Mapping

```python
custom_map = {
    "Oblong": "oblong_custom.cfg",
    "Rectangular": "RECTANGULAR.CFG",
}

mc = MultipleChamber(
    "apertype2.txt",
    "b_L_betax_betay.txt",
    input_dir="examples/ex_multiple/",
    out_dir="output_custom",
    apertype_to_cfg=custom_map
)
mc.run()
```

---

### Inspecting Data After Run

```python
print(len(mc.apertypes))
print(mc.apertypes[:5])
print(mc.b_list[:5])
print(mc.L_list[:5])
```

---

## Notes

* Aperture and geometry files must have identical lengths.
* Only non-zero/non-NaN impedances produce plots.
* The frequency grid is taken from the first element and reused for all.
* The `total/` directory contains the summed impedances for full-lattice analysis.

