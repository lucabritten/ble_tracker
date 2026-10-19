import pytest

from positioning.presence_tracker import PresenceTracker
from positioning.room_estimator import RoomEstimator
from positioning.rssi_window import RssiWindow
from helpers import AWAY_AFTER, CONFIRM_AFTER, DEVICE, feed, MAX_AGE, WINDOW_SIZE


# ==== presence_tracker ====
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

# ==== rssi_window ====
@pytest.fixture
def rssi_window() -> RssiWindow:
    return RssiWindow(WINDOW_SIZE, MAX_AGE)

# ==== room_estimator ====
@pytest.fixture
def room_estimator() -> RoomEstimator:
    return RoomEstimator({"kitchen-esp": "kitchen", "bed-esp": "bedroom", "wardrobe-esp": "bedroom"}, min_rssi = -80)