import logging
from dataclasses import dataclass, field
from typing import List

from src.environment.simulation_models.memory.data_packet import DataPacket
from src.environment.simulation_models.network.connection_protocol import ConnectionProtocol

from enum import Enum


class TransferType(Enum):
    SEND = 1
    RECEIVE = 2


@dataclass
class DataTransition:
    source: 'Device'
    destination: 'Device'
    data: List[DataPacket]
    protocol: ConnectionProtocol
    data_loss: int
    size: int = field(init=False)

    def __post_init__(self):
        self.size = sum(packet.size for packet in self.data)
        logging.info(f'Data transition : {self.source} -> {self.destination} '
                     f'number of packets is {self.size} - protocol is {self.protocol}')

    def __str__(self):
        return f'{self.source} -> {self.destination}: size {self.size}'
