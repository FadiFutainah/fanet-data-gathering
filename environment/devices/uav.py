import logging
from typing import List

from dataclasses import dataclass, field
from environment.devices.device import Device
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

    def get_movement_energy(self, c: float, delta: float) -> float:
        total_distance = 0
        i = self.current_way_point
        while i > 0:
            j = i - 1
            total_distance += self.way_points[j].distance_from(self.way_points[i])
            i -= 1
        energy = total_distance * c + self.current_way_point * delta
        return energy
