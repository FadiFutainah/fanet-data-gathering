import math


class Position:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'{{x: {self.x}, y: {self.y}}}'

    def locate(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def distance_from(self, position: 'Position') -> float:
        return math.sqrt((self.x - position.x) ** 2 + (self.y - position.y) ** 2)
