from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl

app = QApplication([])

# Main Window
window = QWidget()
layout = QVBoxLayout()

# Nav bar
nav_bar = QHBoxLayout()

back_btn = QPushButton("⬅")
forward_btn = QPushButton("➡")
reload_btn = QPushButton("⟳")
new_tab_btn = QPushButton("＋")

url_bar = QLineEdit()

nav_bar.addWidget(back_btn)
nav_bar.addWidget(forward_btn)
nav_bar.addWidget(reload_btn)
nav_bar.addWidget(new_tab_btn)
nav_bar.addWidget(url_bar)

# Tabs
tabs = QTabWidget()
tabs.setTabsClosable(True)

# Function to get current browser
def current_browser():
  return tabs.currentWidget()

# Add Tab
def add_tab(url="https://www.google.com"):
  browser = QWebEngineView()
  browser.setUrl(QUrl(url))
  
  i = tabs.addTab(browser, "New tab")
  tabs.setCurrentIndex(i)
  
  # Update tab title when page loads
  browser.titleChanged.connect(
    lambda title, browser=browser: tabs.setTabText(
      tabs.indexOf(browser), title
    )
  )
  
   # Update URL bar
  browser.urlChanged.connect(
    lambda url, browser=browser: (
      url_bar.setText(url.toString())
      if browser == current_browser() else None
    )
  )
  
# Close Tab
def close_tab(index):
  if tabs.count() > 1:
    tabs.removeTab(index)

tabs.tabCloseRequested.connect(close_tab)

# Connect Buttons
back_btn.clicked.connect(lambda: current_browser().back())
forward_btn.clicked.connect(lambda: current_browser().forward_btn())
reload_btn.clicked.connect(lambda: current_browser().reload())

# Url Bar
url_bar.returnPressed.connect(
  lambda: current_browser().setUrl(QUrl(url_bar.text()))
)

# New Tab Btn
new_tab_btn.clicked.connect(lambda: add_tab())

# Tab Change
def tab_changed():
  browser = current_browser()
  if browser:
    url_bar.setText(browser.url().toString())

tabs.currentChanged.connect(tab_changed)

# Initial Tab
add_tab()

# Add to layout
layout.addLayout(nav_bar)
layout.addWidget(tabs)

window.setLayout(layout)
window.resize(1000, 700)
window.show()

app.exec()