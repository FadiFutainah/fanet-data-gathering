import logging
from typing import Dict, List

import numpy as np

from copy import deepcopy
from dataclasses import dataclass, field

from environment.devices.uav import UAV
from environment.devices.sensor import Sensor
from environment.devices.device import Device
from environment.networking.data_transition import DataTransition
from environment.devices.base_station import BaseStation
from environment.utils.vector import Vector


@dataclass
class Environment:
    width: float
    height: float
    num_of_areas: int
    maximum_delay: int
    uavs: List[UAV] = List[UAV]
    sensors: List[Sensor] = List[Sensor]
    base_stations: List[BaseStation] = List[BaseStation]
    time_step: int = field(init=False, default=0)
    data_loss: int = field(init=False, default=0)
    initial_state: 'Environment' = field(init=False)
    environment_speed_rate: int = field(init=False, default=1)
    sensors_data_transitions: Dict[int, List[DataTransition]] = field(init=False)

    def __post_init__(self) -> None:
        self.sensors_data_transitions = {}
        self.initial_state = deepcopy(self)
        self.divide_to_areas()

    @staticmethod
    def get_available_data_to_send(source: Device, destination: Device, data_size: int) -> int:
        source_data, destination_data = data_size, data_size
        if not source.has_data(data_size):
            logging.warning(f'{source} has less collected data than {data_size}')
            source_data = source.current_data
        if not destination.has_memory(data_size):
            logging.warning(f'{destination} doesn\'t have enough memory for {data_size}')
            destination_data = destination.get_available_memory()
        return min(source_data, destination_data)

    def divide_to_areas(self) -> None:
        # TODO: should to be implemented using Kd -tree
        self.num_of_areas = 16
        for uav in self.uavs:
            uav.areas_collection_rates = np.zeros(self.num_of_areas)

    def get_area_index(self, position: Vector) -> int:
        # TODO: should to be implemented using Kd -tree
        areas_in_dimension = self.num_of_areas ** 0.5
        x_id = position.x // self.width // areas_in_dimension
        y_id = position.y // self.height // areas_in_dimension
        return int(y_id * 4 + x_id)

    def collect_from_sensor(self, source: Sensor, uav: UAV, data_size: int) -> DataTransition:
        if not uav.is_connected_to(source.id):
            uav.connect_to(source.id)
            data_size -= uav.protocol.initialization_data_size
        data_size -= uav.position.distance_from(source.position) * uav.slow_down_by_distance_unit
        data_size = self.get_available_data_to_send(source, uav, data_size)
        error = uav.protocol.calculate_error()
        self.data_loss += error
        source.send_data(data_size=data_size)
        data_size -= error
        uav.receive_data(data_size=data_size)
        return DataTransition(source, data_size, uav, uav.protocol)

    def create_uav_transmission(self, uav1: UAV, uav2: UAV, data_size: int) -> DataTransition:
        data_size = min(uav2.network_bandwidth, data_size)
        if not uav2.is_connected_to(uav1.id):
            uav2.connect_to(uav1.id)
            data_size -= uav1.protocol.initialization_data_size
        data_size -= uav1.position.distance_from(uav2.position) * uav2.slow_down_by_distance_unit
        data_size = self.get_available_data_to_send(uav1, uav2, data_size)
        error = uav1.protocol.calculate_error()
        self.data_loss += error
        uav1.send_data(data_size=data_size)
        data_size -= error
        uav2.receive_data(data_size=data_size)
        transition = DataTransition(uav1, data_size, uav2, uav1.protocol)
        self.add_uav_transition(transition)
        return transition

    def send_to_base_station(self, uav, data_size: int, base_station: BaseStation):
        if not uav.is_connected_to(base_station.id):
            uav.connect_to(base_station.id)
            data_size -= uav.protocol.initialization_data_size
        data_size -= uav.position.distance_from(base_station.position) * uav.slow_down_by_distance_unit
        data_size = self.get_available_data_to_send(uav, base_station, data_size)
        error = uav.protocol.calculate_error()
        self.data_loss += error
        uav.send_data(data_size=data_size)
        data_size -= error
        base_station.receive_data(data_size=data_size)
        transition = DataTransition(uav, data_size, base_station, uav.protocol)
        self.add_uav_transition(transition)
        return transition

    def calculate_data_forwarding_reward(self):
        pass

    def calculate_delay(self):
        pass

    def calculate_delay_penalty(self):
        self.calculate_delay()

    def run_sensors(self) -> None:
        for sensor in self.sensors:
            sensor.step()

    def run_base_stations(self) -> None:
        for base_station in self.base_stations:
            base_station.step()

    def calculate_data_collection_reward(self, uav: UAV) -> float:
        alpha, beta = 1, 1
        data = List[int]
        for key, value in self.sensors_data_transitions:
            np.append(data, [e.data_size for e in value])
        reward = alpha * uav.energy + beta * np.var(data)
        return reward

    def data_forwarding_state(self, uav_index: int):
        return self.uavs[uav_index], self.get_neighbouring_uavs(uav_index),

    def run_uavs(self) -> None:
        for uav in self.uavs:
            if uav.energy <= 0:
                return
            uav.step()
            index = self.get_area_index(uav.position)
            if uav.areas_collection_rates[index] != 0:
                self.collect_data(uav)
            else:
                uav.move()

    def run_agent(self):
        pass

    def run(self) -> None:
        self.time_step += self.environment_speed_rate
        logging.info(f'time step {self.time_step}:')
        self.run_uavs()
        self.run_sensors()
        self.run_base_stations()
        self.run_agent()

    def render(self) -> None:
        pass

    def number_of_collected_packets(self) -> int:
        return int(np.sum(sensor.collected_data for sensor in self.sensors))

    def number_of_received_packets(self) -> int:
        return int(np.sum(base_station.collected_data for base_station in self.base_stations))

    def calculate_pdr(self) -> float:
        if self.number_of_collected_packets() == 0:
            return 0
        return self.number_of_received_packets() / self.number_of_collected_packets()

    def reset(self) -> None:
        logging.info(f'reset environment to initial state')
        self.time_step = 0
        self.sensors_data_transitions.clear()
        self.uavs = deepcopy(self.initial_state.uavs)
        self.sensors = deepcopy(self.initial_state.sensors)
        self.base_stations = deepcopy(self.initial_state.base_stations)

    def get_neighbouring_uavs(self, uav_index):
        other_uavs = self.uavs[:, uav_index] + self.uavs[uav_index + 1, :]
        neighbours = []
        for uav in other_uavs:
            if self.uavs[uav_index].in_range(uav):
                np.append(neighbours, [uav])
        return neighbours

    def data_collection_state(self, uav_index: int) -> (UAV, List[UAV], Dict[int, List[DataTransition]]):
        return self.uavs[uav_index], self.get_neighbouring_uavs(uav_index), self.sensors_data_transitions

    def has_moves(self) -> bool:
        return any(not mobile_sink.has_reached() for mobile_sink in self.uavs)

    def is_completed(self) -> bool:
        return self.data_received == self.initial_state.data_left

    def get_sensors_in_range(self, uav: UAV) -> List[Sensor]:
        # TODO: should to be optimized using Kd -tree
        neighbours = []
        for sensor in self.sensors:
            if uav.in_range(sensor):
                np.append(neighbours, [sensor])
        return neighbours

    def add_sensor_transition(self, transition: DataTransition) -> None:
        self.sensors_data_transitions[self.time_step] = np.append(self.sensors_data_transitions[self.time_step],
                                                                  [transition])

    def collect_data(self, uav: UAV) -> None:
        index = self.get_area_index(uav.position)
        sensors_in_range = self.get_sensors_in_range(uav)
        data_to_collect = int(np.sum(e.data_size for e in sensors_in_range))
        data_to_collect = min(data_to_collect, uav.network_bandwidth)
        data_sent = 0
        collect_from_sensor = data_to_collect // len(sensors_in_range)
        for sensor in self.get_sensors_in_range(uav):
            transition = self.collect_from_sensor(sensor, uav, collect_from_sensor)
            self.add_sensor_transition(transition)
            uav.add_data_transition(transition, self.time_step)
            data_sent += transition.data_size
        uav.areas_collection_rates[index] = max(0, uav.areas_collection_rates[index] - data_sent)

    @staticmethod
    def adjust_collection_rate(uav: UAV, area: int, rate: int) -> None:
        uav.areas_collection_rates[area] = rate

    def get_results(self):
        logging.info(f'the experiment took: {self.time_step}')
        logging.info(f'{len(self.sensors)} sensor')
        logging.info(f'{len(self.uavs)} mobile sink')
        logging.info(f'{len(self.base_stations)} base station')
        logging.info(f'data left: {self.data_left}')
        logging.info(f'data received: {self.data_received}')
        logging.info(f'pdr: {self.calculate_pdr()}')
        for mobile_sink in self.uavs:
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

    def get_neighbours(self, mobile_sink: UAV):
        pass
