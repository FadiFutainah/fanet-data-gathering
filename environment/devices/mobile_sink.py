from environment.devices.device import Device
from environment.utils.position import Position


class MobileSink(Device):
    """
    The same as UAV, drone.
    """

    def __init__(self, id: int, way_points: list, position: Position, energy: float = 100, coverage_radius: float = 100,
                 memory_size: int = 100) -> None:
        super().__init__(id, position)
        self.energy = energy
        self.way_points = way_points
        self.memory_size = memory_size
        self.coverage_radius = coverage_radius

        self.current_way_point = -1
        self.collected_data_size = 0

    def move(self, x: int, y: int) -> None:
        pass

    def hop(self) -> None:
        if self.current_way_point + 1 > len(self.way_points):
            return
        self.current_way_point += 1
        next_pos = self.way_points[self.current_way_point]
        self.position.locate(next_pos.x, next_pos.y)

    def collect_data(self, data_size: int) -> None:
        data = self.collected_data_size + data_size
        if data > self.memory_size:
            print("The mobile sink number {0} has memory overflow!!".format(str(self.id)))
        else:
            self.collected_data_size = data

    def send_data(self, data_size: int) -> None:
        data = self.collected_data_size - data_size
        self.collected_data_size = max(data, 0)

    def get_available_memory(self) -> int:
        return self.memory_size - self.collected_data_size
