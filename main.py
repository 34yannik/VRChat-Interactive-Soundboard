import sys
import os
import tempfile
import subprocess
import threading

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from PySide6.QtCore import QTimer

from ui.main_window import MainWindow
from ui.widgets.notification_widget import TYPE_UPDATE
from updater import Updater
from meta import __version__


# ---- single-instance lock ---------------------------------------------------

LOCK_FILE = os.path.join(
    tempfile.gettempdir(),
    "vrc_soundboard.lock"
)


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, relative_path)


def is_process_running(pid: int) -> bool:
    try:
        output = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid}"],
            creationflags=subprocess.CREATE_NO_WINDOW
        ).decode()
        return str(pid) in output
    except Exception:
        return False


def already_running():
    if not os.path.exists(LOCK_FILE):
        return False

    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())

        if is_process_running(pid):
            return True

    except Exception:
        pass

    try:
        os.remove(LOCK_FILE)
    except Exception:
        pass

    return False


def create_lock():
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except Exception:
        pass


# ---- update check -----------------------------------------------------------

def check_for_updates(window: MainWindow):
    """runs in a background thread, posts a toast to the main thread when done"""
    try:
        updater = Updater(__version__, True)

        if updater.is_update_available():
            version_tag = updater.latest_release["version"]
            print(f"[Updater] update available: {version_tag}")

            # window.notify() is thread-safe via Qt signal
            window.notify(
                "Update Available",
                f"Version {version_tag} is ready to download.",
                TYPE_UPDATE,
                action_label="Download",
                action_callback=lambda: _open_release_url(updater.latest_release.get("url", ""))
            )

    except Exception as e:
        print("[Updater] error:", e)


def _open_release_url(url: str):
    if url:
        import webbrowser
        webbrowser.open(url)


# ---- entry point ------------------------------------------------------------

if __name__ == "__main__":

    if already_running():
        print("already running")
        sys.exit(0)

    create_lock()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    icon = QIcon(resource_path("resources/icon.ico"))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    threading.Thread(target=check_for_updates, args=(window,), daemon=True).start()

    try:
        exit_code = app.exec()
    finally:
        remove_lock()

    sys.exit(exit_code)
