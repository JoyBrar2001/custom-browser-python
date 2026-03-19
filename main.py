from PyQt5.QtWidgets import QApplication
from PyQt5.QtWebEngineWidgets import QWebEngineProfile
from ui.browser import BrowserWindow

app = QApplication([])

# Global user agent
profile = QWebEngineProfile.defaultProfile()
profile.setHttpUserAgent(
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

window = BrowserWindow()
window.show()

app.exec_()