from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QScrollArea
)
from PyQt6.QtCore import Qt, QUrl, QSize
from datetime import datetime

from utils.get_favicon import get_favicon_from_url
from utils import history_handler


class HistoryPage(QWidget):
    """
    Full-tab history page — rendered inside a browser tab just like
    Chrome's chrome://history. Receives an `open_url_fn` callback so
    clicking an entry loads it in the current tab without importing Tabs.
    """

    def __init__(self, open_url_fn):
        super().__init__()
        self.open_url_fn = open_url_fn  # callable(url: str)

        self.setObjectName("history_full_page")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Header bar ────────────────────────────────────
        header_bar = QWidget()
        header_bar.setObjectName("history_page_header")
        header_layout = QHBoxLayout(header_bar)
        header_layout.setContentsMargins(40, 20, 40, 16)
        header_layout.setSpacing(0)

        title = QLabel("History")
        title.setObjectName("history_page_title")

        clear_btn = QPushButton("Clear all history")
        clear_btn.setObjectName("history_page_clear_btn")
        clear_btn.clicked.connect(self._clear_all)

        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(clear_btn)

        root.addWidget(header_bar)

        # ── Scrollable entry list ─────────────────────────
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

    # ── Build / rebuild the list ───────────────────────────
    def _populate(self):
        self._clear_layout()
        entries = history_handler.load_all()

        if not entries:
            empty = QLabel("Your browsing history will appear here.")
            empty.setObjectName("history_page_empty")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list_layout.addWidget(empty)
            return

        current_day = None

        for entry in entries:
            url   = entry.get("url", "")
            title = entry.get("title", url)
            ts    = entry.get("timestamp", "")

            try:
                dt      = datetime.fromisoformat(ts)
                day_str = dt.strftime("%A, %d %B %Y")   # Monday, 06 April 2025
                time_str = dt.strftime("%H:%M")
            except Exception:
                day_str  = "Unknown date"
                time_str = ""

            # ── Day divider ────────────────────────────────
            if day_str != current_day:
                current_day = day_str
                divider = QLabel(day_str)
                divider.setObjectName("history_page_day_divider")
                self._list_layout.addWidget(divider)

            # ── Entry row ──────────────────────────────────
            row = QWidget()
            row.setObjectName("history_page_row")
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(12, 0, 12, 0)
            row_layout.setSpacing(10)

            # Favicon
            favicon_btn = QPushButton()
            favicon_btn.setObjectName("history_page_favicon")
            favicon_btn.setIcon(get_favicon_from_url(url))
            favicon_btn.setIconSize(QSize(16, 16))
            favicon_btn.setFixedSize(28, 28)
            favicon_btn.setToolTip(url)
            favicon_btn.clicked.connect(lambda _, u=url: self.open_url_fn(u))

            # Title (clickable)
            title_btn = QPushButton(title)
            title_btn.setObjectName("history_page_title_btn")
            title_btn.setToolTip(url)
            title_btn.clicked.connect(lambda _, u=url: self.open_url_fn(u))

            # URL (dimmed, read-only feel)
            url_label = QLabel(url if len(url) < 72 else url[:70] + "…")
            url_label.setObjectName("history_page_url_label")

            # Time
            time_label = QLabel(time_str)
            time_label.setObjectName("history_page_time_label")
            time_label.setFixedWidth(40)
            time_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

            # Delete button
            del_btn = QPushButton("✕")
            del_btn.setObjectName("delete_btn")
            del_btn.clicked.connect(lambda _, u=url, t=ts: self._delete_entry(u, t))

            # Inner text column (title + url stacked)
            text_col = QWidget()
            text_col.setObjectName("history_page_text_col")
            text_col_layout = QVBoxLayout(text_col)
            text_col_layout.setContentsMargins(0, 6, 0, 6)
            text_col_layout.setSpacing(1)
            text_col_layout.addWidget(title_btn)
            text_col_layout.addWidget(url_label)

            row_layout.addWidget(favicon_btn)
            row_layout.addWidget(text_col, 1)
            row_layout.addWidget(time_label)
            row_layout.addWidget(del_btn)

            self._list_layout.addWidget(row)

    def _clear_layout(self):
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
        """Call this to reload entries — e.g. when the tab gets focus."""
        self._populate()