import logging
from dataclasses import dataclass, field

from typing import List

import numpy as np

from environment.core.physical_object import PhysicalObject
from environment.networking.memory import Memory


@dataclass
class Device(PhysicalObject):
    id: int
    buffer: Memory
    memory: Memory
    num_of_collected_packets: int
    connected_devices: List[int] = field(init=False, default=List[int])
    """ the ids of the connected devices """

    def __post_init__(self) -> None:
        logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.id}'

    def send_data(self, num_of_packets: int) -> None:
        buffer_size = self.get_available_buffer()

        # get_data_chunk_from_memory(data_size)
        # add_to_sending_queue_buffer()
        # handshake()
        #
        if not self.has_data(num_of_packets):
            raise ValueError(f'{self} has less collected data than {num_of_packets}')
        self.current_data -= num_of_packets

    def receive_data(self, data_size: int) -> None:
        if not self.has_memory(data_size):
            raise ValueError(f'{self} doesn\'t have enough memory for {data_size}')
        self.current_data += data_size
        self.collected_data += data_size

    def is_connected_to(self, id: int) -> bool:
        index = self.connected_devices.searchsorted(v=id)
        return index < len(self.connected_devices) and self.connected_devices[index] == id

    def connect_to(self, id: int):
        if self.is_connected_to(id):
            raise ConnectionAbortedError(f'{self} is already connected to device:{id}')
        index = self.connected_devices.searchsorted(v=id)
        np.insert(self.connected_devices, index, id)
        logging.info(f'connection completed between {self} and device_id: {id}')

    def step(self) -> None:
        pass
