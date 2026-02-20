"""Event-Logging für Intent-Ausführungen."""
import json
import sqlite3
from pathlib import Path


def log_event(db_path: Path, intent: str, phrase: str, method: str, slots: dict, osc_sent: str) -> None:
    """Speichert ein Event in der DB."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO events (intent, phrase, method, slots_json, osc_sent) VALUES (?, ?, ?, ?, ?)",
            (intent, phrase, method, json.dumps(slots), osc_sent),
        )
        conn.commit()
