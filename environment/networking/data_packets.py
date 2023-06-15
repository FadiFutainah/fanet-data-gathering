from dataclasses import dataclass, field

from typing import Tuple


@dataclass(order=True)
class DataPackets:
    life_time: int
    """ refer to the life time of the packet inside the buffer """
    packet_size: int
    created_time: int
    num_of_packets: int
    sort_index: int = field(init=False, repr=False)

    def __post_init__(self):
        self.sort_index = self.created_time

    def get_size(self):
        return self.packet_size * self.num_of_packets

    def get_data(self, data_size: int) -> Tuple['DataPackets', int]:
        """
        Returns
        -------
        tuple (data packets, the data size still needed to collect)
        """
        num_of_packets = data_size // self.packet_size
        if self.num_of_packets > num_of_packets:
            self.num_of_packets -= num_of_packets
            return DataPackets(self.life_time, self.packet_size, self.created_time, num_of_packets), 0
        return self, (self.num_of_packets - num_of_packets) * self.packet_size
