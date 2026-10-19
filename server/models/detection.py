from dataclasses import dataclass

@dataclass(frozen=True)
class Detection:
    device_name: str
    esp_node_name: str
    rssi: int
    arrival_time: float