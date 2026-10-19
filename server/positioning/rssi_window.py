from collections import deque, defaultdict
from statistics import median


class RssiWindow:

    def __init__(self, window_size: int = 5, max_age: float = 10):
        self._window_size = window_size
        self._max_age = max_age # Ab wann sollen alte Werte, obwohl in windows_size verworfen werden (bei unregelmäßigem senden)
        self._window: dict[str, deque[tuple[float,int]]] = defaultdict(lambda: deque(maxlen=window_size))

    def add(self, node: str, rssi: int, at: float) -> None:
        """Neue Messung eines Knotens merken."""
        self._window[node].append((at, rssi))


    def snapshot(self, now: float) -> dict[str, float]:
        """Geglätteter Wert pro Knoten; zu alte Knoten fehlen."""
        snapshot = {}
        for node in self._window.keys():
            data = self._window[node]

            recent_data = [pair[1] for pair in data if now - pair[0] <= self._max_age]
            if len(recent_data) > 0:
                avg_rssi = median(recent_data) # or maybe fmean()
                snapshot[node] = avg_rssi

        return snapshot

