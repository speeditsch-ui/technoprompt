"""SQLite Examples + Embeddings + kNN Similarity."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Callable

import numpy as np


class KNNStore:
    """Speichert Voice-Examples mit Embeddings, kNN-Matching."""

    def __init__(self, db_path: Path, embed_fn: Callable[[str], list[float]]):
        self.db_path = db_path
        self.embed_fn = embed_fn
        self._init_db()

    def _init_db(self) -> None:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
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
            conn.execute("CREATE INDEX IF NOT EXISTS ix_examples_intent ON examples(intent)")
            conn.commit()

    def add(self, phrase: str, intent: str, slots: dict) -> None:
        """Neues Example hinzufügen (mit Embedding)."""
        import json
        emb = self.embed_fn(phrase)
        arr = np.array(emb, dtype=np.float32)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO examples (phrase, intent, slots_json, embedding) VALUES (?, ?, ?, ?)",
                (phrase, intent, json.dumps(slots), arr.tobytes()),
            )
            conn.commit()

    def search(self, phrase: str, k: int = 3) -> list[tuple[float, str, str, dict]]:
        """
        kNN-Suche. Returns Liste von (similarity, intent, phrase, slots).
        Cosine similarity, höher = ähnlicher.
        """
        import json
        q_emb = np.array(self.embed_fn(phrase), dtype=np.float32)
        q_norm = np.linalg.norm(q_emb)
        if q_norm == 0:
            return []

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT phrase, intent, slots_json, embedding FROM examples").fetchall()

        results = []
        for phrase_row, intent, slots_json, emb_blob in rows:
            if not emb_blob:
                continue
            emb = np.frombuffer(emb_blob, dtype=np.float32)
            sim = float(np.dot(q_emb, emb) / (q_norm * np.linalg.norm(emb) + 1e-9))
            slots = json.loads(slots_json) if slots_json else {}
            results.append((sim, intent, phrase_row, slots))

        results.sort(key=lambda x: -x[0])
        return results[:k]
