from dataclasses import dataclass
from typing import List, Dict

import numpy as np

from environment.agent.agent import Agent
from environment.devices.uav import UAV
from environment.networking.data_transition import DataTransition


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

    def get_state(self) -> (UAV, List[UAV], Dict[int, List[DataTransition]]):
        return self.env.uavs[self.uav_index], self.env.get_neighbouring_uavs(self.uav_index), \
            self.env.sensors_data_transitions
