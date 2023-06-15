import logging
from dataclasses import dataclass, field

from environment.devices.device import Device


@dataclass
class Sensor(Device):
    data_collecting_rate: int
    data_loss: int = field(init=False, default=0)

    def receive_data(self, data_size: int) -> None:
        if not self.has_memory(data_size):
            overwritten_data = data_size - self.get_available_memory()
            self.data_loss += overwritten_data
            logging.warning(f'{self} doesn\'t have enough memory so it\'s overwriting {overwritten_data} of the data')
        self.collected_data += data_size
        self.current_data = min(self.current_data + data_size, self.memory_size)

    def step(self) -> None:
        self.receive_data(data_size=self.data_collecting_rate)

    def is_empty(self) -> bool:
        return self.current_data == 0
