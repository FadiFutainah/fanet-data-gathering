from environment.devices.device import Device
from environment.utils.position import Position


class Sensor(Device):
    def __init__(self, id: int, position: Position, memory_size: int = 100) -> None:
        super().__init__(id, position)
        self.memory_size = memory_size

        self.collected_data_size = self.memory_size

    def gather_data(self) -> None:
        pass

    def transmit_data(self) -> None:
        pass

    def is_empty(self) -> bool:
        return self.collected_data_size == 0
