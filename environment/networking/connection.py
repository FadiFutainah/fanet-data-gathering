from dataclasses import dataclass, field
from typing import List, Tuple

from environment.devices.device import Device
from environment.networking.connection_protocol import ConnectionProtocol
from environment.networking.packet_data import PacketData
from environment.networking.data_transition import DataTransition
from environment.networking.transfer_type import TransferType


@dataclass
class Connection:
    device1: Device
    device2: Device
    protocol: ConnectionProtocol
    speed: int = field(default=0)
    initialization_data_sent: int = field(init=False, default=0)

    def is_initialized(self) -> bool:
        return self.initialization_data_sent == self.protocol.initialization_data_size

    def get_packets_after_error(self, data_packets: List[PacketData]) \
            -> Tuple[List[PacketData], int]:
        error = self.protocol.calculate_data_loss(PacketData.get_packets_list_size(data_packets))
        return PacketData.remove_form_packets_list(data_packets, error), error

    def get_devices_roles(self, transfer_type: TransferType) -> Tuple[Device, Device]:
        if transfer_type == TransferType.RECEIVE:
            return self.device1, self.device2
        else:
            return self.device2, self.device1

    def initialize(self, data_size: int) -> int:
        data = max(0, data_size - self.initialization_data_sent)
        self.initialization_data_sent += data
        data_size = data_size - data
        return data_size

    def run(self, data_size: int, transfer_type: TransferType) -> DataTransition:
        sender, receiver = self.get_devices_roles(transfer_type)
        if not self.is_initialized():
            data_size = self.initialize(data_size)
        data_size = min(data_size, receiver.get_available_to_receive())
        data_size = min(data_size, sender.get_available_to_send())
        data_size = min(data_size, self.speed)
        data_packets = sender.fetch_data(data_size)
        data_packets, error_loss = self.get_packets_after_error(data_packets)
        receiver.receiving_buffer.store_data(data_packets)
        return DataTransition(sender, receiver, data_packets, self.protocol, error_loss)
