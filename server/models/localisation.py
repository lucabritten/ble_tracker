from dataclasses import dataclass

@dataclass(frozen=True)
class Localisation:
    device_id: int
    x: int
    y: int
    estimated_location: str
    used_algorithm: str