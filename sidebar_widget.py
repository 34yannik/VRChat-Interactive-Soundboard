from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QPushButton, QScrollArea, QProgressBar, QFrame,
                               QSpacerItem, QSizePolicy)
from PySide6.QtCore import Qt, Signal


class CollectionItem(QWidget):
    """Ein einzelner Eintrag in der Collections-Liste"""

    clicked = Signal(int)  # Gibt collection_id zurueck

    ACTIVE_STYLE = """
        CollectionItem {
            background-color: #1c1c38;
            border-radius: 8px;
        }
    """
    IDLE_STYLE = """
        CollectionItem {
            background: transparent;
            border-radius: 8px;
        }
        CollectionItem:hover {
            background-color: #141428;
        }
    """

    def __init__(self, collection_data, parent=None):
        super().__init__(parent)
        self.collection_data = collection_data
        self.is_active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(40)
        self._setup_ui()
        self._apply_style()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(10)

        # Emoji Icon
        self.icon_label = QLabel(self.collection_data.get("icon", "🎵"))
        self.icon_label.setStyleSheet("font-size: 15px; background: transparent;")
        self.icon_label.setFixedWidth(22)

        # Collection Name
        self.name_label = QLabel(self.collection_data["name"])
        self.name_label.setStyleSheet("font-size: 13px; background: transparent; color: #aaaacc;")

        layout.addWidget(self.icon_label)
        layout.addWidget(self.name_label)
        layout.addStretch()

    def _apply_style(self):
        if self.is_active:
            self.setStyleSheet(self.ACTIVE_STYLE)
            self.name_label.setStyleSheet(
                "font-size: 13px; background: transparent; color: white; font-weight: bold;"
            )
        else:
            self.setStyleSheet(self.IDLE_STYLE)
            self.name_label.setStyleSheet(
                "font-size: 13px; background: transparent; color: #888899;"
            )

    def set_active(self, active):
        self.is_active = active
        self._apply_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.collection_data["id"])


class SidebarWidget(QWidget):
    """Linke Seitenleiste - zeigt alle Collections und den Speicher-Status"""

    collection_selected = Signal(int)
    add_collection_clicked = Signal()

    collection_edit_requested = Signal(int)
    collection_delete_requested = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.collection_items = {}
        self.setFixedWidth(220)
        self.setStyleSheet("background-color: #0a0a16;")
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header "COLLECTIONS" + Plus-Button
        header_widget = QWidget()
        header_widget.setFixedHeight(50)
        header_widget.setStyleSheet("background: transparent;")
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(16, 0, 12, 0)

        header_label = QLabel("COLLECTIONS")
        header_label.setStyleSheet(
            "color: #555577; font-size: 10px; font-weight: bold; letter-spacing: 1.5px; background: transparent;"
        )

        add_collection_btn = QPushButton("+")
        add_collection_btn.setFixedSize(22, 22)
        add_collection_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_collection_btn.clicked.connect(self.add_collection_clicked.emit)
        add_collection_btn.setStyleSheet("""
            QPushButton {
                background: #1e1e35;
                color: #888899;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                line-height: 1;
            }
            QPushButton:hover {
                background: #2a2a4a;
                color: white;
            }
        """)

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        header_layout.addWidget(add_collection_btn)
        main_layout.addWidget(header_widget)

        # Scrollbarer Bereich fuer die Collection-Liste
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical {
                background: transparent;
                width: 4px;
            }
            QScrollBar::handle:vertical {
                background: #2a2a45;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.collections_container = QWidget()
        self.collections_container.setStyleSheet("background: transparent;")
        self.collections_layout = QVBoxLayout(self.collections_container)
        self.collections_layout.setContentsMargins(8, 4, 8, 8)
        self.collections_layout.setSpacing(2)
        self.collections_layout.addStretch()

        scroll_area.setWidget(self.collections_container)
        main_layout.addWidget(scroll_area, stretch=1)

        # Trennlinie vor Storage
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #1a1a30; max-height: 1px; border: none;")
        separator.setFixedHeight(1)
        main_layout.addWidget(separator)

        # Storage-Anzeige unten
        storage_widget = QWidget()
        storage_widget.setFixedHeight(56)
        storage_widget.setStyleSheet("background: transparent;")
        storage_layout = QVBoxLayout(storage_widget)
        storage_layout.setContentsMargins(16, 8, 16, 10)
        storage_layout.setSpacing(4)

        storage_row = QHBoxLayout()
        storage_text = QLabel("Storage")
        storage_text.setStyleSheet("color: #555577; font-size: 11px; background: transparent;")
        self.storage_amount_label = QLabel("0 / 5GB")
        self.storage_amount_label.setStyleSheet("color: #555577; font-size: 11px; background: transparent;")
        storage_row.addWidget(storage_text)
        storage_row.addStretch()
        storage_row.addWidget(self.storage_amount_label)

        self.storage_progress_bar = QProgressBar()
        self.storage_progress_bar.setRange(0, 100)
        self.storage_progress_bar.setValue(24)
        self.storage_progress_bar.setTextVisible(False)
        self.storage_progress_bar.setFixedHeight(3)
        self.storage_progress_bar.setStyleSheet("""
            QProgressBar {
                background-color: #1e1e35;
                border-radius: 2px;
                border: none;
            }
            QProgressBar::chunk {
                background-color: #4a6cf7;
                border-radius: 2px;
            }
        """)

        storage_layout.addLayout(storage_row)
        storage_layout.addWidget(self.storage_progress_bar)
        main_layout.addWidget(storage_widget)

    def load_collections(self, collections_list, active_id=None):
        """Laedt alle Collections in die Sidebar"""
        # Bestehende Items entfernen
        self.collection_items = {}
        while self.collections_layout.count():
            item = self.collections_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for collection_data in collections_list:
            item = CollectionItem(collection_data)
            item.clicked.connect(self._on_item_clicked)
            self.collection_items[collection_data["id"]] = item
            self.collections_layout.addWidget(item)

        self.collections_layout.addStretch()

        # Aktive Collection setzen
        if active_id and active_id in self.collection_items:
            self.collection_items[active_id].set_active(True)
        elif collections_list:
            first_id = collections_list[0]["id"]
            self.collection_items[first_id].set_active(True)

    def _on_item_clicked(self, collection_id):
        # Alle deaktivieren, nur geklickte aktivieren
        for item in self.collection_items.values():
            item.set_active(False)
        if collection_id in self.collection_items:
            self.collection_items[collection_id].set_active(True)
        self.collection_selected.emit(collection_id)

    def update_storage_display(self, used_gb, total_gb=5.0):
        """Aktualisiert die Speicheranzeige"""
        self.storage_amount_label.setText(f"{used_gb:.1f} / {total_gb}GB")
        percentage = int((used_gb / total_gb) * 100)
        self.storage_progress_bar.setValue(min(percentage, 100))
