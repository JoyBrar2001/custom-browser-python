from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea,
    QApplication
)
from PyQt6.QtCore import Qt
from PyQt6 import sip
from datetime import datetime
from urllib.parse import urlparse

from utils import history_handler
from utils.favicon_worker import FaviconWorker, favicon_cache

class HistoryPage(QWidget):
    def __init__(self, open_url_fn):
        super().__init__()
        self.open_url_fn = open_url_fn

        self.setObjectName("history_full_page")

        # Prevent worker threads from being garbage collected
        self._workers = []

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header ─────────────────────────────
        header_bar = QWidget()
        header_bar.setObjectName("history_page_header")

        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(40, 20, 40, 16)

        title = QLabel("History")
        title.setObjectName("history_page_title")

        clear_btn = QPushButton("Clear all history")
        clear_btn.setObjectName("history_page_clear_btn")
        clear_btn.clicked.connect(self._clear_all)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(clear_btn)

        root.addWidget(header_bar)

        # ── Loader ─────────────────────────────
        self.loader = QLabel("Loading History...")
        self.loader.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.loader.setObjectName("history_loader")
        
        root.addWidget(self.loader, 1)

        # ── Scroll area ─────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setObjectName("history_page_scroll")

        self._list_widget = QWidget()
        self._list_widget.setObjectName("history_page_list")

        self._list_layout = QVBoxLayout(self._list_widget)
        self._list_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._list_layout.setContentsMargins(40, 0, 40, 40)
        self._list_layout.setSpacing(0)

        scroll.setWidget(self._list_widget)
        root.addWidget(scroll)

        self._populate()

    # ─────────────────────────────────────────
    # Populate history list
    # ─────────────────────────────────────────
    def _populate(self):
        self.loader.show()
        self._list_widget.hide()

        QApplication.processEvents()

        entries = history_handler.load_all()
        self._clear_layout()

        if not entries:
            empty = QLabel("Your browsing history will appear here.")
            empty.setObjectName("history_page_empty")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
        else:
            current_day = None

            for entry in entries:
                url = entry.get("url", "")
                title = entry.get("title", url)
                ts = entry.get("timestamp", "")

                try:
                    dt = datetime.fromisoformat(ts)
                    day_str = dt.strftime("%A, %d %B %Y")
                    time_str = dt.strftime("%H:%M")
                except Exception:
                    day_str = "Unknown date"
                    time_str = ""

                if day_str != current_day:
                    current_day = day_str
                    divider = QLabel(day_str)
                    divider.setObjectName("history_page_day_divider")
                    self._list_layout.addWidget(divider)

                self._add_entry_row(url, title, ts, time_str)

        self.loader.hide()
        self._list_widget.show()

    def _add_entry_row(self, url, title, ts, time_str):
        row = QWidget()
        row.setObjectName("history_page_row")

        row_layout = QHBoxLayout(row)
        row_layout.setContentsMargins(12, 0, 12, 0)
        row_layout.setSpacing(10)

        favicon_btn = QPushButton()
        favicon_btn.setObjectName("history_page_favicon")
        favicon_btn.setFixedSize(28, 28)
        favicon_btn.setText("🌐")
        favicon_btn.setToolTip(url)
        favicon_btn.clicked.connect(lambda _, u=url: self.open_url_fn(u))

        title_btn = QPushButton(title)
        title_btn.setObjectName("history_page_title_btn")
        title_btn.setToolTip(url)
        title_btn.clicked.connect(lambda _, u=url: self.open_url_fn(u))

        url_label = QLabel(url if len(url) < 72 else url[:70] + "…")
        url_label.setObjectName("history_page_url_label")

        time_label = QLabel(time_str)
        time_label.setObjectName("history_page_time_label")
        time_label.setFixedWidth(40)
        time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        del_btn = QPushButton("✕")
        del_btn.setObjectName("delete_btn")
        del_btn.clicked.connect(lambda _, u=url, t=ts: self._delete_entry(u, t))

        text_col = QWidget()
        text_layout = QVBoxLayout(text_col)
        text_layout.setContentsMargins(0, 6, 0, 6)
        text_layout.setSpacing(1)
        text_layout.addWidget(title_btn)
        text_layout.addWidget(url_label)

        row_layout.addWidget(favicon_btn)
        row_layout.addWidget(text_col, 1)
        row_layout.addWidget(time_label)
        row_layout.addWidget(del_btn)

        self._list_layout.addWidget(row)

        self._load_favicon_async(url, favicon_btn)

    def _load_favicon_async(self, url, button):
        domain = urlparse(url).netloc

        if domain in favicon_cache:
            button.setIcon(favicon_cache[domain])
            button.setText("")
            return

        worker = FaviconWorker(url)
        self._workers.append(worker)

        def on_done(u, icon):
            if sip.isdeleted(button):
                return

            favicon_cache[domain] = icon

            try:
                button.setIcon(icon)
                button.setText("")
            except RuntimeError:
                return

            if worker in self._workers:
                self._workers.remove(worker)

        worker.finished.connect(on_done)
        worker.start()

    def _clear_layout(self):
        for worker in self._workers:
            worker.quit()
            worker.wait()

        self._workers.clear()

        while self._list_layout.count():
            item = self._list_layout.takeAt(0)
            w = item.widget()
            if w:
                w.deleteLater()

    def _delete_entry(self, url: str, timestamp: str):
        history_handler.delete_entry(url, timestamp)
        self._populate()

    def _clear_all(self):
        history_handler.clear_all()
        self._populate()

    def refresh(self):
        self._populate()