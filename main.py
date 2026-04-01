import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWebEngineCore import QWebEngineProfile

from ui.main_window import MainWindow
from utils.load_stylesheet import load_stylesheet

def main():
    app = QApplication(sys.argv)

    app.setStyleSheet(load_stylesheet("styles/global.qss"))

    profile = QWebEngineProfile().defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    )

    window = MainWindow()
    window.resize(1200, 800)
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()