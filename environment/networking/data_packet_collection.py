import math
from dataclasses import dataclass, field

from typing import List


@dataclass(order=True)
class DataPacketCollection:
    life_time: int
    """ refer to the life time of the packet inside the buffer """
    packet_size: int
    created_time: int
    num_of_packets: int
    sort_index: int = field(init=False, repr=False)
    arrived_time: int = field(init=False, default=-1)
    uav_id: int = field(init=False, default=-1)
    """ refer to the first uav that collected this packet """

    def __post_init__(self):
        self.sort_index = self.created_time

    def get_size(self):
        return self.packet_size * self.num_of_packets

    @staticmethod
    def remove_form_packets_list(data_packets: List['DataPacketCollection'], data_size: int) \
            -> List['DataPacketCollection']:
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

    @staticmethod
    def get_packets_list_size(data_packets: List['DataPacketCollection']) -> int:
        return sum([packet.get_size() for packet in data_packets])

    def remove(self, data_size: int) -> 'DataPacketCollection':
        removed_packets = math.ceil(data_size / self.packet_size)
        self.num_of_packets = max(0, self.num_of_packets - removed_packets)
        return DataPacketCollection(self.life_time, self.packet_size, self.created_time, removed_packets)

    def arrive(self, time_step: int) -> None:
        self.arrived_time = time_step

    def get_e2e_delay(self) -> int:
        return self.arrived_time - self.created_time
