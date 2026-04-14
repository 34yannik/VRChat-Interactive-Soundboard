from PySide6.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QFrame, QInputDialog, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut

from data_manager import DataManager, get_data_manager
from audio_player import AudioPlayer, get_audio_duration
from osc_client import OscClient
from sidebar_widget import SidebarWidget
from topbar_widget import TopBarWidget
from pages_tabbar import PagesTabBar
from sound_grid import SoundGrid
from dialogs import AddSoundDialog, AddCollectionDialog, SettingsDialog, EditCollectionDialog, EditPageDialog, \
    DeletePageDialog, DeleteCollectionDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VRC Interactive Soundboard")
        self.resize(1300, 820)
        self.setMinimumSize(900, 600)

        # Kern-Komponenten initialisieren
        self.data_manager = get_data_manager()
        self.audio_player = AudioPlayer()

        settings = self.data_manager.get_settings()
        self.osc_client = OscClient(settings["osc_host"], settings["osc_port"])

        # Aktuelle Auswahl merken
        self.active_collection_id = None
        self.active_page_id = None

        self._setup_ui()
        self._setup_keyboard_shortcuts()
        self._load_initial_data()

    def _setup_ui(self):
        # Zentrales Widget mit dunklem Hintergrund
        central_widget = QWidget()
        central_widget.setStyleSheet("background-color: #0d0d18;")
        self.setCentralWidget(central_widget)

        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Obere Leiste
        self.top_bar = TopBarWidget()
        self.top_bar.volume_changed.connect(self._on_volume_changed)
        self.top_bar.columns_changed.connect(self._on_columns_changed)
        self.top_bar.rows_changed.connect(self._on_rows_changed)
        self.top_bar.search_changed.connect(self._on_search_text_changed)
        self.top_bar.settings_clicked.connect(self._open_settings_dialog)
        root_layout.addWidget(self.top_bar)

        # Haupt-Bereich mit Sidebar und Content
        main_area_widget = QWidget()
        main_area_widget.setStyleSheet("background: transparent;")
        main_area_layout = QHBoxLayout(main_area_widget)
        main_area_layout.setContentsMargins(0, 0, 0, 0)
        main_area_layout.setSpacing(0)

        # Linke Sidebar
        self.sidebar = SidebarWidget()
        self.sidebar.collection_selected.connect(self._on_collection_selected)
        self.sidebar.add_collection_clicked.connect(self._open_add_collection_dialog)
        main_area_layout.addWidget(self.sidebar)
        # Vertikale Trennlinie zwischen Sidebar und Content
        vertical_separator = QFrame()
        vertical_separator.setFrameShape(QFrame.Shape.VLine)
        vertical_separator.setStyleSheet("background-color: #1a1a30; max-width: 1px; border: none;")
        vertical_separator.setFixedWidth(1)
        main_area_layout.addWidget(vertical_separator)

        # Rechter Content-Bereich
        right_panel = QWidget()
        right_panel.setStyleSheet("background-color: #0d0d18;")
        right_panel_layout = QVBoxLayout(right_panel)
        right_panel_layout.setContentsMargins(0, 0, 0, 0)
        right_panel_layout.setSpacing(0)

        # Collection-Header: Name + Stop-All Button
        self.collection_header = self._create_collection_header()
        right_panel_layout.addWidget(self.collection_header)

        # Page-Tabs
        self.pages_tab_bar = PagesTabBar()
        self.pages_tab_bar.page_selected.connect(self._on_page_selected)
        self.pages_tab_bar.add_page_clicked.connect(self._on_add_page_clicked)

        # Pages
        self.pages_tab_bar.page_edit_requested.connect(self._on_edit_page)
        self.pages_tab_bar.page_delete_requested.connect(self._on_delete_page)

        # Collections
        self.sidebar.collection_edit_requested.connect(self._on_edit_collection)
        self.sidebar.collection_delete_requested.connect(self._on_delete_collection)

        right_panel_layout.addWidget(self.pages_tab_bar)

        # Trennlinie unter den Tabs
        tab_line = QFrame()
        tab_line.setFrameShape(QFrame.Shape.HLine)
        tab_line.setStyleSheet("background-color: #1a1a30; max-height: 1px; border: none;")
        tab_line.setFixedHeight(1)
        right_panel_layout.addWidget(tab_line)

        # Sound Grid
        self.sound_grid = SoundGrid()
        self.sound_grid.sound_clicked.connect(self._on_sound_card_clicked)
        self.sound_grid.add_sound_clicked.connect(self._open_add_sound_dialog)
        right_panel_layout.addWidget(self.sound_grid, stretch=1)

        main_area_layout.addWidget(right_panel, stretch=1)
        root_layout.addWidget(main_area_widget, stretch=1)

    def _create_collection_header(self):
        """Erstellt den Header-Bereich mit Collection-Name und Stop-All Button"""
        header = QWidget()
        header.setFixedHeight(68)
        header.setStyleSheet("background: transparent;")

        layout = QHBoxLayout(header)
        layout.setContentsMargins(24, 10, 24, 8)

        # Titel und Info-Text
        title_column = QVBoxLayout()
        title_column.setSpacing(2)

        self.collection_title_label = QLabel("Collection")
        self.collection_title_label.setStyleSheet(
            "color: white; font-size: 20px; font-weight: bold; background: transparent;"
        )

        self.collection_info_label = QLabel("0 sounds")
        self.collection_info_label.setStyleSheet(
            "color: #555577; font-size: 12px; background: transparent;"
        )

        title_column.addWidget(self.collection_title_label)
        title_column.addWidget(self.collection_info_label)

        layout.addLayout(title_column)
        layout.addStretch()

        # Stop-All Button (roter Button oben rechts)
        self.stop_all_button = QPushButton(" Stop All (Esc)")
        self.stop_all_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.stop_all_button.clicked.connect(self._stop_all_sounds)
        self.stop_all_button.setStyleSheet("""
            QPushButton {
                background-color: #1e1010;
                color: #cc3322;
                border: 1px solid #3a1a1a;
                padding: 8px 18px;
                border-radius: 7px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2a1414;
                border-color: #cc3322;
            }
        """)
        layout.addWidget(self.stop_all_button)

        return header

    def _setup_keyboard_shortcuts(self):
        # Escape stoppt alle Sounds
        escape_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Escape), self)
        escape_shortcut.activated.connect(self._stop_all_sounds)

    def _load_initial_data(self):
        """Laedt alle Collections und zeigt die erste an"""
        collections = self.data_manager.get_collections()
        self.sidebar.load_collections(collections)

        saved_volume = self.data_manager.get_settings().get("volume", 75)
        self.top_bar.set_initial_volume(saved_volume)
        self.audio_player.set_volume(saved_volume)

        if collections:
            first_collection = collections[0]
            self.active_collection_id = first_collection["id"]
            self._show_collection(first_collection)

    def _show_collection(self, collection):
        """Zeigt eine Collection mit ihren Pages an"""
        self.active_collection_id = collection["id"]

        total_sounds = sum(len(page["sounds"]) for page in collection.get("pages", []))
        self.collection_title_label.setText(collection["name"])
        self.collection_info_label.setText(f"{total_sounds} sounds")

        pages = collection.get("pages", [])
        self.pages_tab_bar.load_pages(pages)

        if pages:
            self.active_page_id = pages[0]["id"]
            self._show_page(pages[0])
        else:
            self.sound_grid.load_sounds([])

    def _show_page(self, page):
        """Zeigt alle Sounds einer Page im Grid an"""
        self.active_page_id = page["id"]
        self.sound_grid.load_sounds(page.get("sounds", []))

    # --- Event-Handler ---

    def _on_delete_collection(self, collection_id):
        collection = self.data_manager.get_collection(collection_id)
        if not collection:
            return

        dialog = DeleteCollectionDialog(collection["name"], self)

        if dialog.exec() == dialog.DialogCode.Accepted:
            self.data_manager.delete_collection(collection_id)

            collections = self.data_manager.get_collections()

            self.sidebar.load_collections(collections)

            if collections:
                self._show_collection(collections[0])
            else:
                self.sound_grid.load_sounds([])
                self.collection_title_label.setText("No Collection")
                self.collection_info_label.setText("0 sounds")

    def _on_edit_collection(self, collection_id):
        collection = self.data_manager.get_collection(collection_id)
        if not collection:
            return

        dialog = EditCollectionDialog(
            collection["name"],
            collection["icon"],
            self
        )

        if dialog.exec():
            data = dialog.get_data()

            self.data_manager.update_collection(
                collection_id,
                data["name"],
                data["icon"]
            )

            self.sidebar.load_collections(
                self.data_manager.get_collections(),
                self.active_collection_id
            )

    def _on_collection_selected(self, collection_id):
        collection = self.data_manager.get_collection(collection_id)
        if collection:
            self._show_collection(collection)

    def _on_page_selected(self, page_id):
        collection = self.data_manager.get_collection(self.active_collection_id)
        if collection:
            for page in collection["pages"]:
                if page["id"] == page_id:
                    self._show_page(page)
                    break

    def _on_sound_card_clicked(self, sound_data):
        """Sound abspielen und optional OSC-Nachricht senden"""
        file_path = sound_data.get("file_path", "")
        if file_path:
            self.audio_player.play_sound(file_path)

        osc_message = sound_data.get("osc_message", "")
        if osc_message:
            self.osc_client.send_chatbox_message(osc_message)

    def _stop_all_sounds(self):
        self.audio_player.stop_all()
        self.sound_grid.stop_all_animations()

    def _on_volume_changed(self, volume_percent):
        self.audio_player.set_volume(volume_percent)
        self.data_manager.update_settings("volume", volume_percent)

    def _on_columns_changed(self, columns):
        self.sound_grid.set_columns(columns)
        self.data_manager.update_settings("columns", columns)

    def _on_search_text_changed(self, search_text):
        """Filtert die angezeigten Sounds nach dem Suchbegriff"""
        collection = self.data_manager.get_collection(self.active_collection_id)
        if not collection:
            return

        for page in collection["pages"]:
            if page["id"] == self.active_page_id:
                if search_text.strip():
                    filtered = [
                        s for s in page["sounds"]
                        if search_text.lower() in s["name"].lower()
                    ]
                else:
                    filtered = page["sounds"]
                self.sound_grid.load_sounds(filtered)
                break

    def _on_add_page_clicked(self):
        """Fuegt eine neue Page zur aktiven Collection hinzu"""
        collection = self.data_manager.get_collection(self.active_collection_id)
        if collection:
            next_page_number = len(collection["pages"]) + 1
            self.data_manager.add_page_to_collection(
                self.active_collection_id,
                f"Page {next_page_number}"
            )
            # Collection neu laden um die neue Page zu zeigen
            updated_collection = self.data_manager.get_collection(self.active_collection_id)
            self._show_collection(updated_collection)

    def _on_edit_page(self, page_id):
        collection = self.data_manager.get_collection(self.active_collection_id)

        page = next((p for p in collection["pages"] if p["id"] == page_id), None)
        if not page:
            return

        dialog = EditPageDialog(page["name"], self)

        if dialog.exec():
            self.data_manager.rename_page(
                self.active_collection_id,
                page_id,
                dialog.get_name()
            )

            self._show_collection(self.data_manager.get_collection(self.active_collection_id))

    def _on_delete_page(self, page_id):
        collection = self.data_manager.get_collection(self.active_collection_id)
        if not collection:
            return

        page = next((p for p in collection["pages"] if p["id"] == page_id), None)
        if not page:
            return

        dialog = DeletePageDialog(page["name"], self)

        if dialog.exec() == dialog.DialogCode.Accepted:
            self.data_manager.delete_page(
                self.active_collection_id,
                page_id
            )

            self._show_collection(
                self.data_manager.get_collection(self.active_collection_id)
            )

    def _on_rows_changed(self, rows):
        self.sound_grid.set_rows(rows)
        self.data_manager.update_settings("rows", rows)

    # --- Dialog-Oeffner ---

    def _open_add_sound_dialog(self):
        dialog = AddSoundDialog(self)
        if dialog.exec() == AddSoundDialog.DialogCode.Accepted:
            sound_data = dialog.get_sound_data()

            # Audio-Laenge berechnen wenn eine Datei gewaehlt wurde
            if sound_data["file_path"]:
                sound_data["duration"] = get_audio_duration(sound_data["file_path"])

            if self.active_collection_id and self.active_page_id:
                self.data_manager.add_sound_to_page(
                    self.active_collection_id,
                    self.active_page_id,
                    sound_data
                )
                self._on_page_selected(self.active_page_id)

    def _open_add_collection_dialog(self):
        dialog = AddCollectionDialog(self)
        if dialog.exec() == AddCollectionDialog.DialogCode.Accepted:
            data = dialog.get_data()
            self.data_manager.add_collection(data["name"], data["icon"])
            collections = self.data_manager.get_collections()
            self.sidebar.load_collections(collections, self.active_collection_id)

    def _open_settings_dialog(self):
        current_settings = self.data_manager.get_settings()
        dialog = SettingsDialog(current_settings, self)
        if dialog.exec() == SettingsDialog.DialogCode.Accepted:
            new_settings = dialog.get_settings()
            self.data_manager.update_settings("osc_host", new_settings["osc_host"])
            self.data_manager.update_settings("osc_port", new_settings["osc_port"])
            self.osc_client.update_connection(new_settings["osc_host"], new_settings["osc_port"])
