from collections.abc import Callable


class RoomEstimator:
    def __init__(self, room_of: Callable[[str], str]): ...
    def estimate(self, snapshot: dict[str, float]) -> str | None:
        """Raum-Kandidat, oder None für 'weg'."""