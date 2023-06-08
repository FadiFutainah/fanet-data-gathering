from environment.devices.device import Device
from environment.utils.position import Position


class Sensor(Device):
    def __init__(self, id: int, position: Position, memory_size: int, current_data: int,
                 data_collecting_rate: float) -> None:
        super().__init__(id, position, current_data, memory_size, memory_size)
        self.data_collecting_rate = data_collecting_rate

    def is_empty(self) -> bool:
        if self.current_data == 0:
            return True
        return False
