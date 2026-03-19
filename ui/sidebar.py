from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QSize, Qt
from utils.get_icon import get_icon
from utils.load_stylesheet import load_stylesheet

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        
        self.setObjectName("sidebar")
        self.setAttribute(Qt.WA_StyledBackground, True)

        self.tabs = None
        self.expanded = True

        self.setMinimumWidth(0)
        self.setMaximumWidth(80)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(8, 20, 8, 20)

        self.whatsapp = QPushButton()
        self.youtube = QPushButton()
        self.gmail = QPushButton()
        
        self.whatsapp.setIcon(get_icon("https://web.whatsapp.com"))
        self.youtube.setIcon(get_icon("https://youtube.com"))
        self.gmail.setIcon(get_icon("https://mail.google.com"))

        self.buttons = [self.whatsapp, self.youtube, self.gmail]
        self.active_button = None

        for btn in self.buttons:
            btn.setFixedSize(48, 48)
            btn.setIconSize(QSize(26, 26))
            layout.addWidget(btn)

        layout.addStretch()

        # Animation
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

        # Styling
        self.setStyleSheet(load_stylesheet("styles/ui/sidebar.qss"))

    def set_tabs(self, tabs):
        self.tabs = tabs

        self.whatsapp.clicked.connect(
            lambda: [
                self.tabs.add_tab("https://web.whatsapp.com"),
                self.set_active(self.whatsapp)
            ]
        )
        self.youtube.clicked.connect(
            lambda: [
                self.tabs.add_tab("https://youtube.com"),
                self.set_active(self.youtube)
            ]
        )
        self.gmail.clicked.connect(
            lambda: [
                self.tabs.add_tab("https://mail.google.com"),
                self.set_active(self.gmail)
            ]
        )
        
    def set_active(self, btn):
        for button in self.buttons:
            button.setStyleSheet("")
        
        btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 24px;
            }
        """)
        
        self.active_button = btn

    def toggle(self):
        current_width = self.width()

        if self.expanded:
            self.animation.setStartValue(current_width)
            self.animation.setEndValue(0)
        else:
            self.animation.setStartValue(current_width)
            self.animation.setEndValue(80)

        self.animation.start()
        self.expanded = not self.expanded