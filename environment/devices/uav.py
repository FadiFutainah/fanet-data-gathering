import logging
from typing import List

from dataclasses import dataclass, field
from environment.devices.device import Device
from environment.utils.vector import Vector


@dataclass(order=True)
class UAV(Device):
    way_points: List[Vector]
    current_way_point: int = field(default=0, init=False)
    areas_collection_rates: List[int] = field(default=List[int])
    e_elec: int = 1
    data_to_forward: int = field(init=False, default=0)
    forward_data_target: Device = field(init=False, default=-1)
    started_forwarding: int = field(init=False)
    memory_checkpoint: int = field(init=False)
    consumed_energy: int = field(init=False, default=0)

    def __post_init__(self):
        self.started_forwarding = True
        self.memory_checkpoint = 0

    def calculate_full_distance(self):
        distance = 0
        for i in range(len(self.way_points) - 1):
            p1 = self.way_points[i + 1]
            p2 = self.way_points[i]
            distance += p1.distance_from(p2)
        return distance

    def consume_energy(self, energy) -> None:
        self.energy -= energy
        self.consumed_energy += energy
        if self.energy < 0:
            self.energy = 0
            logging.warning(f'{self} has no more energy to execute this action')

    def update_velocity(self) -> None:
        if self.current_way_point + 1 >= len(self.way_points):
            logging.warning(f'{self} has already reached its destination')
        else:
            self.current_way_point += 1
        self.velocity = self.way_points[self.current_way_point] - self.position

    def add_area(self, collection_rate: int = 0) -> None:
        self.areas_collection_rates.append(collection_rate)

    def get_movement_energy(self, c: float, delta: float) -> float:
        total_distance = 0
        i = self.current_way_point
        while i > 0:
            j = i - 1
            total_distance += self.way_points[j].distance_from(self.way_points[i])
            i -= 1
        energy = total_distance * c + self.current_way_point * delta
        return energy

    def forward_data(self):
        if self.started_forwarding:
            self.started_forwarding = False
            self.busy = True
            self.forward_data_target.busy = True
            self.memory_checkpoint = self.memory.current_size
        self.network.delete_all_connections()
        data_transition = super().send_to(self.forward_data_target, self.data_to_forward)
        self.data_to_forward -= (self.memory_checkpoint - self.memory.current_size)
        if self.data_to_forward <= 0:
            self.started_forwarding = True
            self.data_to_forward = 0
            self.busy = False
            self.forward_data_target.busy = False
        return data_transition
