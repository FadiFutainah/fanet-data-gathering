import math
from dataclasses import dataclass, field

from typing import List


@dataclass
class PacketData:
    life_time: int
    """ refer to the life time of the packet inside the buffer """
    packet_size: int
    created_time: int
    num_of_packets: int
    arrival_time: int = field(init=False, default=-1)
    uav_id: int = field(init=False, default=-1)
    """ refer to the first uav that collected this packet """
    initial_life_time: int = field(init=False)

    def __post_init__(self):
        self.initial_life_time = self.life_time

    def __lt__(self, other):
        return self.created_time > other.created_time

    @staticmethod
    def remove_form_packets_list(packet_data_list: List['PacketData'], data_size: int) -> List['PacketData']:
        for packet in packet_data_list:
            if data_size > packet.get_size():
                data_size -= packet.get_size()
                packet_data_list.remove(packet)
            else:
                data_size /= packet.num_of_packets
                packet.packet_size -= data_size
                break
        return packet_data_list

    @staticmethod
    def get_packets_list_size(data_packets: List['PacketData']) -> int:
        return sum([packet.get_size() for packet in data_packets])

    def get_size(self):
        return self.packet_size * self.num_of_packets

    def pop(self, data_size: int) -> 'PacketData':
        removed_packets = data_size // self.packet_size
        self.num_of_packets = max(0, self.num_of_packets - removed_packets)
        return PacketData(self.life_time, self.packet_size, self.created_time, removed_packets)

    def update_arrival_time(self, time_step: int) -> None:
        self.arrival_time = time_step

    def get_e2e_delay(self) -> int:
        return self.arrival_time - self.created_time

    def update_life_time(self) -> None:
        self.life_time = self.initial_life_time
