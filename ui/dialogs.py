import os
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                               QLineEdit, QPushButton, QFileDialog, QComboBox,
                               QFormLayout, QWidget, QSpinBox, QCheckBox, QSlider,
                               QRadioButton, QScrollArea, QButtonGroup, QFrame)
from PySide6.QtGui import QKeySequence
from PySide6.QtCore import Qt, QKeyCombination, Signal
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

POOL_CONFIRM_BTN_STYLE = """
    QPushButton {
        background-color: #6d28d9;
        color: white;
        border: none;
        padding: 8px 20px;
        border-radius: 6px;
        font-size: 13px;
        font-weight: bold;
    }
    QPushButton:hover { background-color: #7c3aed; }
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

POOL_VOLUME_SLIDER_STYLE = """
    QSlider::groove:horizontal {
        background: #2a2a45;
        height: 4px;
        border-radius: 2px;
    }
    QSlider::handle:horizontal {
        background: #7c3aed;
        width: 12px;
        height: 12px;
        margin: -4px 0;
        border-radius: 6px;
    }
    QSlider::sub-page:horizontal {
        background: #7c3aed;
        border-radius: 2px;
    }
"""

SECTION_LABEL_STYLE = (
    "color: #555577; font-size: 10px; font-weight: bold; "
    "letter-spacing: 1px; background: transparent;"
)

RADIO_STYLE = "color: #aaaacc; font-size: 12px; background: transparent;"


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


class PoolSoundRow(QWidget):
    remove_requested = Signal()

    def __init__(self, sound_data=None, individual_mode=False, parent=None):
        super().__init__(parent)
        data = sound_data or {}
        self._file_path = data.get("file_path", "")
        self._setup_ui(data, individual_mode)

    def _setup_ui(self, data, individual_mode):
        self.setStyleSheet("""
            PoolSoundRow {
                background-color: #111128;
                border-radius: 6px;
                border: 1px solid #1e1e38;
            }
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(10, 8, 10, 8)
        outer.setSpacing(5)

        row1 = QHBoxLayout()
        row1.setSpacing(6)

        file_name = os.path.basename(self._file_path) if self._file_path else "No file selected"
        if len(file_name) > 30:
            name_part, ext = os.path.splitext(file_name)
            file_name = name_part[:26] + "…" + ext

        self.file_label = QLabel(file_name)
        self.file_label.setStyleSheet(
            "color: #8888aa; font-size: 11px; background: transparent;"
        )

        change_btn = QPushButton("Change")
        change_btn.setFixedHeight(22)
        change_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        change_btn.clicked.connect(self._change_file)
        change_btn.setStyleSheet("""
            QPushButton {
                background: #1e1e35; color: #888899; border: none;
                padding: 0 8px; border-radius: 4px; font-size: 11px;
            }
            QPushButton:hover { background: #2a2a4a; color: white; }
        """)

        remove_btn = QPushButton("✕")
        remove_btn.setFixedSize(22, 22)
        remove_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        remove_btn.clicked.connect(self.remove_requested.emit)
        remove_btn.setStyleSheet("""
            QPushButton {
                background: #2a1a1a; color: #cc3333; border: none;
                border-radius: 4px; font-size: 11px;
            }
            QPushButton:hover { background: #3a1f1f; color: #ff4444; }
        """)

        row1.addWidget(self.file_label, stretch=1)
        row1.addWidget(change_btn)
        row1.addWidget(remove_btn)
        outer.addLayout(row1)

        row2 = QHBoxLayout()
        row2.setSpacing(6)

        name_lbl = QLabel("Name:")
        name_lbl.setFixedWidth(40)
        name_lbl.setStyleSheet("color: #555577; font-size: 11px; background: transparent;")

        self.name_input = QLineEdit(data.get("name", ""))
        self.name_input.setPlaceholderText("Sound name…")
        self.name_input.setFixedHeight(24)
        self.name_input.setStyleSheet("""
            QLineEdit {
                background: #16162a; color: #ddddee; border: 1px solid #2a2a45;
                border-radius: 4px; padding: 2px 6px; font-size: 11px;
            }
            QLineEdit:focus { border-color: #7c3aed; }
        """)

        vol_lbl = QLabel("Vol:")
        vol_lbl.setFixedWidth(28)
        vol_lbl.setStyleSheet("color: #555577; font-size: 11px; background: transparent;")

        self.vol_slider = QSlider(Qt.Orientation.Horizontal)
        self.vol_slider.setRange(0, 100)
        self.vol_slider.setValue(data.get("volume", 100))
        self.vol_slider.setFixedWidth(72)
        self.vol_slider.setCursor(Qt.CursorShape.PointingHandCursor)
        self.vol_slider.setStyleSheet(POOL_VOLUME_SLIDER_STYLE)

        self.vol_label = QLabel(f"{data.get('volume', 100)}%")
        self.vol_label.setFixedWidth(32)
        self.vol_label.setStyleSheet("color: #aaaacc; font-size: 11px; background: transparent;")
        self.vol_slider.valueChanged.connect(lambda v: self.vol_label.setText(f"{v}%"))

        row2.addWidget(name_lbl)
        row2.addWidget(self.name_input, stretch=1)
        row2.addWidget(vol_lbl)
        row2.addWidget(self.vol_slider)
        row2.addWidget(self.vol_label)
        outer.addLayout(row2)

        self.osc_row_widget = QWidget()
        self.osc_row_widget.setStyleSheet("background: transparent;")
        osc_layout = QHBoxLayout(self.osc_row_widget)
        osc_layout.setContentsMargins(0, 0, 0, 0)
        osc_layout.setSpacing(6)

        osc_lbl = QLabel("OSC:")
        osc_lbl.setFixedWidth(40)
        osc_lbl.setStyleSheet("color: #555577; font-size: 11px; background: transparent;")

        self.osc_input = QLineEdit(data.get("osc_message", ""))
        self.osc_input.setPlaceholderText("Chatbox text for this sound…")
        self.osc_input.setFixedHeight(24)
        self.osc_input.setStyleSheet("""
            QLineEdit {
                background: #16162a; color: #ddddee; border: 1px solid #2a2a45;
                border-radius: 4px; padding: 2px 6px; font-size: 11px;
            }
            QLineEdit:focus { border-color: #7c3aed; }
        """)

        osc_layout.addWidget(osc_lbl)
        osc_layout.addWidget(self.osc_input)
        outer.addWidget(self.osc_row_widget)

        self.osc_row_widget.setVisible(individual_mode)

    def set_individual_mode(self, enabled: bool):
        self.osc_row_widget.setVisible(enabled)

    def _change_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Audio File", "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a);;All Files (*.*)"
        )
        if file_path:
            self._file_path = file_path
            fname = os.path.basename(file_path)
            display = fname if len(fname) <= 30 else fname[:26] + "…" + os.path.splitext(fname)[1]
            self.file_label.setText(display)
            self.file_label.setStyleSheet("color: #aaaacc; font-size: 11px; background: transparent;")
            if not self.name_input.text():
                self.name_input.setText(os.path.splitext(fname)[0])

    def get_data(self) -> dict:
        return {
            "file_path": self._file_path,
            "name": self.name_input.text().strip() or os.path.basename(self._file_path),
            "volume": self.vol_slider.value(),
            "osc_message": self.osc_input.text().strip(),
            "duration": "0:00",
        }


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

        vol_label = QLabel("Sound Volume:")
        vol_label.setStyleSheet("color: #aaaacc; font-size: 13px; background: transparent;")
        layout.addWidget(vol_label)

        vol_row, self.volume_slider, self.volume_label = _make_volume_row(100)
        layout.addWidget(vol_row)

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
            self, "Select Audio File", "",
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
            "type": "sound",
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
            self, "Select New Audio File", "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac *.m4a);;All Files (*.*)"
        )
        if file_path:
            self.selected_file_path = file_path
            self.file_name_label.setText(os.path.basename(file_path))

    def get_sound_data(self):
        return {
            "id": self.sound_id,
            "type": "sound",
            "name": self.name_input.text().strip() or "Unknown Sound",
            "hotkey": self.hotkey_input.text().strip(),
            "osc_message": self.osc_message_input.text().strip(),
            "file_path": self.selected_file_path,
            "volume": self.volume_slider.value(),
            "duration": self.current_duration
        }


class AddSoundPoolDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create Sound Pool")
        self.setFixedSize(480, 580)
        self._rows: list[PoolSoundRow] = []
        self._individual_mode = False
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(22, 20, 22, 20)

        title = QLabel("Create Sound Pool")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("A pool randomly picks one of its sounds each time it's triggered.")
        subtitle.setStyleSheet("color: #555577; font-size: 11px; background: transparent;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Random Hits")
        form.addRow("Name:", self.name_input)

        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.setPlaceholderText("Press keys…")
        form.addRow("Hotkey:", self.hotkey_input)

        layout.addLayout(form)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1a1a30; border: none; max-height: 1px;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        chatbox_lbl = QLabel("CHATBOX MODE")
        chatbox_lbl.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(chatbox_lbl)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(5)

        self._mode_group = QButtonGroup(self)
        self.shared_radio = QRadioButton("Shared: one text for all sounds")
        self.individual_radio = QRadioButton("Individual: each sound has its own text")
        self.shared_radio.setChecked(True)
        self.shared_radio.setStyleSheet(RADIO_STYLE)
        self.individual_radio.setStyleSheet(RADIO_STYLE)
        self._mode_group.addButton(self.shared_radio)
        self._mode_group.addButton(self.individual_radio)

        mode_row.addWidget(self.shared_radio)
        mode_row.addWidget(self.individual_radio)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        self.shared_osc_container = QWidget()
        self.shared_osc_container.setStyleSheet("background: transparent;")
        shared_form = QFormLayout(self.shared_osc_container)
        shared_form.setContentsMargins(0, 0, 0, 0)
        shared_form.setSpacing(6)

        self.shared_osc_input = QLineEdit()
        self.shared_osc_input.setPlaceholderText("e.g. *plays a random sound*  (empty = no message)")
        shared_form.addRow("OSC Message:", self.shared_osc_input)
        layout.addWidget(self.shared_osc_container)

        self.shared_radio.toggled.connect(self._on_mode_toggled)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #1a1a30; border: none; max-height: 1px;")
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)

        pool_lbl = QLabel("POOL SOUNDS")
        pool_lbl.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(pool_lbl)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #1a1a30;
                border-radius: 6px;
                background: transparent;
            }
            QScrollBar:vertical { background: transparent; width: 4px; }
            QScrollBar::handle:vertical { background: #2a2a45; border-radius: 2px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.rows_container = QWidget()
        self.rows_container.setStyleSheet("background: transparent;")
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(8, 8, 8, 8)
        self.rows_layout.setSpacing(6)
        self.rows_layout.addStretch()

        self.scroll_area.setWidget(self.rows_container)
        self.scroll_area.setMinimumHeight(130)
        layout.addWidget(self.scroll_area, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        add_sound_btn = QPushButton("+ Add Sound to Pool")
        add_sound_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_sound_btn.clicked.connect(lambda: self._add_row())
        add_sound_btn.setStyleSheet("""
            QPushButton {
                background: #1a1030; color: #7c3aed;
                border: 1px solid #4c1d95;
                padding: 6px 14px; border-radius: 6px; font-size: 12px;
            }
            QPushButton:hover { background: #200e3a; border-color: #7c3aed; }
        """)

        multi_add_btn = QPushButton("📁")
        multi_add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        multi_add_btn.setFixedWidth(38)
        multi_add_btn.setToolTip("Add multiple audio files")
        multi_add_btn.setStyleSheet("""
            QPushButton {
                background: #111128;
                color: #aaaacc;
                border: 1px solid #2a2a45;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1a1a30;
                color: white;
                border-color: #7c3aed;
            }
        """)

        multi_add_btn.clicked.connect(self._add_multiple_files)

        btn_row.addWidget(add_sound_btn)
        btn_row.addWidget(multi_add_btn)

        layout.addLayout(btn_row)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        create_btn = QPushButton("Create Pool")
        create_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        create_btn.clicked.connect(self.accept)
        create_btn.setStyleSheet(POOL_CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(create_btn)
        layout.addLayout(button_row)

    def _on_mode_toggled(self, shared_checked: bool):
        self._individual_mode = not shared_checked
        self.shared_osc_container.setVisible(shared_checked)
        for row in self._rows:
            row.set_individual_mode(self._individual_mode)

    def _add_row(self, sound_data: dict | None = None):
        row = PoolSoundRow(sound_data, self._individual_mode, self)
        row.remove_requested.connect(lambda r=row: self._remove_row(r))
        self._rows.append(row)
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row)
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

    def _add_multiple_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac)"
        )

        for file_path in files:
            if not file_path:
                continue

            sound_data = {
                "file_path": file_path,
                "name": os.path.splitext(os.path.basename(file_path))[0],
                "volume": 100,
                "osc_message": "",
                "duration": ""
            }

            self._add_row(sound_data)

    def _remove_row(self, row: PoolSoundRow):
        if row in self._rows:
            self._rows.remove(row)
        row.deleteLater()

    def get_pool_data(self) -> dict:
        chatbox_mode = "individual" if self.individual_radio.isChecked() else "shared"
        return {
            "type": "pool",
            "name": self.name_input.text().strip() or "Sound Pool",
            "hotkey": self.hotkey_input.text().strip(),
            "chatbox_mode": chatbox_mode,
            "osc_message": self.shared_osc_input.text().strip(),
            "sounds": [r.get_data() for r in self._rows],
            "duration": "",
        }


