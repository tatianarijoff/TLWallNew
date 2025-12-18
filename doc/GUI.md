# PyTlWall GUI Documentation

**Qt-based configuration editor and impedance visualizer**

This section documents the graphical interface shipped with PyTlWall.  
The GUI is designed to:

- configure one or more chambers through the same `.cfg` structure used by the CLI
- compute selected impedances
- inspect results as tables and overlay plots
- export configurations, impedances, plots, and complete workspaces (“Views”)

---

## Table of Contents

- [Getting Started](#getting-started)
- [Main Window Layout](#main-window-layout)
- [Sidebar](GUI_SIDEBAR.md)
- [Central Panel](#central-panel)
  - [Data Panel](GUI_DATA_PANEL.md)
  - [Plot Panel](GUI_PLOT_PANEL.md)
- [Menu Bar and Actions](GUI_MENU_BAR.md)
- [Saving and Loading Views](GUI_VIEW_IO.md)
- [Tips and Troubleshooting](#tips-and-troubleshooting)

---

## Getting Started

### Launch

From the package entry points (depending on your installation):

```bash
# Launch from the main package (if provided)
python -m pytlwall --gui

# Or launch the GUI module directly (as in README)
python -m QT_interface
```

If the GUI does not start, ensure the GUI dependencies are installed:

```bash
pip install pyqt5 matplotlib
```

---

## Main Window Layout

The main window is split into two areas:

- **Sidebar** (left): chamber tree + configuration editor
- **Central Panel** (right): results in **Data** and **Plot** tabs

This split is resizable via a splitter and the sidebar lists multiple chambers.

See: [Sidebar](GUI_SIDEBAR.md).

---

## Central Panel

The central panel has two tabs:

- **Data**: a table where you can collect multiple impedance components (and export them)
- **Plot**: an overlay plot view with a list of plotted items, visibility toggles, and plot settings

### Typical workflow

1. Create one or more chambers.
2. Configure geometry, layers, boundary, frequency definition, and beam.
3. Choose which impedances to compute.
4. Run **Calculate**.
5. Drag impedances from the chamber tree into:
   - **Data** to build custom tables
   - **Plot** to overlay curves
6. Export results or save the whole workspace as a **View**.

---

## Tips and Troubleshooting

- **Mandatory impedances:** `ZLong` and `ZTrans` are always enabled.
- **Drag & drop:** you can drag an impedance “base” (e.g. `ZLong`) or a component (e.g. `ZLongRe`).
- **Log scales:** when plotting in log scale, absolute values are used and non-positive points are masked.
- **Documentation in Help menu:** after running `build_doc`, HTML pages are expected in `doc/html/`.

If you need the exact meaning of any button or setting, see the dedicated pages for each panel and menu.
