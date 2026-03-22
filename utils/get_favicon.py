import requests
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QIcon, QPixmap

def get_favicon_from_url(url: str, size: int = 16) -> QIcon:
    try:
        domain = QUrl(url).host()
        icon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz={size}"

        response = requests.get(icon_url, timeout=2)

        if response.status_code == 200:
            pixmap = QPixmap()
            pixmap.loadFromData(response.content)
            return QIcon(pixmap)

    except Exception:
        pass

    return QIcon()  # fallback empty icon