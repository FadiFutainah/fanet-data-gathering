import logging

from environment.devices.device import Device
from environment.utils.position import Position


class Sensor(Device):
    def __init__(self, id: int, position: Position, memory_size: int = 100) -> None:
        super().__init__(id, position, memory_size)
        self.memory_size = memory_size

    def is_empty(self) -> bool:
        return self.collected_data_size == 0
