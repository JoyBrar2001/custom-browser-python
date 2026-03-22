from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QSize
from PyQt6.QtGui import QIcon, QPixmap

from utils.get_favicon import get_favicon_from_url
from utils.json_handler import read_file
from utils.get_favicon import get_favicon_from_url

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.container_layout = QHBoxLayout(self)

        self.tabs_layout = QVBoxLayout()
        self.tabs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.btn_bookmarks = QPushButton("📌")
        self.btn_whatsapp = QPushButton()
        self.whatsapp_icon = get_favicon_from_url("https://whatsapp.com")
        self.btn_whatsapp.setIcon(self.whatsapp_icon)
        self.btn_chatgpt = QPushButton()
        self.chatgpt_icon = get_favicon_from_url("https://chat.openai.com")
        self.btn_chatgpt.setIcon(self.chatgpt_icon)

        for btn in [self.btn_bookmarks, self.btn_whatsapp, self.btn_chatgpt]:
            btn.setFixedSize(40, 40)
            self.tabs_layout.addWidget(btn)

        self.stack = QStackedWidget()
        self.stack.setMinimumWidth(0)
        self.stack.setMaximumWidth(600)
        self.stack.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Pages
        self.bookmarks_page = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_page)
        self.bookmarks_layout.addWidget(QLabel("Bookmarks"))
        self.bookmarks_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

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

            icon = get_favicon_from_url(bookmark["path"])

            btn.setIcon(icon)
            btn.setIconSize(QSize(16, 16))
            
            btn.clicked.connect(lambda _, p=bookmark["path"]: self.open_url(p))
            self.bookmarks_layout.addWidget(btn)

    def open_url(self, url):
        if self.tabs:
            browser = self.tabs.get_current_browser()
            if browser:
                browser.setUrl(QUrl(url))