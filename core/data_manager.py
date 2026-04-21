import json
import os
import copy
import fancify_text
from PySide6.QtMultimedia import QMediaDevices

APPDATA_DIR = os.path.join(
    os.getenv("APPDATA"),
    "VRCInteractiveSoundboard"
)

os.makedirs(APPDATA_DIR, exist_ok=True)

SAVE_FILE = os.path.join(
    APPDATA_DIR,
    "soundboard-config.json"
)

DEFAULT_DATA = {
    "collections": [
        {
            "id": 1,
            "name": "Default Soundboard",
            "icon": "🎮",
            "pages": [
                {"id": 1, "name": "Default Page", "sounds": []}
            ]
        }
    ],
    "settings": {
        "volume": 75,
        "columns": 4,
        "rows": 3,
        "osc_host": "127.0.0.1",
        "osc_port": 9000,
        "font": "sansSerif",
        "enable_output": False,
        "output_device": ""
    }
}

_INSTANCE = None


def get_data_manager():
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = DataManager()
    return _INSTANCE


class DataManager:

    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if "settings" not in data:
                    data["settings"] = {}

                data["settings"].setdefault("volume", 75)
                data["settings"].setdefault("columns", 4)
                data["settings"].setdefault("rows", 3)
                data["settings"].setdefault("osc_host", "127.0.0.1")
                data["settings"].setdefault("osc_port", 9000)
                data["settings"].setdefault("font", "sansSerif")
                data["settings"].setdefault("enable_output", False)
                data["settings"].setdefault("output_device", "")

                # migrate existing sounds that have no per-sound volume yet
                for col in data.get("collections", []):
                    for page in col.get("pages", []):
                        for sound in page.get("sounds", []):
                            sound.setdefault("volume", 100)

                print("[LOAD SETTINGS]", data.get("settings"))
                return data

            except Exception as e:
                print(f"load error: {e}")

        return copy.deepcopy(DEFAULT_DATA)

    def save_data(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
                print("[SAVE PATH]", SAVE_FILE)
                print("[SAVE SNAPSHOT]", self.data["settings"])
        except Exception as e:
            print(f"save error: {e}")

    def get_settings(self):
        return self.data["settings"]

    def update_settings(self, key, value):
        self.data["settings"][key] = value
        self.save_data()

    def update_settings_bulk(self, updates: dict):
        self.data["settings"].update(updates)
        self.save_data()

    def get_audio_outputs(self):
        devices = QMediaDevices.audioOutputs()
        names = [d.description() for d in devices]

        fallback = "Default Output"
        saved = self.data["settings"].get("output_device", "")

        if saved and saved not in names:
            print(f"[FALLBACK OUTPUT] '{saved}' not found")
            self.data["settings"]["output_device"] = fallback

        return names or [fallback]

    def get_all_fonts(self):
        fonts = [
            name for name in dir(fancify_text)
            if callable(getattr(fancify_text, name)) and not name.startswith("_")
        ]
        fonts = sorted(set(fonts))
        fonts.insert(0, "Normal")
        fonts.append("UwU")
        return fonts

    def get_output_device(self):
        return self.data["settings"].get("output_device", "")

    def is_output_enabled(self):
        return self.data["settings"].get("enable_output", False)

    def get_collections(self):
        return self.data["collections"]

    def get_collection(self, collection_id):
        for collection in self.data["collections"]:
            if collection["id"] == collection_id:
                return collection
        return None

    def add_collection(self, name, icon="🎵"):
        existing_ids = [c["id"] for c in self.data["collections"]]
        new_id = max(existing_ids) + 1 if existing_ids else 1

        new_collection = {
            "id": new_id,
            "name": name,
            "icon": icon,
            "pages": [{"id": 1, "name": "Page 1", "sounds": []}]
        }

        self.data["collections"].append(new_collection)
        self.save_data()
        return new_collection

    def update_collection(self, collection_id, new_name, new_icon):
        for c in self.data["collections"]:
            if c["id"] == collection_id:
                c["name"] = new_name
                c["icon"] = new_icon
                self.save_data()
                return

    def delete_collection(self, collection_id):
        self.data["collections"] = [
            c for c in self.data["collections"] if c["id"] != collection_id
        ]
        self.save_data()

    def add_page_to_collection(self, collection_id, page_name):
        collection = self.get_collection(collection_id)
        if not collection:
            return None

        existing_ids = [p["id"] for p in collection["pages"]]
        new_id = max(existing_ids) + 1 if existing_ids else 1

        new_page = {"id": new_id, "name": page_name, "sounds": []}
        collection["pages"].append(new_page)
        self.save_data()
        return new_page

    def delete_page(self, collection_id, page_id):
        collection = self.get_collection(collection_id)
        if not collection:
            return

        collection["pages"] = [
            p for p in collection["pages"] if p["id"] != page_id
        ]
        self.save_data()

    def rename_page(self, collection_id, page_id, new_name):
        collection = self.get_collection(collection_id)
        if not collection:
            return

        for page in collection["pages"]:
            if page["id"] == page_id:
                page["name"] = new_name
                self.save_data()
                return

    def add_sound_to_page(self, collection_id, page_id, sound_data):
        collection = self.get_collection(collection_id)
        if not collection:
            return None

        for page in collection["pages"]:
            if page["id"] == page_id:
                existing_ids = [s["id"] for s in page["sounds"]]
                new_id = max(existing_ids) + 1 if existing_ids else 1
                sound_data["id"] = new_id
                sound_data.setdefault("volume", 100)
                page["sounds"].append(sound_data)
                self.save_data()
                return sound_data

        return None

    def update_sound(self, collection_id, page_id, sound_id, new_data):
        collection = self.get_collection(collection_id)
        if not collection:
            return False

        for page in collection.get("pages", []):
            if page["id"] == page_id:
                for i, sound in enumerate(page.get("sounds", [])):
                    if sound.get("id") == sound_id:
                        new_data["id"] = sound_id
                        new_data.setdefault("volume", 100)
                        page["sounds"][i] = new_data
                        self.save_data()
                        return True
        return False

    def delete_sound(self, collection_id, page_id, sound_id):
        collection = self.get_collection(collection_id)
        if not collection:
            return False

        for page in collection.get("pages", []):
            if page["id"] == page_id:
                original_count = len(page["sounds"])
                page["sounds"] = [s for s in page["sounds"] if s.get("id") != sound_id]

                if len(page["sounds"]) < original_count:
                    self.save_data()
                    return True
        return False

    def remove_sound(self, collection_id, page_id, sound_id):
        collection = self.get_collection(collection_id)
        if not collection:
            return

        for page in collection["pages"]:
            if page["id"] == page_id:
                page["sounds"] = [
                    s for s in page["sounds"] if s["id"] != sound_id
                ]
                self.save_data()
                return
