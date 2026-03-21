# ui/browser_window.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt
from .sidebar import Sidebar
from .web_area import WebArea
from utils.load_stylesheet import load_stylesheet

class BrowserWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Browser")
        self.resize(1200, 800)

        self.setObjectName("root")
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(load_stylesheet("styles/global.qss"))

        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Components
        self.sidebar = Sidebar()
        self.web_area = WebArea()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.web_area)

        # Connections
        self.web_area.set_tabs_connections()
        self.sidebar.set_tabs(self.web_area.tabs)

        # Toggle sidebar
        self.web_area.navbar.toggle_btn.clicked.connect(self.sidebar.toggle)