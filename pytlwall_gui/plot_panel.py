"""PyTlWall GUI - Plot Panel with overlay and selectable impedance list."""

from typing import Dict, List, Optional, Tuple, Any
import numpy as np

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QListWidget, QListWidgetItem, QSplitter, QMenu, QFileDialog,
    QMessageBox, QAbstractItemView, QCheckBox, QLineEdit, QComboBox,
    QFormLayout, QGroupBox, QListView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from matplotlib.figure import Figure


class PlotItem:
    """Represents a plotted impedance."""
    
    def __init__(self, chamber_name: str, impedance_name: str, component: str,
                 data: np.ndarray, frequencies: np.ndarray, color: str):
        self.chamber_name = chamber_name
        self.impedance_name = impedance_name
        self.component = component
        self.data = data
        self.frequencies = frequencies
        self.color = color
        self.visible = True
        # Label editabile - default basato sui dati
        self._custom_label = None
    
    @property
    def full_name(self) -> str:
        return f"{self.chamber_name} {self.impedance_name}_{self.component}"
    
    @property
    def default_label(self) -> str:
        """Label di default basata sui dati."""
        return f"{self.chamber_name} {self.impedance_name} {self.component}"
    
    @property
    def label(self) -> str:
        """Label usata nel plot (custom o default)."""
        return self._custom_label if self._custom_label else self.default_label
    
    @label.setter
    def label(self, value: str):
        """Imposta una label custom."""
        self._custom_label = value if value and value != self.default_label else None


class PlotCanvas(FigureCanvas):
    """Matplotlib canvas for impedance plots."""
    
    PLOT_COLORS = [
        '#1976D2', '#D32F2F', '#388E3C', '#F57C00',
        '#7B1FA2', '#0097A7', '#C2185B', '#AFB42B',
        '#5D4037', '#455A64', '#E64A19', '#00796B',
    ]
    
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 6), dpi=100, facecolor='#FAFAFA')
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.fig.add_subplot(111)
        self._color_index = 0
        self._setup_style()
    
    def _setup_style(self):
        self.ax.set_facecolor('#FFFFFF')
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.tick_params(labelsize=9)
        try:
            self.fig.tight_layout(pad=2.0)
        except ValueError:
            pass  # Ignore tight_layout errors during setup
    
    def get_next_color(self) -> str:
        """Get next color in rotation."""
        color = self.PLOT_COLORS[self._color_index % len(self.PLOT_COLORS)]
        self._color_index += 1
        return color
    
    def reset_color_index(self):
        """Reset color rotation."""
        self._color_index = 0
    
    def clear(self):
        self.ax.clear()
        self._setup_style()
        self._color_index = 0
        self.draw()
    
    def plot_items(self, items: List[PlotItem], title: str = "Impedance",
                   xlabel: str = "Frequency [Hz]", ylabel: str = "Z [Ω]",
                   xscale: str = "log", yscale: str = "log"):
        """Plot multiple items with overlay.
        
        Args:
            items: List of PlotItem to plot
            title: Plot title
            xlabel: X-axis label
            ylabel: Y-axis label
            xscale: X-axis scale ('log' or 'linear')
            yscale: Y-axis scale ('log' or 'linear')
        """
        self.ax.clear()
        self._setup_style()
        
        visible_items = [item for item in items if item.visible]
        
        if not visible_items:
            self.ax.set_title("No data to plot", fontsize=11)
            self.draw()
            return
        
        # Track if we have valid data for log scales
        has_valid_y_for_log = False
        has_valid_x_for_log = False
        
        for item in visible_items:
            try:
                y_data = np.array(item.data, dtype=float)
                x_data = np.array(item.frequencies, dtype=float)
                
                # Handle zeros/negatives for log scale
                if yscale == "log":
                    y_data = np.abs(y_data)
                    y_data = np.where(y_data > 0, y_data, np.nan)
                    if np.any(np.isfinite(y_data)):
                        has_valid_y_for_log = True
                else:
                    has_valid_y_for_log = True
                    
                if xscale == "log":
                    x_data = np.where(x_data > 0, x_data, np.nan)
                    if np.any(np.isfinite(x_data)):
                        has_valid_x_for_log = True
                else:
                    has_valid_x_for_log = True
                
                self.ax.plot(
                    x_data, y_data,
                    color=item.color, linewidth=1.5,
                    label=item.label
                )
            except Exception as e:
                print(f"Error plotting {item.full_name}: {e}")
        
        # Set scales - fall back to linear if log scale won't work
        actual_xscale = xscale
        actual_yscale = yscale
        
        if xscale == "log" and not has_valid_x_for_log:
            actual_xscale = "linear"
            print("Warning: No valid positive X data for log scale, using linear")
            
        if yscale == "log" and not has_valid_y_for_log:
            actual_yscale = "linear"
            print("Warning: No valid positive Y data for log scale, using linear")
        
        try:
            self.ax.set_xscale(actual_xscale)
            self.ax.set_yscale(actual_yscale)
        except ValueError as e:
            # Fallback to linear if scale setting fails
            print(f"Scale setting failed ({e}), using linear scales")
            self.ax.set_xscale("linear")
            self.ax.set_yscale("linear")
        
        self.ax.set_xlabel(xlabel, fontsize=10)
        self.ax.set_ylabel(ylabel, fontsize=10)
        self.ax.set_title(title, fontsize=11, fontweight='bold')
        
        if len(visible_items) > 1:
            self.ax.legend(loc='best', fontsize=8)
        
        # Wrap tight_layout in try/except to handle edge cases
        try:
            self.fig.tight_layout(pad=2.0)
        except ValueError as e:
            # This can happen if all data is NaN or axes can't be determined
            print(f"tight_layout failed: {e}")
        
        self.draw()
    
    def save_figure(self, filepath: str, dpi: int = 150) -> bool:
        """Save figure to file."""
        try:
            self.fig.savefig(filepath, dpi=dpi, bbox_inches='tight', facecolor='white')
            return True
        except Exception as e:
            print(f"Error saving figure: {e}")
            return False


