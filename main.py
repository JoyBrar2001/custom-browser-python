import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)

    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120 Safari/537.36"
    )

    window = MainWindow()
    window.resize(1000, 800)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()