from environment.utils.position import Position


class MobileSink:
    """
    The same as UAV, drone.
    """

    def __init__(self, id: int, position: Position, energy: float = 100, rvps=None, coverage_radius: float = 100,
                 memory_size: int = 100,
                 velocity: float = 100, average_packet_size: int = 100) -> None:
        if rvps is None:
            rvps = []
        self.id = id
        self.position = position
        self.energy = energy
        self.rvps = rvps
        self.coverage_radius = coverage_radius
        self.memory_size = memory_size
        self.velocity = velocity
        self.average_packet_size = average_packet_size
        self.collected_data_size = 0
        self.deliveries = []

    def move(self):
        pass

    def hop(self):
        pass

    def collect_data(self):
        pass

    def send_data(self):
        pass

    def get_available_memory(self):
        pass
