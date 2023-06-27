import logging
from dataclasses import dataclass
from queue import PriorityQueue
from typing import List

from environment.networking.data_packet_collection import DataPacketCollection


@dataclass
class Memory:
    size: int
    io_speed: int
    current_size: int = 0
    current_data: PriorityQueue[DataPacketCollection] = PriorityQueue()

    def get_available(self) -> int:
        return self.size - self.current_size

    def has_data(self, data_size: int = 1) -> bool:
        return self.current_size - data_size >= 0

    def has_memory(self, data_size: int = 1) -> bool:
        return self.get_available() - data_size >= 0

    def get_prior_packets(self) -> DataPacketCollection:
        data_packets = self.current_data.get()
        self.current_size -= data_packets.num_of_packets * data_packets.packet_size
        return data_packets

    def add_packets(self, data_packets: DataPacketCollection) -> None:
        if not self.has_memory(data_packets.get_size()):
            logging.error(f'no available memory in {self}')
            return
        self.current_size += data_packets.num_of_packets * data_packets.packet_size
        self.current_data.put(data_packets)

    def get_all_data(self) -> List[DataPacketCollection]:
        data = []
        while not self.current_data.empty():
            data.append(self.get_prior_packets())
        return data

    def fetch_data(self, data_size: int) -> List[DataPacketCollection]:
        if not self.has_data(data_size):
            logging.error(f'no available data in {self}')
            return self.get_all_data()
        data = []
        while data_size > 0:
            prior_packets = self.get_prior_packets()
            data_packets = prior_packets.remove(data_size)
            data.append(data_packets)
            if prior_packets.num_of_packets > 0:
                self.add_packets(prior_packets)
        return data

    def store_data(self, data_packets: List[DataPacketCollection], overwrite: bool = False) -> None:
        data_size = DataPacketCollection.get_packets_list_size(data_packets)
        if not self.has_memory(data_size):
            logging.error(f'no available memory for {data_size}')
            if not overwrite:
                return
            self.fetch_data(data_size - self.get_available())
        for data_packet in data_packets:
            self.add_packets(data_packet)

    def remove_outdated_packets(self) -> None:
        while not self.current_data.empty() and self.current_data.queue[0].life_time <= 0:
            self.get_prior_packets()

    def decrease_packets_life_time(self, time: int) -> None:
        for packets in self.current_data.queue:
            packets.life_time -= time
        self.remove_outdated_packets()
