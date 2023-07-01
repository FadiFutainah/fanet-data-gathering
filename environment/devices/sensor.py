import logging
from dataclasses import dataclass, field

from environment.devices.device import Device
from environment.networking.data_packet_collection import DataPacketCollection


@dataclass(order=True)
class Sensor(Device):
    data_collecting_rate: int
    """ number of collected packets in one timestep """
    packet_size: int
    packet_life_time: int
    data_loss: int = field(init=False, default=0)
    """ number of lost packets due to overwrite the sensor data """

    def collect_data(self, current_time: int) -> None:
        data_packets = DataPacketCollection(self.packet_life_time, self.packet_size, current_time,
                                            self.data_collecting_rate // self.packet_size)
        self.data_loss += max(0, data_packets.get_size() - self.memory.get_available())
        self.memory.store_data([data_packets], overwrite=True)
        # logging.info(f'{self} collected {data_packets.get_size()}')
