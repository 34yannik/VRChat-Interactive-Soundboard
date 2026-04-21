import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFileDialog, QComboBox,
                               QFormLayout, QWidget, QSpinBox, QCheckBox, QSlider)
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt, QKeyCombination
import fancify_text
from core.data_manager import get_data_manager
from core.audio_player import get_audio_outputs
from meta import __version__, __author__

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

VOLUME_SLIDER_STYLE = """
    QSlider::groove:horizontal {
        background: #2a2a45;
        height: 4px;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background: #4a6cf7;
        width: 14px;
        height: 14px;
        margin: -5px 0;
        border-radius: 7px;
    }
    QSlider::sub-page:horizontal {
        background: #4a6cf7;
        border-radius: 2px;
    }
"""


class HotkeyLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setPlaceholderText("Press any keys...")

    def keyPressEvent(self, event):
        key = Qt.Key(event.key())

        if key in (Qt.Key.Key_Control, Qt.Key.Key_Shift, Qt.Key.Key_Alt, Qt.Key.Key_Meta):
            return

        modifiers = event.modifiers()
        combination = QKeyCombination(modifiers, key)
        key_sequence = QKeySequence(combination)
        self.setText(key_sequence.toString())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.RightButton:
            self.clear()
        else:
            super().mousePressEvent(event)


def _make_volume_row(initial_value=100):
    """builds a volume slider row, returns (container_widget, slider, label)"""
    container = QWidget()
    container.setStyleSheet("background: transparent;")
    row_layout = QHBoxLayout(container)
    row_layout.setContentsMargins(0, 0, 0, 0)
    row_layout.setSpacing(8)

    slider = QSlider(Qt.Orientation.Horizontal)
    slider.setRange(0, 100)
    slider.setValue(initial_value)
    slider.setCursor(Qt.CursorShape.PointingHandCursor)
    slider.setStyleSheet(VOLUME_SLIDER_STYLE)

    label = QLabel(f"{initial_value}%")
    label.setFixedWidth(36)
    label.setStyleSheet("color: #aaaacc; font-size: 12px; background: transparent;")

    slider.valueChanged.connect(lambda v: label.setText(f"{v}%"))

    row_layout.addWidget(slider)
    row_layout.addWidget(label)

    return container, slider, label


class AddSoundDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Sound")
        self.setFixedSize(420, 370)
        self.selected_file_path = ""
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Add New Sound")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Bruh Sound Effect #2")
        form.addRow("Name:", self.name_input)

        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.setPlaceholderText("Press keys (e.g. Ctrl+Shift+S)")
        form.addRow("Hotkey:", self.hotkey_input)

        self.osc_message_input = QLineEdit()
        self.osc_message_input.setPlaceholderText("e.g. *bruh* (empty = no message)")
        form.addRow("OSC Chatbox:", self.osc_message_input)

        layout.addLayout(form)

        # per-sound volume slider
        vol_label = QLabel("Sound Volume:")
        vol_label.setStyleSheet("color: #aaaacc; font-size: 13px; background: transparent;")
        layout.addWidget(vol_label)

        vol_row, self.volume_slider, self.volume_label = _make_volume_row(100)
        layout.addWidget(vol_row)

        # file picker
        file_row = QHBoxLayout()
        self.file_name_label = QLabel("No file selected")
        self.file_name_label.setStyleSheet("color: #555577; font-size: 12px; background: transparent;")

        browse_btn = QPushButton("Select File...")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._open_file_dialog)
        browse_btn.setStyleSheet(CANCEL_BTN_STYLE)

        file_row.addWidget(self.file_name_label, stretch=1)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        add_btn = QPushButton("Add")
        add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_btn.clicked.connect(self.accept)
        add_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(add_btn)
        layout.addLayout(button_row)

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a);;All Files (*.*)"
        )
        if file_path:
            self.selected_file_path = file_path
            file_name = os.path.basename(file_path)
            self.file_name_label.setText(file_name)
            self.file_name_label.setStyleSheet("color: #aaaacc; font-size: 12px; background: transparent;")

            if not self.name_input.text():
                self.name_input.setText(os.path.splitext(file_name)[0])

    def get_sound_data(self):
        return {
            "name": self.name_input.text().strip() or "Unknown Sound",
            "hotkey": self.hotkey_input.text().strip(),
            "osc_message": self.osc_message_input.text().strip(),
            "file_path": self.selected_file_path,
            "volume": self.volume_slider.value(),
            "duration": "0:00"
        }


