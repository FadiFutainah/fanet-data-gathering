from environment.devices.device import Device
from environment.utils.position import Position


class BaseStation(Device):
    def __init__(self, id: int, position: Position, collected_data_size: int = 0) -> None:
        super().__init__(id, position, collected_data_size)
