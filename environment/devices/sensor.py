import logging

from environment.devices.device import Device
from environment.utils.vector import Vector


class Sensor(Device):
    def __init__(self, id: int, position: Vector, memory_size: int, current_data: int,
                 data_collecting_rate: int) -> None:
        super().__init__(id, position, current_data, memory_size, memory_size)
        self.data_collecting_rate = data_collecting_rate
        self.data_loss = 0

    def is_empty(self) -> bool:
        if self.current_data == 0:
            return True
        return False

    def receive_data(self, data_size: int) -> int:
        if self.get_available_memory() < data_size:
            overwritten_data = data_size - self.get_available_memory()
            self.data_loss += overwritten_data
            logging.warning(f'{self} doesn\'t have enough memory so it\'s overwriting {overwritten_data} of the data')
            self.current_data = self.memory_size
            self.collected_data += data_size
            return data_size
        self.current_data += data_size
        self.collected_data += data_size
        return data_size

    def next_step(self):
        self.receive_data(data_size=self.data_collecting_rate)
