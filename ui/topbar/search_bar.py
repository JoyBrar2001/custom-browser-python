from PyQt6.QtWidgets import QLineEdit
from PyQt6.QtCore import Qt

class SearchBar(QLineEdit):
    def __init__(self, topbar):
        super().__init__()

        self.topbar = topbar
        self.is_focused = False

        # Default state (centered for first load)
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    def focusInEvent(self, event):
        super().focusInEvent(event)
        self.is_focused = True

        if self.topbar.current_browser:
            full_url = self.topbar.current_browser.url().toString()
            self.setText(full_url)
            self.selectAll()

        # Keep centered while focused
        self.setAlignment(Qt.AlignmentFlag.AlignHCenter)

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.is_focused = False

        # Let TopBar decide what to show
        self.topbar.update_ui()

        # After user interaction → left align
        self.setAlignment(Qt.AlignmentFlag.AlignLeft)