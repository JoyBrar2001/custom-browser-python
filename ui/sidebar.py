from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget, QSizePolicy
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QSize, QPropertyAnimation

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
        self.stack.setMaximumWidth(200)
        self.stack.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Pages
        self.bookmarks_page = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_page)
        self.bookmarks_layout.addWidget(QLabel("Bookmarks"))
        self.bookmarks_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter)

        self.whatsapp_page = QWebEngineView()
        self.whatsapp_page.setUrl(QUrl("https://web.whatsapp.com"))

        self.chatgpt_page = QWebEngineView()
        self.chatgpt_page.setUrl(QUrl("https://chat.openai.com"))

        self.bookmarks_page.setProperty("type", "bookmarks")
        self.whatsapp_page.setProperty("type", "web")
        self.chatgpt_page.setProperty("type", "web")

        self.stack.addWidget(self.bookmarks_page)
        self.stack.addWidget(self.whatsapp_page)
        self.stack.addWidget(self.chatgpt_page)

        self.container_layout.addLayout(self.tabs_layout)
        self.container_layout.addWidget(self.stack)

        self.btn_bookmarks.clicked.connect(lambda: self.handle_page_change(0))
        self.btn_whatsapp.clicked.connect(lambda: self.handle_page_change(1))
        self.btn_chatgpt.clicked.connect(lambda: self.handle_page_change(2))
        
        self.handle_page_change(0)
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
                
    def handle_page_change(self, index: int):
        widget = self.stack.widget(index)
        page_type = widget.property("type")
        
        if page_type == "bookmarks":
            width = 300
        elif page_type == "web":
            width = 800
        else:
            width = 400
        
        self.set_sidebar_width(width)
        self.stack.setCurrentIndex(index)
        
    def get_current_width(self) -> int:
        widget = self.stack.currentWidget()
        page_type = widget.property("type")
        
        if page_type == "bookmarks":
            return 300
        elif page_type == "web":
            return 800    
        return 400
                
    def set_sidebar_width(self, width: int):
        self.animation = QPropertyAnimation(self.stack, b"maximumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(self.stack.width())
        self.animation.setEndValue(width)
        
        self.animation2 = QPropertyAnimation(self.stack, b"minimumWidth")
        self.animation2.setDuration(200)
        self.animation2.setStartValue(self.stack.width())
        self.animation2.setEndValue(width)
        
        self.animation.start()
        self.animation2.start()