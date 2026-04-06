from PyQt6.QtCore import QThread, pyqtSignal
from utils.get_favicon import get_favicon_from_url

favicon_cache = {}

class FaviconWorker(QThread):
    finished = pyqtSignal(str, object)  # url, icon

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        icon = get_favicon_from_url(self.url)
        self.finished.emit(self.url, icon)