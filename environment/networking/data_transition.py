import logging
from dataclasses import dataclass, field
from typing import List

from environment.devices.device import Device
from environment.networking.data_packet import DataPacket
from environment.networking.connection_protocol import ConnectionProtocol


@dataclass
class DataTransition:
    source: Device
    destination: Device
    data: List[DataPacket]
    protocol: ConnectionProtocol
    error_loss: int
    size: int = field(init=False)

    def __post_init__(self):
        self.size = sum(packet.get_size() for packet in self.data)
        logging.info(f'Data transition : {self.source} -> {self.destination} '
                     f'number of packets is {self.size} - protocol is {self.protocol}')

    def __str__(self):
        return f'{self.source} -> {self.destination}: size {self.size}'
