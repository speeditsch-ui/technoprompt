"""Tests für Scheduler (mit Fake-Zeit)."""
import time
from svc.scheduler.scheduler import Scheduler, ScheduledAction


def test_seconds_per_bar():
    s = Scheduler(bpm=120)
    assert abs(s.seconds_per_beat - 0.5) < 0.01
    assert abs(s.seconds_per_bar - 2.0) < 0.01


def test_schedule():
    s = Scheduler(bpm=120)
    executed = []

    def action():
        executed.append(1)

    sa = s.schedule(2, action)
    assert sa is not None
    # Sofort tick – due_bar ist current_bar + 2
    # current_bar startet bei 0 (get_current_bar_float nutzt monotonic time)
    # Ohne Zeitfortschritt wird nichts ausgeführt
    s.tick()
    # Mit sehr kurzer Zeit: current_bar ~ 0, due_bar = 2 -> nicht fällig
    assert len(executed) == 0


def test_cancel():
    s = Scheduler(bpm=120)
    executed = []

    def action():
        executed.append(1)

    sa = s.schedule(0, action)
    sa.cancelled = True
    s.tick()
    assert len(executed) == 0
