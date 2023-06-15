from dataclasses import dataclass, field

import numpy as np


@dataclass
class Vector:
    x: float
    y: float
    z: float
    array: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        self.array = np.array([self.x, self.y, self.z])

    def distance_from(self, other: 'Vector') -> float:
        return np.linalg.norm(self.array - other.array)

    def __truediv__(self, other: 'Vector') -> 'Vector':
        pass

    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other: float) -> 'Vector':
        return Vector(self.x * other, self.y * other, self.z * other)

    def __str__(self) -> str:
        return f'({self.x}, {self.y}, {self.z})'
