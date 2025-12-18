# GUI — Plot Panel

The **Plot** tab provides an overlay plot of impedance curves with a control list on the right.

---

## What the Plot Panel does

- Accepts **drag & drop** of impedances from the chambers tree.
- Overlays multiple curves on the same axes.
- Provides a list to toggle visibility and edit curve labels.
- Offers basic plot settings (axis labels and scales).
- Exports the plot to image.

---

## Drag & drop

Drop an impedance component (e.g. `ZLongRe`) or a base impedance (e.g. `ZLong`).

Each dropped item becomes a **PlotItem** with:

- chamber name
- impedance base name
- component (Re / Im / Abs)
- data array and frequencies
- assigned color
- editable label

---

## Overlay control

### Visibility

Each plotted item can be shown/hidden through its checkbox in the list.

### Editable labels

Each list entry is editable: you can override the legend label without changing the underlying data.

---

## Plot settings

Common settings include:

- plot title
- X/Y labels
- X/Y scale (log or linear)

**Note:** for log scale plotting, the panel uses absolute values and masks invalid points.

---

## Export

From the **File** menu:

- **Save Plot...** exports the current plot as an image file.

Plots are also exported when saving a complete **View**.
