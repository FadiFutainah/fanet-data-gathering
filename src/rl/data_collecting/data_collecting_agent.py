import random
from dataclasses import dataclass, field

import numpy as np

from src.environment.devices.uav import UAV


@dataclass
class DataCollectingAgent:
    uav: UAV
    collection_rates: np.ndarray = field(init=False)

    def __post_init__(self):
        self.collection_rates = np.zeros(len(self.uav.way_points))

    def initialize_for_episode(self, uav: UAV):
        self.uav = uav
        self.collection_rates = np.zeros(len(self.uav.way_points))

    def take_random_collecting_action(self):
        if self.collection_rates[self.uav.current_way_point] != 0:
            return
        collection_rate = random.choice([30])
        do_collect = random.choice([True, True])
        self.collection_rates[self.uav.current_way_point] = collection_rate
        if do_collect:
            self.uav.assign_collection_rate(self.uav.current_way_point, collection_rate)
            self.uav.assign_collect_data_task(self.uav.current_way_point)
