import sys
import requests
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QTabWidget,
    QDialog, QShortcut
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
        
        self.setMaximumWidth(200)
        
        self.sidebar_layout = QVBoxLayout(self)
        self.sidebar_label = QLabel("Your Bookmarks")

        self.sidebar_layout.addWidget(self.sidebar_label)
        self.sidebar_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        self.tabs = None

    def bind_tabs(self, tabs: Tabs) -> None:
        self.tabs = tabs
        self.initBookmarks()

    def initBookmarks(self) -> None:
        bookmarks = read_file("config/bookmarks.json")
        # Clear old buttons (important if re-rendering)
        for i in reversed(range(1, self.sidebar_layout.count())):
            widget = self.sidebar_layout.itemAt(i).widget()
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

            self.sidebar_layout.addWidget(btn)

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

        current_width = self.sidebar.width()
        new_width = 0 if current_width > 0 else 200
        
        self.sidebar_animation = QPropertyAnimation(self.sidebar, b"maximumWidth")
        self.sidebar_animation.setDuration(200)
        self.sidebar_animation.setStartValue(current_width)
        self.sidebar_animation.setEndValue(new_width)
        self.sidebar_animation.start()

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

        self.content_layout.addWidget(self.sidebar, 1)
        self.content_layout.addWidget(self.tabs, 5)

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