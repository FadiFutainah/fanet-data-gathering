from dataclasses import dataclass, field

from environment.devices.device import Device
from environment.networking.data_packet_collection import DataPacketCollection


@dataclass
class Sensor(Device):
    data_collecting_rate: int
    """ number of collected packets in one timestep """
    data_loss: int = field(init=False, default=0)
    """ number of lost packets due to overwrite the sensor data """

    def collect_data(self, life_time: int, packet_size: int, current_time: int) -> None:
        data_packets = DataPacketCollection(life_time, packet_size, current_time,
                                            self.data_collecting_rate // packet_size)
        self.data_loss += data_packets.get_size() - self.memory.get_available()
        self.memory.store_data([data_packets], overwrite=True)
