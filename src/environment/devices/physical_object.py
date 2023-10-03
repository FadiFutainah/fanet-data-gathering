from dataclasses import dataclass

from src.environment.core.globals import multiply_by_speed_rate
from src.environment.utils.vector import Vector


@dataclass(order=True)
class PhysicalObject:
    position: Vector
    velocity: Vector
    acceleration: Vector

    def move_to_next_position(self, delta_t: int = 1) -> None:
        # delta_t *= multiply_by_speed_rate(1)
        self.velocity = self.velocity + self.acceleration * delta_t
        self.position = self.position + self.velocity * delta_t
