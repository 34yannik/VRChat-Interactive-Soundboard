import requests
from packaging import version


class Updater:

    _instance = None

    def __init__(self, current_version, include_prerelease=False):
        self.current_version = current_version
        self.include_prerelease = include_prerelease
        self.api_url = "https://api.github.com/repos/34yannik/VRChat-Interactive-Soundboard/releases"

        self.update_available = False
        self.latest_release = None

        # set instance (Singleton)
        Updater._instance = self

    @staticmethod
    def get_updater():
        if Updater._instance is None:
            raise RuntimeError("Updater not initialized yet")
        return Updater._instance

    def get_releases(self):
        r = requests.get(self.api_url)
        r.raise_for_status()
        return r.json()


    def get_latest_release(self):
        releases = self.get_releases()

        valid = [
            r for r in releases
            if self.include_prerelease or not r["prerelease"]
        ]

        latest = max(valid, key=lambda r: version.parse(r["tag_name"].lstrip("v")))

        asset = next(
            (a for a in latest.get("assets", []) if a["name"].endswith(".exe")),
            None
        )

        if not asset:
            raise ValueError("No .exe asset found in release")

        return {
            "version": latest["tag_name"],
            "url": asset["browser_download_url"],
            "notes": latest.get("body", "")
        }

    def is_update_available(self):
        latest = self.get_latest_release()

        current_v = version.parse(self.current_version.lstrip("v"))
        latest_v = version.parse(latest["version"].lstrip("v"))

        self.update_available = latest_v > current_v
        self.latest_release = latest

        return self.update_available