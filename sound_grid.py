from PySide6.QtWidgets import (QWidget, QScrollArea, QGridLayout, QVBoxLayout,
                               QFrame, QLabel)
from PySide6.QtCore import Qt, Signal

from sound_card import SoundCard


class AddSoundCard(QFrame):
    """Der Plus-Button zum Hinzufuegen neuer Sounds"""

    clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(210, 210)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        plus_label = QLabel("+")
        plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plus_label.setStyleSheet("color: #555577; font-size: 32px; background: transparent;")

        text_label = QLabel("Add Sound")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet("color: #555577; font-size: 13px; background: transparent;")

        layout.addWidget(plus_label)
        layout.addWidget(text_label)

        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            AddSoundCard {
                background-color: transparent;
                border-radius: 10px;
                border: 2px dashed #2a2a45;
            }
            AddSoundCard:hover {
                background-color: #16162a;
                border: 2px dashed #4a4a70;
            }
        """)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()


class SoundGrid(QWidget):
    """Zeigt alle Sound-Karten in einem konfigurierbarem Grid an"""

    sound_clicked = Signal(dict)
    add_sound_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.number_of_columns = 4
        self.sound_cards = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Scrollbarer Bereich fuer viele Sounds
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #0d0d18;
                width: 6px;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical {
                background: #2a2a45;
                border-radius: 3px;
            }
            QScrollBar::handle:vertical:hover {
                background: #4a4a70;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """)

        # Container in dem das Grid liegt
        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")

        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(24, 20, 24, 20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(scroll_area)

    def load_sounds(self, sounds_list):
        """Alle Sound-Karten neu aufbauen basierend auf der uebergebenen Liste"""
        self._clear_grid()
        self.sound_cards = []

        current_row = 0
        current_column = 0

        for sound_data in sounds_list:
            card = SoundCard(sound_data)
            card.clicked.connect(self.sound_clicked.emit)
            card.right_clicked.connect(self._on_right_click)
            self.sound_cards.append(card)
            self.grid_layout.addWidget(card, current_row, current_column)

            current_column += 1
            if current_column >= self.number_of_columns:
                current_column = 0
                current_row += 1

        # Plus-Karte am Ende hinzufuegen
        add_card = AddSoundCard()
        add_card.clicked.connect(self.add_sound_clicked.emit)
        self.grid_layout.addWidget(add_card, current_row, current_column)

    def _clear_grid(self):
        """Entfernt alle bestehenden Karten aus dem Grid"""
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def set_columns(self, columns):
        """Setzt die Anzahl der Spalten und baut das Grid neu auf"""
        self.number_of_columns = columns
        # Alle bestehenden Karten sammeln und neu anordnen
        sound_data_list = [card.sound_data for card in self.sound_cards]
        self.load_sounds(sound_data_list)

    def stop_all_animations(self):
        """Stoppt alle laufenden Animationen"""
        for card in self.sound_cards:
            card.set_playing(False)

    def _on_right_click(self, sound_data):
        """Rechtsklick auf eine Karte - z.B. fuer Loeschen"""
        # Wird spaeter mit Kontextmenu erweitert
        print(f"Rechtsklick auf: {sound_data.get('name')}")
