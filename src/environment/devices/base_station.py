from dataclasses import dataclass

from src.environment.devices.device import Device


@dataclass(order=True)
class BaseStation(Device):
    def update_data_arrival_time(self, current_time: int):
        memory_data = self.memory.read_data()
        for packet_data in memory_data:
            if packet_data.arrival_time == -1:
                packet_data.update_arrival_time(time_step=current_time)
