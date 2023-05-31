import logging

from environment.utils.position import Position


class Device:
    def __init__(self, id: int, position: Position, collected_data_size: int) -> None:
        self.id = id
        self.position = position
        self.collected_data_size = collected_data_size
        logging.info(f'{type(self).__name__} created at pos: {position}')

    def send_data(self, data_size: int) -> None:
        self.collected_data_size -= data_size

    def receive_data(self, data_size: int) -> None:
        self.collected_data_size += data_size
