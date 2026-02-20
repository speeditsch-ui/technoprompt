"""Tests für Intent-Normalisierung."""
import pytest
from svc.intent.schema import Intent, Slots
from svc.intent.rules import normalize_intent


def test_set_energy_value_clamp():
    intent = Intent(intent="SET_ENERGY", slots={"value": 1.5}, confidence=0.9)
    out = normalize_intent(intent)
    assert out.slots_dict()["value"] == 1.0


def test_set_energy_delta_clamp():
    intent = Intent(intent="SET_ENERGY", slots={"delta": 0.15}, confidence=0.9)
    out = normalize_intent(intent)
    assert out.slots_dict()["delta"] == 0.15


def test_set_bpm_value():
    intent = Intent(intent="SET_BPM", slots={"value": 140}, confidence=0.9)
    out = normalize_intent(intent)
    assert out.slots_dict()["value"] == 140


def test_kick_on():
    intent = Intent(intent="KICK_ON", slots={"value": 1}, confidence=0.9)
    out = normalize_intent(intent)
    assert out.slots_dict()["value"] == 1


def test_break_bars():
    intent = Intent(intent="BREAK", slots={"bars": 16}, confidence=0.9)
    out = normalize_intent(intent)
    assert out.slots_dict()["bars"] == 16


def test_unknown_intent():
    intent = Intent(intent="FOO", slots={}, confidence=0.5)
    out = normalize_intent(intent)
    assert out.intent == "UNKNOWN"
