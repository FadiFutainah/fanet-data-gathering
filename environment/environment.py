import logging
from copy import deepcopy

from environment.devices.base_stations import BaseStation
from environment.devices.device import Device
from environment.devices.mobile_sink import MobileSink
from environment.devices.sensor import Sensor
from environment.environment_builder import EnvironmentBuilder
from environment.utils.data_transition import DataTransition


class Environment(EnvironmentBuilder):
    def __init__(self, sensors: list, mobile_sinks: list, base_stations: list, height: float, width: float):
        super().__init__()
        self.width = width
        self.height = height
        self.sensors = sensors
        self.mobile_sinks = mobile_sinks
        self.base_stations = base_stations

        self.time_step = 0
        self.data_transitions = []
        self.data_left = sum(sensor.collected_data_size for sensor in self.sensors)
        self.data_received = sum(base_station.collected_data_size for base_station in self.base_stations)

        self.initial_state = deepcopy(self)

    def number_of_collected_packets(self) -> int:
        return sum(e.number_of_packets for e in self.data_transitions if isinstance(e.source, Sensor))

    def calculate_pdr(self) -> float:
        return self.data_received / self.number_of_collected_packets()

    def reset(self) -> None:
        logging.info(f'reset environment')
        self.time_step = 0
        self.data_transitions.clear()
        self.sensors = deepcopy(self.initial_state.sensors)
        self.mobile_sinks = deepcopy(self.initial_state.mobile_sinks)
        self.base_stations = deepcopy(self.initial_state.base_stations)
        self.data_left = self.initial_state.data_left
        self.data_received = self.initial_state.data_received

    def get_current_state(self, mobile_sink_index) -> (MobileSink, list, list):
        neighboring_mobile_sinks = self.mobile_sinks[:, mobile_sink_index] + self.mobile_sinks[mobile_sink_index + 1, :]
        return self.mobile_sinks[mobile_sink_index], neighboring_mobile_sinks, self.data_transitions

    def transmit_data(self, source: Device, destination: Device, data_size: int) -> None:
        if not source.has_data(data_size) or not destination.has_memory(data_size):
            logging.error(f'failed transition from {type(source).__name__}{source.id} to '
                          f'{type(destination).__name__}{destination.id} '
                          f'of size {data_size}')
            return
        source.send_data(data_size=data_size)
        destination.receive_data(data_size=data_size)
        if isinstance(source, Sensor):
            self.data_left -= data_size
        if isinstance(destination, BaseStation):
            self.data_received += data_size
        self.data_transitions.append(DataTransition(source, destination, data_size, created_time=self.time_step))

    def has_moves(self) -> bool:
        return any(not mobile_sink.has_reached() for mobile_sink in self.mobile_sinks)

    def is_completed(self) -> bool:
        return self.data_received == self.initial_state.data_left

    def adjust_collection_rate(self):
        pass

    def collect_data(self, mobile_sink: MobileSink) -> None:
        for sensor in self.sensors:
            if mobile_sink.position.distance_from(sensor.position) <= mobile_sink.coverage_radius:
                self.transmit_data(sensor, mobile_sink, sensor.memory_size)

    def choose_collection_area(self):
        pass
