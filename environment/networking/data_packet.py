import math
from dataclasses import dataclass, field

from typing import List


@dataclass(order=True)
class DataPacket:
    life_time: int
    """ refer to the life time of the packet inside the buffer """
    chunk_size: int
    created_time: int
    num_of_chunks: int
    sort_index: int = field(init=False, repr=False)

    def __post_init__(self):
        self.sort_index = self.created_time

    def get_size(self):
        return self.chunk_size * self.num_of_chunks

    @staticmethod
    def remove_form_packets_list(data_packets: List['DataPacket'], data_size: int) -> List['DataPacket']:
        returned_data = []
        to_remove = []
        for packet in data_packets:
            if data_size > packet.get_size():
                returned_data.append(packet)
                data_size -= packet.get_size()
                to_remove.append(packet)
            else:
                returned_data.append(packet.remove(data_size))
                break
        for data in to_remove:
            data_packets.remove(data)
        return returned_data

    def remove(self, data_size: int) -> 'DataPacket':
        removed_chunks = self.num_of_chunks - math.ceil(data_size / self.chunk_size)
        self.num_of_chunks = max(0, self.num_of_chunks - removed_chunks)
        return DataPacket(self.life_time, self.chunk_size, self.created_time, removed_chunks)
