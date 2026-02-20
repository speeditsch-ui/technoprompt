"""Bar-basierter Scheduler: Taktbasis, Queue, Tick-Loop."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Callable, Any


@dataclass
class ScheduledAction:
    due_bar: int
    action: Callable[[], None]
    cancelled: bool = False


class Scheduler:
    """Scheduler mit bar-basierter Zeit. BPM -> seconds_per_beat; bar = 4 beats."""

    def __init__(self, bpm: float = 128, max_big_per_8_bars: int = 1):
        self.bpm = bpm
        self.max_big_per_8_bars = max_big_per_8_bars
        self._current_bar: float = 0.0
        self._queue: list[ScheduledAction] = []
        self._last_big_action_bar: float = -100
        self._start_time = time.monotonic()

    @property
    def seconds_per_beat(self) -> float:
        return 60.0 / self.bpm if self.bpm > 0 else 0.5

    @property
    def seconds_per_bar(self) -> float:
        return self.seconds_per_beat * 4

    def set_bpm(self, bpm: float) -> None:
        self.bpm = max(60, min(200, bpm))

    def get_current_bar(self) -> int:
        """Aktuelle Bar (ganzzahlig)."""
        return int(self._current_bar)

    def get_current_bar_float(self) -> float:
        elapsed = time.monotonic() - self._start_time
        return elapsed / self.seconds_per_bar

    def tick(self) -> None:
        """Zeit vorrücken und fällige Aktionen ausführen."""
        self._current_bar = self.get_current_bar_float()
        due = [a for a in self._queue if a.due_bar <= self.get_current_bar() and not a.cancelled]
        for a in due:
            a.action()
        self._queue = [a for a in self._queue if a not in due]

    def schedule(self, bars: int, action: Callable[[], None]) -> ScheduledAction:
        """Planiert Aktion in `bars` Takten."""
        due_bar = self.get_current_bar() + bars
        sa = ScheduledAction(due_bar=due_bar, action=action)
        self._queue.append(sa)
        return sa

    def schedule_big_action(self, bars: int, action: Callable[[], None]) -> ScheduledAction | None:
        """Planiert große Aktion mit Anti-KI-Limit (max 1 pro 8 Takte)."""
        now = self.get_current_bar()
        if now - self._last_big_action_bar < 8:
            return None
        sa = self.schedule(bars, action)
        # Wrapper der last_big_action_bar setzt
        def wrapped():
            action()
            self._last_big_action_bar = self.get_current_bar()
        sa.action = wrapped
        return sa

    def cancel(self, sa: ScheduledAction) -> None:
        sa.cancelled = True
