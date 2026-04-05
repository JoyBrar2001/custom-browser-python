import os
from datetime import datetime
from typing import List

from utils.json_handler import read_file, write_file

HISTORY_PATH = "config/history.json"
MAX_ENTRIES  = 500

def _ensure_file():
    """Create the history file if it doesn't exist yet."""
    if not os.path.exists(HISTORY_PATH):
        os.makedirs(os.path.dirname(HISTORY_PATH), exist_ok=True)
        write_file.__module__
        with open(HISTORY_PATH, "w") as f:
            f.write("[]")

def record(title: str, url: str):
    if not url or url in ("about:blank", "") or url.startswith("data:"):
        return
    
    _ensure_file()
    
    now = datetime.now()
    ts = now.strftime("%Y-%m-%dT%H:%M:%S")
    minute = now.strftime("%Y-%m-%dT%H:%M")
    
    def update(entries):
        filtered = [e for e in entries if not (e["url"] == url and e["timestamp"].startswith(minute))]
        filtered.insert(0, {
            "title": title or url,
            "url": url,
            "timestamp": ts
        })
        return filtered[:MAX_ENTRIES]

    write_file(HISTORY_PATH, update_fn=update)
    

def load_all() -> List:
    _ensure_file()
    return read_file(HISTORY_PATH)

def clear_all():
    _ensure_file()
    write_file(HISTORY_PATH, data=[])
    
def delete_entry(url: str, timestamp: str):
    _ensure_file()
    write_file(HISTORY_PATH, update_fn=lambda entries: [
        e for e in entries
        if not (e["url"] == url and e["timestamp"] == timestamp)
    ])