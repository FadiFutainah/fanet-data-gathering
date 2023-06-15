import logging

from dataclasses import dataclass, field
from typing import List

from environment.core.physical_object import PhysicalObject
from environment.networking.data_packets import DataPackets
from environment.networking.memory import Memory

import numpy as np


@dataclass
class Device(PhysicalObject):
    id: int
    buffer: Memory
    memory: Memory
    num_of_collected_packets: int
    connected_devices: np.ndarray[int] = field(init=False, default=np.array([]))
    """ the ids of the connected devices """

    def __post_init__(self) -> None:
        logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.id}'

    def move_to_buffer_queue(self, data_size: int) -> None:
        data_packets = self.memory.fetch_data(data_size)
        self.receive_in_buffer(data_packets)

    def receive_in_buffer(self, data_packets: List[DataPackets]) -> None:
        self.buffer.store_data(data_packets)

    def remove_from_buffer(self, data_size: int) -> List[DataPackets]:
        return self.buffer.fetch_data(data_size)

    def move_to_memory(self, data_size) -> None:
        data_packets = self.buffer.fetch_data(data_size)
        self.memory.store_data(data_packets)

    def is_connected_to(self, id: int) -> bool:
        index = self.connected_devices.searchsorted(v=id)
        return index < len(self.connected_devices) and self.connected_devices[index] == id

    def connect_to(self, id: int):
        if self.is_connected_to(id):
            raise ConnectionAbortedError(f'{self} is already connected to device:{id}')
        index = self.connected_devices.searchsorted(v=id)
        np.insert(self.connected_devices, index, id)
        logging.info(f'connection established between {self} and device_id: {id}')

    def step(self) -> None:
        pass
