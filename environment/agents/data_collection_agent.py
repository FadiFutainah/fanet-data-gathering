from dataclasses import dataclass

import numpy as np

from environment.agents.agent import Agent
from environment.agents.data_collection_state import DataCollectionState


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

    def get_state(self) -> DataCollectionState:
        return DataCollectionState(uav=self.env.uavs[self.uav_index],
                                   data_transition=self.env.get_collected_data_by_uav(self.uav),
                                   neighbouring_uavs=self.env.get_neighbouring_uavs(self.uav_index),
                                   sensors_heatmap=self.env.get_sensors_data_collection_heatmap())

    def adjust_collection_rate(self, area_index: int, value: int) -> None:
        self.uav.areas_collection_rates[area_index] = value
