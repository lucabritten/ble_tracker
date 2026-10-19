# models/stay_event.py
from dataclasses import dataclass
from typing import Literal

@dataclass(frozen=True)
class StayEvent:
    device_name: str
    room: str
    kind: Literal["started", "ended"]
    at: float