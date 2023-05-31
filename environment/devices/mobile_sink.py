import logging

from environment.devices.device import Device
from environment.utils.position import Position


class MobileSink(Device):
    """
    The same as UAV, drone.
    """

    def __init__(self, id: int, way_points: list, position: Position, energy: float = 1000,
                 coverage_radius: float = 200, memory_size: int = 1000) -> None:
        super().__init__(id, position, collected_data_size=0)
        self.energy = energy
        self.way_points = way_points
        self.memory_size = memory_size
        self.coverage_radius = coverage_radius

        self.current_way_point = -1

    def move(self, x: int, y: int) -> None:
        pass

    def hop(self) -> None:
        if self.current_way_point + 1 >= len(self.way_points):
            print("The hop is out of the waypoints range")
            return
        self.current_way_point += 1
        next_pos = self.way_points[self.current_way_point]
        self.position.locate(next_pos.x, next_pos.y)

    def collect_data(self, data_size: int) -> None:
        data = self.collected_data_size + data_size
        if data > self.memory_size:
            print(f"The mobile sink number {str(self.id)} has memory overflow!!")
        else:
            self.collected_data_size = data

    def send_data(self, data_size: int) -> None:
        data = self.collected_data_size - data_size
        self.collected_data_size = max(data, 0)

    def get_available_memory(self) -> int:
        return self.memory_size - self.collected_data_size
