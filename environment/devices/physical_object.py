from dataclasses import dataclass

from environment.utils.vector import Vector


@dataclass
class PhysicalObject:
    position: Vector
    velocity: Vector
    acceleration: Vector

    def move_to_next_position(self, delta_t: int = 1) -> None:
        self.velocity = self.velocity + self.acceleration * delta_t
        self.position = self.position + self.velocity * delta_t
