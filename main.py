from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import QUrl

app = QApplication([])

# Main Window
window = QWidget()
main_layout = QHBoxLayout()

# Sidebar (Left)
sidebar = QVBoxLayout()

whatsapp_btn = QPushButton("WhatsApp")
youtube_btn = QPushButton("Youtube")
gmail_btn = QPushButton("Gmail")

sidebar.addWidget(whatsapp_btn)
sidebar.addWidget(youtube_btn)
sidebar.addWidget(gmail_btn)
sidebar.addStretch()

# Sidebar button actions
whatsapp_btn.clicked.connect(
    lambda: add_tab("https://web.whatsapp.com")
)

youtube_btn.clicked.connect(
    lambda: add_tab("https://www.youtube.com")
)

gmail_btn.clicked.connect(
    lambda: add_tab("https://mail.google.com")
)

# Right Side
right_layout = QVBoxLayout()

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

# Main Layout
right_layout.addLayout(nav_bar)
right_layout.addWidget(tabs)

main_layout.addLayout(sidebar, 1)
main_layout.addLayout(right_layout, 5)

window.setLayout(main_layout)
window.resize(1000, 700)
window.show()

app.exec()