from environment.devices.device import Device
from environment.utils.position import Position


class BaseStation(Device):
    def __init__(self, id: int, position: Position, memory_size, current_data: int = 0,
                 collected_data: int = 0) -> None:
        super().__init__(id, position, memory_size, current_data, collected_data)
