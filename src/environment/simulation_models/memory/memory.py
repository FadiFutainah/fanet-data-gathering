from copy import copy
from dataclasses import dataclass, field
from typing import List

from src.environment.core.globals import multiply_by_speed_rate
from src.environment.simulation_models.memory.data_packet import DataPacket
from src.environment.utils.priority_queue import PriorityQueue


@dataclass
class Memory:
    size: int
    io_speed: int
    current_size: int = 0
    current_data: PriorityQueue = field(default_factory=PriorityQueue, init=False)

    def __post_init__(self):
        self.io_speed = multiply_by_speed_rate(self.io_speed)

    def move_to(self, other: 'Memory', data_size: int) -> None:
        other.store_data(self.fetch_data(data_size))

    def get_available(self) -> int:
        return self.size - self.current_size

    def has_data(self, data_size: int = 1) -> bool:
        return self.current_size >= data_size

    def has_memory(self, data_size: int = 1) -> bool:
        return self.get_available() >= data_size

    def pop_prior_packet(self) -> DataPacket:
        data_packets = self.current_data.pop()
        self.current_size -= data_packets.size
        return data_packets

    def add_packet(self, data_packet: DataPacket) -> None:
        self.current_size += data_packet.size
        self.current_data.push(data_packet)

    def pop_all_data(self) -> List[DataPacket]:
        self.current_size = 0
        data = list(self.current_data)
        self.current_data.clear()
        return data

    def read_data(self) -> List[DataPacket]:
        return list(copy(self.current_data))

    def fetch_data(self, data_size: int) -> List[DataPacket]:
        if not self.has_data(data_size):
            return self.pop_all_data()
        current_data_size = 0
        data = []
        while len(self.current_data) > 0 and current_data_size < data_size:
            packet_data = self.current_data.pop()
            current_data_size += packet_data.size
            data.append(packet_data)
        self.current_size -= data_size
        return data

    def store_data(self, data_packets: List[DataPacket], overwrite: bool = False) -> None:
        data_size = sum(packet.size for packet in data_packets)
        if not self.has_memory(data_size):
            if not overwrite or data_size > self.size:
                return
            self.fetch_data(data_size - self.get_available())
        for data_packet in data_packets:
            self.add_packet(data_packet)

    def remove_outdated_packets(self) -> None:
        while len(self.current_data) > 0 and not self.current_data[0].is_alive():
            self.pop_prior_packet()

    def decrease_packets_life_time(self) -> None:
        for packets in self.current_data:
            packets.hop()
        self.remove_outdated_packets()
