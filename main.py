import sys
import requests
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QTabWidget,
    QDialog, QShortcut, QStackedWidget,
    QSizePolicy
)
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QPropertyAnimation, QSize
from PyQt5.QtGui import QKeySequence, QMouseEvent, QIcon, QPixmap
from utils.json_handler import read_file, write_file

class Tabs(QWidget):
    def __init__(self) -> None:
        super().__init__()

        layout = QVBoxLayout(self)
        self.tabs_widget = QTabWidget()
        self.tabs_widget.setTabsClosable(True)

        layout.addWidget(self.tabs_widget)

        self.tabs_widget.tabCloseRequested.connect(self.close_tab)
        
        self.new_tab_shortcut = QShortcut(QKeySequence("Ctrl+T"), self)
        self.new_tab_shortcut.activated.connect(self.add_tab)
        
        self.close_tab_shortcut = QShortcut(QKeySequence("Ctrl+W"), self)
        self.close_tab_shortcut.activated.connect(self.close_current_tab)

        self.reload_shortcut = QShortcut(QKeySequence("Ctrl+R"), self)
        self.reload_shortcut.activated.connect(lambda: self.get_current_browser().reload())

        self.add_tab("https://google.com")

    def add_tab(self, url: Optional[str]=None) -> None:
        if not isinstance(url, str):
            url = "https://google.com"
            
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))

        index = self.tabs_widget.addTab(browser, "New Tab")
        self.tabs_widget.setCurrentIndex(index)

        browser.titleChanged.connect(
            lambda title, browser=browser: self.update_tab_title(browser, title)
        )
        
        browser.iconChanged.connect(
            lambda icon, browser=browser: self.update_tab_icon(browser, icon)
        )
        
    def close_current_tab(self) -> None:
        index = self.tabs_widget.currentIndex()
        self.close_tab(index)

    def update_tab_title(self, browser: QWebEngineView, title: str) -> None:
        index = self.tabs_widget.indexOf(browser)
        if index != -1:
            self.tabs_widget.setTabText(index, title[:20])

    def update_tab_icon(self, browser: QWebEngineView, icon) -> None:
        index = self.tabs_widget.indexOf(browser)
        if index != -1:
            self.tabs_widget.setTabIcon(index, icon)

    def close_tab(self, index: int) -> None:
        if self.tabs_widget.count() > 1:
            self.tabs_widget.removeTab(index)

    def get_current_browser(self) -> QWebEngineView:
        return self.tabs_widget.currentWidget()

