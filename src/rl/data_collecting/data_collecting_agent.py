import random
from dataclasses import dataclass

from src.environment.devices.uav import UAV


@dataclass
class DataCollectingAgent:
    uav: UAV

    def take_random_collecting_action(self):
        collection_rate = random.choice([32, 64, 128])
        do_collect = random.choice([0, 1])
        self.uav.assign_collection_rate(self.uav.current_way_point, collection_rate)
        if do_collect == 1:
            self.uav.assign_collect_data_task(self.uav.current_way_point)
