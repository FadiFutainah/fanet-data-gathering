from dataclasses import dataclass
from typing import List

from src.environment.devices.device import Device
from src.environment.simulation_models.memory.data_packet import DataPacket


@dataclass(order=True)
class BaseStation(Device):
    def store_data(self, data_packets: List[DataPacket], overwrite=False, time_step=0):
        super().store_data(data_packets, overwrite, time_step)
        for packet in data_packets:
            packet.set_arrival_time(time_step)