class EditSoundPoolDialog(QDialog):
    def __init__(self, pool_data: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Sound Pool")
        self.setFixedSize(480, 580)
        self._rows: list[PoolSoundRow] = []
        self._individual_mode = pool_data.get("chatbox_mode", "shared") == "individual"
        self._pool_id = pool_data.get("id")
        self._setup_ui()
        self.setStyleSheet(DIALOG_STYLE)
        self._populate(pool_data)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(22, 20, 22, 20)

        title = QLabel("Edit Sound Pool")
        title.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        layout.addWidget(title)

        subtitle = QLabel("A pool randomly picks one of its sounds each time it's triggered.")
        subtitle.setStyleSheet("color: #555577; font-size: 11px; background: transparent;")
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g. Random Hits")
        form.addRow("Name:", self.name_input)

        self.hotkey_input = HotkeyLineEdit()
        self.hotkey_input.setPlaceholderText("Press keys…")
        form.addRow("Hotkey:", self.hotkey_input)

        layout.addLayout(form)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("background-color: #1a1a30; border: none; max-height: 1px;")
        sep.setFixedHeight(1)
        layout.addWidget(sep)

        chatbox_lbl = QLabel("CHATBOX MODE")
        chatbox_lbl.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(chatbox_lbl)

        mode_row = QHBoxLayout()
        mode_row.setSpacing(5)

        self._mode_group = QButtonGroup(self)
        self.shared_radio = QRadioButton("Shared  –  one text for all sounds")
        self.individual_radio = QRadioButton("Individual  –  each sound has its own text")
        self.shared_radio.setStyleSheet(RADIO_STYLE)
        self.individual_radio.setStyleSheet(RADIO_STYLE)
        self._mode_group.addButton(self.shared_radio)
        self._mode_group.addButton(self.individual_radio)

        mode_row.addWidget(self.shared_radio)
        mode_row.addWidget(self.individual_radio)
        mode_row.addStretch()
        layout.addLayout(mode_row)

        self.shared_osc_container = QWidget()
        self.shared_osc_container.setStyleSheet("background: transparent;")
        shared_form = QFormLayout(self.shared_osc_container)
        shared_form.setContentsMargins(0, 0, 0, 0)
        shared_form.setSpacing(6)

        self.shared_osc_input = QLineEdit()
        self.shared_osc_input.setPlaceholderText("e.g. *plays a random sound*  (empty = no message)")
        shared_form.addRow("OSC Message:", self.shared_osc_input)
        layout.addWidget(self.shared_osc_container)

        self.shared_radio.toggled.connect(self._on_mode_toggled)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("background-color: #1a1a30; border: none; max-height: 1px;")
        sep2.setFixedHeight(1)
        layout.addWidget(sep2)

        pool_lbl = QLabel("POOL SOUNDS")
        pool_lbl.setStyleSheet(SECTION_LABEL_STYLE)
        layout.addWidget(pool_lbl)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #1a1a30;
                border-radius: 6px;
                background: transparent;
            }
            QScrollBar:vertical { background: transparent; width: 4px; }
            QScrollBar::handle:vertical { background: #2a2a45; border-radius: 2px; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
        """)

        self.rows_container = QWidget()
        self.rows_container.setStyleSheet("background: transparent;")
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(8, 8, 8, 8)
        self.rows_layout.setSpacing(6)
        self.rows_layout.addStretch()

        self.scroll_area.setWidget(self.rows_container)
        self.scroll_area.setMinimumHeight(130)
        layout.addWidget(self.scroll_area, stretch=1)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        add_sound_btn = QPushButton("+ Add Sound to Pool")
        add_sound_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        add_sound_btn.clicked.connect(lambda: self._add_row())
        add_sound_btn.setStyleSheet("""
            QPushButton {
                background: #1a1030; color: #7c3aed;
                border: 1px solid #4c1d95;
                padding: 6px 14px; border-radius: 6px; font-size: 12px;
            }
            QPushButton:hover { background: #200e3a; border-color: #7c3aed; }
        """)

        multi_add_btn = QPushButton("📁")
        multi_add_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        multi_add_btn.setFixedWidth(38)
        multi_add_btn.setToolTip("Add multiple audio files")
        multi_add_btn.setStyleSheet("""
            QPushButton {
                background: #111128;
                color: #aaaacc;
                border: 1px solid #2a2a45;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover {
                background: #1a1a30;
                color: white;
                border-color: #7c3aed;
            }
        """)

        multi_add_btn.clicked.connect(self._add_multiple_files)

        btn_row.addWidget(add_sound_btn)
        btn_row.addWidget(multi_add_btn)

        layout.addLayout(btn_row)

        button_row = QHBoxLayout()
        button_row.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet(CANCEL_BTN_STYLE)

        save_btn = QPushButton("Save Pool")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(self.accept)
        save_btn.setStyleSheet(POOL_CONFIRM_BTN_STYLE)

        button_row.addWidget(cancel_btn)
        button_row.addWidget(save_btn)
        layout.addLayout(button_row)

    def _populate(self, pool_data: dict):
        self.name_input.setText(pool_data.get("name", ""))
        self.hotkey_input.setText(pool_data.get("hotkey", ""))
        self.shared_osc_input.setText(pool_data.get("osc_message", ""))

        if self._individual_mode:
            self.individual_radio.setChecked(True)
            self.shared_osc_container.setVisible(False)
        else:
            self.shared_radio.setChecked(True)

        for sub_sound in pool_data.get("sounds", []):
            self._add_row(sub_sound)

    def _on_mode_toggled(self, shared_checked: bool):
        self._individual_mode = not shared_checked
        self.shared_osc_container.setVisible(shared_checked)
        for row in self._rows:
            row.set_individual_mode(self._individual_mode)

    def _add_row(self, sound_data: dict | None = None):
        row = PoolSoundRow(sound_data, self._individual_mode, self)
        row.remove_requested.connect(lambda r=row: self._remove_row(r))
        self._rows.append(row)
        self.rows_layout.insertWidget(self.rows_layout.count() - 1, row)

    def _add_multiple_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Audio Files",
            "",
            "Audio Files (*.mp3 *.wav *.ogg *.flac)"
        )

        existing_paths = {
            r.get_data().get("file_path") for r in self._rows
        }

        for file_path in files:
            if not file_path or file_path in existing_paths:
                continue

            sound_data = {
                "file_path": file_path,
                "name": os.path.splitext(os.path.basename(file_path))[0],
                "volume": 100,
                "osc_message": "",
                "duration": ""
            }

            self._add_row(sound_data)

    def _remove_row(self, row: PoolSoundRow):
        if row in self._rows:
            self._rows.remove(row)
        row.deleteLater()

    def get_pool_data(self) -> dict:
        chatbox_mode = "individual" if self.individual_radio.isChecked() else "shared"
        return {
            "id": self._pool_id,
            "type": "pool",
            "name": self.name_input.text().strip() or "Sound Pool",
            "hotkey": self.hotkey_input.text().strip(),
            "chatbox_mode": chatbox_mode,
            "osc_message": self.shared_osc_input.text().strip(),
            "sounds": [r.get_data() for r in self._rows],
            "duration": "",
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

        label = QLabel(f"Delete\n'{sound_name}'?")
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

        import subprocess

        def open_folder():
            folder = os.path.join(os.environ.get("APPDATA"), "VRCInteractiveSoundboard")
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