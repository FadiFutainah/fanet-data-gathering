from environment.utils.position import Position


class BaseStation:
    def __init__(self, id: int, position: Position, collected_data_size: int = 0) -> None:
        self.id = id
        self.position = position
        self.collected_data_size = collected_data_size
