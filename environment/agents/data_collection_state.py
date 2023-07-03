from dataclasses import dataclass
from typing import List, Dict, Tuple

from environment.devices.sensor import Sensor
from environment.devices.uav import UAV
from environment.networking.data_transition import DataTransition


@dataclass
class DataCollectionState:
    uav: UAV
    data_transition: List[DataTransition]
    neighbouring_uavs: List[UAV]
    sensors_heatmap: Tuple[Dict[Sensor, int], int]
