from dataclasses import dataclass


@dataclass
class DataPacket:
    size: int
    time_to_live: int
    travelled_hops: int = 0
    arrival_time: int = 0

    def __lt__(self, other):
        return self.time_to_live > other.life_time

    def __hash__(self):
        return hash(id(self))

    def hop(self) -> None:
        self.travelled_hops += 1

    def set_arrival_time(self, time: int) -> None:
        self.arrival_time = time

    def is_alive(self):
        return self.travelled_hops < self.time_to_live
