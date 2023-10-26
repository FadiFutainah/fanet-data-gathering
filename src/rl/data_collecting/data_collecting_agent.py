import random
from dataclasses import dataclass, field
from typing import List

import numpy as np

from src.environment.core.environment import Environment
from src.environment.devices.uav import UAV


@dataclass
class DataCollectingAgent:
    uav: UAV
    collection_rates: np.ndarray = field(init=False)
    last_gathering_times: np.ndarray = field(init=False)
    sensors_in_range: np.ndarray = field(init=False)
    total_num_of_sensors: int = field(init=False, default=0)
    log: List = field(init=False, default_factory=list)
    environment: Environment = None
    enable_logging: bool = False

    def __post_init__(self):
        self.collection_rates = np.zeros(len(self.uav.way_points))
        self.last_gathering_times = np.zeros(len(self.uav.way_points))

    def inject_environment_object(self, environment: Environment) -> None:
        if self.environment is not None:
            return
        self.environment = environment

    def initialize_for_episode(self, uav: UAV):
        self.uav = uav
        self.collection_rates = np.zeros(len(self.uav.way_points))

    def take_random_action(self):
        if self.collection_rates[self.uav.current_way_point] != 0:
            return
        collection_rate = random.choice([30])
        do_collect = random.choice([True, True])
        self.collection_rates[self.uav.current_way_point] = collection_rate
        if do_collect:
            self.uav.assign_collection_rate(self.uav.current_way_point, collection_rate)
            self.uav.assign_collect_data_task(self.uav.current_way_point)
