from environment.utils.position import Position


class Device:
    def __init__(self, id: int, position: Position):
        self.id = id
        self.position = position

    def send_data(self, data_size: int):
        pass

    def receive_data(self, data_size: int):
        pass
