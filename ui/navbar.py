from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit
from PyQt5.QtCore import QUrl

class Navbar(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = None

        layout = QHBoxLayout(self)

        self.toggle_btn = QPushButton("☰")
        self.back_btn = QPushButton("⬅")
        self.forward_btn = QPushButton("➡")
        self.reload_btn = QPushButton("⟳")
        self.new_tab_btn = QPushButton("＋")
        self.url_bar = QLineEdit()

        layout.addWidget(self.toggle_btn)
        layout.addWidget(self.back_btn)
        layout.addWidget(self.forward_btn)
        layout.addWidget(self.reload_btn)
        layout.addWidget(self.url_bar)
        layout.addWidget(self.new_tab_btn)

    def set_tabs(self, tabs):
        self.tabs = tabs

        self.back_btn.clicked.connect(lambda: self.tabs.current_browser().back())
        self.forward_btn.clicked.connect(lambda: self.tabs.current_browser().forward())
        self.reload_btn.clicked.connect(lambda: self.tabs.current_browser().reload())
        self.new_tab_btn.clicked.connect(lambda: self.tabs.add_tab())

        self.url_bar.returnPressed.connect(
            lambda: self.tabs.current_browser().setUrl(QUrl(self.url_bar.text()))
        )

        self.tabs.currentChanged.connect(self.update_url)

    def update_url(self):
        browser = self.tabs.current_browser()
        if browser:
            self.url_bar.setText(browser.url().toString())