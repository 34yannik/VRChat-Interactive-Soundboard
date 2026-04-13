import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFileDialog, QComboBox,
                               QFormLayout, QWidget, QSpinBox, QCheckBox)
from PySide6.QtCore import Qt
import fancify_text
from data_manager import get_data_manager

# Gemeinsamer Style fuer alle Dialoge
DIALOG_STYLE = """
    QDialog {
        background-color: #0d0d1e;
    }
    QLabel {
        color: #aaaacc;
        background: transparent;
    }
    QLineEdit, QSpinBox, QComboBox {
        background-color: #16162a;
        color: #ddddee;
        border: 1px solid #2a2a45;
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 13px;
    }
    QLineEdit:focus, QSpinBox:focus {
        border: 1px solid #4a6cf7;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox QAbstractItemView {
        background-color: #16162a;
        color: #ddddee;
        border: 1px solid #2a2a45;
        selection-background-color: #2a2a45;
    }
"""

CANCEL_BTN_STYLE = """
    QPushButton {
        background: #1e1e35;
        color: #aaaacc;
        border: none;
        padding: 8px 18px;
        border-radius: 6px;
        font-size: 13px;
    }
    QPushButton:hover { background: #2a2a45; }
"""

CONFIRM_BTN_STYLE = """
    QPushButton {
        background-color: #4a6cf7;
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #5a7cf7; }
"""


class AddSoundDialog(QDialog):
    """Fenster zum Hinzufuegen eines neuen Sounds zur aktuellen Page"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sound hinzufuegen")
        self.setFixedSize(420, 330)
        self.selected_file_path = ""
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        # Titel
        title_label = QLabel("Neuen Sound hinzufuegen")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # Formular
        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("z.B. Bruh Sound Effect #2")
        form.addRow("Name:", self.name_input)

        self.icon_input = QLineEdit()
        self.icon_input.setPlaceholderText("🔊")
        self.icon_input.setMaxLength(2)
        self.icon_input.setFixedWidth(60)
        form.addRow("Icon (Emoji):", self.icon_input)

        self.hotkey_input = QLineEdit()
        self.hotkey_input.setPlaceholderText("z.B. NUM 1")
        form.addRow("Hotkey:", self.hotkey_input)

        self.osc_message_input = QLineEdit()
        self.osc_message_input.setPlaceholderText("z.B. *bruh* (leer = keine Nachricht)")
        form.addRow("OSC Chatbox:", self.osc_message_input)

        layout.addLayout(form)

        # Datei-Auswahl
        file_row = QHBoxLayout()
        self.file_name_label = QLabel("Keine Datei ausgewaehlt")
        self.file_name_label.setStyleSheet("color: #555577; font-size: 12px; background: transparent;")

        browse_btn = QPushButton("Datei waehlen...")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._open_file_dialog)
        browse_btn.setStyleSheet(CANCEL_BTN_STYLE)

        file_row.addWidget(self.file_name_label, stretch=1)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        layout.addStretch()

        # Bestaetigungs-Buttons
        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        add_btn = QPushButton("Hinzufuegen")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.accept)
        add_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(add_btn)
        layout.addLayout(button_row)

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Audio-Datei auswaehlen",
            "",
            "Audio-Dateien (*.mp3 *.wav *.ogg *.flac *.m4a);;Alle Dateien (*.*)"
        )
        if file_path:
            self.selected_file_path = file_path
            file_name = os.path.basename(file_path)
            self.file_name_label.setText(file_name)
            self.file_name_label.setStyleSheet("color: #aaaacc; font-size: 12px; background: transparent;")

            # Name automatisch befuellen wenn noch leer
            if not self.name_input.text():
                name_without_extension = os.path.splitext(file_name)[0]
                self.name_input.setText(name_without_extension)

    def get_sound_data(self):
        """Gibt alle eingegebenen Daten als Dictionary zurueck"""
        return {
            "name": self.name_input.text().strip() or "Unbekannter Sound",
            "icon": self.icon_input.text().strip() or "🔊",
            "hotkey": self.hotkey_input.text().strip(),
            "osc_message": self.osc_message_input.text().strip(),
            "file_path": self.selected_file_path,
            "duration": "0:00"  # wird nach dem Hinzufuegen berechnet
        }


class AddCollectionDialog(QDialog):
    """Fenster zum Erstellen einer neuen Collection"""

    AVAILABLE_ICONS = ["🎮", "🎭", "🎵", "💥", "😂", "🔊", "🎤", "🎸", "🌟", "🔥", "🎯", "🎲"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Collection erstellen")
        self.setFixedSize(360, 220)
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Neue Collection erstellen")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("z.B. Funny Moments")
        form.addRow("Name:", self.name_input)

        self.icon_combo = QComboBox()
        for icon in self.AVAILABLE_ICONS:
            self.icon_combo.addItem(icon)
        form.addRow("Icon:", self.icon_combo)

        layout.addLayout(form)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        create_btn = QPushButton("Erstellen")
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self.accept)
        create_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(create_btn)
        layout.addLayout(button_row)

    def get_data(self):
        return {
            "name": self.name_input.text().strip() or "Neue Collection",
            "icon": self.icon_combo.currentText()
        }

class DeleteCollectionDialog(QDialog):
    """Sicherheitsdialog zum Löschen einer Collection"""

    def __init__(self, collection_name, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Collection löschen")
        self.setFixedSize(320, 160)

        self._setup_ui(collection_name)
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self, collection_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(f"Delete Collection '{collection_name}'?")
        label.setStyleSheet("color: white; font-size: 13px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.accept)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a1515;
                color: #ff4d4d;
                border: 1px solid #5a1f1f;
                padding: 8px 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4a1a1a;
            }
        """)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)

        layout.addLayout(btn_row)

