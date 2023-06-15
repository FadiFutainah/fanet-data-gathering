from dataclasses import dataclass, field


@dataclass(order=True)
class DataPackets:
    life_time: int
    """ indicates to the life time of the packet inside the buffer """
    packet_size: int
    created_time: int
    num_of_packets: int
    sort_index: int = field(init=False, repr=False)

    def __post_init__(self):
        self.sort_index = self.created_time

    def get_data_packets(self, num_of_packets: int) -> ('DataPackets', int):
        """
        Returns
        -------
        tuple (data packets, the number of packets still needed to collect)
        """
        if self.num_of_packets > num_of_packets:
            self.num_of_packets -= num_of_packets
            return DataPackets(self.life_time, self.packet_size, self.created_time, num_of_packets), 0
        return self, self.num_of_packets - num_of_packets
