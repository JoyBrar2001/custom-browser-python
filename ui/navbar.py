from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QLineEdit, QStyle
from PyQt5.QtCore import QUrl, QSize, Qt
from utils.load_stylesheet import load_stylesheet

class Navbar(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = None
        self.setObjectName("navbar")
        self.setAttribute(Qt.WA_StyledBackground, True)

        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 8, 10, 8)

        style = self.style()
        
        # Buttons with icons
        self.toggle_btn = QPushButton()
        self.toggle_btn.setText("☰")  # keep this for now

        self.back_btn = QPushButton()
        self.back_btn.setIcon(style.standardIcon(QStyle.SP_ArrowBack))

        self.forward_btn = QPushButton()
        self.forward_btn.setIcon(style.standardIcon(QStyle.SP_ArrowForward))

        self.reload_btn = QPushButton()
        self.reload_btn.setIcon(style.standardIcon(QStyle.SP_BrowserReload))

        self.new_tab_btn = QPushButton()
        self.new_tab_btn.setText("+")  # cleaner than unicode plus

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("Search or enter URL...")

        # Add widgets
        for btn in [self.toggle_btn, self.back_btn, self.forward_btn, self.reload_btn]:
            btn.setFixedSize(32, 32)
            btn.setIconSize(QSize(16, 16))
            layout.addWidget(btn)

        layout.addWidget(self.url_bar)

        self.new_tab_btn.setFixedSize(32, 32)
        layout.addWidget(self.new_tab_btn)
        
        self.setStyleSheet(load_stylesheet("styles/ui/navbar.qss"))

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