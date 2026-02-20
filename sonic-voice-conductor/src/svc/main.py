"""CLI Entry: sonic-voice-conductor / svc."""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure src is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from svc.config import Config, get_data_dir
from svc.audio import Recorder, resolve_device, list_devices
from svc.stt import WhisperSTT
from svc.llm import OllamaClient
from svc.llm.prompts import INTENT_SYSTEM_PROMPT, build_intent_prompt
from svc.intent import IntentParser
from svc.intent.knn_store import KNNStore
from svc.intent.rules import apply_context_rules
from svc.osc.client import OSCClient
from svc.osc.protocol import intent_to_osc_messages
from svc.memory.db import init_db, get_db_path
from svc.memory.events import log_event
from svc.memory.ratings import add_rating
from svc.profiles import get_profile
from svc.profiles.profiles import clamp_to_profile
from svc.macros.registry import get_macro
from svc.macros.engine import MacroEngine
from svc.scheduler import Scheduler


# Globals für Controller-State
_state: dict = {}
_last_phrase = ""
_last_intent = ""
_last_confidence = 0.0
_last_method = ""
_scheduled: list[str] = []
_active_macro = ""
_message = ""
_waiting_confirm = False
_pending_suggestion: tuple | None = None  # (intent, phrase)
_correction_mode = False
_osc_client = None
_db_path = None
_macro_engine = None
_scheduler = None


def apply_intent(intent, phrase: str, method: str) -> None:
    """Wendet Intent an: OSC senden, State updaten."""
    global _state, _active_macro
    msgs = intent_to_osc_messages(intent, _state)
    osc = _osc_client
    # SAVE vor größeren Änderungen für UNDO
    if intent.intent in ("BREAK", "DROP", "SET_BPM", "RESET"):
        osc.send("save", 1)
    if intent.intent == "RATE":
        r = intent.slots_dict().get("rating")
        if r:
            add_rating(_db_path, r, macro_name=_active_macro or None)
    elif intent.intent == "PROFILE_SET":
        prof = get_profile(intent.slots_dict().get("name", ""))
        if prof:
            _state["profile"] = prof.name
            for k, v in prof.defaults.items():
                _state[k] = v
                osc.send(k, v)
    elif intent.intent == "MACRO_RUN":
        name = intent.slots_dict().get("name", "")
        if _macro_engine and _macro_engine.run(name):
            _active_macro = name
    for k, v in msgs:
        osc.send(k, v)
        if k in ("energy", "darkness", "hats", "bpm", "kick_on", "profile"):
            _state[k] = v
    if msgs:
        log_event(_db_path, intent.intent, phrase, method, intent.slots_dict(), json.dumps(msgs))


