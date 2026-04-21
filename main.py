import sys
import os
import tempfile
import subprocess
import threading

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon

from ui.main_window import MainWindow
from updater import Updater
from meta import __version__


# ---------------- LOCK ----------------

LOCK_FILE = os.path.join(
    tempfile.gettempdir(),
    "vrc_soundboard.lock"
)


# ---------------- FUNCTIONS ----------------

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
    except:
        return False


def already_running():
    if not os.path.exists(LOCK_FILE):
        return False

    try:
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())

        if is_process_running(pid):
            return True

    except:
        pass

    try:
        os.remove(LOCK_FILE)
    except:
        pass

    return False


def create_lock():
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))


def remove_lock():
    try:
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    except:
        pass


# ---------------- UPDATE CHECK ----------------

def check_for_updates():
    try:
        updater = Updater(__version__, True)

        if updater.is_update_available():
            print(f"[Updater] Update verfügbar: {updater.latest_release['version']}")

    except Exception as e:
        print("[Updater] Fehler:", e)


# ---------------- MAIN ----------------

if __name__ == "__main__":

    if already_running():
        print("App läuft bereits!")
        sys.exit(0)

    create_lock()

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    icon = QIcon(resource_path("resources/icon.ico"))
    app.setWindowIcon(icon)

    window = MainWindow()
    window.setWindowIcon(icon)
    window.show()

    # ---------------- THREADING UPDATE CHECK ----------------
    threading.Thread(target=check_for_updates, daemon=True).start()

    try:
        exit_code = app.exec()
    finally:
        remove_lock()

    sys.exit(exit_code)