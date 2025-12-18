# Installation Guide

**PyTlWall – Installation Instructions**

PyTlWall is a Python package for transmission-line wall impedance calculations.
It can be used:

* from **Python scripts**,
* from the **command line**,
* optionally through a **graphical user interface (GUI)**.

👉 **The GUI is optional**. All numerical features of PyTlWall work without any graphical components.

---

## Requirements

### Python

| Component | Minimum | Recommended |
| --------- | ------- | ----------- |
| Python    | 3.9     | 3.11–3.12   |

### Core dependencies (always required)

These dependencies are needed for any use of PyTlWall:

* `numpy >= 1.20`
* `scipy >= 1.7`
* `matplotlib >= 3.5`
* `openpyxl >= 3.0`

They are installed automatically when installing PyTlWall.

### Optional dependencies

| Package          | Purpose                        |
| ---------------- | ------------------------------ |
| PyQt5 or PySide6 | Graphical user interface (GUI) |
| pytest           | Test suite                     |
| pandas           | Data analysis utilities        |

---

## Standard Installation (no GUI)

This is the **recommended installation** for most users.

### From source

```bash
git clone https://github.com/CERN/pytlwall.git
cd pytlwall
pip install .
```

This installs the **core PyTlWall package only**, without any graphical interface.

### Verifying the installation

```python
import pytlwall
print(pytlwall.__version__)
```

---

## Optional: Graphical User Interface (GUI)

The PyTlWall GUI provides an interactive interface to configure inputs and run calculations.

⚠️ **The GUI is optional**.
If the required Qt libraries are not installed, PyTlWall will still work perfectly in:

* batch mode,
* command-line usage,
* Python scripts.

### Install GUI dependencies (recommended method)

```bash
pip install pyqt5
```

Alternatively, you may use PySide6:

```bash
pip install pyside6
```

### Optional pip extras (advanced users)

If PyTlWall is installed from source, GUI dependencies can also be installed using *pip extras*:

```bash
pip install ".[gui]"
```

This command installs PyTlWall together with the optional dependency group `gui`.
If you are not familiar with pip extras, simply install `pyqt5` manually as shown above.

### Launching the GUI

You can start the GUI in any of the following ways:

```bash
# Recommended (module entry point)
python -m pytlwall_gui
```

```bash
# Repository helper script
python run_gui.py
```

```bash
# If installed with a console entry point (when available)
pytlwall-gui
```

---

## Development Installation

For developers and contributors:

```bash
git clone https://github.com/CERN/pytlwall.git
cd pytlwall
pip install -e ".[dev]"
```

This installs PyTlWall in editable mode together with development tools.

---

## Conda Installation

```bash
conda create -n pytlwall python=3.12
conda activate pytlwall
conda install numpy scipy matplotlib openpyxl
pip install .
```

GUI dependencies (optional):

```bash
pip install pyqt5
```

---

## Running PyTlWall

### Command line

```bash
python -m pytlwall config.cfg
```

### Python script

```python
from pytlwall import CfgIo

cfg = CfgIo('config.cfg')
wall = cfg.read_pytlwall()
wall.calc_ZLong()
wall.calc_ZTrans()
```

### Graphical interface (optional)

```bash
python -m pytlwall_gui
```

---

## Troubleshooting

### GUI does not start

```bash
pip install pyqt5
python -c "from PyQt5.QtWidgets import QApplication; print('PyQt5 OK')"
```

### Headless systems (no display)

```bash
export MPLBACKEND=Agg
```

---

## Uninstallation

```bash
pip uninstall pytlwall
```

---

## Authors

* Tatiana Rijoff
* Carlo Zannini (CERN)

---

*Last updated: December 2025*
