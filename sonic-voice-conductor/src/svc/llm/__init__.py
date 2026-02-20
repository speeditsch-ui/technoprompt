"""Ollama Client für LLM und Embeddings."""
from .ollama_client import OllamaClient
from .prompts import INTENT_SYSTEM_PROMPT, INTENT_USER_TEMPLATE

__all__ = ["OllamaClient", "INTENT_SYSTEM_PROMPT", "INTENT_USER_TEMPLATE"]
