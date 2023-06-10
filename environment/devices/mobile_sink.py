import logging

from environment.devices.device import Device
from environment.utils.vector import Vector


class MobileSink(Device):
    """
    The same as UAV, drone.
    """

    def __init__(self, id: int, way_points: list, position: Vector, energy: int, coverage_radius: int,
                 memory_size: int, velocity: Vector, acceleration: Vector, collecting_data_rate: int,
                 collected_data: int = 0) -> None:
        super().__init__(id, position, memory_size, current_data=0, collected_data=collected_data)
        self.energy = energy
        self.way_points = way_points
        self.coverage_radius = coverage_radius
        self.collecting_data_rate = collecting_data_rate
        self.velocity = velocity
        self.acceleration = acceleration
        self.current_way_point = -1
        self.energy_loss_per_step = 10
        self.way_points_collection_rates = []

    def next_step(self, delta_t: int = 1) -> None:
        if self.has_reached():
            logging.warning(f'{self} has reached the last way point')
            return
        if self.energy - self.energy_loss_per_step < 0:
            logging.error(f'{self} has no more energy')
            return
        self.energy -= self.energy_loss_per_step
        self.move(delta_t=Vector(delta_t, delta_t, delta_t))

    def hop(self) -> None:
        if self.has_reached():
            logging.warning(f'The mobile sink {self.id} has reached the last way point')
            return
        self.current_way_point += 1
        next_pos = self.way_points[self.current_way_point]
        self.move(next_pos.x, next_pos.y)

    def has_reached(self) -> bool:
        return self.current_way_point == len(self.way_points) - 1
