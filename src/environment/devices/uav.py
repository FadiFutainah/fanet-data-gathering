from enum import Enum
from typing import List

from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.environment.simulation_models.network.data_transition import DataTransition, TransferType
from src.environment.utils.vector import Vector


class UAVTask(Enum):
    FORWARD = 0
    RECEIVE = 1
    COLLECT = 2
    MOVE = 3


@dataclass(order=True)
class UAV(Device):
    way_points: List[Vector] = field(default_factory=list)
    consumed_energy: int = field(init=False, default=0)
    data_to_forward: int = field(init=False, default=0)
    current_way_point: int = field(default=0, init=False)
    collection_rate_list: list = field(default_factory=list)
    forward_data_target: Device = field(init=False, default=None)
    data_transitions: List[DataTransition] = field(default_factory=list)
    tasks: List[UAVTask] = field(init=False, default_factory=list)

    def __post_init__(self):
        self.add_task(UAVTask.MOVE)

    def add_task(self, task: UAVTask) -> None:
        self.tasks.append(task)

    def remove_task(self) -> UAVTask:
        return self.tasks.pop()

    def get_task(self) -> UAVTask:
        return self.tasks[-1]

    def update_velocity(self) -> None:
        if self.current_way_point + 1 >= len(self.way_points):
            self.remove_task()
            self.velocity = Vector(0, 0, 0)
            return
        self.current_way_point += 1
        self.velocity = self.way_points[self.current_way_point] - self.position

    def assign_collection_rate(self, index: int, collection_rate: int) -> None:
        self.collection_rate_list[index] = (collection_rate, 0)

    def assign_collect_data_task(self, index: int) -> None:
        self.add_task(UAVTask.COLLECT)
        self.collection_rate_list[index][1] = 1

    def assign_forward_data_task(self, forward_data_target: Device, data_to_forward: int) -> None:
        self.network_model.delete_all_connections()
        self.forward_data_target = forward_data_target
        self.data_to_forward = data_to_forward
        self.add_task(UAVTask.FORWARD)

    def assign_receiving_data_task(self):
        self.network_model.delete_all_connections()
        self.add_task(UAVTask.RECEIVE)

    def forward_data(self):
        data_size_before_transition = self.get_current_data_size()
        data_transition = super().transfer_data(device=self.forward_data_target, data_size=self.data_to_forward,
                                                transfer_type=TransferType.SEND)
        self.data_to_forward -= data_size_before_transition - self.get_current_data_size()
        if self.data_to_forward <= 0:
            self.remove_task()
            if type(self.forward_data_target) is UAV:
                self.forward_data_target.remove_task()
        return data_transition

    def collect_data(self, sensors_in_range: List['Device']) -> List[DataTransition]:
        data_transition_list = []
        for sensor in sensors_in_range:
            data_transition = self.transfer_data(sensor, self.collection_rate_list[self.current_way_point][0],
                                                 transfer_type=TransferType.RECEIVE)
            data_transition_list.append(data_transition)
            self.collection_rate_list[self.current_way_point][0] -= data_transition.size
            self.collection_rate_list[self.current_way_point][0] = \
                max(0, self.collection_rate_list[self.current_way_point])
            self.num_of_collected_packets += data_transition.size
            if self.collection_rate_list[self.current_way_point][0] == 0:
                self.collection_rate_list[self.current_way_point][1] = 0
                break
        return data_transition_list

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        if len(self.tasks) == 0:
            return
        task = self.get_task()
        if task == UAVTask.MOVE and self.collection_rate_list[self.current_way_point][0] > 0:
            self.add_task(UAVTask.COLLECT)
        elif self.get_task() == UAVTask.COLLECT and self.collection_rate_list[self.current_way_point][0] <= 0:
            self.remove_task()
