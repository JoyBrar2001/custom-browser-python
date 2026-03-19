from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve

class Sidebar(QWidget):
    def __init__(self):
        super().__init__()

        self.tabs = None
        self.expanded = True

        self.setMinimumWidth(0)
        self.setMaximumWidth(80)

        layout = QVBoxLayout(self)

        self.whatsapp = QPushButton("💬")
        self.youtube = QPushButton("▶")
        self.gmail = QPushButton("✉")

        for btn in [self.whatsapp, self.youtube, self.gmail]:
            btn.setFixedSize(50, 50)
            layout.addWidget(btn)

        layout.addStretch()

        # Animation
        self.animation = QPropertyAnimation(self, b"maximumWidth")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.InOutCubic)

        # Styling
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; }
            QPushButton {
                background-color: #2b2b2b;
                color: white;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #3c3c3c;
            }
        """)

    def set_tabs(self, tabs):
        self.tabs = tabs

        self.whatsapp.clicked.connect(
            lambda: self.tabs.add_tab("https://web.whatsapp.com")
        )
        self.youtube.clicked.connect(
            lambda: self.tabs.add_tab("https://youtube.com")
        )
        self.gmail.clicked.connect(
            lambda: self.tabs.add_tab("https://mail.google.com")
        )

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