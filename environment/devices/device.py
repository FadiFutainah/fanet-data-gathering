import logging
from dataclasses import dataclass, field

from environment.utils.vector import Vector


@dataclass(order=True)
class Device:
    id: int
    position: Vector
    velocity: Vector
    acceleration: Vector
    memory_size: int
    current_data: int
    collected_data: int

    def __post_init__(self):
        logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.id}'

    def send_data(self, data_size: int) -> int:
        if not self.has_data(data_size):
            logging.warning(f'{self} has less collected data than {data_size}')
            available_data = self.current_data
            self.current_data = 0
            return available_data
        self.current_data -= data_size
        return data_size

    def receive_data(self, data_size: int) -> int:
        if self.get_available_memory() < data_size:
            logging.warning(f'{self} doesn\'t have enough memory')
            self.current_data = self.memory_size
            self.collected_data += self.get_available_memory()
            return self.get_available_memory()
        self.current_data += data_size
        self.collected_data += data_size
        return data_size

    def get_available_memory(self) -> int:
        return self.memory_size - self.current_data

    def has_data(self, data_size: int = 1):
        return self.current_data - data_size >= 0

    def has_memory(self, data_size: int = 1):
        return self.get_available_memory() - data_size >= 0

    def move(self, delta_t: Vector) -> None:
        self.velocity = self.velocity + self.acceleration / t_vector
        self.position = self.position + self.velocity / t_vector

    def next_step(self):
        pass
