import logging

from environment.utils.position import Position


class Device:
    def __init__(self, id: int, position: Position, memory_size: int, collected_data_size: int) -> None:
        self.id = id
        self.position = position
        self.memory_size = memory_size
        self.collected_data_size = collected_data_size
        logging.info(f'{type(self).__name__} created at pos: {position}')

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.id}'

    def send_data(self, data_size: int) -> int:
        if not self.has_data(data_size):
            logging.warning(f'{self} has less collected data than {data_size}')
            available_data = self.collected_data_size
            self.collected_data_size = 0
            return available_data
        self.collected_data_size -= data_size
        return data_size

    def receive_data(self, data_size: int) -> int:
        if self.get_available_memory() < data_size:
            logging.warning(f'{self} doesn\'t have enough memory')
            self.collected_data_size = self.memory_size
            return self.get_available_memory()
        self.collected_data_size += data_size
        return data_size

    def get_available_memory(self) -> int:
        return self.memory_size - self.collected_data_size

    def has_data(self, data_size: int = 1):
        return self.collected_data_size - data_size >= 0

    def has_memory(self, data_size: int = 1):
        return self.get_available_memory() - data_size >= 0
