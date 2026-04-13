import json
import os

SAVE_FILE = "soundboard_data.json"

# Standard-Daten wenn noch keine Datei existiert
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
        "osc_host": "127.0.0.1",
        "osc_port": 9000
    }
}


class DataManager:
    def __init__(self):
        self.data = self._load_data()

    def _load_data(self):
        if os.path.exists(SAVE_FILE):
            try:
                with open(SAVE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"Fehler beim Laden der Daten: {e}")
        # Kopie der Standard-Daten zurueckgeben
        import copy
        return copy.deepcopy(DEFAULT_DATA)

    def save_data(self):
        try:
            with open(SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Fehler beim Speichern: {e}")

    def get_collections(self):
        return self.data["collections"]

    def get_collection(self, collection_id):
        for collection in self.data["collections"]:
            if collection["id"] == collection_id:
                return collection
        return None

    def get_settings(self):
        return self.data["settings"]

    def update_settings(self, key, value):
        self.data["settings"][key] = value
        self.save_data()

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
        if collection:
            existing_ids = [p["id"] for p in collection["pages"]]
            new_id = max(existing_ids) + 1 if existing_ids else 1
            new_page = {"id": new_id, "name": page_name, "sounds": []}
            collection["pages"].append(new_page)
            self.save_data()
            return new_page
        return None

    def delete_page(self, collection_id, page_id):
        collection = self.get_collection(collection_id)

        collection["pages"] = [
            p for p in collection["pages"] if p["id"] != page_id
        ]

        self.save_data()

    def rename_page(self, collection_id, page_id, new_name):
        collection = self.get_collection(collection_id)

        for page in collection["pages"]:
            if page["id"] == page_id:
                page["name"] = new_name
                self.save_data()
                return

    def add_sound_to_page(self, collection_id, page_id, sound_data):
        collection = self.get_collection(collection_id)
        if collection:
            for page in collection["pages"]:
                if page["id"] == page_id:
                    existing_ids = [s["id"] for s in page["sounds"]] if page["sounds"] else []
                    new_id = max(existing_ids) + 1 if existing_ids else 1
                    sound_data["id"] = new_id
                    page["sounds"].append(sound_data)
                    self.save_data()
                    return sound_data
        return None

    def remove_sound(self, collection_id, page_id, sound_id):
        collection = self.get_collection(collection_id)
        if collection:
            for page in collection["pages"]:
                if page["id"] == page_id:
                    page["sounds"] = [s for s in page["sounds"] if s["id"] != sound_id]
                    self.save_data()
