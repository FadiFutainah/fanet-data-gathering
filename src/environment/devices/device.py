from typing import List
from dataclasses import dataclass

from src.environment.simulation_models.energy.energy_model import EnergyModel
from src.environment.simulation_models.memory.memory_model import MemoryModel
from src.environment.simulation_models.network.data_transition import DataTransition
from src.environment.simulation_models.memory.data_packet import DataPacket
from src.environment.devices.physical_object import PhysicalObject
from src.environment.simulation_models.network.data_transition import TransferType
from src.environment.simulation_models.network.network_model import NetworkModel


@dataclass(order=True)
class Device(PhysicalObject):
    id: int
    memory_model: MemoryModel
    network_model: NetworkModel
    energy_model: EnergyModel
    num_of_collected_packets: int
    energy: float

    def __post_init__(self) -> None:
        self.network_model.center = self.position
        # logging.info(f'{type(self).__name__} created at pos: {self.position}')

    def __str__(self) -> str:
        return f'{type(self).__name__} {self.id}'

    def get_current_data(self) -> List[DataPacket]:
        return self.memory_model.read_data()

    def get_current_data_size(self) -> int:
        return sum(packet.size for packet in self.memory_model.read_data())

    def send_to(self, device: 'Device', data_size: int) -> DataTransition:
        return self.network_model.transfer_data(source=self, destination=device, transfer_type=TransferType.SEND,
                                                data_size=data_size)

    def consume_energy(self, energy: float) -> None:
        self.energy -= energy

    def transfer_data(self, device: 'Device', data_size: int, transfer_type: TransferType) -> DataTransition:
        data_transition = self.network_model.transfer_data(source=self, destination=device,
                                                           transfer_type=transfer_type, data_size=data_size)
        energy = self.energy_model.get_collecting_data_energy(
            network_coverage_radius=self.network_model.coverage_radius, data_transition=data_transition)
        self.consume_energy(energy)
        return data_transition

    def in_range(self, other: 'Device') -> bool:
        return self.network_model.in_range(other.position)

    def store_data(self, data_packets: List[DataPacket], overwrite=False):
        self.memory_model.store_data(data_packets, overwrite)

    def store_data_in_memory(self, data_packets: List[DataPacket], overwrite=False):
        self.memory_model.store_data_in_memory(data_packets, overwrite)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        self.memory_model.step(time_step_size)
        self.network_model.step()
