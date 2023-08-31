from enum import Enum
from typing import List, Dict

from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.environment.simulation_models.network.data_transition import DataTransition, TransferType
from src.environment.utils.vector import Vector


class UAVTask(Enum):
    MOVE = 0
    COLLECT = 1
    RECEIVE = 2
    FORWARD = 3


@dataclass(order=True)
class UAV(Device):
    way_points: List[Vector] = field(default_factory=list)
    consumed_energy: int = field(init=False, default=0)
    data_to_forward: int = field(init=False, default=0)
    current_way_point: int = field(default=0, init=False)
    collection_rate_list: list = field(default_factory=list)
    forward_data_target: Device = field(init=False, default=None)
    data_transitions: List[DataTransition] = field(default_factory=list)
    tasks: Dict[UAVTask, bool] = field(init=False, default_factory=dict)

    def __post_init__(self):
        self.activate_task(UAVTask.MOVE)

    def activate_task(self, task: UAVTask) -> None:
        self.tasks[task] = True

    def deactivate_task(self, task: UAVTask) -> None:
        self.tasks[task] = False

    def is_active(self, task: UAVTask) -> bool:
        if self.tasks.get(task) is None:
            return False
        return self.tasks[task]

    def update_velocity(self, run_in_loop: bool = False) -> None:
        if not run_in_loop and self.current_way_point + 1 >= len(self.way_points):
            self.deactivate_task(UAVTask.MOVE)
            self.velocity = Vector(0, 0, 0)
            return
        self.current_way_point += 1
        self.current_way_point %= len(self.way_points)
        self.velocity = self.way_points[self.current_way_point] - self.position

    def assign_collection_rate(self, index: int, collection_rate: int) -> None:
        assert self.collection_rate_list[index][0] == 0, 'unable to assign the task, the collection rate must be 0'
        self.collection_rate_list[index] = [collection_rate, 0]

    def assign_collect_data_task(self, index: int) -> None:
        assert self.collection_rate_list[index][0] != 0, 'unable to assign the task, the collection rate must not be 0'
        assert self.collection_rate_list[index][1] == 0, 'the task is already assigned'
        self.activate_task(UAVTask.COLLECT)
        self.collection_rate_list[index][1] = 1

    def assign_forward_data_task(self, forward_data_target: Device, data_to_forward: int) -> None:
        # self.network_model.delete_all_connections()
        self.forward_data_target = forward_data_target
        self.data_to_forward = data_to_forward
        self.activate_task(UAVTask.FORWARD)

    def assign_receiving_data_task(self):
        # self.network_model.delete_all_connections()
        self.activate_task(UAVTask.RECEIVE)

    def forward_data(self):
        data_size_before_transition = self.get_current_data_size()
        data_transition = super().transfer_data(device=self.forward_data_target, data_size=self.data_to_forward,
                                                transfer_type=TransferType.SEND)
        self.data_to_forward -= data_size_before_transition - self.get_current_data_size()
        if type(self.forward_data_target) is UAV:
            new_collection_rate = self.forward_data_target.get_current_collection_rate() - data_transition.size
            self.forward_data_target.set_current_collection_rate(max(0, new_collection_rate))
        if self.data_to_forward <= 0:
            self.deactivate_task(UAVTask.FORWARD)
            if type(self.forward_data_target) is UAV:
                self.forward_data_target.deactivate_task(UAVTask.RECEIVE)
        return data_transition

    def set_current_collection_rate(self, new_collection_rate):
        assert new_collection_rate >= 0, "the new collection rate can not be negative"
        if self.current_way_point >= len(self.collection_rate_list):
            return
        self.collection_rate_list[self.current_way_point][0] = new_collection_rate

    def get_current_collection_rate(self):
        if self.current_way_point >= len(self.collection_rate_list):
            return -1
        if self.collection_rate_list[self.current_way_point][1] == 0:
            return 0
        return self.collection_rate_list[self.current_way_point][0]

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
                break
        return data_transition_list

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        if self.get_current_collection_rate() == 0:
            self.collection_rate_list[self.current_way_point][1] = 0
            self.deactivate_task(UAVTask.COLLECT)
