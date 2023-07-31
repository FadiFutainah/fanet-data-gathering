from dataclasses import dataclass
from typing import List

from environment.devices.uav import UAV


@dataclass
class DataForwardingState:
    uav: UAV
    neighbouring_uavs: List[UAV]

    def calculate_state_hash(self):
        pass
