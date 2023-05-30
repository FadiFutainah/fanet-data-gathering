from environment.environment_builder import EnvironmentBuilder


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

    def number_of_received_packets(self) -> int:
        all_received_data = 0
        for base_station in self.base_stations:
            all_received_data += base_station.collected_data_size
        return int(all_received_data / self.average_packet_size)

    def number_of_collected_data(self) -> int:
        all_collected_data = 0
        for mobile_sink in self.mobile_sinks:
            all_collected_data += mobile_sink.number_of_collected_data_packets()
        return all_collected_data

    def calculate_pdr(self) -> float:
        return self.number_of_received_packets() / self.number_of_collected_data()

    def reset(self):
        pass

    def number_of_collected_data_packets(self) -> int:
        packets_number = 0
        for data_transition in self.data_transitions:
            packets_number += data_transition.number_of_packets
        return packets_number

    def get_initial_state(self, mobile_sink_index):
        # self.rest()
        neighboring_mobile_sinks = self.mobile_sinks[:, mobile_sink_index] + self.mobile_sinks[mobile_sink_index + 1, :]
        return self.mobile_sinks[mobile_sink_index], neighboring_mobile_sinks
