from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

class ResizeHandle(QWidget):
    def __init__(self):
        super().__init__()

        self.setFixedWidth(5)
        self.setCursor(Qt.SizeHorCursor)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(":")
        layout.addWidget(label)

        self.dragging = False
        self.sidebar = None

    def bind_sidebar(self, sidebar):
        self.sidebar = sidebar

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.start_x = event.globalX()
            self.start_width = self.sidebar.stack.width()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging and self.sidebar:
            delta = event.globalX() - self.start_x
            new_width = self.start_width + delta
            new_width = max(0, min(600, new_width))

            self.sidebar.stack.setMinimumWidth(new_width)
            self.sidebar.stack.setMaximumWidth(new_width)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.dragging = False