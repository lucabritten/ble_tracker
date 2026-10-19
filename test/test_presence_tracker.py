"""Spezifikation des PresenceTrackers.

Parameter: confirm_after = 5, away_after = 20.
Entscheidung zum Zeitstempel: 'at' ist der Zeitpunkt der Bestätigung (now),
nicht der Beginn der Probe.
"""
import pytest

from positioning.presence_tracker import PresenceTracker
from helpers import DEVICE, ended, every_second, feed, started


# ---------- A. Start ----------

def test_none_from_start_emits_nothing(tracker):                        # 1
    assert feed(tracker, every_second(0, 30, None)) == []


def test_single_candidate_is_not_confirmed(tracker):                    # 2
    assert feed(tracker, [(0, "kitchen")]) == []


def test_first_room_confirmed_after_threshold(tracker):                 # 3
    events = feed(tracker, [(0, "kitchen"), (3, "kitchen"), (5, "kitchen")])
    assert events == [started("kitchen", 5)]


def test_probe_too_short_emits_nothing(tracker):                        # 4
    steps = [(0, "kitchen"), (3, "kitchen"), (4, None), (10, None)]
    assert feed(tracker, steps) == []


@pytest.mark.parametrize("now, expected", [                             # 5, 6
    (4.99, []),
    (5.0, [started("kitchen", 5.0)]),
    (5.01, [started("kitchen", 5.01)]),
])
def test_confirmation_boundary(tracker, now, expected):
    assert feed(tracker, [(0, "kitchen"), (now, "kitchen")]) == expected


# ---------- B. Stabil ----------

def test_same_room_repeated_emits_nothing(tracker_in_kitchen):          # 7
    assert feed(tracker_in_kitchen, every_second(6, 100, "kitchen")) == []


def test_no_duplicate_events_after_change(tracker_in_kitchen):          # 8
    feed(tracker_in_kitchen, [(10, "bath"), (15, "bath")])
    assert feed(tracker_in_kitchen, [(16, "bath")]) == []


# ---------- C. Raumwechsel ----------

def test_clean_room_change(tracker_in_kitchen):                         # 9
    events = feed(tracker_in_kitchen, [(10, "bath"), (12, "bath"), (15, "bath")])
    assert events == [ended("kitchen", 15), started("bath", 15)]


def test_ended_comes_before_started(tracker_in_kitchen):                # 10
    events = feed(tracker_in_kitchen, [(10, "bath"), (15, "bath")])
    assert [e.kind for e in events] == ["ended", "started"]


def test_flicker_emits_nothing(tracker_in_kitchen):                     # 11
    steps = [(10, "bath"), (12, "kitchen"), (14, "bath"),
             (16, "kitchen"), (18, "bath"), (20, "kitchen")]
    assert feed(tracker_in_kitchen, steps) == []


def test_interrupted_probe_restarts(tracker_in_kitchen):                # 12
    # Die Probe für 'bath' beginnt bei 10 neu, nicht bei 6.
    assert feed(tracker_in_kitchen, [(6, "bath"), (8, "kitchen"), (10, "bath"), (14, "bath")]) == []
    assert feed(tracker_in_kitchen, [(15, "bath")]) == [ended("kitchen", 15), started("bath", 15)]


def test_probe_switches_to_third_room(tracker_in_kitchen):              # 13
    events = feed(tracker_in_kitchen, [(10, "bath"), (12, "living"), (17, "living")])
    assert events == [ended("kitchen", 17), started("living", 17)]


# ---------- D. Weg und zurück ----------

def test_away_needs_away_after_not_confirm_after(tracker_in_kitchen):   # 14
    assert feed(tracker_in_kitchen, [(10, None), (15, None), (29, None)]) == []


def test_leaving_emits_ended(tracker_in_kitchen):                       # 15
    events = feed(tracker_in_kitchen, every_second(10, 30, None))
    assert events == [ended("kitchen", 30)]


def test_short_dropout_keeps_room(tracker_in_kitchen):                  # 16
    steps = every_second(10, 25, None) + [(26, "kitchen")]
    assert feed(tracker_in_kitchen, steps) == []
    # Die Küche gilt weiter: ein späteres Verlassen beendet sie.
    assert feed(tracker_in_kitchen, every_second(30, 50, None)) == [ended("kitchen", 50)]


def test_return_after_leaving(tracker_in_kitchen):                      # 17
    feed(tracker_in_kitchen, every_second(10, 30, None))
    assert feed(tracker_in_kitchen, [(40, "kitchen"), (45, "kitchen")]) == [started("kitchen", 45)]


def test_away_probe_then_other_room(tracker_in_kitchen):                # 18
    events = feed(tracker_in_kitchen, [(10, None), (12, "bath"), (17, "bath")])
    assert events == [ended("kitchen", 17), started("bath", 17)]


# ---------- E. Robustheit ----------

def test_trackers_do_not_share_state():                                 # 19
    first = PresenceTracker("first", 5.0, 20.0)
    second = PresenceTracker("second", 5.0, 20.0)
    feed(first, [(0, "kitchen"), (5, "kitchen")])
    assert feed(second, [(5, "kitchen")]) == []


def test_events_carry_device_name(tracker_in_kitchen):                  # 20
    events = feed(tracker_in_kitchen, [(10, "bath"), (15, "bath")])
    assert events
    assert all(e.device_name == DEVICE for e in events)


def test_time_going_backwards(tracker):                                 # 21
    # Entscheidung: kein Absturz, kein Ereignis.
    assert feed(tracker, [(10, "kitchen"), (8, "kitchen")]) == []


def test_duplicate_timestamp(tracker):                                  # 22
    events = feed(tracker, [(0, "kitchen"), (5, "kitchen"), (5, "kitchen")])
    assert events == [started("kitchen", 5)]
