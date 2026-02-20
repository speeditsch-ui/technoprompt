"""Ollama Client: Generate + Embeddings."""
from __future__ import annotations

import json
import os
import re
from typing import Any

import ollama


class OllamaClient:
    """Lokaler Ollama-Client für LLM und Embeddings."""

    def __init__(self, base_url: str = "http://127.0.0.1:11434", llm_model: str = "llama3.2", embed_model: str = "nomic-embed-text"):
        self.base_url = base_url
        self.llm_model = llm_model
        self.embed_model = embed_model
        os.environ.setdefault("OLLAMA_HOST", base_url)

    def generate(self, system: str, user: str) -> str:
        """LLM-Generierung. Liefert Rohtext."""
        resp = ollama.chat(
            model=self.llm_model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return (resp.get("message") or {}).get("content", "")

    def embed(self, text: str) -> list[float]:
        """Embedding für einen Text. Liefert Vektor."""
        resp = ollama.embeddings(model=self.embed_model, prompt=text)
        return resp.get("embedding", [])

    @staticmethod
    def extract_json(text: str) -> dict[str, Any] | None:
        """Extrahiert erstes {...} aus dem Text (robust)."""
        match = re.search(r"\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        return None