def main() -> int:
    global _state, _last_phrase, _last_intent, _last_confidence, _last_method
    global _scheduled, _active_macro, _message, _waiting_confirm, _pending_suggestion, _correction_mode
    global _osc_client, _db_path, _macro_engine, _scheduler

    config = Config.load()
    data_dir = get_data_dir(config)
    _db_path = get_db_path(data_dir)
    init_db(data_dir)

    # Init Komponenten
    ollama = OllamaClient(
        base_url=config.ollama_base_url,
        llm_model=config.llm_model,
        embed_model=config.embed_model,
    )
    knn_store = KNNStore(_db_path, ollama.embed)
    parser = IntentParser(
        knn_store=knn_store,
        llm_generate=ollama.generate,
        extract_json=OllamaClient.extract_json,
        knn_auto=config.knn_auto,
        knn_suggest=config.knn_suggest,
        llm_auto_conf=config.llm_auto_conf,
    )
    _osc_client = OSCClient(host=config.osc_host, port=config.osc_port)
    recorder = Recorder(
        sample_rate=config.sample_rate,
        record_seconds=config.record_seconds,
        device=resolve_device(config.mic_device),
    )
    stt = WhisperSTT(model_size=config.whisper_model_size, language=config.language)

    # State
    _state = {
        "energy": 0.5,
        "darkness": 0.5,
        "hats": 0.5,
        "bpm": 128,
        "kick_on": 1,
        "profile": "peak",
    }
    _scheduler = Scheduler(bpm=_state["bpm"], max_big_per_8_bars=config.max_big_changes_per_8_bars)
    _macro_engine = MacroEngine(
        state=_state,
        send_osc=lambda k, v: _osc_client.send(k, v),
        get_current_bar=_scheduler.get_current_bar,
    )

    def send_osc_param(k: str, v: float) -> None:
        _osc_client.send(k, v)
        _state[k] = v

    # Background-Tick für Scheduler + Makro (wird in TUI-Loop aufgerufen)
    import threading
    _tick_stop = threading.Event()
    def tick_loop():
        while not _tick_stop.wait(0.15):
            _scheduler.set_bpm(_state.get("bpm", 128))
            _scheduler.tick()
            _macro_engine.tick()
    _tick_thread = threading.Thread(target=tick_loop, daemon=True)
    _tick_thread.start()

    def do_record_and_process() -> None:
        global _last_phrase, _last_intent, _last_confidence, _last_method, _message, _waiting_confirm
        global _pending_suggestion, _correction_mode
        if _correction_mode:
            _message = "Sag den richtigen Befehl"
        else:
            _message = ""
        _waiting_confirm = False
        audio = recorder.record()
        phrase = stt.transcribe(audio)
        if not phrase:
            _message = "Nichts erkannt."
            return

        if _correction_mode:
            # Korrektur: neue Phrase als richtigen Intent parsen, anwenden, lernen
            intent, method = parser.parse(phrase)
            if intent.intent != "UNKNOWN":
                apply_intent(intent, phrase, "corrected")
                parser.learn_correction(_pending_suggestion[1], intent.intent, intent.slots_dict())
            _correction_mode = False
            _pending_suggestion = None
            _last_phrase, _last_intent = phrase, intent.intent
            _last_confidence, _last_method = intent.confidence, "corrected"
            return

        intent, method = parser.parse(phrase)
        intent = apply_context_rules(intent, _state)

        if method in ("knn_auto", "llm_auto"):
            apply_intent(intent, phrase, method)
            _last_phrase, _last_intent = phrase, intent.intent
            _last_confidence, _last_method = intent.confidence, method
            return

        if method in ("knn_suggest", "llm_suggest"):
            _pending_suggestion = (intent, phrase)
            _message = "Unsicher. Sag: ja / nein / abbrechen"
            _waiting_confirm = True
            _last_phrase, _last_intent = phrase, intent.intent
            _last_confidence, _last_method = intent.confidence, method + "_pending"
            return

        _message = "Nicht erkannt."
        _last_phrase, _last_intent = phrase, "UNKNOWN"
        _last_confidence, _last_method = 0.0, "unknown"

    def do_confirm(answer: str) -> None:
        """Ja/Nein/Abbrechen nach Bestätigungsaufnahme."""
        global _pending_suggestion, _correction_mode, _message, _waiting_confirm
        if not _waiting_confirm or not _pending_suggestion:
            return
        intent, phrase = _pending_suggestion
        a = answer.strip().lower()
        if a in ("ja", "yes", "j", "y", "bestätigen"):
            apply_intent(intent, phrase, "confirmed")
            _last_method = "confirmed"
            _pending_suggestion = None
            _waiting_confirm = False
            _message = ""
        elif a in ("nein", "no", "n"):
            _correction_mode = True
            _message = "Sag den richtigen Befehl"
            _waiting_confirm = False
        elif a in ("abbrechen", "cancel", "abbruch"):
            _pending_suggestion = None
            _waiting_confirm = False
            _message = ""
            _correction_mode = False

    def process_phrase_direct(phrase: str) -> None:
        """Verarbeitet Phrase direkt (für Confirm-Aufnahme)."""
        do_confirm(phrase)

    def on_enter() -> None:
        if _waiting_confirm:
            # Kurze Bestätigungsaufnahme
            audio = recorder.record()
            phrase = stt.transcribe(audio)
            process_phrase_direct(phrase)
        else:
            do_record_and_process()

    def get_state() -> dict:
        return dict(_state)

    def get_last_result() -> tuple:
        return _last_phrase, _last_intent, _last_confidence, _last_method

    def get_scheduled() -> list:
        return list(_scheduled)

    def get_active_macro() -> str:
        return _active_macro or ""

    def get_message() -> str:
        return _message or ""

    def get_waiting_confirm() -> bool:
        return _waiting_confirm

    # TUI starten
    from svc.ui.tui import run_tui
    try:
        run_tui(
        on_enter=on_enter,
        on_key=lambda _: None,
        get_state=get_state,
        get_last_result=get_last_result,
        get_scheduled=get_scheduled,
        get_active_macro=get_active_macro,
        get_message=get_message,
        get_waiting_confirm=get_waiting_confirm,
        list_devices=list_devices,
    )
    finally:
        _tick_stop.set()
    return 0


if __name__ == "__main__":
    sys.exit(main())
