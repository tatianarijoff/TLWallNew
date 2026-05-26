# EXAMPLES_MULTIPLE.md

![PyTlWall Logo](logo005.png)

**Multiple-Chamber Impedance Calculation Using Lattice Aperture and Geometry Files**

## Authors

- **Tatiana Rijoff** — tatiana.rijoff@gmail.com  
- **Carlo Zannini** — carlo.zannini@cern.ch  

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
| tlwall_wake | [EXAMPLES_WAKE.md](EXAMPLES_WAKE.md) |
| **multiple** | *You are here* |
| logging | [EXAMPLES_LOGGING.md](EXAMPLES_LOGGING.md) |

---

## Table of Contents

- [Overview](#overview)
- [Input Files](#input-files)
- [Example 1: Basic MultipleChamber Workflow](#example-1-basic-multiplechamber-workflow)
- [Example 2: Complete Example Script](#example-2-complete-example-script)
- [Example 3: Directory Structure of the Output](#example-3-directory-structure-of-the-output)
- [Example 4: Per-Chamber Impedance Files](#example-4-per-chamber-impedance-files)
- [Example 5: Plotting Individual Elements](#example-5-plotting-individual-elements)
- [Example 6: Total Impedance Summation](#example-6-total-impedance-summation)
- [Example 7: Case-Insensitive Mapping](#example-7-case-insensitive-mapping)
- [Example 8: Common Frequency Grid](#example-8-common-frequency-grid)
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

## Example 1: Basic MultipleChamber Workflow

```python
from pytlwall import MultipleChamber

# Create MultipleChamber instance
mc = MultipleChamber(
    apertype_file="apertype2.txt",
    geom_file="b_L_betax_betay.txt",
    input_dir="./input/",
    out_dir="./output/"
)

# Step 1: Load input files (lightweight operation)
mc.load()

# Step 2: Calculate impedances for all lattice elements
mc.calculate_all()

# Step 3: Plot total accumulated impedances
mc.plot_totals(show=False)
```

Key features:

- All files are read from `input_dir`
- Configuration files are matched ignoring case
- Frequencies of the *first* element define the frequency grid for all others
- Automatically generates per-chamber directories
- Automatically generates plots for non-zero impedances

---

## Example 2: Complete Example Script

```python
#!/usr/bin/env python3
"""Multiple chamber impedance calculation example."""

from pathlib import Path
from pytlwall import MultipleChamber

def main():
    """Run the multiple chamber example workflow."""
    input_dir = Path("./examples/ex_multiple")
    output_dir = Path("./output_multiple")
    
    print("=" * 60)
    print("Multiple Chamber Impedance Calculation Example")
    print("=" * 60)
    print(f"Input directory:  {input_dir}")
    print(f"Output directory: {output_dir}")
    
    # Check required files exist
    if not input_dir.is_dir():
        raise SystemExit(f"Error: input directory not found: {input_dir}")
    
    required = ["apertype2.txt", "b_L_betax_betay.txt"]
    missing = [name for name in required if not (input_dir / name).exists()]
    if missing:
        raise SystemExit(f"Error: missing required files: {missing}")
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize MultipleChamber
    mc = MultipleChamber(
        apertype_file="apertype2.txt",
        geom_file="b_L_betax_betay.txt",
        input_dir=input_dir,
        out_dir=output_dir,
    )
    
    # Load inputs (lightweight)
    mc.load()
    
    # Perform the full calculation for all lattice elements
    mc.calculate_all()
    
    # Plot total accumulated impedances (saved under out_dir/total)
    mc.plot_totals(show=False)
    
    # Optional: plot individual elements
    if mc.n_elements > 0:
        mc.plot_element(0, show=False)
    
    print(f"\nDone. Results written to: {output_dir}")

if __name__ == "__main__":
    main()
```

---

## Example 3: Directory Structure of the Output

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

## Example 4: Per-Chamber Impedance Files

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

## Example 5: Plotting Individual Elements

To plot the impedance of a specific lattice element:

```python
from pytlwall import MultipleChamber

mc = MultipleChamber(
    apertype_file="apertype2.txt",
    geom_file="b_L_betax_betay.txt",
    input_dir="./input/",
    out_dir="./output/"
)

mc.load()
mc.calculate_all()

# Plot element 0 (first element)
mc.plot_element(0, show=False)

# Plot element 5
mc.plot_element(5, show=False)

# Plot multiple elements
for i in range(min(5, mc.n_elements)):
    mc.plot_element(i, show=False)
```

The `show=False` parameter saves plots to disk without displaying them interactively.

---

## Example 6: Total Impedance Summation

After processing all chambers:

```
Z_total[name] = Σ (Z_element[name])
```

Results are saved to:

```
output/total/total_impedance.xlsx
```

Plots generated by `mc.plot_totals()`:

- `ZLong_tot.png`
- `ZTrans_tot.png`
- `ZDipX_tot.png`
- `ZQuadX_tot.png`
- …

---

## Example 7: Case-Insensitive Mapping

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

## Example 8: Common Frequency Grid

To guarantee element-by-element impedance summation:

- The frequency grid of the **first** processed element is stored
- The same `Frequencies` object is reused for all elements
- All impedance arrays have identical shapes

This ensures:

- consistent longitudinal/transverse summation  
- no frequency mismatch  
- identical interpolation-free workflow  

---

## API Reference

### MultipleChamber Methods

| Method | Description |
|--------|-------------|
| `__init__(apertype_file, geom_file, input_dir, out_dir)` | Initialize with input file paths |
| `load()` | Load aperture types, geometry, and configuration files |
| `calculate_all()` | Calculate impedances for all lattice elements |
| `plot_totals(show=False)` | Plot total accumulated impedances |
| `plot_element(index, show=False)` | Plot impedance for a specific element |
| `n_elements` | Property: number of lattice elements |

### Workflow

```
1. __init__()     →  Set up file paths
2. load()         →  Read input files, validate data
3. calculate_all() →  Compute impedances for all elements
4. plot_totals()  →  Generate total impedance plots
5. plot_element() →  (Optional) Plot individual elements
```

---

## Notes and Best Practices

- `apertype2.txt` and `b_L_betax_betay.txt` must have the **same number of lines**
- Chamber plots are only created for impedances containing meaningful data
- `.cfg` files may define different frequencies, but only the first is used
- Use the `total/` directory for cross-checks and global validation
- Ensure `input_dir` contains all `.cfg` files required by the mapping
- Always call `load()` before `calculate_all()`
- Use `show=False` for batch processing to avoid interactive plot windows

---

**[◀ Back to Examples](EXAMPLES.md)** | **[◀ Previous: tlwall_wake](EXAMPLES_WAKE.md)** | **[Next: logging ▶](EXAMPLES_LOGGING.md)**
