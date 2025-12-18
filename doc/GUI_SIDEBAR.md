# GUI — Sidebar

The sidebar is the left panel of the main window and provides two tabs:

- **Chambers**: manage chambers and select outputs (impedances)
- **Chamber Info**: edit the configuration parameters for the selected chamber

---

## Chambers Tab

### Add / remove chambers

- **Add chamber**: creates a new chamber with default values.
- **[Remove chamber]** (in the tree): removes the selected chamber and renumbers the remaining ones.

### Chamber tree structure

Each chamber shows a subtree of impedances:

- Parent impedance (e.g. `ZLong`, `ZTrans`, `ZDip`, …)
- Child components:
  - `...Re` (real part)
  - `...Im` (imaginary part)

#### Mandatory impedances

`ZLong` and `ZTrans` are mandatory and always enabled.

### Drag & drop format (advanced)

Dragging from the tree provides MIME data in the form:

```
chamber_name|impedance_name
```

Examples:

- `Chamber 1|ZLongRe`
- `Chamber 1|ZLong`  (means “base impedance”, used to add both components)

This is used by the Data and Plot panels.

---

## Chamber Info Tab

This tab edits the same information stored in a `.cfg` file, organized in collapsible sections:

- `[base_info]`
  - `component_name`
  - `chamber_shape` (CIRCULAR / ELLIPTICAL / RECTANGULAR)
  - geometry parameters (radius or horizontal/vertical semi-axes, length)
  - beta functions (`betax`, `betay`)
- `[layers_info]` and individual `[layerN]` sections
  - add/remove layers, edit thickness and material parameters
- `[boundary]`
  - boundary type and related parameters
- `[frequency_info]`
  - frequency range mode (log range) or file input mode
- `[beam_info]`
  - relativistic gamma, test beam shift, and particle mass

The GUI updates visibility of geometry fields based on the selected chamber shape.

---

## Notes

- The chamber selector (combo box) on top selects the active chamber.
- When you calculate impedances, the tree labels can display sample counts (e.g. `ZLong (N)`).
