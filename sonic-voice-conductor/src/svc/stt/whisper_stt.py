"""faster-whisper Wrapper für Speech-to-Text."""
from __future__ import annotations

import numpy as np
from faster_whisper import Whisper


class WhisperSTT:
    """STT via faster-whisper, lokal."""

    def __init__(self, model_size: str = "base", language: str = "de", device: str = "auto"):
        self.model = Whisper(model_size, device=device)
        self.language = language if language != "auto" else None

    def transcribe(self, audio: np.ndarray) -> str:
        """Transkribiert Audio zu Text. Leer wenn Stille/Nichts erkannt."""
        segments, _ = self.model.transcribe(
            audio,
            language=self.language,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500),
        )
        parts = [s.text.strip() for s in segments if s.text.strip()]
        return " ".join(parts).strip()
