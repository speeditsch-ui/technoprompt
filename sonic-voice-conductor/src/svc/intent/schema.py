"""Intent + Slots Pydantic-Modelle."""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class Slots(BaseModel):
    """Slots für Intents. Flexibel für verschiedene Keys."""
    model_config = {"extra": "allow"}

    value: float | None = None
    delta: float | None = None
    bars: int | None = None
    mode: str | None = None
    name: str | None = None
    action: str | None = None


class Intent(BaseModel):
    """Erkannter Intent mit Slots und Confidence."""
    intent: str
    slots: Slots | dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.0

    def slots_dict(self) -> dict[str, Any]:
        s = self.slots
        if isinstance(s, Slots):
            return s.model_dump(exclude_none=True)
        return dict(s) if s else {}
