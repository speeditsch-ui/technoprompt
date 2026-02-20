"""Ratings: gut, langweilig, peak, fail. Simple Heuristik für Präferenzen."""
import sqlite3
from pathlib import Path


def add_rating(db_path: Path, rating: str, macro_name: str | None = None, params_json: str | None = None) -> None:
    """Speichert ein Rating (gut, langweilig, peak, fail)."""
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            "INSERT INTO ratings (rating, macro_name, params_json) VALUES (?, ?, ?)",
            (rating, macro_name, params_json),
        )
        conn.commit()


def get_preferred_macros(db_path: Path, limit: int = 5) -> list[str]:
    """Makros die häufig als gut/peak markiert wurden."""
    with sqlite3.connect(db_path) as conn:
        rows = conn.execute("""
            SELECT macro_name, COUNT(*) as c
            FROM ratings
            WHERE rating IN ('gut', 'peak') AND macro_name IS NOT NULL
            GROUP BY macro_name
            ORDER BY c DESC
            LIMIT ?
        """, (limit,)).fetchall()
    return [r[0] for r in rows if r[0]]
