import logging

from dataclasses import dataclass
from typing import List

from environment.devices.physical_object import PhysicalObject
from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.data_packet import DataPacket
from environment.devices.memory import Memory

from environment.networking.wifi_network import WiFiNetwork


@dataclass
class Device(PhysicalObject):
    id: int
    buffer: Memory
    memory: Memory
    num_of_collected_packets: int
    protocol: ConnectionProtocol
    network: WiFiNetwork
    """ the ids of the connected devices """

    def __post_init__(self) -> None:
        logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__}{self.id}'

    def move_to_buffer_queue(self, data_size: int) -> None:
        data_packets = self.memory.fetch_data(data_size)
        self.buffer.store_data(data_packets)

    def move_from_buffer_queue(self, data_size: int) -> List[DataPacket]:
        return self.buffer.fetch_data(data_size)

    def move_to_memory(self, data_size) -> None:
        data_packets = self.buffer.fetch_data(data_size)
        self.memory.store_data(data_packets)

    def move_form_memory(self, data_size: int) -> List[DataPacket]:
        return self.memory.fetch_data(data_size)

    def prepare_data_sending(self):
        if len(self.network.connections) > 0:
            self.move_to_buffer_queue(self.buffer.io_speed)

