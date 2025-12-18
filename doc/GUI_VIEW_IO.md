# GUI — Saving and Loading Views

A **View** is a complete GUI workspace snapshot saved as a directory.

It includes:

- all chamber configurations (`*.cfg`)
- impedance results (if calculated)
- Data panel export (CSV)
- Plot panel export (PNG)
- a manifest file describing the saved content

---

## View directory structure

A saved View directory contains:

- `view_manifest.json`
- `*.cfg` (one per chamber)
- `output_<chamber_name>/` directories with impedance files
- `data_<...>.csv` (or a title-based CSV name)
- `plot_<...>.png` (or a title-based PNG name)

The manifest stores metadata (version, creation time, view name) and references to all saved artifacts.

---

## Save View

From **File → Save View...**:

1. Choose a View name
2. Choose a base directory
3. The GUI creates a subdirectory and writes all files

Notes:

- Chamber names and titles are sanitized to become safe filenames.
- Chambers without computed impedances are still saved as cfg, but may not have `output_*`.

---

## Load View

From **File → Load View...**:

1. Choose the View directory
2. The GUI reconstructs:
   - chambers and their configuration
   - computed impedances (if present)
   - the Data table and its settings
   - the Plot items and their settings

---

## Manifest format (advanced)

The manifest is JSON and is versioned.

It stores, among other fields:

- `chambers`: list of `{id, component_name, cfg_file, impedance_dir, impedances}`
- `data_settings`: title, frequency column name, and column reconstruction info
- `plot_settings`: plotted items info and plot settings

This format is intended to be stable and forward compatible where possible.
