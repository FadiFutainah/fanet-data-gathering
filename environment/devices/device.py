import logging

from dataclasses import dataclass
from typing import List

from environment.devices.physical_object import PhysicalObject
from environment.networking.data_packet_collection import DataPacketCollection
from environment.devices.memory import Memory

from environment.networking.wifi_network import WiFiNetwork


@dataclass
class Device(PhysicalObject):
    id: int
    buffer: Memory
    memory: Memory
    network: WiFiNetwork
    num_of_collected_packets: int
    """ the ids of the connected devices """

    def __post_init__(self) -> None:
        logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.id}'

    def move_to_buffer_queue(self, data_size: int) -> None:
        data_packets = self.memory.fetch_data(data_size)
        self.buffer.store_data(data_packets)

    def move_to_memory(self, data_size) -> None:
        data_packets = self.buffer.fetch_data(data_size)
        self.memory.store_data(data_packets)

    def fetch_data(self, data_size: int) -> List[DataPacketCollection]:
        if not self.buffer.has_data(data_size):
            remaining_data = data_size - self.buffer.current_size
            self.move_to_buffer_queue(remaining_data)
        return self.buffer.fetch_data(data_size)

    def prepare_data_sending(self):
        speed = min(self.buffer.io_speed, self.memory.io_speed)
        if len(self.network.connections) > 0:
            self.move_to_buffer_queue(speed)

    def run(self, time: int = 1) -> None:
        self.buffer.decrease_packets_life_time(time)

    def in_range(self, other: 'Device') -> bool:
        return self.position.distance_from(other.position) <= self.network.coverage_radius
