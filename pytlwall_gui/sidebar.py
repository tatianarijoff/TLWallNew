"""
Sidebar widget for pytlwall GUI.

This module provides the SideBar widget that displays the chambers tree
and the configuration editing panel. It connects to the ChamberData model
for all configuration parameters.

Authors: Tatiana Rijoff
Date: December 2025
"""

from typing import List, Optional

from PyQt5.QtWidgets import (
    QWidget,
    QTabWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QFormLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QScrollArea,
    QDoubleSpinBox,
    QSpinBox,
    QLayout,
    QPushButton,
    QToolButton,
    QFrame,
)
from PyQt5.QtCore import QSize, Qt, pyqtSignal, QMimeData, QByteArray
from PyQt5.QtGui import QDoubleValidator, QBrush, QColor, QFont

from .chamber_data import (
    ChamberData,
    LayerData,
    DEFAULT_OUTPUT_LIST,
)

from .impedance_constants import IMPEDANCE_NAMES, MANDATORY_IMPEDANCES, DEFAULT_IMPEDANCES, TOTAL_CHAMBER_ID


class ImpedanceTreeWidget(QTreeWidget):
    """
    Custom QTreeWidget that properly handles drag operations for impedance items.
    
    This class overrides mimeData() to provide properly formatted data
    when dragging impedance items (ZLong, ZLongRe, ZLongIm, etc.) to the DataPanel/PlotPanel.
    """
    
    def _extract_chamber_name(self, item_text: str) -> str:
        """Extract chamber name from tree item text.
        
        Handles special cases like:
        - "★ Total: Total (sum of all chambers)" -> "Total"
        - "Chamber 1: MyComponent" -> "Chamber 1"
        - "Chamber 1" -> "Chamber 1"
        
        Args:
            item_text: Text from the tree item
            
        Returns:
            Clean chamber name (id)
        """
        # Remove star prefix if present (used for Total chamber highlighting)
        name = item_text.lstrip("★ ").strip()
        # Split on colon and take first part
        name = name.split(":")[0].strip()
        return name
    
    def mimeData(self, items):
        """
        Create MIME data for dragged items.
        
        Args:
            items: List of dragged QTreeWidgetItem objects.
            
        Returns:
            QMimeData with impedance information.
            
        Data format: "chamber_name|impedance_name"
        - If dragging ZLongRe: "Chamber 1|ZLongRe"
        - If dragging ZLong (parent): "Chamber 1|ZLong" (means both Re and Im)
        """
        mime = QMimeData()
        
        if not items:
            return mime
        
        item = items[0]
        text = item.text(0)
        
        # Case 1: Dragging Re or Im component (child item)
        # e.g., ZLongRe, ZLongIm
        if text.endswith("Re") or text.endswith("Im"):
            parent = item.parent()  # This is ZLong, ZTrans, etc.
            if parent:
                grandparent = parent.parent()  # This is the chamber item
                if grandparent:
                    chamber_name = self._extract_chamber_name(grandparent.text(0))
                    data = f"{chamber_name}|{text}"
                    mime.setText(data)
                    mime.setData("application/x-pytlwall-impedance", 
                                QByteArray(data.encode('utf-8')))
        
        # Case 2: Dragging impedance parent (ZLong, ZTrans, etc.)
        # Check if it's an impedance name (might have count suffix like "ZLong (7)")
        else:
            # Extract base name without count or checkmark
            base_name = text.split(" (")[0].replace(" ✓", "").strip()
            
            # Import here to avoid circular import
            from .impedance_constants import IMPEDANCE_NAMES
            
            if base_name in IMPEDANCE_NAMES:
                parent = item.parent()  # This is the chamber item
                if parent:
                    chamber_name = self._extract_chamber_name(parent.text(0))
                    # Use base name without "Re" or "Im" suffix to indicate "both"
                    data = f"{chamber_name}|{base_name}"
                    mime.setText(data)
                    mime.setData("application/x-pytlwall-impedance", 
                                QByteArray(data.encode('utf-8')))
        
        return mime


