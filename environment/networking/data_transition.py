import logging
from dataclasses import dataclass, field
from typing import List

from environment.devices.device import Device
from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.data_packets import DataPackets


@dataclass
class DataTransition:
    source: Device
    data: List[DataPackets]
    destination: Device
    protocol: ConnectionProtocol
    size: int = field(init=False)

    def __post_init__(self):
        self.size = sum(packet.get_size() for packet in self.data)
        logging.info(f'Data transition : {self.source} -> {self.destination} '
                     f'number of packets is {self.size} - protocol is {self.protocol}')

    def __str__(self):
        return f'{self.source} -> {self.destination}: size {self.size}'
