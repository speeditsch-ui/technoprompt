"""Mikrofon-Aufnahme mit sounddevice."""
import numpy as np
import sounddevice as sd


class Recorder:
    """Push-to-talk Aufnahme: record() liefert Audio-Array."""

    def __init__(
        self,
        sample_rate: int = 16000,
        record_seconds: float = 3.0,
        device: int | None = None,
    ):
        self.sample_rate = sample_rate
        self.record_seconds = record_seconds
        self.device = device

    def record(self) -> np.ndarray:
        """Aufnahme durchführen. Mono, float32, normalisiert -1..1."""
        samples = int(self.sample_rate * self.record_seconds)
        recording = sd.rec(
            frames=samples,
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            device=self.device,
        )
        sd.wait()
        return recording.flatten()
