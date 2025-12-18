# MultipleChamber Example

This example demonstrates how to calculate impedances for an entire accelerator
with multiple elements having different chamber types.

## Overview

The `MultipleChamber` class computes wall impedances for many lattice elements
and sums them to get the total accelerator impedance.

## Input Files Required

All input files should be placed in a single directory:

### 1. `apertype2.txt` - Aperture Types
One line per element, specifying the chamber type:
```
Round
Round
Oblong
Rectangular
Round
...
```

### 2. `b_L_betax_betay.txt` - Geometry and Optics
Four columns: pipe radius (m), length (m), βx, βy
```
# b[m]  L[m]  betax  betay
0.025  1.5   12.0   8.0
0.030  2.0   15.0   10.0
0.020  1.0   10.0   6.0
...
```

### 3. Configuration Files (*.cfg)
One `.cfg` file for each aperture type (case-insensitive matching):
- `Round.cfg` for "Round" elements
- `Oblong.cfg` for "Oblong" elements
- `Rectangular.cfg` for "Rectangular" elements
- `Diamond.cfg` for "Diamond" elements

Each `.cfg` file should contain the full chamber configuration (layers, boundary, frequencies, beam).

## Usage

### Command Line
```bash
cd examples
python example_multiple_chamber.py
```

### Python API
```python
from pytlwall import MultipleChamber

mc = MultipleChamber(
    apertype_file="apertype2.txt",
    geom_file="b_L_betax_betay.txt",
    input_dir="./ex_multiple/",
    out_dir="./output_multiple/"
)
mc.run()
```

### GUI
1. Open PyTlWall GUI
2. File → Load Accelerator...
3. Select input directory and files
4. Click "Load Accelerator"

## Output

The calculation produces:

```
output/
├── chamber001/
│   ├── impedance.xlsx    # All impedances for element 1
│   ├── ZLong.png         # Longitudinal impedance plot
│   ├── ZTrans.png        # Transverse impedance plot
│   └── ...
├── chamber002/
│   └── ...
├── ...
└── total/
    ├── total_impedance.xlsx  # Summed impedances
    ├── ZLong_tot.png
    └── ...
```

## Custom Aperture Type Mapping

You can define custom mappings:

```python
custom_map = {
    "MyType": "my_chamber.cfg",
    "AnotherType": "another.cfg",
}

mc = MultipleChamber(
    apertype_file="apertype2.txt",
    geom_file="geometry.txt",
    input_dir="./input/",
    out_dir="./output/",
    apertype_to_cfg=custom_map,
)
```

## Notes

- All elements use the same frequency grid (from the first element's config)
- Geometry values from `b_L_betax_betay.txt` override values in `.cfg` files
- Plots are only generated for non-trivial (non-zero) impedances
