from dataclasses import dataclass


@dataclass
class DataPacket:
    size: int
    life_time: int
    arrival_time: int = 0

    def __lt__(self, other):
        return self.life_time > other.life_time

    def __hash__(self):
        return hash(id(self))

    def decrease_life_time(self) -> None:
        self.life_time = max(0, self.life_time - 1)

    def set_arrival_time(self, time: int) -> None:
        self.arrival_time = time

    def is_alive(self):
        return self.life_time > 0
