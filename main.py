import sys
from typing import Optional
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QLineEdit, QTabWidget,
    QDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineProfile, QWebEngineView
from PyQt5.QtCore import QUrl, Qt
from utils.json_handler import read_file, write_file

class Tabs(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.tabs_widget = QTabWidget()
        self.tabs_widget.setTabsClosable(True)

        self.layout.addWidget(self.tabs_widget)

        self.tabs_widget.tabCloseRequested.connect(self.close_tab)

        self.add_tab("https://google.com")

    def add_tab(self, url: Optional[str]=None) -> None:
        if not isinstance(url, str):
            url = "https://google.com"
            
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))

        index = self.tabs_widget.addTab(browser, "New Tab")
        self.tabs_widget.setCurrentIndex(index)

        browser.urlChanged.connect(
            lambda qurl, browser=browser: self.update_tab_title(browser, qurl)
        )

    def update_tab_title(self, browser: QWebEngineView, qurl: QUrl) -> None:
        index = self.tabs_widget.indexOf(browser)
        if index != -1:
            self.tabs_widget.setTabText(index, qurl.toString()[:20])

    def close_tab(self, index: int) -> None:
        if self.tabs_widget.count() > 1:
            self.tabs_widget.removeTab(index)

    def get_current_browser(self):
        return self.tabs_widget.currentWidget()

class Sidebar(QWidget):
    def __init__(self) -> None:
        super().__init__()

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
            self.sidebar_layout.addWidget(btn)

            # Fix lambda closure + signal argument
            btn.clicked.connect(lambda _, p=path: self.open_url(p))

    def open_url(self, url: str) -> None:
        if not self.tabs:
            return

        browser = self.tabs.get_current_browser()
        if browser:
            browser.setUrl(QUrl(url))

class Navbar(QWidget):
    def __init__(self) -> None:
        super().__init__()

        self.navbar_layout = QHBoxLayout(self)

        self.back_btn = QPushButton("Back")
        self.forward_btn = QPushButton("Forward")
        self.reload_btn = QPushButton("Reload")
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search or enter URL")
        self.star_button = QPushButton("Star")
        self.add_tab_button = QPushButton("+")

        self.navbar_layout.addWidget(self.back_btn)
        self.navbar_layout.addWidget(self.forward_btn)
        self.navbar_layout.addWidget(self.reload_btn)
        self.navbar_layout.addWidget(self.search_bar)
        self.navbar_layout.addWidget(self.star_button)
        self.navbar_layout.addWidget(self.add_tab_button)

        self.current_browser = None

    def bind_tabs(self, tabs: Tabs) -> None:
        self.tabs = tabs

        self.add_tab_button.clicked.connect(self.tabs.add_tab)
        self.tabs.tabs_widget.currentChanged.connect(self.on_tab_changed)
        self.search_bar.returnPressed.connect(self.load_url)

        self.on_tab_changed()
        
    def bind_sidebar(self, sidebar: Sidebar) -> None:
        self.sidebar = sidebar

    def on_tab_changed(self) -> None:
        browser = self.tabs.get_current_browser()
        if not browser:
            return

        self.current_browser = browser

        try:
            self.back_btn.clicked.disconnect()
            self.forward_btn.clicked.disconnect()
            self.reload_btn.clicked.disconnect()
            self.star_button.clicked.disconnect()
        except:
            pass

        try:
            browser.urlChanged.disconnect()
        except:
            pass

        self.back_btn.clicked.connect(browser.back)
        self.forward_btn.clicked.connect(browser.forward)
        self.reload_btn.clicked.connect(browser.reload)
        self.star_button.clicked.connect(lambda: self.handle_bookmark(self.current_browser))

        browser.urlChanged.connect(self.update_ui)

        self.update_ui()

    def handle_bookmark(self, browser: QWebEngineView) -> None:
        self.dialog = QDialog()
        
        dialog_layout = QVBoxLayout()
        
        dialog_label = QLabel("Add Website to Bookmarks")
        dialog_name = QLabel("Name")
        dialog_name_input = QLineEdit()
        dialog_submit = QPushButton("Submit")
        
        dialog_name_input.setText(browser.title())
        dialog_submit.clicked.connect(
            lambda: self.handle_bookmark_submit(
                dialog_name_input.text(), 
                browser.url().toString()
            )
        )
        
        dialog_layout.addWidget(dialog_label)
        dialog_layout.addWidget(dialog_name)
        dialog_layout.addWidget(dialog_name_input)
        dialog_layout.addWidget(dialog_submit)
        
        self.dialog.setLayout(dialog_layout)
        
        self.dialog.exec_()
    
    def handle_bookmark_submit(self, name: str, path: str) -> None:
        write_file(
            "config/bookmarks.json",
            lambda data: data + [{
                "title": name,
                "path": path
            }]
        )
        
        self.sidebar.initBookmarks()
        
        self.dialog.close()

    def update_ui(self) -> None:
        if not self.current_browser:
            return

        self.back_btn.setEnabled(self.current_browser.history().canGoBack())
        self.forward_btn.setEnabled(self.current_browser.history().canGoForward())

        if not self.search_bar.hasFocus():
            self.search_bar.setText(self.current_browser.url().toString())

    def load_url(self) -> None:
        url = self.search_bar.text().strip()

        if "." not in url:
            url = f"https://www.google.com/search?q={url}"
        elif not url.startswith("http"):
            url = "http://" + url

        self.current_browser.setUrl(QUrl(url))

class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self) -> None:
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout(self.central_widget)

        self.sidebar = Sidebar()

        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)

        self.navbar = Navbar()
        self.navbar.bind_sidebar(self.sidebar)
        self.tabs = Tabs()

        self.navbar.bind_tabs(self.tabs)
        self.sidebar.bind_tabs(self.tabs)

        self.right_layout.addWidget(self.navbar, 1)
        self.right_layout.addWidget(self.tabs, 5)

        self.main_layout.addWidget(self.sidebar, 1)
        self.main_layout.addWidget(self.right_widget, 5)

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