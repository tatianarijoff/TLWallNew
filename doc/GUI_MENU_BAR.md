# GUI — Menu Bar and Actions

The GUI provides the following top-level menus:

- **File**
- **Chamber**
- **Help**

---

## File menu

Typical export and workspace actions:

- **Save Chamber cfg...**  
  Save the configuration of the current chamber as a `.cfg` file.

- **Save Chamber impedance...**  
  Save impedance results (text files) for the current chamber.

- **Save Chamber Complete...**  
  Save configuration + impedance files + plots for the current chamber.

- **Save All cfg...**  
  Save `.cfg` files for all chambers.

- **Save All impedances...**  
  Save impedance files for all chambers with computed data.

- **Save All Complete...**  
  Save cfg + impedance files + plots for all chambers.

- **Save Data...**  
  Export the Data table.

- **Save Plot...**  
  Export the current plot as an image.

- **Save View...**  
  Save a complete workspace (“View”): chambers, computed impedances, data table, and plot.

- **Load View...**  
  Restore a workspace previously saved as a View.

- **Exit**

---

## Chamber menu

- **New Chamber**  
  Add a new default chamber.

- **New Chamber with config...**  
  Create a chamber from an existing `.cfg` file.

- **Select All** / **Deselect All**  
  Enable/disable impedance outputs for the current chamber (mandatory ones remain enabled).

- **Calculate**  
  Run impedance computation for the selected chamber and selected outputs.

---

## Help menu

### Documentation

The Help menu opens the generated HTML documentation from `doc/html/`.

Expected workflow:

1. Write/update Markdown sources
2. Run `build_doc`
3. Open pages from **Help → Documentation**

See also: [GUI Documentation](GUI.md)
