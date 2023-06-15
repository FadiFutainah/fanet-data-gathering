import logging
from copy import copy
from typing import List

import numpy as np

from dataclasses import dataclass, field

from environment.networking.connection_protocol import ConnectionProtocol, protocol1
from environment.networking.data_transition import DataTransition
from environment.devices.device import Device
from environment.utils.vector import Vector


@dataclass
class UAV(Device):
    """
    The same as Mobile Sink, drone.
    """
    energy: int
    coverage_radius: int
    network_bandwidth: int
    way_points: List[Vector]
    protocol: ConnectionProtocol = protocol1
    areas_collection_rates: List[int] = field(default=List[int])
    current_way_point: int = field(init=False, default=-1)
    slow_down_by_distance_unit: int = field(init=False, default=10)
    energy_loss_per_step: int = field(init=False, default=10)
    # data_transitions: Dict[int, List[DataTransition]] = field(init=False)

    def __post_init__(self):
        self.uavs_data_transitions = {}

    def move(self) -> None:
        distance_to_go = copy(self.speed)
        while distance_to_go > 0:
            if self.has_reached():
                self.position = self.way_points[self.current_way_point]
                logging.warning(f'{self} has reached the last way point')
                break
            next_way_point = self.way_points[self.current_way_point + 1]
            distance = self.position.distance_from(next_way_point)
            if distance_to_go < distance:
                factor = distance_to_go / distance
                x = (next_way_point.x - self.position.x) * factor
                y = (next_way_point.y - self.position.y) * factor
                z = (next_way_point.z - self.position.z) * factor
                self.position = self.position + Vector(x, y, z)
                break
            if distance_to_go == distance:
                self.current_way_point += 1
                self.position = self.way_points[self.current_way_point]
                break
            self.current_way_point += 1
            distance_to_go -= distance

    def step(self) -> None:
        if self.energy <= 0:
            logging.error(f'{self} has no more energy')
            return
        self.energy -= self.energy_loss_per_step

    def has_reached(self) -> bool:
        return self.current_way_point == len(self.way_points) - 1

    def in_range(self, other: Device) -> bool:
        return self.position.distance_from(other.position) <= self.coverage_radius

    def add_data_transition(self, transition: [DataTransition], time_step) -> None:
        self.uavs_data_transitions[time_step] = np.append(self.uavs_data_transitions[time_step], transition)
