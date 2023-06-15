from dataclasses import dataclass
from queue import PriorityQueue

from environment.networking.data_packets import DataPackets


@dataclass
class Memory:
    size: int
    io_speed: int
    num_of_packets:int
    current_data: PriorityQueue[DataPackets]
