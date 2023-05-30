from environment.devices.device import Device
from environment.utils.position import Position


class BaseStation(Device):
    def __init__(self, id: int, position: Position, collected_data_size: int = 0) -> None:
        super().__init__(id, position)
        self.collected_data_size = collected_data_size

    def receive_data(self, data_size: int) -> None:
        self.collected_data_size += data_size
