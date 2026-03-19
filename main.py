from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl

app = QApplication([])

browser = QWebEngineView()
browser.setUrl(QUrl("https://www.google.com"))

browser.show()
app.exec()