from PySide6.QtWidgets import (QWidget, QHBoxLayout, QLabel, QPushButton,
                               QSlider, QLineEdit, QMenu)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction

TOPBAR_BUTTON_STYLE = """
    QPushButton {
        background: transparent;
        color: #ccccdd;
        border: none;
        padding: 5px 12px;
        font-size: 13px;
        border-radius: 5px;
    }
    QPushButton:hover {
        background: #1c1c30;
    }
"""


class TopBarWidget(QWidget):
    volume_changed = Signal(int)
    columns_changed = Signal(int)
    rows_changed = Signal(int)
    search_changed = Signal(str)
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_columns = 4
        self.current_rows = 4
        self.setFixedHeight(50)
        self.setStyleSheet("TopBarWidget { background-color: #0a0a16; border-bottom: 1px solid #1a1a30; }")
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 16, 0)
        layout.setSpacing(4)

        settings_btn = QPushButton("Settings")
        settings_btn.setStyleSheet(TOPBAR_BUTTON_STYLE)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn)

        more_btn = QPushButton("More ▾")
        more_btn.setStyleSheet(TOPBAR_BUTTON_STYLE)
        more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(more_btn)

        layout.addStretch()

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search sounds, hotkeys...")
        self.search_field.setFixedWidth(200)
        self.search_field.textChanged.connect(self.search_changed.emit)
        self.search_field.setStyleSheet("""
            QLineEdit {
                background-color: #16162a;
                color: #ccccdd;
                border: 1px solid #2a2a45;
                border-radius: 6px;
                padding: 4px 10px;
                font-size: 12px;
            }
            QLineEdit:focus { border: 1px solid #4a6cf7; }
            QLineEdit::placeholder { color: #444466; }
        """)
        layout.addWidget(self.search_field)

        # Columns-Button
        self.columns_btn = QPushButton(f"{self.current_columns} Columns ▾")
        self.columns_btn.setStyleSheet(TOPBAR_BUTTON_STYLE)
        self.columns_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.columns_btn.clicked.connect(self._open_columns_menu)
        layout.addWidget(self.columns_btn)

        # Rows-Button (neu)
        self.rows_btn = QPushButton(f"{self.current_rows} Rows ▾")
        self.rows_btn.setStyleSheet(TOPBAR_BUTTON_STYLE)
        self.rows_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.rows_btn.clicked.connect(self._open_rows_menu)
        layout.addWidget(self.rows_btn)

        layout.addSpacing(12)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setFixedWidth(90)
        self.volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.volume_slider.valueChanged.connect(self._update_volume_label)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal { background: #2a2a45; height: 4px; border-radius: 2px; }
            QSlider::handle:horizontal { background: #ddddee; width: 12px; height: 12px; margin: -4px 0; border-radius: 6px; }
            QSlider::sub-page:horizontal { background: #ddddee; border-radius: 2px; }
        """)
        layout.addWidget(self.volume_slider)

        self.volume_label = QLabel("75%")
        self.volume_label.setFixedWidth(34)
        self.volume_label.setStyleSheet("color: #777799; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self.volume_label)

        layout.addSpacing(14)

        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #22cc55; font-size: 11px; background: transparent; border: none;")
        layout.addWidget(self.status_dot)

        self.status_text = QLabel("VRChat Connected")
        self.status_text.setStyleSheet("color: #777799; font-size: 12px; background: transparent; border: none;")
        layout.addWidget(self.status_text)

    def _update_volume_label(self, value):
        self.volume_label.setText(f"{value}%")

    def _open_columns_menu(self):
        menu = self._make_menu()
        for n in range(2, 13):
            menu.addAction(f"{n} Columns", lambda c=n: self._set_columns(c))
        menu.exec(self.columns_btn.mapToGlobal(self.columns_btn.rect().bottomLeft()))

    def _open_rows_menu(self):
        menu = self._make_menu()
        for n in range(1, 13):
            menu.addAction(f"{n} Rows", lambda r=n: self._set_rows(r))
        menu.exec(self.rows_btn.mapToGlobal(self.rows_btn.rect().bottomLeft()))

    def _make_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #16162a; color: #ccccdd; border: 1px solid #2a2a45; border-radius: 6px; padding: 4px; }
            QMenu::item { padding: 6px 16px; border-radius: 4px; }
            QMenu::item:selected { background-color: #2a2a45; }
        """)
        return menu

    def _set_columns(self, columns):
        self.current_columns = columns
        self.columns_btn.setText(f"{columns} Columns ▾")
        self.columns_changed.emit(columns)

    def _set_rows(self, rows):
        self.current_rows = rows
        self.rows_btn.setText(f"{rows} Rows ▾")
        self.rows_changed.emit(rows)

    def set_vrchat_status(self, connected):
        if connected:
            self.status_dot.setStyleSheet("color: #22cc55; font-size: 11px; background: transparent; border: none;")
            self.status_text.setText("VRChat Connected")
        else:
            self.status_dot.setStyleSheet("color: #cc3322; font-size: 11px; background: transparent; border: none;")
            self.status_text.setText("VRChat Disconnected")

    def set_initial_volume(self, volume):
        self.volume_slider.setValue(volume)