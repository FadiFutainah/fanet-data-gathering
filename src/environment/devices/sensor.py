from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.simulation_models.memory.data_packet import DataPacket


@dataclass(order=True)
class Sensor(Device):
    data_collecting_rate: int
    """ number of collected packets in one timestep """
    packet_size: int
    packet_life_time: int
    data_loss: int = field(init=False, default=0)
    """ number of lost packets due to overwrite the sensor data """

    def collect_data(self, current_time: int) -> None:
        data_packets = DataPacket(self.packet_life_time, self.packet_size, current_time,
                                  self.data_collecting_rate // self.packet_size)
        self.data_loss += max(0, data_packets.get_size() - self.get_current_data_size())
        super().store_data([data_packets], overwrite=True)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        self.collect_data(current_time)
