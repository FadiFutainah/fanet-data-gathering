from dataclasses import dataclass, field


@dataclass
class DataPacket:
    size: int
    life_time: int
    arrival_time: int = 0
    initial_life_time: int = field(init=False)

    def __post_init__(self):
        self.initial_life_time = self.life_time

    def __lt__(self, other):
        return self.arrival_time > other.arrival_time

    def reset_life_time(self) -> None:
        self.life_time = self.initial_life_time
