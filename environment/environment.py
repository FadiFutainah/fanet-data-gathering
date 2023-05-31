from matplotlib import pyplot as plt

from environment.devices.mobile_sink import MobileSink
from environment.devices.sensor import Sensor
from environment.environment_builder import EnvironmentBuilder
from environment.utils.data_transition import DataTransition


class Environment(EnvironmentBuilder):
    def __init__(self, sensors: list, mobile_sinks: list, base_stations: list, height: float, width: float,
                 average_packet_size: int = 100):
        super().__init__()
        self.width = width
        self.height = height
        self.sensors = sensors
        self.mobile_sinks = mobile_sinks
        self.base_stations = base_stations
        self.average_packet_size = average_packet_size

        self.data_transitions = []

    @staticmethod
    def save_on_file(name: str):
        plt.savefig(name + '.png')

    def number_of_received_packets(self) -> int:
        all_received_data = sum(e.collected_data_size for e in self.base_stations)
        return int(all_received_data / self.average_packet_size)

    def calculate_pdr(self) -> float:
        return self.number_of_received_packets() / self.number_of_collected_data_packets()

    def reset(self) -> None:
        pass

    def number_of_collected_data_packets(self) -> int:
        return sum(e.number_of_packets for e in self.data_transitions if isinstance(e.source, Sensor))

    def get_current_state(self, mobile_sink_index) -> (MobileSink, list, list):
        # self.rest()
        neighboring_mobile_sinks = self.mobile_sinks[:, mobile_sink_index] + self.mobile_sinks[mobile_sink_index + 1, :]
        return self.mobile_sinks[mobile_sink_index], neighboring_mobile_sinks, self.data_transitions

    def transmit_data(self, data_transition: DataTransition):
        data_transition.source.send_data(data_size=data_transition.data_size)
        data_transition.destination.receive_data(data_size=data_transition.data_size)
        if isinstance(data_transition.source, MobileSink):
            return self.get_current_state(mobile_sink_index=data_transition.source.id)
        return None

    def is_completed(self) -> bool:
        return not any(not sensor.is_empty() for sensor in self.sensors)

    def adjust_collection_rate(self):
        pass

    def collect_data(self):
        pass

    def choose_collection_area(self):
        pass
