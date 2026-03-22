import requests
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy
)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QSize
from PyQt5.QtGui import QIcon, QPixmap
from utils.json_handler import read_file

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.container_layout = QHBoxLayout(self)

        self.tabs_layout = QVBoxLayout()
        self.tabs_layout.setAlignment(Qt.AlignTop)

        self.btn_bookmarks = QPushButton("📌")
        self.btn_whatsapp = QPushButton("💬")
        self.btn_chatgpt = QPushButton("🤖")

        for btn in [self.btn_bookmarks, self.btn_whatsapp, self.btn_chatgpt]:
            btn.setFixedSize(40, 40)
            self.tabs_layout.addWidget(btn)

        self.stack = QStackedWidget()
        self.stack.setMinimumWidth(0)
        self.stack.setMaximumWidth(600)
        self.stack.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

        # Pages
        self.bookmarks_page = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_page)
        self.bookmarks_layout.addWidget(QLabel("Bookmarks"))
        self.bookmarks_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.whatsapp_browser = QWebEngineView()
        self.whatsapp_browser.setUrl(QUrl("https://web.whatsapp.com"))

        self.chatgpt_browser = QWebEngineView()
        self.chatgpt_browser.setUrl(QUrl("https://chat.openai.com"))

        self.stack.addWidget(self.bookmarks_page)
        self.stack.addWidget(self.whatsapp_browser)
        self.stack.addWidget(self.chatgpt_browser)

        self.container_layout.addLayout(self.tabs_layout)
        self.container_layout.addWidget(self.stack)

        self.btn_bookmarks.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_whatsapp.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_chatgpt.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.tabs = None

    def bind_tabs(self, tabs):
        self.tabs = tabs
        self.initBookmarks()

    def initBookmarks(self):
        bookmarks = read_file("config/bookmarks.json")

        for bookmark in bookmarks:
            btn = QPushButton(bookmark["title"])

            domain = QUrl(bookmark["path"]).host()
            icon_url = f"https://www.google.com/s2/favicons?domain={domain}"

            try:
                response = requests.get(icon_url)
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(16, 16))
            except:
                pass

            btn.clicked.connect(lambda _, p=bookmark["path"]: self.open_url(p))
            self.bookmarks_layout.addWidget(btn)

    def open_url(self, url):
        if self.tabs:
            browser = self.tabs.get_current_browser()
            if browser:
                browser.setUrl(QUrl(url))