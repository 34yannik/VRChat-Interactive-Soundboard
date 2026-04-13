import random
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QColor, QBrush


class WaveformWidget(QWidget):
    """Zeigt animierte Balken - leise wenn idle, animiert wenn ein Sound spielt"""

    def __init__(self, parent=None):
        super().__init__(parent)
        # Standard-Hoehen der Balken (0.0 bis 1.0)
        self.bar_heights = [0.2, 0.4, 0.6, 0.5, 0.7, 0.4, 0.3, 0.5, 0.2]
        self.is_playing = False

        # Timer fuer die Animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._update_animation)

        self.setMinimumHeight(50)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

    def start_animation(self):
        self.is_playing = True
        self.animation_timer.start(80)  # Alle 80ms aktualisieren

    def stop_animation(self):
        self.is_playing = False
        self.animation_timer.stop()
        # Balken wieder auf Standard-Hoehen
        self.bar_heights = [0.2, 0.4, 0.6, 0.5, 0.7, 0.4, 0.3, 0.5, 0.2]
        self.update()

    def _update_animation(self):
        # Zufaellige Hoehen fuer lebhafte Animation
        self.bar_heights = [random.uniform(0.15, 1.0) for _ in range(9)]
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        widget_width = self.width()
        widget_height = self.height()

        number_of_bars = len(self.bar_heights)
        bar_width = 4
        spacing = 3
        total_bars_width = number_of_bars * bar_width + (number_of_bars - 1) * spacing

        # Balken zentrieren
        start_x = (widget_width - total_bars_width) / 2

        for index, height_ratio in enumerate(self.bar_heights):
            bar_height = max(4, int(height_ratio * (widget_height - 12)))
            x_position = int(start_x + index * (bar_width + spacing))
            y_position = int((widget_height - bar_height) / 2)

            # Blaue Farbe wenn spielt, grau wenn idle
            if self.is_playing:
                bar_color = QColor(74, 108, 247)  # Blau
            else:
                bar_color = QColor(75, 75, 100)   # Grau

            painter.setBrush(QBrush(bar_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x_position, y_position, bar_width, bar_height, 2, 2)
