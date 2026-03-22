from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

from ui.sidebar import Sidebar
from ui.tabs import Tabs
from ui.topbar import TopBar
from ui.resize_handle import ResizeHandle

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint)

        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)

        self.topbar = TopBar(self)
        self.sidebar = Sidebar()
        self.tabs = Tabs()
        self.resize_handle = ResizeHandle()

        self.resize_handle.bind_sidebar(self.sidebar)
        self.topbar.bind_tabs(self.tabs)
        self.topbar.bind_sidebar(self.sidebar)
        self.sidebar.bind_tabs(self.tabs)

        content = QHBoxLayout()
        content.addWidget(self.sidebar)
        content.addWidget(self.resize_handle)
        content.addWidget(self.tabs)

        main_layout.addWidget(self.topbar)
        main_layout.addLayout(content)