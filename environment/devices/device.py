import logging

from environment.utils.position import Position


class Device:
    def __init__(self, id: int, position: Position, memory_size: int, collected_data_size: int) -> None:
        self.id = id
        self.position = position
        self.collected_data_size = collected_data_size
        self.memory_size = memory_size
        logging.info(f'{type(self).__name__} created at pos: {position}')

    def send_data(self, data_size: int) -> int:
        if self.collected_data_size < data_size:
            logging.warning(f'{type(self).__name__} {self.id} did\'t send the hole packet')
            self.collected_data_size = 0
            return self.collected_data_size
        self.collected_data_size -= data_size
        return data_size

    def receive_data(self, data_size: int) -> int:
        if self.get_available_memory() < data_size:
            logging.warning(f'{type(self).__name__} {self.id} did\'t receive the hole packet')
            self.collected_data_size = self.memory_size
            return self.get_available_memory()
        self.collected_data_size += data_size
        return data_size

    def get_available_memory(self) -> int:
        return self.memory_size - self.collected_data_size
