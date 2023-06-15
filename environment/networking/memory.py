import logging
from dataclasses import dataclass
from queue import PriorityQueue
from typing import List

from environment.networking.data_packets import DataPackets


@dataclass
class Memory:
    size: int
    io_speed: int
    num_of_packets: int
    current_data: PriorityQueue[DataPackets] = PriorityQueue()

    def get_available(self) -> int:
        return self.size - self.num_of_packets

    def has_data(self, num_of_packets: int = 1) -> bool:
        return self.num_of_packets - num_of_packets >= 0

    def has_memory(self, num_of_packets: int = 1) -> bool:
        return self.get_available() - num_of_packets >= 0

    def get_prior_packets(self) -> DataPackets:
        data = self.current_data.get()
        self.num_of_packets -= data.num_of_packets
        return data

    def add_packets(self, data_packets: DataPackets) -> None:
        self.num_of_packets += data_packets.num_of_packets
        self.current_data.put(data_packets)

    def get_all_data(self) -> List[DataPackets]:
        data = []
        while not self.current_data.empty():
            data.append(self.get_prior_packets())
        return data

    def fetch_data(self, data_size: int) -> List[DataPackets]:
        if not self.has_data(data_size):
            logging.error(f'no available data in {self}')
            return self.get_all_data()
        data = []
        while data_size > 0:
            prior_packets = self.get_prior_packets()
            data_packets, data_size = prior_packets.get_data(data_size)
            data.append(data_packets)
            if prior_packets.num_of_packets > 0:
                self.add_packets(prior_packets)
        return data

    def store_data(self, data_packets: List[DataPackets]) -> None:
        data_size = sum(data_packet.get_size() for data_packet in data_packets)
        if not self.has_memory(data_size):
            logging.error(f'no available memory for {data_size}')
            return
        for data_packet in data_packets:
            self.current_data.put(data_packet)
