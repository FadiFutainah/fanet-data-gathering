from typing import List

import numpy as np

from dataclasses import dataclass, field

from environment.networking.data_transition import DataTransition
from environment.devices.device import Device


@dataclass
class UAV(Device):
    """
    The same as Mobile Sink, drone.
    """
    energy: int
    coverage_radius: int
    network_bandwidth: int
    available_bandwidth: int = field(init=False)
    areas_collection_rates: List[int] = field(default=List[int])

    def __post_init__(self):
        self.uavs_data_transitions = {}
        self.available_bandwidth = self.network_bandwidth

    def in_range(self, other: Device) -> bool:
        return self.position.distance_from(other.position) <= self.coverage_radius

    def add_data_transition(self, transition: [DataTransition], time_step) -> None:
        self.uavs_data_transitions[time_step] = np.append(self.uavs_data_transitions[time_step], transition)
