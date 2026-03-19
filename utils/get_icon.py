import requests
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QByteArray
from PyQt5.QtGui import QPixmap

def get_icon(url):
    try:
        domain = url.split("//")[-1].split("/")[0]
        icon_url = f"https://www.google.com/s2/favicons?domain={domain}&sz=64"

        response = requests.get(icon_url)
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(response.content))

        return QIcon(pixmap)

    except:
        return QIcon()  # fallback empty icon