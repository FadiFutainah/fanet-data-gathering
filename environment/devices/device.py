import logging

from typing import List
from dataclasses import dataclass

from environment.devices.memory import Memory
from environment.networking.packet_data import PacketData
from environment.networking.wifi_network import WiFiNetwork
from environment.networking.transfer_type import TransferType
from environment.devices.physical_object import PhysicalObject
from environment.networking.data_transition import DataTransition


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
        data_size = min(data_size, self.sending_buffer.io_speed)
        self.memory.move_to(other=self.sending_buffer, data_size=data_size)

    def move_to_memory(self) -> None:
        speed = min(self.receiving_buffer.io_speed, self.memory.io_speed)
        self.receiving_buffer.move_to(other=self.memory, data_size=speed)

    def fetch_data(self, data_size: int) -> List[PacketData]:
        if not self.sending_buffer.has_data(data_size):
            remaining_data = data_size - self.sending_buffer.current_size
            remaining_data = min(remaining_data, self.sending_buffer.io_speed)
            self.move_to_buffer_queue(remaining_data)
        return self.sending_buffer.fetch_data(data_size)

    def store_data(self, data_packets: List[PacketData]) -> None:
        return self.receiving_buffer.store_data(data_packets)

    def prepare_data_sending(self):
        # speed = min(self.sending_buffer.io_speed, self.memory.io_speed)
        if len(self.network.connections) > 0:
            self.move_to_buffer_queue(self.sending_buffer.io_speed)

    def run_memory(self, time):
        # self.prepare_data_sending()
        self.move_to_memory()
        self.sending_buffer.decrease_packets_life_time(time)
        self.receiving_buffer.decrease_packets_life_time(time)

    def run(self, time: int = 1) -> None:
        self.run_memory(time)
        self.network.update_connections_distances()

    def read_data(self) -> List[PacketData]:
        return self.memory.read_data()

    def get_available_to_send(self) -> int:
        return self.sending_buffer.current_size

    def get_available_to_receive(self) -> int:
        return self.receiving_buffer.get_available()

    def send_to(self, device: 'Device', data_size: int) -> DataTransition:
        return self.network.transfer_data(source=self, destination=device, transfer_type=TransferType.SEND,
                                          data_size=data_size)

    def receive_from(self, device: 'Device', data_size: int) -> DataTransition:
        return self.network.transfer_data(source=self, destination=device, transfer_type=TransferType.RECEIVE,
                                          data_size=data_size)

    def connect_to_all(self, devices: List['Device']) -> None:
        for device in devices:
            if not self.network.is_connected_to(device):
                self.network.connect(self, device)

    def in_range(self, other: 'Device') -> bool:
        return self.position.distance_from(other.position) <= self.network.coverage_radius or \
            other.position.distance_from(self.position) <= other.network.coverage_radius


def consume_energy(self) -> None:
    pass


@staticmethod
def get_collecting_data_energy(e_elec, distance_threshold, power_amplifier_for_fs, power_amplifier_for_amp,
                               data_transition: DataTransition) -> float:
    k = data_transition.size
    distance = data_transition.source.position.distance_from(data_transition.destination.position)
    if distance < distance_threshold:
        e_t = k * (e_elec + power_amplifier_for_fs * (distance ** 2))
    else:
        e_t = k * (e_elec + power_amplifier_for_amp * (distance ** 4))
    e_r = k * e_elec
    energy = e_t + e_r
    return energy
