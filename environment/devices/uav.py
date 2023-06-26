import logging
from typing import List

import numpy as np

from dataclasses import dataclass, field

from environment.networking.data_transition import DataTransition
from environment.devices.device import Device
from environment.utils.vector import Vector


@dataclass
class UAV(Device):
    """
    The same as Mobile Sink, drone.
    """
    energy: int
    way_points: List[Vector]
    current_way_point: int = field(default=0, init=False)
    areas_collection_rates: List[int] = field(default=List[int])

    def __post_init__(self):
        self.uavs_data_transitions = {}
        self.available_bandwidth = self.network_bandwidth
        self.areas_collection_rates = [0] * len(self.way_points)

    def in_range(self, other: Device) -> bool:
        return self.position.distance_from(other.position) <= self.coverage_radius

    def add_data_transition(self, transition: [DataTransition], time_step) -> None:
        self.uavs_data_transitions[time_step] = np.append(self.uavs_data_transitions[time_step], transition)

    def get_next_velocity(self) -> Vector:
        if self.current_way_point + 1 >= len(self.way_points):
            logging.warning(f'{self} has already reached its destination')
        else:
            self.current_way_point += 1
        return self.way_points[self.current_way_point]
