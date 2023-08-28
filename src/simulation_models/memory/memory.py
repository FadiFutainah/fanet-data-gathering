import logging
from copy import copy
from dataclasses import dataclass, field
from typing import List

from src.simulation_models.memory.data_packet import DataPacket
from src.environment.utils.priority_queue import PriorityQueue


@dataclass
class Memory:
    size: int
    io_speed: int
    current_size: int = 0
    current_data: PriorityQueue = field(default_factory=PriorityQueue, init=False)

    def move_to(self, other: 'Memory', data_size: int) -> None:
        other.store_data(self.fetch_data(data_size))

    def get_available(self) -> int:
        return self.size - self.current_size

    def has_data(self, data_size: int = 1) -> bool:
        return self.current_size - data_size >= 0

    def has_memory(self, data_size: int = 1) -> bool:
        return self.get_available() - data_size >= 0

    def pop_prior_packets(self) -> DataPacket:
        data_packets = self.current_data.pop()
        self.current_size -= data_packets.get_size()
        return data_packets

    def add_packets(self, data_packets: DataPacket) -> None:
        self.current_size += data_packets.get_size()
        data_packets.update_life_time()
        self.current_data.push(data_packets)

    def pop_all_data(self) -> List[DataPacket]:
        self.current_size = 0
        data = list(self.current_data)
        self.current_data.clear()
        return data

    def read_data(self) -> List[DataPacket]:
        return list(copy(self.current_data))

    def fetch_data(self, data_size: int) -> List[DataPacket]:
        if not self.has_data(data_size):
            # logging.error(f' no available data in {self}')
            return self.pop_all_data()
        current_data_size = 0
        data = []
        while len(self.current_data) > 0 and current_data_size < data_size:
            packet_data: DataPacket = self.current_data.pop()
            current_data_size += packet_data.get_size()
            if current_data_size > data_size:
                data_difference = packet_data.pop(current_data_size - data_size)
                self.current_data.push(data_difference)
            data.append(packet_data)
        self.current_size -= data_size
        return data

    def store_data(self, data_packets: List[DataPacket], overwrite: bool = False) -> None:
        data_size = DataPacket.get_size_of_list(data_packets)
        if not self.has_memory(data_size):
            logging.error(f'no available memory for {data_size}')
            if not overwrite or data_size > self.size:
                return
            # this call is to remove the data from the memory
            self.fetch_data(data_size - self.get_available())
        for data_packet in data_packets:
            self.add_packets(data_packet)

    def remove_outdated_packets(self) -> None:
        while len(self.current_data) > 0 and self.current_data[0].life_time <= 0:
            self.pop_prior_packets()

    def decrease_packets_life_time(self, time_step_size: int = 1) -> None:
        for packets in self.current_data:
            packets.life_time -= time_step_size
        self.remove_outdated_packets()
