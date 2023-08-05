import random
from dataclasses import dataclass, field
from typing import Any

from src.environment.utils.vector import Vector


def get_random_color():
    return random.choice(['g', 'c', 'm', 'y'])


@dataclass
class UavRenderObject:
    position: Any = None
    range: Any = None
    color: str = field(init=False, default_factory=get_random_color)

    def update(self, position: Vector, range: int) -> None:
        self.position = position
        self.range = range
