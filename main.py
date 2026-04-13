import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from main_window import MainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Fusion Style gibt uns ein sauberes Basis-Design
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
