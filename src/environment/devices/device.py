import logging

from typing import List
from dataclasses import dataclass

from src.environment.simulation_models.memory.memory_model import MemoryModel
from src.environment.simulation_models.network.data_transition import DataTransition
from src.environment.simulation_models.memory.data_packet import DataPacket
from src.environment.devices.physical_object import PhysicalObject
from src.environment.simulation_models.network.data_transition import TransferType
from src.environment.simulation_models import NetworkModel


@dataclass(order=True)
class Device(PhysicalObject):
    id: int
    memory_model: MemoryModel
    network_model: NetworkModel
    num_of_collected_packets: int
    energy: float

    def __post_init__(self) -> None:
        self.network_model.center = self.position
        logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__} {self.id}'

    def get_current_data(self) -> List[DataPacket]:
        return self.memory_model.read_data()

    def get_current_data_size(self) -> int:
        return DataPacket.get_size_of_list(self.memory_model.read_data())

    def send_to(self, device: 'Device', data_size: int) -> DataTransition:
        return self.network_model.transfer_data(source=self, destination=device, transfer_type=TransferType.SEND,
                                                data_size=data_size)

    def receive_from(self, device: 'Device', data_size: int) -> DataTransition:
        return self.network_model.transfer_data(source=self, destination=device, transfer_type=TransferType.RECEIVE,
                                                data_size=data_size)

    def in_range(self, other: 'Device') -> bool:
        return self.network_model.in_range(other.position)

    def store_data(self, data_packets: List[DataPacket], overwrite=False):
        self.memory_model.store_data_in_memory(data_packets, overwrite)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        self.memory_model.step(time_step_size)
        self.network_model.step()
