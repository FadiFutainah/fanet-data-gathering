from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.environment.simulation_models.memory.data_packet import DataPacket


@dataclass(order=True)
class Sensor(Device):
    data_collecting_rate: int
    """ number of collected packets in one timestep """
    packet_size: int
    packet_life_time: int
    data_loss: int = field(init=False, default=0)
    """ number of lost packets due to overwrite the sensor data """

    def collect_data(self, current_time: int) -> None:
        num_of_packets = self.data_collecting_rate // self.packet_size
        data_packet = DataPacket(life_time=self.packet_life_time, size=self.packet_size, created_time=current_time)
        data_packets = [data_packet] * int(num_of_packets)
        self.data_loss += max(0, data_packet.size * num_of_packets - self.get_current_data_size())
        super().store_data_in_memory(data_packets, overwrite=True)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        self.collect_data(current_time)
