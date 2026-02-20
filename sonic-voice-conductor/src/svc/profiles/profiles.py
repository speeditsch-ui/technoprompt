"""Built-in Profile-Definitionen: warmup, peak, afterhour, industrial."""
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Profile:
    name: str
    bpm_min: int
    bpm_max: int
    max_delta_per_minute: float
    param_clamps: dict[str, tuple[float, float]]
    allowed_actions: set[str]
    defaults: dict[str, Any]


PROFILE_DEFAULTS: dict[str, Profile] = {
    "warmup": Profile(
        name="warmup",
        bpm_min=115,
        bpm_max=128,
        max_delta_per_minute=2.0,
        param_clamps={"energy": (0.2, 0.6), "darkness": (0.3, 0.7), "hats": (0.3, 0.6)},
        allowed_actions={"bpm_small", "break", "energy", "darkness", "hats"},
        defaults={"bpm": 122, "energy": 0.4, "darkness": 0.5, "hats": 0.45},
    ),
    "peak": Profile(
        name="peak",
        bpm_min=125,
        bpm_max=135,
        max_delta_per_minute=5.0,
        param_clamps={"energy": (0.5, 1.0), "darkness": (0.2, 0.8), "hats": (0.4, 1.0)},
        allowed_actions={"bpm", "break", "drop", "energy", "darkness", "hats", "macro"},
        defaults={"bpm": 128, "energy": 0.75, "darkness": 0.4, "hats": 0.7},
    ),
    "afterhour": Profile(
        name="afterhour",
        bpm_min=110,
        bpm_max=122,
        max_delta_per_minute=3.0,
        param_clamps={"energy": (0.2, 0.6), "darkness": (0.5, 0.95), "hats": (0.2, 0.6)},
        allowed_actions={"bpm_small", "break", "energy", "darkness", "hats"},
        defaults={"bpm": 118, "energy": 0.35, "darkness": 0.7, "hats": 0.4},
    ),
    "industrial": Profile(
        name="industrial",
        bpm_min=130,
        bpm_max=145,
        max_delta_per_minute=4.0,
        param_clamps={"energy": (0.6, 1.0), "darkness": (0.4, 0.9), "hats": (0.5, 1.0)},
        allowed_actions={"bpm", "break", "drop", "energy", "darkness", "hats", "macro"},
        defaults={"bpm": 135, "energy": 0.8, "darkness": 0.6, "hats": 0.75},
    ),
}


def get_profile(name: str) -> Profile | None:
    return PROFILE_DEFAULTS.get(name.lower())


def list_profiles() -> list[str]:
    return list(PROFILE_DEFAULTS.keys())


def clamp_to_profile(value: float, param: str, profile: Profile) -> float:
    """Clamp Wert nach Profil-Grenzen."""
    if param in profile.param_clamps:
        lo, hi = profile.param_clamps[param]
        return max(lo, min(hi, value))
    return value
