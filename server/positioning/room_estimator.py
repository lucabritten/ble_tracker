

class RoomEstimator:
    def __init__(self, node_rooms: dict[str, str], min_rssi: float = -80):
        self._node_rooms = node_rooms
        self._min_rssi = min_rssi


    def estimate(self, snapshot: dict[str, float]) -> str | None:
        """Raum-Kandidat, oder None für 'weg'."""
        if len(snapshot.keys()) == 0:
            return None

        max_node = max(snapshot, key=snapshot.get)

        if snapshot[max_node] < self._min_rssi:
            return None
        room = self._node_rooms[max_node]

        return room
