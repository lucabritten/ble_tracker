# services/device_tracker.py
from typing import Callable

from models.stay_event import StayEvent
from models.detection import Detection
from positioning.presence_tracker import PresenceTracker
from positioning.rssi_window import RssiWindow
from positioning.room_estimator import RoomEstimator

class DeviceTracker:
    """Die komplette Ortung für EIN Gerät."""

    def __init__(self, device_name: str, estimator: RoomEstimator,
                 emit: Callable[[StayEvent], None]):
        self._device_name = device_name
        self._estimator = estimator          # geteilt, ohne Zustand
        self._emit = emit                    # wohin die Ereignisse gehen
        self._window = RssiWindow()          # Zustand pro Gerät
        self._presence = PresenceTracker(device_name)  # Zustand pro Gerät

    def on_detection(self, detection: Detection) -> None:
        self._window.add(detection.esp_node_name, detection.rssi, detection.arrival_time)
        self._evaluate(detection.arrival_time)

    def on_tick(self, now: float) -> None:
        self._evaluate(now)

    def _evaluate(self, now: float) -> None:
        snapshot = self._window.snapshot(now)
        candidate = self._estimator.estimate(snapshot)
        for event in self._presence.update(candidate, now):
            self._emit(event)