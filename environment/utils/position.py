class Position:
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def locate(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f'{{x: {self.x}, y: {self.y}}}'
