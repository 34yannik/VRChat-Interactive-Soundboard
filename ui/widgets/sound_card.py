from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from waveform_widget import WaveformWidget
from core.data_manager import get_data_manager
import fancify_text
import uwuify

CARD_BACKGROUND = "#16162a"
CARD_BACKGROUND_HOVER = "#1c1c34"
CARD_BORDER = "#2a2a45"
CARD_BORDER_ACTIVE = "#4a6cf7"
CARD_BACKGROUND_ACTIVE = "#1a2050"
BASE_SIZE = 210


class SoundCard(QFrame):
    clicked = Signal(dict)
    right_clicked = Signal(dict)

    def __init__(self, sound_data, size=BASE_SIZE, parent=None):
        super().__init__(parent)
        self.sound_data = sound_data
        self.is_playing = False
        self.size = size

        # Skalierungsfaktor relativ zur Basisgröße
        self.scale = size / BASE_SIZE

        self._setup_ui()
        self._apply_idle_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(size, size)

    def _scaled(self, base_px):
        """Skaliert einen Pixelwert anhand der Kartengröße"""
        return max(1, int(base_px * self.scale))

    def _setup_ui(self):
        pad = self._scaled(12)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(pad, self._scaled(10), pad, pad)
        layout.setSpacing(self._scaled(4))

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)

        hotkey_text = self.sound_data.get("hotkey", "")
        if hotkey_text:
            self.hotkey_label = QLabel(hotkey_text)
            self.hotkey_label.setStyleSheet(
                f"color: #666688; font-size: {max(8, self._scaled(10))}px; font-weight: bold; "
                f"background: transparent; font-family: monospace;"
            )
            top_row.addWidget(self.hotkey_label)

        layout.addLayout(top_row)

        # Wellenform
        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform, stretch=1)

        sound_name = self.sound_data.get("name", "Unbekannt")
        self.name_label = QLabel(sound_name)
        self.name_label.setStyleSheet(
            f"color: white; font-size: {max(9, self._scaled(13))}px; "
            f"font-weight: bold; background: transparent;"
        )
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        sound_osc = self.sound_data.get("osc_message")
        if sound_osc:

            font = get_data_manager().get_settings().get("font")

            if font == "UwU":
                if "?" not in sound_osc and "!" not in sound_osc:
                    sound_osc += "."
                sound_osc = uwuify.uwu(sound_osc, flags=uwuify.SMILEY | uwuify.STUTTER)

            elif font:
                try:
                    sound_osc = fancify_text.fancify(sound_osc, font)
                except Exception as e:
                    print(f"[FONT ERROR] {e} → fallback used")

            self.osc_label = QLabel("OSC - " + sound_osc)
            self.osc_label.setStyleSheet(
                f"color: #4a6cf7; font-size: {max(8, self._scaled(11))}px; "
                f"font-style: italic; background: transparent;"
            )
            self.osc_label.setWordWrap(True)
            layout.addWidget(self.osc_label)

        duration_text = self.sound_data.get("duration", "0:00")
        self.duration_label = QLabel(duration_text)
        self.duration_label.setStyleSheet(
            f"color: #666688; font-size: {max(8, self._scaled(11))}px; background: transparent;"
        )
        layout.addWidget(self.duration_label)



    def _apply_idle_style(self):
        radius = self._scaled(10)
        self.setStyleSheet(f"""
            SoundCard {{
                background-color: {CARD_BACKGROUND};
                border-radius: {radius}px;
                border: 1px solid {CARD_BORDER};
            }}
            SoundCard:hover {{
                background-color: {CARD_BACKGROUND_HOVER};
                border: 1px solid #3a3a60;
            }}
        """)

    def _apply_playing_style(self):
        radius = self._scaled(10)
        self.setStyleSheet(f"""
            SoundCard {{
                background-color: {CARD_BACKGROUND_ACTIVE};
                border-radius: {radius}px;
                border: 2px solid {CARD_BORDER_ACTIVE};
            }}
        """)

    def set_playing(self, playing):
        self.is_playing = playing
        if playing:
            self.waveform.start_animation()
            self._apply_playing_style()
        else:
            self.waveform.stop_animation()
            self._apply_idle_style()

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.sound_data)
        elif event.button() == Qt.MouseButton.RightButton:
            self.right_clicked.emit(self.sound_data)