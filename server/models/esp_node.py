from dataclasses import dataclass

@dataclass(frozen=True)
class EspNode:
    name: str
    room_name: str
