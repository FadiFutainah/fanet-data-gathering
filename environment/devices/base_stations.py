from environment.devices.device import Device
from environment.utils.position import Position


class BaseStation(Device):
    def __init__(self, id: int, position: Position, current_data: int = 0, memory_size: int = 1e10) -> None:
        super().__init__(id, position, memory_size, current_data)
