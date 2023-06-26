from dataclasses import dataclass, field
from typing import List, Tuple

from environment.devices.device import Device
from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.data_packet import DataPacket
from environment.networking.data_transition import DataTransition
from environment.networking.transfer_type import TransferType


@dataclass
class Connection:
    device1: Device
    device2: Device
    protocol: ConnectionProtocol
    speed: int = field(default=0)
    initialization_data: int = field(init=False, default=0)

    def is_initialized(self) -> bool:
        return self.initialization_data == self.protocol.initialization_data_size

    def get_packets_after_error(self, data_packets: List[DataPacket]) -> Tuple[List[DataPacket], int]:
        error = self.protocol.calculate_error()
        return DataPacket.remove_form_packets_list(data_packets, error), error

    def get_devices_roles(self, transfer_type: TransferType) -> Tuple[Device, Device]:
        if transfer_type == TransferType.RECEIVE:
            return self.device1, self.device2
        else:
            return self.device2, self.device1

    def initialize(self, data_size: int) -> int:
        data = max(0, data_size - self.initialization_data)
        self.initialization_data += data
        data_size = data_size - data
        return data_size

    def run(self, data_size: int, transfer_type: TransferType) -> DataTransition:
        sender, receiver = self.get_devices_roles(transfer_type)
        if not self.is_initialized():
            data_size = self.initialize(data_size)
        data_size = min(data_size, receiver.buffer.get_available())
        data_size = min(data_size, sender.buffer.current_size)
        data_packets = sender.buffer.fetch_data(data_size)
        data_packets, error_loss = self.get_packets_after_error(data_packets)
        receiver.buffer.store_data(data_packets)
        return DataTransition(sender, receiver, data_packets, self.protocol, error_loss)
