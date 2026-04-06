from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QScrollArea, QSizePolicy, QFrame
)
from PyQt6.QtCore import Qt, QUrl, QSize, QTimer, QTime, QDate
from PyQt6.QtGui import QFont

from utils.get_favicon import get_favicon_from_url
from utils.json_handler import read_file


class BookmarkTile(QWidget):
    """A single square bookmark tile: favicon on top, title below."""

    def __init__(self, title: str, url: str, open_fn):
        super().__init__()
        self.setObjectName("bm_tile")
        self.setFixedSize(88, 88)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 12, 0, 8)
        layout.setSpacing(6)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        # Favicon button (acts as the click target)
        icon_btn = QPushButton()
        icon_btn.setObjectName("bm_tile_icon")
        icon_btn.setFixedSize(36, 36)
        icon_btn.setIcon(get_favicon_from_url(url))
        icon_btn.setIconSize(QSize(20, 20))
        icon_btn.clicked.connect(lambda: open_fn(url))

        # Title label — two lines max, centered
        label = QLabel(title[:18])
        label.setObjectName("bm_tile_label")
        label.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        label.setWordWrap(True)

        layout.addWidget(icon_btn, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addWidget(label)

        # Make the whole tile clickable
        self.mousePressEvent = lambda e: open_fn(url)


class WeatherCard(QWidget):
    """Static sample weather card — replace with a live API later."""

    SAMPLE = {
        "city":    "Bengaluru",
        "temp":    "24°C",
        "feels":   "Feels like 22°C",
        "desc":    "Partly Cloudy",
        "icon":    "⛅",
        "high":    "28°C",
        "low":     "18°C",
        "humidity":"62%",
        "wind":    "14 km/h",
    }

    def __init__(self):
        super().__init__()
        self.setObjectName("weather_card")
        self.setFixedWidth(300)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(0)

        # Top row: city + icon
        top = QHBoxLayout()
        city = QLabel(self.SAMPLE["city"])
        city.setObjectName("weather_city")
        icon = QLabel(self.SAMPLE["icon"])
        icon.setObjectName("weather_icon")
        top.addWidget(city)
        top.addStretch()
        top.addWidget(icon)
        layout.addLayout(top)

        # Temperature
        temp = QLabel(self.SAMPLE["temp"])
        temp.setObjectName("weather_temp")
        layout.addWidget(temp)

        # Description + feels like
        desc = QLabel(f"{self.SAMPLE['desc']}  ·  {self.SAMPLE['feels']}")
        desc.setObjectName("weather_desc")
        layout.addWidget(desc)

        layout.addSpacing(14)

        # Bottom row: H/L, humidity, wind
        divider = QFrame()
        divider.setObjectName("weather_divider")
        divider.setFrameShape(QFrame.Shape.HLine)
        layout.addWidget(divider)

        layout.addSpacing(10)

        stats = QHBoxLayout()
        stats.setSpacing(0)

        for label_text, value_text in [
            ("HIGH", self.SAMPLE["high"]),
            ("LOW",  self.SAMPLE["low"]),
            ("HUMIDITY", self.SAMPLE["humidity"]),
            ("WIND", self.SAMPLE["wind"]),
        ]:
            col = QVBoxLayout()
            col.setSpacing(2)
            val = QLabel(value_text)
            val.setObjectName("weather_stat_value")
            val.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            lbl = QLabel(label_text)
            lbl.setObjectName("weather_stat_label")
            lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            col.addWidget(val)
            col.addWidget(lbl)
            stats.addLayout(col)
            if label_text != "WIND":
                stats.addStretch()

        layout.addLayout(stats)


class HomePage(QWidget):
    """
    New-tab home page. Pass `open_url_fn` so bookmark tiles can
    navigate without importing Tabs.
    """

    def __init__(self, open_url_fn):
        super().__init__()
        self.open_url_fn = open_url_fn
        self.setObjectName("home_page")

        # Outer scroll area so content is reachable on small windows
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setObjectName("home_scroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        container = QWidget()
        container.setObjectName("home_container")
        self._root = QVBoxLayout(container)
        self._root.setContentsMargins(80, 60, 80, 60)
        self._root.setSpacing(0)
        self._root.setAlignment(Qt.AlignmentFlag.AlignTop)

        scroll.setWidget(container)
        outer.addWidget(scroll)

        self._build()

    def _build(self):
        # ── Greeting + clock row ──────────────────────────
        top_row = QHBoxLayout()
        top_row.setAlignment(Qt.AlignmentFlag.AlignTop)

        # Left: greeting + date
        greeting_col = QVBoxLayout()
        greeting_col.setSpacing(4)

        self._greeting = QLabel()
        self._greeting.setObjectName("home_greeting")

        self._date_label = QLabel()
        self._date_label.setObjectName("home_date")

        greeting_col.addWidget(self._greeting)
        greeting_col.addWidget(self._date_label)

        # Right: clock
        self._clock = QLabel()
        self._clock.setObjectName("home_clock")
        self._clock.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        top_row.addLayout(greeting_col, 1)
        top_row.addWidget(self._clock)

        self._root.addLayout(top_row)
        self._root.addSpacing(40)

        # ── Weather + bookmarks row ───────────────────────
        mid_row = QHBoxLayout()
        mid_row.setAlignment(Qt.AlignmentFlag.AlignTop)
        mid_row.setSpacing(40)

        self._weather = WeatherCard()
        mid_row.addWidget(self._weather, 0, Qt.AlignmentFlag.AlignTop)

        # Bookmarks section
        bm_col = QVBoxLayout()
        bm_col.setSpacing(14)

        bm_header = QLabel("BOOKMARKS")
        bm_header.setObjectName("home_section_label")
        bm_col.addWidget(bm_header)

        self._grid_widget = QWidget()
        self._grid_widget.setObjectName("home_bm_grid")
        self._grid = QGridLayout(self._grid_widget)
        self._grid.setSpacing(10)
        self._grid.setContentsMargins(0, 0, 0, 0)

        bm_col.addWidget(self._grid_widget)
        bm_col.addStretch()

        mid_row.addLayout(bm_col, 1)

        self._root.addLayout(mid_row)

        # ── Populate dynamic parts ────────────────────────
        self._update_time()
        self._populate_bookmarks()

        # Tick every second
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._update_time)
        self._timer.start(1000)

    # ── Clock / greeting ──────────────────────────────────
    def _update_time(self):
        now  = QTime.currentTime()
        date = QDate.currentDate()

        hour = now.hour()
        if hour < 12:
            greeting = "Good morning."
        elif hour < 17:
            greeting = "Good afternoon."
        else:
            greeting = "Good evening."

        self._greeting.setText(f"Hi there — {greeting}")
        self._date_label.setText(date.toString("dddd, d MMMM yyyy"))
        self._clock.setText(now.toString("hh:mm:ss"))

    # ── Bookmarks grid ────────────────────────────────────
    def _populate_bookmarks(self):
        # Clear existing tiles
        while self._grid.count():
            item = self._grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        try:
            bookmarks = read_file("config/bookmarks.json")
        except Exception:
            bookmarks = []

        if not bookmarks:
            empty = QLabel("No bookmarks yet. Star a page to add one.")
            empty.setObjectName("home_empty_label")
            self._grid.addWidget(empty, 0, 0)
            return

        COLS = 6
        for i, bm in enumerate(bookmarks):
            tile = BookmarkTile(bm["title"], bm["path"], self.open_url_fn)
            self._grid.addWidget(tile, i // COLS, i % COLS)

    def refresh(self):
        """Re-read bookmarks from disk — call when tab gains focus."""
        self._populate_bookmarks()