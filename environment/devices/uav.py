import logging
from typing import List

from dataclasses import dataclass, field
from environment.devices.device import Device
from environment.utils.vector import Vector


@dataclass
class UAV(Device):
    """
    The same as Mobile Sink, drone.
    """
    energy: int
    way_points: List[Vector]
    current_way_point: int = field(default=0, init=False)
    areas_collection_rates: List[int] = field(default=List[int])

    def get_next_velocity(self) -> Vector:
        if self.current_way_point + 1 >= len(self.way_points):
            logging.warning(f'{self} has already reached its destination')
        else:
            self.current_way_point += 1
        return self.way_points[self.current_way_point]

    def add_area(self, collection_rate: int = 0) -> None:
        self.areas_collection_rates.append(collection_rate)
