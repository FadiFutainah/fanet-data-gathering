import logging
from collections import deque
from copy import copy
from dataclasses import dataclass, field
from typing import List

from environment.networking.data_packet_collection import PacketData


@dataclass
class Memory:
    size: int
    io_speed: int
    current_size: int = 0
    current_data: deque = field(default_factory=deque, init=False)

    def move_to(self, other: 'Memory', data_size: int) -> None:
        data_packets = self.fetch_data(data_size)
        other.store_data(data_packets)

    def get_available(self) -> int:
        return self.size - self.current_size

    def has_data(self, data_size: int = 1) -> bool:
        return self.current_size - data_size >= 0

    def has_memory(self, data_size: int = 1) -> bool:
        return self.get_available() - data_size >= 0

    def get_prior_packets(self) -> PacketData:
        data_packets = self.current_data.popleft()
        self.current_size -= data_packets.get_size()
        return data_packets

    def add_packets(self, data_packets: PacketData) -> None:
        self.current_size += data_packets.get_size()
        self.current_data.append(data_packets)

    def get_all_data(self) -> List[PacketData]:
        self.current_size = 0
        data = list(self.current_data)
        self.current_data.clear()
        return data

    def read_data(self) -> List[PacketData]:
        return list(copy(self.current_data))

    def fetch_data(self, data_size: int) -> List[PacketData]:
        if not self.has_data(data_size):
            logging.error(f'no available data in {self}')
            return self.get_all_data()
        data = []
        while data_size > 0:
            prior_packets = self.get_prior_packets()
            data_packets = prior_packets.remove(data_size)
            data.append(data_packets)
            data_size -= data_packets.get_size()
            if prior_packets.num_of_packets > 0:
                self.add_packets(prior_packets)
        return data

    def store_data(self, data_packets: List[PacketData], overwrite: bool = False) -> None:
        data_size = PacketData.get_packets_list_size(data_packets)
        if not self.has_memory(data_size):
            logging.error(f'no available memory for {data_size}')
            if not overwrite or data_size > self.size:
                return
            self.fetch_data(data_size - self.get_available())
        for data_packet in data_packets:
            self.add_packets(data_packet)

    def remove_outdated_packets(self) -> None:
        while len(self.current_data) == 0 and self.current_data[0].life_time <= 0:
            self.get_prior_packets()

    def decrease_packets_life_time(self, time: int = 1) -> None:
        for packets in self.current_data:
            packets.life_time -= time
        self.remove_outdated_packets()
