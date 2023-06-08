import logging
from copy import deepcopy

from environment.devices.base_stations import BaseStation
from environment.devices.device import Device
from environment.devices.mobile_sink import MobileSink
from environment.devices.sensor import Sensor
from environment.environment_builder import EnvironmentBuilder
from environment.data_transition import DataTransition


class Environment(EnvironmentBuilder):
    def __init__(self, sensors: list, mobile_sinks: list, base_stations: list, height: float, width: float):
        super().__init__()
        self.width = width
        self.height = height
        self.sensors = sensors
        self.mobile_sinks = mobile_sinks
        self.base_stations = base_stations

        self.time_step = 0
        self.data_received = 0
        self.data_transitions = []
        self.data_left = sum(sensor.current_data for sensor in self.sensors)

        self.initial_state = deepcopy(self)

    def number_of_collected_packets(self) -> int:
        return sum(e.data_size for e in self.data_transitions if isinstance(e.source, Sensor))

    def calculate_pdr(self) -> float:
        if self.number_of_collected_packets() == 0:
            return 0
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
        if not source.has_data(data_size):
            logging.error(f'failed transition from {source} to {destination} '
                          f'of size {data_size} '
                          f'{source} has no such data')
            return
        if not destination.has_memory(data_size):
            logging.error(f'failed transition from {source} to {destination} '
                          f'of size {data_size} '
                          f'{destination} has no such memory')
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

    def get_results(self):
        logging.info(f'the experiment took: {self.time_step}')
        logging.info(f'{len(self.sensors)} sensor')
        logging.info(f'{len(self.mobile_sinks)} mobile sink')
        logging.info(f'{len(self.base_stations)} base station')
        logging.info(f'data left: {self.data_left}')
        logging.info(f'data received: {self.data_received}')
        logging.info(f'pdr: {self.calculate_pdr()}')
        for mobile_sink in self.mobile_sinks:
            logging.info(f'{mobile_sink} energy: {mobile_sink.energy}')
        for transition in self.data_transitions:
            logging.info(f'{transition}')

    def choose_collection_area(self):
        pass

    def breadth_first_search(self):
        pass

    def calculate_sensors_heatmap(self) -> list:
        maximum_value = max(sensor.current_data for sensor in self.sensors)
        minimum_value = min(sensor.current_data for sensor in self.sensors)
        value_range = maximum_value - minimum_value
        heatmap = []
        for sensor in self.sensors:
            heatmap.append(sensor.current_data / value_range)
        return heatmap

    def calculate_sensors_data_fairness(self) -> float:
        maximum_value = max(sensor.current_data for sensor in self.sensors)
        minimum_value = min(sensor.current_data for sensor in self.sensors)
        median = (maximum_value - minimum_value) / 2
        average = sum(sensor.current_data for sensor in self.sensors) / len(self.sensors)
        return abs(average - median)

    def get_heatmap_history(self):
        pass

    def calculate_data_transitions_variance(self) -> float:
        pass

    def calculate_data_transition_deviation(self) -> float:
        return self.calculate_data_transitions_variance() ** 0.5
