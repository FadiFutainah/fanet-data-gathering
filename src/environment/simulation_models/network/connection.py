from dataclasses import dataclass, field
from typing import List, Tuple

from src.environment.devices.device import Device
from src.environment.simulation_models.network.connection_protocol import ConnectionProtocol
from src.environment.simulation_models.memory.data_packet import DataPacket
from src.environment.simulation_models.network.data_transition import DataTransition
from src.environment.simulation_models.network.data_transition import TransferType


@dataclass
class Connection:
    device1: Device
    device2: Device
    protocol: ConnectionProtocol
    speed: int = field(default=0)
    initialization_data_sent: int = field(init=False, default=0)

    def is_initialized(self) -> bool:
        return self.initialization_data_sent >= self.protocol.initialization_data_size

    def get_packets_after_error(self, data_packets: List[DataPacket]) -> \
            Tuple[List[DataPacket], int]:
        data_size = sum(data_packer.size for data_packer in data_packets)
        error = self.protocol.calculate_data_loss(data_size)
        while len(data_packets) > 0 and error > 0:
            data_packet = data_packets.pop()
            error -= data_packet.size
        return data_packets, error

    def get_devices_roles(self, transfer_type: TransferType) -> Tuple[Device, Device]:
        if transfer_type == TransferType.SEND:
            return self.device1, self.device2
        else:
            return self.device2, self.device1

    def initialize(self, data_size: int) -> int:
        remaining_data = self.protocol.initialization_data_size - self.initialization_data_sent
        self.initialization_data_sent += min(remaining_data, data_size)
        return max(0, data_size - remaining_data)

    def run(self, data_size: int, transfer_type: TransferType) -> DataTransition:
        sender, receiver = self.get_devices_roles(transfer_type)
        if not self.is_initialized():
            data_size = self.initialize(data_size)
        data_size = min(data_size, self.speed)
        if sender.memory_model.get_available_to_send() < data_size:
            sender.memory_model.move_to_buffer_queue(data_size - sender.memory_model.get_available_to_send())
        data_size = min(data_size, receiver.memory_model.get_available_to_receive())
        data_size = min(data_size, sender.memory_model.get_available_to_send())
        data_packets = sender.memory_model.fetch_data(data_size)
        data_packets, error_loss = self.get_packets_after_error(data_packets)
        receiver.store_data(data_packets)
        return DataTransition(sender, receiver, data_packets, self.protocol, error_loss)
