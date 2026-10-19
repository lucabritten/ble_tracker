from models.stay_event import StayEvent

_NO_PROBE = object()

class PresenceTracker:
    def __init__(self, device_name: str,
                 confirm_after: float = 5.0,
                 away_after: float = 20.0) -> None:
        self.device_name = device_name
        self.confirm_after = confirm_after
        self.away_after = away_after
        self._confirmed: str | None = None
        self._pending: str | None | object = _NO_PROBE
        self._pending_since: float | None = None

    def update(self, candidate: str | None, now: float) -> list[StayEvent]:
        """Verarbeitet einen neuen Kandidaten.

        candidate: Raum vom RoomEstimator oder None für 'weg'.
        now:       aktuelle Zeit, von außen übergeben (für Tests).
        returns:   [] im Normalfall,
                   [started] beim ersten bestätigten Raum,
                   [ended] beim bestätigten Verlassen,
                   [ended, started] bei einem bestätigten Raumwechsel.
        """
        if candidate == self._confirmed:
            self._pending = _NO_PROBE
            return []

        if candidate != self._pending:
            self._pending = candidate
            self._pending_since = now
            return []

        if candidate is None:
            threshold = self.away_after
        else:
            threshold = self.confirm_after

        if now - self._pending_since < threshold:
            return []

        events = []
        if self._confirmed is not None:
            events.append(StayEvent(self.device_name, self._confirmed, "ended", now))
        if candidate is not None:
            events.append(StayEvent(self.device_name, candidate, "started", now))

        self._confirmed = candidate
        self._pending = _NO_PROBE
        self._pending_since = None
        return events



