from PySide6.QtWidgets import QWidget, QHBoxLayout, QPushButton, QMenu, QInputDialog
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QAction


TAB_ACTIVE_STYLE = """
QPushButton {
    background-color: #0d0d18;
    color: white;
    border: none;
    border-bottom: 2px solid #4a6cf7;
    padding: 8px 18px;
    font-size: 13px;
    font-weight: bold;
}
"""

TAB_IDLE_STYLE = """
QPushButton {
    background: transparent;
    color: #777799;
    border: none;
    border-bottom: 2px solid transparent;
    padding: 8px 18px;
    font-size: 13px;
}
QPushButton:hover {
    color: #aaaacc;
    background: rgba(255,255,255, 0.03);
}
"""

PLUS_BUTTON_STYLE = """
QPushButton {
    background: transparent;
    color: #555577;
    border: none;
    padding: 6px 12px;
    font-size: 18px;
}
QPushButton:hover {
    color: #aaaacc;
    background: rgba(255,255,255, 0.04);
    border-radius: 4px;
}
"""


class PagesTabBar(QWidget):
    page_selected = Signal(int)

    # Context Menu Signals
    page_edit_requested = Signal(int)
    page_delete_requested = Signal(int)

    add_page_clicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.active_page_id = None
        self.tab_buttons = {}

        self._setup_ui()

    def _setup_ui(self):
        self.setStyleSheet("background: transparent; border-bottom: 1px solid #1a1a30;")

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(20, 0, 20, 0)
        self.layout.setSpacing(0)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.add_page_button = QPushButton("+")
        self.add_page_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.add_page_button.setStyleSheet(PLUS_BUTTON_STYLE)
        self.add_page_button.clicked.connect(self.add_page_clicked.emit)

    # -----------------------------
    # LOAD PAGES
    # -----------------------------
    def load_pages(self, pages_list):

        # alte Buttons entfernen (plus button behalten)
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()

            if widget and widget is not self.add_page_button:
                widget.deleteLater()

        self.tab_buttons.clear()

        for page in pages_list:
            page_id = page["id"]

            btn = QPushButton(page["name"])
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setCheckable(True)
            btn.setStyleSheet(TAB_IDLE_STYLE)

            # click select
            btn.clicked.connect(lambda checked=False, pid=page_id: self._select_page(pid))

            # RIGHT CLICK MENU
            btn.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            btn.customContextMenuRequested.connect(
                lambda pos, pid=page_id, b=btn: self._open_context_menu(pid, b)
            )

            self.tab_buttons[page_id] = btn
            self.layout.addWidget(btn)

        self.layout.addWidget(self.add_page_button)
        self.layout.addStretch(1)

        if pages_list:
            self._select_page(pages_list[0]["id"], emit_signal=False)

    # -----------------------------
    # CONTEXT MENU
    # -----------------------------
    def _open_context_menu(self, page_id, button):
        menu = QMenu(self)

        edit_action = menu.addAction("Edit Page")
        delete_action = menu.addAction("Delete Page")

        edit_action.triggered.connect(
            lambda: self.page_edit_requested.emit(page_id)
        )
        delete_action.triggered.connect(
            lambda: self.page_delete_requested.emit(page_id)
        )

        menu.exec(button.mapToGlobal(button.rect().bottomLeft()))

    # -----------------------------
    # SELECT PAGE
    # -----------------------------
    def _select_page(self, page_id, emit_signal=True):
        self.active_page_id = page_id

        for pid, btn in self.tab_buttons.items():
            if pid == page_id:
                btn.setChecked(True)
                btn.setStyleSheet(TAB_ACTIVE_STYLE)
            else:
                btn.setChecked(False)
                btn.setStyleSheet(TAB_IDLE_STYLE)

        if emit_signal:
            self.page_selected.emit(page_id)