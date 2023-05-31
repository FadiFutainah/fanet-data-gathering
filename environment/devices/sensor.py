import logging

from environment.devices.device import Device
from environment.utils.position import Position


class Sensor(Device):
    def __init__(self, id: int, position: Position, memory_size: int = 100) -> None:
        super().__init__(id, position, memory_size, memory_size)

    def is_empty(self) -> bool:
        if self.collected_data_size == 0:
            logging.warning(f'{self} is empty!!')
            return True
        return False
