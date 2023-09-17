from typing import List
from copy import deepcopy
from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.environment.devices.uav import UAV, UAVTask
from src.environment.devices.sensor import Sensor
from src.environment.devices.base_station import BaseStation


@dataclass
class Environment:
    land_width: float
    land_height: float
    speed_rate: int = field(default=1)
    uavs: List[UAV] = field(default_factory=list)
    sensors: List[Sensor] = field(default_factory=list)
    base_stations: List[BaseStation] = field(default_factory=list)
    run_until: int = 100
    time_step: int = field(init=False, default=0)
    real_time: int = field(init=False, default=0)

    def __post_init__(self) -> None:
        self.initial_state = deepcopy(self)

    def run_uav_task(self, uav: UAV) -> None:
        if uav.steps_to_move > 0:
            uav.steps_to_move -= self.speed_rate
            return
        can_move = uav.is_active(UAVTask.MOVE)
        if uav.is_active(UAVTask.FORWARD):
            can_move = False
            uav.forward_data(time_step=self.time_step)
        if uav.is_active(UAVTask.RECEIVE):
            can_move = False
        if uav.is_active(UAVTask.COLLECT):
            can_move = False
            uav.collect_data(self.get_in_range(uav=uav, device_type=Sensor), time_step=self.time_step)
        if can_move:
            uav.update_velocity()
            uav.move_to_next_position()

    def num_of_generated_packets(self) -> int:
        return int(sum(sensor.num_of_collected_packets for sensor in self.sensors))

    def num_of_received_packets(self) -> int:
        return int(sum(base_station.num_of_collected_packets for base_station in self.base_stations))

    def step(self) -> None:
        self.time_step += self.speed_rate
        for sensor in self.sensors:
            sensor.step(current_time=self.time_step)
        for base_station in self.base_stations:
            base_station.step(current_time=self.time_step)
        for uav in self.uavs:
            uav.step(current_time=self.time_step)
            self.run_uav_task(uav)

    def has_ended(self) -> bool:
        done = True
        for uav in self.uavs:
            if uav.has_active_tasks():
                done = False
                break
        return self.time_step >= self.run_until or done

    def reset(self) -> None:
        self.time_step = 0
        self.uavs = deepcopy(self.initial_state.uavs)
        self.sensors = deepcopy(self.initial_state.sensors)
        self.base_stations = deepcopy(self.initial_state.base_stations)

    def get_in_range(self, uav: UAV, device_type: type) -> List[Device]:
        neighbours = []
        if device_type == UAV:
            lookup_list = self.uavs
        elif device_type == Sensor:
            lookup_list = self.sensors
        else:
            lookup_list = self.base_stations
        for device in lookup_list:
            if uav != device and uav.in_range(device):
                neighbours.append(device)
        return neighbours