class SideBar(QWidget):
    """
    Sidebar widget containing the chambers tree and configuration panel.
    
    The sidebar provides two main tabs:
    - Chambers: Tree view of all chambers with impedance selection
    - Chamber Info: Configuration editor for the selected chamber
    
    Signals:
        request_add_chamber: Emitted when user requests to add a new chamber
        request_remove_chamber: Emitted with chamber index when user requests removal
        chamber_data_changed: Emitted with (index, ChamberData) when data changes
    """
    
    # Signals for communication with MainWindow
    request_add_chamber = pyqtSignal()
    request_remove_chamber = pyqtSignal(int)
    chamber_data_changed = pyqtSignal(int, object)  # index, ChamberData
    
    def __init__(self, parent: Optional[QWidget] = None):
        """
        Initialize the sidebar widget.
        
        Args:
            parent: Parent widget.
        """
        super().__init__(parent)
        
        # Local view of chambers data, provided by MainWindow
        self._chambers: List[ChamberData] = []
        self._chamber_items: List[QTreeWidgetItem] = []
        self._layer_widgets: List[QWidget] = []
        
        # Labels for visibility toggling
        self._pipe_radius_label = None
        self._pipe_hor_label = None
        self._pipe_ver_label = None
        
        self.setMinimumWidth(50)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Tab widget
        self.tabs = QTabWidget(self)
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.chambers_tab = QWidget()
        self.tabs.addTab(self.chambers_tab, "Chambers")
        
        self.chamber_info_tab = QWidget()
        self.tabs.addTab(self.chamber_info_tab, "Chamber Info")
        
        # Setup tab contents
        self._setup_chambers_tab()
        self._setup_chamber_info_tab()
    
    def sizeHint(self) -> QSize:
        """Return preferred size for the sidebar."""
        return QSize(280, 400)
    
    # =========================================================================
    # Public API
    # =========================================================================
    
    def set_chambers(self, chambers: List[ChamberData]) -> None:
        """
        Update the sidebar with current chambers list.
        
        Called by MainWindow when chambers are added, removed, or modified.
        
        Args:
            chambers: List of ChamberData objects.
        """
        self._chambers = list(chambers)
        self._refresh_tree()
        self._refresh_chamber_combo()
        self._load_selected_chamber_to_gui()
    
    def get_current_chamber_index(self) -> int:
        """
        Get the index of the currently selected chamber.
        
        Returns:
            Index of selected chamber, or -1 if none selected.
        """
        if hasattr(self, 'chamber_select'):
            return self.chamber_select.currentIndex()
        return -1
    
    def get_current_chamber_data(self) -> Optional[ChamberData]:
        """
        Get the ChamberData for the currently selected chamber.
        
        Returns:
            ChamberData object or None if no chamber selected.
        """
        idx = self.get_current_chamber_index()
        if 0 <= idx < len(self._chambers):
            return self._chambers[idx]
        return None
    
    # =========================================================================
    # Chambers Tab Setup
    # =========================================================================
    
    def _setup_chambers_tab(self) -> None:
        """Setup the 'Chambers' tab with tree view."""
        layout = QVBoxLayout(self.chambers_tab)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(4)
        
        # Top bar with Add chamber button
        top_bar = QHBoxLayout()
        self.add_chamber_button = QPushButton("Add chamber")
        top_bar.addWidget(self.add_chamber_button)
        top_bar.addStretch()
        layout.addLayout(top_bar)
        
        # Chambers tree - use custom tree widget for proper drag support
        self.tree = ImpedanceTreeWidget()
        self.tree.setHeaderHidden(True)
        self.tree.setColumnCount(1)

        # Enable drag from impedance items
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QTreeWidget.DragOnly)
        
        layout.addWidget(self.tree)

        # Connect signals
        self.add_chamber_button.clicked.connect(self.request_add_chamber)
        self.tree.itemClicked.connect(self._on_tree_item_clicked)
        self.tree.itemChanged.connect(self._on_tree_item_changed)
        
    
    def _format_chamber_label(self, chamber: ChamberData) -> str:
        """
        Format the tree item label for a chamber.
        
        Args:
            chamber: ChamberData object.
            
        Returns:
            Formatted label string.
        """
        cid = chamber.id.strip()
        cname = chamber.component_name.strip()
        if cname and cname != cid:
            return f"{cid}: {cname}"
        return cid
    
    def _refresh_tree(self) -> None:
        """Rebuild the chambers tree from current data.
        
        The 'Total' chamber (sum of all chambers) is highlighted with a
        distinct background color for easy identification.
        """
        # Background color for Total chamber (light gold/yellow)
        total_bg_brush = QBrush(QColor(255, 250, 205))  # Lemon chiffon
        
        # Font bold for Total chamber
        bold_font = QFont()
        bold_font.setBold(True)
        
        self.tree.blockSignals(True)
        self.tree.clear()
        self._chamber_items = []
        
        for chamber in self._chambers:
            root_text = self._format_chamber_label(chamber)
            root_item = QTreeWidgetItem([root_text])
            
            # Highlight the "Total" chamber (sum of all chambers)
            is_total_chamber = (chamber.id == TOTAL_CHAMBER_ID)
            if is_total_chamber:
                root_item.setBackground(0, total_bg_brush)
                root_item.setFont(0, bold_font)
                # Add star prefix for visibility
                root_item.setText(0, f"★ {root_text}")
            
            self.tree.addTopLevelItem(root_item)
            self._chamber_items.append(root_item)
            
            # Remove chamber action item (not for Total chamber)
            if not is_total_chamber:
                remove_item = QTreeWidgetItem(["[Remove chamber]"])
                root_item.addChild(remove_item)
            
            # Impedance subtree
            for name in IMPEDANCE_NAMES:
                imp_item = QTreeWidgetItem([name])
                
                if name in MANDATORY_IMPEDANCES:
                    # Mandatory impedances: always enabled and not user-modifiable
                    imp_item.setText(0, f"{name} ✓")
                    chamber.output_flags[name] = True
                else:
                    # Allow user to toggle non-mandatory impedances
                    imp_item.setFlags(imp_item.flags() | Qt.ItemIsUserCheckable)

                    # Set default state based on DEFAULT_IMPEDANCES
                    if name not in chamber.output_flags:
                        chamber.output_flags[name] = (name in DEFAULT_IMPEDANCES)

                    is_checked = bool(chamber.output_flags[name])
                    imp_item.setCheckState(
                        0, Qt.Checked if is_checked else Qt.Unchecked
                    )
                
                # Highlight impedances in Total chamber
                if is_total_chamber:
                    imp_item.setBackground(0, total_bg_brush)
                
                # Add Real and Imaginary child entries
                re_item = QTreeWidgetItem([f"{name}Re"])
                im_item = QTreeWidgetItem([f"{name}Im"])
                
                if is_total_chamber:
                    re_item.setBackground(0, total_bg_brush)
                    im_item.setBackground(0, total_bg_brush)
                
                imp_item.addChild(re_item)
                imp_item.addChild(im_item)
                
                root_item.addChild(imp_item)

            self.tree.expandItem(root_item)
        
        self.tree.blockSignals(False)


    def _on_tree_item_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        """
        Handle clicks in the chambers tree.
        
        Args:
            item: Clicked tree item.
            column: Column index (unused).
        """
        # Trova la chamber root (top-level item) per questo item
        current = item
        while current.parent() is not None:
            current = current.parent()
        
        # Aggiorna la selezione nel combo box
        chamber_idx = self.tree.indexOfTopLevelItem(current)
        if chamber_idx >= 0 and hasattr(self, 'chamber_select'):
            self.chamber_select.blockSignals(True)
            self.chamber_select.setCurrentIndex(chamber_idx)
            self.chamber_select.blockSignals(False)
            # Aggiorna anche la GUI con i dati della chamber selezionata
            self._load_selected_chamber_to_gui()
        
        # Gestione click su [Remove chamber]
        parent = item.parent()
        if parent is not None and item.text(0) == "[Remove chamber]":
            idx = self.tree.indexOfTopLevelItem(parent)
            if idx >= 0:
                self.request_remove_chamber.emit(idx)
    
    def _on_tree_item_changed(self, item: QTreeWidgetItem, column: int) -> None:
        """Handle check state changes for impedance items."""
        # Mandatory impedances are defined in impedance_constants
        
        parent = item.parent()
        if parent is None:
            return  

        item_text = item.text(0)
        # Rimuovi eventuale conteggio e simbolo ✓
        name = item_text.split(" (")[0].replace(" ✓", "").strip()
        if name not in IMPEDANCE_NAMES:
            return  

        # Impedenze obbligatorie: non dovrebbero arrivare qui perché non hanno checkbox
        # Ma per sicurezza, ignoriamo
        if name in MANDATORY_IMPEDANCES:
            return

        # Trova la chamber root (top-level item) per questo item
        current = item
        while current.parent() is not None:
            current = current.parent()
        
        idx = self.tree.indexOfTopLevelItem(current)
        if idx < 0 or idx >= len(self._chambers):
            return

        chamber = self._chambers[idx]
        checked = item.checkState(0) == Qt.Checked
        chamber.output_flags[name] = checked

        self.chamber_data_changed.emit(idx, chamber)


    def _on_chamber_data_changed(self, index: int, chamber: ChamberData) -> None:
        """Handle updates to a chamber and synchronize related UI state."""
        if 0 <= index < len(self.chambers):
            self.chambers[index] = chamber
            self.statusBar().showMessage(f"Updated {chamber.id}", 2000)
            self._sync_impedance_menu_from_chamber(chamber)
        
    def _sync_impedance_menu_from_chamber(self, chamber: ChamberData) -> None:
        """Update impedance menu actions to reflect the given chamber state."""
        for key, action in self.impedance_actions.items():
            if key in chamber.output_flags:
                action.blockSignals(True)
                action.setChecked(bool(chamber.output_flags[key]))
                action.blockSignals(False)
                
    def update_impedance_checks_from_model(self) -> None:
        """Refresh tree check states to match the current chamber's impedance flags."""
        # Mandatory impedances are defined in impedance_constants
        
        idx = self.get_current_chamber_index()
        if idx < 0 or idx >= len(self._chambers):
            return
        chamber = self._chambers[idx]

        self.tree.blockSignals(True)
        root_item = self._chamber_items[idx]
        for i in range(root_item.childCount()):
            imp_item = root_item.child(i)
            item_text = imp_item.text(0)
            # Remove count and checkmark symbol
            name = item_text.split(" (")[0].replace(" ✓", "").strip()
            if name not in IMPEDANCE_NAMES:
                continue
            
            if name in MANDATORY_IMPEDANCES:
                # Mandatory impedances: no checkbox, skip
                continue
            else:
                is_checked = chamber.output_flags.get(name, False)
                imp_item.setCheckState(0, Qt.Checked if is_checked else Qt.Unchecked)
        self.tree.blockSignals(False)

    def update_all_impedance_checks(self) -> None:
        """Refresh tree check states for ALL chambers to match their impedance flags.
        
        Call this after bulk changes to output_flags (e.g., from Accelerator menu).
        """
        self.tree.blockSignals(True)
        
        for idx, chamber in enumerate(self._chambers):
            if idx >= len(self._chamber_items):
                continue
            root_item = self._chamber_items[idx]
            
            for i in range(root_item.childCount()):
                imp_item = root_item.child(i)
                item_text = imp_item.text(0)
                # Remove count, checkmark symbol, and star prefix
                name = item_text.split(" (")[0].replace(" ✓", "").replace("★ ", "").strip()
                if name not in IMPEDANCE_NAMES:
                    continue
                
                if name in MANDATORY_IMPEDANCES:
                    # Mandatory impedances: no checkbox, skip
                    continue
                else:
                    is_checked = chamber.output_flags.get(name, name in DEFAULT_IMPEDANCES)
                    imp_item.setCheckState(0, Qt.Checked if is_checked else Qt.Unchecked)
        
        self.tree.blockSignals(False)
        
    def update_impedance_item_labels(self, chamber_index: int, chamber: ChamberData) -> None:
        """Update impedance tree item labels with number of computed samples."""
        # Impedenze obbligatorie
        # Using MANDATORY_IMPEDANCES from impedance_constants
        
        if chamber_index < 0 or chamber_index >= len(self._chamber_items):
            return

        root_item = self._chamber_items[chamber_index]

        for i in range(root_item.childCount()):
            imp_item = root_item.child(i)
            item_text = imp_item.text(0)
            # Rimuovi conteggio precedente e simbolo ✓
            base_name = item_text.split(" (", 1)[0].replace(" ✓", "").strip()
            if base_name not in IMPEDANCE_NAMES:
                continue

            key_re = f"{base_name}Re"
            n = 0
            if hasattr(chamber, "impedance_results") and key_re in chamber.impedance_results:
                n = len(chamber.impedance_results[key_re])

            # Costruisci la label
            if base_name in MANDATORY_IMPEDANCES:
                # Impedenze obbligatorie: mantieni il simbolo ✓
                label = f"{base_name} ✓ ({n})" if n > 0 else f"{base_name} ✓"
            else:
                label = f"{base_name} ({n})" if n > 0 else base_name
            
            imp_item.setText(0, label)
            imp_item.setText(0, label)



    # =========================================================================
    # Chamber Info Tab Setup
    # =========================================================================
    
    def _setup_chamber_info_tab(self) -> None:
        """Setup the 'Chamber Info' tab with configuration editor."""
        main_layout = QVBoxLayout(self.chamber_info_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Scroll area for vertical scrolling
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        main_layout.addWidget(scroll)
        
        content = QWidget()
        scroll.setWidget(content)
        
        layout = QVBoxLayout(content)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(6)
        
        # Chamber selector combo box
        self.chamber_select = QComboBox()
        # Forza l'uso di QListView per evitare problemi di rendering
        from PyQt5.QtWidgets import QListView
        self.chamber_select.setView(QListView())
        layout.addWidget(self.chamber_select)
        
        # Chamber title label
        self.chamber_title_label = QLabel()
        title_font = self.chamber_title_label.font()
        title_font.setPointSize(title_font.pointSize() + 4)
        title_font.setBold(True)
        self.chamber_title_label.setFont(title_font)
        layout.addWidget(self.chamber_title_label)
        
        # Create configuration sections
        self._create_base_info_section(layout)
        self._create_layers_section(layout)
        self._create_boundary_section(layout)
        self._create_frequency_section(layout)
        self._create_beam_section(layout)
        
        layout.addStretch()
        
        # Connect signals
        self.chamber_select.currentIndexChanged.connect(
            self._on_chamber_selection_changed
        )

    def _create_base_info_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the [base_info] configuration section."""
        form = QFormLayout()
        
        # Component name
        self.component_name_edit = QLineEdit()
        self.component_name_edit.textChanged.connect(self._on_base_info_changed)
        form.addRow("component_name", self.component_name_edit)
        
        # Chamber shape
        self.chamber_shape_combo = QComboBox()
        self.chamber_shape_combo.addItems(["CIRCULAR", "ELLIPTICAL", "RECTANGULAR"])
        self.chamber_shape_combo.currentTextChanged.connect(self._on_chamber_shape_changed)
        form.addRow("chamber_shape", self.chamber_shape_combo)
        
        # Pipe dimensions
        self.pipe_radius_spin = ScientificDoubleSpinBox()
        self.pipe_radius_spin.setDecimals(6)
        self.pipe_radius_spin.setRange(1e-9, 1e3)
        self.pipe_radius_spin.valueChanged.connect(self._on_base_info_changed)
        form.addRow("pipe_radius_m", self.pipe_radius_spin)
        self._pipe_radius_label = form.labelForField(self.pipe_radius_spin)
        
        self.pipe_hor_spin = ScientificDoubleSpinBox()
        self.pipe_hor_spin.setDecimals(6)
        self.pipe_hor_spin.setRange(1e-9, 1e3)
        self.pipe_hor_spin.valueChanged.connect(self._on_base_info_changed)
        form.addRow("pipe_hor_m", self.pipe_hor_spin)
        self._pipe_hor_label = form.labelForField(self.pipe_hor_spin)
        
        self.pipe_ver_spin = ScientificDoubleSpinBox()
        self.pipe_ver_spin.setDecimals(6)
        self.pipe_ver_spin.setRange(1e-9, 1e3)
        self.pipe_ver_spin.valueChanged.connect(self._on_base_info_changed)
        form.addRow("pipe_ver_m", self.pipe_ver_spin)
        self._pipe_ver_label = form.labelForField(self.pipe_ver_spin)
        
        self.pipe_len_spin = ScientificDoubleSpinBox()
        self.pipe_len_spin.setDecimals(6)
        self.pipe_len_spin.setRange(1e-9, 1e6)
        self.pipe_len_spin.valueChanged.connect(self._on_base_info_changed)
        form.addRow("pipe_len_m", self.pipe_len_spin)
        
        # Beta functions
        self.betax_spin = ScientificDoubleSpinBox()
        self.betax_spin.setDecimals(6)
        self.betax_spin.setRange(1e-9, 1e6)
        self.betax_spin.valueChanged.connect(self._on_base_info_changed)
        form.addRow("betax", self.betax_spin)
        
        self.betay_spin = ScientificDoubleSpinBox()
        self.betay_spin.setDecimals(6)
        self.betay_spin.setRange(1e-9, 1e6)
        self.betay_spin.valueChanged.connect(self._on_base_info_changed)
        form.addRow("betay", self.betay_spin)
        
        # Create collapsible section
        section = CollapsibleSection("[base_info]")
        section.setContentLayout(form)
        parent_layout.addWidget(section)
    
    def _create_layers_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the [layers_info] configuration section."""
        layers_layout = QVBoxLayout()
        
        # Number of layers display
        header_layout = QFormLayout()
        self.nbr_layers_spin = QSpinBox()
        self.nbr_layers_spin.setRange(0, 99)
        self.nbr_layers_spin.setReadOnly(True)
        header_layout.addRow("nbr_layers", self.nbr_layers_spin)
        layers_layout.addLayout(header_layout)
        
        # Container for layer widgets
        self.layers_container = QWidget()
        self.layers_container_layout = QVBoxLayout(self.layers_container)
        self.layers_container_layout.setContentsMargins(0, 0, 0, 0)
        self.layers_container_layout.setSpacing(4)
        layers_layout.addWidget(self.layers_container)
        
        # Add layer button
        self.add_layer_button = QPushButton("Add layer")
        self.add_layer_button.clicked.connect(self._on_add_layer)
        layers_layout.addWidget(self.add_layer_button)
        
        # Create collapsible section
        section = CollapsibleSection("[layers_info]")
        section.setContentLayout(layers_layout)
        parent_layout.addWidget(section)
    
    def _create_boundary_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the [boundary] configuration section."""
        form = QFormLayout()
        
        # Boundary type
        self.boundary_type_combo = QComboBox()
        self.boundary_type_combo.addItems(["CW", "PEC", "PMC", "V"])
        # Fix: prevent text from disappearing on hover (Qt theme issue)
        self.boundary_type_combo.setStyleSheet("""
            QComboBox { color: palette(text); }
            QComboBox:hover { color: palette(text); }
            QComboBox QAbstractItemView { color: palette(text); }
        """)
        self.boundary_type_combo.currentTextChanged.connect(self._on_boundary_type_changed)
        form.addRow("type", self.boundary_type_combo)
        
        # CW/RW parameters
        self.boundary_muinf_spin = ScientificDoubleSpinBox()
        self.boundary_muinf_spin.setDecimals(3)
        self.boundary_muinf_spin.setRange(0.0, 1e12)
        self.boundary_muinf_spin.valueChanged.connect(self._on_boundary_changed)
        form.addRow("muinf_Hz", self.boundary_muinf_spin)
        
        self.boundary_kHz_spin = ScientificDoubleSpinBox()
        self.boundary_kHz_spin.setDecimals(3)
        self.boundary_kHz_spin.setRange(0.0, 1e20)
        self.boundary_kHz_spin.valueChanged.connect(self._on_boundary_changed)
        form.addRow("k_Hz", self.boundary_kHz_spin)
        
        self.boundary_sigma_spin = ScientificDoubleSpinBox()
        self.boundary_sigma_spin.setDecimals(6)
        self.boundary_sigma_spin.setRange(0.0, 1e12)
        self.boundary_sigma_spin.valueChanged.connect(self._on_boundary_changed)
        form.addRow("sigmaDC", self.boundary_sigma_spin)
        
        self.boundary_epsr_spin = ScientificDoubleSpinBox()
        self.boundary_epsr_spin.setDecimals(6)
        self.boundary_epsr_spin.setRange(1e-9, 1e6)
        self.boundary_epsr_spin.valueChanged.connect(self._on_boundary_changed)
        form.addRow("epsr", self.boundary_epsr_spin)
        
        self.boundary_tau_spin = ScientificDoubleSpinBox()
        self.boundary_tau_spin.setDecimals(12)
        self.boundary_tau_spin.setRange(0.0, 1e3)
        self.boundary_tau_spin.valueChanged.connect(self._on_boundary_changed)
        form.addRow("tau", self.boundary_tau_spin)
        
        self.boundary_RQ_spin = ScientificDoubleSpinBox()
        self.boundary_RQ_spin.setDecimals(9)
        self.boundary_RQ_spin.setRange(0.0, 1e6)
        self.boundary_RQ_spin.valueChanged.connect(self._on_boundary_changed)
        form.addRow("RQ", self.boundary_RQ_spin)
        
        # Create collapsible section
        section = CollapsibleSection("[boundary]")
        section.setContentLayout(form)
        parent_layout.addWidget(section)
        
        # Store CW parameter widgets for visibility toggling
        self._boundary_cw_widgets = [
            self.boundary_muinf_spin,
            self.boundary_kHz_spin,
            self.boundary_sigma_spin,
            self.boundary_epsr_spin,
            self.boundary_tau_spin,
            self.boundary_RQ_spin,
        ]
        self._boundary_cw_labels = [
            form.labelForField(w) for w in self._boundary_cw_widgets
        ]

    def _create_frequency_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the [frequency_info] configuration section."""
        freq_layout = QVBoxLayout()
        
        # Mode selector
        mode_form = QFormLayout()
        self.freq_mode_combo = QComboBox()
        self.freq_mode_combo.addItems(["Range", "From file"])
        self.freq_mode_combo.currentIndexChanged.connect(self._on_freq_mode_changed)
        mode_form.addRow("Mode", self.freq_mode_combo)
        freq_layout.addLayout(mode_form)
        
        # Range mode widgets
        self.freq_range_widget = QWidget()
        range_form = QFormLayout(self.freq_range_widget)
        
        self.fmin_spin = QSpinBox()
        self.fmin_spin.setRange(0, 40)
        self.fmin_spin.valueChanged.connect(self._on_frequency_changed)
        range_form.addRow("fmin", self.fmin_spin)
        
        self.fmax_spin = QSpinBox()
        self.fmax_spin.setRange(0, 40)
        self.fmax_spin.valueChanged.connect(self._on_frequency_changed)
        range_form.addRow("fmax", self.fmax_spin)
        
        self.fstep_spin = QSpinBox()
        self.fstep_spin.setRange(1, 10)
        self.fstep_spin.valueChanged.connect(self._on_frequency_changed)
        range_form.addRow("fstep", self.fstep_spin)
        
        freq_layout.addWidget(self.freq_range_widget)
        
        # File mode widgets
        self.freq_file_widget = QWidget()
        file_form = QFormLayout(self.freq_file_widget)
        
        self.freq_filename_edit = QLineEdit()
        self.freq_filename_edit.textChanged.connect(self._on_frequency_changed)
        file_form.addRow("filename", self.freq_filename_edit)
        
        self.freq_separator_combo = QComboBox()
        self.freq_separator_combo.addItems(["whitespace", ",", ";", "tab"])
        self.freq_separator_combo.currentTextChanged.connect(self._on_frequency_changed)
        file_form.addRow("separator", self.freq_separator_combo)
        
        self.freq_col_spin = QSpinBox()
        self.freq_col_spin.setRange(0, 9999)
        self.freq_col_spin.valueChanged.connect(self._on_frequency_changed)
        file_form.addRow("freq_col", self.freq_col_spin)
        
        self.skip_rows_spin = QSpinBox()
        self.skip_rows_spin.setRange(0, 999999)
        self.skip_rows_spin.valueChanged.connect(self._on_frequency_changed)
        file_form.addRow("skip_rows", self.skip_rows_spin)
        
        freq_layout.addWidget(self.freq_file_widget)
        
        # Create collapsible section
        section = CollapsibleSection("[frequency_info]")
        section.setContentLayout(freq_layout)
        parent_layout.addWidget(section)
    
    def _create_beam_section(self, parent_layout: QVBoxLayout) -> None:
        """Create the [beam_info] configuration section."""
        form = QFormLayout()
        
        self.test_beam_shift_spin = ScientificDoubleSpinBox()
        self.test_beam_shift_spin.setDecimals(6)
        self.test_beam_shift_spin.setRange(-1e3, 1e3)
        self.test_beam_shift_spin.valueChanged.connect(self._on_beam_changed)
        form.addRow("test_beam_shift", self.test_beam_shift_spin)
        
        self.gammarel_spin = ScientificDoubleSpinBox()
        self.gammarel_spin.setDecimals(3)
        self.gammarel_spin.setRange(1.0, 1e9)
        self.gammarel_spin.valueChanged.connect(self._on_beam_changed)
        form.addRow("gammarel", self.gammarel_spin)
        
        self.mass_spin = ScientificDoubleSpinBox()
        self.mass_spin.setDecimals(6)
        self.mass_spin.setRange(0.001, 1e9)
        self.mass_spin.valueChanged.connect(self._on_beam_changed)
        form.addRow("mass_MeV_c2", self.mass_spin)
        
        # Create collapsible section
        section = CollapsibleSection("[beam_info]")
        section.setContentLayout(form)
        parent_layout.addWidget(section)
    
    # =========================================================================
    # Data Loading and Saving
    # =========================================================================
    
    def _refresh_chamber_combo(self) -> None:
        """Refresh the chamber selector combo box."""
        if not hasattr(self, 'chamber_select'):
            return
        
        current_id = self.chamber_select.currentText()
        
        self.chamber_select.blockSignals(True)
        self.chamber_select.clear()
        for chamber in self._chambers:
            self.chamber_select.addItem(chamber.id)
        
        # Restore selection
        idx = self.chamber_select.findText(current_id)
        self.chamber_select.setCurrentIndex(idx if idx >= 0 else 0)
        self.chamber_select.blockSignals(False)
    
    def _on_chamber_selection_changed(self, index: int) -> None:
        """Handle chamber selection change."""
        self._load_selected_chamber_to_gui()
    
    def _load_selected_chamber_to_gui(self) -> None:
        """Load the selected chamber's data into all GUI widgets."""
        idx = self.get_current_chamber_index()
        if idx < 0 or idx >= len(self._chambers):
            return
        
        chamber = self._chambers[idx]
        
        # Block signals during loading
        self._block_all_signals(True)
        
        try:
            # Update title
            self.chamber_title_label.setText(chamber.id)
            
            # Load base_info
            base = chamber.base_info
            self.component_name_edit.setText(base.component_name)
            self.chamber_shape_combo.setCurrentText(base.chamber_shape)
            self.pipe_radius_spin.setValue(base.pipe_radius_m)
            self.pipe_hor_spin.setValue(base.pipe_hor_m)
            self.pipe_ver_spin.setValue(base.pipe_ver_m)
            self.pipe_len_spin.setValue(base.pipe_len_m)
            self.betax_spin.setValue(base.betax)
            self.betay_spin.setValue(base.betay)
            
            # Update dimension field visibility
            self._update_dimension_visibility(base.chamber_shape)
            
            # Load layers
            self._load_layers_to_gui(chamber.layers)
            
            # Load boundary
            boundary = chamber.boundary
            self.boundary_type_combo.setCurrentText(boundary.layer_type)
            self.boundary_muinf_spin.setValue(boundary.muinf_Hz)
            self.boundary_kHz_spin.setValue(
                boundary.k_Hz if boundary.k_Hz != float('inf') else 1e20
            )
            self.boundary_sigma_spin.setValue(boundary.sigmaDC)
            self.boundary_epsr_spin.setValue(boundary.epsr)
            self.boundary_tau_spin.setValue(boundary.tau)
            self.boundary_RQ_spin.setValue(boundary.RQ)
            self._update_boundary_cw_visibility(boundary.layer_type)
            
            # Load frequency
            freq = chamber.frequency
            self.freq_mode_combo.setCurrentIndex(0 if freq.mode == "range" else 1)
            self.fmin_spin.setValue(int(freq.fmin))
            self.fmax_spin.setValue(int(freq.fmax))
            self.fstep_spin.setValue(int(freq.fstep))
            self.freq_filename_edit.setText(freq.filename)
            self.freq_separator_combo.setCurrentText(freq.separator)
            self.freq_col_spin.setValue(freq.freq_col)
            self.skip_rows_spin.setValue(freq.skip_rows)
            self._update_freq_mode_visibility(freq.mode)
            
            # Load beam
            beam = chamber.beam
            self.test_beam_shift_spin.setValue(beam.test_beam_shift)
            self.gammarel_spin.setValue(beam.gammarel)
            self.mass_spin.setValue(beam.mass_MeV_c2)
            
        finally:
            self._block_all_signals(False)
    
    def _load_layers_to_gui(self, layers: List[LayerData]) -> None:
        """Load layer data into GUI widgets."""
        # Clear existing layer widgets
        for widget in self._layer_widgets:
            self.layers_container_layout.removeWidget(widget)
            widget.deleteLater()
        self._layer_widgets = []
        
        # Create widgets for each layer
        for i, layer in enumerate(layers):
            widget = self._create_layer_widget(i, layer)
            self.layers_container_layout.addWidget(widget)
            self._layer_widgets.append(widget)
        
        # Update layer count
        self.nbr_layers_spin.setValue(len(layers))

    def _create_layer_widget(self, index: int, layer: LayerData) -> QWidget:
        """
        Create a widget for editing a single layer.
        
        Args:
            index: Layer index.
            layer: LayerData to display.
            
        Returns:
            Container widget with layer editing controls.
        """
        container = QWidget()
        form = QFormLayout(container)
        form.setContentsMargins(0, 4, 0, 4)
        form.setSpacing(2)
        
        # Layer header
        header = QLabel(f"--- Layer {index} ---")
        header.setStyleSheet("font-weight: bold;")
        form.addRow(header)
        
        # Type combo
        type_combo = QComboBox()
        type_combo.addItems(["CW", "PEC", "PMC", "V"])
        # Fix: prevent text from disappearing on hover (Qt theme issue)
        type_combo.setStyleSheet("""
            QComboBox { color: palette(text); }
            QComboBox:hover { color: palette(text); }
            QComboBox QAbstractItemView { color: palette(text); }
        """)
        type_combo.setCurrentText(layer.layer_type)
        type_combo.currentTextChanged.connect(
            lambda text, idx=index: self._on_layer_type_changed(idx, text)
        )
        form.addRow("type", type_combo)
        
        # Thickness
        thick_spin = ScientificDoubleSpinBox()
        thick_spin.setDecimals(12)
        thick_spin.setRange(1e-15, 1e3)
        thick_spin.setValue(layer.thick_m if layer.thick_m != float('inf') else 1e3)
        thick_spin.valueChanged.connect(lambda: self._on_layer_changed(index))
        form.addRow("thick_m", thick_spin)
        
        # CW/RW parameters
        muinf_spin = ScientificDoubleSpinBox()
        muinf_spin.setDecimals(3)
        muinf_spin.setRange(0.0, 1e12)
        muinf_spin.setValue(layer.muinf_Hz)
        muinf_spin.valueChanged.connect(lambda: self._on_layer_changed(index))
        form.addRow("muinf_Hz", muinf_spin)
        
        kHz_spin = ScientificDoubleSpinBox()
        kHz_spin.setDecimals(3)
        kHz_spin.setRange(0.0, 1e20)
        kHz_spin.setValue(layer.k_Hz if layer.k_Hz != float('inf') else 1e20)
        kHz_spin.valueChanged.connect(lambda: self._on_layer_changed(index))
        form.addRow("k_Hz", kHz_spin)
        
        sigma_spin = ScientificDoubleSpinBox()
        sigma_spin.setDecimals(6)
        sigma_spin.setRange(0.0, 1e12)
        sigma_spin.setValue(layer.sigmaDC)
        sigma_spin.valueChanged.connect(lambda: self._on_layer_changed(index))
        form.addRow("sigmaDC", sigma_spin)
        
        epsr_spin = ScientificDoubleSpinBox()
        epsr_spin.setDecimals(6)
        epsr_spin.setRange(1e-9, 1e6)
        epsr_spin.setValue(layer.epsr)
        epsr_spin.valueChanged.connect(lambda: self._on_layer_changed(index))
        form.addRow("epsr", epsr_spin)
        
        tau_spin = ScientificDoubleSpinBox()
        tau_spin.setDecimals(12)
        tau_spin.setRange(0.0, 1e3)
        tau_spin.setValue(layer.tau)
        tau_spin.valueChanged.connect(lambda: self._on_layer_changed(index))
        form.addRow("tau", tau_spin)
        
        RQ_spin = ScientificDoubleSpinBox()
        RQ_spin.setDecimals(9)
        RQ_spin.setRange(0.0, 1e6)
        RQ_spin.setValue(layer.RQ)
        RQ_spin.valueChanged.connect(lambda: self._on_layer_changed(index))
        form.addRow("RQ", RQ_spin)
        
        # Remove button
        remove_btn = QPushButton("Remove layer")
        remove_btn.clicked.connect(lambda: self._on_remove_layer(index))
        form.addRow(remove_btn)
        
        # Store references to widgets
        container.type_combo = type_combo
        container.thick_spin = thick_spin
        container.muinf_spin = muinf_spin
        container.kHz_spin = kHz_spin
        container.sigma_spin = sigma_spin
        container.epsr_spin = epsr_spin
        container.tau_spin = tau_spin
        container.RQ_spin = RQ_spin
        container.cw_widgets = [muinf_spin, kHz_spin, sigma_spin, epsr_spin, tau_spin, RQ_spin]
        container.cw_labels = [form.labelForField(w) for w in container.cw_widgets]
        
        # Update CW parameter visibility
        self._update_layer_cw_visibility(container, layer.layer_type)
        
        return container
    
    def _save_gui_to_chamber(self) -> None:
        """Save current GUI values to the selected chamber's data."""
        chamber = self.get_current_chamber_data()
        if chamber is None:
            return
        
        # Save base_info
        base = chamber.base_info
        base.component_name = self.component_name_edit.text()
        base.chamber_shape = self.chamber_shape_combo.currentText()
        base.pipe_radius_m = self.pipe_radius_spin.value()
        base.pipe_hor_m = self.pipe_hor_spin.value()
        base.pipe_ver_m = self.pipe_ver_spin.value()
        base.pipe_len_m = self.pipe_len_spin.value()
        base.betax = self.betax_spin.value()
        base.betay = self.betay_spin.value()
        
        # Save layers
        chamber.layers = []
        for widget in self._layer_widgets:
            layer = LayerData()
            layer.layer_type = widget.type_combo.currentText()
            layer.thick_m = widget.thick_spin.value()
            layer.muinf_Hz = widget.muinf_spin.value()
            layer.k_Hz = widget.kHz_spin.value()
            if layer.k_Hz >= 1e19:
                layer.k_Hz = float('inf')
            layer.sigmaDC = widget.sigma_spin.value()
            layer.epsr = widget.epsr_spin.value()
            layer.tau = widget.tau_spin.value()
            layer.RQ = widget.RQ_spin.value()
            chamber.layers.append(layer)
        
        # Save boundary
        boundary = chamber.boundary
        boundary.layer_type = self.boundary_type_combo.currentText()
        boundary.muinf_Hz = self.boundary_muinf_spin.value()
        boundary.k_Hz = self.boundary_kHz_spin.value()
        if boundary.k_Hz >= 1e19:
            boundary.k_Hz = float('inf')
        boundary.sigmaDC = self.boundary_sigma_spin.value()
        boundary.epsr = self.boundary_epsr_spin.value()
        boundary.tau = self.boundary_tau_spin.value()
        boundary.RQ = self.boundary_RQ_spin.value()
        
        # Save frequency
        freq = chamber.frequency
        freq.mode = "range" if self.freq_mode_combo.currentIndex() == 0 else "file"
        freq.fmin = float(self.fmin_spin.value())
        freq.fmax = float(self.fmax_spin.value())
        freq.fstep = float(self.fstep_spin.value())
        freq.filename = self.freq_filename_edit.text()
        freq.separator = self.freq_separator_combo.currentText()
        freq.freq_col = self.freq_col_spin.value()
        freq.skip_rows = self.skip_rows_spin.value()
        
        # Save beam
        beam = chamber.beam
        beam.test_beam_shift = self.test_beam_shift_spin.value()
        beam.gammarel = self.gammarel_spin.value()
        beam.mass_MeV_c2 = self.mass_spin.value()
        
        # Emit change signal
        idx = self.get_current_chamber_index()
        self.chamber_data_changed.emit(idx, chamber)

    # =========================================================================
    # Change Handlers
    # =========================================================================
    
    def _on_base_info_changed(self) -> None:
        """Handle changes to base_info fields."""
        self._save_gui_to_chamber()
        # Update tree label for component name changes
        idx = self.get_current_chamber_index()
        if 0 <= idx < len(self._chamber_items):
            chamber = self._chambers[idx]
            self._chamber_items[idx].setText(0, self._format_chamber_label(chamber))
    
    def _on_chamber_shape_changed(self, shape: str) -> None:
        """Handle chamber shape changes."""
        self._update_dimension_visibility(shape)
        self._save_gui_to_chamber()
    
    def _update_dimension_visibility(self, shape: str) -> None:
        """Update visibility of dimension fields based on shape."""
        is_circular = (shape == "CIRCULAR")
        
        self.pipe_radius_spin.setVisible(is_circular)
        if self._pipe_radius_label:
            self._pipe_radius_label.setVisible(is_circular)
        
        self.pipe_hor_spin.setVisible(not is_circular)
        if self._pipe_hor_label:
            self._pipe_hor_label.setVisible(not is_circular)
        
        self.pipe_ver_spin.setVisible(not is_circular)
        if self._pipe_ver_label:
            self._pipe_ver_label.setVisible(not is_circular)
    
    def _on_layer_changed(self, index: int) -> None:
        """Handle changes to layer fields."""
        self._save_gui_to_chamber()
    
    def _on_layer_type_changed(self, index: int, layer_type: str) -> None:
        """Handle layer type changes."""
        if 0 <= index < len(self._layer_widgets):
            widget = self._layer_widgets[index]
            self._update_layer_cw_visibility(widget, layer_type)
        self._save_gui_to_chamber()
    
    def _update_layer_cw_visibility(self, container: QWidget, layer_type: str) -> None:
        """Update visibility of CW parameters for a layer widget."""
        # Note: RW is converted to CW on load, so only check for CW
        show_cw = layer_type == "CW"
        for i, widget in enumerate(container.cw_widgets):
            widget.setVisible(show_cw)
            if i < len(container.cw_labels) and container.cw_labels[i]:
                container.cw_labels[i].setVisible(show_cw)
    
    def _on_add_layer(self) -> None:
        """Handle add layer button click."""
        chamber = self.get_current_chamber_data()
        if chamber is None:
            return
        
        new_layer = chamber.add_layer()
        widget = self._create_layer_widget(len(chamber.layers) - 1, new_layer)
        self.layers_container_layout.addWidget(widget)
        self._layer_widgets.append(widget)
        self.nbr_layers_spin.setValue(len(chamber.layers))
        
        self._save_gui_to_chamber()
    
    def _on_remove_layer(self, index: int) -> None:
        """Handle remove layer button click."""
        chamber = self.get_current_chamber_data()
        if chamber is None or len(chamber.layers) <= 1:
            return  # Keep at least one layer
        
        chamber.remove_layer(index)
        self._load_layers_to_gui(chamber.layers)
        self._save_gui_to_chamber()
    
    def _on_boundary_changed(self) -> None:
        """Handle changes to boundary fields."""
        self._save_gui_to_chamber()
    
    def _on_boundary_type_changed(self, boundary_type: str) -> None:
        """Handle boundary type changes."""
        self._update_boundary_cw_visibility(boundary_type)
        self._save_gui_to_chamber()
    
    def _update_boundary_cw_visibility(self, boundary_type: str) -> None:
        """Update visibility of CW parameters for boundary."""
        # Note: RW is converted to CW on load, so only check for CW
        show_cw = boundary_type == "CW"
        for i, widget in enumerate(self._boundary_cw_widgets):
            widget.setVisible(show_cw)
            if i < len(self._boundary_cw_labels) and self._boundary_cw_labels[i]:
                self._boundary_cw_labels[i].setVisible(show_cw)
    
    def _on_freq_mode_changed(self, index: int) -> None:
        """Handle frequency mode changes."""
        mode = "range" if index == 0 else "file"
        self._update_freq_mode_visibility(mode)
        self._save_gui_to_chamber()
    
    def _update_freq_mode_visibility(self, mode: str) -> None:
        """Update visibility of frequency widgets based on mode."""
        self.freq_range_widget.setVisible(mode == "range")
        self.freq_file_widget.setVisible(mode == "file")
    
    def _on_frequency_changed(self) -> None:
        """Handle changes to frequency fields."""
        self._save_gui_to_chamber()
    
    def _on_beam_changed(self) -> None:
        """Handle changes to beam fields."""
        self._save_gui_to_chamber()
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _block_all_signals(self, block: bool) -> None:
        """Block or unblock signals from all editable widgets."""
        widgets = [
            self.component_name_edit,
            self.chamber_shape_combo,
            self.pipe_radius_spin,
            self.pipe_hor_spin,
            self.pipe_ver_spin,
            self.pipe_len_spin,
            self.betax_spin,
            self.betay_spin,
            self.boundary_type_combo,
            self.boundary_muinf_spin,
            self.boundary_kHz_spin,
            self.boundary_sigma_spin,
            self.boundary_epsr_spin,
            self.boundary_tau_spin,
            self.boundary_RQ_spin,
            self.freq_mode_combo,
            self.fmin_spin,
            self.fmax_spin,
            self.fstep_spin,
            self.freq_filename_edit,
            self.freq_separator_combo,
            self.freq_col_spin,
            self.skip_rows_spin,
            self.test_beam_shift_spin,
            self.gammarel_spin,
            self.mass_spin,
        ]
        
        for widget in widgets:
            widget.blockSignals(block)
        
        for layer_widget in self._layer_widgets:
            layer_widget.type_combo.blockSignals(block)
            layer_widget.thick_spin.blockSignals(block)
            layer_widget.muinf_spin.blockSignals(block)
            layer_widget.kHz_spin.blockSignals(block)
            layer_widget.sigma_spin.blockSignals(block)
            layer_widget.epsr_spin.blockSignals(block)
            layer_widget.tau_spin.blockSignals(block)
            layer_widget.RQ_spin.blockSignals(block)


class CollapsibleSection(QWidget):
    """
    Expandable/collapsible section widget.
    
    Provides a header button that toggles visibility of the content area.
    Used to organize configuration sections in a compact, user-friendly way.
    """
    
    def __init__(self, title: str, parent: Optional[QWidget] = None):
        """
        Initialize the collapsible section.
        
        Args:
            title: Header text for the section.
            parent: Parent widget.
        """
        super().__init__(parent)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header button
        self.toggle_button = QToolButton()
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggle_button.setArrowType(Qt.RightArrow)
        self.toggle_button.setText(title)
        self.toggle_button.setCheckable(True)
        self.toggle_button.setChecked(False)
        
        # Content frame
        self.content_area = QFrame()
        self.content_area.setFrameShape(QFrame.NoFrame)
        self.content_area.setVisible(False)
        
        main_layout.addWidget(self.toggle_button)
        main_layout.addWidget(self.content_area)
        
        self.toggle_button.toggled.connect(self._on_toggled)
    
    def setContentLayout(self, layout: QLayout) -> None:
        """
        Set the layout for the collapsible content area.
        
        Args:
            layout: Layout to use for content.
        """
        self.content_area.setLayout(layout)
    
    def _on_toggled(self, checked: bool) -> None:
        """Handle toggle button state changes."""
        self.toggle_button.setArrowType(Qt.DownArrow if checked else Qt.RightArrow)
        self.content_area.setVisible(checked)


class ScientificDoubleSpinBox(QDoubleSpinBox):
    """
    Double spin box with scientific notation support.
    
    Accepts standard and scientific notation input (e.g., 1e5, -2.3E-4)
    and displays large/small values in scientific notation.
    """
    
    def __init__(
        self,
        parent: Optional[QWidget] = None,
        sci_threshold_high: float = 1e4,
        sci_threshold_low: float = 1e-4,
        sci_decimals: int = 6
    ):
        """
        Initialize the scientific double spin box.
        
        Args:
            parent: Parent widget.
            sci_threshold_high: Use scientific notation above this value.
            sci_threshold_low: Use scientific notation below this value.
            sci_decimals: Number of decimal places in scientific notation.
        """
        super().__init__(parent)
        
        self._sci_threshold_high = sci_threshold_high
        self._sci_threshold_low = sci_threshold_low
        self._sci_decimals = sci_decimals
        
        # Allow many decimals for internal precision
        self.setDecimals(12)
        
        # Validator for scientific notation input
        validator = QDoubleValidator(self)
        validator.setNotation(QDoubleValidator.ScientificNotation)
        validator.setDecimals(12)
        self.lineEdit().setValidator(validator)
        
        self.setAlignment(Qt.AlignRight)
    
    def valueFromText(self, text: str) -> float:
        """
        Parse user input string into a float.
        
        Args:
            text: Input text to parse.
            
        Returns:
            Parsed float value, or current value if parsing fails.
        """
        try:
            return float(text)
        except ValueError:
            return self.value()
    
    def textFromValue(self, value: float) -> str:
        """
        Convert internal value to display string.
        
        Uses scientific notation for very large or very small values.
        
        Args:
            value: Value to format.
            
        Returns:
            Formatted string representation.
        """
        abs_val = abs(value)
        
        if abs_val == 0.0:
            return "0"
        
        if abs_val >= self._sci_threshold_high or abs_val <= self._sci_threshold_low:
            return f"{value:.{self._sci_decimals}e}"
        else:
            return f"{value:.{self.decimals()}f}"
