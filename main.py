import sys
import os
import tempfile
import subprocess
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from main_window import MainWindow

# ---------------- META ----------------

__version__ = "0.4.0"
__author__ = "Yannik / M o o n y ~"

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
    """Windows-only check if PID exists"""
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

    # stale lock entfernen
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

    try:
        exit_code = app.exec()
    finally:
        remove_lock()

    sys.exit(exit_code)