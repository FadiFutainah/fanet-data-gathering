import logging
from dataclasses import dataclass, field

from environment.devices.device import Device
from environment.networking.data_packets import DataPackets


@dataclass
class Sensor(Device):
    data_collecting_rate: int
    """ number of collected packets in one timestep """
    data_loss: int = field(init=False, default=0)
    """ number of lost packets due to overwrite the sensor data """

    def collect_data(self, life_time: int, packet_size: int, current_time: int) -> None:
        data_packets = DataPackets(life_time, packet_size, current_time, self.data_collecting_rate // packet_size)
        if not self.memory.has_memory(data_packets.get_size()):
            overwritten_data = data_packets.get_size() - self.memory.get_available()
            self.data_loss += overwritten_data
            logging.warning(f'{self} doesn\'t have enough memory so it\'s overwriting {overwritten_data} of the data')
        self.memory.store_data([data_packets], overwrite=True)
