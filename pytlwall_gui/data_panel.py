"""PyTlWall GUI - Data Panel with drag & drop support."""

from typing import Optional, Dict, List, Tuple, Any
from datetime import datetime
import numpy as np

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QMenu, QAction, QHeaderView, QAbstractItemView,
    QFileDialog, QMessageBox, QLabel, QLineEdit, QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush


class DataColumn:
    """Represents a data column in the table."""
    
    def __init__(self, chamber_name: str, impedance_name: str, component: str, data: np.ndarray):
        """
        Args:
            chamber_name: Name of the source chamber
            impedance_name: Name of the impedance (e.g., "ZLong")
            component: "Re", "Im", or "Abs"
            data: numpy array of values
        """
        self.chamber_name = chamber_name
        self.impedance_name = impedance_name
        self.component = component
        self.data = data
        self._custom_name: Optional[str] = None  # User-defined column name
    
    @property
    def full_name(self) -> str:
        """Get full column name for display."""
        if self._custom_name:
            return self._custom_name
        return f"{self.chamber_name} {self.impedance_name}_{self.component}"
    
    @property
    def short_name(self) -> str:
        """Get short column name."""
        return f"{self.impedance_name}_{self.component}"
    
    def set_custom_name(self, name: str):
        """Set a custom display name for this column."""
        self._custom_name = name if name else None
    
    def get_custom_name(self) -> Optional[str]:
        """Get custom name if set."""
        return self._custom_name


