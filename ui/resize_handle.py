from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent

from ui.sidebar import Sidebar

class ResizeHandle(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(5)
        self.setCursor(Qt.CursorShape.SizeHorCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        label = QLabel(":")
        layout.addWidget(label)

        self.dragging = False
        self.sidebar = None

    def bind_sidebar(self, sidebar: Sidebar):
        self.sidebar = sidebar

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = True
            self.start_x = event.globalPosition().x()
            self.start_width = self.sidebar.stack.width()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and self.sidebar:
            delta = event.globalPosition().x() - self.start_x
            new_width = self.start_width + delta
            new_width = int(max(0, min(600, new_width)))

            self.sidebar.stack.setMinimumWidth(new_width)
            self.sidebar.stack.setMaximumWidth(new_width)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False