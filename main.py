from app.ui.main_window import MainWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
import sys
from pathlib import Path


def main():
    app = QApplication(sys.argv)

    # Project folder
    BASE_DIR = Path(__file__).resolve().parent

    # Icon path
    ICON_PATH = BASE_DIR / "asset" / "Arinutpam Logo.jpeg"

    # Set application icon
    if ICON_PATH.exists():
        app.setWindowIcon(
            QIcon(str(ICON_PATH))
        )
    else:
        print(f"Icon not found: {ICON_PATH}")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()