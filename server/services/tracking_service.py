from collections.abc import Callable

from positioning.room_estimator import RoomEstimator
from services.device_tracker import DeviceTracker
from models.stay_event import StayEvent
from models.detection import Detection


class TrackingService:
    """Verteiler: leitet jede Messung an den Tracker des passenden Geräts."""

    def __init__(self, device_names: list[str], estimator: RoomEstimator,
                 emit: Callable[[StayEvent], None]):
        self._trackers = {
            name: DeviceTracker(name, estimator, emit) for name in device_names
        }

    def on_detection(self, detection: Detection) -> None:
        tracker = self._trackers.get(detection.device_name)
        if tracker is None:
            print(f"Unknown device: {detection.device_name}")  # sollte nie passieren
            return
        tracker.on_detection(detection)

    def on_tick(self, now: float) -> None:
        for tracker in self._trackers.values():
            tracker.on_tick(now)