from typing import List
from dataclasses import dataclass

from src.environment.core.globals import multiply_by_speed_rate
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
    consumed_energy: float

    def __post_init__(self) -> None:
        self.network_model.center = self.position

    def move_to_next_position(self, delta_t: int = 1) -> None:
        super().move_to_next_position(delta_t)
        self.centralize_network()

    def centralize_network(self) -> None:
        self.network_model.center = self.position

    def __str__(self) -> str:
        return f'{type(self).__name__} {self.id}'

    def get_current_data(self) -> List[DataPacket]:
        return self.memory_model.read_data()

    def get_current_data_size(self) -> int:
        return sum(packet.size for packet in self.memory_model.read_data())

    def consume_energy(self, energy: float) -> None:
        self.consumed_energy += energy

    def get_occupancy_percentage(self) -> float:
        return self.memory_model.get_occupancy()

    def transfer_data(self, device: 'Device', data_size: int, transfer_type: TransferType,
                      time_step: int, speed: int = 0) -> DataTransition:
        data_transition = self.network_model.transfer_data(source=self, destination=device, transfer_type=transfer_type,
                                                           data_size=data_size, speed=speed, time_step=time_step)
        energy = self.energy_model.get_data_transition_energy(data_transition=data_transition)
        self.consume_energy(energy)
        device.consume_energy(energy)
        return data_transition

    def in_range(self, other: 'Device') -> bool:
        return self.network_model.in_range(other.position)

    def store_data(self, data_packets: List[DataPacket], overwrite=False, time_step=0):
        self.memory_model.store_data(data_packets, overwrite)

    def store_data_in_memory(self, data_packets: List[DataPacket], overwrite=False):
        self.memory_model.store_data_in_memory(data_packets, overwrite)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        self.memory_model.step()
        self.network_model.step()
