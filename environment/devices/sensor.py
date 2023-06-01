import logging

from environment.devices.device import Device
from environment.utils.position import Position


class Sensor(Device):
    def __init__(self, id: int, position: Position, memory_size: int = 99) -> None:
        super().__init__(id, position, memory_size, memory_size, memory_size)

    def is_empty(self) -> bool:
        if self.current_data == 0:
            return True
        return False
