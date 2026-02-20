"""SQLite Init und Migrationen."""
from pathlib import Path


def get_db_path(data_dir: Path) -> Path:
    return data_dir / "svc.db"


def init_db(data_dir: Path) -> None:
    """Erstellt DB und Tabellen."""
    db = get_db_path(data_dir)
    db.parent.mkdir(parents=True, exist_ok=True)
    import sqlite3
    with sqlite3.connect(db) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS examples (
                id INTEGER PRIMARY KEY,
                phrase TEXT NOT NULL,
                intent TEXT NOT NULL,
                slots_json TEXT,
                embedding BLOB,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                ts TEXT DEFAULT CURRENT_TIMESTAMP,
                intent TEXT,
                phrase TEXT,
                method TEXT,
                slots_json TEXT,
                osc_sent TEXT
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS ratings (
                id INTEGER PRIMARY KEY,
                ts TEXT DEFAULT CURRENT_TIMESTAMP,
                rating TEXT,
                macro_name TEXT,
                params_json TEXT,
                segment_start INTEGER,
                segment_end INTEGER
            )
        """)
        conn.commit()
