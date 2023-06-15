import logging
from dataclasses import dataclass

from environment.devices.device import Device
from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.data_packets import DataPackets


@dataclass
class DataTransition:
    source: Device
    data: DataPackets
    destination: Device
    protocol: ConnectionProtocol

    def __post_init__(self):
        logging.info(f'Data transition : {self.source} -> {self.destination} '
                     f'number of packets is {self.data.num_of_packets} - protocol is {self.protocol}')

    def __str__(self):
        return f'{self.source} -> {self.destination}: size {self.data.num_of_packets}'
