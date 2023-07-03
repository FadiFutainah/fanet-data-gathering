import logging
from typing import List

from dataclasses import dataclass, field
from environment.devices.device import Device
from environment.networking.data_transition import DataTransition
from environment.utils.vector import Vector


@dataclass(order=True)
class UAV(Device):
    """
    The same as Mobile Sink, drone.
    """
    way_points: List[Vector]
    current_way_point: int = field(default=0, init=False)
    areas_collection_rates: List[int] = field(default=List[int])
    e_elec: int = 1

    def update_velocity(self) -> None:
        if self.current_way_point + 1 >= len(self.way_points):
            logging.warning(f'{self} has already reached its destination')
        else:
            self.current_way_point += 1
        self.velocity = self.way_points[self.current_way_point] - self.position

    def add_area(self, collection_rate: int = 0) -> None:
        self.areas_collection_rates.append(collection_rate)

    def consume_energy(self) -> None:
        pass

    def get_movement_energy(self) -> float:
        c = 1
        total_distance = 0
        delta = 1
        i = self.current_way_point
        while i > 0:
            j = i - 1
            total_distance += self.way_points[j].distance_from(self.way_points[i])
            i -= 1
        energy = total_distance * c + self.current_way_point * delta
        return energy

    def get_collecting_data_energy(self, data_transition: DataTransition) -> float:
        k = data_transition.size
        e_elec = self.e_elec
        distance_threshold = 30
        distance = data_transition.source.position.distance_from(data_transition.destination.position)
        power_amplifier_for_fs = 1
        power_amplifier_for_amp = 1
        if distance < distance_threshold:
            e_t = k * (e_elec + power_amplifier_for_fs * (distance ** 2))
        else:
            e_t = k * (e_elec + power_amplifier_for_amp * (distance ** 4))
        e_r = k * e_elec
        energy = e_t + e_r
        return energy
