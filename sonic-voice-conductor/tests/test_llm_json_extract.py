"""Tests für LLM JSON-Extraktion."""
import pytest
from svc.llm.ollama_client import OllamaClient


def test_extract_simple():
    text = 'Here is the result: {"intent":"SET_ENERGY","slots":{"delta":0.2},"confidence":0.9}'
    out = OllamaClient.extract_json(text)
    assert out is not None
    assert out["intent"] == "SET_ENERGY"
    assert out["slots"]["delta"] == 0.2
    assert out["confidence"] == 0.9


def test_extract_nested():
    text = 'Ignore this. {"intent":"BREAK","slots":{"bars":8,"mode":"filter"},"confidence":0.8}'
    out = OllamaClient.extract_json(text)
    assert out is not None
    assert out["intent"] == "BREAK"
    assert out["slots"]["bars"] == 8
    assert out["slots"]["mode"] == "filter"


def test_extract_fail():
    text = "No JSON here at all"
    out = OllamaClient.extract_json(text)
    assert out is None


def test_extract_first_brace():
    text = 'A {"a":1} B {"b":2}'
    out = OllamaClient.extract_json(text)
    assert out is not None
    assert "a" in out or "b" in out
