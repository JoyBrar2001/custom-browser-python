from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl


class WebPanel(QWidget):
    def __init__(self, url: str):
        super().__init__()
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # ── Mini Topbar ─────────────────────────────
        self.nav_bar = QWidget()
        self.nav_bar.setObjectName("sidebar_nav_bar")

        nav_layout = QHBoxLayout(self.nav_bar)
        nav_layout.setContentsMargins(6, 4, 6, 4)
        nav_layout.setSpacing(3)
        
        self.back_btn = QPushButton("←")
        self.forward_btn = QPushButton("→")
        self.reload_btn = QPushButton("⟳")
        
        for btn in (self.back_btn, self.forward_btn, self.reload_btn):
            btn.setObjectName("sidebar_nav_btn")
            btn.setFixedSize(28, 28)
            
        self.url_label = QLineEdit()
        self.url_label.setObjectName("sidebar_url_bar")
        self.url_label.setReadOnly(True)
        self.url_label.setPlaceholderText("Loading...")
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_label, 1)
        
        # ── Web View ───────────────────────────────
        self.view = QWebEngineView()
        self.view.setUrl(QUrl(url))
        
        self.nav_bar.setFixedHeight(36)
        layout.addWidget(self.nav_bar, 0)
        layout.addWidget(self.view, 1)
        
        # ── Signals ────────────────────────────────
        self.back_btn.clicked.connect(self.view.back)
        self.forward_btn.clicked.connect(self.view.forward)
        self.reload_btn.clicked.connect(self.view.reload)
        
        self.view.urlChanged.connect(self.on_url_changed)
        self.view.loadFinished.connect(self.update_nav_state)
        
        self.update_nav_state()
        
    def on_url_changed(self, url: QUrl):
        self.url_label.setText(url.toString())
        self.update_nav_state()
    
    def update_nav_state(self):
        history = self.view.history()
        self.back_btn.setEnabled(history.canGoBack())
        self.forward_btn.setEnabled(history.canGoForward())
    
    def navigate(self, url: str):
        self.view.setUrl(QUrl(url))