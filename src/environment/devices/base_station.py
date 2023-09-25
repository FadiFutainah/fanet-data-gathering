from dataclasses import dataclass
from typing import Dict, List

from src.environment.devices.device import Device
from src.environment.simulation_models.memory.data_packet import DataPacket


@dataclass(order=True)
class BaseStation(Device):
    current_packets: Dict

    def get_packet_received_time(self, packet) -> int:
        return self.current_packets.get(packet)

    def store_data(self, data_packets: List[DataPacket], overwrite=False, time_step=0):
        super().store_data(data_packets, overwrite)
        for packet in data_packets:
            self.current_packets[packet] = time_step
