# EXAMPLES_MULTIPLE.md

![PyTlWall Logo](logo005.png)

**Multiple-Chamber Impedance Calculation Using Lattice Aperture and Geometry Files**

## Authors

- **Tatiana Rijoff** – tatiana.rijoff@gmail.com  
- **Carlo Zannini** – carlo.zannini@cern.ch  

*Copyright: CERN*

---

## Navigation

**[◀ Back to Examples](EXAMPLES.md)**

| Module | Link |
|--------|------|
| beam | [EXAMPLES_BEAM.md](EXAMPLES_BEAM.md) |
| frequencies | [EXAMPLES_FREQUENCIES.md](EXAMPLES_FREQUENCIES.md) |
| layer | [EXAMPLES_LAYER.md](EXAMPLES_LAYER.md) |
| chamber | [EXAMPLES_CHAMBER.md](EXAMPLES_CHAMBER.md) |
| tlwall | [EXAMPLES_TLWALL.md](EXAMPLES_TLWALL.md) |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |
| **multiple** | *You are here* |

---

## Table of Contents

- [Overview](#overview)
- [Input Files](#input-files)
- [Example 1: Running MultipleChamber](#example-1-running-multiplechamber)
- [Example 2: Directory Structure of the Output](#example-2-directory-structure-of-the-output)
- [Example 3: Per-Chamber Impedance Files](#example-3-per-chamber-impedance-files)
- [Example 4: Automatic Impedance Plots](#example-4-automatic-impedance-plots)
- [Example 5: Total Impedance Summation](#example-5-total-impedance-summation)
- [Example 6: Case-Insensitive Mapping](#example-6-case-insensitive-mapping)
- [Example 7: Common Frequency Grid](#example-7-common-frequency-grid)
- [Notes and Best Practices](#notes-and-best-practices)

---

## Overview

The `MultipleChamber` class performs a **fully automated impedance calculation** for an accelerator lattice, using:

- a list of **aperture types** (`apertype2.txt`)
- a list of **geometrical and optical parameters** (`b_L_betax_betay.txt`)
- chamber **configuration templates** (`*.cfg`)

For each lattice element:

1. The correct chamber geometry is selected  
2. Element-specific parameters (radius, length, betax, betay) are applied  
3. A `TlWall` object is instantiated  
4. Longitudinal and transverse impedances are computed  
5. Impedances are saved in a dedicated directory  
6. Non-zero impedances are automatically plotted  

After processing all elements, the **total impedance** is computed and plotted.

---

## Input Files

### 1. Aperture Type File — `apertype2.txt`

Each line corresponds to one lattice element:

```
Oblong
Rectangular
Oblong
Round
Diamond
...
```

---

### 2. Geometry and Optics File — `b_L_betax_betay.txt`

Each line contains:

```
b   L   betax   betay
```

Example:

```
0.04   0.419   5.8405   4.425
0.02   1.126   5.7071   4.2467
...
```

| Column | Meaning |
|--------|---------|
| **b** | Pipe radius / half-height |
| **L** | Element length (m) |
| **betax** | Horizontal beta function |
| **betay** | Vertical beta function |

---

### 3. Chamber Configuration Templates

The directory must include the `.cfg` files defining each chamber type:

```
Oblong.cfg
Rectangular.cfg
Round.cfg
Diamond.cfg
```

Names are matched **case-insensitively**, both as dictionary keys and as filenames.

---

## Example 1: Running MultipleChamber

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

Key features:

- All files are read from `input_dir`
- Configuration files are matched ignoring case
- Frequencies of the *first* element define the frequency grid for all others
- Automatically generates per-chamber directories
- Automatically generates plots for non-zero impedances

---

## Example 2: Directory Structure of the Output

After running the example:

```
output/
    chamber001/
        impedance.xlsx
        ZLong.png
        ZTrans.png
        ...
    chamber002/
        impedance.xlsx
        ZLong.png
        ZTrans.png
        ...
    ...
    chamber211/
        impedance.xlsx
        ...
    total/
        total_impedance.xlsx
        ZLong_tot.png
        ZTrans_tot.png
        ...
```

Notes:

- One directory per lattice element  
- Only non-zero impedances produce plots  
- The total directory contains summed impedances and their plots  

---

## Example 3: Per-Chamber Impedance Files

Each file `impedance.xlsx` contains:

| Column | Description |
|--------|-------------|
| f [Hz] | Frequency |
| ZLong real / imag | Longitudinal impedance |
| ZTrans real / imag | Transverse impedance |
| ZDipX / ZDipY | Dipolar components |
| ZQuadX / ZQuadY | Quadrupolar components |
| ZLongISC / ZTransISC | Space-charge corrections |

All impedances are exported using `io_util.export_impedance`.

---

## Example 4: Automatic Impedance Plots

Plots are generated using:

```
plot_util.plot_Z_vs_f_simple()
```

Only impedances that are **not identically zero or NaN** are plotted.

Example internal call:

```python
plot_util.plot_Z_vs_f_simple(
    f=freqs,
    Z=Z,
    imped_type="L",
    title="Chamber 001 – ZLong",
    savedir="output/chamber001",
    savename="ZLong.png",
    xscale="log",
    yscale="log",
)
```

Plots are saved inside each chamber directory with filenames like:

- `ZLong.png`
- `ZTrans.png`
- `ZDipX.png`
- …

---

## Example 5: Total Impedance Summation

After processing all chambers:

```
Z_total[name] = Σ (Z_element[name])
```

Results are saved to:

```
output/total/total_impedance.xlsx
```

Plots generated:

- `ZLong_tot.png`
- `ZTrans_tot.png`
- `ZDipX_tot.png`
- `ZQuadX_tot.png`
- …

---

## Example 6: Case-Insensitive Mapping

Mapping used:

```python
DEFAULT_APERTYPE_TO_CFG = {
    "Oblong": "Oblong.cfg",
    "Rectangular": "Rectangular.cfg",
    "Round": "Round.cfg",
    "Diamond": "Diamond.cfg",
}
```

Both:

- input strings (`oblong`, `OBLONG`, `ObLoNg`)
- filenames (`OBLONG.CFG`, `rectangular.cfg`)

are matched ignoring case.

This ensures robustness in large-scale workflows.

---

## Example 7: Common Frequency Grid

To guarantee element-by-element impedance summation:

- The frequency grid of the **first** processed element is stored
- The same `Frequencies` object is reused for all elements
- All impedance arrays have identical shapes

This ensures:

- consistent longitudinal/transverse summation  
- no frequency mismatch  
- identical interpolation-free workflow  

---

## Notes and Best Practices

- `apertype2.txt` and `b_L_betax_betay.txt` must have the **same number of lines**
- Chamber plots are only created for impedances containing meaningful data
- `.cfg` files may define different frequencies, but only the first is used
- Use the `total/` directory for cross-checks and global validation
- Ensure `input_dir` contains all `.cfg` files required by the mapping

---

**[◀ Back to Examples](EXAMPLES.md)**
