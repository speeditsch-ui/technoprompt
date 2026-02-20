"""OSC Protokoll-Konstanten und Helper."""
from __future__ import annotations

# Sonic Pi empfängt auf /ai: [key, value]
OSC_ADDRESS = "/ai"

OSC_KEYS = (
    "energy", "darkness", "hats", "bpm", "kick_on",
    "save", "undo", "break", "drop", "reset",
    "profile", "macro", "schedule", "hold",
)


def intent_to_osc_messages(intent: "Intent", state: dict) -> list[tuple[str, float | int | str]]:
    """Konvertiert Intent + State zu Liste von (key, value) für OSC."""
    name = intent.intent
    slots = intent.slots_dict() if hasattr(intent, "slots_dict") else (intent.slots or {})

    msgs: list[tuple[str, float | int | str]] = []

    if name == "SET_ENERGY":
        energy = state.get("energy", 0.5)
        if "value" in slots:
            energy = float(slots["value"])
        elif "delta" in slots:
            energy = max(0, min(1, energy + float(slots["delta"])))
        msgs.append(("energy", energy))
    elif name == "SET_DARKNESS":
        dark = state.get("darkness", 0.5)
        if "value" in slots:
            dark = float(slots["value"])
        elif "delta" in slots:
            dark = max(0, min(1, dark + float(slots["delta"])))
        msgs.append(("darkness", dark))
    elif name == "SET_HATS":
        hats = state.get("hats", 0.5)
        if "value" in slots:
            hats = float(slots["value"])
        elif "delta" in slots:
            hats = max(0, min(1, hats + float(slots["delta"])))
        msgs.append(("hats", hats))
    elif name == "SET_BPM":
        bpm = state.get("bpm", 128)
        if "value" in slots:
            bpm = int(slots["value"])
        elif "delta" in slots:
            bpm = int(bpm + slots["delta"])
        bpm = max(60, min(200, bpm))
        msgs.append(("bpm", bpm))
    elif name == "KICK_ON":
        msgs.append(("kick_on", int(slots.get("value", 1))))
    elif name == "BREAK":
        msgs.append(("break", slots.get("bars", 8)))
        if slots.get("mode"):
            msgs.append(("break_mode", slots["mode"]))
    elif name == "DROP":
        msgs.append(("drop", 1))
    elif name == "UNDO":
        msgs.append(("undo", 1))
    elif name == "SAVE":
        msgs.append(("save", 1))
    elif name == "RESET":
        msgs.append(("reset", 1))
    elif name == "PROFILE_SET":
        if slots.get("name"):
            msgs.append(("profile", slots["name"]))
    elif name == "MACRO_RUN":
        if slots.get("name"):
            msgs.append(("macro", slots["name"]))
    elif name == "SCHEDULE":
        if slots.get("action") and "bars" in slots:
            msgs.append(("schedule", f"{slots['action']}:{slots['bars']}"))
    elif name == "HOLD":
        msgs.append(("hold", 1))

    return msgs
