from models.device import Device
from models.esp_node import EspNode

class Registry:
    def __init__(self, devices: list[Device], nodes: list[EspNode]):
        self._devices = devices
        self._nodes = nodes

    @property
    def device_names(self) -> list[str]:
        return [device.name for device in self._devices]

    @property
    def node_rooms(self) -> dict[str, str]:
        return {node.name: node.room_name for node in self._nodes}