# GUI — Data Panel

The **Data** tab provides a table for collecting and exporting impedance results.

---

## What the Data Panel does

- Accepts **drag & drop** from the chambers impedance tree.
- Builds a table with:
  - a frequency column
  - one or more impedance columns (Re / Im / Abs)
- Allows column and title customization.
- Exports the table to file.

---

## Drag & drop

You can drop either:

- a **base impedance** (e.g. `ZLong`) → typically adds *both* components (Re/Im)
- a **single component** (e.g. `ZLongRe`) → adds only that component

The drop emits a request to the main window, which resolves the data arrays and updates the panel.

---

## Table editing

### Title

The title is editable (inline). By default it includes the current date.

### Column naming

- Double-click a header to rename a column.
- A custom name is stored per column (without changing the underlying source).

### Context menu

The table provides a context menu for common operations (depending on selection), such as:

- removing selected columns
- exporting
- renaming (column or frequency column)

(Exact items may evolve; see implementation for the current list.)

---

## Export

From the **File** menu you can use **Save Data...** to export the current table.

The saved file is also used when saving a complete **View**.
