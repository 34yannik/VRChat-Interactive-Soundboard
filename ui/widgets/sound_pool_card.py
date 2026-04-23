from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from ui.widgets.waveform_widget import WaveformWidget

POOL_BACKGROUND       = "#18102e"
POOL_BACKGROUND_HOVER = "#201440"
POOL_BORDER           = "#3a2060"
POOL_BORDER_ACTIVE    = "#a855f7"
POOL_BACKGROUND_ACTIVE = "#1e0f40"
POOL_ACCENT           = "#a855f7"
BASE_SIZE             = 210


class SoundPoolCard(QFrame):
    clicked = Signal(dict)
    right_clicked = Signal(dict)

    def __init__(self, sound_data, size=BASE_SIZE, parent=None):
        super().__init__(parent)
        self.sound_data = sound_data
        self.is_playing = False
        self.size = size
        self.scale = size / BASE_SIZE

        self._setup_ui()
        self._apply_idle_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(size, size)

    def _scaled(self, base_px):
        return max(1, int(base_px * self.scale))

    def _setup_ui(self):
        pad = self._scaled(12)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(pad, self._scaled(10), pad, pad)
        layout.setSpacing(self._scaled(4))

        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(4)

        badge = QLabel("POOL")
        badge.setStyleSheet(
            f"color: {POOL_ACCENT}; font-size: {max(7, self._scaled(9))}px; "
            f"font-weight: bold; background: #2a1050; border-radius: 3px; "
            f"padding: 1px 4px;"
        )
        top_row.addWidget(badge)

        sounds = self.sound_data.get("sounds", [])
        count_lbl = QLabel(f"{len(sounds)} sounds")
        count_lbl.setStyleSheet(
            f"color: #7755aa; font-size: {max(7, self._scaled(9))}px; background: transparent;"
        )
        top_row.addWidget(count_lbl)
        top_row.addStretch()

        hotkey_text = self.sound_data.get("hotkey", "")
        if hotkey_text:
            hk = QLabel(hotkey_text)
            hk.setStyleSheet(
                f"color: #666688; font-size: {max(8, self._scaled(10))}px; "
                f"font-weight: bold; background: transparent; font-family: monospace;"
            )
            top_row.addWidget(hk)

        layout.addLayout(top_row)

        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform, stretch=1)

        self.name_label = QLabel(self.sound_data.get("name", "Unknown Pool"))
        self.name_label.setStyleSheet(
            f"color: white; font-size: {max(9, self._scaled(13))}px; "
            f"font-weight: bold; background: transparent;"
        )
        self.name_label.setWordWrap(True)
        layout.addWidget(self.name_label)

        mode = self.sound_data.get("chatbox_mode", "individual")
        shared_text = self.sound_data.get("osc_message", "")

        if mode == "shared" and shared_text:
            osc_lbl = QLabel("OSC - " + shared_text)
            osc_lbl.setStyleSheet(
                f"color: {POOL_ACCENT}; font-size: {max(8, self._scaled(11))}px; "
                f"font-style: italic; background: transparent;"
            )
            osc_lbl.setWordWrap(True)
            layout.addWidget(osc_lbl)
        elif mode == "individual":
            osc_lbl = QLabel("OSC - per sound")
            osc_lbl.setStyleSheet(
                f"color: #7755aa; font-size: {max(8, self._scaled(11))}px; "
                f"font-style: italic; background: transparent;"
            )
            layout.addWidget(osc_lbl)

    def _apply_idle_style(self):
        r = self._scaled(10)
        self.setStyleSheet(f"""
            SoundPoolCard {{
                background-color: {POOL_BACKGROUND};
                border-radius: {r}px;
                border: 1px solid {POOL_BORDER};
            }}
            SoundPoolCard:hover {{
                background-color: {POOL_BACKGROUND_HOVER};
                border: 1px solid #5a3090;
            }}
        """)

    def _apply_playing_style(self):
        r = self._scaled(10)
        self.setStyleSheet(f"""
            SoundPoolCard {{
                background-color: {POOL_BACKGROUND_ACTIVE};
                border-radius: {r}px;
                border: 2px solid {POOL_BORDER_ACTIVE};
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
