from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QStackedWidget,
    QSizePolicy, QScrollArea, QLineEdit
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QUrl, QSize, QPropertyAnimation

from utils.get_favicon import get_favicon_from_url
from utils.json_handler import read_file, write_file

class WebPanel(QWidget):
    def __init__(self, url: str):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Mini Topbar
        self.nav_bar = QWidget()
        self.nav_bar.setObjectName("sidebar_nav_bar")
        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(6, 4, 6, 4)
        nav_layout.setSpacing(3)
        
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("⟳")
        
        for btn in (self.back_btn, self.forward_btn, self.reload_btn):
            btn.setObjectName("sidebar_nav_btn")
            btn.setFixedSize(28, 28)
            
        self.url_label = QLineEdit()
        self.url_label.setObjectName("sidebar_url_bar")
        self.url_label.setReadOnly(True)
        self.url_label.setPlaceholderText("Loading...")
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_label, 1)
        
        # Web View
        self.view = QWebEngineView()
        self.view.setUrl(QUrl(url))
        
        self.nav_bar.setFixedHeight(36)
        layout.addWidget(self.nav_bar, 0)
        layout.addWidget(self.view, 1)
        
        # Wire Up
        self.back_btn.clicked.connect(self.view.back)
        self.forward_btn.clicked.connect(self.view.forward)
        self.reload_btn.clicked.connect(self.view.reload)
        
        self.view.urlChanged.connect(self.on_url_changed)
        self.view.loadFinished.connect(self.update_nav_state)
        
        self.update_nav_state()
        
    def on_url_changed(self, url: QUrl):
        self.url_label.setText(url.toString())
        self.update_nav_state()
    
    def update_nav_state(self):
        history = self.view.history()
        self.back_btn.setEnabled(history.canGoBack())
        self.forward_btn.setEnabled(history.canGoForward())
    
    def navigate(self, url: str):
        self.view.setUrl(QUrl(url))
        

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.container_layout = QHBoxLayout(self)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(0)

        # ── Icon rail ──────────────────────────────────────
        self.icon_rail = QWidget()
        self.icon_rail.setObjectName("sidebar_icon_bar")
        self.icon_rail.setFixedWidth(46)

        self.tabs_layout = QVBoxLayout(self.icon_rail)
        self.tabs_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.tabs_layout.setContentsMargins(5, 8, 5, 8)
        self.tabs_layout.setSpacing(4)

        self.btn_bookmarks = QPushButton("📌")
        self.btn_whatsapp = QPushButton()
        self.whatsapp_icon = get_favicon_from_url("https://whatsapp.com")
        self.btn_whatsapp.setIcon(self.whatsapp_icon)
        self.btn_whatsapp.setIconSize(QSize(20, 20))
        self.btn_chatgpt = QPushButton()
        self.chatgpt_icon = get_favicon_from_url("https://chat.openai.com")
        self.btn_chatgpt.setIcon(self.chatgpt_icon)
        self.btn_chatgpt.setIconSize(QSize(20, 20))

        self._icon_buttons = [self.btn_bookmarks, self.btn_whatsapp, self.btn_chatgpt]

        for btn in self._icon_buttons:
            btn.setFixedSize(36, 36)
            self.tabs_layout.addWidget(btn)

        # ── Stack (panel) ──────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setObjectName("sidebar_stack")
        self.stack.setMinimumWidth(0)
        self.stack.setMaximumWidth(260)
        self.stack.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)

        # Bookmarks page
        self.bookmarks_page = QWidget()
        bookmarks_outer = QVBoxLayout(self.bookmarks_page)
        bookmarks_outer.setContentsMargins(0, 0, 0, 0)
        bookmarks_outer.setSpacing(0)

        header = QLabel("BOOKMARKS")
        header.setObjectName("section_label")
        bookmarks_outer.addWidget(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        scroll_content = QWidget()
        self.bookmarks_layout = QVBoxLayout(scroll_content)
        self.bookmarks_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.bookmarks_layout.setContentsMargins(0, 4, 0, 8)
        self.bookmarks_layout.setSpacing(2)

        scroll.setWidget(scroll_content)
        bookmarks_outer.addWidget(scroll)

        # Web panel pages
        self.whatsapp_page = WebPanel("https://web.whatsapp.com")

        self.chatgpt_page = WebPanel("https://chat.openai.com")

        self.bookmarks_page.setProperty("type", "bookmarks")
        self.whatsapp_page.setProperty("type", "web")
        self.chatgpt_page.setProperty("type", "web")

        self.stack.addWidget(self.bookmarks_page)
        self.stack.addWidget(self.whatsapp_page)
        self.stack.addWidget(self.chatgpt_page)

        self.container_layout.addWidget(self.icon_rail)
        self.container_layout.addWidget(self.stack)

        self.btn_bookmarks.clicked.connect(lambda: self.handle_page_change(0))
        self.btn_whatsapp.clicked.connect(lambda: self.handle_page_change(1))
        self.btn_chatgpt.clicked.connect(lambda: self.handle_page_change(2))

        self.handle_page_change(0)
        self.tabs = None

    def _set_active_btn(self, index: int):
        for i, btn in enumerate(self._icon_buttons):
            btn.setProperty("active", "true" if i == index else "false")
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def bind_tabs(self, tabs):
        self.tabs = tabs
        self.initBookmarks()

    def initBookmarks(self):
        bookmarks = read_file("config/bookmarks.json")
        self.clear_bookmarks()

        for bookmark in bookmarks:
            container = QWidget()
            container.setObjectName("bookmark_item")
            layout = QHBoxLayout(container)
            layout.setContentsMargins(4, 2, 4, 2)
            layout.setSpacing(0)

            btn = QPushButton(bookmark["title"])
            btn.setObjectName("bookmark_btn")
            icon = get_favicon_from_url(bookmark["path"])
            btn.setIcon(icon)
            btn.setIconSize(QSize(14, 14))
            btn.clicked.connect(lambda _, p=bookmark["path"]: self.open_url(p))

            delete_btn = QPushButton("✕")
            delete_btn.setObjectName("delete_btn")
            delete_btn.clicked.connect(lambda _, p=bookmark["path"]: self.delete_bookmark(p))

            layout.addWidget(btn, 1)
            layout.addWidget(delete_btn)

            self.bookmarks_layout.addWidget(container)

    def clear_bookmarks(self):
        while self.bookmarks_layout.count():
            item = self.bookmarks_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def delete_bookmark(self, path):
        write_file(
            "config/bookmarks.json", 
            update_fn=lambda bm: [b for b in bm if b["path"] != path]
        )
        self.initBookmarks()

    def open_url(self, url):
        if self.tabs:
            browser = self.tabs.get_current_browser()
            if browser:
                browser.setUrl(QUrl(url))

    def handle_page_change(self, index: int):
        widget = self.stack.widget(index)
        page_type = widget.property("type")
        width = 800 if page_type == "web" else 260
        self._set_active_btn(index)
        self.set_sidebar_width(width)
        self.stack.setCurrentIndex(index)

    def get_current_width(self) -> int:
        widget = self.stack.currentWidget()
        return 800 if widget.property("type") == "web" else 260

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