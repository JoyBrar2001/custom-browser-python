from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QPushButton, QLineEdit,
    QMainWindow, QDialog, QVBoxLayout, QLabel
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QPropertyAnimation, QUrl, Qt
from PyQt6.QtGui import QMouseEvent

from ui.tabs import Tabs
from ui.sidebar import Sidebar
from utils.json_handler import write_file


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
            self.sidebar_open = False

        start = stack.maximumWidth()

        # ❌ OLD BUG: self.sidebar_open > 0
        # ✅ FIX:
        end = 0 if self.sidebar_open else 600

        self.sidebar_open = not self.sidebar_open

        # Animate maximumWidth
        self.animation = QPropertyAnimation(stack, b"maximumWidth")
        self.animation.setDuration(200)
        self.animation.setStartValue(start)
        self.animation.setEndValue(end)

        # Animate minimumWidth (important)
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