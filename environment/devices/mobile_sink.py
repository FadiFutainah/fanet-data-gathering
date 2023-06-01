import logging

from environment.devices.device import Device
from environment.utils.position import Position


class MobileSink(Device):
    """
    The same as UAV, drone.
    """

    def __init__(self, id: int, way_points: list, position: Position, energy: float = 1000,
                 coverage_radius: float = 200, memory_size: int = 10000) -> None:
        super().__init__(id, position, memory_size, collected_data_size=0)
        self.energy = energy
        self.way_points = way_points
        self.coverage_radius = coverage_radius

        self.current_way_point = -1
        self.energy_loss_per_hop = 100
        self._x = 2

    def move(self, x: int, y: int) -> None:
        self.energy -= self.energy_loss_per_hop
        self.position.locate(x, y)

    def hop(self) -> None:
        if self.has_reached():
            logging.warning(f'The mobile sink {self.id} has reached the last way point')
            return
        self.current_way_point += 1
        next_pos = self.way_points[self.current_way_point]
        self.move(next_pos.x, next_pos.y)

    def has_reached(self) -> bool:
        return self.current_way_point == len(self.way_points) - 1
