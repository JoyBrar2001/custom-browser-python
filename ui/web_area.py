# ui/web_area.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from .tabs import TabManager
from .navbar import Navbar

class WebArea(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(4)

        # Components inside the web area
        self.navbar = Navbar()
        self.tabs = TabManager()

        self.layout.addWidget(self.navbar)
        self.layout.addWidget(self.tabs)

    def set_tabs_connections(self):
        self.navbar.set_tabs(self.tabs)