from PyQt5.QtWidgets import QTabWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class TabManager(QTabWidget):
    def __init__(self):
        super().__init__()

        self.setTabsClosable(True)
        self.tabCloseRequested.connect(self.close_tab)

        self.add_tab()

    def current_browser(self):
        return self.currentWidget()

    def add_tab(self, url="https://www.google.com"):
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))

        i = self.addTab(browser, "New Tab")
        self.setCurrentIndex(i)

        browser.titleChanged.connect(
            lambda title, browser=browser: self.setTabText(
                self.indexOf(browser), title[:15]
            )
        )

    def close_tab(self, index):
        if self.count() > 1:
            self.removeTab(index)