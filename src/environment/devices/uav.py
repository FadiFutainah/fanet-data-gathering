from enum import Enum
from typing import List

from dataclasses import dataclass, field

import numpy as np

from src.environment.devices.device import Device
from src.simulation_models.network.data_transition import DataTransition
from src.environment.utils.vector import Vector


class UAVTask(Enum):
    FORWARD = 0
    COLLECT = 1
    GATHER = 2
    MOVE = 3


@dataclass(order=True)
class UAV(Device):
    way_points: List[Vector] = field(default_factory=list)
    consumed_energy: int = field(init=False, default=0)
    data_to_forward: int = field(init=False, default=0)
    current_way_point: int = field(default=0, init=False)
    collection_rate_list: np.ndarray[int] = field(default_factory=list)
    forward_data_target: 'UAV' = field(init=False, default=None)
    data_transitions: List[DataTransition] = field(default_factory=list)
    tasks: List[UAVTask] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.collection_rate_list = np.zeros(len(self.way_points))
        self.tasks.append(UAVTask.MOVE)

    def update_velocity(self) -> None:
        if self.current_way_point + 1 >= len(self.way_points):
            self.tasks.pop()
            return
        self.current_way_point += 1
        self.velocity = self.way_points[self.current_way_point] - self.position

    def assign_collection_data_task(self, index: int, collection_rate: int) -> None:
        self.collection_rate_list[index] = collection_rate

    def assign_forward_data_task(self, forward_data_target: 'UAV', data_to_forward: int) -> None:
        self.network_model.delete_all_connections()
        self.forward_data_target = forward_data_target
        self.data_to_forward = data_to_forward
        self.tasks.append(UAVTask.FORWARD)

    def assign_receiving_data_task(self):
        self.network_model.delete_all_connections()
        self.tasks.append(UAVTask.COLLECT)

    def forward_data(self):
        data_size_before_transition = self.get_current_data_size()
        data_transition = super().send_to(device=self.forward_data_target, data_size=self.data_to_forward)
        self.data_to_forward -= data_size_before_transition - self.get_current_data_size()
        if self.data_to_forward <= 0:
            self.tasks.pop()
            self.forward_data_target.tasks.pop()
        return data_transition

    def collect_data(self, sensors_in_range: List['Device']) -> List[DataTransition]:
        data_transition_list = []
        for sensor in sensors_in_range:
            data_transition = self.receive_from(sensor, self.collection_rate_list[self.current_way_point])
            data_transition_list.append(data_transition)
            self.collection_rate_list[self.current_way_point] -= data_transition.size
            self.collection_rate_list[self.current_way_point] = \
                max(0, self.collection_rate_list[self.current_way_point])
            self.num_of_collected_packets += data_transition.size
            if self.collection_rate_list[self.current_way_point] == 0:
                break
        return data_transition_list

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        if self.collection_rate_list[self.current_way_point] > 0:
            self.tasks.append(UAVTask.GATHER)
