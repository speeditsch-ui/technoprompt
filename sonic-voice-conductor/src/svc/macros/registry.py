"""Makro-Definitionen: Steps mit bar_offset -> Aktion."""
from dataclasses import dataclass
from typing import Callable, Any


@dataclass
class MacroStep:
    bar_offset: int
    action: str  # "set_param" | "run_action"
    param: str | None
    value: float | str | None


@dataclass
class Macro:
    name: str
    steps: list[MacroStep]


MACROS: dict[str, Macro] = {
    "hypnotischer_zug": Macro(
        name="hypnotischer_zug",
        steps=[
            MacroStep(0, "set_param", "hats", -0.1),
            MacroStep(4, "set_param", "darkness", 0.1),
            MacroStep(8, "set_param", "energy", 0.1),
            MacroStep(12, "set_param", "hats", 0.15),
        ],
    ),
    "mechanischer_groove": Macro(
        name="mechanischer_groove",
        steps=[
            MacroStep(0, "set_param", "hats", 0.1),
            MacroStep(4, "set_param", "energy", 0.05),
            MacroStep(8, "set_param", "darkness", -0.05),
        ],
    ),
    "schmutziger_peak": Macro(
        name="schmutziger_peak",
        steps=[
            MacroStep(0, "set_param", "energy", 0.2),
            MacroStep(4, "set_param", "darkness", 0.1),
            MacroStep(8, "set_param", "hats", 0.15),
        ],
    ),
    "micro_variation": Macro(
        name="micro_variation",
        steps=[
            MacroStep(0, "set_param", "hats", -0.02),
            MacroStep(2, "set_param", "hats", 0.02),
            MacroStep(4, "set_param", "hats", -0.02),
            MacroStep(6, "set_param", "hats", 0.02),
        ],
    ),
    "tighten_hats": Macro(
        name="tighten_hats",
        steps=[
            MacroStep(0, "set_param", "hats", -0.05),
            MacroStep(4, "set_param", "hats", 0.03),
            MacroStep(8, "set_param", "hats", -0.02),
        ],
    ),
}


def get_macro(name: str) -> Macro | None:
    n = name.lower().replace(" ", "_").replace("-", "_")
    return MACROS.get(n)


def list_macros() -> list[str]:
    return list(MACROS.keys())