class EditCollectionDialog(QDialog):
    """Fenster zum Bearbeiten einer Collection"""

    AVAILABLE_ICONS = ["🎮", "🎭", "🎵", "💥", "😂", "🔊", "🎤", "🎸", "🌟", "🔥", "🎯", "🎲"]

    def __init__(self, current_name, current_icon, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Collection bearbeiten")
        self.setFixedSize(360, 220)

        self._setup_ui(current_name, current_icon)
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self, current_name, current_icon):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Collection bearbeiten")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setText(current_name)
        form.addRow("Name:", self.name_input)

        self.icon_combo = QComboBox()
        for icon in self.AVAILABLE_ICONS:
            self.icon_combo.addItem(icon)

        # aktuelles Icon setzen
        index = self.icon_combo.findText(current_icon)
        if index >= 0:
            self.icon_combo.setCurrentIndex(index)

        form.addRow("Icon:", self.icon_combo)

        layout.addLayout(form)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Speichern")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)

        layout.addLayout(button_row)

    def get_data(self):
        return {
            "name": self.name_input.text().strip() or "Collection",
            "icon": self.icon_combo.currentText()
        }

class EditPageDialog(QDialog):
    """Dialog zum Bearbeiten eines Page-Namens"""

    def __init__(self, current_name, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Page bearbeiten")
        self.setFixedSize(360, 200)

        self._setup_ui(current_name)
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self, current_name):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title = QLabel("Page bearbeiten")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setText(current_name)
        self.name_input.setPlaceholderText("z.B. Main Sounds")

        form.addRow("Name:", self.name_input)

        layout.addLayout(form)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Speichern")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)

        layout.addLayout(button_row)

    def get_name(self):
        return self.name_input.text().strip() or "Page"

class DeletePageDialog(QDialog):
    """Sicherheitsdialog zum Löschen einer Page"""

    def __init__(self, page_name, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Page löschen")
        self.setFixedSize(320, 160)

        self._setup_ui(page_name)
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self, page_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        label = QLabel(f"Delete Page '{page_name}'?")
        label.setStyleSheet("color: white; font-size: 13px;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(label)
        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        delete_btn = QPushButton("Delete")
        delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        delete_btn.clicked.connect(self.accept)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #3a1515;
                color: #ff4d4d;
                border: 1px solid #5a1f1f;
                padding: 8px 14px;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #4a1a1a;
            }
        """)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)

        layout.addLayout(btn_row)

class SettingsDialog(QDialog):
    """Einstellungs-Fenster fuer OSC und andere Optionen"""

    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Einstellungen")
        self.setFixedSize(400, 320)
        self.current_settings = current_settings
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Einstellungen")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # OSC-Einstellungen
        osc_label = QLabel("VRChat OSC Verbindung")
        osc_label.setStyleSheet("color: #777799; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(osc_label)

        form = QFormLayout()
        form.setSpacing(10)

        self.osc_host_input = QLineEdit()
        self.osc_host_input.setText(self.current_settings.get("osc_host", "127.0.0.1"))
        form.addRow("OSC Host (IP):", self.osc_host_input)

        self.osc_port_input = QSpinBox()
        self.osc_port_input.setRange(1024, 65535)
        self.osc_port_input.setValue(self.current_settings.get("osc_port", 9000))
        self.osc_port_input.setStyleSheet(
            "background-color: #16162a; color: #ddddee; border: 1px solid #2a2a45; "
            "border-radius: 6px; padding: 4px 8px;"
        )
        form.addRow("OSC Port:", self.osc_port_input)

        layout.addLayout(form)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        # ---------------- FONT SETTING ----------------
        font_label = QLabel("Chatbox Font")
        font_label.setStyleSheet("color: #777799; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(font_label)

        self.font_dropdown = QComboBox()
        self.font_dropdown.addItems(self.get_all_fonts())

        self.font_dropdown.setCurrentText(
            self.current_settings.get("font")
        )

        self.font_dropdown.setStyleSheet(
            "background-color: #16162a; color: #ddddee; border: 1px solid #2a2a45; "
            "border-radius: 6px; padding: 6px;"
        )

        layout.addWidget(self.font_dropdown)

        cancel_btn = QPushButton("Abbrechen")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Speichern")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        layout.addLayout(button_row)


    def get_settings(self):
        return {
            "osc_host": self.osc_host_input.text().strip(),
            "osc_port": self.osc_port_input.value(),
            "font": self.font_dropdown.currentText()
        }

    def get_all_fonts(self):
        fonts = list(fancify_text.fonts.keys())
        fonts.append("UwU")
        return fonts

    def save_and_close(self):
        settings = {
            "osc_host": self.osc_host_input.text().strip(),
            "osc_port": self.osc_port_input.value(),
            "font": self.font_dropdown.currentText()
        }

        dm = get_data_manager()
        dm.update_settings_bulk(settings)

        self.accept()