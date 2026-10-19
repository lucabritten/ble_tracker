from dataclasses import dataclass

from shared.utility import is_mac_address

@dataclass(frozen=True)
class Device:
    name: str
    display_name: str
    irk: str
