from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PySide6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve

TYPE_INFO    = "info"
TYPE_SUCCESS = "success"
TYPE_WARNING = "warning"
TYPE_UPDATE  = "update"

_ACCENT_CSS = {
    TYPE_INFO:    "#4a6cf7",
    TYPE_SUCCESS: "#22cc66",
    TYPE_WARNING: "#f7a84a",
    TYPE_UPDATE:  "#a855f7",
}

CARD_WIDTH  = 300
CARD_MARGIN = 16
DISPLAY_MS  = 6000
ANIM_MS     = 200


class NotificationCard(QWidget):
    """child widget of main window, absolutely positioned bottom-right"""

    def __init__(self, title, message, notif_type, action_label, action_callback, parent):
        super().__init__(parent)

        self._closing = False
        accent = _ACCENT_CSS.get(notif_type, _ACCENT_CSS[TYPE_INFO])

        self.setFixedWidth(CARD_WIDTH)
        self.setStyleSheet(f"""
            NotificationCard {{
                background-color: #0f1020;   /* etwas dunkler, weniger blau */
                border: 1px solid #25254a;   /* dezenter Grundrahmen */
                border-left: 4px solid #8b5cf6; /* sanftes Lila als Accent */
                border-radius: 10px;
            }}

            QLabel {{
                background: transparent;
            }}

            QPushButton {{
                background: transparent;
            }}

            NotificationCard:hover {{
                border: 1px solid #2f2f5f;
                border-left: 4px solid #a78bfa; /* leicht helleres Lila beim Hover */
            }}
        """)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 12, 12)
        layout.setSpacing(6)

        # header
        header = QHBoxLayout()
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet("color: white; font-size: 13px; font-weight: bold;")

        close_btn = QPushButton("✕")
        close_btn.setFixedSize(18, 18)
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.clicked.connect(self._start_close)
        close_btn.setStyleSheet("""
            QPushButton { color: #555577; border: none; font-size: 11px; padding: 0; }
            QPushButton:hover { color: #ccccdd; }
        """)
        header.addWidget(title_lbl, stretch=1)
        header.addWidget(close_btn)
        layout.addLayout(header)

        if message:
            msg = QLabel(message)
            msg.setWordWrap(True)
            msg.setStyleSheet("color: #8888aa; font-size: 12px;")
            layout.addWidget(msg)

        if action_label and action_callback:
            btn = QPushButton(action_label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(28)
            btn.setStyleSheet(f"""
                QPushButton {{
                    color: {accent}; border: 1px solid {accent};
                    border-radius: 5px; font-size: 12px; padding: 0 10px;
                }}
                QPushButton:hover {{ background: rgba(255,255,255,0.06); }}
            """)
            btn.clicked.connect(action_callback)
            btn.clicked.connect(self._start_close)
            row = QHBoxLayout()
            row.addStretch()
            row.addWidget(btn)
            layout.addLayout(row)

        self.adjustSize()

        # fade effect — works reliably on child widgets
        self._fx = QGraphicsOpacityEffect(self)
        self._fx.setOpacity(0.0)
        self.setGraphicsEffect(self._fx)

        # auto-dismiss
        QTimer.singleShot(DISPLAY_MS, self._start_close)

    def show_and_fade_in(self):
        self.show()
        self.raise_()
        anim = QPropertyAnimation(self._fx, b"opacity", self)
        anim.setDuration(ANIM_MS)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        anim.start()
        self._anim_in = anim  # keep reference

    def _start_close(self):
        if self._closing:
            return
        self._closing = True

        anim = QPropertyAnimation(self._fx, b"opacity", self)
        anim.setDuration(ANIM_MS)
        anim.setStartValue(self._fx.opacity())
        anim.setEndValue(0.0)
        anim.setEasingCurve(QEasingCurve.Type.InCubic)
        anim.finished.connect(self._on_done)
        anim.start()
        self._anim_out = anim

    def _on_done(self):
        if hasattr(self, "_on_removed"):
            self._on_removed(self)
        self.deleteLater()


class NotificationManager:
    """
    plain python class — no widget.
    cards are children of main_window and positioned with move().

    usage:
        nm = NotificationManager(main_window)
        nm.show_notification("Title", "Body text", TYPE_UPDATE)
    """

    def __init__(self, main_window: QWidget):
        self._win   = main_window
        self._cards: list[NotificationCard] = []

    def show_notification(self, title, message="", notif_type=TYPE_INFO,
                          action_label=None, action_callback=None):
        card = NotificationCard(
            title, message, notif_type,
            action_label, action_callback,
            parent=self._win   # child of main window — always visible inside it
        )
        card._on_removed = self._on_card_removed
        self._cards.append(card)
        self._reposition()
        card.show_and_fade_in()

    def update_geometry(self):
        self._reposition()

    def _reposition(self):
        w = self._win
        x = w.width()  - CARD_WIDTH  - CARD_MARGIN
        y = w.height() - CARD_MARGIN

        for card in reversed(self._cards):
            h = card.height() or 80
            y -= h
            card.move(x, y)
            card.raise_()
            y -= CARD_MARGIN

    def _on_card_removed(self, card):
        if card in self._cards:
            self._cards.remove(card)
        self._reposition()
