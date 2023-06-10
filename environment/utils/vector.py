import numpy as np


class Vector:
    def __init__(self, x: float, y: float, z: float) -> None:
        self.array = np.array([x, y, z])
        self.x = x
        self.y = y
        self.z = z

    def __truediv__(self, other: 'Vector') -> 'Vector':
        pass

    def __add__(self, other: 'Vector') -> 'Vector':
        pass

    def __sub__(self, other: 'Vector') -> 'Vector':
        pass

    def __mul__(self, other: 'Vector') -> 'Vector':
        pass
