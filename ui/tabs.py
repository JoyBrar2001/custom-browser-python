from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QKeySequence, QShortcut


class Tabs(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.tabs_widget = QTabWidget()
        self.tabs_widget.setTabsClosable(True)
        self.tabs_widget.setDocumentMode(True)   # cleaner look — no frame around tab bar

        layout.addWidget(self.tabs_widget)

        self.tabs_widget.tabCloseRequested.connect(self.close_tab)

        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.add_tab)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(
            lambda: self.get_current_browser() and self.get_current_browser().reload()
        )

        self.add_tab("https://google.com")

    def add_tab(self, url: Optional[str] = None):
        if not isinstance(url, str):
            url = "https://google.com"

        browser = QWebEngineView()
        browser.setUrl(QUrl(url))

        index = self.tabs_widget.addTab(browser, "New Tab")
        self.tabs_widget.setCurrentIndex(index)

        browser.titleChanged.connect(lambda title, b=browser: self.update_tab_title(b, title))
        browser.iconChanged.connect(lambda icon, b=browser: self.update_tab_icon(b, icon))

    def close_current_tab(self):
        self.close_tab(self.tabs_widget.currentIndex())

    def close_tab(self, index):
        if self.tabs_widget.count() > 1:
            self.tabs_widget.removeTab(index)

    def update_tab_title(self, browser, title):
        index = self.tabs_widget.indexOf(browser)
        if index != -1:
            self.tabs_widget.setTabText(index, title[:22])

    def update_tab_icon(self, browser, icon):
        index = self.tabs_widget.indexOf(browser)
        if index != -1:
            self.tabs_widget.setTabIcon(index, icon)

    def get_current_browser(self):
        return self.tabs_widget.currentWidget()