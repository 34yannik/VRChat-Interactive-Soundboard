from PySide6.QtWidgets import (QWidget, QScrollArea, QGridLayout, QVBoxLayout,
                               QFrame, QLabel, QMenu)
from PySide6.QtCore import Qt, Signal

from ui.widgets.sound_card import SoundCard

BASE_CARD_SIZE = 210
MIN_CARD_SIZE = 80


def card_size_for_columns(columns):
    """Berechnet die Kartengröße anhand der Spaltenanzahl"""
    size = int(BASE_CARD_SIZE * (4 / columns))
    return max(size, MIN_CARD_SIZE)


class AddSoundCard(QFrame):
    clicked = Signal()

    def __init__(self, size=BASE_CARD_SIZE, parent=None):
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(6)

        font_size = max(16, int(32 * size / BASE_CARD_SIZE))
        text_size = max(9, int(13 * size / BASE_CARD_SIZE))

        plus_label = QLabel("+")
        plus_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        plus_label.setStyleSheet(f"color: #555577; font-size: {font_size}px; background: transparent;")

        text_label = QLabel("Add Sound")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        text_label.setStyleSheet(f"color: #555577; font-size: {text_size}px; background: transparent;")

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
    sound_clicked = Signal(dict)
    sound_edit_requested = Signal(dict)
    sound_delete_requested = Signal(dict)
    add_sound_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.number_of_columns = 4
        self.number_of_rows = 4  # Beibehalten für spätere Nutzung
        self.sound_cards = []
        self._setup_ui()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("""
            QScrollArea { border: none; background: transparent; }
            QScrollBar:vertical { background: #0d0d18; width: 6px; border-radius: 3px; }
            QScrollBar::handle:vertical { background: #2a2a45; border-radius: 3px; }
            QScrollBar::handle:vertical:hover { background: #4a4a70; }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
        """)

        self.grid_container = QWidget()
        self.grid_container.setStyleSheet("background: transparent;")

        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setSpacing(12)
        self.grid_layout.setContentsMargins(24, 20, 24, 20)
        self.grid_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        scroll_area.setWidget(self.grid_container)
        main_layout.addWidget(scroll_area)

    def load_sounds(self, sounds_list):
        self._clear_grid()
        self.sound_cards = []

        card_size = card_size_for_columns(self.number_of_columns)
        current_row = 0
        current_column = 0

        for sound_data in sounds_list:
            card = SoundCard(sound_data, size=card_size)
            card.clicked.connect(self.sound_clicked.emit)
            card.right_clicked.connect(self.sound_right_clicked_action)

            # FIX: Nur ein einziges Mal zur Liste hinzufügen!
            self.sound_cards.append(card)

            self.grid_layout.addWidget(card, current_row, current_column)

            current_column += 1
            if current_column >= self.number_of_columns:
                current_column = 0
                current_row += 1

        add_card = AddSoundCard(size=card_size)
        add_card.clicked.connect(self.add_sound_clicked.emit)
        self.grid_layout.addWidget(add_card, current_row, current_column)

    def set_columns(self, columns):
        self.number_of_columns = columns
        # Daten sichern, bevor die Widgets gelöscht werden
        sound_data_list = [card.sound_data for card in self.sound_cards]
        self.load_sounds(sound_data_list)

    # --- WIEDER EINGEFÜGTE METHODEN ---

    def set_rows(self, rows):
        """Setzt die Anzahl der Reihen"""
        self.number_of_rows = rows

    def stop_all_animations(self):
        """Stoppt die Wellenform-Animation auf allen Karten"""
        for card in self.sound_cards:
            card.set_playing(False)

    # ----------------------------------

    def sound_right_clicked_action(self, sound_data):
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu { background-color: #16162a; color: white; border: 1px solid #2a2a45; }
            QMenu::item:selected { background-color: #4a6cf7; }
        """)

        edit_action = menu.addAction("Edit Sound")
        delete_action = menu.addAction("Delete Sound")

        action = menu.exec(self.cursor().pos())

        if action == edit_action:
            self.sound_edit_requested.emit(sound_data)
        elif action == delete_action:
            self.sound_delete_requested.emit(sound_data)

    def _clear_grid(self):
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()