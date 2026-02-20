"""Tests für kNN-Matching (mit Mock-Embeddings)."""
import tempfile
from pathlib import Path

import pytest
from svc.intent.knn_store import KNNStore


def _mock_embed(text: str) -> list[float]:
    """Deterministischer Mock: gleicher Text = gleicher Vektor."""
    h = hash(text) % 10000
    return [float((h + i) % 100) / 100 for i in range(128)]


def test_add_and_search():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "test.db"
        store = KNNStore(db, _mock_embed)
        store.add("energie hoch", "SET_ENERGY", {"delta": 0.2})
        store.add("bpm schneller", "SET_BPM", {"delta": 5})
        results = store.search("energie mehr", k=1)
        assert len(results) >= 1
        sim, intent, phrase, slots = results[0]
        assert intent in ("SET_ENERGY", "SET_BPM")
        assert 0 <= sim <= 1


def test_empty_search():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "test.db"
        store = KNNStore(db, _mock_embed)
        results = store.search("irgendwas", k=3)
        assert results == []
