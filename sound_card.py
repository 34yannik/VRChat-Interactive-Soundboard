from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal
from waveform_widget import WaveformWidget

# Farben fuer das Design
CARD_BACKGROUND = "#16162a"
CARD_BACKGROUND_HOVER = "#1c1c34"
CARD_BORDER = "#2a2a45"
CARD_BORDER_ACTIVE = "#4a6cf7"
CARD_BACKGROUND_ACTIVE = "#1a2050"


class SoundCard(QFrame):
    """Eine einzelne Sound-Karte mit Icon, Wellenform, Name und Hotkey"""

    # Signal wenn die Karte geklickt wird - gibt Sound-Daten mit
    clicked = Signal(dict)
    # Signal fuer Rechtsklick (Kontextmenu)
    right_clicked = Signal(dict)

    def __init__(self, sound_data, parent=None):
        super().__init__(parent)
        self.sound_data = sound_data
        self.is_playing = False

        self._setup_ui()
        self._apply_idle_style()
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(210, 210)

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(4)

        # Obere Zeile: Icon links, Hotkey rechts
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(0)

        icon_text = self.sound_data.get("icon", "🔊")
        self.icon_label = QLabel(icon_text)
        self.icon_label.setStyleSheet("font-size: 16px; background: transparent; color: white;")

        top_row.addWidget(self.icon_label)
        top_row.addStretch()

        hotkey_text = self.sound_data.get("hotkey", "")
        if hotkey_text:
            self.hotkey_label = QLabel(hotkey_text)
            self.hotkey_label.setStyleSheet(
                "color: #666688; font-size: 10px; font-weight: bold; "
                "background: transparent; font-family: monospace;"
            )
            top_row.addWidget(self.hotkey_label)

        layout.addLayout(top_row)

        # Wellenform in der Mitte
        self.waveform = WaveformWidget()
        layout.addWidget(self.waveform, stretch=1)

        # Sound-Name
        sound_name = self.sound_data.get("name", "Unbekannt")
        self.name_label = QLabel(sound_name)
        self.name_label.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold; background: transparent;"
        )
        self.name_label.setWordWrap(True)

        # Dauer
        duration_text = self.sound_data.get("duration", "0:00")
        self.duration_label = QLabel(duration_text)
        self.duration_label.setStyleSheet("color: #666688; font-size: 11px; background: transparent;")

        layout.addWidget(self.name_label)
        layout.addWidget(self.duration_label)

    def _apply_idle_style(self):
        self.setStyleSheet(f"""
            SoundCard {{
                background-color: {CARD_BACKGROUND};
                border-radius: 10px;
                border: 1px solid {CARD_BORDER};
            }}
            SoundCard:hover {{
                background-color: {CARD_BACKGROUND_HOVER};
                border: 1px solid #3a3a60;
            }}
        """)

    def _apply_playing_style(self):
        self.setStyleSheet(f"""
            SoundCard {{
                background-color: {CARD_BACKGROUND_ACTIVE};
                border-radius: 10px;
                border: 2px solid {CARD_BORDER_ACTIVE};
            }}
        """)

    def set_playing(self, playing):
        """Schaltet den Animationsmodus um"""
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
