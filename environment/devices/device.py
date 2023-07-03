import logging

from dataclasses import dataclass
from typing import List

from environment.devices.physical_object import PhysicalObject
from environment.networking.data_packet_collection import DataPacketCollection
from environment.devices.memory import Memory
from environment.networking.transfer_type import TransferType

from environment.networking.wifi_network import WiFiNetwork


@dataclass(order=True)
class Device(PhysicalObject):
    id: int
    sending_buffer: Memory
    receiving_buffer: Memory
    memory: Memory
    network: WiFiNetwork
    num_of_collected_packets: int
    energy: float

    def __post_init__(self) -> None:
        logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__} {self.id}'

    def move_to_buffer_queue(self, data_size: int) -> None:
        """ called before sending the data """
        self.memory.move_to(self.sending_buffer, data_size)

    def move_to_memory(self) -> None:
        """ called after receiving the data """
        self.receiving_buffer.move_to(self.memory, self.receiving_buffer.io_speed)

    def fetch_data(self, data_size: int) -> List[DataPacketCollection]:
        if not self.sending_buffer.has_data(data_size):
            remaining_data = data_size - self.sending_buffer.current_size
            remaining_data = min(remaining_data, self.sending_buffer.io_speed)
            self.move_to_buffer_queue(remaining_data)
        return self.sending_buffer.fetch_data(data_size)

    def store_data(self, data_packets: List[DataPacketCollection]) -> None:
        return self.receiving_buffer.store_data(data_packets)

    def prepare_data_sending(self):
        speed = min(self.sending_buffer.io_speed, self.memory.io_speed)
        if len(self.network.connections) > 0:
            self.move_to_buffer_queue(speed)

    def run(self, time: int = 1) -> None:
        self.sending_buffer.decrease_packets_life_time(time)
        self.receiving_buffer.decrease_packets_life_time(time)

    def read_data(self) -> List[DataPacketCollection]:
        return self.memory.read_data()

    def get_available_to_send(self) -> int:
        return self.sending_buffer.current_size

    def get_available_to_receive(self) -> int:
        return self.receiving_buffer.get_available()

    def transfer_data(self, device: 'Device', data_size: int, transfer_type: TransferType) -> 'DataTransition':
        return self.network.transfer_data(source=self, destination=device, data_size=data_size,
                                          transfer_type=transfer_type)

    def in_range(self, other: 'Device') -> bool:
        return self.position.distance_from(other.position) <= self.network.coverage_radius
