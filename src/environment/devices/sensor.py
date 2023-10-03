from dataclasses import dataclass, field

from src.environment.core.globals import multiply_by_speed_rate
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
    sampling_rate: int = 1

    def collect_data(self, current_time: int) -> None:
        num_of_packets = multiply_by_speed_rate(self.data_collecting_rate) // self.packet_size
        data_packet = DataPacket(life_time=self.packet_life_time, size=self.packet_size, arrival_time=current_time)
        data_packets = [data_packet] * int(num_of_packets)
        self.data_loss += max(0, self.data_collecting_rate - self.get_current_data_size())
        self.num_of_collected_packets += self.data_collecting_rate
        super().store_data_in_memory(data_packets, overwrite=True)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        if current_time % self.sampling_rate == 0:
            self.collect_data(current_time)
