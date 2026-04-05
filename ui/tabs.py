from typing import Optional
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QKeySequence, QShortcut

from ui.history_page import HistoryPage

from utils.history_handler import record

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
        
        self.tabs_widget.currentChanged.connect(self.on_tab_switched)

        QShortcut(QKeySequence("Ctrl+T"), self).activated.connect(self.add_tab)
        QShortcut(QKeySequence("Ctrl+W"), self).activated.connect(self.close_current_tab)
        QShortcut(QKeySequence("Ctrl+R"), self).activated.connect(
            lambda: self.get_current_browser() and self.get_current_browser().reload()
        )
        QShortcut(QKeySequence("Ctrl+H"), self).activated.connect(self.add_history_tab)

        self.sidebar = None
        self.add_tab("https://google.com")

    def bind_sidebar(self, sidebar):
        self.sidebar = sidebar

    def add_tab(self, url: Optional[str] = None):
        if not isinstance(url, str):
            url = "https://google.com"

        browser = QWebEngineView()
        browser.setUrl(QUrl(url))

        index = self.tabs_widget.addTab(browser, "New Tab")
        self.tabs_widget.setCurrentIndex(index)

        browser.titleChanged.connect(lambda title, b=browser: self.update_tab_title(b, title))
        browser.iconChanged.connect(lambda icon, b=browser: self.update_tab_icon(b, icon))
        browser.loadFinished.connect(lambda ok, b=browser: self.record_visit(b, ok))

    def close_current_tab(self):
        self.close_tab(self.tabs_widget.currentIndex())
        
    def add_history_tab(self):
        for i in range(self.tabs_widget.count()):
            widget = self.tabs_widget.widget(1)
            
            if isinstance(widget, HistoryPage):
                self.tabs_widget.setCurrentIndex(i)
                widget.refresh()
                return

        page = HistoryPage(open_url_fn=lambda url: self.add_tab(url))
        
        index = self.tabs_widget.addTab(page, "🕘  History")
        self.tabs_widget.setCurrentIndex(index)

    def on_tab_switched(self, index: int):
        widget = self.tabs_widget.widget(index)
        if isinstance(widget, HistoryPage):
            widget.refresh()
            
    def record_visit(self, browser: QWebEngineView, ok: bool):
        if not ok:
            return

        url = browser.url().toString()
        title = browser.title()
        record(title, url)

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
        widget = self.tabs_widget.currentWidget()
        if isinstance(widget, QWebEngineView):
            return widget
        return None