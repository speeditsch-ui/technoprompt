"""Makro-Execution: bar-basierte Scheduling, respektiert Profil-Grenzen."""
from __future__ import annotations

from .registry import Macro, MacroStep, get_macro
from ..profiles.profiles import Profile, get_profile, clamp_to_profile


class MacroEngine:
    """Führt Makros über bar-basiertes Scheduling aus."""

    def __init__(self, state: dict, send_osc: Callable[[str, float], None], get_current_bar: Callable[[], int]):
        self.state = state
        self.send_osc = send_osc
        self.get_current_bar = get_current_bar
        self._active_macro: str | None = None
        self._macro_steps_done: set[int] = set()

    def run(self, macro_name: str) -> bool:
        """Startet ein Makro. Returns True wenn Makro gefunden."""
        macro = get_macro(macro_name)
        if not macro:
            return False
        self._active_macro = macro.name
        self._macro_steps_done = set()
        return True

    def tick(self) -> None:
        """Sollte pro Bar aufgerufen werden. Führt ausstehende Steps aus."""
        if not self._active_macro:
            return
        macro = get_macro(self._active_macro)
        if not macro:
            return
        bar = self.get_current_bar()
        profile = get_profile(self.state.get("profile", "peak") or "peak")
        for step in macro.steps:
            if step.bar_offset <= bar and step.bar_offset not in self._macro_steps_done:
                self._execute_step(step, profile)
                self._macro_steps_done.add(step.bar_offset)

    def _execute_step(self, step: MacroStep, profile: "Profile | None") -> None:
        if step.action == "set_param" and step.param and step.value is not None:
            val = self.state.get(step.param, 0.5)
            if isinstance(step.value, (int, float)):
                val = val + step.value
            else:
                val = step.value
            if profile:
                val = clamp_to_profile(val, step.param, profile)
            self.send_osc(step.param, float(val))
            self.state[step.param] = val

    def stop(self) -> None:
        self._active_macro = None
        self._macro_steps_done.clear()

    @property
    def active_macro(self) -> str | None:
        return self._active_macro
