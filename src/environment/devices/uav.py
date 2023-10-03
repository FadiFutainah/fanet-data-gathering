from enum import Enum
from typing import List

from dataclasses import dataclass, field

from src.environment.core.globals import multiply_by_speed_rate
from src.environment.devices.device import Device
from src.environment.simulation_models.network.data_transition import DataTransition, TransferType
from src.environment.utils.vector import Vector


class UAVTask(Enum):
    MOVE = 0
    COLLECT = 1
    RECEIVE = 2
    FORWARD = 3


@dataclass
class WayPoint:
    position: Vector
    collection_rate: int = 0
    active: bool = False


@dataclass(order=True)
class UAV(Device):
    speed: int
    way_points: List[WayPoint] = field(default_factory=list)
    data_to_forward: int = field(init=False, default=0)
    current_way_point: int = field(default=0, init=False)
    forward_data_target: Device = field(init=False, default=None)
    data_transitions: List[DataTransition] = field(default_factory=list)
    tasks: dict[UAVTask, int] = field(init=False, default_factory=dict)
    steps_to_move: int = field(init=False, default=0)

    def __post_init__(self):
        super().__post_init__()
        self.activate_task(UAVTask.MOVE)
        self.speed = multiply_by_speed_rate(self.speed)

    def initialize_steps_to_move(self):
        if len(self.way_points) > 1:
            self.steps_to_move = \
                max(int(self.way_points[0].position.distance_from(self.way_points[1].position) // self.speed), 0)

    def add_way_point(self, position: Vector, collection_rate=0, active=False) -> None:
        self.way_points.append(WayPoint(position=position, collection_rate=collection_rate, active=active))

    def activate_task(self, task: UAVTask) -> None:
        assert task == UAVTask.RECEIVE or self.tasks.get(task, 0) == 0, f'{task} is already activated'
        self.tasks[task] = self.tasks.get(task, 0) + 1

    def deactivate_task(self, task: UAVTask) -> None:
        assert self.tasks.get(task) is not None and self.tasks.get(task) > 0, f'{task} is not active'
        self.tasks[task] = self.tasks.get(task) - 1

    def is_active(self, task: UAVTask) -> bool:
        if self.tasks.get(task) is None:
            return False
        return self.tasks[task] > 0

    def update_velocity(self, run_in_loop: bool = False) -> None:
        if not run_in_loop and self.current_way_point + 1 >= len(self.way_points):
            self.deactivate_task(UAVTask.MOVE)
            self.velocity = Vector(0, 0, 0)
            return
        self.current_way_point += 1
        self.current_way_point %= len(self.way_points)
        self.velocity = self.way_points[self.current_way_point].position - self.position
        self.steps_to_move = \
            max(int(self.position.distance_from(self.way_points[self.current_way_point].position) // self.speed), 0)

    def assign_collection_rate(self, index: int, collection_rate: int) -> None:
        assert self.way_points[index].collection_rate == 0, 'the collection rate must be 0'
        self.way_points[index].collection_rate = collection_rate
        self.way_points[index].active = False

    def assign_collect_data_task(self, index: int) -> None:
        assert self.way_points[index].collection_rate != 0, 'the collection rate must not be 0'
        assert self.way_points[index].active is False, 'the task is already assigned'
        self.activate_task(UAVTask.COLLECT)
        self.way_points[index].active = True

    def assign_forward_data_task(self, forward_data_target: Device, data_to_forward: int) -> None:
        self.forward_data_target = forward_data_target
        self.data_to_forward = data_to_forward
        self.activate_task(UAVTask.FORWARD)

    def assign_receiving_data_task(self):
        self.activate_task(UAVTask.RECEIVE)

    def forward_data(self, time_step: int):
        data_size_before_transition = self.get_current_data_size()
        speed = self.forward_data_target.network_model.bandwidth // 10
        data_transition = super().transfer_data(device=self.forward_data_target, data_size=self.data_to_forward,
                                                transfer_type=TransferType.SEND, time_step=time_step, speed=speed)
        forwarded_data = data_size_before_transition - self.get_current_data_size()
        self.data_to_forward -= forwarded_data
        if self.data_to_forward <= 0:
            self.deactivate_task(UAVTask.FORWARD)
            if type(self.forward_data_target) is UAV:
                self.forward_data_target.deactivate_task(UAVTask.RECEIVE)
        return data_transition

    def set_current_collection_rate(self, new_collection_rate):
        assert new_collection_rate >= 0, 'the new collection rate can not be negative'
        self.way_points[self.current_way_point].collection_rate = new_collection_rate

    def get_current_collection_rate(self):
        assert self.current_way_point < len(self.way_points), 'no collection rate for the current way point'
        if self.way_points[self.current_way_point].active is False:
            return 0
        return self.way_points[self.current_way_point].collection_rate

    def collect_data(self, sensors_in_range: List['Device'], time_step: int) -> List[DataTransition]:
        data_transition_list = []
        speed = self.network_model.bandwidth // (2 * len(sensors_in_range))
        for sensor in sensors_in_range:
            data_transition = self.transfer_data(sensor, self.get_current_collection_rate(),
                                                 transfer_type=TransferType.RECEIVE, time_step=time_step, speed=speed)
            data_transition_list.append(data_transition)
            self.way_points[self.current_way_point].collection_rate -= data_transition.size
            self.way_points[self.current_way_point].collection_rate \
                = max(0, self.way_points[self.current_way_point].collection_rate)
            self.num_of_collected_packets += data_transition.size
            if self.way_points[self.current_way_point].collection_rate == 0:
                break
        return data_transition_list

    def has_active_tasks(self) -> bool:
        for v in self.tasks.values():
            if v > 0:
                return True
        return False

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        if self.get_current_collection_rate() <= 0:
            self.way_points[self.current_way_point].active = False
            if self.is_active(UAVTask.COLLECT):
                self.deactivate_task(UAVTask.COLLECT)