class ImpedanceListItem(QListWidgetItem):
    """List item representing a plotted impedance."""
    
    def __init__(self, plot_item: PlotItem):
        super().__init__()
        self.plot_item = plot_item
        self.setText(plot_item.label)
        self.setFlags(self.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEditable)
        self.setCheckState(Qt.Checked if plot_item.visible else Qt.Unchecked)
        
        # Color indicator
        self.setForeground(QColor(plot_item.color))
    
    def update_label(self):
        """Aggiorna il testo visualizzato dalla label del PlotItem."""
        self.setText(self.plot_item.label)


class PlotPanel(QWidget):
    """Panel with plot canvas and impedance list for overlay control."""
    
    # Signals
    impedance_removed = pyqtSignal(str)  # full_name
    impedance_drop_requested = pyqtSignal(str, str)  # chamber_name, impedance_name (e.g., "ZLongRe")
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._items: List[PlotItem] = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Enable drop on the entire PlotPanel
        self.setAcceptDrops(True)
        
        # Left side: Plot
        plot_widget = QWidget()
        plot_layout = QVBoxLayout(plot_widget)
        plot_layout.setContentsMargins(0, 0, 0, 0)
        plot_layout.setSpacing(2)
        
        # Canvas
        self._canvas = PlotCanvas(self)
        # Enable drop on canvas
        self._canvas.setAcceptDrops(True)
        self._canvas.dragEnterEvent = self._drag_enter
        self._canvas.dragMoveEvent = self._drag_move
        self._canvas.dropEvent = self._drop_event
        plot_layout.addWidget(self._canvas, stretch=1)
        
        # Toolbar
        self._toolbar = NavigationToolbar2QT(self._canvas, self)
        plot_layout.addWidget(self._toolbar)
        
        # Right side: Controls and Impedance list
        right_widget = QWidget()
        right_widget.setMinimumWidth(180)
        right_widget.setMaximumWidth(280)
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(4)
        
        # === Plot Settings Group ===
        settings_group = QGroupBox("Plot Settings")
        settings_layout = QFormLayout(settings_group)
        settings_layout.setContentsMargins(4, 8, 4, 4)
        settings_layout.setSpacing(4)
        
        # Title
        self._title_edit = QLineEdit("Impedance")
        self._title_edit.setPlaceholderText("Plot title")
        self._title_edit.textChanged.connect(self._on_settings_changed)
        settings_layout.addRow("Title:", self._title_edit)
        
        # X Label
        self._xlabel_edit = QLineEdit("Frequency [Hz]")
        self._xlabel_edit.setPlaceholderText("X-axis label")
        self._xlabel_edit.textChanged.connect(self._on_settings_changed)
        settings_layout.addRow("X Label:", self._xlabel_edit)
        
        # Y Label
        self._ylabel_edit = QLineEdit("Z [Ω]")
        self._ylabel_edit.setPlaceholderText("Y-axis label")
        self._ylabel_edit.textChanged.connect(self._on_settings_changed)
        settings_layout.addRow("Y Label:", self._ylabel_edit)
        
        # Scale options disponibili in matplotlib
        scale_options = ['linear', 'log', 'symlog', 'logit', 'asinh']
        
        # X Scale
        self._xscale_combo = QComboBox()
        self._xscale_combo.setView(QListView())  # Fix visualizzazione dropdown
        self._xscale_combo.addItems(scale_options)
        self._xscale_combo.setCurrentText("log")
        self._xscale_combo.currentTextChanged.connect(self._on_settings_changed)
        settings_layout.addRow("X Scale:", self._xscale_combo)
        
        # Y Scale
        self._yscale_combo = QComboBox()
        self._yscale_combo.setView(QListView())  # Fix visualizzazione dropdown
        self._yscale_combo.addItems(scale_options)
        self._yscale_combo.setCurrentText("log")
        self._yscale_combo.currentTextChanged.connect(self._on_settings_changed)
        settings_layout.addRow("Y Scale:", self._yscale_combo)
        
        right_layout.addWidget(settings_group)
        
        # === Plotted Impedances Group ===
        list_group = QGroupBox("Plotted Impedances")
        list_layout = QVBoxLayout(list_group)
        list_layout.setContentsMargins(4, 8, 4, 4)
        list_layout.setSpacing(2)
        
        # Info label
        self._info_label = QLabel("Drag impedances here")
        self._info_label.setStyleSheet("color: #78909C; font-size: 9px; font-style: italic;")
        list_layout.addWidget(self._info_label)
        
        # List
        self._list = QListWidget()
        self._list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._list.itemChanged.connect(self._on_item_changed)
        
        # Context menu
        self._list.setContextMenuPolicy(Qt.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        
        # Enable drop on list
        self._list.setAcceptDrops(True)
        self._list.dragEnterEvent = self._drag_enter
        self._list.dragMoveEvent = self._drag_move
        self._list.dropEvent = self._drop_event
        
        list_layout.addWidget(self._list, stretch=1)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(2)
        
        self._plot_btn = QPushButton("Update Plot")
        self._plot_btn.setFixedHeight(24)
        self._plot_btn.clicked.connect(self._update_plot)
        btn_layout.addWidget(self._plot_btn)
        
        self._clear_btn = QPushButton("Clear")
        self._clear_btn.setFixedHeight(24)
        self._clear_btn.clicked.connect(self.clear)
        btn_layout.addWidget(self._clear_btn)
        
        list_layout.addLayout(btn_layout)
        
        # Selection buttons
        sel_layout = QHBoxLayout()
        sel_layout.setSpacing(2)
        
        self._select_all_btn = QPushButton("All")
        self._select_all_btn.setFixedHeight(22)
        self._select_all_btn.setFixedWidth(40)
        self._select_all_btn.clicked.connect(self._select_all)
        sel_layout.addWidget(self._select_all_btn)
        
        self._select_none_btn = QPushButton("None")
        self._select_none_btn.setFixedHeight(22)
        self._select_none_btn.setFixedWidth(40)
        self._select_none_btn.clicked.connect(self._select_none)
        sel_layout.addWidget(self._select_none_btn)
        
        sel_layout.addStretch()
        list_layout.addLayout(sel_layout)
        
        right_layout.addWidget(list_group, stretch=1)
        
        # Add to main layout
        layout.addWidget(plot_widget, stretch=1)
        layout.addWidget(right_widget)
        
        # Style
        self._list.setStyleSheet("""
            QListWidget {
                background-color: #FAFAFA;
                border: 1px solid #B0BEC5;
                font-size: 9px;
            }
            QListWidget::item {
                padding: 3px;
            }
            QListWidget::item:selected {
                background-color: #BBDEFB;
            }
        """)
    
    def _drag_enter(self, event):
        """Handle drag enter."""
        if event.mimeData().hasFormat("application/x-pytlwall-impedance"):
            event.acceptProposedAction()
        elif event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _drag_move(self, event):
        """Handle drag move."""
        if event.mimeData().hasFormat("application/x-pytlwall-impedance"):
            event.acceptProposedAction()
        elif event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _drop_event(self, event):
        """Handle drop - extract data and emit signal for MainWindow to handle."""
        mime = event.mimeData()
        
        # Check for custom MIME type first
        if mime.hasFormat("application/x-pytlwall-impedance"):
            data = bytes(mime.data("application/x-pytlwall-impedance")).decode('utf-8')
            if "|" in data:
                chamber_name, impedance_name = data.split("|", 1)
                self.impedance_drop_requested.emit(chamber_name, impedance_name)
                event.acceptProposedAction()
                return
        
        # Fallback to text
        if mime.hasText():
            text = mime.text()
            if "|" in text:
                chamber_name, impedance_name = text.split("|", 1)
                self.impedance_drop_requested.emit(chamber_name, impedance_name)
                event.acceptProposedAction()
                return
        
        event.ignore()
    
    # Override Qt drag/drop methods for the PlotPanel widget itself
    def dragEnterEvent(self, event):
        """Qt drag enter event handler."""
        self._drag_enter(event)
    
    def dragMoveEvent(self, event):
        """Qt drag move event handler."""
        self._drag_move(event)
    
    def dropEvent(self, event):
        """Qt drop event handler."""
        self._drop_event(event)
    
    def _on_item_changed(self, item: ImpedanceListItem):
        """Handle checkbox state change and label editing."""
        if isinstance(item, ImpedanceListItem):
            # Aggiorna visibilità
            item.plot_item.visible = (item.checkState() == Qt.Checked)
            
            # Aggiorna label se è stata modificata
            new_text = item.text()
            if new_text != item.plot_item.label:
                item.plot_item.label = new_text
            
            self._update_plot()
    
    def _show_context_menu(self, pos):
        """Show context menu."""
        item = self._list.itemAt(pos)
        
        menu = QMenu(self)
        
        if item and isinstance(item, ImpedanceListItem):
            # Edit label
            action = menu.addAction("Edit Label")
            action.triggered.connect(lambda: self._edit_item_label(item))
            
            # Reset label
            action = menu.addAction("Reset Label")
            action.triggered.connect(lambda: self._reset_item_label(item))
            
            menu.addSeparator()
            
            action = menu.addAction(f"Remove '{item.plot_item.full_name}'")
            action.triggered.connect(lambda: self._remove_item(item))
            
            if item.plot_item.visible:
                action = menu.addAction("Hide")
                action.triggered.connect(lambda: self._toggle_item(item, False))
            else:
                action = menu.addAction("Show")
                action.triggered.connect(lambda: self._toggle_item(item, True))
            
            menu.addSeparator()
        
        # Remove selected
        selected = self._list.selectedItems()
        if len(selected) > 1:
            action = menu.addAction(f"Remove {len(selected)} selected")
            action.triggered.connect(self._remove_selected)
        
        menu.addSeparator()
        
        action = menu.addAction("Clear All")
        action.triggered.connect(self.clear)
        
        menu.exec_(self._list.mapToGlobal(pos))
    
    def _remove_item(self, item: ImpedanceListItem):
        """Remove single item."""
        if item.plot_item in self._items:
            self._items.remove(item.plot_item)
            self.impedance_removed.emit(item.plot_item.full_name)
        
        row = self._list.row(item)
        self._list.takeItem(row)
        
        self._update_plot()
        self._update_info()
    
    def _edit_item_label(self, item: ImpedanceListItem):
        """Start editing the item label."""
        self._list.editItem(item)
    
    def _reset_item_label(self, item: ImpedanceListItem):
        """Reset item label to default."""
        item.plot_item.label = None  # Reset to default
        item.setText(item.plot_item.label)
        self._update_plot()
    
    def _remove_selected(self):
        """Remove selected items."""
        selected = self._list.selectedItems()
        for item in selected:
            if isinstance(item, ImpedanceListItem):
                self._remove_item(item)
    
    def _toggle_item(self, item: ImpedanceListItem, visible: bool):
        """Toggle item visibility."""
        item.plot_item.visible = visible
        item.setCheckState(Qt.Checked if visible else Qt.Unchecked)
        self._update_plot()
    
    def _select_all(self):
        """Check all items."""
        for i in range(self._list.count()):
            item = self._list.item(i)
            if isinstance(item, ImpedanceListItem):
                item.setCheckState(Qt.Checked)
    
    def _select_none(self):
        """Uncheck all items."""
        for i in range(self._list.count()):
            item = self._list.item(i)
            if isinstance(item, ImpedanceListItem):
                item.setCheckState(Qt.Unchecked)
    
    def _on_settings_changed(self):
        """Handle changes to plot settings."""
        self._update_plot()
    
    def _update_plot(self):
        """Update the plot with current items and settings."""
        # Get settings from controls
        title = self._title_edit.text() or "Impedance"
        xlabel = self._xlabel_edit.text() or "Frequency [Hz]"
        ylabel = self._ylabel_edit.text() or "Z [Ω]"
        xscale = self._xscale_combo.currentText()
        yscale = self._yscale_combo.currentText()
        
        # Update title if multiple items
        if len(self._items) > 1 and self._title_edit.text() == "Impedance":
            title = "Impedance Overlay"
        
        self._canvas.plot_items(
            self._items, 
            title=title,
            xlabel=xlabel,
            ylabel=ylabel,
            xscale=xscale,
            yscale=yscale
        )
    
    def _update_info(self):
        """Update info label."""
        n_items = len(self._items)
        if n_items == 0:
            self._info_label.setText("Drag impedances here")
        else:
            n_visible = sum(1 for item in self._items if item.visible)
            self._info_label.setText(f"{n_visible}/{n_items} visible")
    
    # Public API
    def add_impedance(self, chamber_name: str, impedance_name: str,
                     data: np.ndarray, frequencies: np.ndarray,
                     component: str = "Abs"):
        """
        Add impedance to plot.
        
        Args:
            chamber_name: Name of source chamber
            impedance_name: Name of impedance (e.g., "ZLong")
            data: Complex impedance array
            frequencies: Frequency array
            component: "Re", "Im", or "Abs"
        """
        # Check if already exists
        full_name = f"{chamber_name} {impedance_name}_{component}"
        for item in self._items:
            if item.full_name == full_name:
                return  # Already exists
        
        # Get data component
        # Se data è già float (non complesso), usalo direttamente
        if component == "Re":
            plot_data = np.real(data) if np.iscomplexobj(data) else data
        elif component == "Im":
            plot_data = np.imag(data) if np.iscomplexobj(data) else data
        else:  # Abs
            plot_data = np.abs(data)
        
        # Create plot item
        color = self._canvas.get_next_color()
        plot_item = PlotItem(chamber_name, impedance_name, component, plot_data, frequencies, color)
        self._items.append(plot_item)
        
        # Add to list
        list_item = ImpedanceListItem(plot_item)
        self._list.addItem(list_item)
        
        self._update_plot()
        self._update_info()
    
    def remove_impedance(self, chamber_name: str, impedance_name: str, component: str = None):
        """Remove impedance from plot."""
        to_remove = []
        for item in self._items:
            if item.chamber_name == chamber_name and item.impedance_name == impedance_name:
                if component is None or item.component == component:
                    to_remove.append(item)
        
        for item in to_remove:
            self._items.remove(item)
            # Remove from list
            for i in range(self._list.count()):
                list_item = self._list.item(i)
                if isinstance(list_item, ImpedanceListItem) and list_item.plot_item == item:
                    self._list.takeItem(i)
                    break
        
        self._update_plot()
        self._update_info()
    
    def has_impedance(self, chamber_name: str, impedance_name: str, component: str = "Abs") -> bool:
        """Check if impedance is already plotted."""
        full_name = f"{chamber_name} {impedance_name}_{component}"
        return any(item.full_name == full_name for item in self._items)
    
    def get_item_count(self) -> int:
        """Get number of plotted items."""
        return len(self._items)
    
    def clear(self):
        """Clear all plotted items."""
        self._items.clear()
        self._list.clear()
        self._canvas.clear()
        self._canvas.reset_color_index()
        self._update_info()
    
    def save_plot(self, filepath: str) -> bool:
        """Save current plot to file."""
        return self._canvas.save_figure(filepath)
    
    # Legacy API
    def set_data(self, frequencies: np.ndarray, impedances: Dict[str, np.ndarray]):
        """Legacy method - add impedances from dict."""
        # Don't clear, just add new ones
        for name, data in impedances.items():
            if not self.has_impedance("Current", name, "Abs"):
                self.add_impedance("Current", name, data, frequencies, "Abs")
    
    def get_canvas(self) -> PlotCanvas:
        return self._canvas
