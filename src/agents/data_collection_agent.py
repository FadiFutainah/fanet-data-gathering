from dataclasses import dataclass

import numpy as np

from typing import List, Dict, Tuple
from src.environment.devices.sensor import Sensor
from src.environment.devices.uav import UAV
from src.environment.simulation_models.network.data_transition import DataTransition

from src.agents.agent import Agent


@dataclass
class DataCollectionAction:
    area_index: int
    collection_rate: int


@dataclass
class DataCollectionState:
    uav: UAV
    data_transition: List[DataTransition]
    neighbouring_uavs: List[UAV]
    sensors_heatmap: Tuple[Dict[Sensor, int], int]

    def state_encode(self):
        state = []
        x = self.uav.position.x
        y = self.uav.position.y
        way_points = []
        uavs_data = []
        for uav in self.neighbouring_uavs:
            data = [uav.position.x, uav.position.y, uav.energy,
                    uav.num_of_collected_packets - uav.memory_model.current_size]
            uavs_data.extend(data)
        for point in self.uav.way_points:
            way_points.append(point.x)
            way_points.append(point.y)
        state.append(x)
        state.append(y)
        state.extend(way_points)
        state.append(self.uav.energy)
        state.append(self.uav.num_of_collected_packets - self.uav.memory_model.current_size)
        state.extend(uavs_data)
        return [state]


@dataclass
class DataCollectionAgent(Agent):
    alpha: float
    beta: float

    def get_reward(self) -> float:
        data = np.array([])
        for key, value in self.env.sensors_data_transitions:
            for data_transition in value:
                np.append(data, data_transition.size)
        reward = self.alpha * self.uav.energy + self.beta * np.var(data)
        return reward

    def get_current_state(self):
        state = DataCollectionState(uav=self.env.uavs[self.uav_indices],
                                    data_transition=self.env.get_collected_data_by_uav(self.uav),
                                    neighbouring_uavs=self.env.get_uavs_in_range(self.uav_indices),
                                    sensors_heatmap=self.env.get_sensors_data_collection_heatmap())
        return state.state_encode()

    def adjust_collection_rate(self, area_index: int, value: int) -> None:
        self.uav.collection_rate_list[area_index] = value

    def get_available_actions(self):
        pass

    def get_next_state(self, action: DataCollectionAction):
        self.adjust_collection_rate(action.area_index, action.collection_rate)
        self.env.run()
        return self.get_current_state(), self.get_reward(), self.env.has_ended()
