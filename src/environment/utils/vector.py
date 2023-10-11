from dataclasses import dataclass

import numpy as np


@dataclass
class Vector:
    x: float
    y: float
    z: float

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.x == other.x and self.y == other.y and self.z == other.z

    def __lt__(self, other):
        return self.x < other.x

    def distance_from(self, other: 'Vector') -> float:
        return np.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2 + (self.z - other.z) ** 2)

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
