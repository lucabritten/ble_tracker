import pytest

from positioning.presence_tracker import PresenceTracker
from helpers import AWAY_AFTER, CONFIRM_AFTER, DEVICE, feed


@pytest.fixture
def tracker() -> PresenceTracker:
    """Frischer Tracker ohne Vorgeschichte."""
    return PresenceTracker(DEVICE, CONFIRM_AFTER, AWAY_AFTER)


@pytest.fixture
def tracker_in_kitchen(tracker) -> PresenceTracker:
    """Tracker, bei dem 'kitchen' ab now=5 bestätigt ist.

    Alle Tests, die diese Fixture nutzen, müssen mit Zeiten > 5 weitermachen.
    """
    feed(tracker, [(0, "kitchen"), (5, "kitchen")])
    return tracker