class Sidebar(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.container = QWidget()
        self.container_layout = QHBoxLayout(self.container)
        
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
        self.stack.setMaximumWidth(300)
        self.stack.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        
        # Page 1 - Bookmarks
        self.bookmarks_page = QWidget()
        self.bookmarks_layout = QVBoxLayout(self.bookmarks_page)
        
        self.bookmarks_label = QLabel("Bookmarks")
        self.bookmarks_layout.addWidget(self.bookmarks_label)
        self.bookmarks_layout.setAlignment(Qt.AlignTop)
        
        # Page 2 - Whatsapp
        self.whatsapp_browser = QWebEngineView()
        self.whatsapp_browser.setUrl(QUrl("https://web.whatsapp.com"))
        
        # Page 3 - ChatGPT
        self.chatgpt_browser = QWebEngineView()
        self.chatgpt_browser.setUrl(QUrl("https://chat.openai.com"))

        # Add to stack
        self.stack.addWidget(self.bookmarks_page)
        self.stack.addWidget(self.whatsapp_browser)
        self.stack.addWidget(self.chatgpt_browser)
        
        # Layout assembly
        self.container_layout.addLayout(self.tabs_layout)
        self.container_layout.addWidget(self.stack)
        
        self.container_layout.setSpacing(5)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        
        # Bind clicks
        self.btn_bookmarks.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        self.btn_whatsapp.clicked.connect(lambda: self.stack.setCurrentIndex(1))
        self.btn_chatgpt.clicked.connect(lambda: self.stack.setCurrentIndex(2))

        self.setLayout(self.container_layout)
        
        self.tabs = None

    def bind_tabs(self, tabs: Tabs) -> None:
        self.tabs = tabs
        self.initBookmarks()

    def initBookmarks(self) -> None:
        bookmarks = read_file("config/bookmarks.json")
        # Clear old buttons (important if re-rendering)
        for i in reversed(range(1, self.bookmarks_layout.count())):
            widget = self.bookmarks_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        # Dynamically create buttons
        for bookmark in bookmarks:
            title = bookmark["title"]
            path = bookmark["path"]
            
            btn = QPushButton(title)
            
            domain = QUrl(path).host()
            icon_url = f"https://www.google.com/s2/favicons?domain={domain}"
            
            try:
                response = requests.get(icon_url)
                pixmap = QPixmap()
                pixmap.loadFromData(response.content)
                btn.setIcon(QIcon(pixmap))
                btn.setIconSize(QSize(16, 16))
            except:
                pass

            self.bookmarks_layout.addWidget(btn)

            # Fix lambda closure + signal argument
            btn.clicked.connect(lambda _, p=path: self.open_url(p))

    def open_url(self, url: str) -> None:
        if not self.tabs:
            return

        browser = self.tabs.get_current_browser()
        if browser:
            browser.setUrl(QUrl(url))

class TopBar(QWidget):
    def __init__(self, parent: QMainWindow):
        super().__init__()

        self.parent = parent
        self.tabs = None
        self.sidebar = None

        layout = QHBoxLayout(self)

        # Navigation
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.toggle_sidebar_btn = QPushButton("☰")

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or enter URL")

        self.reload_btn = QPushButton("⟳")
        self.star_btn = QPushButton("★")
        self.add_tab_btn = QPushButton("+")

        # Window controls
        self.min_btn = QPushButton("-")
        self.max_btn = QPushButton("□")
        self.close_btn = QPushButton("X")

        # Layout
        layout.addWidget(self.back_btn)
        layout.addWidget(self.forward_btn)
        layout.addWidget(self.toggle_sidebar_btn)
        layout.addStretch()

        layout.addWidget(self.search_bar, 1)

        layout.addWidget(self.reload_btn)
        layout.addWidget(self.star_btn)
        layout.addWidget(self.add_tab_btn)

        layout.addStretch()

        layout.addWidget(self.min_btn)
        layout.addWidget(self.max_btn)
        layout.addWidget(self.close_btn)

        # Connections
        self.min_btn.clicked.connect(self.parent.showMinimized)
        self.max_btn.clicked.connect(self.toggle_maximized)
        self.close_btn.clicked.connect(self.parent.close)

    # ---------- Window Drag ----------
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPos() - self.old_pos
            self.parent.move(self.parent.pos() + delta)
            self.old_pos = event.globalPos()

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.toggle_maximized()

    def toggle_maximized(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()

    # ---------- Bindings ----------
    def bind_tabs(self, tabs: Tabs):
        self.tabs = tabs

        self.add_tab_btn.clicked.connect(self.tabs.add_tab)
        self.tabs.tabs_widget.currentChanged.connect(self.on_tab_changed)
        self.search_bar.returnPressed.connect(self.load_url)

        self.on_tab_changed()

    def bind_sidebar(self, sidebar: Sidebar):
        self.sidebar = sidebar
        self.toggle_sidebar_btn.clicked.connect(self.toggle_sidebar)

    def toggle_sidebar(self):
        if not self.sidebar:
            return

        stack = self.sidebar.stack

        if not hasattr(self, "sidebar_open"):
            self.sidebar_open = True

        start = stack.maximumWidth()
        end = 0 if self.sidebar_open > 0 else 300
        
        self.sidebar_open = not self.sidebar_open
        
         # Animate maximumWidth
        self.animation = QPropertyAnimation(stack, b"maximumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)

        # ALSO animate minimumWidth (CRITICAL)
        self.animation2 = QPropertyAnimation(stack, b"minimumWidth")
        self.animation2.setDuration(200)
        self.animation2.setStartValue(start)
        self.animation2.setEndValue(end)

        self.animation.start()
        self.animation2.start()

    def on_tab_changed(self):
        browser = self.tabs.get_current_browser()
        if not browser:
            return

        self.current_browser = browser

        try:
            self.back_btn.clicked.disconnect()
            self.forward_btn.clicked.disconnect()
            self.reload_btn.clicked.disconnect()
            self.star_btn.clicked.disconnect()
        except:
            pass

        try:
            browser.urlChanged.disconnect()
        except:
            pass

        self.back_btn.clicked.connect(browser.back)
        self.forward_btn.clicked.connect(browser.forward)
        self.reload_btn.clicked.connect(browser.reload)
        self.star_btn.clicked.connect(
            lambda: self.handle_bookmark(self.current_browser)
        )

        browser.urlChanged.connect(self.update_ui)

        self.update_ui()

    def update_ui(self):
        if not self.current_browser:
            return

        self.back_btn.setEnabled(self.current_browser.history().canGoBack())
        self.forward_btn.setEnabled(self.current_browser.history().canGoForward())

        if not self.search_bar.hasFocus():
            self.search_bar.setText(self.current_browser.url().toString())

    def load_url(self):
        url = self.search_bar.text().strip()

        if "." not in url:
            url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"):
            url = "http://" + url

        self.current_browser.setUrl(QUrl(url))

    # ---------- Bookmark ----------
    def handle_bookmark(self, browser: QWebEngineView):
        dialog = QDialog()

        layout = QVBoxLayout()

        name_input = QLineEdit()
        name_input.setText(browser.title())

        submit = QPushButton("Save")

        submit.clicked.connect(
            lambda: self.save_bookmark(
                dialog,
                name_input.text(),
                browser.url().toString()
            )
        )

        layout.addWidget(QLabel("Bookmark Name"))
        layout.addWidget(name_input)
        layout.addWidget(submit)

        dialog.setLayout(layout)
        dialog.exec_()

    def save_bookmark(self, dialog, name, path):
        write_file(
            "config/bookmarks.json",
            lambda data: data + [{"title": name, "path": path}]
        )

        if self.sidebar:
            self.sidebar.initBookmarks()

        dialog.close()

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)

        # Topbar
        self.topbar = TopBar(self)

        # Content area
        self.content = QWidget()
        self.content_layout = QHBoxLayout(self.content)

        self.sidebar = Sidebar()
        self.tabs = Tabs()

        self.topbar.bind_tabs(self.tabs)
        self.topbar.bind_sidebar(self.sidebar)
        self.sidebar.bind_tabs(self.tabs)

        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.tabs)

        self.main_layout.addWidget(self.topbar)
        self.main_layout.addWidget(self.content)

def main():
    app = QApplication(sys.argv)

    profile = QWebEngineProfile.defaultProfile()
    profile.setHttpUserAgent(
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )

    window = MainWindow()
    window.setWindowTitle("My Browser")
    window.resize(1000, 800)
    window.show()

    sys.exit(app.exec_())

if __name__ == "__main__":
    main()