from models.stay_event import StayEvent

CONFIRM_AFTER = 5.0
AWAY_AFTER = 20.0
DEVICE = "luca-iphone"


def feed(tracker, steps: list[tuple[float, str | None]]) -> list[StayEvent]:
    """Spielt (now, candidate)-Paare ein und gibt alle Ereignisse zurück."""
    events = []
    for now, candidate in steps:
        events += tracker.update(candidate, now)
    return events


def every_second(start: int, end: int, candidate: str | None) -> list[tuple[float, str | None]]:
    """Schritte im Sekundentakt von start bis einschließlich end."""
    return [(t, candidate) for t in range(start, end + 1)]


def started(room: str, at: float) -> StayEvent:
    return StayEvent(DEVICE, room, "started", at)


def ended(room: str, at: float) -> StayEvent:
    return StayEvent(DEVICE, room, "ended", at)
