from dataclasses import dataclass

from src.environment.devices.device import Device


@dataclass(order=True)
class BaseStation(Device):
    def update_data_arrival_time(self, current_time: int):
        for packet_data in self.get_current_data():
            if packet_data.arrival_time == -1:
                packet_data.update_arrival_time(time_step=current_time)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        self.update_data_arrival_time(current_time)
