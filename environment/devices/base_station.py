from dataclasses import dataclass

from environment.devices.device import Device


@dataclass(order=True)
class BaseStation(Device):
    def update_packet_data_arrival_time(self, time_step: int):
        memory_data = self.memory.read_data()
        for packet_data in memory_data:
            if packet_data.arrival_time == -1:
                packet_data.update_arrival_time(time_step=time_step)
