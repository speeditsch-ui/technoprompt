"""Kontextregeln, Normalisierung, Clamping."""
from __future__ import annotations

from .schema import Intent, Slots


def normalize_intent(intent: Intent) -> Intent:
    """Normalisiert Slots (Typen, Grenzen) und Intent-Name."""
    name = str(intent.intent).strip().upper()
    if name not in {
        "SET_ENERGY", "SET_DARKNESS", "SET_HATS", "SET_BPM", "KICK_ON",
        "BREAK", "DROP", "UNDO", "SAVE", "RESET", "PROFILE_SET", "MACRO_RUN",
        "SCHEDULE", "HOLD", "RATE", "UNKNOWN",
    }:
        name = "UNKNOWN"

    slots = intent.slots_dict()
    out: dict = {}

    if name == "SET_ENERGY":
        if "value" in slots:
            out["value"] = clamp(float(slots["value"]), 0.0, 1.0)
        if "delta" in slots:
            out["delta"] = clamp(float(slots["delta"]), -1.0, 1.0)
    elif name == "SET_DARKNESS":
        if "value" in slots:
            out["value"] = clamp(float(slots["value"]), 0.0, 1.0)
        if "delta" in slots:
            out["delta"] = clamp(float(slots["delta"]), -1.0, 1.0)
    elif name == "SET_HATS":
        if "value" in slots:
            out["value"] = clamp(float(slots["value"]), 0.0, 1.0)
        if "delta" in slots:
            out["delta"] = clamp(float(slots["delta"]), -1.0, 1.0)
    elif name == "SET_BPM":
        if "value" in slots:
            out["value"] = clamp(int(float(slots["value"])), 60, 200)
        if "delta" in slots:
            out["delta"] = clamp(int(float(slots["delta"])), -50, 50)
    elif name == "KICK_ON":
        v = slots.get("value", 1)
        out["value"] = 1 if v in (1, "1", True, "on") else 0
    elif name == "BREAK":
        bars = slots.get("bars", 8)
        if isinstance(bars, str):
            bars = {"4": 4, "8": 8, "16": 16, "32": 32}.get(bars, 8)
        out["bars"] = clamp(int(float(bars)), 4, 32)
        if "mode" in slots:
            out["mode"] = str(slots["mode"])
    elif name == "PROFILE_SET":
        out["name"] = str(slots.get("name", ""))
    elif name == "MACRO_RUN":
        out["name"] = str(slots.get("name", ""))
    elif name == "SCHEDULE":
        out["action"] = str(slots.get("action", ""))
        out["bars"] = clamp(int(float(slots.get("bars", 8))), 1, 64)
    elif name == "RATE":
        r = str(slots.get("rating", "")).lower()
        if r in ("gut", "langweilig", "peak", "fail"):
            out["rating"] = r

    return Intent(intent=name, slots=out, confidence=intent.confidence)


def clamp(v: float | int, lo: float | int, hi: float | int) -> float | int:
    return max(lo, min(hi, v))


def apply_context_rules(
    intent: Intent,
    state: dict,
) -> Intent:
    """
    Kontextregeln: z.B. BREAK wenn kick schon aus -> anderes Mapping.
    State: kick_on, bpm, energy, darkness, hats, profile, ...
    """
    name = intent.intent
    slots = intent.slots_dict()

    if name == "BREAK" and state.get("kick_on") == 0:
        # Alternative: bass filter / hat reduction statt klassischer Break
        # Vereinfacht: Slots anpassen (mode = "filter")
        slots = {**slots, "mode": slots.get("mode") or "filter"}

    return Intent(intent=name, slots=slots, confidence=intent.confidence)
