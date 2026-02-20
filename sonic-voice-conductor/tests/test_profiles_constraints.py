"""Tests für Profile und Constraints."""
import pytest
from svc.profiles.profiles import get_profile, list_profiles, clamp_to_profile


def test_list_profiles():
    profs = list_profiles()
    assert "warmup" in profs
    assert "peak" in profs
    assert "afterhour" in profs
    assert "industrial" in profs


def test_get_profile():
    p = get_profile("peak")
    assert p is not None
    assert p.name == "peak"
    assert p.bpm_min <= p.bpm_max
    assert "energy" in p.param_clamps


def test_clamp_to_profile():
    p = get_profile("warmup")
    assert p is not None
    v = clamp_to_profile(0.9, "energy", p)
    assert v <= 0.6
    v = clamp_to_profile(0.1, "energy", p)
    assert v >= 0.2


def test_unknown_profile():
    assert get_profile("foo") is None
