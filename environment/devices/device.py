import logging
from dataclasses import dataclass, field
from queue import PriorityQueue

from typing import List

import numpy as np

from environment.core.physical_object import PhysicalObject
from environment.networking.data_packets import DataPackets


@dataclass
class Device(PhysicalObject):
    id: int
    buffer_size: int
    """ number of packets that could be in the buffer """
    memory_size: int
    """ number of packets that could be in the device memory """
    buffer_io_speed: int
    """ number of packets that could transferred in and out of the buffer in one timestep """
    num_of_current_packets: int
    """ the number of current data packets """
    current_data: List[DataPackets]
    """ the current data packets ordered(hashed) by created time """
    num_of_collected_packets: int
    """ the collected data packets ordered(hashed) by created time """
    data_buffer_queue: PriorityQueue[DataPackets] = field(init=False)
    """ the data packets in the queue ordered(hashed) by created time """
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

    def get_available_memory(self) -> int:
        return self.memory_size - self.num_of_current_packets

    def get_available_buffer(self) -> int:
        return self.buffer_size - self.

    def has_data(self, num_of_packets: int = 1) -> bool:
        return self.num_of_current_packets - num_of_packets >= 0

    def has_memory(self, num_of_packets: int = 1) -> bool:
        return self.get_available_memory() - num_of_packets >= 0

    def step(self) -> None:
        pass
