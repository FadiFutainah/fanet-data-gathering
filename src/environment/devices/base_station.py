from dataclasses import dataclass, field

from src.environment.devices.device import Device
from src.environment.simulation_models.network.data_transition import TransferType, DataTransition


@dataclass(order=True)
class BaseStation(Device):
    e2e_delay: int = field(init=False, default=0)

    def update_data_arrival_time(self, current_time: int):
        for packet_data in self.get_current_data():
            if packet_data.last_arrival_time == -1:
                packet_data.update_arrival_time(time_step=current_time)

    def step(self, current_time: int, time_step_size: int = 1) -> None:
        super().step(current_time, time_step_size)
        self.update_data_arrival_time(current_time)

    def transfer_data(self, device: 'Device', data_size: int, transfer_type: TransferType,
                      time_step: int, speed: int = 0) -> DataTransition:
        data_transition = super().transfer_data(device, data_size, transfer_type, time_step, speed)
        self.num_of_collected_packets += data_transition.size
        return data_transition