class DataPanel(QWidget):
    """Panel containing the impedance data table with drag & drop support."""
    
    # Signals
    column_removed = pyqtSignal(str)  # column full_name
    impedance_drop_requested = pyqtSignal(str, str)  # chamber_name, impedance_name (e.g., "ZLongRe")
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._frequencies: Optional[np.ndarray] = None
        self._columns: List[DataColumn] = []
        self._freq_column_name: str = "f [Hz]"  # Customizable frequency column name
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Title (editable)
        title_layout = QHBoxLayout()
        title_layout.setSpacing(4)
        
        self._title_edit = QLineEdit()
        self._title_edit.setText(f"Data {datetime.now().strftime('%d/%m/%Y')}")
        self._title_edit.setStyleSheet("""
            QLineEdit {
                font-size: 12px;
                font-weight: bold;
                border: 1px solid transparent;
                background: transparent;
                padding: 2px 4px;
            }
            QLineEdit:hover {
                border: 1px solid #B0BEC5;
                background: #FAFAFA;
            }
            QLineEdit:focus {
                border: 1px solid #1976D2;
                background: white;
            }
        """)
        self._title_edit.setPlaceholderText("Enter table title...")
        title_layout.addWidget(self._title_edit)
        title_layout.addStretch()
        
        layout.addLayout(title_layout)
        
        # Toolbar
        toolbar = QHBoxLayout()
        toolbar.setSpacing(4)
        
        self._info_label = QLabel("Drag impedances here from chamber tree")
        self._info_label.setStyleSheet("color: #78909C; font-size: 9px; font-style: italic;")
        toolbar.addWidget(self._info_label)
        
        toolbar.addStretch()
        
        self._clear_btn = QPushButton("Clear All")
        self._clear_btn.setFixedHeight(22)
        self._clear_btn.clicked.connect(self.clear)
        toolbar.addWidget(self._clear_btn)
        
        layout.addLayout(toolbar)
        
        # Table
        self._table = QTableWidget()
        self._table.setAlternatingRowColors(True)
        self._table.setSelectionBehavior(QAbstractItemView.SelectColumns)
        self._table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # Enable drop
        self._table.setAcceptDrops(True)
        self._table.dragEnterEvent = self._drag_enter
        self._table.dragMoveEvent = self._drag_move
        self._table.dropEvent = self._drop_event
        
        # Context menu
        self._table.setContextMenuPolicy(Qt.CustomContextMenu)
        self._table.customContextMenuRequested.connect(self._show_context_menu)
        
        # Header context menu for removing columns
        header = self._table.horizontalHeader()
        header.setContextMenuPolicy(Qt.CustomContextMenu)
        header.customContextMenuRequested.connect(self._show_header_context_menu)
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        
        # Double-click on header to rename column
        header.sectionDoubleClicked.connect(self._on_header_double_clicked)
        
        layout.addWidget(self._table)
        
        # Style
        self._table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                gridline-color: #E0E0E0;
                font-size: 9px;
            }
            QTableWidget::item {
                padding: 2px 4px;
            }
            QTableWidget::item:selected {
                background-color: #BBDEFB;
                color: black;
            }
            QHeaderView::section {
                background-color: #ECEFF1;
                padding: 4px;
                border: 1px solid #B0BEC5;
                font-size: 9px;
                font-weight: bold;
            }
        """)
    
    def _drag_enter(self, event):
        """Handle drag enter event."""
        if event.mimeData().hasFormat("application/x-pytlwall-impedance"):
            event.acceptProposedAction()
        elif event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _drag_move(self, event):
        """Handle drag move event."""
        if event.mimeData().hasFormat("application/x-pytlwall-impedance"):
            event.acceptProposedAction()
        elif event.mimeData().hasText():
            event.acceptProposedAction()
        else:
            event.ignore()
    
    def _drop_event(self, event):
        """Handle drop event - extract data and emit signal for MainWindow to handle."""
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
    
    def _show_context_menu(self, pos):
        """Show context menu for table."""
        menu = QMenu(self)
        
        # Get selected columns
        selected = self._table.selectedItems()
        if selected:
            action = menu.addAction("Remove Selected Columns")
            action.triggered.connect(self._remove_selected_columns)
        
        menu.addSeparator()
        
        action = menu.addAction("Clear All")
        action.triggered.connect(self.clear)
        
        menu.exec_(self._table.mapToGlobal(pos))
    
    def _show_header_context_menu(self, pos):
        """Show context menu for header (column removal and rename)."""
        col = self._table.horizontalHeader().logicalIndexAt(pos)
        
        menu = QMenu(self)
        
        # Rename option (available for all columns including frequency)
        if col == 0:
            # Frequency column
            action = menu.addAction(f"Rename '{self._freq_column_name}'")
            action.triggered.connect(lambda: self._rename_frequency_column())
        elif col > 0:
            col_idx = col - 1  # Adjust for frequency column
            if col_idx < len(self._columns):
                col_data = self._columns[col_idx]
                
                # Rename action
                action = menu.addAction(f"Rename '{col_data.full_name}'")
                action.triggered.connect(lambda: self._rename_column(col_idx))
                
                menu.addSeparator()
                
                # Remove action
                action = menu.addAction(f"Remove '{col_data.full_name}'")
                action.triggered.connect(lambda: self._remove_column(col_idx))
        
        menu.exec_(self._table.horizontalHeader().mapToGlobal(pos))
    
    def _on_header_double_clicked(self, col: int):
        """Handle double-click on header to rename column."""
        if col == 0:
            self._rename_frequency_column()
        else:
            col_idx = col - 1
            if col_idx < len(self._columns):
                self._rename_column(col_idx)
    
    def _rename_frequency_column(self):
        """Rename the frequency column."""
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Frequency Column",
            "Enter new name for frequency column:",
            QLineEdit.Normal,
            self._freq_column_name
        )
        if ok and new_name.strip():
            self._freq_column_name = new_name.strip()
            self._rebuild_table()
    
    def _rename_column(self, col_idx: int):
        """Rename a data column."""
        if col_idx < 0 or col_idx >= len(self._columns):
            return
        
        col_data = self._columns[col_idx]
        current_name = col_data.full_name
        
        new_name, ok = QInputDialog.getText(
            self,
            "Rename Column",
            f"Enter new name for column:",
            QLineEdit.Normal,
            current_name
        )
        if ok and new_name.strip():
            col_data.set_custom_name(new_name.strip())
            self._rebuild_table()
    
    def _remove_selected_columns(self):
        """Remove selected columns."""
        selected_cols = set()
        for item in self._table.selectedItems():
            col = self._table.column(item)
            if col > 0:  # Don't remove frequency column
                selected_cols.add(col - 1)  # Adjust for frequency column
        
        # Remove in reverse order to maintain indices
        for col_idx in sorted(selected_cols, reverse=True):
            if col_idx < len(self._columns):
                self._remove_column(col_idx)
    
    def _remove_column(self, col_idx: int):
        """Remove a specific column."""
        if col_idx < 0 or col_idx >= len(self._columns):
            return
        
        col_data = self._columns[col_idx]
        self._columns.pop(col_idx)
        self.column_removed.emit(col_data.full_name)
        
        self._rebuild_table()
    
    def _rebuild_table(self):
        """Rebuild table with current columns."""
        if self._frequencies is None or not self._columns:
            self._table.clear()
            self._table.setRowCount(0)
            self._table.setColumnCount(0)
            self._info_label.setText("Drag impedances here from chamber tree")
            return
        
        n_rows = len(self._frequencies)
        n_cols = 1 + len(self._columns)  # freq + data columns
        
        self._table.clear()
        self._table.setRowCount(n_rows)
        self._table.setColumnCount(n_cols)
        
        # Headers (use customizable frequency column name)
        headers = [self._freq_column_name] + [col.full_name for col in self._columns]
        self._table.setHorizontalHeaderLabels(headers)
        
        # Fill data
        for row in range(n_rows):
            # Frequency column
            freq_val = self._frequencies[row]
            item = QTableWidgetItem(f"{freq_val:.6e}")
            item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            item.setBackground(QBrush(QColor("#F5F5F5")))
            self._table.setItem(row, 0, item)
            
            # Data columns
            for col_idx, col_data in enumerate(self._columns):
                value = col_data.data[row] if row < len(col_data.data) else 0
                text = f"{value:.6e}" if isinstance(value, (float, np.floating)) else str(value)
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                self._table.setItem(row, col_idx + 1, item)
        
        self._table.resizeColumnsToContents()
        self._info_label.setText(f"{len(self._columns)} columns")
    
    # Public API
    def add_impedance(self, chamber_name: str, impedance_name: str, 
                     data: np.ndarray, frequencies: np.ndarray,
                     component: str = None):
        """
        Add impedance data as columns.
        
        Args:
            chamber_name: Name of source chamber
            impedance_name: Name of impedance (e.g., "ZLong")
            data: Impedance array (real or complex)
            frequencies: Frequency array
            component: If None, add both Re and Im (if complex). 
                      If "Re" or "Im", add only that component.
        """
        # Set frequencies if not set
        if self._frequencies is None:
            self._frequencies = frequencies
        
        # Check frequency compatibility
        if len(frequencies) != len(self._frequencies):
            QMessageBox.warning(
                self, "Incompatible Data",
                f"Frequency array length mismatch:\n"
                f"Existing: {len(self._frequencies)}\n"
                f"New: {len(frequencies)}"
            )
            return
        
        if component == "Re":
            # Add only Real part
            re_data = np.real(data) if np.iscomplexobj(data) else data
            if not self._has_column(chamber_name, impedance_name, "Re"):
                self._columns.append(DataColumn(chamber_name, impedance_name, "Re", re_data))
        elif component == "Im":
            # Add only Imaginary part
            # Se data è già float (non complesso), usalo direttamente
            im_data = np.imag(data) if np.iscomplexobj(data) else data
            if not self._has_column(chamber_name, impedance_name, "Im"):
                self._columns.append(DataColumn(chamber_name, impedance_name, "Im", im_data))
        else:
            # Add both Re and Im (if complex)
            re_data = np.real(data) if np.iscomplexobj(data) else data
            if not self._has_column(chamber_name, impedance_name, "Re"):
                self._columns.append(DataColumn(chamber_name, impedance_name, "Re", re_data))
            
            if np.iscomplexobj(data):
                im_data = np.imag(data)
                if not self._has_column(chamber_name, impedance_name, "Im"):
                    self._columns.append(DataColumn(chamber_name, impedance_name, "Im", im_data))
        
        self._rebuild_table()
    
    def _has_column(self, chamber_name: str, impedance_name: str, component: str) -> bool:
        """Check if a specific column already exists."""
        for col in self._columns:
            if (col.chamber_name == chamber_name and 
                col.impedance_name == impedance_name and 
                col.component == component):
                return True
        return False
    
    def remove_impedance(self, chamber_name: str, impedance_name: str):
        """Remove all columns for a specific impedance."""
        # Find and remove matching columns
        to_remove = []
        for i, col in enumerate(self._columns):
            if col.chamber_name == chamber_name and col.impedance_name == impedance_name:
                to_remove.append(i)
        
        for idx in reversed(to_remove):
            self._columns.pop(idx)
        
        self._rebuild_table()
    
    def remove_columns_for_chamber(self, chamber_name: str) -> int:
        """
        Remove all columns belonging to a specific chamber.
        
        This is called when a chamber is recalculated to ensure stale data
        is removed from the DataPanel.
        
        Args:
            chamber_name: Name of the chamber whose columns should be removed.
            
        Returns:
            Number of columns removed.
        """
        to_remove = []
        for i, col in enumerate(self._columns):
            if col.chamber_name == chamber_name:
                to_remove.append(i)
        
        # Remove in reverse order to maintain correct indices
        for idx in reversed(to_remove):
            self._columns.pop(idx)
        
        if to_remove:
            self._rebuild_table()
        
        return len(to_remove)
    
    def has_impedance(self, chamber_name: str, impedance_name: str) -> bool:
        """Check if impedance is already in table."""
        for col in self._columns:
            if col.chamber_name == chamber_name and col.impedance_name == impedance_name:
                return True
        return False
    
    def set_frequencies(self, frequencies: np.ndarray):
        """Set the frequency array."""
        self._frequencies = frequencies
        self._rebuild_table()
    
    def get_data_as_dict(self) -> Dict[str, np.ndarray]:
        """Get all data as dictionary for saving."""
        result = {}
        if self._frequencies is not None:
            result[self._freq_column_name] = self._frequencies
        for col in self._columns:
            result[col.full_name] = col.data
        return result
    
    def get_column_count(self) -> int:
        """Get number of data columns (excluding frequency)."""
        return len(self._columns)
    
    def get_title(self) -> str:
        """Get the current table title."""
        return self._title_edit.text()
    
    def set_title(self, title: str):
        """Set the table title."""
        self._title_edit.setText(title)
    
    def clear(self):
        """Clear all data and reset to defaults."""
        self._table.clear()
        self._table.setRowCount(0)
        self._table.setColumnCount(0)
        self._columns.clear()
        self._frequencies = None
        self._freq_column_name = "f [Hz]"  # Reset to default
        self._title_edit.setText(f"Data {datetime.now().strftime('%d/%m/%Y')}")
        self._info_label.setText("Drag impedances here from chamber tree")
    
    # Legacy API for compatibility
    def set_data(self, frequencies: np.ndarray, impedances: Dict[str, np.ndarray]):
        """Legacy method - adds all impedances from dict."""
        self._frequencies = frequencies
        self._columns.clear()
        
        for name, data in impedances.items():
            re_data = np.real(data) if np.iscomplexobj(data) else data
            self._columns.append(DataColumn("Current", name, "Re", re_data))
            
            if np.iscomplexobj(data):
                im_data = np.imag(data)
                self._columns.append(DataColumn("Current", name, "Im", im_data))
        
        self._rebuild_table()
    
    def set_single_impedance(self, frequencies: np.ndarray, impedance: np.ndarray, name: str):
        """Legacy method - set single impedance."""
        self.clear()
        self._frequencies = frequencies
        self.add_impedance("Current", name, impedance, frequencies)
    
    def save_to_file(self, filepath: str) -> bool:
        """Save data to file (Excel or CSV).
        
        For Excel files, the title is used as the sheet name.
        For CSV files, the title is included as a comment in the first line.
        """
        try:
            import pandas as pd
            
            data = self.get_data_as_dict()
            if not data:
                return False
            
            df = pd.DataFrame(data)
            title = self.get_title()
            
            if filepath.endswith('.xlsx') or filepath.endswith('.xls'):
                # Use title as sheet name (sanitize for Excel)
                sheet_name = title[:31] if title else "Data"  # Excel sheet names max 31 chars
                # Remove invalid characters for sheet names
                invalid_chars = ['\\', '/', '*', '?', ':', '[', ']']
                for char in invalid_chars:
                    sheet_name = sheet_name.replace(char, '_')
                df.to_excel(filepath, index=False, sheet_name=sheet_name)
            else:
                # For CSV, add title as comment in first line
                with open(filepath, 'w', encoding='utf-8') as f:
                    if title:
                        f.write(f"# {title}\n")
                    df.to_csv(f, index=False)
            
            return True
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save data:\n{str(e)}")
            return False
