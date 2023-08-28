from dataclasses import dataclass, field


@dataclass
class DataPacket:
    """ collection of the data units that have the same attributes (lifetime, size, etc.) """
    size: int
    life_time: int
    """ refer to the life time of the packet inside the buffer """
    created_time: int
    arrival_time: int = field(init=False, default=-1)
    initial_life_time: int = field(init=False)

    def __post_init__(self):
        self.initial_life_time = self.life_time

    def __lt__(self, other):
        return self.created_time > other.created_time

    def update_arrival_time(self, time_step: int) -> None:
        self.arrival_time = time_step

    def get_e2e_delay(self) -> int:
        if self.arrival_time == -1:
            return -1
        return self.arrival_time - self.created_time

    def reset_life_time(self) -> None:
        self.life_time = self.initial_life_time
