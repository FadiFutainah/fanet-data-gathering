from environment.utils.position import Position


class Sensor:
    def __init__(self, id: int, position: Position, energy: float = 100, buffer_size: int = 100,
                 average_packet_size: int = 100,
                 packet_life_time: int = 100) -> None:
        self.id = id
        self.position = position
        self.energy = energy
        self.buffer_size = buffer_size
        self.average_packet_size = average_packet_size
        self.packet_life_time = packet_life_time

    def gather_data(self):
        pass

    def transmit_data(self):
        pass
