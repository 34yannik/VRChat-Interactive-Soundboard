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
    """Obere Navigationsleiste des Programms"""

    volume_changed = Signal(int)
    columns_changed = Signal(int)
    search_changed = Signal(str)
    settings_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_columns = 4
        self.setFixedHeight(50)
        self.setStyleSheet("background-color: #0a0a16; border-bottom: 1px solid #1a1a30;")
        self._setup_ui()

    def _setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(14, 0, 16, 0)
        layout.setSpacing(4)

        # App-Logo / Icon
        app_icon_label = QLabel("🎮")
        app_icon_label.setStyleSheet("font-size: 20px;")
        app_icon_label.setFixedWidth(32)
        layout.addWidget(app_icon_label)

        # Settings-Button
        settings_btn = QPushButton("Settings ▾")
        settings_btn.setStyleSheet(TOPBAR_BUTTON_STYLE)
        settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        settings_btn.clicked.connect(self.settings_clicked.emit)
        layout.addWidget(settings_btn)

        # More-Button (fuer spaetere Erweiterungen)
        more_btn = QPushButton("More ▾")
        more_btn.setStyleSheet(TOPBAR_BUTTON_STYLE)
        more_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        layout.addWidget(more_btn)

        layout.addStretch()

        # Such-Icon
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("color: #555577;")
        layout.addWidget(search_icon)

        # Suchfeld
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
            QLineEdit:focus {
                border: 1px solid #4a6cf7;
            }
            QLineEdit::placeholder {
                color: #444466;
            }
        """)
        layout.addWidget(self.search_field)

        # Tastatur-Shortcut Anzeige
        shortcut_badge = QLabel("Ctrl+K")
        shortcut_badge.setStyleSheet(
            "color: #444466; font-size: 10px; background: #16162a; "
            "padding: 2px 7px; border-radius: 4px; border: 1px solid #2a2a45;"
        )
        layout.addWidget(shortcut_badge)

        layout.addSpacing(12)

        # Spalten-Auswahl Button
        self.columns_btn = QPushButton(f"⊞ {self.current_columns} Columns ▾")
        self.columns_btn.setStyleSheet(TOPBAR_BUTTON_STYLE)
        self.columns_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.columns_btn.clicked.connect(self._open_columns_menu)
        layout.addWidget(self.columns_btn)

        layout.addSpacing(12)

        # Lautstaerke-Icon
        volume_icon = QLabel("🔊")
        volume_icon.setStyleSheet("font-size: 14px;")
        layout.addWidget(volume_icon)

        # Lautstaerke-Slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(75)
        self.volume_slider.setFixedWidth(90)
        self.volume_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        self.volume_slider.valueChanged.connect(self._update_volume_label)
        self.volume_slider.setStyleSheet("""
            QSlider::groove:horizontal {
                background: #2a2a45;
                height: 4px;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #ddddee;
                width: 12px;
                height: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::sub-page:horizontal {
                background: #ddddee;
                border-radius: 2px;
            }
        """)
        layout.addWidget(self.volume_slider)

        # Lautstaerke-Prozentanzeige
        self.volume_label = QLabel("75%")
        self.volume_label.setFixedWidth(34)
        self.volume_label.setStyleSheet("color: #777799; font-size: 12px; background: transparent;")
        layout.addWidget(self.volume_label)

        layout.addSpacing(14)

        # VRChat Status-Punkt
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #22cc55; font-size: 11px;")
        layout.addWidget(self.status_dot)

        # VRChat Status-Text
        self.status_text = QLabel("VRChat Connected")
        self.status_text.setStyleSheet("color: #777799; font-size: 12px;")
        layout.addWidget(self.status_text)

    def _update_volume_label(self, value):
        self.volume_label.setText(f"{value}%")

    def _open_columns_menu(self):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #16162a;
                color: #ccccdd;
                border: 1px solid #2a2a45;
                border-radius: 6px;
                padding: 4px;
            }
            QMenu::item {
                padding: 6px 16px;
                border-radius: 4px;
            }
            QMenu::item:selected {
                background-color: #2a2a45;
            }
        """)
        for num_columns in [2, 3, 4, 5, 6]:
            menu.addAction(f"{num_columns} Columns", lambda c=num_columns: self._set_columns(c))

        button_bottom_left = self.columns_btn.mapToGlobal(self.columns_btn.rect().bottomLeft())
        menu.exec(button_bottom_left)

    def _set_columns(self, columns):
        self.current_columns = columns
        self.columns_btn.setText(f"⊞ {columns} Columns ▾")
        self.columns_changed.emit(columns)

    def set_vrchat_status(self, connected):
        """Zeigt gruen fuer verbunden, rot fuer getrennt"""
        if connected:
            self.status_dot.setStyleSheet("color: #22cc55; font-size: 11px;")
            self.status_text.setText("VRChat Connected")
        else:
            self.status_dot.setStyleSheet("color: #cc3322; font-size: 11px;")
            self.status_text.setText("VRChat Disconnected")

    def set_initial_volume(self, volume):
        self.volume_slider.setValue(volume)
