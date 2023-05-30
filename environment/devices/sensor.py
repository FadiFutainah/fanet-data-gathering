from environment.devices.device import Device
from environment.utils.position import Position


class Sensor(Device):
    def __init__(self, id: int, position: Position, memory_size: int = 100) -> None:
        super().__init__(id, position)
        self.memory_size = memory_size

        # this is only temporary for the first version of the experiment
        self.collected_data_size = self.memory_size

    def gather_data(self) -> None:
        pass

    def send_data(self, data_size: int) -> None:
        pass

    def is_empty(self) -> bool:
        return self.collected_data_size == 0
