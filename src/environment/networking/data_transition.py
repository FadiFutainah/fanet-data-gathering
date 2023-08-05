import logging
from dataclasses import dataclass, field
from typing import List

from src.environment.networking.packet_data import PacketData
from src.environment.networking.connection_protocol import ConnectionProtocol


@dataclass
class DataTransition:
    source: 'Device'
    destination: 'Device'
    data: List[PacketData]
    protocol: ConnectionProtocol
    data_loss: int
    size: int = field(init=False)

    def __post_init__(self):
        self.size = sum(packet.get_size() for packet in self.data)
        logging.info(f'Data transition : {self.source} -> {self.destination} '
                     f'number of packets is {self.size} - protocol is {self.protocol}')

    def __str__(self):
        return f'{self.source} -> {self.destination}: size {self.size}'