class EditSoundDialog(QDialog):

    def __init__(self, sound_data, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Sound")
        self.setFixedSize(420, 370)

        self.sound_id = sound_data.get("id")
        self.selected_file_path = sound_data.get("file_path", "")
        self.current_duration = sound_data.get("duration", "0:00")

        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)
        self._load_data(sound_data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Edit Sound Details")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        form = QFormLayout()
        form.setSpacing(10)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Bruh Sound Effect #2")
        form.addRow("Name:", self.name_input)

        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.setPlaceholderText("Press keys...")
        form.addRow("Hotkey:", self.hotkey_input)

        self.osc_message_input = QLineEdit()
        self.osc_message_input.setPlaceholderText("e.g. *bruh* (empty = no message)")
        form.addRow("OSC Chatbox:", self.osc_message_input)

        layout.addLayout(form)

        vol_label = QLabel("Sound Volume:")
        vol_label.setStyleSheet("color: #aaaacc; font-size: 13px; background: transparent;")
        layout.addWidget(vol_label)

        vol_row, self.volume_slider, self.volume_label = _make_volume_row(100)
        layout.addWidget(vol_row)

        file_row = QHBoxLayout()
        initial_file_name = os.path.basename(self.selected_file_path) if self.selected_file_path else "No file selected"
        self.file_name_label = QLabel(initial_file_name)
        self.file_name_label.setStyleSheet("color: #aaaacc; font-size: 12px; background: transparent;")

        browse_btn = QPushButton("Change File...")
        browse_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        browse_btn.clicked.connect(self._open_file_dialog)
        browse_btn.setStyleSheet(CANCEL_BTN_STYLE)

        file_row.addWidget(self.file_name_label, stretch=1)
        file_row.addWidget(browse_btn)
        layout.addLayout(file_row)

        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Save Changes")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        layout.addLayout(button_row)

    def _load_data(self, data):
        self.name_input.setText(data.get("name", ""))
        self.hotkey_input.setText(data.get("hotkey", ""))
        self.osc_message_input.setText(data.get("osc_message", ""))
        self.volume_slider.setValue(data.get("volume", 100))

    def _open_file_dialog(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select New Audio File",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a);;All Files (*.*)"
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_name_label.setText(os.path.basename(file_path))

    def get_sound_data(self):
        return {
            "id": self.sound_id,
            "name": self.name_input.text().strip() or "Unknown Sound",
            "hotkey": self.hotkey_input.text().strip(),
            "osc_message": self.osc_message_input.text().strip(),
            "file_path": self.selected_file_path,
            "volume": self.volume_slider.value(),
            "duration": self.current_duration
        }


class AddCollectionDialog(QDialog):

    AVAILABLE_ICONS = ["🎮", "🎭", "🎵", "💥", "😂", "🔊", "🎤", "🎸", "🌟", "🔥", "🎯", "🎲"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Collection")
        self.setFixedSize(360, 220)
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Create New Collection")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Funny Moments")
        form.addRow("Name:", self.name_input)

        self.icon_combo = QComboBox()
        for icon in self.AVAILABLE_ICONS:
            self.icon_combo.addItem(icon)
        form.addRow("Icon:", self.icon_combo)

        layout.addLayout(form)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        create_btn = QPushButton("Create")
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self.accept)
        create_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(create_btn)
        layout.addLayout(button_row)

    def get_data(self):
        return {
            "name": self.name_input.text().strip() or "New Collection",
            "icon": self.icon_combo.currentText()
        }


class DeleteCollectionDialog(QDialog):

    def __init__(self, collection_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Collection")
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
            QPushButton:hover { background-color: #4a1a1a; }
        """)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)
        layout.addLayout(btn_row)


class EditCollectionDialog(QDialog):

    AVAILABLE_ICONS = ["🎮", "🎭", "🎵", "💥", "😂", "🔊", "🎤", "🎸", "🌟", "🔥", "🎯", "🎲"]

    def __init__(self, current_name, current_icon, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Collection")
        self.setFixedSize(360, 220)
        self._setup_ui(current_name, current_icon)
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self, current_name, current_icon):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Edit Collection")
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

        index = self.icon_combo.findText(current_icon)
        if index >= 0:
            self.icon_combo.setCurrentIndex(index)

        form.addRow("Icon:", self.icon_combo)

        layout.addLayout(form)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Save")
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


class DeleteSoundDialog(QDialog):

    def __init__(self, sound_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Sound")
        self.setFixedSize(340, 170)
        self._setup_ui(sound_name)
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self, sound_name):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(15)

        label = QLabel(f"Delete sound\n'{sound_name}'?")
        label.setStyleSheet("color: white; font-size: 13px; line-height: 1.4;")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setWordWrap(True)
        layout.addWidget(label)

        layout.addStretch()

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

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
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4a1a1a;
                border-color: #ff4d4d;
            }
        """)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)
        layout.addLayout(btn_row)


class EditPageDialog(QDialog):

    def __init__(self, current_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Page")
        self.setFixedSize(360, 200)
        self._setup_ui(current_name)
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self, current_name):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title = QLabel("Edit Page")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.name_input = QLineEdit()
        self.name_input.setText(current_name)
        self.name_input.setPlaceholderText("e.g. Main Sounds")
        form.addRow("Name:", self.name_input)

        layout.addLayout(form)
        layout.addStretch()

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        layout.addLayout(button_row)

    def get_name(self):
        return self.name_input.text().strip() or "Page"


class DeletePageDialog(QDialog):

    def __init__(self, page_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Delete Page")
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
            QPushButton:hover { background-color: #4a1a1a; }
        """)

        btn_row.addWidget(cancel_btn)
        btn_row.addWidget(delete_btn)
        layout.addLayout(btn_row)


class SettingsDialog(QDialog):

    def __init__(self, current_settings, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setFixedSize(400, 560)
        self.current_settings = current_settings
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(22, 20, 22, 20)

        title_label = QLabel("Settings")
        title_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        info = QLabel(f"Version {__version__} by {__author__}")
        info.setStyleSheet("background: transparent; font-size: 12px; line-height: 1.6;")
        layout.addWidget(info)

        osc_label = QLabel("VRChat OSC Connection")
        osc_label.setStyleSheet("color: #777799; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(osc_label)

        osc_form = QFormLayout()
        osc_form.setSpacing(10)

        self.osc_host_input = QLineEdit()
        self.osc_host_input.setText(self.current_settings.get("osc_host", "127.0.0.1"))
        osc_form.addRow("OSC Host (IP):", self.osc_host_input)

        self.osc_port_input = QSpinBox()
        self.osc_port_input.setRange(1024, 65535)
        self.osc_port_input.setValue(self.current_settings.get("osc_port", 9000))
        self.osc_port_input.setStyleSheet(
            "background-color: #16162a; color: #ddddee; border: 1px solid #2a2a45; "
            "border-radius: 6px; padding: 4px 8px;"
        )
        osc_form.addRow("OSC Port:", self.osc_port_input)

        layout.addLayout(osc_form)

        chatbox_label = QLabel("Chatbox")
        chatbox_label.setStyleSheet("color: #777799; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(chatbox_label)

        chatbox_form = QFormLayout()
        chatbox_form.setSpacing(10)

        self.enable_chatbox = QCheckBox("Enable OSC Chatbox")
        self.enable_chatbox.setChecked(self.current_settings.get("enable_chatbox", True))
        chatbox_form.addRow(self.enable_chatbox)

        self.font_dropdown = QComboBox()
        self.font_dropdown.addItems(self.get_all_fonts())
        self.font_dropdown.setCurrentText(self.current_settings.get("font", ""))
        self.font_dropdown.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.font_dropdown.setEditable(False)
        self.font_dropdown.setStyleSheet(
            "background-color: #16162a; color: #ddddee; border: 1px solid #2a2a45; "
            "border-radius: 6px; padding: 6px;"
        )
        chatbox_form.addRow("Chatbox Font:", self.font_dropdown)

        layout.addLayout(chatbox_form)

        sound_label = QLabel("Sound Settings")
        sound_label.setStyleSheet("color: #777799; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(sound_label)

        self.enable_output = QCheckBox("Enable Output Device")
        self.enable_output.setChecked(self.current_settings.get("enable_output", True))
        layout.addWidget(self.enable_output)

        self.output_device = QComboBox()
        self.output_device.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.output_device.setEditable(False)
        self.output_device.addItems(get_audio_outputs())

        saved_output = self.current_settings.get("output_device", "")
        if saved_output:
            index = self.output_device.findText(saved_output)
            if index != -1:
                self.output_device.setCurrentIndex(index)

        self.output_device.setEnabled(self.enable_output.isChecked())
        layout.addWidget(self.output_device)

        self.enable_output.toggled.connect(self.output_device.setEnabled)

        storage_container = QHBoxLayout()

        storage_lbl = QLabel(f"%APPDATA%/VRCInteractiveSoundboard")
        storage_lbl.setStyleSheet(
            "color: #777799; background: transparent; font-size: 11px; font-family: monospace;")

        open_folder_btn = QPushButton("Open Folder")
        open_folder_btn.setFixedHeight(32)
        open_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)

        import os
        import subprocess

        def open_folder():
            folder = os.path.join(os.environ.get("APPDATA"), "VRLinks")
            os.makedirs(folder, exist_ok=True)
            subprocess.Popen(f'explorer "{folder}"')

        open_folder_btn.clicked.connect(open_folder)

        storage_container.addWidget(storage_lbl)
        storage_container.addStretch()
        storage_container.addWidget(open_folder_btn)

        layout.addLayout(storage_container)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Save")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.save_and_close)
        save_btn.setStyleSheet(CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        layout.addLayout(button_row)
        layout.addStretch()

    def get_all_fonts(self):
        fonts = list(fancify_text.fonts.keys())
        fonts.append("UwU")
        return fonts

    def get_settings(self):
        return {
            "osc_host": self.osc_host_input.text().strip(),
            "osc_port": self.osc_port_input.value(),
            "font": self.font_dropdown.currentText(),
            "enable_output": self.enable_output.isChecked(),
            "output_device": self.output_device.currentText(),
            "enable_chatbox": self.enable_chatbox.isChecked(),
        }

    def save_and_close(self):
        settings = {
            "osc_host": self.osc_host_input.text().strip(),
            "osc_port": self.osc_port_input.value(),
            "font": self.font_dropdown.currentText(),
            "enable_output": self.enable_output.isChecked(),
            "output_device": self.output_device.currentText(),
            "enable_chatbox": self.enable_chatbox.isChecked(),
        }
        dm = get_data_manager()
        dm.update_settings_bulk(settings)
        self.accept()
