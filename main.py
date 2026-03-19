from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl

app = QApplication([])

# Main Window
window = QWidget()
layout = QVBoxLayout()

# Nav bar
nav_bar = QHBoxLayout()

back_btn = QPushButton("⬅ Back")
forward_btn = QPushButton("Forward ➡")

nav_bar.addWidget(back_btn)
nav_bar.addWidget(forward_btn)

# Browser
browser = QWebEngineView()
browser.setUrl(QUrl("https://www.google.com"))

# Connect Buttons
back_btn.clicked.connect(browser.back)
forward_btn.clicked.connect(browser.forward)

# Add to layout
layout.addLayout(nav_bar)
layout.addWidget(browser)

window.setLayout(layout)
window.resize(1000, 700)
window.show()

app.exec()