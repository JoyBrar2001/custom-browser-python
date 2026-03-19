from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout
from .sidebar import Sidebar
from .navbar import Navbar
from .tabs import TabManager

class BrowserWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("My Browser")
        self.resize(1200, 800)

        main_layout = QHBoxLayout(self)

        # Components
        self.sidebar = Sidebar()
        self.tabs = TabManager()
        self.navbar = Navbar()

        # Layout
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.navbar)
        right_layout.addWidget(self.tabs)

        main_layout.addWidget(self.sidebar)
        main_layout.addLayout(right_layout)

        # Connections
        self.navbar.set_tabs(self.tabs)
        self.sidebar.set_tabs(self.tabs)

        # Toggle sidebar
        self.navbar.toggle_btn.clicked.connect(self.sidebar.toggle)